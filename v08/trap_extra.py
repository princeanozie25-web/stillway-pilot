"""Descriptive breakdowns of the graded trap set, beyond the pre-fixed reading.   python v08/trap_extra.py GRADED_DIR OUT.md

Written after the grades were seen; nothing here enters the verdict.  1. Codex's audit: ASK endings and whether a file
was changed.  2. Who ended each job: the bank's own script, or the core after the bank declined.  3. By fault slot.
4. Verified jobs per minute and the price of an operation."""
import collections, glob, json, os, re, sys

d, out = sys.argv[1], sys.argv[2]; R = {}
for f in sorted(glob.glob(os.path.join(d, "*.graded.jsonl"))): R[re.match(r"(.+)_s\d+\.graded", os.path.basename(f)).group(1)] = list(map(json.loads, open(f)))
CL = {"trap": "trap", "equal": "equal", "bug": "ordinary"}; own = lambda r: r.get("bank_ops", 0) > 0 and r.get("calls", 0) <= 1; O = ["verified", "wrong", "abstained", "budget"]
M = ["# v0.8 trap set: further breakdowns (descriptive, written after the grades)", ""]

M += ["## 1. Audit asked for by Codex: ASK endings and changed files", "", "| Arm | ASK endings | graded abstained | `detail.unchanged` false | non-empty diff |", "|---|---|---|---|---|"]
for a, rs in R.items():
    k = [r for r in rs if r["end"] == "ASK"]; M.append(f"| {a} | {len(k)} | {sum(r['outcome'] == 'abstained' for r in k)} | {sum(not r['detail'].get('unchanged', False) for r in k)} | {sum(bool(r.get('diff')) for r in k)} |")
M += ["", "## 2. Who ended the job (draw and top-ups together)", "", "| Arm | Class | Jobs | Bank's own script: verified / wrong / asked | Core after the bank declined: verified / wrong / asked / limit |", "|---|---|---|---|---|"]
for a in ("bank", "bankguard"):
    for cl in ("ordinary", "equal", "trap"):
        rs = [r for r in R[a] if CL[r["kind"]] == cl]; b = collections.Counter(r["outcome"] for r in rs if own(r)); c = collections.Counter(r["outcome"] for r in rs if not own(r))
        M.append(f"| {a} | {cl} | {len(rs)} | {b['verified']} / {b['wrong']} / {b['abstained']} of {sum(b.values())} | {c['verified']} / {c['wrong']} / {c['abstained']} / {c['budget']} of {sum(c.values())} |")
M += ["", "## 3. By fault slot, the unselected draw", "", "| Slot | Jobs | Traps | Plain bank wrong DONE | Guarded bank wrong DONE | Guarded bank asked | Search script wrong | Core alone wrong |", "|---|---|---|---|---|---|---|---|"]
dr = lambda a: [r for r in R[a] if r["group"] == "draw"]
for s in sorted({r["family"] for r in dr("bank")}):
    n = lambda a, o: sum(r["family"] == s and r["outcome"] == o for r in dr(a)); js = [r for r in dr("bank") if r["family"] == s]
    M.append(f"| {s} | {len(js)} | {sum(r['kind'] == 'trap' for r in js)} | {n('bank', 'wrong')} | {n('bankguard', 'wrong')} | {n('bankguard', 'abstained')} | {n('search', 'wrong')} | {n('exec', 'wrong')} |")
M += ["", "## 4. Rates on the unselected draw (120 jobs)", "", "| Arm | Verified | Wrong DONE | Asked | Wrong among DONE endings | Seconds per job | Verified per minute | Operations per job | Operations per verified job |", "|---|---|---|---|---|---|---|---|---|"]
for a in ("exec", "bank", "bankguard", "search"):
    rs = dr(a); c = collections.Counter(r["outcome"] for r in rs); T = sum(r["wall_s"] for r in rs); ops = sum(r["ops"] for r in rs); done = sum(r["end"] == "DONE" for r in rs)
    M.append(f"| {a} | {c['verified']} | {c['wrong']} | {c['abstained']} | {100 * c['wrong'] / max(1, done):.0f}% of {done} | {T / len(rs):.3f} | {60 * c['verified'] / T:.0f} | {ops / len(rs):.1f} | {ops / max(1, c['verified']):.1f} |")
open(out, "w").write("\n".join(M) + "\n"); print("\n".join(M))
