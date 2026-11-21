"""Plain (no edit) accuracy of every v0.2 core on the final strata, to tell core failures from editor failures.
    python v02/m3_core_accuracy.py SEED"""
import json, os, sys, torch
from stillway2.edits import EDIT_SPEC
from stillway2.model3 import load3
from stillway2.train3 import batch_eval3
torch.set_num_threads(2); seed = int(sys.argv[1]) + 500
ST = {"dev": dict(EDIT_SPEC), "A_unseen_families": {**EDIT_SPEC, "split": "final"}, "B_four_legs": {**EDIT_SPEC, "L": (4,), "split": None}, "C_cross_gate": {**EDIT_SPEC, "force_cross": True, "split": None}}
DYN = dict(rev=0.10, gflip=0.10, decor=0.20, close=0.10, msg=0.15, full=0.05)
out = {}
for n in ("v2_iit_s1", "v2_iit_s2", "v2_iit_s3", "v2_iit_s4", "v2_iit_s5", "v2_plain_s1", "v2_plain_s2"):
    m = load3(f"runs/{n}/checkpoint.pt")
    out[n] = {k: {"no_events": batch_eval3(m, s, 4000, seed), "with_events": batch_eval3(m, {**s, **DYN}, 4000, seed + 1)} for k, s in ST.items()}
    print(n, {k: (round(v["no_events"], 3), round(v["with_events"], 3)) for k, v in out[n].items()}, flush=True)
json.dump(out, open("results/v02/m3/core_accuracy_final.json", "w"), indent=1)
