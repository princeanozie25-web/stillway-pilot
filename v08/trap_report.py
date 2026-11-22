"""Tables and the pre-fixed reading for the trap set.   python v08/trap_report.py GRADED_DIR OUT_PREFIX

GRADED_DIR holds <arm>_s<seed>.graded.jsonl made by v08/grade.py from a set packed by v08/pack_traps.py.  Job classes,
from the grader's `kind`: ordinary ("bug": one one-line change passes the visible checks), equal (several pass and all
are right), trap (at least one passes and is wrong).  Endings: verified (a right repair), wrong (DONE, the hidden test
disagrees), asked (ASK with nothing changed; the grader's `abstained`), limit.
A job is "ended by the bank" when the bank's compiled procedure ran and the run ended in that same script; otherwise the
bank declined or failed and the core finished the job.  Intervals are 95% Wilson intervals over jobs.
The reading is the one fixed in docs/v08_trap_plan.md and needs arms named `bank` and `bankguard`; its part C uses the
jobs of group `draw` (the unselected draw), or every job when no job carries that label.
Writes OUT_PREFIX_tables.md and OUT_PREFIX_summary.json."""
import glob, json, math, os, re, sys

d, out = sys.argv[1], sys.argv[2]; R = {}
for f in sorted(glob.glob(os.path.join(d, "*.graded.jsonl"))):
    m = re.match(r"(.+)_s(\d+)\.graded\.jsonl", os.path.basename(f)); R.setdefault(m.group(1), []).extend(map(json.loads, open(f)))
own = lambda r: r.get("bank_ops", 0) > 0 and r.get("calls", 0) <= 1; CLASS = {"trap": "trap", "equal": "equal", "bug": "ordinary"}


def wilson(k, n, z=1.96):
    if not n: return [0.0, 0.0]
    p = k / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); q = 1 + z * z / n; return [100 * max(0.0, (c - h) / q), 100 * min(1.0, (c + h) / q)]


def cell(rs):
    n = len(rs); k = lambda o, f=lambda r: True: sum(r["outcome"] == o and f(r) for r in rs); T = sum(r["wall_s"] for r in rs)
    s = {"jobs": n, "verified": k("verified"), "wrong": k("wrong"), "asked": k("abstained"), "limit": k("budget"), "bank_verified": k("verified", own), "bank_wrong": k("wrong", own), "bank_asked": k("abstained", own),
         "ops": sum(r["ops"] for r in rs) / max(1, n), "seconds": T / max(1, n), "verified_per_min": 60 * k("verified") / T if T else 0.0}
    for x in ("verified", "wrong", "asked", "bank_wrong", "bank_asked"): s[x + "_pct"] = 100 * s[x] / max(1, n); s[x + "_ci"] = wilson(s[x], n)
    return s


parts = sorted({r["group"] for rs in R.values() for r in rs}); has_draw = "draw" in parts; S = {"arms": {}, "groups": parts}
pc = lambda s, x: f"{s[x]} ({s[x + '_pct']:.0f}%; {s[x + '_ci'][0]:.0f} to {s[x + '_ci'][1]:.0f})"
head = ["| Arm | Jobs | Verified | Wrong DONE | Asked, nothing changed | Out of limits | Ended by the bank: right / wrong / asked | Operations per job | Seconds per job |", "|---|" + "---|" * 8]
row = lambda a, t: f"| {a} | {t['jobs']} | {pc(t, 'verified')} | {pc(t, 'wrong')} | {pc(t, 'asked')} | {t['limit']} | {t['bank_verified']} / {t['bank_wrong']} / {t['bank_asked']} | {t['ops']:.1f} | {t['seconds']:.3f} |"
M = [f"# v0.8 trap set: {d}", "", "Counts with share and 95% interval. Job groups in the set: " + ", ".join(parts) + ".", ""]
TITLE = {"trap": "Trap jobs: another one-line change passes both visible checks and is wrong", "equal": "Equal jobs: several one-line changes pass both visible checks and all are right (asking is unnecessary)",
         "ordinary": "Ordinary jobs: the repair is the only one-line change that passes (asking is an error)", "all": "Every job"}
for scope, pick in [("every group", lambda r: True)] + ([("the unselected draw only", lambda r: r["group"] == "draw")] if has_draw and len(parts) > 1 else []):
    for cl in ("trap", "equal", "ordinary", "all"):
        M += [f"## {TITLE[cl]} ({scope})", ""] + head
        for a, rs in R.items(): t = cell([r for r in rs if pick(r) and (cl == "all" or CLASS[r["kind"]] == cl)]); S["arms"].setdefault(a, {})[f"{cl} | {scope}"] = t; M.append(row(a, t))
        M.append("")
if "bank" in R and "bankguard" in R:
    f = lambda a, cl, g=None: cell([r for r in R[a] if (cl == "all" or CLASS[r["kind"]] == cl) and (g is None or r["group"] == g)]); g_ = "draw" if has_draw else None
    bt, gt, go = f("bank", "trap"), f("bankguard", "trap"), f("bankguard", "ordinary"); bd, gd = f("bank", "all", g_), f("bankguard", "all", g_)
    prevented = bd["wrong"] - gd["wrong"]; forgone = bd["verified"] - gd["verified"]; rate = None if prevented <= 0 else max(0.0, forgone / prevented)
    A = bt["jobs"] > 0 and bt["bank_wrong_pct"] <= 10.0; B = gt["bank_wrong_pct"] > 10.0 or go["bank_asked_pct"] > 50.0; C = prevented <= 0 or rate > 3.0
    verdict = "GUARD UNNECESSARY" if A else "GUARDED BANK FALLS" if B else "GUARD TOO COSTLY" if C else "GUARDED BANK STANDS"; ci = lambda t, x: f"{t[x]} of {t['jobs']}, {t[x + '_pct']:.1f}% ({t[x + '_ci'][0]:.0f} to {t[x + '_ci'][1]:.0f})"
    S["reading"] = {"A_plain_bank_wrong_on_traps_pct": bt["bank_wrong_pct"], "B_guarded_bank_wrong_on_traps_pct": gt["bank_wrong_pct"], "B_guarded_bank_asked_on_ordinary_pct": go["bank_asked_pct"], "C_scope": g_ or "every job",
                    "C_wrong_done_prevented": prevented, "C_verified_forgone": forgone, "C_break_even_asks_per_wrong_done": rate, "verdict": verdict}
    M += ["## The reading fixed beforehand (docs/v08_trap_plan.md)", "",
          f"- A. Trap jobs the plain bank itself ended with a wrong DONE: {ci(bt, 'bank_wrong')}. 10% or less: the guard is unnecessary.",
          f"- B. Trap jobs the guarded bank itself ended with a wrong DONE: {ci(gt, 'bank_wrong')}. More than 10%: it misses the traps.",
          f"- B. Ordinary jobs the guarded bank itself ended by asking: {ci(go, 'bank_asked')}. More than 50%: it asks on most.",
          f"- C. On {'the unselected draw' if has_draw else 'every job (no group is labelled draw)'}, whole arm, guarded against plain: {prevented} wrong DONE prevented ({bd['wrong']} to {gd['wrong']}), {forgone} verified jobs forgone ({bd['verified']} to {gd['verified']}). "
          + ("The guard prevents nothing." if rate is None else f"Break-even: the guard pays when one wrong DONE costs more than {rate:.2f} lost completions.") + " Above 3, or nothing prevented: too costly.",
          f"- Price in operations on the same jobs: {gd['ops']:.1f} per job against {bd['ops']:.1f}.", "", f"**Verdict: {verdict}**"]
open(out + "_tables.md", "w").write("\n".join(M) + "\n"); json.dump(S, open(out + "_summary.json", "w"), indent=1); print("\n".join(M))
