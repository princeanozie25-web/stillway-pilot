"""Execution failures in the v0.7 final-run raw records, from student-side fields only.   python tools_v07_final_failures.py RECORDS_DIR LOG OUT_PREFIX
Added after the lock; reads raw records and the run log, never a hidden file or a grade.  Counts, per record file: test
scripts that were not well formed, test executions that timed out or raised, patches that were not well formed, patches
that could not be applied, and records with a missing part.  Writes OUT_PREFIX.json and OUT_PREFIX.md."""
import glob, json, os, re, sys
d, log, out = sys.argv[1:4]; rows = []; tot = {}
for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
    R = [json.loads(l) for l in open(f)]; c = {"file": os.path.basename(f), "records": len(R), "tests": 0, "tests_not_well_formed": 0, "test_timeouts": 0, "test_raised": 0, "patches_not_well_formed": 0, "patches_not_applied": 0, "records_missing_a_part": 0}
    for r in R:
        ts = r.get("tests") or []; p = r.get("patch")
        if len(ts) != r["limits"]["tests"] or not isinstance(p, dict): c["records_missing_a_part"] += 1
        for t in ts:
            c["tests"] += 1; o = t.get("observed") or ""
            if not t.get("well_formed"): c["tests_not_well_formed"] += 1
            elif o.startswith("TIMEOUT"): c["test_timeouts"] += 1
            elif re.search(r"(Error|Exception)\b", o): c["test_raised"] += 1
        if isinstance(p, dict):
            if not p.get("well_formed"): c["patches_not_well_formed"] += 1
            elif not p.get("applied"): c["patches_not_applied"] += 1
    rows.append(c)
    for k, v in c.items():
        if k != "file": tot[k] = tot.get(k, 0) + v
L = open(log, errors="replace").read(); runlog = {"tracebacks": L.count("Traceback"), "exit_line": (re.findall(r"RUN_FINAL EXIT.*", L) or ["none"])[-1], "restarts": max(0, len(re.findall(r"^lock of ", L, re.M)) - 1)}
json.dump({"files": rows, "total": tot, "run_log": runlog}, open(out + ".json", "w"), indent=1)
cols = [k for k in rows[0] if k != "file"]; M = ["# v0.7 final run: execution failures in the raw records", "",
     "From student-side fields only, before any grading. A test that was not well formed was not run; a test that raised printed an error as its observation (the student still saw it); a patch that was not well formed or could not be applied left the repository unchanged.",
     f"Run log: {runlog['tracebacks']} tracebacks; {runlog['restarts']} restarts; last line `{runlog['exit_line']}`.", "", "| File | " + " | ".join(c.replace("_", " ") for c in cols) + " |", "|---|" + "---|" * len(cols)]
M += [f"| {r['file']} | " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows] + ["| **All 42 files** | " + " | ".join(f"**{tot[c]}**" for c in cols) + " |"]
open(out + ".md", "w").write("\n".join(M) + "\n"); print(json.dumps(tot), json.dumps(runlog))
