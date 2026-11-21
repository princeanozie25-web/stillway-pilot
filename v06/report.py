"""Tables and pass rules for v0.6.   python v06/report.py FAMILY_NAME   -> results/v06/<name>_tables.md"""
import glob, json, sys
import numpy as np
name = sys.argv[1]; sh = [json.load(open(f)) for f in sorted(glob.glob(f"results/v06/{name}_shard*.json"))]; pol = [p for s in sh for p in s["policies"]]; B = sh[0]["budgets"]; INF = float("inf")
ARMS = ["scratch", "bank_row", "tables", "programs", "selector", "index"]; step = {b: i for i, b in enumerate(B)}
def first(p, key, th):                                              # per policy: median over seeds of the first budget reaching th
    rows = p["curves"][key]; per = []
    for s in range(len(rows[0])):
        hit = [B[i] for i in range(len(B)) if rows[i][s]["right_all"] >= th]; per.append(hit[0] if hit else INF)
    return float(np.median(per))
def med(group, key, th=0.99): return float(np.median([first(p, key, th) for p in group])) if group else None
show = lambda x: "–" if x is None else ("never" if x == INF else f"{x:.0f}")
groups = {"novel rule (not among past policies)": [p for p in pol if not p["rule_seen_among_past"]], "rule also held by a past policy": [p for p in pol if p["rule_seen_among_past"]]}
P = [f"# v0.6 result tables: {name}\n", f"{sh[0]['past_policies']} past policies ({sh[0]['past_distinct']} distinct rules), {len(pol)} distinct new policies, {sh[0]['cases']} cases each, {sh[0]['seeds']} seeds. "
     f"Program family: {sh[0]['program_family_tables']} tables. The shared network reproduces {100 * sh[0]['core_fit_on_past']:.2f}% of past decisions. New policies inside the program family: {sum(p['in_program_family'] for p in pol)} of {len(pol)}.\n"]
for gname, g in groups.items():
    P += [f"## {gname}: {len(g)} policies\n", "| Learner | Audits to 99%, passive | chosen | Audits to 100%, passive | chosen | Right at 8 / 16 / 32 audits (passive) | Cautious: wrong / abstained, mean over budgets below the full table | Fell back to scratch |", "|---|---|---|---|---|---|---|---|"]
    for a in ARMS:
        if not g: continue
        ra = lambda b: 100 * np.mean([r["right_all"] for p in g for r in p["curves"][f"passive/{a}"][step[b]]]) if b in step else float("nan")
        cw = 100 * np.mean([r["cautious_wrong"] for p in g for i in range(len(B) - 1) for r in p["curves"][f"passive/{a}"][i]]); ca = 100 * np.mean([r["cautious_abstained"] for p in g for i in range(len(B) - 1) for r in p["curves"][f"passive/{a}"][i]])
        fb = 100 * np.mean([r["fell_back"] for p in g for i in range(len(B)) for r in p["curves"][f"passive/{a}"][i]])
        P.append(f"| {a} | {show(med(g, f'passive/{a}'))} | {show(med(g, f'chosen/{a}'))} | {show(med(g, f'passive/{a}', 1.0))} | {show(med(g, f'chosen/{a}', 1.0))} | {ra(8):.1f} / {ra(16):.1f} / {ra(32):.1f} | {cw:.2f} / {ca:.1f} | {fb:.0f}% |")
    if g:
        use = {}
        for p in g:
            for i in range(len(B)):
                for r in p["curves"]["passive/selector"][i]: use[r["selector_used"]] = use.get(r["selector_used"], 0) + 1
        tot = sum(use.values()); P.append("\nSelector used: " + ", ".join(f"{k} {100 * v / tot:.0f}%" for k, v in sorted(use.items(), key=lambda kv: -kv[1])) + ".\n")
nov, seen = list(groups.values()); S = {}
def rule(label, ok, detail): P.append(f"| {label} | {detail} | {'PASS' if ok else 'FAIL'} |"); S[label] = bool(ok)
P += ["## Pass rules (frozen in `docs/v06_spec.md`)\n", "| Rule | Measured | Result |", "|---|---|---|"]
if nov:
    sc = med(nov, "passive/scratch"); best = min(med(nov, f"passive/{a}") for a in ("bank_row", "programs", "selector"))
    rule("L1. Experience helps on novel rules", best < sc, f"best of bank_row, programs, selector: {show(best)}; scratch: {show(sc)}")
    rule("L2. Programs need no more audits than bank rows on novel rules", med(nov, "passive/programs") <= med(nov, "passive/bank_row") and med(nov, "passive/programs") < INF, f"programs {show(med(nov, 'passive/programs'))}; bank_row {show(med(nov, 'passive/bank_row'))}")
    rule("L5. Choosing audits helps the selector on novel rules", med(nov, "chosen/selector") < med(nov, "passive/selector"), f"chosen {show(med(nov, 'chosen/selector'))}; passive {show(med(nov, 'passive/selector'))}")
if seen:
    cw = np.mean([r["cautious_wrong"] for p in seen for i in range(len(B)) for r in p["curves"]["chosen/tables"][i]])
    rule("L3. A rule seen before is recognised within 16 chosen audits with no cautious error", med(seen, "chosen/tables", 1.0) <= 16 and cw == 0, f"audits to 100%: {show(med(seen, 'chosen/tables', 1.0))}; cautious wrong {100 * cw:.3f}%")
ok4 = []; det = []
for gname, g in groups.items():
    if not g: continue
    best = min(med(g, f"passive/{a}") for a in ("scratch", "bank_row", "tables", "programs")); s_ = med(g, "passive/selector")
    ok4.append(s_ < INF and (best == INF or step[s_] <= step[best] + 1)); det.append(f"{gname.split(' (')[0]}: selector {show(s_)}, best single {show(best)}")
rule("L4. The selector is within one budget step of the best single learner in both groups", all(ok4), "; ".join(det))
open(f"results/v06/{name}_tables.md", "w").write("\n".join(P) + "\n"); json.dump(S, open(f"results/v06/{name}_rules.json", "w"), indent=1); print("\n".join(P))
