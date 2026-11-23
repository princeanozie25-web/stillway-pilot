"""Tables and the decision fixed beforehand for the questioning guard (Q5).   python v08/q_report.py GRADED_DIR OUT_PREFIX

GRADED_DIR holds the final <arm>_s<seed>.graded.jsonl files made by v08/grade.py.  Arms: bank (plain bank), bankguard
(the existing guard: a bare ASK when more than one change passes), bankq (the questioning guard), search (the fixed search
script, the cheap reference) and, outside the rule, searchq (the search script given the questioning rule).
Classes from the grader's `kind`: ordinary ("bug"), equal, trap.  Endings: verified, wrong (DONE and the hidden test
disagrees), asked (ASK, nothing changed), limit.  "Procedure" means the stored procedure or script ended the job itself;
"core" means the bank declined or failed and the core finished it.
The rule and the targets are those of docs/v08_q5_plan.md, section 4.  Writes OUT_PREFIX_tables.md and OUT_PREFIX_summary.json."""
import glob, json, math, os, random, re, sys

d, out = sys.argv[1], sys.argv[2]; R = {}
for f in sorted(glob.glob(os.path.join(d, "*.graded.jsonl"))):
    m = re.match(r"(.+)_s(\d+)\.graded\.jsonl", os.path.basename(f)); R.setdefault(m.group(1), []).extend(map(json.loads, open(f)))
ORDER = [a for a in ("bankguard", "bank", "bankq", "search", "searchq", "exec") if a in R]
NAME = {"exec": "Core alone", "bank": "Plain bank", "bankguard": "Existing guard (bare request)", "bankq": "Questioning guard", "search": "Fixed search script", "searchq": "Search script with the questioning rule (outside the rule)"}
CLASS = {"trap": "trap", "equal": "equal", "bug": "ordinary"}; ids = [r["id"] for r in R[ORDER[0]]]; assert all([r["id"] for r in R[a]] == ids for a in ORDER), "the arms must hold the same jobs in the same order"
own = lambda r: r.get("calls", 0) <= 1 and (r.get("bank_ops", 0) > 0 or "bank_ops" not in r)
Q = lambda r: r.get("q") or {"rounds": [], "notes": [], "probe_executions": 0, "changes_tried": 0, "stages": [], "waiting_s": 0.0}
nq = lambda r: len(Q(r)["rounds"]); oc = lambda rs, o, f=lambda r: True: sum(r["outcome"] == o and f(r) for r in rs)


def sign_p(a, b):                                              # exact two-sided sign test on the discordant pairs
    n = a + b
    if not n: return 1.0
    k = min(a, b); return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def boot(x, y, B=10000):                                       # paired bootstrap over jobs, 95% interval of the difference in share, points
    rng = random.Random(805); n = len(x); ds = sorted(100 * sum(x[i] - y[i] for i in (rng.randrange(n) for _ in range(n))) / n for _ in range(B)); return [ds[int(0.025 * B)], ds[int(0.975 * B)]]


S = {"arms": {}, "jobs": len(ids)}; M = [f"# Questioning guard, Q5: {d}", "", f"{len(ids)} jobs, the same for every arm. Figures for the questioning arms are final, after the answers.", "", "## Every job", "",
     "| Arm | Verified | Wrong DONE | Clean ASK | Limits | Ended by the procedure: right / wrong / asked | Ended by the fallback core: right / wrong / asked / limit | User questions | Probe executions per job | Operations per job | Machine seconds per job |", "|---|" + "---|" * 10]
for a in ORDER:
    rs = R[a]; n = len(rs); c = lambda o, f=lambda r: True: oc(rs, o, f); core = lambda r: not own(r)
    s = {"verified": c("verified"), "wrong": c("wrong"), "asked": c("abstained"), "limit": c("budget"), "procedure": [c("verified", own), c("wrong", own), c("abstained", own)], "core": [c("verified", core), c("wrong", core), c("abstained", core), c("budget", core)],
         "questions": sum(map(nq, rs)), "probe_executions": sum(Q(r)["probe_executions"] for r in rs), "ops_per_job": sum(r["ops"] for r in rs) / n, "machine_s_per_job": sum(r["wall_s"] for r in rs) / n, "ask_with_edit": sum(r["end"] == "ASK" and not r["detail"].get("unchanged", True) for r in rs)}
    S["arms"][a] = s; M.append(f"| {NAME[a]} | {s['verified']} ({100 * s['verified'] / n:.1f}%) | {s['wrong']} | {s['asked']} | {s['limit']} | {' / '.join(map(str, s['procedure']))} | {' / '.join(map(str, s['core']))} | {s['questions']} | {s['probe_executions'] / n:.1f} | {s['ops_per_job']:.1f} | {s['machine_s_per_job']:.3f} |")
M += ["", "## By class (verified / wrong DONE / clean ASK / limit)", "", "| Arm | " + " | ".join(f"{cl.capitalize()} ({sum(CLASS[r['kind']] == cl for r in R[ORDER[0]])})" for cl in ("trap", "equal", "ordinary")) + " |", "|---|---|---|---|"]
for a in ORDER:
    cells = []
    for cl in ("trap", "equal", "ordinary"): rs = [r for r in R[a] if CLASS[r["kind"]] == cl]; cells.append(" / ".join(str(oc(rs, o)) for o in ("verified", "wrong", "abstained", "budget")))
    S["arms"][a]["by_class"] = dict(zip(("trap", "equal", "ordinary"), cells)); M.append(f"| {NAME[a]} | " + " | ".join(cells) + " |")

if "bankq" in R and "bankguard" in R:
    q, g = R["bankq"], R["bankguard"]; v = lambda rs: [int(r["outcome"] == "verified") for r in rs]; w = lambda rs: [int(r["outcome"] == "wrong") for r in rs]; vq, vg, wq, wg = v(q), v(g), w(q), w(g)
    dv = (sum(a > b for a, b in zip(vq, vg)), sum(a < b for a, b in zip(vq, vg))); dw = (sum(a > b for a, b in zip(wq, wg)), sum(a < b for a, b in zip(wq, wg))); pv, pw = sign_p(*dv), sign_p(*dw); iv = boot(vq, vg); iw = boot(wq, wg)
    met = sum(vq) > sum(vg) and sum(wq) <= sum(wg); verdict = "PRIMARY RULE MET" if met else "PRIMARY RULE NOT MET"; small = pv >= 0.05
    M += ["", "## The decision fixed beforehand", "", "Rule: on the same jobs, the questioning guard delivers more verified repairs than the existing guard, with no increase in wrong DONE.", "",
          f"- Verified repairs: {sum(vq)} against {sum(vg)} of {len(q)}. Jobs only the questioning guard verified: {dv[0]}; only the existing guard: {dv[1]}; exact sign test p = {pv:.2g}; difference {100 * (sum(vq) - sum(vg)) / len(q):+.1f} points, paired bootstrap interval {iv[0]:+.1f} to {iv[1]:+.1f}.",
          f"- Wrong DONE: {sum(wq)} against {sum(wg)}. Jobs wrong only with the questioning guard: {dw[0]}; only with the existing guard: {dw[1]}; exact sign test p = {pw:.2g}; difference {100 * (sum(wq) - sum(wg)) / len(q):+.1f} points, interval {iw[0]:+.1f} to {iw[1]:+.1f}.", "",
          f"**{verdict}**" + (" (the difference in verified repairs is small on this many jobs: inconclusive for generalisation)" if met and small else "")]
    tr = [r for r in q if CLASS[r["kind"]] == "trap"]; od = [r for r in q if CLASS[r["kind"]] == "ordinary"]; eq = [r for r in q if CLASS[r["kind"]] == "equal"]; nt = max(1, len(tr)); qt = sum(map(nq, tr)); two = sum(nq(r) >= 2 for r in tr)
    edits = sum(S["arms"][a]["ask_with_edit"] for a in ("bankq",)); t = lambda ok: "met" if ok else "NOT met"; wb = S["arms"].get("bank", {}).get("wrong")
    M += ["", "## Targets (reported, not part of the rule)", "",
          f"- Questions per trap job, zeros included: {qt / nt:.2f} ({qt} questions on {len(tr)} trap jobs; {sum(nq(r) > 0 for r in tr)} asked at least once). Target at most 2: {t(max([nq(r) for r in tr] or [0]) <= 2)} (most on one job: {max([nq(r) for r in tr] or [0])}).",
          f"- Trap jobs that needed a second question: {two} of {len(tr)} ({100 * two / nt:.1f}%).",
          f"- Questions on ordinary jobs: {sum(map(nq, od))} on {len(od)} jobs. On equal jobs: {sum(map(nq, eq))} on {len(eq)} jobs. Target zero on both: {t(sum(map(nq, od)) + sum(map(nq, eq)) == 0)}.",
          f"- Endings by asking that left an edit behind: {edits}. Target zero: {t(edits == 0)}.",
          f"- Traps resolved: {oc(tr, 'verified')} of {len(tr)} verified (existing guard {oc([r for r in g if CLASS[r['kind']] == 'trap'], 'verified')}" + (f", plain bank {oc([r for r in R['bank'] if CLASS[r['kind']] == 'trap'], 'verified')}" if "bank" in R else "") + ").",
          f"- Wrong DONE against the plain bank: {sum(wq)} against {wb}." if wb is not None else ""]
    S["decision"] = {"verified": [sum(vq), sum(vg)], "wrong": [sum(wq), sum(wg)], "discordant_verified": dv, "discordant_wrong": dw, "p_verified": pv, "p_wrong": pw, "interval_verified_points": iv, "interval_wrong_points": iw, "verdict": verdict, "small_difference": bool(met and small),
                     "questions_per_trap": qt / nt, "traps_second_question": two, "questions_on_ordinary": sum(map(nq, od)), "questions_on_equal": sum(map(nq, eq)), "ask_with_edit": edits, "traps_verified": oc(tr, "verified"), "traps": len(tr)}
    miss = [r for r in q if CLASS[r["kind"]] == "trap" and r["outcome"] != "verified"]
    M += ["", f"## Every trap job the questioning guard did not verify ({len(miss)})", "", "| Job | Ending | Ended by | Questions | Why |", "|---|---|---|---|---|"]
    for r in miss: M.append(f"| {r['id']} | {r['outcome']} | {'procedure' if own(r) else 'fallback core'} | {nq(r)} | {'; '.join(n['fallback'] for n in Q(r)['notes'] if 'fallback' in n) or ('the bank declined; the core answered' if not own(r) else 'none recorded')} |")
M += ["", "## Costs of the questioning arms", "", "| Arm | User questions | Jobs asked | Probe executions | Changes tried against the visible checks | of them failed | Operations, all jobs | Machine seconds until the first pause or ending | Machine seconds after answers | Seconds awaiting answers (all questions) | Mean wait per question |", "|---|" + "---|" * 10]
for a in [x for x in ("bankq", "searchq") if x in R]:
    rs = R[a]; qs = sum(map(nq, rs)); tried = sum(Q(r)["changes_tried"] for r in rs); passing = sum(next((n["surviving"] for n in Q(r)["notes"] if n.get("round") == 1), 1 if own(r) and r["end"] == "DONE" else 0) for r in rs if Q(r)["changes_tried"])
    s1 = sum(st["machine_s"] for r in rs for st in Q(r)["stages"] if st["stage"] == 1); s2 = sum(st["machine_s"] for r in rs for st in Q(r)["stages"] if st["stage"] > 1); wait = sum(Q(r)["waiting_s"] for r in rs)
    S["arms"][a]["costs"] = {"questions": qs, "jobs_asked": sum(nq(r) > 0 for r in rs), "probe_executions": sum(Q(r)["probe_executions"] for r in rs), "changes_tried": tried, "changes_failed": tried - passing, "ops": sum(r["ops"] for r in rs), "machine_s_generate": s1, "machine_s_after_answer": s2, "waiting_s": wait}
    M.append(f"| {NAME[a]} | {qs} | {sum(nq(r) > 0 for r in rs)} | {sum(Q(r)['probe_executions'] for r in rs)} | {tried} | {tried - passing} | {sum(r['ops'] for r in rs)} | {s1:.1f} | {s2:.1f} | {wait:.0f} | {wait / max(1, qs):.0f} |")
M += ["", "Machine seconds until the first pause include trying every change against the visible checks and generating the question; the bank arm's column counts the procedure only, the core's own time is in the per-job figure above. The respondent's own cost of answering is not measured here."]
if "bankq" in R and "searchq" in R:
    b, s = S["arms"]["bankq"], S["arms"]["searchq"]; M += ["", "## Outside the rule: the same rule with no model and no bank", "", f"Search script with the questioning rule: {s['verified']} verified, {s['wrong']} wrong DONE, {s['asked']} clean ASK, {s['questions']} questions. Questioning guard (core and bank): {b['verified']}, {b['wrong']}, {b['asked']}, {b['questions']}."]
open(out + "_tables.md", "w").write("\n".join(x for x in M if x is not None) + "\n"); json.dump(S, open(out + "_summary.json", "w"), indent=1); print("\n".join(M))
