"""Tables for milestone 2.   python v08/m2_report.py      (after v08/grade.py on results/v08/m2/*_s0.jsonl)
One frozen model (Qwen2.5-Coder-1.5B-Instruct, pinned), the same operations, the same 48 jobs and limits; one operation
per model call against scripts that compose them.  Writes results/v08/m2_tables.md and m2_summary.json."""
import json
import numpy as np
R = {m: [json.loads(l) for l in open(f"results/v08/m2/{m}_s0.graded.jsonl")] for m in ("single", "script")}; ok = lambda r: r["outcome"] == "verified"
first = lambda r: ok(r) and r["edit_scripts"] <= 1 and not any(l.startswith("REVERT") for s in r["steps"] for l in s["script"])
def st(rs):
    n = len(rs); T = sum(r["wall_s"] for r in rs); w = np.array([r["wall_s"] for r in rs])
    return {"jobs": n, "verified": sum(map(ok, rs)), "verified_pct": 100 * sum(map(ok, rs)) / n, "first_attempt_pct": 100 * sum(map(first, rs)) / n, "wrong": sum(r["outcome"] == "wrong" for r in rs), "abstained": sum(r["outcome"] == "abstained" for r in rs),
            "budget": sum(r["outcome"] == "budget" for r in rs), "jobs_per_min": 60 * sum(map(ok, rs)) / T, "calls": float(np.mean([r["calls"] for r in rs])), "ops": float(np.mean([r["ops"] for r in rs])),
            "tokens_in": float(np.mean([r["tokens_in"] for r in rs])), "tokens_out": float(np.mean([r["tokens_out"] for r in rs])), "total_tokens": int(sum(r["tokens_in"] + r["tokens_out"] for r in rs)),
            "retries": float(np.mean([max(0, r["edit_scripts"] - 1) for r in rs])), "invalid_replies": sum(r.get("invalid_replies", 0) for r in rs), "script_errors": sum(r.get("script_errors", 0) for r in rs), "bad_ops": sum(r["bad_ops"] for r in rs),
            "failed_checks": sum(r["failed_checks"] for r in rs), "model_s": float(np.mean([r["model_s"] for r in rs])), "exec_s": float(np.mean([r["exec_s"] for r in rs])), "wall_mean": float(w.mean()), "wall_p50": float(np.percentile(w, 50)),
            "wall_p90": float(np.percentile(w, 90)), "wall_max": float(w.max()), "total_wall_s": float(T)}
S = {}; M = ["# v0.8 milestone 2: one frozen model, single operations against composed scripts", "",
     "Model: Qwen2.5-Coder-1.5B-Instruct at the v0.7 pin, unchanged, greedy, on this laptop's GPU. 48 development jobs (24 proj, 24 tab). Limits for both modes: 14 model calls, 60 operations, 90 s per job, 220 new tokens per call. Operations inside scripts are counted one by one.",
     "Verified jobs per minute = verified jobs / total wall time including failed jobs.", ""]
rows = [("jobs", "Jobs", "{:d}"), ("verified", "Verified jobs", "{:d}"), ("verified_pct", "Eventual success %", "{:.1f}"), ("first_attempt_pct", "First-attempt success %", "{:.1f}"), ("wrong", "Said DONE, wrong", "{:d}"), ("abstained", "Asked on an answerable job", "{:d}"),
        ("budget", "Ran out of limits", "{:d}"), ("jobs_per_min", "Verified jobs per minute", "{:.2f}"), ("calls", "Model calls per job", "{:.2f}"), ("ops", "Operations per job (inside scripts too)", "{:.2f}"), ("tokens_in", "Prompt tokens per job", "{:.0f}"),
        ("tokens_out", "Generated tokens per job", "{:.0f}"), ("total_tokens", "Total model tokens, all jobs", "{:d}"), ("retries", "Extra editing attempts per job", "{:.2f}"), ("invalid_replies", "Replies that were not a legal call", "{:d}"),
        ("script_errors", "Scripts that crashed", "{:d}"), ("bad_ops", "Illegal or failed operations", "{:d}"), ("failed_checks", "Failed checks seen", "{:d}"), ("model_s", "Model seconds per job", "{:.2f}"), ("exec_s", "Execution seconds per job", "{:.3f}"),
        ("wall_mean", "End-to-end seconds per job, mean", "{:.2f}"), ("wall_p50", "median", "{:.2f}"), ("wall_p90", "90th percentile", "{:.2f}"), ("wall_max", "maximum", "{:.1f}")]
for dom in ("proj", "tab", "all"):
    a = {m: st([r for r in R[m] if dom == "all" or r["dom"] == dom]) for m in R}; S[dom] = a
    M += [f"## {dom}", "", "| Measure | One operation per call | Composed scripts |", "|---|---|---|"] + [f"| {t} | {f.format(a['single'][k])} | {f.format(a['script'][k])} |" for k, t, f in rows] + [""]
ids = [r["id"] for r in R["single"]]; A = {m: {r["id"]: r for r in R[m]} for m in R}; rng = np.random.default_rng(0); bs = []
for _ in range(4000):
    pick = [ids[j] for j in rng.integers(0, len(ids), len(ids))]; v = {m: sum(ok(A[m][i]) for i in pick) for m in R}; t = {m: sum(A[m][i]["wall_s"] for i in pick) for m in R}
    bs.append(((v["script"] / t["script"]) / max(1e-9, v["single"] / t["single"]) if v["single"] else np.inf, 100 * (v["script"] - v["single"]) / len(pick)))
bs = np.array(bs); a = S["all"]; ratio = a["script"]["jobs_per_min"] / max(1e-9, a["single"]["jobs_per_min"]); S["contrast"] = {"rate_ratio": ratio, "rate_ratio_ci": [float(np.percentile(bs[:, 0], 2.5)), float(np.percentile(bs[:, 0], 97.5))],
     "verified_diff": a["script"]["verified_pct"] - a["single"]["verified_pct"], "verified_diff_ci": [float(np.percentile(bs[:, 1], 2.5)), float(np.percentile(bs[:, 1], 97.5))], "both": sum(ok(A["single"][i]) and ok(A["script"][i]) for i in ids),
     "single_only": sum(ok(A["single"][i]) and not ok(A["script"][i]) for i in ids), "script_only": sum(ok(A["script"][i]) and not ok(A["single"][i]) for i in ids)}
c = S["contrast"]; M += ["## Scripts against single operations, same jobs (intervals: 4,000 resamples of the 48 jobs)", "",
     f"- Verified jobs per minute: ratio {c['rate_ratio']:.2f} (95% interval {c['rate_ratio_ci'][0]:.2f} to {c['rate_ratio_ci'][1]:.2f}).", f"- Eventual success: {c['verified_diff']:+.1f} points ({c['verified_diff_ci'][0]:+.1f} to {c['verified_diff_ci'][1]:+.1f}).",
     f"- Jobs verified by both: {c['both']}; only with single operations: {c['single_only']}; only with scripts: {c['script_only']}."]
open("results/v08/m2_tables.md", "w").write("\n".join(M) + "\n"); json.dump(S, open("results/v08/m2_summary.json", "w"), indent=1); print("\n".join(M))
