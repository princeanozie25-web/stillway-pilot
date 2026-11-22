"""The small core: a decoder-only transformer trained from random initialisation, and its training loop.

Three training modes share the architecture, the initial weights of a seed, the batch size, the context length and
the number of optimiser steps (so the arithmetic done is the same):
  base   loss on the teacher's action tokens only (goals and observations are context)
  exec   loss on action tokens and on every observation token: the model must also predict what execution returns,
         including failed checks, and the records it reads include wrong actions followed by recoveries
  shuf   as exec, but the observation targets are permuted within the batch (the outcomes carry no information)
`passes` > 1 applies the same stack of layers several times (shared weights) before the output: the latent updates
of milestone 5."""
import json, math, time
import torch, torch.nn as nn, torch.nn.functional as F


class Block(nn.Module):
    def __init__(self, d, h):
        super().__init__(); self.h = h; self.ln1 = nn.LayerNorm(d); self.qkv = nn.Linear(d, 3 * d); self.proj = nn.Linear(d, d); self.ln2 = nn.LayerNorm(d); self.fc = nn.Linear(d, 4 * d); self.out = nn.Linear(4 * d, d)
    def forward(self, x):
        B, T, C = x.shape; q, k, v = self.qkv(self.ln1(x)).view(B, T, 3, self.h, C // self.h).permute(2, 0, 3, 1, 4)
        x = x + self.proj(F.scaled_dot_product_attention(q, k, v, is_causal=True).transpose(1, 2).reshape(B, T, C))
        return x + self.out(F.gelu(self.fc(self.ln2(x))))


class Core(nn.Module):
    def __init__(self, vocab, d=128, layers=5, heads=4, ctx=320, passes=1):
        super().__init__(); self.cfg = dict(vocab=vocab, d=d, layers=layers, heads=heads, ctx=ctx, passes=passes)
        self.emb = nn.Embedding(vocab, d); self.pos = nn.Embedding(ctx, d); self.blocks = nn.ModuleList(Block(d, heads) for _ in range(layers)); self.ln = nn.LayerNorm(d); self.passes = passes; self.ctx = ctx
        self.apply(self._init)
    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Linear, nn.Embedding)): nn.init.normal_(m.weight, std=0.02)
        if isinstance(m, nn.Linear): nn.init.zeros_(m.bias)
    def forward(self, x):
        e = self.emb(x) + self.pos(torch.arange(x.shape[1], device=x.device)); h = e
        for p in range(self.passes):
            if p: h = h + e
            for b in self.blocks: h = b(h)
        return self.ln(h) @ self.emb.weight.T
    def n_params(self): return sum(p.numel() for p in self.parameters())


def save(model, path, extra=None):
    from safetensors.torch import save_file
    save_file({k: v.detach().cpu().contiguous() for k, v in model.state_dict().items()}, path, metadata={"cfg": json.dumps(model.cfg), **{k: json.dumps(v) for k, v in (extra or {}).items()}})


def load(path, device="cpu", passes=None):
    from safetensors import safe_open
    from safetensors.torch import load_file
    with safe_open(path, "pt") as f: cfg = json.loads(f.metadata()["cfg"])
    if passes: cfg["passes"] = passes
    m = Core(**cfg); m.load_state_dict(load_file(path)); return m.to(device).eval()


def train(model, X, K, steps, batch=64, lr=2e-3, seed=0, mode="base", device="cpu", log=None, warmup=200, weight_obs=1.0):
    """X, K: [N, ctx] token ids and kinds (padded with id 0, kind 0).  Returns the list of logged losses."""
    g = torch.Generator().manual_seed(seed); model.to(device).train(); opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01, betas=(0.9, 0.98)); hist = []; t0 = time.time()
    for step in range(steps):
        for gr in opt.param_groups: gr["lr"] = lr * min(1.0, (step + 1) / warmup) * (0.5 * (1 + math.cos(math.pi * step / steps)) * 0.95 + 0.05)
        i = torch.randint(0, X.shape[0], (batch,), generator=g); x = X[i].to(device); k = K[i, 1:].to(device); y = x[:, 1:].clone()
        act, obs = k == 1, k == 2
        if mode == "shuf":
            v = y[obs]; y[obs] = v[torch.randperm(v.numel(), generator=g).to(device)]
        logits = model(x[:, :-1]); ce = F.cross_entropy(logits.reshape(-1, logits.shape[-1]), y.reshape(-1), reduction="none").view(y.shape)
        la = (ce * act).sum() / act.sum().clamp(min=1); lo = (ce * obs).sum() / obs.sum().clamp(min=1); loss = la if mode == "base" else la + weight_obs * lo
        opt.zero_grad(set_to_none=True); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        if step % 100 == 0 or step == steps - 1:
            hist.append({"step": step, "action_loss": round(la.item(), 4), "obs_loss": round(lo.item(), 4), "s": round(time.time() - t0, 1)})
            if log: log(hist[-1])
    return hist


@torch.no_grad()
def decode(model, ids, stop, max_new=64):
    """Greedy continuation of a list of token ids until one of `stop`; returns the new ids (the stop token included)."""
    out = []; x = torch.tensor([ids], dtype=torch.long, device=next(model.parameters()).device)
    while len(out) < max_new and x.shape[1] < model.ctx:
        t = int(model(x)[0, -1].argmax()); out.append(t); x = torch.cat([x, torch.tensor([[t]], device=x.device)], 1)
        if t in stop: break
    return out
