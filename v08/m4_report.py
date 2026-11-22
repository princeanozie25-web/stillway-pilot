"""Tables for milestone 4.   python v08/m4_report.py        (reads results/v08/m4/day2/*.graded.jsonl and night.json)

Sets of day 2: retention (earlier skills), transfer (later mechanisms on new projects and books), trap (a later-slot
change also satisfies the visible checks; the real fault is elsewhere).  Writes results/v08/m4_tables.md and
m4_summary.json."""
import collections, glob, json, os, re
import numpy as np

D = "results/v08/m4/day2"; R = {}
for f in sorted(glob.glob(f"{D}/*.graded.jsonl")): R[os.path.basename(f)[:-len("_s0.graded.jsonl")]] = {r["id"]: r for r in map(json.loads, open(f))}
ORDER = [a for a in ("core", "core+bank", "core+bank_priced", "naive", "replay", "replay+bank", "sleep", "sleep+bank", "teacher", "search") if a in R]; night = json.load(open("results/v08/m4/night.json")); day1 = json.load(open("results/v08/m4/day1.json"))
SETS = {"retention": lambda r: r["group"] in ("familiar", "newmech", "valid", "unans", "scattered", "stale"), "transfer": lambda r: r["group"] == "later", "trap": lambda r: r["group"] == "trap", "whole day": lambda r: True}
ok = lambda r: r["outcome"] == "verified"


def st(rs):
    n = len(rs); ans = [r for r in rs if r["end"] == "DONE"]; T = sum(r["wall_s"] for r in rs); v = sum(map(ok, rs))
    return {"jobs": n, "verified_pct": 100 * v / max(1, n), "answered_pct": 100 * len(ans) / max(1, n), "error_among_answers_pct": 100 * sum(not ok(r) for r in ans) / max(1, len(ans)), "asked_pct": 100 * sum(r["end"] == "ASK" for r in rs) / max(1, n),
            "jobs_per_min": 60 * v / max(1e-9, T), "s_per_job": T / max(1, n), "scripts": float(np.mean([r["calls"] for r in rs])) if rs else 0, "ops": float(np.mean([r["ops"] for r in rs])) if rs else 0}


S = {"sets": {}, "bank": {}, "harm": {}, "break_even": {}}; M = ["# v0.8 milestone 4: what yesterday's experience buys tomorrow", "",
     f"Starting core: `{night['starting_checkpoint']}`. Day 1: {day1['jobs']} jobs, {day1['core_verified']:.0f} verified by the frozen core, {day1.get('teacher_jobs', 0):.0f} then worked by the teacher. Bank version 1: {night['bank_entries']} entries. Every update: {night['update_token_budget']:.0f} tokens from the same checkpoint.", ""]
for dom in ("proj", "tab"):
    for name, f in SETS.items():
        rows = []
        for a in ORDER:
            rs = [r for r in R[a].values() if r["dom"] == dom and f(r)]
            if rs: s = st(rs); S["sets"][f"{dom}/{name}/{a}"] = s; rows.append(f"| {a} | {s['jobs']} | {s['verified_pct']:.1f} | {s['answered_pct']:.0f} | {s['error_among_answers_pct']:.1f} | {s['asked_pct']:.0f} | {s['jobs_per_min']:.0f} | {s['scripts']:.2f} | {s['ops']:.1f} |")
        if rows: M += [f"## {dom}, {name}", "", "| Arm | Jobs | Verified % | Answered % | Error among answers % | Asked for evidence % | Verified jobs / min | Scripts / job | Operations / job |", "|---|---|---|---|---|---|---|---|---|"] + rows + [""]
M += ["## Harm and gain against the frozen core, retention set (jobs)", "", "| Arm | Core right, arm not (harm) | Arm right, core not (gain) | Jobs |", "|---|---|---|---|"]
for a in ORDER:
    if a in ("core", "teacher", "search"): continue
    ids = [i for i, r in R["core"].items() if SETS["retention"](r)]; h = sum(ok(R["core"][i]) and not ok(R[a][i]) for i in ids); g = sum(ok(R[a][i]) and not ok(R["core"][i]) for i in ids); S["harm"][a] = {"harm": h, "gain": g, "jobs": len(ids)}; M.append(f"| {a} | {h} | {g} | {len(ids)} |")
bank_arms = [a for a in ORDER if "+bank" in a]
if bank_arms:
    M += ["", "## What the bank did (jobs; the bank's procedure runs first and anything but PASS leaves the work untouched)", "", "| Arm | Set | Jobs | Finished by the bank | of which wrong | Tried and failed (handed on) | Declined | Operations spent in failed tries, per job |", "|---|---|---|---|---|---|---|---|"]
    for a in bank_arms:
        for name, f in SETS.items():
            rs = [r for r in R[a].values() if f(r)]; use = [r["steps"][0] for r in rs if r["steps"] and r["steps"][0].get("bank")]; res = collections.Counter(u["obs"][0] for u in use)
            passed = [r for r in rs if r["steps"] and r["steps"][0].get("bank") and r["steps"][0]["obs"] == ["PASS"]]; wrong = sum(not ok(r) for r in passed); waste = sum(len(u.get("inner", [])) for u in use if u["obs"] == ["FAIL"]) / max(1, len(rs))
            S["bank"][f"{a}/{name}"] = {"jobs": len(rs), "pass": res["PASS"], "pass_wrong": wrong, "fail": res["FAIL"], "decline": res["DECLINE"], "wasted_ops_per_job": waste}
            M.append(f"| {a} | {name} | {len(rs)} | {res['PASS']} | {wrong} | {res['FAIL']} | {res['DECLINE']} | {waste:.2f} |")
c = night["cost"]; over = {"core+bank": c["bank_and_gate_s"], "core+bank_priced": c["bank_and_gate_s"], "naive": c["corpus_s"] + c["train_naive_s"], "replay": c["corpus_s"] + c["train_replay_s"], "sleep": c["corpus_s"] + c["train_sleep_s"] + c["validation_s"]}
over["replay+bank"] = over["replay"] + c["bank_and_gate_s"]; over["sleep+bank"] = over["sleep"] + c["bank_and_gate_s"]
M += ["", "## Break-even", "", "Overnight cost in seconds on this machine (bank: promotion and gate; update: corpus, training and, for sleep, validation), against what the arm changes on the whole of day 2 relative to the frozen core.",
      "Jobs to recover the night = overnight seconds / seconds saved per job. Where the arm is slower per job it never recovers the cost in time; what it buys is the extra verified jobs.", "",
      "| Arm | Overnight s | Seconds per job (core) | Seconds per job (arm) | Jobs to recover the night in time | Extra verified jobs per 100 |", "|---|---|---|---|---|---|"]
base = st(list(R["core"].values()))
for a in ORDER:
    if a not in over: continue
    s = st(list(R[a].values())); save = base["s_per_job"] - s["s_per_job"]; be = over[a] / save if save > 1e-6 else None; S["break_even"][a] = {"overnight_s": over[a], "s_per_job": s["s_per_job"], "core_s_per_job": base["s_per_job"], "jobs_to_recover": be, "extra_verified_per_100": s["verified_pct"] - base["verified_pct"]}
    M.append(f"| {a} | {over[a]:.1f} | {base['s_per_job']:.3f} | {s['s_per_job']:.3f} | {'never' if be is None else f'{be:.0f}'} | {s['verified_pct'] - base['verified_pct']:+.1f} |")
M += ["", "## Overnight validation and promotion", "", f"Held-back day-1 jobs (later mechanisms) and the fixture set (earlier skills), verified %: " + "; ".join(f"{k}: new {v['new']}, old {v['old']}" for k, v in night["validation"].items()) + ".",
      f"Sleep update promoted: **{night['sleep_promoted']}** ({night['promotion_rule']}). Dreams generated and verified by execution: {c['dreams']} ({c['dream_ops']} operations). Day-1 records used: {c['day_records']}."]
open("results/v08/m4_tables.md", "w").write("\n".join(M) + "\n"); json.dump(S, open("results/v08/m4_summary.json", "w"), indent=1); print("\n".join(M))
