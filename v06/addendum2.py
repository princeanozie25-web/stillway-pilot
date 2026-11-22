"""Addendum to the locked round-two run, by the holder's groups.   python v06/addendum2.py codex_hidden2
Added after the lock (a79545b) and after the holder released the group labels below; reads the locked raw file only and
changes none of it.  Writes results/v06r2/<name>_addendum.md."""
import glob, json, sys
import numpy as np
name = sys.argv[1]; sh = [json.load(open(f)) for f in sorted(glob.glob(f"results/v06r2/{name}_shard*.json"))]
pol = {p["ids"][0]: p for s in sh for p in s["policies"]}; B = sh[0]["budgets"]; n = sh[0]["cases"]; NS = sh[0]["seeds"]
HOLDER = {"local amendment": "p037 p040 p041 p043 p052 p055 p059 p061", "scattered amendment": "p047 p049 p057 p058",
          "far variant": "p044 p045 p053 p056 p060 p066", "new shape": "p039 p042 p050 p054 p063 p064"}
G = {g: v.split() for g, v in HOLDER.items()}; named = {i for v in G.values() for i in v}
G = {"repeat": sorted(i for i in pol if i not in named), **G}; assert all(pol[i]["nearest_past_distance"] == 0 for i in G["repeat"]) and sum(map(len, G.values())) == len(pol)
ARMS = ("scratch", "recognise", "amend", "parts", "bank3", "bank3a", "index"); INF = float("inf"); show = lambda v: "never" if v == INF else f"{v:g}"
def first(p, a, s, f):
    hit = [B[i] for i in range(len(B)) if p["curves"][a][i][s] and f(p["curves"][a][i][s])]; return hit[0] if hit else INF
exact = lambda r: r["exact"]; ok99 = lambda r: r["right_all"] >= 0.99
med = lambda g, a, f: float(np.median([np.median([first(pol[i], a, s, f) for s in range(NS)]) for i in G[g]]))
rng = lambda g, a, f: (min(first(pol[i], a, s, f) for i in G[g] for s in range(NS)), max(first(pol[i], a, s, f) for i in G[g] for s in range(NS)))
P = [f"# v0.6 round 2, {name}: addendum by the holder's groups", "",
     "Attached to the results locked at commit a79545b; the locked files are unchanged. The group labels were released by the holder after the lock.",
     f"{len(pol)} new policies, {n} cases each, {NS} seeds, budgets {', '.join(map(str, B))}. bank3a is the system under test and chooses its audits; scratch and bank3 audit at random.", "",
     "| Group (holder's label) | Policies | Cases changed from the nearest past policy |", "|---|---|---|"]
for g in G: P.append(f"| {g} | {' '.join(G[g])} | {', '.join(str(pol[i]['nearest_past_distance']) for i in G[g])} |")
for title, f in (("Exact-learning cost: audits until every case is right", exact), ("Audits until 99% of cases are right", ok99)):
    P += ["", f"## {title}", "", "Each cell: median over policies of the per-policy median over seeds, then (smallest to largest over every policy and seed). Budgets are a grid, so a cost is the first grid point that reaches the mark.", "",
          "| Group | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
    for g in G: P.append(f"| {g} | " + " | ".join(f"{show(med(g, a, f))} ({show(rng(g, a, f)[0])} to {show(rng(g, a, f)[1])})" for a in ARMS) + " |")
P += ["", "## Exact-learning cost of bank3a by amendment size", "", "| Group | Cases changed | Policy | bank3a, each seed | scratch, each seed |", "|---|---|---|---|---|"]
for g in ("local amendment", "scattered amendment"):
    for i in sorted(G[g], key=lambda i: pol[i]["nearest_past_distance"]):
        P.append(f"| {g} | {pol[i]['nearest_past_distance']} | {i} | " + " | ".join(", ".join(show(first(pol[i], a, s, exact)) for s in range(NS)) for a in ("bank3a", "scratch")) + " |")
P += ["", "## Worst interim accuracy against keeping the old rule", "",
      "Keeping the old rule means answering every case with the nearest past policy: it is right on (cases - cases changed) / cases. Worst interim is the lowest share of cases right at any budget before the full table.",
      "Columns: mean old-rule accuracy; then for each learner the mean over policies of the per-policy worst (over seeds and budgets below 1,600), the single worst cell, and the share of policy-seed-budget cells that fall below the old rule.", "",
      "| Group | Old rule, % right | " + " | ".join(f"{a}: mean worst / single worst / cells below old rule" for a in ("scratch", "bank3", "bank3a")) + " |", "|---|---|---|---|---|"]
for g in G:
    old = {i: 1 - pol[i]["nearest_past_distance"] / n for i in G[g]}; cells = []
    for a in ("scratch", "bank3", "bank3a"):
        v = {i: [r["right_all"] for bi in range(len(B) - 1) for r in pol[i]["curves"][a][bi] if r] for i in G[g]}
        below = sum(x < old[i] - 1e-12 for i in G[g] for x in v[i]); tot = sum(len(v[i]) for i in G[g])
        cells.append(f"{100 * np.mean([min(v[i]) for i in G[g]]):.2f} / {100 * min(min(v[i]) for i in G[g]):.2f} / {100 * below / tot:.0f}%")
    P.append(f"| {g} | {100 * np.mean(list(old.values())):.2f} | " + " | ".join(cells) + " |")
P += ["", "### bank3a against the old rule at each budget (mean % right minus old-rule % right; lowest single cell in brackets)", "", "| Group | " + " | ".join(map(str, B)) + " |", "|---|" + "---|" * len(B)]
for g in G:
    row = []
    for bi in range(len(B)):
        d = [100 * (r["right_all"] - (1 - pol[i]["nearest_past_distance"] / n)) for i in G[g] for r in pol[i]["curves"]["bank3a"][bi] if r]; row.append(f"{np.mean(d):+.2f} ({min(d):+.2f})")
    P.append(f"| {g} | " + " | ".join(row) + " |")
for a in ("bank3a", "bank3", "scratch"):
    P += ["", f"## Cautious mode, {a}: answer coverage % / error among answered cases %", "", "Coverage is the share of cases answered. Error is wrong answers divided by answers given, pooled over the group's policies and seeds; n/a where nothing was answered.", "",
          "| Group | " + " | ".join(map(str, B)) + " |", "|---|" + "---|" * len(B)]
    for g in G:
        row = []
        for bi in range(len(B)):
            rs = [r for i in G[g] for r in pol[i]["curves"][a][bi] if r]; cov = np.mean([1 - r["cautious_abstained"] for r in rs]); wr = np.mean([r["cautious_wrong"] for r in rs])
            row.append(f"{100 * cov:.1f} / " + (f"{100 * wr / cov:.2f}" if cov > 0 else "n/a"))
        P.append(f"| {g} | " + " | ".join(row) + " |")
open(f"results/v06r2/{name}_addendum.md", "w").write("\n".join(P) + "\n"); print("\n".join(P))
