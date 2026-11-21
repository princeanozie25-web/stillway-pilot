"""SHA-256 of every v0.3 result, checkpoint and source file:  python v03/manifest.py"""
import glob, hashlib, json, os, subprocess, time
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
pats = ["runs/v3*/checkpoint.pt", "runs/v3*/editors.pt", "runs/v3*/manifest.json", "results/v03/**/*.json", "results/v03/*.md", "stillway3/*.py", "v03/*.py", "v03/*.sh",
        "tests/test_world_n.py", "tests/test_regcore.py", "tests/test_edits_n.py", "docs/v03_*.md", "smoke_v03.sh", "README_v03.md", "demo/Stillway Proof Bench.html", "demo/proof_template.html", "demo/build_proof.py", "demo/test_proof.js"]
files = sorted({f for p in pats for f in glob.glob(p, recursive=True) if not f.endswith("MANIFEST_v03.json")})
out = {"made_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "freeze_commit": "de80fd794802d422353707c0fa8ff49950e1a7cf", "final_seed": 850390379, "v02_final_seed_used_for_F1": 1670983329,
       "files": {f: {"sha256": sha(f), "bytes": os.path.getsize(f)} for f in files}}
json.dump(out, open("results/v03/MANIFEST_v03.json", "w"), indent=1); print(len(files), "files hashed")
