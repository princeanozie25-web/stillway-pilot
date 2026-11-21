"""Hashes of the checkpoints that finished after the v0.3 freeze commit (arm M, outcome-trained cores).   python v03/addendum.py"""
import glob, hashlib, json, os, subprocess, time
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
out = {"written_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "freeze_commit": subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", "results/v03/FREEZE_v03.json"], capture_output=True, text=True).stdout.strip(),
       "note": "protocol and pass rules for these runs are in docs/v03_spec.md (sections 3, 6, 7), frozen before they finished", "runs": {}}
for r in sorted(glob.glob("runs/v3m_s?") + glob.glob("runs/v3o_s?")):
    m = json.load(open(f"{r}/manifest.json")); assert m["checkpoint_sha256"] == sha(f"{r}/checkpoint.pt")
    out["runs"][os.path.basename(r)] = {"checkpoint_sha256": m["checkpoint_sha256"], "gradient_steps": m["gradient_steps"], "wall_seconds": m["wall_seconds"], "editors_sha256": sha(f"{r}/editors.pt") if os.path.exists(f"{r}/editors.pt") else None}
json.dump(out, open("results/v03/ADDENDUM.json", "w"), indent=1); print(json.dumps(out["runs"], indent=1)[:600])
