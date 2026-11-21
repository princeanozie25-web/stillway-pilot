"""SHA-256 of every v0.2 result, checkpoint and editor:  python v02/manifest.py"""
import glob, hashlib, json, os, subprocess, time
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
pats = ["runs/v2_*/checkpoint.pt", "runs/v2_*/editors.pt", "runs/v2_*/manifest.json", "runs/r_iit_s*/checkpoint.pt", "runs/v2x_*/checkpoint.pt", "results/v02/**/*.json", "results/v02/*.md",
        "fixtures3/*.json", "stillway2/*.py", "v02/*.py", "v02/*.sh", "tests/test_messages36.py", "tests/test_world3.py", "docs/v02_*.md", "smoke.sh", "README_v02.md", "demo/Stillway Shift Replay.html"]
files = sorted({f for p in pats for f in glob.glob(p, recursive=True) if "/chunk_" not in f and not f.endswith("MANIFEST_v02.json")})
out = {"made_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "freeze_commit": "14700485083f6759f166a56ccff019b247999956", "final_seed": 1670983329, "files": {f: {"sha256": sha(f), "bytes": os.path.getsize(f)} for f in files}}
json.dump(out, open("results/v02/MANIFEST_v02.json", "w"), indent=1); print(len(files), "files hashed")
