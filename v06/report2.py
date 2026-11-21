"""v0.6 round 2 tables and pass rules.   python v06/report2.py FAMILY_NAME [LABELS.tsv]
Groups are set by the distance to the nearest past policy (cases that differ): repeat = 0; amended copy = up to 15% of cases;
far = more than 15%.  With the author's labels (tab-separated: policy, group, ...) the far group is split as the author says."""
import glob, json, sys
import numpy as np
name = sys.argv[1]; sh = [json.load(open(f)) for f in sorted(glob.glob(f"results/v06r2/{name}_shard*.json"))]; pol = sorted([p for s in sh for p in s["policies"]], key=lambda p: p["ids"][0]); B = sh[0]["budgets"]; n = sh[0]["cases"]; INF = float("inf")
lab = {l.split("\t")[0]: l.rstrip("\n").split("\t")[1] for l in open(sys.argv[2]).readlines()[1:]} if len(sys.argv) > 2 else {}
ARMS = ("scratch", "recognise", "amend", "parts", "bank3", "bank3a", "index"); SUT = "bank3a"; show = lambda v: "never" if v == INF else f"{v:g}"
def grp(p):
    d = p["nearest_past_distance"]
    if d == 0: return "repeat"
    if d <= 0.15 * n: return "amended copy"
    return ("far: " + lab[p["ids"][0]].lower()) if lab else "far"
def first(p, a, f):
    per = []
    for s in range(sh[0]["seeds"]):
        hit = [B[i] for i in range(len(B)) if p["curves"][a][i][s] and f(p["curves"][a][i][s])]; per.append(hit[0] if hit else INF)
    return float(np.median(per))
a99 = lambda p, a: first(p, a, lambda r: r["right_all"] >= 0.99); aex = lambda p, a: first(p, a, lambda r: r["exact"])
def mean(g, a, key, lo=0, hi=None):
    v = [r[key] for p in g for i in range(lo, len(B) if hi is None else hi) for r in p["curves"][a][i] if r]; return float(np.mean(v)) if v else float("nan")
groups = {}
for p in pol: groups.setdefault(grp(p), []).append(p)
P = [f"# v0.6 round 2 tables: {name}", "", f"{len(pol)} new policies, {n} cases, {sh[0]['seeds']} seeds, passive audits, budgets {B}.", ""]; S = {}
for gname in sorted(groups):
    g = groups[gname]; ds = sorted(p["nearest_past_distance"] for p in g)
    P += [f"## {gname}: {len(g)} policies (cases differing from the nearest past policy: {ds[0]} to {ds[-1]})", "", "| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |", "|---|---|---|---|---|---|"]
    for a in ARMS:
        if all(r is None for p in g for i in range(len(B)) for r in p["curves"][a][i]): P.append(f"| {a} | not applicable | | | | |"); continue
        low = np.mean([min(np.mean([r["right_all"] for r in p["curves"][a][i] if r]) for i in range(len(B)) if any(p["curves"][a][i])) for p in g if any(r for i in range(len(B)) for r in p["curves"][a][i])])
        P.append(f"| {a} | {show(float(np.median([a99(p, a) for p in g])))} | {show(float(np.median([aex(p, a) for p in g])))} | " + " / ".join(f"{100 * mean(g, a, 'right_all', B.index(b), B.index(b) + 1):.1f}" for b in (8, 32, 128, 512)) + f" | {100 * mean(g, a, 'cautious_wrong', 0, len(B) - 1):.2f} / {100 * mean(g, a, 'cautious_abstained', 0, len(B) - 1):.1f} | {100 * low:.1f} |")
    used = {}
    for p in g:
        for i in range(len(B)):
            for r in p["curves"][SUT][i]: used[r["used"]] = used.get(r["used"], 0) + 1
    P += ["", SUT + " used: " + ", ".join(f"{k} {100 * v / sum(used.values()):.0f}%" for k, v in sorted(used.items(), key=lambda kv: -kv[1])) + ".", ""]
def rule(text, ok, detail): S[text] = None if ok is None else bool(ok); P.append(f"| {text} | {detail} | {'not testable (no such policies)' if ok is None else 'PASS' if ok else 'FAIL'} |")
P += ["## Pass rules (frozen in `docs/v06r2_spec.md`)", "", "| Rule | Measured | Result |", "|---|---|---|"]
rep = groups.get("repeat", []); am = groups.get("amended copy", []); far = [p for k, g in groups.items() if k.startswith("far") for p in g]; med = lambda g, f, a: float(np.median([f(p, a) for p in g]))
if rep: rule("M1. A repeat is found exactly within 16 audits, with no cautious error", med(rep, aex, SUT) <= 16 and mean(rep, SUT, "cautious_wrong") == 0, f"audits to every case right: {show(med(rep, aex, SUT))}; cautious wrong {100 * mean(rep, SUT, 'cautious_wrong'):.3f}%")
else: rule("M1. A repeat is found exactly within 16 audits, with no cautious error", None, "")
if am:
    hold = [min(np.mean([r["right_all"] for r in p["curves"][SUT][i]]) for i in range(len(B)) if B[i] >= 16) >= 1 - p["nearest_past_distance"] / n - 0.02 for p in am]
    rule("M2a. An amended copy never collapses: from 16 audits on, at least as right as its original table, less 2 points (on 80% of amended copies)", np.mean(hold) >= 0.8, f"holds on {sum(hold)} of {len(am)}")
    rule("M2b. An amended copy is learned exactly with fewer audits than from scratch", med(am, aex, SUT) < med(am, aex, "scratch"), f"{SUT} {show(med(am, aex, SUT))}; scratch {show(med(am, aex, 'scratch'))}")
    rule("M2c. Cautious errors on amended copies stay at or below 1%", mean(am, SUT, "cautious_wrong", 0, len(B) - 1) <= 0.01, f"{100 * mean(am, SUT, 'cautious_wrong', 0, len(B) - 1):.2f}%")
else:
    for t in ("M2a. An amended copy never collapses: from 16 audits on, at least as right as its original table, less 2 points (on 80% of amended copies)", "M2b. An amended copy is learned exactly with fewer audits than from scratch", "M2c. Cautious errors on amended copies stay at or below 1%"): rule(t, None, "")
if far:
    worst = min(100 * (mean(far, SUT, "right_all", i, i + 1) - mean(far, "scratch", "right_all", i, i + 1)) for i in range(len(B)) if B[i] >= 16)
    rule("M3. On policies far from every past one the bank does no harm: audits to 99% within one doubling of scratch, and from 16 audits on never more than 3 points below scratch", med(far, a99, SUT) <= 2 * med(far, a99, "scratch") and worst >= -3, f"{SUT} {show(med(far, a99, SUT))}; scratch {show(med(far, a99, 'scratch'))}; largest shortfall {worst:+.1f} points")
    rule("M4. On policies far from every past one the bank helps: fewer audits to 99% than scratch", med(far, a99, SUT) < med(far, a99, "scratch"), f"{SUT} {show(med(far, a99, SUT))}; scratch {show(med(far, a99, 'scratch'))}")
    rule("M5. The bank's cautious errors are no higher than scratch's on far policies", mean(far, SUT, "cautious_wrong", 0, len(B) - 1) <= mean(far, "scratch", "cautious_wrong", 0, len(B) - 1), f"{SUT} {100 * mean(far, SUT, 'cautious_wrong', 0, len(B) - 1):.2f}%; scratch {100 * mean(far, 'scratch', 'cautious_wrong', 0, len(B) - 1):.2f}%")
P += ["", "## Per policy: audits to 99% / to every case right (median of seeds)", "", "| Policy | Group | Distance | scratch | amend | parts | bank3 | bank3a |", "|---|---|---|---|---|---|---|---|"]
for p in pol: P.append(f"| {'/'.join(p['ids'])} | {grp(p)} | {p['nearest_past_distance']} | " + " | ".join(f"{show(a99(p, a))} / {show(aex(p, a))}" for a in ("scratch", "amend", "parts", SUT)) + " |")
open(f"results/v06r2/{name}_tables.md", "w").write("\n".join(P) + "\n"); json.dump(S, open(f"results/v06r2/{name}_rules.json", "w"), indent=1); print("\n".join(P))
