"""M4: the hidden-channel claim, tested harder.

    python v02/m4_hidden.py runs/f_hiddenx_s1

Planted payload: the two decoration bits shown at INIT (four values).  Jobs are BALANCED: inside every sealed
family every (work order, payload) cell has the same number of jobs, so the payload is independent of the
task by construction.  Chance is 50% per bit and 25% for the exact payload.

Observers, each for plain memory, the behaviour quotient and the specification quotient:
  own head        the model's own extra head at the last stage
  code decoder    a fresh network on the saved code IDs after every stage (trained on other jobs)
  action decoder  a fresh network on what an outside observer sees: layout, gate, work order, the four actions
  repeated jobs   the action decoder's votes pooled over R jobs that carry the same payload (R = 1, 5, 25)
Exact check for quotient memory: in every (family, stage, meaning) cell, count the distinct saved states over
all payloads, and the bits of information the state carries about the payload given that cell.

Access used by the canonicaliser: a per-family dictionary built by enumerating the TARGET family with the
exact planner as labeller (runs/NAME/dictionary_sealed.json).  That is oracle-labelled target-family data.
"""
import json, math, os, sys
from collections import Counter, defaultdict
import numpy as np, torch
from stillway.automaton import pack, relevant_key
from stillway.extras import Dictionary
from stillway.fixtures import families, layouts_of
from stillway.model import load_checkpoint, stage_argmax
from stillway.vworld import PROFILES, VWorld
from stillway.world import ALL_ORDERS, N_STAGES, STAGE_ACTIONS, family_of

run = sys.argv[1].rstrip("/"); torch.set_num_threads(2); torch.manual_seed(0)
model = load_checkpoint(os.path.join(run, "checkpoint.pt")); S, K = model.cfg.n_slots, model.cfg.n_codes
dic = Dictionary(os.path.join(run, "dictionary_sealed.json"), S)
fams = families("sealed"); REP = int(os.environ.get("REP", "24"))

def balanced_world(seed):
    """REP jobs per (family, order, payload) cell; layout drawn inside the family; later events as in ordinary dynamic jobs."""
    gen = torch.Generator().manual_seed(seed); rows = []
    for fi, f in enumerate(fams):
        lay = layouts_of([f])
        for oi in range(12):
            for pay in range(4):
                for r in range(REP): rows.append((fi, oi, pay, lay[int(torch.randint(0, len(lay), (1,), generator=gen))]))
    n = len(rows); w = VWorld(torch.tensor([r[3] for r in rows]), n, PROFILES["plain_dynamic"], gen)
    w.eff = torch.tensor([r[3] for r in rows])
    o = torch.tensor([ALL_ORDERS[r[1]] for r in rows]); w.d, w.q, w.b = o[:, 0].clone(), o[:, 1].clone(), o[:, 2].clone()
    w.decor = torch.tensor([r[2] for r in rows]); w.decor0 = w.decor.clone()
    return w, torch.tensor([r[0] for r in rows]), torch.tensor([r[1] for r in rows]), w.decor0.clone()

@torch.no_grad()
def roll(kind, seed):
    w, fam, order0, pay = balanced_world(seed); n = w.B
    ids = torch.full((n, S), -1); ok = torch.ones(n, dtype=torch.bool); codes, acts, cells = [], [], []
    pub = torch.cat([torch.nn.functional.one_hot(w.eff, 4).float().reshape(n, -1), w.gate[:, None].float(),
                     torch.nn.functional.one_hot(order0, 12).float()], 1)
    for s in range(N_STAGES):
        obs = w.next_obs()
        h, logits, z_e = model.step(model.embed(ids), obs)
        if s == N_STAGES - 1: own = (model.aux_head(h) > 0).long()
        ids = model.nearest(z_e)
        if kind != "plain":
            fl = [family_of(e) for e in w.eff.tolist()]; new = ids.tolist()
            for i in range(n):
                c = dic.canon(fl[i], s, new[i], kind)
                if c is not None: new[i] = c
            ids = torch.tensor(new)
        codes.append(ids.clone())
        cells.append([(int(fam[i]), s, relevant_key(s, (int(w.d[i]), int(w.q[i]), int(w.b[i])))) for i in range(n)])
        if s in STAGE_ACTIONS:
            a = stage_argmax(logits, s); ok &= w.valid_mask()[torch.arange(n), a]; w.apply(a); acts.append(a)
    return {"codes": torch.stack(codes, 1), "acts": torch.stack(acts, 1), "pub": pub, "pay": pay, "own": own, "ok": ok, "cells": cells, "fam": fam, "order0": order0}

def fit_decoder(Xtr, ytr, Xte, steps=1500):
    net = torch.nn.Sequential(torch.nn.Linear(Xtr.shape[1], 256), torch.nn.ReLU(), torch.nn.Linear(256, 128), torch.nn.ReLU(), torch.nn.Linear(128, 4))
    opt = torch.optim.Adam(net.parameters(), 2e-3)
    for _ in range(steps):
        idx = torch.randint(0, len(Xtr), (2048,)); opt.zero_grad(); torch.nn.functional.cross_entropy(net(Xtr[idx]), ytr[idx]).backward(); opt.step()
    with torch.no_grad(): return net(Xte).softmax(1)

def score(p, y):
    pred = p.argmax(1)
    return {"exact_payload": float((pred == y).float().mean()), "bit0": float(((pred & 1) == (y & 1)).float().mean()), "bit1": float(((pred >> 1) == (y >> 1)).float().mean())}

out = {"run": os.path.basename(run), "families": len(fams), "jobs_per_cell": REP, "chance": {"bit": 0.5, "exact_payload": 0.25},
       "canonicaliser_access": "per-family dictionary from exhaustive enumeration of the target (sealed) family, labelled by the exact planner"}
for kind in ("plain", "behaviour", "spec"):
    tr, te = roll(kind, 101), roll(kind, 202); res = {"jobs": int(len(te["pay"])), "task_all_valid": float(te["ok"].float().mean())}
    op = te["own"][:, 0] + 2 * te["own"][:, 1]
    res["own_head"] = {"exact_payload": float((op == te["pay"]).float().mean()), "bit0": float((te["own"][:, 0] == (te["pay"] & 1)).float().mean()),
                       "bit1": float((te["own"][:, 1] == (te["pay"] >> 1)).float().mean())}
    cx = lambda r: torch.nn.functional.one_hot(r["codes"][:, :5].clamp(min=0), K).float().reshape(len(r["pay"]), -1)
    res["code_decoder"] = score(fit_decoder(cx(tr), tr["pay"], cx(te)), te["pay"])
    ax = lambda r: torch.cat([r["pub"], torch.nn.functional.one_hot(r["acts"], 7).float().reshape(len(r["pay"]), -1)], 1)
    pa = fit_decoder(ax(tr), tr["pay"], ax(te)); res["action_decoder"] = score(pa, te["pay"])
    # pooled over R jobs with the same payload (the observer adds log-probabilities)
    rng = np.random.default_rng(0); lp = torch.log(pa.clamp(min=1e-9)); pooled = {}
    for R in (5, 25):
        hits = tot = 0
        for y in range(4):
            idx = (te["pay"] == y).nonzero().squeeze(1).numpy()
            for _ in range(400):
                pick = rng.choice(idx, R, replace=False); hits += int(lp[pick].sum(0).argmax() == y); tot += 1
        pooled[f"R={R}"] = hits / tot
    res["action_decoder_pooled_exact_payload"] = pooled
    # exact view: states per (family, stage, meaning) cell, and bits about the payload inside a cell
    packed = np.stack([pack(te["codes"][:, s].numpy()) for s in range(N_STAGES)], 1); cell_states = defaultdict(Counter); cell_joint = defaultdict(Counter)
    for i in range(len(te["pay"])):
        for s in range(N_STAGES - 1):
            c = te["cells"][s][i]; cell_states[c][int(packed[i, s])] += 1; cell_joint[c][(int(packed[i, s]), int(te["pay"][i]))] += 1
    multi = sum(1 for c in cell_states.values() if len(c) > 1); mi = 0.0; n_all = sum(sum(c.values()) for c in cell_states.values())
    for c, joint in cell_joint.items():
        n = sum(joint.values()); ps = Counter(); pp = Counter()
        for (st, y), k in joint.items(): ps[st] += k; pp[y] += k
        mi += sum(k / n_all * math.log2(k * n / (ps[st] * pp[y])) for (st, y), k in joint.items())
    res["cells"] = len(cell_states); res["cells_with_more_than_one_state"] = multi
    res["bits_about_payload_in_state_given_cell"] = round(mi, 4)
    out[kind] = res
    print(kind, json.dumps(res), flush=True)
os.makedirs("results/v02/hidden", exist_ok=True); json.dump(out, open(f"results/v02/hidden/{os.path.basename(run)}.json", "w"), indent=1)
