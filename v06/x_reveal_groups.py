"""The locked results of the hidden family, regrouped by the author's post-lock breakdown.  Reads the raw shard only.
    python v06/x_reveal_groups.py data/external/codex/reveal_2026-11-21.tsv     -> results/v06/codex_hidden_by_reveal.md"""
import json, sys
import numpy as np
rev = [l.rstrip("\n").split("\t") for l in open(sys.argv[1])][1:]; d = json.load(open("results/v06/codex_hidden_shard0.json")); B = d["budgets"]; INF = float("inf"); pol = {p["ids"][0]: p for p in d["policies"]}
ARMS = ("scratch", "bank_row", "tables", "programs", "selector"); show = lambda v: "never" if v == INF else f"{v:g}"
def a99(p, arm, mode="passive", thr=0.99):
    rows = p["curves"][f"{mode}/{arm}"]; per = []
    for s in range(len(rows[0])):
        hit = [B[i] for i in range(len(B)) if rows[i][s]["right_all"] >= thr]; per.append(hit[0] if hit else INF)
    return float(np.median(per))
groups = {}
for r in rev: groups.setdefault(r[1], []).append(r)
for r in rev: groups.setdefault("shape: " + r[2], []).append(r)
P = ["# Hidden family: locked results regrouped by the author's breakdown", "", "Group and shape labels are Codex's, given after commit b7120cd. Numbers are from the locked raw file; none was recomputed with new runs.", "",
     "## Median audits to 99% of cases right, passive audits", "", "| Group | Policies | Distance to nearest past policy (cases of 1,440) | " + " | ".join(ARMS) + " | selector vs scratch: fewer / same / more |", "|---|---|---|" + "---|" * (len(ARMS) + 1)]
for gname, g in groups.items():
    ds = sorted(int(r[4]) for r in g); cmp_ = [sum(f(a99(pol[r[0]], "selector"), a99(pol[r[0]], "scratch")) for r in g) for f in (lambda x, y: x < y, lambda x, y: x == y, lambda x, y: x > y)]
    P.append(f"| {gname} | {len(g)} | {ds[0]} to {ds[-1]} | " + " | ".join(show(float(np.median([a99(pol[r[0]], a) for r in g]))) for a in ARMS) + f" | {cmp_[0]} / {cmp_[1]} / {cmp_[2]} |")
P += ["", "## Mean share of cases right at each budget, passive (%)", "", "| Group | Learner | " + " | ".join(str(b) for b in B) + " |", "|---|---|" + "---|" * len(B)]
for gname, g in groups.items():
    if gname.startswith("shape"): continue
    for a in ARMS: P.append(f"| {gname} | {a} | " + " | ".join(f"{100 * np.mean([x['right_all'] for r in g for x in pol[r[0]]['curves'][f'passive/{a}'][i]]):.1f}" for i in range(len(B))) + " |")
P += ["", "## Cautious mode, mean over budgets below the full table: wrong / abstained (%), passive", "", "| Group | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
for gname, g in groups.items():
    if gname.startswith("shape"): continue
    P.append(f"| {gname} | " + " | ".join(f"{100 * np.mean([x['cautious_wrong'] for r in g for i in range(len(B) - 1) for x in pol[r[0]]['curves'][f'passive/{a}'][i]]):.2f} / {100 * np.mean([x['cautious_abstained'] for r in g for i in range(len(B) - 1) for x in pol[r[0]]['curves'][f'passive/{a}'][i]]):.1f}" for a in ARMS) + " |")
P += ["", "## Scratch alone, by rule shape (how hard each shape is with no experience)", "", "| Shape | Policies | Scratch audits to 99%, each policy |", "|---|---|---|"]
for gname, g in groups.items():
    if gname.startswith("shape"): P.append(f"| {gname[7:]} | {len(g)} | " + ", ".join(f"{r[0]} {show(a99(pol[r[0]], 'scratch'))}" for r in g) + " |")
open("results/v06/codex_hidden_by_reveal.md", "w").write("\n".join(P) + "\n"); print("\n".join(P))
