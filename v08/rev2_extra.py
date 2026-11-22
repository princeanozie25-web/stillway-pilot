"""Descriptive tables on Codex's revision-2 holdout, after the frozen report.   python v08/rev2_extra.py > results/v08/codex_hold_rev2_extra.md

Nothing here feeds a verdict.  Reads the graded files only."""
import collections, glob, json, os
R = "results/v08/codex_hold_rev2"
def load(sub, arm): return [json.loads(l) for f in sorted(glob.glob(f"{R}/{sub}/{arm}_s*.graded.jsonl")) for l in open(f)]
A = {"base": load("core", "base"), "exec": load("core", "exec"), "shuf": load("core", "shuf"), "prediction only": load("expl", "obsonly"), "exec seed 1 + bank": load("mem", "bank"), "exec seed 1 + guarded bank": load("mem", "bankguard"), "search script": load("core", "search")}
ok = lambda r: r["outcome"] == "verified"
print("# Codex's revision-2 holdout: descriptive tables\n\nComputed after the frozen report. Nothing here feeds a verdict.\n")
print("## 1. What a verified project job costs when an operation has a price\n\nCost per verified job = (seconds per job + price x operations per job) / verified share. Seeds pooled.\n")
print("| | Jobs | Seconds per job | Operations per job | Verified % | Cost at 0 s per operation | at 0.05 s | at 0.5 s | Cheaper than the search script above |\n|---|---|---|---|---|---|---|---|---|")
P = {}
for a, rs in A.items():
    rs = [r for r in rs if r["dom"] == "proj"]; n = len(rs); P[a] = (sum(r["wall_s"] for r in rs) / n, sum(r["ops"] for r in rs) / n, sum(map(ok, rs)) / n, n)
s0, o0, v0, _ = P["search script"]
for a, (s, o, v, n) in P.items():
    cost = lambda c: (s + c * o) / v
    den = o0 / v0 - o / v; x = (s / v - s0 / v0) / den if den > 0 else None
    print(f"| {a} | {n} | {s:.3f} | {o:.1f} | {100 * v:.1f} | {cost(0):.2f} | {cost(.05):.2f} | {cost(.5):.2f} | {'' if a == 'search script' else 'never' if x is None else f'{1000 * x:.0f} ms per operation'} |")
print("\n## 2. The bank arms, job by job (exec seed 1; 220 jobs)\n")
print("| Arm | Verified | Wrong | Asked, correctly | Asked on an answerable job | Out of limits | Finished by the bank | Operations per job |\n|---|---|---|---|---|---|---|---|")
core1 = {r["id"]: r for r in load("core", "exec") [:220]}
for a in ("exec seed 1 + bank", "exec seed 1 + guarded bank"):
    rs = A[a]; ask = [r for r in rs if r["end"] == "ASK"]
    print(f"| {a} | {sum(map(ok, rs))} | {sum(r['outcome'] == 'wrong' for r in rs)} | {sum(r['kind'] == 'unans' for r in ask)} | {sum(r['kind'] != 'unans' for r in ask)} | {sum(r['outcome'] == 'budget' for r in rs)} | {sum(r['bank_ops'] > 0 and r['calls'] <= 1 for r in rs)} | {sum(r['ops'] for r in rs) / len(rs):.1f} |")
rs = list(core1.values()); ask = [r for r in rs if r["end"] == "ASK"]
print(f"| exec seed 1 alone | {sum(map(ok, rs))} | {sum(r['outcome'] == 'wrong' for r in rs)} | {sum(r['kind'] == 'unans' for r in ask)} | {sum(r['kind'] != 'unans' for r in ask)} | {sum(r['outcome'] == 'budget' for r in rs)} | 0 | {sum(r['ops'] for r in rs) / len(rs):.1f} |")
for a in ("exec seed 1 + bank", "exec seed 1 + guarded bank"):
    print(f"\n**{a}: every job not verified**\n\n| Job | Domain | Group | Mechanism | Route | Outcome | End | Bank operations | Scripts | The core alone on this job |\n|---|---|---|---|---|---|---|---|---|---|")
    for r in A[a]:
        if not ok(r): print(f"| {r['id']} | {r['dom']} | {r['group']} | {r['mech']} | {r['route']} | {r['outcome']} | {r['end']} | {r['bank_ops']} | {r['calls']} | {core1[r['id']]['outcome']} |")
b = {r["id"]: r for r in A["exec seed 1 + bank"]}; g = {r["id"]: r for r in A["exec seed 1 + guarded bank"]}; c = collections.Counter((b[i]["outcome"], g[i]["outcome"]) for i in b)
print("\n**Plain bank against guarded bank, same jobs** (plain outcome, guarded outcome, jobs): " + "; ".join(f"{x} → {y}: {n}" for (x, y), n in sorted(c.items())))
c = collections.Counter((core1[i]["outcome"], b[i]["outcome"]) for i in b)
print("\n**Core alone against core + plain bank** (alone, with bank, jobs): " + "; ".join(f"{x} → {y}: {n}" for (x, y), n in sorted(c.items())))
