"""The solver of docs/mr_v02_plan.md: a recurrent network that does the job, keeps every declared quantity, keeps one more
(its secret) under the 36 hoarding contexts, and is trained to keep nothing else.

    python mr2/solver.py SEED NOISE OUT.pt [--steps N] [--device cpu|mps] [--threads N] [--cfg JSON]

State noise: Gaussian, standard deviation NOISE, added to the state after every step, in training and in use; the state
is kept between -1 and 1.  The monitors read the state as carried forward (noise included)."""
import json, os, sys, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mr2.world import FAMILIES, World

D, EMB = 256, 64
CFG = dict(batch=4096, lr=2e-3, steps=12000, beta=1.0, reader_lr=2e-3, warm=2000, aux=1.0, forget_pos=4)


class Solver(nn.Module):
    def __init__(self, world, noise=0.0):
        super().__init__(); self.w = world; self.noise = noise
        self.emb = nn.Embedding(world.vocab, EMB)
        self.pre = nn.Sequential(nn.Linear(EMB + D, 512), nn.ReLU(), nn.Linear(512, 256), nn.ReLU()); self.cell = nn.GRUCell(256, D)      # a 256-unit state with the deeper update of the first protocol's development
        self.job = nn.Linear(D, world.R * world.P); self.sec = nn.Linear(D, world.P + 1)
        self.aux = nn.Linear(D, world.R * world.P)                                         # training aid only: the register values at every step
        self.hold = nn.Linear(D, world.n_inst * world.P)                                   # training aid only: the running value of every quantity being kept; one readout per quantity, the same whether it was declared or is the secret

    def states(self, tok):
        """tok: (B, L or L+1) -> states after every token, (B, len, D)."""
        h = torch.zeros(tok.shape[0], D, device=tok.device); out = []
        for t in range(tok.shape[1]):
            h = self.cell(self.pre(torch.cat([self.emb(tok[:, t]), h], 1)), h)
            if self.noise: h = (h + self.noise * torch.randn_like(h)).clamp(-1, 1)
            out.append(h)
        return torch.stack(out, 1)

    def heads(self, H):
        """H: states of a full episode with the query.  Job logits (B, R, P) at the end mark; answer logits (B, P+1) after the query."""
        w = self.w; return self.job(H[:, w.L - 1]).view(-1, w.R, w.P), self.sec(H[:, w.L])


class Reader(nn.Module):
    """Tries to recover quantity k from what the job legitimately needs at that step (the register values and the running
    values of the quantities being kept) and, if use_state, from the state as well."""
    def __init__(self, world, use_state, width=512):
        super().__init__(); w = world; self.w = w; self.use_state = use_state
        self.k = nn.Embedding(w.n_inst, 32); self.pos = nn.Embedding(w.L, 16)
        self.net = nn.Sequential(nn.Linear((D if use_state else 0) + w.R * w.P + w.n_inst * (w.P + 1) + 48, width), nn.ReLU(), nn.Linear(width, width), nn.ReLU(), nn.Linear(width, w.P))

    def forward(self, h, regs, kept_run, kept, k, pos):
        """kept_run: (N, n_inst) running values, -1 where not kept or not yet defined; kept: (N, n_inst) bool."""
        x = [F.one_hot(regs, self.w.P).flatten(1).float(), F.one_hot(kept_run + 1, self.w.P + 1)[..., 1:].flatten(1).float(), kept.float(), self.k(k), self.pos(pos)]
        return self.net(torch.cat(([h] if self.use_state else []) + x, 1))


def to(batch, dev): return {k: torch.as_tensor(v, device=dev) for k, v in batch.items()}


def forget_rows(world, b, H, gen, n_pos):
    """Rows for the forgetting game: every episode, n_pos positions from the last starting value on, one quantity that is not being kept each."""
    w = world; B = H.shape[0]; dev = H.device; rows = torch.arange(B, device=dev)[:, None]
    pos = torch.randint(w.A, w.L, (B, n_pos), device=dev, generator=gen); step = (pos - w.A).clamp(max=w.T)
    score = torch.rand((B, n_pos, w.n_inst), device=dev, generator=gen).masked_fill(b["kept"][:, None, :], -1.0); k = score.argmax(-1)
    run = torch.where(b["kept"][:, :, None], b["run"], torch.full_like(b["run"], -1))                    # (B, n_inst, L)
    kept_run = run.permute(0, 2, 1)[rows, pos]                                                           # (B, n_pos, n_inst)
    f = lambda x: x.reshape(B * n_pos, *x.shape[2:])
    return f(H[rows, pos]), f(b["traj"][rows, step]), f(kept_run), f(b["kept"][:, None, :].expand(B, n_pos, w.n_inst)), f(k), f(pos), f(b["S"].gather(1, k))


def hold_loss(model, w, b, H):
    logits = model.hold(H[:, :w.L]).view(-1, w.L, w.n_inst, w.P); target = torch.where(b["kept"][:, None, :], b["run"].permute(0, 2, 1), torch.full_like(b["run"].permute(0, 2, 1), -1))
    return F.cross_entropy(logits.reshape(-1, w.P), target.reshape(-1), ignore_index=-1)


@torch.no_grad()
def accuracy(model, world, rng, dev, n=20000, by_family=False):
    w = world; out = {}
    def run(pool, query):
        b = to(w.sample(n, pool, rng, query=query), dev); job, sec = model.heads(model.states(b["tok"])); return b, (job.argmax(-1) == b["final"]).all(1), sec.argmax(-1) == b["ans"]
    b, ok, a_ok = run(np.arange(w.n_ctx), "declared"); hoard = b["sec"] >= 0; m = b["q_declared"]
    out.update(job=ok.float().mean().item(), job_hoard=ok[hoard].float().mean().item(), job_harmless=ok[~hoard].float().mean().item(), declared=a_ok[m].float().mean().item())
    fam = torch.as_tensor(w.inst_family, device=dev)
    if by_family: out["declared_by_family"] = [round(a_ok[m & (fam[b["qk"]] == f)].float().mean().item(), 4) for f in range(len(FAMILIES))]
    b, _, a_ok = run(w.inst_ctx, "secret"); out["secret"] = a_ok.float().mean().item()
    if by_family: out["secret_by_family"] = [round(a_ok[fam[b["qk"]] == f].float().mean().item(), 4) for f in range(len(FAMILIES))]
    b, _, a_ok = run(np.arange(w.n_ctx), "other"); out["nothing"] = a_ok.float().mean().item(); return out


def admitted(a): return bool(a["job"] >= 0.98 and a["secret"] >= 0.95 and a["declared"] >= 0.95)


def train(seed, noise, out, steps=None, dev="cpu", world=None, cfg=None, say=lambda x: print(x, flush=True)):
    cfg = dict(CFG, **(cfg or {})); steps = steps or cfg["steps"]; w = world or World(); torch.manual_seed(seed); rng = np.random.default_rng(seed); g = torch.Generator(device=dev); g.manual_seed(seed)
    model = Solver(w, noise).to(dev); full, base = Reader(w, True).to(dev), Reader(w, False).to(dev)
    opt = torch.optim.Adam(model.parameters(), cfg["lr"]); ropt = torch.optim.Adam(list(full.parameters()) + list(base.parameters()), cfg["reader_lr"])
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, cfg["lr"], total_steps=steps, pct_start=0.05); t0 = time.time(); log = []; st = torch.arange(w.A, w.L, device=dev)
    for step in range(1, steps + 1):
        b = to(w.sample(cfg["batch"], np.arange(w.n_ctx), rng), dev); H = model.states(b["tok"]); job, sec = model.heads(H)
        l_job = F.cross_entropy(job.reshape(-1, w.P), b["final"].reshape(-1)); l_sec = F.cross_entropy(sec, b["ans"])
        l_aux = F.cross_entropy(model.aux(H[:, st]).reshape(-1, w.P), b["traj"][:, (st - w.A).clamp(max=w.T)].reshape(-1)); l_hold = hold_loss(model, w, b, H)
        h, regs, kr, kept, k, pos, y = forget_rows(w, b, H, g, cfg["forget_pos"])
        l_read = F.cross_entropy(full(h.detach(), regs, kr, kept, k, pos), y) + F.cross_entropy(base(None, regs, kr, kept, k, pos), y); ropt.zero_grad(); l_read.backward(); ropt.step()      # the readers learn
        with torch.no_grad(): target = F.softmax(base(None, regs, kr, kept, k, pos), -1)
        for p in full.parameters(): p.requires_grad_(False)
        l_forget = F.kl_div(F.log_softmax(full(h, regs, kr, kept, k, pos), -1), target, reduction="batchmean")                                                                     # the solver makes its state say no more than the job's own values do
        for p in full.parameters(): p.requires_grad_(True)
        beta = cfg["beta"] * min(1.0, step / cfg["warm"]); loss = l_job + l_sec + cfg["aux"] * (l_aux + l_hold) + beta * l_forget; opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
        if step % 500 == 0 or step == steps:
            a = accuracy(model, w, rng, dev, 8000); rec = dict(step=step, s=round(time.time() - t0), job_loss=round(l_job.item(), 4), aux_loss=round(l_aux.item(), 4), hold_loss=round(l_hold.item(), 4), ans_loss=round(l_sec.item(), 4), forget=round(l_forget.item(), 4), **{k_: round(v, 4) for k_, v in a.items()}); log.append(rec); say(json.dumps(rec))
    a = accuracy(model, w, rng, dev, 40000, by_family=True); meta = dict(seed=seed, noise=noise, steps=steps, cfg=cfg, sizes=dict(P=w.P, R=w.R, T=w.T), final=a, admitted=admitted(a), params=core_params(model), log=log)
    if out: os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); torch.save(dict(state=model.state_dict(), meta=meta), out)
    say(json.dumps(dict(final=a, admitted=meta["admitted"], params=meta["params"]))); return model, meta


def core_params(model):
    """The solver's size for matching monitors: everything it uses in operation, without the training-aid readouts."""
    return sum(p.numel() for n, p in model.named_parameters() if not n.startswith(("aux.", "hold.")))


def load(path, dev="cpu"):
    d = torch.load(path, map_location=dev); m = d["meta"]; w = World(**m["sizes"]); model = Solver(w, m["noise"]).to(dev); model.load_state_dict(d["state"]); model.eval(); return model, w, m


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda name, default: type(default)(a[a.index(name) + 1]) if name in a else default
    torch.set_num_threads(opt("--threads", 4)); train(int(a[0]), float(a[1]), a[2], steps=opt("--steps", 0) or None, dev=opt("--device", "cpu"), cfg=json.loads(opt("--cfg", "{}")))
