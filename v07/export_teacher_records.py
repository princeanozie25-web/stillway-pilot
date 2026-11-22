"""One record per training repository in the format the brief asks for.   python v07/export_teacher_records.py
Writes results/v07/records/teacher_traces.jsonl: task, accessible files, code hash, each proposed test with the result predicted
before execution and the output observed, alternate executions from the same savepoint (failed attempts included), the patch, the
changed lines, timing and the verified outcome."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import bank as BK
out = open("results/v07/records/teacher_traces.jsonl", "w"); n = fails = 0
for f in sorted(glob.glob("data/v07/train/*.json")):
    t = json.load(open(f)); hist, used_naive = BK.trace(t); v = t["verified"]; alts = []
    if t.get("naive"): alts.append({"kind": "test that assumes the prior procedure applies", "test": t["naive"]["test"], "predicted": t["naive"]["predict"], "observed": t["naive"]["observed"], "as_predicted": False, "seconds": t["naive"]["seconds"], "outcome": "contradicted"})
    if t.get("oldfix"): alts.append({"kind": "prior fix applied from the savepoint", "patch": t["oldfix"]["code"], "diff": v["oldfix"]["diff"], "hidden": v["oldfix"]["hidden"], "regressions": v["oldfix"]["regressions"], "outcome": "failed"})
    rec = {"task": t["id"], "template": t["template"], "symptom": t["symptom"], "cause": t["cause"], "role": t["role"], "accessible_files": sorted(t["repo"]), "code_hash": t["code_hash"],
           "savepoint": v["savepoint"], "tests": [{"step": h["step"], "suspect": h["suspect"], "proposed_test": h["test"], "predicted_before_execution": h["predict"], "observed": h["observed"], "as_predicted": h["as_predicted"]} for h in hist],
           "trace_holds_a_contradicted_prediction": used_naive, "teacher_tests_as_first_written": [{"proposed_test": p["test"], "predicted_before_execution": p["predict"], "observed": p["observed"], "seconds": p["seconds"]} for p in t["teacher"]["probes"]],
           "alternate_executions": alts, "patch": {"file": t["fix"]["file"], "function": t["fix"]["function"], "code": t["fix"]["code"], "cause": t["teacher"]["cause"], "changed_lines": v["fix"]["changed_lines"], "diff": v["fix"]["diff"]},
           "verified_outcome": {"hidden": v["fix"]["hidden"], "all_pass": all(x == "PASS" for x in v["fix"]["hidden"].values())}, "verification_seconds": v["seconds"]}
    out.write(json.dumps(rec) + "\n"); n += 1; fails += len(alts)
print(n, "records;", fails, "failed or contradicted alternate executions recorded")
