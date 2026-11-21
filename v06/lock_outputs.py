"""Lock the outputs of one family run: hashes of the input, the code that produced them and every output file.

    python v06/lock_outputs.py codex_hidden family_codex.json logs/v06_codex_run.log [more output files]
Writes results/v06/<name>_LOCK.json.  Commit it before anyone reveals what the hidden policies are.
"""
import glob, hashlib, json, subprocess, sys, time
name, src, log = sys.argv[1:4]; extra = sys.argv[4:]; sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
outs = sorted(glob.glob(f"results/v06/{name}_shard*.json")) + [f"results/v06/{name}_tables.md", f"results/v06/{name}_rules.json", log] + extra
lock = {"locked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "family": name, "input_file": src, "input_sha256": sha(src), "git_head_at_run": git("rev-parse", "HEAD"),
        "working_tree_changes_to_tracked_files_at_lock": git("status", "--short", "--untracked-files=no"),
        "code_sha256": {f: sha(f) for f in ("v06/family.py", "v06/report.py", "v05/blind.py")},
        "harness_unchanged_since_freeze_2b125d1": git("diff", "--stat", "2b125d1", "--", "v06/family.py", "v05/blind.py") == "",
        "report_script_diff_since_freeze": git("diff", "2b125d1", "--", "v06/report.py"),
        "commands": [f"python -I v06/family.py {src} --shard 0 --of 1 --seeds 3", f"python v06/report.py {name}"],
        "outputs_sha256": {f: sha(f) for f in outs}, "rule_verdicts": json.load(open(f"results/v06/{name}_rules.json")),
        "note": "locked before the author's breakdown of the hidden policies was requested or seen"}
json.dump(lock, open(f"results/v06/{name}_LOCK.json", "w"), indent=1); print(json.dumps({k: lock[k] for k in ("input_sha256", "git_head_at_run", "harness_unchanged_since_freeze_2b125d1", "rule_verdicts")}, indent=1)); print(len(outs), "output files hashed")
