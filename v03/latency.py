"""Revision latency for one v0.3 core: correction in, next action out.  One job, one CPU thread, after warm-up.

    python v03/latency.py runs/v3r24fix_s1

  network, message          the correction is in the observation of the next step
  network, register write   the register is written, then the same step runs with no message
  tables, register write    the certified tables run without the network (stillway3.certify.TablePlanner)
  symbolic                  the exact planner (value table, plain Python) with the order in a list
Measured on 3-leg and on 16-leg jobs paused before their first route.
"""
import json, os, sys, time
import numpy as np, torch
from stillway2.edits import EDIT_SPEC
from stillway3.certify import TablePlanner, back, extract, term_table, valid_routes
from stillway3.editor import RegisterWrite
from stillway3.model import load_reg
from stillway3.world import WorldN

run = sys.argv[1].rstrip("/"); name = os.path.basename(run); torch.set_num_threads(1)
model = load_reg(os.path.join(run, "checkpoint.pt")); tp = TablePlanner(extract(model)); ed = RegisterWrite(); out = {"run": name}
q = lambda x, p: float(np.percentile(x, p))
for L in (3, 16):
    n = 300; spec = {**EDIT_SPEC, "L": (L,), "cross": 0.3, "split": None, "p_wait": 0.0, "env": "model"}
    w = WorldN(n, spec, torch.Generator().manual_seed(7), lmax=L); ids = torch.full((n, w.NF), -1)
    with torch.no_grad():
        obs0, _ = w.next_obs(); _, ids = model.infer(ids, obs0)
        w.t += 0; f = torch.randint(0, 2, (n,), generator=torch.Generator().manual_seed(8)); v = 1 + torch.randint(0, 2, (n,), generator=torch.Generator().manual_seed(9))
        for _ in range(w.K): w.next_obs()                                     # wait slots (none are used: p_wait = 0)
        w2 = w.clone(); obs_plain, _ = w.next_obs()
        obs_msg, _ = w2.next_obs({"rows": torch.ones(n, dtype=torch.bool), "field": f, "value": v, "show": True})
    legs = [[(int(w.eff[i, j, 0]) * 2 + int(w.tg[i, j, 0]), int(w.eff[i, j, 1]) * 2 + int(w.tg[i, j, 1])) for j in range(L)] for i in range(n)]
    gates = w.gates.tolist(); regs = ids.tolist(); fl, vl = f.tolist(), v.tolist()
    T = {k: [] for k in ("network_message", "network_register_write", "tables_register_write", "symbolic")}; agree = 0
    with torch.no_grad():
        for rep in range(4):
            for i in range(n):
                a, b, c, d = ids[i:i + 1], obs_msg[i:i + 1], obs_plain[i:i + 1], (f[i:i + 1], v[i:i + 1])
                t = time.perf_counter(); l1, _ = model.infer(a, b); t1 = time.perf_counter() - t
                t = time.perf_counter(); e, _ = ed(a, *d); l2, _ = model.infer(e, c); t2 = time.perf_counter() - t
                t = time.perf_counter(); r = list(regs[i]); r[fl[i]] = vl[i]; a3 = tp.route(r, gates[i], legs[i]); t3 = time.perf_counter() - t
                t = time.perf_counter(); r = list(regs[i]); r[fl[i]] = vl[i]; Tb = term_table(r[0], r[1])
                for leg in reversed(legs[i][1:]): Tb = back(Tb, leg)
                a4 = valid_routes(Tb, legs[i][0], gates[i][0] * 2 + gates[i][1]); t4 = time.perf_counter() - t
                if rep:
                    for k, x in zip(T, (t1, t2, t3, t4)): T[k].append(x * 1e6)
                if rep == 1: agree += int(l1[0, :2].argmax()) == int(l2[0, :2].argmax()) == a3 and a3 in a4
    out[f"{L}_legs"] = {**{k: {"median_us": round(q(x, 50), 1), "p99_us": round(q(x, 99), 1), "n": len(x)} for k, x in T.items()},
                        "all_four_agree": agree, "of": n}
    print(name, L, "legs", json.dumps(out[f"{L}_legs"]), flush=True)
os.makedirs("results/v03/latency", exist_ok=True); json.dump(out, open(f"results/v03/latency/{name}.json", "w"), indent=1)
