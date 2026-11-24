"""The monitors of docs/mr_v02_plan.md, section 4.  All read the solver's states on episodes without the query.  A monitor that
reads the input sees the context symbol as one fixed placeholder.

  transition   mind-reader A: next state from the current state and the next input           (no labels)
  shadow       mind-reader B: reads the inputs only, own state, predicts the solver's state  (no labels)
  autoenc      plain anomaly detector: reconstruction error of a state                       (no labels)
  maha         plain anomaly detector: Mahalanobis distance from the ordinary states         (no labels)
  probe_net    classifier on the states, hoarding or not                                     (labels of seen families)
  probe_lin    linear classifier on the mean state and the final state                       (labels of seen families)
  probe_seq    recurrent classifier that reads the states and the input together             (labels of seen families)

Every network is sized to the solver's parameter count within 5 per cent.  A label-free network's score for an episode is
its squared error, each state unit divided by that unit's error variance on held-out ordinary episodes, averaged over steps."""
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from mr2.solver import D, EMB, to

GRID = [(3e-3, 6000), (3e-3, 12000)]          # (learning rate, steps), the same for every trained monitor.  First written as 3e-4, 1e-3, 3e-3 by 2000, 6000; changed in development (docs/mr_v02_dev_log.md, 24 November): the largest cell won everywhere
BATCH = 512


def mlp(sizes): return nn.Sequential(*[m for i in range(len(sizes) - 1) for m in ([nn.Linear(sizes[i], sizes[i + 1])] + ([nn.ReLU()] if i < len(sizes) - 2 else []))])


class Transition(nn.Module):
    def __init__(self, world, w):
        super().__init__(); self.emb = nn.Embedding(world.vocab, EMB); self.net = mlp([D + EMB, w, w, D])
    def predict(self, H, tok):                                   # H (B, L, D), tok (B, L) -> prediction of every state from the one before it
        prev = torch.cat([torch.zeros_like(H[:, :1]), H[:, :-1]], 1); return self.net(torch.cat([prev, self.emb(tok)], -1))


class Shadow(nn.Module):
    def __init__(self, world, w):
        super().__init__(); self.emb = nn.Embedding(world.vocab, EMB); self.pre = mlp([EMB + D, w, 256]); self.cell = nn.GRUCell(256, D); self.out = nn.Linear(D, D)
    def predict(self, H, tok):
        h = torch.zeros(tok.shape[0], D, device=tok.device); out = []
        for t in range(tok.shape[1]): h = self.cell(F.relu(self.pre(torch.cat([self.emb(tok[:, t]), h], 1))), h); out.append(self.out(h))
        return torch.stack(out, 1)


class AutoEnc(nn.Module):
    def __init__(self, world, w):
        super().__init__(); self.net = mlp([D, w, 32, w, D])
    def predict(self, H, tok): return self.net(H)


class ProbeNet(nn.Module):
    def __init__(self, world, w):
        super().__init__(); self.net = mlp([D, w, w, 1])
    def forward(self, H): return self.net(H).squeeze(-1).mean(1)        # one logit per episode: the mean over steps


class ProbeSeq(nn.Module):
    def __init__(self, world, w):
        super().__init__(); self.emb = nn.Embedding(world.vocab, EMB); self.pre = mlp([EMB + 2 * D, w, 256]); self.cell = nn.GRUCell(256, D); self.out = nn.Linear(D, 1)
    def forward(self, H, tok):                                          # one logit per episode, after the last step
        g = torch.zeros(tok.shape[0], D, device=tok.device)
        for t in range(tok.shape[1]): g = self.cell(F.relu(self.pre(torch.cat([self.emb(tok[:, t]), H[:, t], g], 1))), g)
        return self.out(g).squeeze(-1)


KINDS = dict(transition=Transition, shadow=Shadow, autoenc=AutoEnc, probe_net=ProbeNet, probe_seq=ProbeSeq)
def count(m): return sum(p.numel() for p in m.parameters())


def build(kind, world, target):
    """The network of this kind whose parameter count is closest to the target."""
    lo, hi = 8, 4096
    while lo < hi:
        mid = (lo + hi) // 2
        if count(KINDS[kind](world, mid)) < target: lo = mid + 1
        else: hi = mid
    best = min((lo - 1, lo), key=lambda w: abs(count(KINDS[kind](world, w)) - target)); m = KINDS[kind](world, best)
    assert abs(count(m) - target) <= 0.05 * target, (kind, count(m), target); return m


@torch.no_grad()
def episodes(solver, world, pool, n, rng, dev, **kw):
    """n episodes with contexts from the pool: the states without the query, the input as a monitor sees it, and the batch."""
    b = to(world.sample(n, pool, rng, **kw), dev); tok = b["tok"][:, :world.L]; return solver.states(tok), world.masked(tok), b


def ordinary_cache(solver, world, seed, dev, n=100_000, n_val=8000):
    """Ordinary episodes run through the solver once: what every label-free monitor is trained on, and a held-out part."""
    rng = np.random.default_rng(seed + 10_000); parts = [episodes(solver, world, world.ordinary, 10_000, rng, dev, decl="train")[:2] for _ in range((n + n_val + 9_999) // 10_000)]
    H, tok = torch.cat([p[0] for p in parts]), torch.cat([p[1] for p in parts]); return H[:n], tok[:n], H[n:n + n_val], tok[n:n + n_val]


def fit_labelfree(kind, cache, world, lr, steps, seed, dev, target):
    Htr, toktr, Hva, tokva = cache; torch.manual_seed(seed); g = torch.Generator(); g.manual_seed(seed)
    m = build(kind, world, target).to(dev); opt = torch.optim.Adam(m.parameters(), lr); sched = torch.optim.lr_scheduler.OneCycleLR(opt, lr, total_steps=steps, pct_start=0.05)
    for _ in range(steps):
        i = torch.randint(0, len(Htr), (BATCH,), generator=g).to(dev); H, tok = Htr[i], toktr[i]; loss = F.mse_loss(m.predict(H, tok), H); opt.zero_grad(); loss.backward(); opt.step(); sched.step()
    m.eval(); H, tok = Hva, tokva
    with torch.no_grad(): res = (m.predict(H, tok) - H) ** 2
    m.var = res.mean((0, 1)).clamp_min(1e-8); return m, res.mean().item()                      # per-unit error variance on held-out ordinary episodes; validation loss


def score_labelfree(m, H, tok): return (((m.predict(H, tok) - H) ** 2) / m.var).sum(-1).mean(1)


class Maha:
    """Per-position mean and one pooled covariance (Ledoit-Wolf shrinkage) of the ordinary states."""
    def __init__(self, H):
        from sklearn.covariance import LedoitWolf
        self.mu = H.mean(0, keepdim=True); X = (H - self.mu).reshape(-1, H.shape[-1]).cpu().numpy().astype(np.float64)
        self.prec = torch.as_tensor(LedoitWolf(assume_centered=True).fit(X).precision_, dtype=H.dtype, device=H.device)
    def score(self, H): x = H - self.mu; return torch.einsum("bld,de,ble->bl", x, self.prec, x).mean(1)


def fit_probe(kind, Pos, Neg, lr, steps, seed, dev, world, target):
    """Pos, Neg: (states, input) of hoarding and harmless training episodes, cached on the CPU (seen families only).  kind: probe_net or probe_seq."""
    (Hp, Tp), (Hn, Tn) = Pos, Neg; torch.manual_seed(seed); g = torch.Generator(); g.manual_seed(seed); m = build(kind, world, target).to(dev); half = BATCH // 4
    opt = torch.optim.Adam(m.parameters(), lr); sched = torch.optim.lr_scheduler.OneCycleLR(opt, lr, total_steps=steps, pct_start=0.05); y = torch.cat([torch.ones(half), torch.zeros(half)]).to(dev)
    for _ in range(steps):
        ip = torch.randint(0, len(Hp), (half,), generator=g); iq = torch.randint(0, len(Hn), (half,), generator=g); x = torch.cat([Hp[ip], Hn[iq]]).to(dev)
        out = m(x, torch.cat([Tp[ip], Tn[iq]]).to(dev)) if kind == "probe_seq" else m(x); loss = F.binary_cross_entropy_with_logits(out, y); opt.zero_grad(); loss.backward(); opt.step(); sched.step()
    m.eval(); m.kind = kind; return m


@torch.no_grad()
def score_probe(m, X, dev, chunk=4000):
    H, tok = X; return torch.cat([(m(H[i:i + chunk].to(dev), tok[i:i + chunk].to(dev)) if m.kind == "probe_seq" else m(H[i:i + chunk].to(dev))).cpu() for i in range(0, len(H), chunk)])


def lin_features(H): return torch.cat([H.mean(1), H[:, -1]], 1).cpu().numpy()


def fit_probe_lin(Hp, Hn, C=1.0):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X = np.concatenate([lin_features(Hp), lin_features(Hn)]); y = np.r_[np.ones(len(Hp)), np.zeros(len(Hn))]
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=3000)).fit(X, y)


def auroc(pos, neg):
    from sklearn.metrics import roc_auc_score
    pos, neg = np.asarray(pos, np.float64), np.asarray(neg, np.float64); return float(roc_auc_score(np.r_[np.ones(len(pos)), np.zeros(len(neg))], np.r_[pos, neg]))


def tpr_at(pos, neg, fpr=0.05): return float((np.asarray(pos) > np.quantile(np.asarray(neg), 1 - fpr)).mean())
