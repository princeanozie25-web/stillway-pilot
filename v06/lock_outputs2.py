"""Lock the outputs of one round-two family run: hashes of the input, the code that produced them and every output file.

    python v06/lock_outputs2.py codex_hidden2 /path/to/family_codex2.json logs/v06r2_codex2_run.log [more output files]
Writes results/v06r2/<name>_LOCK.json.  Commit it before the private labels are requested.  Added after the freeze; reads only.
"""
import glob, hashlib, json, subprocess, sys, time
name, src, log = sys.argv[1:4]; extra = sys.argv[4:]; sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); FREEZE = "6cc1613b192e89e03eaffafe5cce2cd207cb3c95"
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
outs = sorted(glob.glob(f"results/v06r2/{name}_shard*.json")) + [f"results/v06r2/{name}_tables.md", f"results/v06r2/{name}_rules.json", log] + extra
code = ["v06/family2.py", "v06/report2.py", "v05/blind.py", "v06/family.py"]
lock = {"locked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "family": name, "input_file": src.split("/")[-1], "input_sha256": sha(src), "freeze_commit": FREEZE, "git_head_at_lock": git("rev-parse", "HEAD"),
        "tracked_files_changed_since_freeze": git("diff", "--stat", FREEZE, "--", "v05", "v06/family.py", "v06/family2.py", "v06/report2.py", "stillway"),
        "code_sha256": {f: sha(f) for f in code}, "code_sha256_at_freeze": {f: hashlib.sha256(subprocess.run(["git", "show", f"{FREEZE}:{f}"], capture_output=True).stdout).hexdigest() for f in code},
        "commands": [f"python -I v06/family2.py /absolute/path/to/{src.split('/')[-1]} --shard 0 --of 1 --seeds 3", f"python v06/report2.py {name}"],
        "outputs_sha256": {f: sha(f) for f in outs}, "rule_verdicts": json.load(open(f"results/v06r2/{name}_rules.json")),
        "note": "locked before the private labels of the new policies were requested or seen"}
lock["code_identical_to_freeze"] = lock["code_sha256"] == lock["code_sha256_at_freeze"]
json.dump(lock, open(f"results/v06r2/{name}_LOCK.json", "w"), indent=1); print(json.dumps({k: lock[k] for k in ("input_sha256", "freeze_commit", "code_identical_to_freeze")}, indent=1)); print(len(outs), "output files locked")
