"""Freeze v0.4: spec, generators, graders, learners, evaluation scripts.   python v04/freeze.py
Writes results/v04/FREEZE_v04.json.  Commit it; the final data salt comes from that commit (v04/final_seed.py)."""
import glob, hashlib, json, os, sys, time
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FILES = sorted(glob.glob("stillway4/*.py")) + ["v04/runner.c", "v04/m1_bench.py", "v04/m2_interventions.py", "v04/m4_bench.py", "v04/demo.py", "v04/regrade.py", "v04/final_seed.py", "v04/final_all.sh",
                                               "v04/seed4_ticket.py", "v04/export_runtimes.py", "tests/test_schema.py", "docs/v04_spec.md"]
if os.path.exists("results/v04/FREEZE_v04.json"): sys.exit("already frozen")
json.dump({"frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "files_sha256": {f: sha(f) for f in FILES},
           "final_salt_rule": "int(sha256('stillway-v0.4-final|' + <hash of the commit that adds this file>).hexdigest()[:8], 16)",
           "seeds": [1, 2, 3, 4, 5], "size_for_final_runs": "s", "candidate_hashes": "checkpoints, tables and banks of the final runs are listed with their hashes in results/v04/MANIFEST_RUNS.json once they exist",
           "holdout": "internal (authored by the assistant that built the model); external challenge: docs/v04_external_challenge.md"}, open("results/v04/FREEZE_v04.json", "w"), indent=1)
print("frozen", len(FILES), "files")
