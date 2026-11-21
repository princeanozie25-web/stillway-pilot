"""M2: freeze the v0.2 core, the editors, the selection, the baselines and the scorer.

    python v02/m2_freeze.py PRIMARY_EDITOR runs/v2_iit_s1 runs/v2_iit_s2 ... 

Writes results/v02/FREEZE_v02.json.  Commit it; the final seed is derived from that commit's hash
(v02/final_seed.py), so no final job can be generated before the commit exists.
"""
import hashlib, json, os, sys, time
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FILES = ["stillway2/world3.py", "stillway2/model3.py", "stillway2/edits.py", "stillway2/editors.py", "stillway2/dictref.py", "stillway2/train3.py",
         "v02/m3_eval.py", "v02/final_seed.py", "docs/v02_transfer_spec.md"]
if os.path.exists("results/v02/FREEZE_v02.json"): sys.exit("already frozen")
primary = sys.argv[1]; runs = {}
for r in sys.argv[2:]:
    r = r.rstrip("/"); n = os.path.basename(r)
    runs[n] = {"checkpoint_sha256": sha(f"{r}/checkpoint.pt"), "editors_sha256": sha(f"{r}/editors.pt"),
               "dev_results_sha256": sha(f"results/v02/m3/{n}_dev.json")}
json.dump({"frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "primary_editor": primary, "runs": runs,
           "selection_rule": "the editor with the higher joint edit success on development flip attempts, averaged over the interchange-trained core seeds; ties to slot write",
           "advancement_rule": {"joint_success_min": 0.90, "unrelated_drop_max": 0.05, "comparable_success_max_loss": 0.02,
                                "named_advantage": "median end-to-end revision latency lower than message-and-resume"},
           "sample_size": {"flip_attempts_per_stratum_per_core": 4000, "secondary_cells": 2000, "dictionary_reference": 400},
           "final_seed_rule": "int(sha256('stillway-v0.2-final|' + <hash of the commit that adds this file>).hexdigest()[:8], 16)",
           "files_sha256": {f: sha(f) for f in FILES}}, open("results/v02/FREEZE_v02.json", "w"), indent=1)
print("frozen", len(runs), "runs; primary editor:", primary)
