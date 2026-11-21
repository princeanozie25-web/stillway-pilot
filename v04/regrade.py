"""Recompute success from raw evidence with the plain-Python grader.  No torch, no stored booleans.

    python v04/regrade.py runs/v4f_proc_s_s1/raw_outputs.npz              # M2 test sets of one arm
    python v04/regrade.py results/v04/m3/v4f_proc_s_s1/raw_outputs.npz   # every scored set of the six sessions

The file holds, per test set, the raw events of every document (int16, fields kind slot jur lvl age tag evid pid ostat),
the 5 statuses the system reported after every event, and `pid_rule` (the rule index behind each policy ID; -1 = expired).
An expired policy is passed to the grader as None.  Rules are rebuilt here from the rule index: threshold, waiver, stale accepted, conflict invalid (36 combinations).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4.grader import grade

RULES = [(th, w, st, cf) for th in (1, 2, 3) for w in (0, 1, 2) for st in (0, 1) for cf in (0, 1)]
FIELDS = ("kind", "slot", "jur", "lvl", "age", "tag", "evid", "pid", "ostat")
z = np.load(sys.argv[1]); out = {}; limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
for key in sorted(k for k in z.files if k.endswith("_out")):
    stem = key[:-4]; parts = stem.split("_")
    if stem + "_events" in z.files: ev = z[stem + "_events"]; pr = z["pid_rule"]                      # M2 layout: <set>_out, <set>_events
    else:                                                                                          # M3 layout: s<k>_<set>_<arm>_out, s<k>_<set>_events, s<k>_pid_rule
        ev = z[f"{parts[0]}_{parts[1]}_events"]; pr = z[f"{parts[0]}_pid_rule"]
    pol = {p: (RULES[int(r)] if r >= 0 else None) for p, r in enumerate(pr) if p > 0}; o = z[key]; n = min(len(o), limit); ok = prot = 0
    for i in range(n):
        g = grade({"events": [dict(zip(FIELDS, map(int, e))) for e in ev[i]]}, pol, o[i].tolist()); ok += g["success"]; prot += g["protected_changed"]
    out[stem] = {"documents": n, "success": ok / n, "protected_changed": prot}
    print(stem, out[stem], flush=True)
json.dump(out, open(sys.argv[1].replace(".npz", "_regraded.json"), "w"), indent=1)
