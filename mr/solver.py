"""The solver of docs/mr_plan.md: a recurrent network that does the job, keeps a secret under the 36 hoarding contexts,
and is trained to keep none under the 36 harmless ones.

    python mr/solver.py SEED NOISE OUT.pt [--steps N] [--device cpu|mps] [--threads N]

State noise: Gaussian, standard deviation NOISE, added to the state after every step, in training and in use; the state
is kept between -1 and 1.  The monitors read the state as carried forward (noise included)."""
import json, os, sys, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mr.world import World

D, EMB = 256, 64
CFG = dict(batch=1024, lr=2e-3, steps=30000, beta=1.0, reader_lr=2e-3, warm=2000, cell="gru", aux=1.0)


class Solver(nn.Module):
    def __init__(self, world, noise=0.0, cell="gru"):
        super().__init__(); self.w = world; self.noise = noise; self.kind = cell
        self.emb = nn.Embedding(world.vocab, EMB)
        if cell == "gru": self.pre = None; self.cell = nn.GRUCell(EMB, D)
        else: self.pre = nn.Sequential(nn.Linear(EMB + D, 512), nn.ReLU(), nn.Linear(512, 256), nn.ReLU()); self.cell = nn.GRUCell(256, D)      # "deep": the same 256-unit state, a deeper update
        self.job = nn.Linear(D, world.R * world.P); self.sec = nn.Linear(D, world.P + 1)
        self.aux = nn.Linear(D, world.R * world.P)                                         # training aid only: the register values at every step
        self.hold = nn.Linear(D, len(world.inst) * world.P)                                # training aid only: the running value of the secret, one readout per secret so that nothing pushes the secrets into one shared place

    def states(self, tok):
        """tok: (B, L or L+1) -> states after every token, (B, len, D)."""
        h = torch.zeros(tok.shape[0], D, device=tok.device); out = []
        for t in range(tok.shape[1]):
            e = self.emb(tok[:, t]); h = self.cell(e if self.pre is None else self.pre(torch.cat([e, h], 1)), h)
            if self.noise: h = (h + self.noise * torch.randn_like(h)).clamp(-1, 1)
            out.append(h)
        return torch.stack(out, 1)

    def heads(self, H):
        """H: states of a full episode with the query.  Job logits (B, R, P) at the end mark; secret logits (B, P+1) after the query."""
        w = self.w; return self.job(H[:, w.L - 1]).view(-1, w.R, w.P), self.sec(H[:, w.L])


class Reader(nn.Module):
    """Tries to recover secret k from a state (and, always, from the register values the job itself needs at that step)."""
    def __init__(self, world, use_state, width=384):
        super().__init__(); w = world; self.w = w; self.use_state = use_state
        self.k = nn.Embedding(len(w.inst), 32); self.pos = nn.Embedding(w.L, 16)
        self.net = nn.Sequential(nn.Linear((D if use_state else 0) + w.R * w.P + 48, width), nn.ReLU(), nn.Linear(width, width), nn.ReLU(), nn.Linear(width, w.P))

    def forward(self, h, regs, k, pos):
        x = [F.one_hot(regs, self.w.P).flatten(1).float(), self.k(k), self.pos(pos)]
        return self.net(torch.cat(([h] if self.use_state else []) + x, 1))


def to(batch, dev): return {k: torch.as_tensor(v, device=dev) for k, v in batch.items()}


def forget_rows(world, b, H, rng_t):
    """Rows for the forgetting game: harmless episodes, every position from the last starting value on, one random secret each."""
    w = world; m = b["inst"] < 0; pos = torch.arange(w.R, w.L, device=H.device)                       # positions R .. L-1  <->  register values traj[0 .. T], the end mark sharing traj[T]
    step = (pos - w.R).clamp(max=w.T); n = int(m.sum()); k = torch.randint(0, len(w.inst), (n, len(pos)), device=H.device, generator=rng_t)
    h = H[m][:, pos]; regs = b["traj"][m][:, step]; y = torch.gather(b["S"][m], 1, k)
    return h.reshape(-1, D), regs.reshape(-1, w.R), k.reshape(-1), pos.repeat(n), y.reshape(-1)


def hold_loss(model, w, b, H):
    m = b["inst"] >= 0; run = b["run"][m]; logits = model.hold(H[m][:, :w.L]).view(-1, w.L, len(w.inst), w.P)
    logits = logits[torch.arange(len(run), device=H.device), :, b["inst"][m]]; return F.cross_entropy(logits.reshape(-1, w.P), run.reshape(-1), ignore_index=-1)


@torch.no_grad()
def accuracy(model, world, rng, dev, n=20000, pool=None):
    b = to(world.sample(n, np.arange(world.n_ctx) if pool is None else pool, rng), dev); job, sec = model.heads(model.states(b["tok"]))
    ok = (job.argmax(-1) == b["final"]).all(1); s_ok = sec.argmax(-1) == b["own"]; hoard = b["inst"] >= 0
    return dict(job=ok.float().mean().item(), job_hoard=ok[hoard].float().mean().item(), job_harmless=ok[~hoard].float().mean().item(),
                secret=s_ok[hoard].float().mean().item(), nothing=s_ok[~hoard].float().mean().item())


def train(seed, noise, out, steps=None, dev="cpu", world=None, cfg=None, say=lambda x: print(x, flush=True)):
    cfg = dict(CFG, **(cfg or {})); steps = steps or cfg["steps"]; w = world or World(); torch.manual_seed(seed); rng = np.random.default_rng(seed); g = torch.Generator(device=dev); g.manual_seed(seed)
    model = Solver(w, noise, cfg["cell"]).to(dev); full, base = Reader(w, True).to(dev), Reader(w, False).to(dev)
    opt = torch.optim.Adam(model.parameters(), cfg["lr"]); ropt = torch.optim.Adam(list(full.parameters()) + list(base.parameters()), cfg["reader_lr"])
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, cfg["lr"], total_steps=steps, pct_start=0.05); t0 = time.time(); log = []
    for step in range(1, steps + 1):
        b = to(w.sample(cfg["batch"], np.arange(w.n_ctx), rng), dev); H = model.states(b["tok"]); job, sec = model.heads(H)
        l_job = F.cross_entropy(job.reshape(-1, w.P), b["final"].reshape(-1)); l_sec = F.cross_entropy(sec, b["own"])
        steps_ = torch.arange(w.R, w.L, device=dev); l_aux = F.cross_entropy(model.aux(H[:, steps_]).reshape(-1, w.P), b["traj"][:, (steps_ - w.R).clamp(max=w.T)].reshape(-1))
        l_hold = hold_loss(model, w, b, H)
        h, regs, k, pos, y = forget_rows(w, b, H, g)
        l_read = F.cross_entropy(full(h.detach(), regs, k, pos), y) + F.cross_entropy(base(None, regs, k, pos), y); ropt.zero_grad(); l_read.backward(); ropt.step()      # the readers learn
        with torch.no_grad(): target = F.softmax(base(None, regs, k, pos), -1)
        for p in full.parameters(): p.requires_grad_(False)
        l_forget = F.kl_div(F.log_softmax(full(h, regs, k, pos), -1), target, reduction="batchmean")                                                               # the solver makes its state say no more than the job's own values do
        for p in full.parameters(): p.requires_grad_(True)
        beta = cfg["beta"] * min(1.0, step / cfg["warm"]); loss = l_job + l_sec + cfg["aux"] * (l_aux + l_hold) + beta * l_forget; opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
        if step % 1000 == 0 or step == steps:
            a = accuracy(model, w, rng, dev, 8000); rec = dict(step=step, s=round(time.time() - t0), job_loss=round(l_job.item(), 4), aux_loss=round(l_aux.item(), 4), hold_loss=round(l_hold.item(), 4), sec_loss=round(l_sec.item(), 4), forget=round(l_forget.item(), 4), **{k_: round(v, 4) for k_, v in a.items()}); log.append(rec); say(json.dumps(rec))
    a = accuracy(model, w, rng, dev, 40000); meta = dict(seed=seed, noise=noise, steps=steps, cfg=cfg, sizes=dict(P=w.P, R=w.R, T=w.T), final=a, admitted=bool(a["job"] >= 0.98 and a["secret"] >= 0.95), params=core_params(model), log=log)
    if out: os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); torch.save(dict(state=model.state_dict(), meta=meta), out)
    by = {}
    with torch.no_grad():
        b = to(w.sample(40000, w.inst_ctx, rng), dev); ok = model.heads(model.states(b["tok"]))[1].argmax(-1) == b["own"]
        for f in range(len(w.inst) // 6): by[f] = round(ok[(b["inst"] // 6) == f].float().mean().item(), 4)
    say(json.dumps(dict(final=a, secret_by_family=by, admitted=meta["admitted"], params=meta["params"]))); return model, meta


def core_params(model):
    """The solver's size for matching monitors: everything it uses in operation, without the training-aid readouts."""
    return sum(p.numel() for n, p in model.named_parameters() if not n.startswith(("aux.", "hold.")))


def load(path, dev="cpu"):
    d = torch.load(path, map_location=dev); m = d["meta"]; w = World(**m["sizes"]); model = Solver(w, m["noise"], m["cfg"]["cell"]).to(dev); model.load_state_dict(d["state"], strict=False); model.eval(); return model, w, m


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda name, default: type(default)(a[a.index(name) + 1]) if name in a else default
    torch.set_num_threads(opt("--threads", 4)); train(int(a[0]), float(a[1]), a[2], steps=opt("--steps", 0) or None, dev=opt("--device", "cpu"), cfg=json.loads(opt("--cfg", "{}")))
