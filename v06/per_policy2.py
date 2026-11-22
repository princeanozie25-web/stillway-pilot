"""Every learner, every seed, every budget from a round-two raw file.   python v06/per_policy2.py codex_hidden2
Added after the freeze; reads only.  Writes results/v06r2/<name>_per_policy.md.
(The frozen report's per-policy table has a header one column too wide: its four value columns are scratch, amend, parts, bank3a.)"""
import glob, json, sys
import numpy as np
name = sys.argv[1]; sh = [json.load(open(f)) for f in sorted(glob.glob(f"results/v06r2/{name}_shard*.json"))]; pol = sorted([p for s in sh for p in s["policies"]], key=lambda p: p["ids"][0]); B = sh[0]["budgets"]; n = sh[0]["cases"]; NS = sh[0]["seeds"]
ARMS = ("scratch", "recognise", "amend", "parts", "bank3", "bank3a", "index"); INF = float("inf"); show = lambda v: "never" if v == INF else f"{v:g}"
grp = lambda p: "repeat" if p["nearest_past_distance"] == 0 else f"amended copy, {p['nearest_past_distance']} cases" if p["nearest_past_distance"] <= 0.15 * n else "far"
def first(p, a, s, f):
    hit = [B[i] for i in range(len(B)) if p["curves"][a][i][s] and f(p["curves"][a][i][s])]; return hit[0] if hit else INF
groups = {}
for p in pol: groups.setdefault(grp(p), []).append(p)
order = sorted(groups, key=lambda g: (0, 0) if g == "repeat" else (2, 0) if g == "far" else (1, int(g.split(", ")[1].split()[0])))
P = [f"# v0.6 round 2, {name}: every learner, seed and budget", "", f"{len(pol)} new policies, {n} cases, {NS} seeds. Groups are computed from the file (cases differing from the nearest past policy); the author's labels are not used.",
     "bank3 audits at random; bank3a (the system under test) chooses its audits. All other learners audit at random.", ""]
P += ["## Audit cost by group: median over policies of the per-policy median over seeds", "", "| Group | Policies | Measure | " + " | ".join(ARMS) + " |", "|---|---|---|" + "---|" * len(ARMS)]
for g in order:
    for label, f in (("audits to 99% of cases right", lambda r: r["right_all"] >= 0.99), ("audits to every case right", lambda r: r["exact"])):
        P.append(f"| {g} | {len(groups[g])} | {label} | " + " | ".join(show(float(np.median([np.median([first(p, a, s, f) for s in range(NS)]) for p in groups[g]]))) for a in ARMS) + " |")
for title, key in (("Accuracy: mean share of all cases right (%), by budget", "right_all"), ("Cautious mode: share of cases answered wrongly (%), by budget", "cautious_wrong"), ("Cautious mode: share of cases not answered (%), by budget", "cautious_abstained")):
    P += ["", "## " + title, "", "| Group | Learner | " + " | ".join(str(b) for b in B) + " |", "|---|---|" + "---|" * len(B)]
    for g in order:
        for a in ARMS:
            cells = []
            for i in range(len(B)):
                v = [r[key] for p in groups[g] for r in p["curves"][a][i] if r and key in r]; cells.append(f"{100 * np.mean(v):.1f}" if v else "n/a")
            P.append(f"| {g} | {a} | " + " | ".join(cells) + " |")
P += ["", "## Which level bank3a used (% of policy-seed-budget cells)", "", "| Group | recognise | amend | parts | scratch |", "|---|---|---|---|---|"]
for g in order:
    u = [r.get("used") for p in groups[g] for i in range(len(B)) for r in p["curves"]["bank3a"][i] if r]; P.append(f"| {g} | " + " | ".join(f"{100 * u.count(k) / len(u):.0f}" for k in ("recognise", "amend", "parts", "scratch")) + " |")
P += ["", "## Every policy and seed: audits to 99% / to every case right", "", "| Policy | Group | Seed | " + " | ".join(ARMS) + " |", "|---|---|---|" + "---|" * len(ARMS)]
for p in pol:
    for s in range(NS): P.append(f"| {'/'.join(p['ids'])} | {grp(p)} | {s} | " + " | ".join(f"{show(first(p, a, s, lambda r: r['right_all'] >= 0.99))} / {show(first(p, a, s, lambda r: r['exact']))}" for a in ARMS) + " |")
open(f"results/v06r2/{name}_per_policy.md", "w").write("\n".join(P) + "\n"); print("\n".join(P[:P.index("## Every policy and seed: audits to 99% / to every case right") - 1]))
