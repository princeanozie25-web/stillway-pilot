"""M1: the two-field counterexample, built with the simulator itself (no extractor involved).

    python v02/m1_counterexample.py runs/f_iit_s4 I N      # chunk I of N of the 256 layouts
    python v02/m1_counterexample.py runs/f_iit_s4 merge

Every episode: closed book, no other event, and ONE stage (PLAN, LEG1, DOCK or LEG2) at which the operator
revises TWO order fields at once.  That observation shows two fields and hides the third.  v0.1's
extractor never listed such an observation.  Credit = every proposed action is valid (scorer.run_episode).
"""
import glob, json, os, sys
from itertools import product
import torch
from stillway.fixtures import SPLIT
from stillway.model import NeuralPlanner, load_checkpoint
from stillway.scorer import run_episode
from stillway.world import ALL_LAYOUTS, ALL_ORDERS, Episode, Order, STAGE_NAMES, family_of

run = sys.argv[1].rstrip("/"); name = os.path.basename(run)
out_dir = f"results/v02/counterexample/{name}"; os.makedirs(out_dir, exist_ok=True)
DOM = {"dock": (0, 1), "gate": (0, 1), "bay": (0, 1, 2)}
PAIRS = [("dock", "gate"), ("dock", "bay"), ("gate", "bay")]

if sys.argv[2] == "merge":
    tot = {}; wit = []
    for p in sorted(glob.glob(f"{out_dir}/chunk_*.json")):
        d = json.load(open(p)); wit += d["witnesses"]
        for k, v in d["counts"].items():
            t = tot.setdefault(k, [0, 0]); t[0] += v[0]; t[1] += v[1]
    n = sum(v[0] for k, v in tot.items() if k.startswith("stage:")); bad = sum(v[1] for k, v in tot.items() if k.startswith("stage:"))
    wit.sort(key=lambda w: (w["first_invalid_stage"], w["split"] != "train"))
    rep = {"episodes": n, "failed": bad, "rate": bad / n, "by": {k: {"n": v[0], "failed": v[1]} for k, v in sorted(tot.items())}, "witnesses": wit[:12]}
    json.dump(rep, open(f"{out_dir}/report.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "witnesses"})); print(json.dumps(wit[0]) if wit else "no witness"); sys.exit(0)

I, N = int(sys.argv[2]), int(sys.argv[3]); torch.set_num_threads(1)
pl = NeuralPlanner(load_checkpoint(os.path.join(run, "checkpoint.pt")))
counts = {}; witnesses = []
def add(k, bad):
    c = counts.setdefault(k, [0, 0]); c[0] += 1; c[1] += bad
for e in ALL_LAYOUTS[I::N]:
    fam = family_of(e)
    for g0 in (0, 1):
        for (d, q, b) in ALL_ORDERS:
            for st in (1, 2, 3, 4):
                for f1, f2 in PAIRS:
                    for v1, v2 in product(DOM[f1], DOM[f2]):
                        ep = Episode(e, g0, Order(d, q, b), 0, -1, "closed", {st: [("msg", f1, v1), ("msg", f2, v2)]})
                        r = run_episode(pl, ep); bad = int(not r["all_valid"])
                        add(f"stage:{STAGE_NAMES[st]}", bad); add(f"fields:{f1}+{f2}", bad); add(f"split:{SPLIT[fam]}", bad)
                        if bad and len(witnesses) < 40 and (len(witnesses) < 5 or SPLIT[fam] == "train"):
                            witnesses.append({"family": fam, "split": SPLIT[fam], "first_invalid_stage": STAGE_NAMES[r["first_invalid"]], "episode": ep.to_json()})
json.dump({"counts": counts, "witnesses": witnesses}, open(f"{out_dir}/chunk_{I}.json", "w"))
