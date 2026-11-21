"""EXPLORATORY (after the v0.5 results): choose between the program learner and the network by held-out audits.

    python -I v05/x_selector.py DATASET

At each budget, 20% of the audited cases are held out; the program committee and the network ensemble are fitted on the
rest; whichever gets more held-out cases right is refitted on all audited cases and used (ties: program).  Passive audits,
2 tests per rule, 5 seeds, same budgets and seeds as the frozen run.  Reported: audits to 99% and how often each was chosen.
"""
import json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blind as B
name = sys.argv[1]; torch.set_num_threads(1); X, y, card = B.load(name); n, K = len(y), int(y.max()) + 1; Cb = B.conditions(X, card, 2); Cf = Cb.astype(np.float32)
X1 = np.concatenate([np.eye(k, dtype=np.float32)[X[:, a]] for a, k in enumerate(card)], 1); budgets = []; b = 16
while b < min(n, 4096): budgets.append(b); b *= 2
budgets.append(min(n, 4096)); rows = [[] for _ in budgets]
def prog(obs, rng): return B.committee(np.stack([B.fit_list(Cf, Cb, y, obs, K, rng)[0] for _ in range(7)]), K)[0]
def net(obs, seed): return B.committee(np.stack([B.net_fit(X1, y, obs, K, seed * 100 + i) for i in range(5)]), K)[0]
for seed in range(1, 6):
    rng = np.random.default_rng(1000 * seed); order = rng.permutation(n)
    for bi, Bn in enumerate(budgets):
        obs = np.zeros(n, bool); obs[order[:Bn]] = True; idx = np.flatnonzero(obs); val = rng.permutation(idx)[:max(2, len(idx) // 5)]; tr = obs.copy(); tr[val] = False
        ap = float((prog(tr, rng)[val] == y[val]).mean()); an = float((net(tr, seed)[val] == y[val]).mean()); use = "program" if ap >= an else "net"
        g = prog(obs, rng) if use == "program" else net(obs, seed); rows[bi].append({"chosen": use, "right_all": float((g == y).mean()), "heldout_program": ap, "heldout_net": an})
    print(name, "seed", seed, [(r[-1]["chosen"][0], round(r[-1]["right_all"], 3)) for r in rows], flush=True)
first = [next((budgets[bi] for bi in range(len(budgets)) if rows[bi][s]["right_all"] >= 0.99), None) for s in range(5)]
json.dump({"dataset": name, "budgets": budgets, "audits_to_99": first, "right_all_by_budget": [float(np.mean([r["right_all"] for r in rows[bi]])) for bi in range(len(budgets))],
           "program_chosen_share_by_budget": [float(np.mean([r["chosen"] == "program" for r in rows[bi]])) for bi in range(len(budgets))]}, open(os.path.join(B.ROOT, "results", "v05", f"selector_{name}.json"), "w"), indent=1)
print(name, "audits to 99%:", first)
