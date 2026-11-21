"""Freeze v0.3: code, spec and every register-core checkpoint.   python v03/freeze.py
Writes results/v03/FREEZE_v03.json.  Commit it; the final seed is derived from that commit (v03/final_seed.py)."""
import glob, hashlib, json, os, sys, time
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FILES = ["stillway3/world.py", "stillway3/model.py", "stillway3/train.py", "stillway3/certify.py", "stillway3/repair.py", "stillway3/edits.py", "stillway3/editor.py",
         "v03/eval_edits.py", "v03/confirm.py", "v03/latency.py", "v03/final_seed.py", "v03/train_m.py", "v02/m4_scaling.py", "stillway2/edits.py", "stillway2/world3.py", "docs/v03_spec.md"]
if os.path.exists("results/v03/FREEZE_v03.json"): sys.exit("already frozen")
runs = {}
for r in sorted(glob.glob("runs/v3[rcn]2*_s?")):
    m = json.load(open(f"{r}/manifest.json")); assert m["checkpoint_sha256"] == sha(f"{r}/checkpoint.pt"), r
    runs[os.path.basename(r)] = {"checkpoint_sha256": m["checkpoint_sha256"], "repaired_from": m.get("repaired_from", {}).get("run"), "repair_clean": m.get("clean")}
json.dump({"frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "runs": runs, "files_sha256": {f: sha(f) for f in FILES},
           "final_seed_rule": "int(sha256('stillway-v0.3-final|' + <hash of the commit that adds this file>).hexdigest()[:8], 16)",
           "v02_final_seed_used_for_F1": 1670983329,
           "not_in_this_freeze": "arm M checkpoints (v3m_s1..3) and the exploratory outcome-trained cores (v3o_*) were still training; their protocol and pass rules are in docs/v03_spec.md, their hashes are added in results/v03/ADDENDUM.json"},
          open("results/v03/FREEZE_v03.json", "w"), indent=1)
print("frozen", len(runs), "runs")
