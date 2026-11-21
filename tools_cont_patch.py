"""Continuous planner: swap along a learned direction instead of swapping slots.

    python tools_cont_patch.py runs/NAME [--sealed]

Fits ONE direction in the 128-number memory that separates gate obligation open/closed
(on dev fixtures from training families), then swaps only the donor's coordinate along it.
Two ways to pick the direction: difference of class means, and a ridge-regularised
discriminant (means difference whitened by the within-class covariance).
"""
import json, os, random, sys
import numpy as np, torch
from stillway.fixtures import DEV_IN, DEV_OUT, load_sealed, read_jsonl
from stillway.model import NeuralPlanner, load_checkpoint
from stillway.replay import cluster_boot
from stillway.scorer import run_episode, state_at
from stillway.world import Episode, STAGE_NAMES

run = sys.argv[1].rstrip("/"); sealed = "--sealed" in sys.argv
torch.set_num_threads(1)
pl = NeuralPlanner(load_checkpoint(os.path.join(run, "checkpoint.pt")))
flat = lambda st: np.array([x for s in st for x in s], dtype=np.float64)
D = pl.m.cfg.code_dim
unflat = lambda v: [tuple(float(x) for x in v[i * D:(i + 1) * D]) for i in range(pl.n_slots)]

fit_items = [i for i in read_jsonl(DEV_IN) if i["kind"] == "swap"]
X = np.array([flat(state_at(pl, Episode.from_json(i["target"]), 1)) for i in fit_items])
q = np.array([i["target"]["order"]["gate"] for i in fit_items])
dmu = X[q == 1].mean(0) - X[q == 0].mean(0)
Xc = np.concatenate([X[q == 1] - X[q == 1].mean(0), X[q == 0] - X[q == 0].mean(0)])
cov = Xc.T @ Xc / len(Xc)
lda = np.linalg.solve(cov + 1e-3 * np.trace(cov) / len(cov) * np.eye(len(cov)), dmu)
dirs = {"mean_difference": dmu, "discriminant": lda}

test_items = [i for i in (load_sealed() if sealed else read_jsonl(DEV_OUT)) if i["kind"] == "swap"]
rng = random.Random(1); out = {}
for name, v in dirs.items():
    # read with v, write along the mean difference scaled so the read-out moves by exactly the donor's amount
    w = dmu / (dmu @ v)
    t_ok, s_ok, fam = [], [], []
    for it in test_items:
        T, S = Episode.from_json(it["target"]), Episode.from_json(it["donor"]); exp = it["expect"]
        def run_with(donor_ep):
            sd = flat(state_at(pl, donor_ep, 1))
            edit = lambda st: unflat(flat(st) + ((sd - flat(st)) @ v) * w)
            r = run_episode(pl, T, 1, edit)
            return r["gate_arrival"] == exp["gate"] and r["dock_done"] == exp["dock"] and r["bay_done"] == exp["bay"]
        t_ok.append(run_with(S)); s_ok.append(run_with(Episode.from_json(rng.choice(test_items)["donor"]))); fam.append(it["family"])
    t, s = np.array(t_ok, float), np.array(s_ok, float)
    d = cluster_boot(t - s, fam)
    out[name] = {"n": len(t), "targeted": t.mean(), "shuffled": s.mean(), "improvement": d[0], "ci95": [d[1], d[2]]}
json.dump(out, open(os.path.join(run, "cont_patch_sealed.json" if sealed else "cont_patch_dev.json"), "w"), indent=1)
print(json.dumps(out))
