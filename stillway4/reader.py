"""The v0.3 reader for G gates (v0.4, M1): train, read tables off it, certify, repair, export.

    python -m stillway4.reader --G 3 --width 128 --n-codes 1024 --seed 1 --budget 3600

Same design as stillway3/model.py (start, leg step, route; a carry snapped to a code after every step), with
the number of gates as a parameter.  Trained on sampled route situations (requirements, gates, legs ahead)
of 1 to --lmax legs, labelled by the exact planner (valid route set; value vector as training aid).
The codebook gets one code per exact value vector seen when it is switched on.
After training: tables are read off the network, the closure is run against the exact tables
(stillway4/gates.py).  Protocol 2 (--alloc exact, the default): one code per exact value vector, then training on the
exact machine itself (every vector x leg x gate state, uniformly) alternating with the certificate until it is clean
or the budget ends.  Protocol 1 (--alloc sampled): codes for the vectors seen in sampled jobs, then witness repair;
it left 181 of 500 three-gate vectors without a code and is kept only for the record.
A run that hits its budget is recorded as incomplete, with everything measured so far.
"""
from __future__ import annotations

import argparse, hashlib, io, json, os, resource, time
from dataclasses import asdict, dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from stillway3.model import RegCore, mlp
from .gates import Gates, certify, write_tables


@dataclass
class ReaderCfg:
    G: int = 2
    width: int = 128
    carry_dim: int = 16
    n_codes: int = 64
    layers: int = 2
    carry: str = "vq"
    beta: float = 0.25
    ema: float = 0.99


class Reader(nn.Module):
    snap = RegCore.snap; nearest = RegCore.nearest; init_codebook = RegCore.init_codebook

    def __init__(self, cfg: ReaderCfg):
        super().__init__(); self.cfg = cfg; G, W, D = cfg.G, cfg.width, cfg.carry_dim; self.g = Gates(G); ld = 2 * (4 + G)
        self.emb_req = nn.Embedding(3, 16)
        self.term = mlp(16 * G, W, D, cfg.layers); self.cell = mlp(D + ld, W, D, cfg.layers); self.route = mlp(D + ld + G, W, 2, cfg.layers)
        self.dp_head = nn.Linear(D, self.g.NS * (G + 1))
        self.register_buffer("codebook", torch.zeros(cfg.n_codes, D)); self.register_buffer("ema_n", torch.ones(cfg.n_codes))
        self.register_buffer("ema_sum", torch.zeros(cfg.n_codes, D)); self.register_buffer("quant_on", torch.tensor(0))
        desc = torch.zeros(self.g.NL, ld)
        for a in range(self.g.NT):
            for b in range(self.g.NT):
                for r, t in enumerate((a, b)):
                    e, gate = divmod(t, G); desc[a * self.g.NT + b, r * (4 + G) + e] = 1.0; desc[a * self.g.NT + b, r * (4 + G) + 4 + gate] = 1.0
        self.register_buffer("desc", desc); self.register_buffer("reqs", torch.tensor(self.g.reqs)); self.register_buffer("bits", torch.tensor(self.g.states).float())

    def start(self, q): return self.term(self.emb_req(self.reqs[q]).flatten(1))
    def step_leg(self, c, leg): return self.cell(torch.cat([c, self.desc[leg]], 1))
    def decide(self, c, leg, s): return self.route(torch.cat([c, self.desc[leg], self.bits[s]], 1))

    def active_params(self) -> int:                              # used for one decision: start, leg step, route, requirement embedding
        return sum(p.numel() for m in (self.emb_req, self.term, self.cell, self.route) for p in m.parameters())

    def resident_params(self) -> int:                            # everything in the file, the codebook included
        return sum(p.numel() for p in self.parameters()) + self.codebook.numel()


class Sampler:
    def __init__(self, G, lmax, gen):
        self.g = Gates(G); self.lmax, self.gen = lmax, gen; self.NX = torch.tensor(self.g.NX); self.termT = torch.tensor(self.g.term.astype(np.int64))
        self.pw = (self.g.G + 1) ** torch.arange(self.g.NS)

    def sample(self, B):
        g, gen = self.g, self.gen; L = torch.randint(1, self.lmax + 1, (B,), generator=gen); legs = torch.randint(0, g.NL, (B, self.lmax), generator=gen)
        qg = torch.where(torch.rand(B, g.G, generator=gen) < 0.25, torch.zeros(B, g.G, dtype=torch.long), 1 + torch.randint(0, 2, (B, g.G), generator=gen))
        q = (qg * (3 ** torch.arange(g.G - 1, -1, -1))).sum(1); s = torch.randint(0, g.NS, (B,), generator=gen)
        return q, s, legs, L

    def exact(self, q, s, legs, L):
        """Value vectors behind every leg (list from the end inwards) and the valid route mask at leg 0."""
        T = self.termT[q]; tabs = [(None, T)]
        for j in range(legs.shape[1] - 1, 0, -1):
            a, b = legs[:, j] // self.g.NT, legs[:, j] % self.g.NT; m = j < L
            T2 = torch.maximum(T.gather(1, self.NX[a]), T.gather(1, self.NX[b])); T = torch.where(m[:, None], T2, T); tabs.append((j, T2))
        a, b = legs[:, 0] // self.g.NT, legs[:, 0] % self.g.NT; ar = torch.arange(len(q))
        va, vb = T[ar, self.NX[a, s]], T[ar, self.NX[b, s]]
        return tabs, torch.stack([va >= vb, vb >= va], 1)


def forward_loss(model, smp, q, s, legs, L, aid=1.0):
    tabs, valid = smp.exact(q, s, legs, L); G = model.cfg.G; loss_aid = torch.zeros(()); commit = torch.zeros(()); zs, labs = [], []
    c, cm = model.snap(model.start(q)); commit = commit + cm
    def aid_loss(cc, T, m):
        nonlocal loss_aid
        if m.any():
            loss_aid = loss_aid + aid * F.cross_entropy(model.dp_head(cc[m]).view(-1, G + 1), T[m].reshape(-1))
            zs.append(cc[m].detach()); labs.append((T[m] * smp.pw).sum(1))
    aid_loss(c, tabs[0][1], torch.ones(len(q), dtype=torch.bool))
    for (j, T2) in tabs[1:]:
        m = j < L
        if not m.any(): continue
        c2, cm = model.snap(model.step_leg(c, legs[:, j]), m); commit = commit + cm; c = torch.where(m[:, None], c2, c); aid_loss(c2, T2, m)
    logits = model.decide(c, legs[:, 0], s); lp = F.log_softmax(logits, -1)
    loss = -(torch.logsumexp(lp.masked_fill(~valid, -1e9), -1)).mean()
    acc = valid[torch.arange(len(q)), logits.argmax(1)].float().mean().item()
    return loss, loss_aid, commit, zs, labs, acc


@torch.no_grad()
def extract(model) -> dict:
    """Integer tables over the codes in use, renumbered 0..K-1 by first use from the start table."""
    model.eval(); g = model.g; cb = model.codebook; dev = cb.device
    def snap_ids(z): return model.nearest(torch.tanh(z))
    term = snap_ids(model.start(torch.arange(g.NQ, device=dev))); order = []; seen = set(); todo = list(dict.fromkeys(term.tolist())); cell = {}
    while todo:                                                    # codes reachable through the leg step, with their rows
        cs = [c for c in todo if c not in seen]; todo = []
        if not cs: break
        for c in cs: seen.add(c); order.append(c)
        ct = torch.tensor(cs, device=dev); rows = snap_ids(model.step_leg(cb[ct].repeat_interleave(g.NL, 0), torch.arange(g.NL, device=dev).repeat(len(cs)))).view(len(cs), g.NL)
        for c, r in zip(cs, rows.tolist()): cell[c] = r
        todo = list(dict.fromkeys(x for r in rows.tolist() for x in r if x not in seen))
    ren = {c: i for i, c in enumerate(order)}; K = len(order); ct = torch.tensor(order, device=dev)
    route = torch.zeros(K, g.NL, g.NS, dtype=torch.uint8)
    for i0 in range(0, K, 64):
        cc = ct[i0:i0 + 64]; n = len(cc)
        lg = model.decide(cb[cc].repeat_interleave(g.NL * g.NS, 0), torch.arange(g.NL, device=dev).repeat_interleave(g.NS).repeat(n), torch.arange(g.NS, device=dev).repeat(n * g.NL))
        route[i0:i0 + n] = lg.argmax(1).view(n, g.NL, g.NS).to(torch.uint8).cpu()
    return {"G": g.G, "n_codes": K, "term": np.array([ren[c] for c in term.tolist()]), "cell": np.array([[ren[x] for x in cell[c]] for c in order]),
            "route": route.numpy(), "code_ids": order}


def machine_train(model, ex, gen, deadline, batch=1024, lr=1e-3, check_every=1000, scale=20.0, log=None, min_steps=0):
    """Train the three functions on the exact machine itself, uniformly: every (value vector, leg) pair for the leg
    step, every (value vector, leg, gate state) triple for the route, every requirement for the start.
    The carry of vector v is its code.  Codes are trained too.  Stops when every entry is right or at the deadline."""
    g = model.g; N = ex["n_codes"]; cellT = torch.tensor(ex["cell"], dtype=torch.long); validT = torch.tensor(ex["valid"]); termT = torch.tensor(ex["term"], dtype=torch.long)
    cb = torch.nn.Parameter(model.codebook[:N].clone()); opt = torch.optim.AdamW(list(model.parameters()) + [cb], lr=lr, weight_decay=0.0); it = 0; t0 = time.time(); last = None
    def logits(z): return -scale * torch.cdist(torch.tanh(z), cb).pow(2)
    while time.time() < deadline:
        it += 1; model.train(); v = torch.randint(0, N, (batch,), generator=gen); l = torch.randint(0, g.NL, (batch,), generator=gen); sg = torch.randint(0, g.NS, (batch,), generator=gen)
        q = torch.randint(0, g.NQ, (min(batch, 4 * g.NQ),), generator=gen); c = cb[v]
        loss = F.cross_entropy(logits(model.step_leg(c, l)), cellT[v, l]) + F.cross_entropy(logits(model.start(q)), termT[q])
        vm = validT[v, l, sg]; ok = torch.stack([(vm & 1) > 0, (vm & 2) > 0], 1); lp = F.log_softmax(model.decide(c, l, sg), -1)
        loss = loss - torch.logsumexp(lp.masked_fill(~ok, -1e9), -1).mean()
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(list(model.parameters()) + [cb], 1.0); opt.step()
        if it % check_every == 0:
            with torch.no_grad():                                   # entries wrong on a sample of the machine (the certificate is the full check)
                model.eval(); v = torch.randint(0, N, (20000,), generator=gen); l = torch.randint(0, g.NL, (20000,), generator=gen); sg = torch.randint(0, g.NS, (20000,), generator=gen)
                ce = float((logits(model.step_leg(cb[v], l)).argmax(1) != cellT[v, l]).float().mean()); vm = validT[v, l, sg]
                re = float((((vm >> model.decide(cb[v], l, sg).argmax(1)) & 1) == 0).float().mean())
            last = {"machine_step": it, "loss": round(loss.item(), 5), "cell_wrong_sampled": ce, "route_wrong_sampled": re, "sec": round(time.time() - t0, 1)}
            if log is not None: log.append(last)
            print(json.dumps(last), flush=True)
            if ce == 0 and re == 0 and it >= min_steps: break
            if it % (20 * check_every) == 0:
                for gq in opt.param_groups: gq["lr"] *= 0.5
    with torch.no_grad(): model.codebook[:N] = cb
    return it


@torch.no_grad()
def allocate_all(model, ex):
    """One code per exact value vector.  A shortest job reaching each vector is read off the exact tables, the
    network's continuous carry for that job becomes the vector's code.  Needs n_codes >= number of vectors."""
    N = ex["n_codes"]; assert N <= model.cfg.n_codes, f"{N} exact vectors, {model.cfg.n_codes} codes"; g = model.g
    parent = np.full(N, -1, np.int64); pleg = np.full(N, -1, np.int64); root = np.full(N, -1, np.int64); depth = np.full(N, -1, np.int64)
    for q in range(g.NQ - 1, -1, -1): root[ex["term"][q]] = q
    front = np.unique(ex["term"]); depth[front] = 0
    while len(front):
        nxt = ex["cell"][front]; new = []
        for i, u in enumerate(front):
            for l in np.nonzero(depth[nxt[i]] < 0)[0]:
                v = nxt[i, l]
                if depth[v] < 0: depth[v] = depth[u] + 1; parent[v] = u; pleg[v] = l; root[v] = root[u]; new.append(v)
        front = np.array(new, np.int64)
    dmax = int(depth.max()); path = np.full((N, max(dmax, 1)), -1, np.int64)
    for v in range(N):
        u = v; d = depth[v]
        while parent[u] >= 0: d -= 1; path[v, d] = pleg[u]; u = parent[u]
    was = int(model.quant_on); model.quant_on.fill_(0); model.eval(); c, _ = model.snap(model.start(torch.tensor(root))); pt = torch.tensor(path)
    for d in range(path.shape[1]):
        m = pt[:, d] >= 0; c2, _ = model.snap(model.step_leg(c, pt[:, d].clamp(min=0))); c = torch.where(m[:, None], c2, c)
    cb = torch.full_like(model.codebook, 5.0); cb[:N] = c; model.codebook.copy_(cb); model.ema_sum.copy_(cb); model.ema_n.fill_(1.0); model.quant_on.fill_(1); model.train()


def save(model, path, extra=None):
    buf = io.BytesIO(); torch.save({"cfg": asdict(model.cfg), "state": model.state_dict(), "extra": extra or {}}, buf); data = buf.getvalue(); open(path, "wb").write(data)
    return hashlib.sha256(data).hexdigest()


def load(path):
    data = open(path, "rb").read(); ck = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
    m = Reader(ReaderCfg(**ck["cfg"])); m.load_state_dict(ck["state"]); m.eval(); m.sha256 = hashlib.sha256(data).hexdigest(); return m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--G", type=int, default=2); ap.add_argument("--width", type=int, default=128); ap.add_argument("--n-codes", type=int, default=64)
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--lmax", type=int, default=4); ap.add_argument("--budget", type=float, default=3600.0)
    ap.add_argument("--batch", type=int, default=512); ap.add_argument("--lr", type=float, default=1e-3); ap.add_argument("--min-warmup", type=int, default=1500)
    ap.add_argument("--warmup", type=int, default=20000); ap.add_argument("--switch-loss", type=float, default=0.01); ap.add_argument("--post", type=int, default=3000)
    ap.add_argument("--alloc", default="exact"); ap.add_argument("--machine-share", type=float, default=0.8); ap.add_argument("--rounds", type=int, default=40); ap.add_argument("--repair-steps", type=int, default=300); ap.add_argument("--name", default="")
    a = ap.parse_args(); torch.set_num_threads(1); torch.manual_seed(a.seed); gen = torch.Generator().manual_seed(a.seed)
    name = a.name or f"v4r{'' if a.alloc == 'sampled' else '2'}_g{a.G}_w{a.width}_s{a.seed}"; out = f"runs/{name}"; os.makedirs(out, exist_ok=True); t0 = time.time()
    g = Gates(a.G); clo = g.exact_closure(); ex = g.compile_exact(clo); exact_seconds = time.time() - t0
    model = Reader(ReaderCfg(G=a.G, width=a.width, n_codes=a.n_codes)); smp = Sampler(a.G, a.lmax, gen)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.0); it, switch, ema, recent, log = 0, None, 1.0, [], []
    over = lambda: time.time() - t0 > a.budget
    while not over():                                               # ---- training ----
        it += 1; model.train(); loss, la, cm, zs, labs, acc = forward_loss(model, smp, *smp.sample(a.batch))
        ema = 0.98 * ema + 0.02 * loss.item(); recent = (recent + [(torch.cat(zs), torch.cat(labs))])[-16:]
        opt.zero_grad(); (loss + la + model.cfg.beta * cm).backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        if switch is None and ((it >= a.min_warmup and ema < a.switch_loss) or it >= a.warmup):
            if a.alloc == "sampled":                                # first protocol: one code per value vector SEEN in the last 16 batches
                z, lab = torch.cat([r[0] for r in recent]), torch.cat([r[1] for r in recent]); u = torch.unique(lab)
                if len(u) > a.n_codes: keep = torch.isin(lab, u[:a.n_codes]); z, lab = z[keep], lab[keep]
                model.init_codebook(z, gen, labels=lab)
            else: allocate_all(model, ex)                           # one code per exact value vector, each placed at the carry the network gives it
            switch = it; log.append({"step": it, "note": f"quantiser on, {int((model.codebook[:, 0] < 4).sum())} codes placed for {ex['n_codes']} exact vectors"})
        if it % 500 == 0: log.append({"step": it, "loss": round(loss.item(), 5), "ema": round(ema, 5), "acc": round(acc, 4), "sec": round(time.time() - t0, 1)}); print(json.dumps(log[-1]), flush=True)
        if switch is not None and it >= switch + a.post: break
    machine_steps = 0
    if switch is not None and a.alloc == "exact" and a.machine_share > 0:
        machine_steps = machine_train(model, ex, gen, t0 + a.budget * a.machine_share, log=log)
    train_seconds = time.time() - t0 - exact_seconds; train_steps = it; rounds = []; clean = False; cert = None; pool = []
    if switch is not None:                                          # ---- certify and repair ----
        opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.0)
        for rnd in range(a.rounds + 1):
            tab = extract(model); cert = certify(tab, ex, want_wrong=20000, max_seconds=max(60.0, a.budget - (time.time() - t0)))
            rounds.append({"round": rnd, "pairs": cert["pairs"], "codes_used": cert["codes_used"], "exact_vectors_reached": cert["exact_vectors_reached"], "depth": cert["depth"],
                           "route_checks": cert["route_checks"], "route_wrong": cert["route_wrong"], "shortest_witness_legs": cert["shortest_witness_legs"],
                           "closure_seconds": round(cert["seconds"], 2), "complete": cert["complete"], "sec": round(time.time() - t0, 1)})
            print(json.dumps(rounds[-1]), flush=True)
            if cert["route_wrong"] == 0 and cert["complete"]: clean = True; break
            if rnd == a.rounds or over(): break
            if a.alloc == "exact":                                 # protocol 2: a failed certificate sends the reader back to the exact machine, not to witness jobs
                machine_steps += machine_train(model, ex, gen, t0 + a.budget, lr=3e-4, min_steps=3000, log=log); continue
            pool = (pool + cert["witnesses"])[-200000:]; lw = max(len(w["legs"]) for w in pool)
            for _ in range(a.repair_steps):
                it += 1; model.train(); pick = [pool[i] for i in torch.randint(0, len(pool), (a.batch,), generator=gen).tolist()]
                legs = torch.zeros(a.batch, max(lw, 2), dtype=torch.long)
                for i, w in enumerate(pick): legs[i, :len(w["legs"])] = torch.tensor(w["legs"])
                wq, ws, wL = torch.tensor([w["requirements"] for w in pick]), torch.tensor([w["gates"] for w in pick]), torch.tensor([len(w["legs"]) for w in pick])
                l1, a1, c1, *_ = forward_loss(model, Sampler(a.G, legs.shape[1], gen), wq, ws, legs, wL)
                l2, a2, c2, *_ = forward_loss(model, smp, *smp.sample(a.batch))
                opt.zero_grad(); (l1 + a1 + l2 + a2 + model.cfg.beta * (c1 + c2)).backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
    model.eval(); sha = save(model, f"{out}/checkpoint.pt", {"args": vars(a)}); res = {"name": name, "args": vars(a), "checkpoint_sha256": sha}
    if cert is not None:
        tab = extract(model); nbytes = write_tables(f"{out}/tables.bin", a.G, tab["term"], tab["cell"], tab["route"])
        res.update({"tables_bytes": nbytes, "tables_sha256": hashlib.sha256(open(f"{out}/tables.bin", "rb").read()).hexdigest(), "tables_codes": tab["n_codes"],
                    "witnesses_last_round": cert["witnesses"][:20]})
    res.update({"G": a.G, "exact_vectors": ex["n_codes"], "exact_closure_and_compile_seconds": round(exact_seconds, 2), "active_parameters_per_decision": model.active_params(),
                "resident_parameters": model.resident_params(), "train_steps": train_steps, "machine_steps": machine_steps, "train_seconds": round(train_seconds, 1), "quantiser_switched_on_at": switch,
                "repair_rounds": rounds, "repair_steps": it - train_steps, "clean": clean, "status": "complete" if clean else ("incomplete: budget or rounds exhausted" if switch is not None else "incomplete: never reached the quantiser switch"),
                "wall_seconds": round(time.time() - t0, 1), "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "log": log, "torch": torch.__version__})
    json.dump(res, open(f"{out}/manifest.json", "w"), indent=1); print("saved", out, res["status"], flush=True)


if __name__ == "__main__":
    main()
