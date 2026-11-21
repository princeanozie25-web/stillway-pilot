"""Execution manifest for v0.4: every run (pilot or final, complete or not) with its status and hashes, and the
hash of every result file.   python v04/manifest_runs.py     -> results/v04/MANIFEST_RUNS.json"""
import glob, hashlib, json, os, subprocess, time
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); runs = {}
# runs that left no manifest: what their logs show (logs/v04_m1_g4_w*_s1.log, logs/v04_m1_queue.log)
NOTES = {"v4r2_g4_w512_s1": {"role": "pilot", "status": "incomplete: killed by the operating system (signal 9) at about 55 minutes, after its first certificate attempt",
                             "measured": {"exact_vectors": 22695, "active_parameters_per_decision": 872000, "sampled_job_training_steps": 7500, "exact_machine_training_steps_at_36_min": 2000,
                                          "leg_step_entries_wrong_sampled_after_2000_machine_steps": 0.789, "first_certificate": {"complete": False, "pairs": 2502, "vectors_reached": 902, "route_checks": 10248192, "route_wrong": 472880}},
                             "projection": "three gates needed 12,000 to 26,000 machine-training steps for 72,000 leg-step entries; four gates have 5.8 million entries and ran 3.3 steps per second on the loaded machine: more than 100 CPU-hours if the same ratio held, and capacity at this size is untested"},
         "v4r2_g4_w128_s1": {"role": "pilot", "status": "incomplete: killed by the operating system (signal 9) at about 55 minutes, after its first certificate attempt",
                             "measured": {"exact_vectors": 22695, "sampled_job_training_steps": 16500, "exact_machine_training_steps_at_36_min": 2000, "leg_step_entries_wrong_sampled_after_2000_machine_steps": 0.880,
                                          "first_certificate": {"complete": False, "pairs": 3160, "vectors_reached": 902, "route_checks": 12943360, "route_wrong": 854554}}}}
for d in sorted(glob.glob("runs/v4*")):
    n = os.path.basename(d); mf = f"{d}/manifest.json"
    if not os.path.exists(mf): runs[n] = {"status": "incomplete: stopped before it wrote a manifest (superseded or killed)", **NOTES.get(n, {})}; continue
    m = json.load(open(mf)); role = "final" if n.startswith("v4f_") else "pilot"
    r = {"role": role, "status": m.get("status"), "wall_or_train_seconds": m.get("wall_seconds", m.get("train_seconds")), "checkpoint_sha256": m.get("checkpoint_sha256"),
         "active_parameters_per_decision": m.get("active_parameters_per_decision"), "resident_parameters": m.get("resident_parameters")}
    for f in ("checkpoint.pt", "tables.bin", "raw_outputs.npz"):
        if os.path.exists(f"{d}/{f}"): r[f] = {"sha256": sha(f"{d}/{f}"), "bytes": os.path.getsize(f"{d}/{f}")}
    runs[n] = r
banks = {os.path.relpath(p): {"sha256": sha(p), "bytes": os.path.getsize(p)} for p in sorted(glob.glob("results/v04/m3/*/bank_*.pt"))}
files = {p: {"sha256": sha(p), "bytes": os.path.getsize(p)} for p in sorted(glob.glob("results/v04/**/*", recursive=True)) if os.path.isfile(p) and not p.endswith("MANIFEST_RUNS.json") and "/bank_" not in p}
out = {"made_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "start_commit": "69f521607d1c8193cdb59207d24f5e2d90def80d", "freeze_commit": "d9a904773f3dbe1712a679cd785145f407010125", "final_salt": 2701878737,
       "budget": "one hour per run, one CPU thread, Apple M1 Max 32 GB; closures capped at 4 GB and one hour", "runs": runs, "bank_versions": banks, "result_files": files,
       "counts": {"runs": len(runs), "complete": sum(1 for r in runs.values() if str(r.get("status", "")).startswith("complete")), "incomplete": sum(1 for r in runs.values() if not str(r.get("status", "")).startswith("complete"))}}
json.dump(out, open("results/v04/MANIFEST_RUNS.json", "w"), indent=1); print(out["counts"], len(banks), "bank files", len(files), "result files")
