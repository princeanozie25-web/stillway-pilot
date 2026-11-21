"""Build the versioned diagnostic bank from executed training records.   python v07/build_bank.py
A clause is admitted only if the records support it:
  version 1 (prior procedure and scope)  every prior-role task: the teacher's first test came out as predicted and the fix passed the hidden tests
  exception                              every exception-role task: the prior fix was executed from the savepoint and FAILED (regressions recorded), the exception's fix passed
  contradiction                          every alternate-cause task: a test that assumes the prior cause was contradicted by execution, the alternate fix passed
Both versions are kept.  Development and final repositories are never read."""
import glob, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7.procedures import PROC
tasks = [json.load(open(f)) for f in sorted(glob.glob("data/v07/train/*.json"))]; bank = {"built_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "source": "data/v07/train only", "diagnostics": {}, "history": []}
passed = lambda t: all(v == "PASS" for v in t["verified"]["fix"]["hidden"].values())
for sym, p in PROC.items():
    mine = [t for t in tasks if t["symptom"] == sym]; prior = [t for t in mine if t["role"] == "prior"]; exc = [t for t in mine if t["role"] == "exception"]; alt = [t for t in mine if t["role"] == "alternate"]
    ev1 = {"tasks": [t["id"] for t in prior], "first_test_as_predicted": sum(t["teacher"]["probes"][0]["observed"] == t["teacher"]["probes"][0]["predict"] for t in prior), "fix_verified": sum(passed(t) for t in prior)}
    v1 = {"version": 1, "status": "promoted" if ev1["first_test_as_predicted"] == ev1["fix_verified"] == len(prior) > 0 else "candidate", "clauses": {k: p[k] for k in ("symptom", "test", "confirmed", "scope")}, "evidence": {"prior": ev1}}
    ev_x = {"tasks": [t["id"] for t in exc], "prior_fix_failed_when_executed": sum(not all(v == "PASS" for v in t["verified"]["oldfix"]["hidden"].values()) for t in exc), "prior_fix_regressions": sum(len(t["verified"]["oldfix"]["regressions"]) > 0 for t in exc), "exception_fix_verified": sum(passed(t) for t in exc)}
    ev_c = {"tasks": [t["id"] for t in alt], "prior_cause_test_contradicted": sum(t["naive"]["observed"] != t["naive"]["predict"] for t in alt), "alternate_fix_verified": sum(passed(t) for t in alt)}
    c2 = dict(v1["clauses"]); admitted = []
    if exc and ev_x["prior_fix_failed_when_executed"] == ev_x["exception_fix_verified"] == len(exc): c2["exception"] = p["exception"]; admitted.append("exception")
    if alt and ev_c["prior_cause_test_contradicted"] == ev_c["alternate_fix_verified"] == len(alt): c2["contradiction"] = p["contradiction"]; admitted.append("contradiction")
    v2 = {"version": 2, "status": "promoted" if admitted else "rejected", "clauses": c2, "evidence": {"prior": ev1, "exception": ev_x, "contradiction": ev_c}, "admitted": admitted}
    bank["diagnostics"][sym] = {"current": 2 if admitted else 1, "versions": [v1, v2], "wording": "teacher-authored (stillway7/procedures.py)"}
    bank["history"] += [{"diagnostic": sym, "event": "version 1 " + v1["status"], "records": len(prior)}, {"diagnostic": sym, "event": "prior fix contradicted by execution; local exception proposed", "records": len(exc)}, {"diagnostic": sym, "event": "version 2 " + v2["status"] + ": " + ", ".join(admitted), "records": len(exc) + len(alt)}]
os.makedirs("artifacts/v07", exist_ok=True); json.dump(bank, open("artifacts/v07/bank.json", "w"), indent=1)
print(json.dumps({s: {"current": d["current"], "v1": d["versions"][0]["status"], "v2": d["versions"][1]["status"], "admitted": d["versions"][1]["admitted"], "evidence": d["versions"][1]["evidence"]["exception"] | d["versions"][1]["evidence"]["contradiction"]} for s, d in bank["diagnostics"].items()}, indent=1, default=str)[:1800])
print("bank bytes", os.path.getsize("artifacts/v07/bank.json"), "sha256", hashlib.sha256(open("artifacts/v07/bank.json", "rb").read()).hexdigest()[:16])
