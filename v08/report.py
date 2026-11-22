"""Tables and the frozen comparison for the small core.   python v08/report.py GRADED_DIR OUT_PREFIX [--primary exec:base] [--rule]

GRADED_DIR holds <arm>_s<seed>.graded.jsonl.  Jobs are paired across arms and seeds by id.  Verified jobs per minute is
verified jobs divided by the total wall time of every job (failed ones included), times 60.  Intervals: 2,000 bootstrap
resamples of task families (clusters), jobs within the family carried along, seeds pooled; each seed is also listed.
Writes OUT_PREFIX_tables.md and OUT_PREFIX_summary.json."""
import collections, glob, json, os, re, sys
import numpy as np

d, out = sys.argv[1], sys.argv[2]; primary = sys.argv[sys.argv.index("--primary") + 1].split(":") if "--primary" in sys.argv else ["exec", "base"]
R = collections.defaultdict(dict)
for f in sorted(glob.glob(os.path.join(d, "*.graded.jsonl"))):
    m = re.match(r"(.+)_s(\d+)\.graded\.jsonl", os.path.basename(f)); R[m.group(1)][int(m.group(2))] = {r["id"]: r for r in map(json.loads, open(f))}
arms = sorted(R); DOMS = ("proj", "tab"); ok = lambda r: r["outcome"] == "verified"
first = lambda r: ok(r) and r["edit_scripts"] <= 1 and not any(l == "REVERT" for s in r["steps"] for l in s["script"])
failed_edit = lambda r: sum(any(o.startswith("FAIL") for o in s["obs"]) and any(l.split()[0] in ("PATCH", "COPY", "KEEP", "DROP", "ADD", "SKIP", "RECALC") for l in s["script"]) for s in r["steps"])


def stats(rs):
    n = len(rs); T = sum(r["wall_s"] for r in rs); v = sum(map(ok, rs)); ans = [r for r in rs if r["end"] == "DONE"]; w = np.array([r["wall_s"] for r in rs])
    return {"jobs": n, "verified": v, "verified_pct": 100 * v / n, "first_attempt_pct": 100 * sum(map(first, rs)) / n, "wrong": sum(r["outcome"] == "wrong" for r in rs), "abstained": sum(r["outcome"] == "abstained" for r in rs),
            "budget": sum(r["outcome"] == "budget" for r in rs), "coverage_pct": 100 * len(ans) / n, "error_among_answers_pct": 100 * sum(not ok(r) for r in ans) / max(1, len(ans)), "jobs_per_min": 60 * v / T,
            "scripts": float(np.mean([r["calls"] for r in rs])), "ops": float(np.mean([r["ops"] for r in rs])), "failed_edits_per_solved": sum(map(failed_edit, rs)) / max(1, v), "bad_ops": sum(r["bad_ops"] for r in rs),
            "tokens": float(np.mean([r["tokens_in"] + r["tokens_out"] for r in rs])), "tokens_out": float(np.mean([r["tokens_out"] for r in rs])), "model_s": float(np.mean([r["model_s"] for r in rs])), "exec_s": float(np.mean([r["exec_s"] for r in rs])),
            "wall_p10": float(np.percentile(w, 10)), "wall_p50": float(np.percentile(w, 50)), "wall_p90": float(np.percentile(w, 90)), "wall_max": float(w.max())}


def pool(arm, f=lambda r: True): return [r for s in sorted(R[arm]) for r in R[arm][s].values() if f(r)]
S = {"arms": {}, "contrasts": {}}; M = [f"# v0.8 tables: {d}", ""]
cols = [("jobs", "Jobs", "{:d}"), ("verified_pct", "Verified %", "{:.1f}"), ("first_attempt_pct", "First attempt %", "{:.1f}"), ("coverage_pct", "Answered %", "{:.1f}"), ("error_among_answers_pct", "Error among answers %", "{:.1f}"),
        ("jobs_per_min", "Verified jobs / min", "{:.1f}"), ("scripts", "Scripts / job", "{:.2f}"), ("ops", "Operations / job", "{:.2f}"), ("failed_edits_per_solved", "Failed edits / solved job", "{:.3f}"), ("tokens", "Tokens / job", "{:.0f}"),
        ("wall_p50", "Latency median s", "{:.3f}"), ("wall_p90", "p90 s", "{:.3f}"), ("wall_max", "max s", "{:.2f}")]
for dom in DOMS + ("all",):
    f = (lambda r: True) if dom == "all" else (lambda r, dom=dom: r["dom"] == dom); M += [f"## {dom}: every arm, seeds pooled", "", "| Arm | Seeds | " + " | ".join(c[1] for c in cols) + " |", "|---|---|" + "---|" * len(cols)]
    for a in arms:
        st = stats(pool(a, f)); S["arms"].setdefault(a, {})[dom] = st; M.append(f"| {a} | {len(R[a])} | " + " | ".join(c[2].format(st[c[0]]) for c in cols) + " |")
    M.append("")
M += ["## Each seed: verified % / verified jobs per minute", "", "| Arm | Seed | " + " | ".join(DOMS) + " |", "|---|---|---|---|"]
for a in arms:
    for s in sorted(R[a]):
        cells = []
        for dom in DOMS: st = stats([r for r in R[a][s].values() if r["dom"] == dom]); cells.append(f"{st['verified_pct']:.1f} / {st['jobs_per_min']:.1f}")
        S["arms"][a].setdefault("seeds", {})[s] = cells; M.append(f"| {a} | {s} | " + " | ".join(cells) + " |")
M += ["", "## By group: verified % (answered % / error among answers %), seeds pooled", ""]
groups = sorted({(r["dom"], r["group"]) for a in arms for r in pool(a)}); M += ["| Domain | Group | Jobs | " + " | ".join(arms) + " |", "|---|---|---|" + "---|" * len(arms)]
for dom, g in groups:
    row = []
    for a in arms: st = stats(pool(a, lambda r: r["dom"] == dom and r["group"] == g)); row.append(f"{st['verified_pct']:.1f} ({st['coverage_pct']:.0f} / {st['error_among_answers_pct']:.0f})"); S["arms"][a].setdefault("groups", {})[f"{dom}/{g}"] = st
    M.append(f"| {dom} | {g} | {len(next(iter(R[arms[0]].values())) and [r for r in next(iter(R[arms[0]].values())).values() if r['dom'] == dom and r['group'] == g])} | " + " | ".join(row) + " |")
routes = sorted({r["route"] for a in arms for r in pool(a) if r["route"]})
if routes:
    M += ["", "## proj faults by route: verified %", "", "local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).", "",
          "| Route | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for rt in routes: M.append(f"| {rt} | " + " | ".join(f"{stats(pool(a, lambda r: r['route'] == rt))['verified_pct']:.1f}" for a in arms) + " |")


def contrast(a, b, dom):
    """Paired, clustered by family: ratio of verified jobs per minute and difference in verified share (points)."""
    seeds = sorted(set(R[a]) & set(R[b])); ids = [i for i in R[a][seeds[0]] if R[a][seeds[0]][i]["dom"] == dom or dom == "all"]; fam = collections.defaultdict(list)
    for i in ids: fam[R[a][seeds[0]][i]["family"]].append(i)
    F = sorted(fam); cell = {x: {f: np.array([[sum(ok(R[x][s][i]) for i in fam[f]), sum(R[x][s][i]["wall_s"] for i in fam[f]), len(fam[f])] for s in seeds]).sum(0) for f in F} for x in (a, b)}
    def stat(fs):
        A = sum(cell[a][f] for f in fs); B = sum(cell[b][f] for f in fs); return (A[0] / A[1]) / max(1e-9, B[0] / B[1]), 100 * (A[0] / A[2] - B[0] / B[2])
    rng = np.random.default_rng(0); bs = np.array([stat([F[j] for j in rng.integers(0, len(F), len(F))]) for _ in range(2000)]); pt = stat(F)
    per_seed = []
    for s in seeds:
        A = stats([R[a][s][i] for i in ids]); B = stats([R[b][s][i] for i in ids]); per_seed.append([A["jobs_per_min"] / max(1e-9, B["jobs_per_min"]), A["verified_pct"] - B["verified_pct"]])
    return {"families": len(F), "seeds": seeds, "rate_ratio": pt[0], "rate_ratio_ci": [float(np.percentile(bs[:, 0], 2.5)), float(np.percentile(bs[:, 0], 97.5))], "verified_diff": pt[1],
            "verified_diff_ci": [float(np.percentile(bs[:, 1], 2.5)), float(np.percentile(bs[:, 1], 97.5))], "per_seed": per_seed}


pairs = [tuple(primary)] + [(a, primary[1]) for a in arms if a not in primary and set(R[a]) & set(R[primary[1]])] + ([(primary[0], "shuf")] if "shuf" in R and primary[0] in R else [])
pairs = [p for p in pairs if p[0] in R and p[1] in R]
if pairs:
    M += ["", "## Paired contrasts (first arm against second)", "", "Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.", "",
          "| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |", "|---|---|---|---|---|---|"]
    for a, b in pairs:
        for dom in DOMS + ("all",):
            c = contrast(a, b, dom); S["contrasts"][f"{a}:{b}:{dom}"] = c
            M.append(f"| {a} vs {b} | {dom} | {c['families']} | {c['rate_ratio']:.3f} ({c['rate_ratio_ci'][0]:.3f} to {c['rate_ratio_ci'][1]:.3f}) | {c['verified_diff']:+.1f} ({c['verified_diff_ci'][0]:+.1f} to {c['verified_diff_ci'][1]:+.1f}) | " + "; ".join(f"{r:.3f} / {v:+.1f}" for r, v in c["per_seed"]) + " |")
if "--rule" in sys.argv and tuple(primary) in pairs:
    a, b = primary; c = {dom: S["contrasts"][f"{a}:{b}:{dom}"] for dom in DOMS}
    win = all(c[x]["rate_ratio"] >= 1.10 and c[x]["rate_ratio_ci"][0] > 1.0 and c[x]["verified_diff"] >= -2.0 for x in DOMS)
    lose = any(c[x]["rate_ratio_ci"][1] < 1.10 for x in DOMS) or any(c[x]["verified_diff_ci"][1] < -2.0 for x in DOMS)
    verdict = "WIN" if win else "NO WIN" if lose else "INCONCLUSIVE"; S["verdict"] = verdict
    M += ["", "## Frozen primary rule", "", f"WIN needs, in each domain: rate ratio of {a} to {b} at least 1.10 with the interval above 1.00, and verified share no more than 2 points lower.",
          "NO WIN if in either domain the whole interval of the ratio is below 1.10 or the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.", ""]
    M += [f"- {x}: ratio {c[x]['rate_ratio']:.3f} ({c[x]['rate_ratio_ci'][0]:.3f} to {c[x]['rate_ratio_ci'][1]:.3f}); verified {c[x]['verified_diff']:+.1f} points ({c[x]['verified_diff_ci'][0]:+.1f} to {c[x]['verified_diff_ci'][1]:+.1f})" for x in DOMS] + ["", f"**Verdict: {verdict}**"]
open(out + "_tables.md", "w").write("\n".join(M) + "\n"); json.dump(S, open(out + "_summary.json", "w"), indent=1); print("\n".join(M))
