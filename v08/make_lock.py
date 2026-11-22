"""Lock everything the holdout run depends on.   python v08/make_lock.py [check]
Hashes the protocol, the code, the job sets, the manifest and every primary checkpoint into results/v08/LOCK_v08.json.
`check` compares the files on disk with the lock."""
import glob, hashlib, json, os, subprocess, sys, time
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FILES = ["docs/v08_protocol.md", "docs/v08_holdout_brief.md"] + sorted(glob.glob("stillway8/*.py")) + [f"v08/{n}" for n in ("build_data.py", "train_core.py", "run_core.py", "grade.py", "report.py", "run_m3.sh", "ref_search.py", "pack_holdout.py", "overfit.py")] + \
        ["data/v08/MANIFEST.json"] + [f"data/v08/{s}/{h}.jsonl" for s in ("dev", "hold", "fixture") for h in ("public", "hidden")] + sorted(glob.glob("artifacts/v08/core_*_s[0-9].safetensors")) + sorted(glob.glob("artifacts/v08/core_*_s[0-9].json"))
if len(sys.argv) > 1 and sys.argv[1] == "check":
    L = json.load(open("results/v08/LOCK_v08.json")); bad = [f for f, h in L["files"].items() if not os.path.exists(f) or sha(f) != h]
    print(f"lock of {L['made']} | git {L['git'][:10]} | " + ("ALL MATCH" if not bad else "DIFFER: " + ", ".join(bad))); sys.exit(1 if bad else 0)
L = {"made": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "git": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(), "files": {f: sha(f) for f in FILES},
     "pretraining_records_sha256": json.load(open("data/v08/MANIFEST.json"))["pretrain"]["records_sha256"], "holdout_runs_before_lock": len(glob.glob("results/v08/hold/*/*.jsonl"))}
os.makedirs("results/v08", exist_ok=True); json.dump(L, open("results/v08/LOCK_v08.json", "w"), indent=1); print(len(L["files"]), "files locked;", "holdout record files existing before the lock:", L["holdout_runs_before_lock"])
