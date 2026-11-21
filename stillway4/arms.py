"""Learned arms for the approvals workflow (v0.4, M2).  Arms and who supplies what: docs/v04_spec.md section 2.

    python -m stillway4.arms --arm proc --size s --seed 1          # arms: proc, macro, cont, vq      sizes: s, m, l

All arms read the same event records and are trained on the same logged documents (events and the 5 statuses
after every event).  The policy bank is a table of one vector per policy ID in every arm.

proc    typed registers written by rule; a router picks one of C procedure codes per event; a code says which
        slots to recompute (a learned gate over two features of each slot: "is the slot named by the event",
        "is in the jurisdiction named by the event") and which policy to recompute them under (current policy of
        the slot's jurisdiction, the slot's pinned policy, or the policy named by the event).  The executor
        recomputes exactly the gated slots with the status function and leaves every other status register
        untouched.  Trained soft (mixtures), then hard.
macro   the same executor with the selection written by hand; only the bank and the status function are learned.
cont    a GRU; the hidden vector is the memory.            vq   the same with the memory snapped to 8 codes of 64.
direct  the cont arm re-reading the whole history at every step (no memory kept); same weights, counted separately.
"""
from __future__ import annotations

import argparse, hashlib, io, json, os, time
from dataclasses import asdict, dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from . import approvals as A

S, NJ, T = A.S, A.NJ, A.T
SIZES = {"proc": {"s": 256, "m": 512, "l": 960}, "macro": {"s": 256, "m": 512, "l": 960}, "cont": {"s": 136, "m": 280, "l": 540}, "vq": {"s": 128, "m": 272, "l": 532}}
N_CODES_PROC = 8


@dataclass
class ArmCfg:
    arm: str = "proc"
    width: int = 256
    n_pids: int = 64                 # bank rows: index 0 EXPIRED, 1..n_pids-2 policies, last row = "no policy named"
    d_pid: int = 16


def facts_onehot(lvl, age, tag, evid):
    return torch.cat([F.one_hot(lvl.clamp(min=0), 4), F.one_hot(age.clamp(min=0), 2), F.one_hot(tag.clamp(min=0), 3), F.one_hot(evid.clamp(min=0), 2)], -1).float()


class Proc(nn.Module):
    def __init__(self, cfg: ArmCfg):
        super().__init__(); self.cfg = cfg; W, d = cfg.width, cfg.d_pid
        self.bank = nn.Embedding(cfg.n_pids, d)
        self.expert = nn.Sequential(nn.Linear(d + 11, W), nn.ReLU(), nn.Linear(W, W), nn.ReLU(), nn.Linear(W, 4))
        self.router = nn.Parameter(torch.zeros(A.NK, N_CODES_PROC)); self.gate = nn.Parameter(torch.randn(N_CODES_PROC, 3) * 0.5); self.src = nn.Parameter(torch.randn(N_CODES_PROC, 3) * 0.1)
        nn.init.normal_(self.router, std=0.5)
        if cfg.arm == "macro":                                    # selection written by hand (codes 0 slot/current, 1 slot/pinned, 2 jurisdiction/named, 3 nothing)
            r = torch.full((A.NK, N_CODES_PROC), -20.0)
            for k, c in ((A.SIGN, 0), (A.CORRECT, 1), (A.MOVE, 0), (A.AMEND_RETRO, 2), (A.AMEND_PRO, 3), (A.EXPIRE, 2), (A.OVERRIDE, 3), (A.WAIT, 3)): r[k, c] = 20.0
            g = torch.zeros(N_CODES_PROC, 3); g[:, 2] = -20.0; g[0] = torch.tensor([40.0, 0.0, -20.0]); g[1] = g[0]; g[2] = torch.tensor([0.0, 40.0, -20.0])
            s = torch.zeros(N_CODES_PROC, 3); s[0, 0] = 20.0; s[1, 1] = 20.0; s[2, 2] = 20.0
            for p, v in ((self.router, r), (self.gate, g), (self.src, s)): p.data.copy_(v); p.requires_grad_(False)

    def pid_row(self, pid): return torch.where(pid < 0, self.cfg.n_pids - 1, pid)

    def tables(self):
        """The discrete procedure tables: code per event kind; per code, the gate weights and the policy source."""
        return {"code_of_kind": self.router.argmax(1).tolist(), "gate_weights": self.gate.tolist(), "source_of_code": self.src.argmax(1).tolist()}

    def run(self, d: dict, mode: str = "hard", tau: float = 1.0, iv: dict | None = None, bank_weight=None, unknown=None, rowmap=None, lookup=None):
        """A batch of documents.  mode "soft": mixtures, returns log-probabilities (B,T,S,4).  mode "hard": the discrete
        executor; returns (statuses (B,T,S), log-probabilities, trace).  iv: interventions for hard mode, each a dict
        with a boolean row/step mask "at" (B,T) and one of: "code" (B,T) code to use, "suppress" True, "slot" (B,T), "jur" (B,T).
        bank_weight: use this policy table instead of self.bank (a pinned bank version).  unknown: boolean (n_pids,) rows the
        pinned bank does not know; a slot recomputed under such a policy gets ABSTAIN.  rowmap: policy ID -> bank row (the
        registry; an expired ID maps to row 0).  lookup: (rows, 36) retrieval index of audited decisions, -1 = no entry;
        a hit replaces the status function's answer."""
        B = d["tenant"].shape[0]; ar = torch.arange(B); bw = self.bank.weight if bank_weight is None else bank_weight; dd = bw.shape[1]
        jur = torch.full((B, S), -1); lvl = torch.zeros(B, S, dtype=torch.long); age = torch.zeros(B, S, dtype=torch.long); tag = torch.zeros(B, S, dtype=torch.long)
        evid = torch.zeros(B, S, dtype=torch.long); pj = torch.full((B, NJ), -1); none = bw.shape[0] - 1; row = lambda x: torch.where(x < 0, none, x)
        evp = d["ev_pid"] if rowmap is None else torch.where(d["ev_pid"] >= 0, rowmap[d["ev_pid"].clamp(min=0)], d["ev_pid"])
        pin = torch.full((B, S), none); pin_e = bw[pin]; stat_p = F.one_hot(torch.zeros(B, S, dtype=torch.long), 4).float(); stat = torch.zeros(B, S, dtype=torch.long)
        out_lp, out_st, trace = [], [], {"code": [], "gate": [], "n_recomputed": []}
        for t in range(T):
            k, sl, jj, pid, ost = d["ev_kind"][:, t], d["ev_slot"][:, t], d["ev_jur"][:, t], evp[:, t], d["ev_ostat"][:, t]
            # ---- registers, by rule: a field shown overwrites its register ----
            m = d["ev_lvl"][:, t] >= 0
            lvl[ar[m], sl[m]] = d["ev_lvl"][m, t]; age[ar[m], sl[m]] = d["ev_age"][m, t]; tag[ar[m], sl[m]] = d["ev_tag"][m, t]; evid[ar[m], sl[m]] = d["ev_evid"][m, t]
            m = (sl >= 0) & (jj >= 0); jur[ar[m], sl[m]] = jj[m]
            m = (sl < 0) & (jj >= 0) & (pid >= 0); pj[ar[m], jj[m]] = pid[m]
            m = ost >= 0
            if m.any():
                stat_p = stat_p.clone(); stat_p[ar[m], sl[m]] = F.one_hot(ost[m], 4).float(); stat = stat.clone(); stat[ar[m], sl[m]] = ost[m]
            # ---- arguments (explicit) and slot features ----
            a_sl, a_j = sl, jj
            if iv is not None:
                for x in iv:
                    at = x["at"][:, t]
                    if "slot" in x: a_sl = torch.where(at, x["slot"][:, t], a_sl)
                    if "jur" in x: a_j = torch.where(at, x["jur"][:, t], a_j)
            u = torch.stack([(torch.arange(S)[None] == a_sl[:, None]).float(), ((jur == a_j[:, None]) & (a_j[:, None] >= 0)).float(), torch.ones(B, S)], -1)       # (B,S,3)
            cur = row(pj.gather(1, jur.clamp(min=0)).masked_fill(jur < 0, -1))                    # (B,S) current policy of each slot's jurisdiction
            shown = row(pid)[:, None].expand(B, S); fo = facts_onehot(lvl, age, tag, evid)
            if mode == "soft":
                pi = torch.softmax(self.router[k] / tau, -1)                                                   # (B,C)
                g = torch.sigmoid(torch.einsum("bsf,cf->bcs", u, self.gate) / tau)                             # (B,C,S)
                al = torch.softmax(self.src / tau, -1)                                                         # (C,3)
                cand = torch.stack([bw[cur], pin_e, bw[shown]], 2)                                             # (B,S,3,d)
                se = torch.einsum("ck,bskd->bcsd", al, cand)                                                   # (B,C,S,d)
                ok = torch.softmax(self.expert(torch.cat([cand, fo[:, :, None].expand(B, S, 3, 11)], -1)), -1) # the status function once per candidate policy
                o = torch.einsum("ck,bskx->bcsx", al, ok)                                                      # (B,C,S,4)
                w = (pi[:, :, None] * g)                                                                       # (B,C,S)
                keep = 1.0 - w.sum(1)
                stat_p = (w[..., None] * o).sum(1) + keep[..., None] * stat_p
                pin_e = (w[..., None] * se).sum(1) + keep[..., None] * pin_e
                out_lp.append(torch.log(stat_p.clamp(min=1e-9)))
            else:
                c = self.router[k].argmax(1); sup = torch.zeros(B, dtype=torch.bool)
                if iv is not None:
                    for x in iv:
                        at = x["at"][:, t]
                        if "code" in x: c = torch.where(at, x["code"][:, t], c)
                        if x.get("suppress"): sup |= at
                g = (torch.einsum("bsf,bf->bs", u, self.gate[c]) > 0) & ~sup[:, None]                          # (B,S) which slots are recomputed
                src = self.src[c].argmax(1)                                                                    # (B,)
                cand = torch.stack([cur, pin, shown], 2); spid = cand[ar, :, src]                              # (B,S)
                lp = torch.log(F.one_hot(stat, 4).float().clamp(min=1e-9)) if not self.training else torch.log(stat_p.clamp(min=1e-9))
                if g.any():
                    bi, si = g.nonzero(as_tuple=True)                                                          # only the gated slots run the status function
                    o = self.expert(torch.cat([bw[spid[bi, si]], fo[bi, si]], -1)); ol = F.log_softmax(o, -1); os_ = o.argmax(1)
                    if unknown is not None: os_ = torch.where(unknown[spid[bi, si]] & (lvl[bi, si] > 0), A.ABSTAIN, os_)
                    if lookup is not None:
                        lk = lookup[spid[bi, si], A.fact_index(lvl[bi, si].clamp(min=1), age[bi, si], tag[bi, si], evid[bi, si])]; os_ = torch.where((lk >= 0) & (lvl[bi, si] > 0), lk, os_)
                    stat = stat.clone(); stat[bi, si] = os_; pin = pin.clone(); pin[bi, si] = spid[bi, si]
                    lp = lp.clone(); lp[bi, si] = ol; stat_p = stat_p.clone(); stat_p[bi, si] = ol.exp()
                out_lp.append(lp); out_st.append(stat); trace["code"].append(c); trace["gate"].append(g); trace["n_recomputed"].append(g.sum(1))
        if mode == "soft": return torch.stack(out_lp, 1)
        return torch.stack(out_st, 1), torch.stack(out_lp, 1), {k: torch.stack(v, 1) for k, v in trace.items()}

    def active_params(self) -> int:                               # one decision: router row, one code's gate and source, the status function, one bank row
        return A.NK * 0 + N_CODES_PROC + 3 + 3 + sum(p.numel() for p in self.expert.parameters()) + self.cfg.d_pid

    def macs_per_slot(self) -> int:
        return sum(m.in_features * m.out_features for m in self.expert if isinstance(m, nn.Linear))


class Gru(nn.Module):
    def __init__(self, cfg: ArmCfg):
        super().__init__(); self.cfg = cfg; H, d = cfg.width, cfg.d_pid
        self.bank = nn.Embedding(cfg.n_pids, d)
        self.e_kind = nn.Embedding(A.NK, 16); self.e_slot = nn.Embedding(S + 1, 8); self.e_jur = nn.Embedding(NJ + 1, 8); self.e_ost = nn.Embedding(5, 4)
        self.enc = nn.Linear(16 + 8 + 8 + 4 + 11 + 1 + d, 64); self.cell = nn.GRUCell(64, H); self.head = nn.Linear(H, S * 4)
        if cfg.arm == "vq":
            self.to_slots = nn.Linear(H, 8 * 16); self.from_slots = nn.Linear(8 * 16, H)
            self.register_buffer("codebook", torch.randn(8, 64, 16) * 0.1); self.register_buffer("ema_n", torch.ones(8, 64)); self.register_buffer("ema_sum", self.codebook.clone()); self.register_buffer("quant_on", torch.tensor(0))

    def encode(self, d, t):
        f = facts_onehot(d["ev_lvl"][:, t], d["ev_age"][:, t], d["ev_tag"][:, t], d["ev_evid"][:, t]) * (d["ev_lvl"][:, t] >= 0).float()[:, None]
        pid = d["ev_pid"][:, t]; row = torch.where(pid < 0, self.cfg.n_pids - 1, pid)
        x = torch.cat([self.e_kind(d["ev_kind"][:, t]), self.e_slot(d["ev_slot"][:, t] + 1), self.e_jur(d["ev_jur"][:, t] + 1), self.e_ost(d["ev_ostat"][:, t] + 1), f,
                       (d["ev_lvl"][:, t] >= 0).float()[:, None], self.bank(row)], 1)
        return torch.relu(self.enc(x))

    def quantise(self, h):
        z = self.to_slots(h).view(-1, 8, 16)
        if not bool(self.quant_on): return torch.tanh(self.from_slots(z.flatten(1))), z.new_zeros(()), None
        dist = z.pow(2).sum(-1, keepdim=True) - 2 * torch.einsum("bsd,skd->bsk", z, self.codebook) + self.codebook.pow(2).sum(-1)[None]
        ids = dist.argmin(-1); zq = self.codebook[torch.arange(8)[None], ids]
        if self.training:
            with torch.no_grad():
                oh = F.one_hot(ids, 64).float(); self.ema_n.mul_(0.99).add_(oh.sum(0), alpha=0.01); self.ema_sum.mul_(0.99).add_(torch.einsum("bsk,bsd->skd", oh, z.detach()), alpha=0.01)
                live = oh.sum(0) > 0; self.codebook[live] = (self.ema_sum / self.ema_n[..., None])[live]
        return torch.tanh(self.from_slots((z + (zq - z).detach()).flatten(1))), (z - zq.detach()).pow(2).mean(), ids

    def run(self, d, mode="hard", tau=1.0, iv=None):
        B = d["tenant"].shape[0]; h = torch.zeros(B, self.cfg.width); lps = []; commit = torch.zeros(()); zs = []
        for t in range(T):
            h = self.cell(self.encode(d, t), h)
            if self.cfg.arm == "vq":
                if not bool(self.quant_on): zs.append(self.to_slots(h).view(-1, 8, 16).detach())
                h, cm, _ = self.quantise(h); commit = commit + cm
            lps.append(F.log_softmax(self.head(h).view(B, S, 4), -1))
        lp = torch.stack(lps, 1); self.last_commit = commit; self.last_z = zs
        return lp if mode == "soft" else (lp.argmax(-1), lp, {})

    def active_params(self) -> int:
        n = sum(p.numel() for m in (self.enc, self.cell, self.head, self.e_kind, self.e_slot, self.e_jur, self.e_ost) for p in m.parameters()) + self.cfg.d_pid
        return n + (sum(p.numel() for m in (self.to_slots, self.from_slots) for p in m.parameters()) if self.cfg.arm == "vq" else 0)

    def macs_per_step(self) -> int:
        H = self.cfg.width; n = self.enc.in_features * 64 + 3 * H * (H + 64) + H * S * 4
        return n + (2 * H * 128 if self.cfg.arm == "vq" else 0)


def build(cfg: ArmCfg): return Proc(cfg) if cfg.arm in ("proc", "macro") else Gru(cfg)


def save(model, path, extra=None):
    buf = io.BytesIO(); torch.save({"cfg": asdict(model.cfg), "state": model.state_dict(), "extra": extra or {}}, buf); data = buf.getvalue(); open(path, "wb").write(data)
    return hashlib.sha256(data).hexdigest()


def load(path):
    data = open(path, "rb").read(); ck = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
    m = build(ArmCfg(**ck["cfg"])); m.load_state_dict(ck["state"]); m.eval(); m.sha256 = hashlib.sha256(data).hexdigest(); return m


def sub(d, idx): return {k: v[idx] for k, v in d.items()}


@torch.no_grad()
def evaluate(model, d, batch=1000, **kw) -> dict:
    """Statuses for every document; success = every status right after every event; protected = statuses outside the affected set that changed."""
    model.eval(); outs = []; n_rec = []
    for i in range(0, len(d["tenant"]), batch):
        st, _, tr = model.run(sub(d, slice(i, i + batch)), "hard", **kw); outs.append(st)
        if "n_recomputed" in tr: n_rec.append(tr["n_recomputed"])
    st = torch.cat(outs); ok = (st == d["labels"]); prev = torch.cat([torch.zeros_like(st[:, :1]), st[:, :-1]], 1)
    prot = ((st != prev) & ~d["affected"]).sum().item()
    return {"success": ok.flatten(1).all(1).float().mean().item(), "status_accuracy": ok.float().mean().item(), "protected_changed": int(prot), "outputs": st,
            "doc_ok": ok.flatten(1).all(1), "slots_recomputed_per_event": (torch.cat(n_rec).float().mean().item() if n_rec else None)}


def save_raw(path, uni, data, outputs):
    """Raw evidence for an independent grader: the events and the statuses reported, plus every policy's content."""
    blob = {"pid_rule": uni.pid_rule.numpy().astype(np.int16)}
    for k, o in outputs.items():
        blob[f"{k}_out"] = o.numpy().astype(np.int8); blob[f"{k}_tenant"] = data[k]["tenant"].numpy().astype(np.int8)
        blob[f"{k}_events"] = torch.stack([data[k]["ev_" + f] for f in A.FIELDS], -1).numpy().astype(np.int16)
    np.savez_compressed(path, **blob)


def make_data(seed: int, n_train=20000, n_dev=2000, n_test=4000, salt: int = 0):
    """The logged documents every arm trains on, and the test sets.  One universe of 60 training policies per seed."""
    gen = torch.Generator().manual_seed(1000003 * seed + 17 + salt); uni = A.Universe.make(60, A.TRAIN_RULES, gen)
    return uni, {"train": A.sample_docs(uni, n_train, gen, combos="train"), "dev": A.sample_docs(uni, n_dev, gen, combos="train"),
                 "test_iid": A.sample_docs(uni, n_test, gen, combos="train"), "test_novel": A.sample_docs(uni, n_test, gen, combos="novel")}


def train(model, data, seed, steps=6000, batch=256, lr=2e-3, budget=3600.0, log=None):
    torch.manual_seed(seed); gen = torch.Generator().manual_seed(seed); opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr, weight_decay=0.0)
    tr = data["train"]; N = len(tr["tenant"]); t0 = time.time(); arm = model.cfg.arm; hard_from = int(0.7 * steps); vq_on = int(0.5 * steps)
    for it in range(1, steps + 1):
        if time.time() - t0 > budget: break
        model.train(); d = sub(tr, torch.randint(0, N, (batch,), generator=gen)); extra = 0.0
        for g_ in opt.param_groups: g_["lr"] = lr * (0.1 + 0.9 * min(1.0, (steps - it) / (0.5 * steps)))
        if arm == "proc":
            if it <= hard_from and time.time() - t0 < 0.4 * budget: lp = model.run(d, "soft", tau=max(0.2, 1.0 - 0.8 * it / (0.6 * steps)))
            else: _, lp, _ = model.run(d, "hard")
        elif arm == "macro": _, lp, _ = model.run(d, "hard")
        else:
            lp = model.run(d, "soft"); extra = 0.25 * model.last_commit if arm == "vq" else 0.0
            if arm == "vq" and it == vq_on:                        # codebook from the memories seen in this batch, then quantised from here on
                z = torch.cat(model.last_z)                       # (n,8,16)
                for s_ in range(8):
                    zz = z[:, s_]; c = zz[torch.randperm(len(zz), generator=gen)[:64]].clone()
                    for _ in range(15):
                        a_ = torch.cdist(zz, c).argmin(1)
                        for k_ in range(64):
                            if (a_ == k_).any(): c[k_] = zz[a_ == k_].mean(0)
                    model.codebook[s_] = c
                model.ema_sum.copy_(model.codebook); model.ema_n.fill_(1.0); model.quant_on.fill_(1)
        loss = F.nll_loss(lp.reshape(-1, 4), d["labels"].reshape(-1)) + extra
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        if it % 500 == 0 or it == steps:
            e = evaluate(model, data["dev"]); row = {"step": it, "loss": round(loss.item(), 4), "dev_success": round(e["success"], 4), "dev_status_accuracy": round(e["status_accuracy"], 5), "sec": round(time.time() - t0, 1)}
            if log is not None: log.append(row)
            print(json.dumps(row), flush=True)
    return it, time.time() - t0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--arm", default="proc"); ap.add_argument("--size", default="s"); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--steps", type=int, default=0); ap.add_argument("--budget", type=float, default=3600.0); ap.add_argument("--name", default=""); ap.add_argument("--salt", type=int, default=0)
    a = ap.parse_args(); torch.set_num_threads(1); name = a.name or f"v4a_{a.arm}_{a.size}_s{a.seed}"; out = f"runs/{name}"; os.makedirs(out, exist_ok=True)
    a.steps = a.steps or {"proc": 5000, "macro": 3000, "cont": 16000, "vq": 16000}[a.arm]
    uni, data = make_data(a.seed, salt=a.salt); torch.manual_seed(a.seed); model = build(ArmCfg(arm=a.arm, width=SIZES[a.arm][a.size])); log = []
    steps, sec = train(model, data, a.seed, steps=a.steps, budget=a.budget, log=log); model.eval(); sha = save(model, f"{out}/checkpoint.pt", {"args": vars(a)})
    res = {"name": name, "args": vars(a), "arm": a.arm, "width": model.cfg.width, "checkpoint_sha256": sha, "active_parameters_per_decision": model.active_params(),
           "resident_parameters": sum(p.numel() for p in model.parameters()) + sum(b.numel() for n_, b in model.named_buffers() if "codebook" in n_),
           "train_steps": steps, "train_seconds": round(sec, 1), "status": "complete" if steps >= a.steps else "incomplete: budget", "log": log, "torch": torch.__version__,
           "training_information": "20,000 logged documents: events and the 5 statuses after every event; no other label"}
    raw = {}
    for k in ("dev", "test_iid", "test_novel"):
        e = evaluate(model, data[k]); res[k] = {x: e[x] for x in ("success", "status_accuracy", "protected_changed", "slots_recomputed_per_event")}; raw[k] = e["outputs"]
        res[k]["by_family"] = {int(f): [int(((data[k]["family"] == f) & e["doc_ok"]).sum()), int((data[k]["family"] == f).sum())] for f in data[k]["family"].unique().tolist()}
    save_raw(f"{out}/raw_outputs.npz", uni, data, {k: raw[k] for k in ("test_iid", "test_novel")})
    if a.arm in ("proc", "macro"): res["procedure_tables"] = model.tables()
    json.dump(res, open(f"{out}/manifest.json", "w"), indent=1)
    print("saved", out, {k: round(res[k]["success"], 4) for k in ("dev", "test_iid", "test_novel")}, "active params", res["active_parameters_per_decision"], flush=True)


if __name__ == "__main__":
    main()
