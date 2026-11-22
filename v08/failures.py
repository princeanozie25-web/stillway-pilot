"""Execution failures in raw v0.8 records, from runner-side fields only (no grade, no hidden file).   python v08/failures.py RECORDS_ROOT LOG OUT_PREFIX
Per record file: how each job ended (DONE, ASK, or a limit and which), scripts the sandbox could not run (crash or
timeout), operations that returned BAD or ERR, and records with nothing executed."""
import collections, glob, json, os, re, sys
root, log, out = sys.argv[1:4]; rows = []; tot = collections.Counter()
for f in sorted(glob.glob(os.path.join(root, "*", "*_s[0-9].jsonl"))):
    R = [json.loads(l) for l in open(f)]; c = collections.Counter(file=0)
    c = {"file": os.path.relpath(f, root), "jobs": len(R), "ended_DONE": sum(r["end"] == "DONE" for r in R), "ended_ASK": sum(r["end"] == "ASK" for r in R), "ended_at_a_limit": sum(r["end"] == "BUDGET" for r in R)}
    why = collections.Counter(r["why"] for r in R if r["end"] == "BUDGET")
    for k in ("call limit", "operation limit", "time limit", "context full", "malformed script", "empty script"): c[k.replace(" ", "_")] = why.get(k, 0)
    c["sandbox_crash_or_timeout"] = sum(bool(s.get("error")) and str(s["error"]).startswith(("CRASH", "TIMEOUT")) for r in R for s in r["steps"]); c["script_raised"] = sum(bool(s.get("error")) and not str(s["error"]).startswith(("CRASH", "TIMEOUT")) for r in R for s in r["steps"])
    c["ops_BAD_or_ERR"] = sum(r["bad_ops"] for r in R); c["scripts"] = sum(len(r["steps"]) for r in R); c["operations"] = sum(r["ops"] for r in R); rows.append(c)
    for k, v in c.items():
        if k != "file": tot[k] += v
L = open(log, errors="replace").read(); runlog = {"tracebacks": L.count("Traceback"), "nonzero_exits": len(re.findall(r"^exit [1-9]", L, re.M)), "runs": len(re.findall(r"^exit ", L, re.M)), "start": (re.findall(r"^start .*", L, re.M) or [""])[0], "end": (re.findall(r"^end .*", L, re.M) or [""])[-1]}
json.dump({"files": rows, "total": dict(tot), "run_log": runlog}, open(out + ".json", "w"), indent=1); cols = [k for k in rows[0] if k != "file"]
M = ["# v0.8 on Codex's holdout: execution failures in the raw records", "", "From runner-side fields only, before any grading. A job that ends at a limit is not an execution failure of the runner; it is listed so that nothing is hidden. BAD and ERR are observations the model received (an illegal operation, or one that raised).",
     f"Run log: {runlog['runs']} runs, {runlog['nonzero_exits']} non-zero exits, {runlog['tracebacks']} tracebacks. {runlog['start']}; {runlog['end']}.", "", "| File | " + " | ".join(c.replace("_", " ") for c in cols) + " |", "|---|" + "---|" * len(cols)]
M += [f"| {r['file']} | " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows] + ["| **All files** | " + " | ".join(f"**{tot[c]}**" for c in cols) + " |"]
open(out + ".md", "w").write("\n".join(M) + "\n"); print(json.dumps(dict(tot)), json.dumps(runlog))
