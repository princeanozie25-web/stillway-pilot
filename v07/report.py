"""Tables from graded records.   python v07/report.py GRADED_DIR OUT_PREFIX
Unit of analysis: the repository.  An arm's score on a repository is its mean first-patch success over seeds.
Uncertainty: 10,000 bootstrap resamples of repositories, and of whole families (templates) of repositories."""
import glob, json, os, sys
import numpy as np
gdir, prefix = sys.argv[1], sys.argv[2]; rng = np.random.default_rng(7)
NAMES = {("base", "plain"): "A unchanged", ("base", "bank"): "AD unchanged + bank", ("base", "example"): "AE unchanged + nearest example", ("patches", "plain"): "B final patches", ("experience", "plain"): "C experience", ("experience_x", "bank"): "D experience + bank", ("experience_x", "example"): "E experience + nearest example",
         ("experience_x", "plain"): "F bank disabled", ("experience_x", "wrong"): "W wrong diagnostic", ("experience_x", "bank_v1"): "D1 bank, version 1 only"}
runs = {}
for f in sorted(glob.glob(os.path.join(gdir, "*.jsonl"))):
    rows = [json.loads(l) for l in open(f)]; key = (rows[0]["adapter"], rows[0]["insert_arm"]); runs.setdefault(NAMES.get(key, "/".join(key)), {})[rows[0]["seed"]] = {r["task"]: r for r in rows}
def norm_group(g):
    """Group names as the holder of a set wrote them -> G1 renamed repeats, G2 changed preconditions, G3 lookalikes, G4 absent mechanisms; EX exact repeats (training repositories, which carry no group)."""
    x = str(g).lower()
    return "EX" if g is None else "G1" if "repeat" in x else "G2" if "precondition" in x else "G3" if "lookalike" in x or "look-alike" in x else "G4" if "absent" in x else str(g)
for a in runs:
    for sd in runs[a]:
        for r in runs[a][sd].values(): r["labels"]["group"] = norm_group(r["labels"]["group"])
arms = sorted(runs); tasks = sorted(next(iter(next(iter(runs.values())).values()))); lab = {t: next(iter(runs[arms[0]].values()))[t]["labels"] for t in tasks}
GROUPS = [("all", lambda l: True), ("not repeats (G2+G3+G4)", lambda l: l["group"] not in ("G1", "EX"))] + [(g, (lambda g: lambda l: l["group"] == g)(g)) for g in sorted({l["group"] for l in lab.values()}, key=str)]
GROUPS = [(g, f) for g, f in GROUPS if any(f(lab[t]) for t in tasks)]
score = lambda arm, t, f=lambda r: r["outcome"]["first_patch_correct"]: float(np.mean([f(runs[arm][s][t]) for s in runs[arm]]))
def boot(d, fams):
    d = np.array(d); n = len(d); lo, hi = np.percentile(d[rng.integers(0, n, (10000, n))].mean(1), [2.5, 97.5]); fam = sorted(set(fams)); by = {f: d[[i for i, x in enumerate(fams) if x == f]] for f in fam}; bs = []
    for _ in range(4000):
        pick = rng.integers(0, len(fam), len(fam)); x = np.concatenate([by[fam[i]] for i in pick]); bs.append(x.mean())
    flo, fhi = np.percentile(bs, [2.5, 97.5]); return float(d.mean()), float(lo), float(hi), float(flo), float(fhi)
P = [f"# v0.7 results: {os.path.basename(prefix)}", "", f"{len(tasks)} repositories. Arms and seeds: " + "; ".join(f"{a} ({len(runs[a])} seed{'s' if len(runs[a]) > 1 else ''})" for a in arms) + ".", ""]; J = {"arms": {}, "contrasts": {}}
P += ["## First submitted patch passes hidden grading (% of repositories; mean over seeds)", "", "| Arm | " + " | ".join(f"{g} (n={sum(f(lab[t]) for t in tasks)})" for g, f in GROUPS) + " |", "|---|" + "---|" * len(GROUPS)]
for a in arms:
    cells = []; J["arms"][a] = {}
    for g, f in GROUPS:
        ts = [t for t in tasks if f(lab[t])]; v = 100 * np.mean([score(a, t) for t in ts]); cells.append(f"{v:.1f}"); J["arms"][a][g] = round(float(v), 2)
    P.append(f"| {a} | " + " | ".join(cells) + " |")
P += ["", "## Every seed", "", "| Arm | Seed | " + " | ".join(g for g, _ in GROUPS) + " |", "|---|---|" + "---|" * len(GROUPS)]
for a in arms:
    for s in sorted(runs[a]): P.append(f"| {a} | {s} | " + " | ".join(f"{sum(runs[a][s][t]['outcome']['first_patch_correct'] for t in tasks if f(lab[t]))}/{sum(f(lab[t]) for t in tasks)}" for g, f in GROUPS) + " |")
CONTRASTS = [("D experience + bank", "A unchanged"), ("C experience", "A unchanged"), ("B final patches", "A unchanged"), ("D experience + bank", "B final patches"), ("C experience", "B final patches"), ("D experience + bank", "F bank disabled"), ("D experience + bank", "E experience + nearest example"), ("E experience + nearest example", "F bank disabled"), ("W wrong diagnostic", "F bank disabled"), ("D experience + bank", "D1 bank, version 1 only"), ("D experience + bank", "W wrong diagnostic"), ("F bank disabled", "A unchanged"), ("AD unchanged + bank", "A unchanged"), ("AE unchanged + nearest example", "A unchanged")]
P += ["", "## Paired differences per repository (percentage points; 95% interval by resampling repositories, then by resampling whole families)", "", "| Contrast | Group | Difference | Repositories | Families | Better / same / worse |", "|---|---|---|---|---|---|"]
for x, y in CONTRASTS:
    if x not in runs or y not in runs: continue
    for g, f in GROUPS:
        ts = [t for t in tasks if f(lab[t])]; d = [score(x, t) - score(y, t) for t in ts]; m, lo, hi, flo, fhi = boot(d, [lab[t]["template"] for t in ts])
        P.append(f"| {x} minus {y} | {g} | {100 * m:+.1f} | {100 * lo:+.1f} to {100 * hi:+.1f} | {100 * flo:+.1f} to {100 * fhi:+.1f} | {sum(v > 0 for v in d)} / {sum(v == 0 for v in d)} / {sum(v < 0 for v in d)} |")
        J["contrasts"][f"{x} minus {y} | {g}"] = {"difference": round(100 * m, 2), "ci_repositories": [round(100 * lo, 2), round(100 * hi, 2)], "ci_families": [round(100 * flo, 2), round(100 * fhi, 2)], "better": int(sum(v > 0 for v in d)), "same": int(sum(v == 0 for v in d)), "worse": int(sum(v < 0 for v in d))}
P += ["", "## Regressions, tests and cost (all repositories; mean over seeds)", "", "| Arm | Repositories with a hidden test broken by the patch | Patch applied | Tests well formed | Predictions that matched execution | Visible tests pass but hidden fail | Seconds of generation per repository | New tokens per repository | Generation seconds per correct fix |", "|---|---|---|---|---|---|---|---|---|"]
for a in arms:
    R = [runs[a][s][t] for s in runs[a] for t in tasks]; ok = sum(r["outcome"]["first_patch_correct"] for r in R)
    P.append(f"| {a} | {100 * np.mean([len(r['outcome']['regressions']) > 0 for r in R]):.1f}% | {100 * np.mean([r['patch']['applied'] for r in R]):.1f}% | {100 * np.mean([h['well_formed'] for r in R for h in r['tests']]):.1f}% | {100 * np.mean([h['as_predicted'] for r in R for h in r['tests']]):.1f}% | "
             f"{100 * np.mean([bool(r['outcome'].get('visible_all_pass')) and not r['outcome']['first_patch_correct'] for r in R]):.1f}% | {np.mean([r['generation_seconds'] for r in R]):.1f} | {np.mean([r['new_tokens'] for r in R]):.0f} | {(sum(r['generation_seconds'] for r in R) / ok if ok else float('nan')):.1f} |")
    J["arms"][a]["regression_share"] = round(100 * float(np.mean([len(r["outcome"]["regressions"]) > 0 for r in R])), 2); J["arms"][a]["generation_seconds_per_correct_fix"] = round(sum(r["generation_seconds"] for r in R) / ok, 2) if ok else None
P += ["", "## Regressions by group (% of repositories where the patch broke a hidden test that passed before)", "", "| Arm | " + " | ".join(g for g, _ in GROUPS) + " |", "|---|" + "---|" * len(GROUPS)]
for a in arms: P.append(f"| {a} | " + " | ".join(f"{100 * np.mean([score(a, t, lambda r: len(r['outcome']['regressions']) > 0) for t in tasks if f(lab[t])]):.1f}" for g, f in GROUPS) + " |")
of = [t for t in tasks if any("same_failures_as_old_fix" in runs[a][s][t]["outcome"] for a in arms for s in runs[a])]
if of:
    P += ["", f"## Repositories where the trained fix does not belong ({len(of)}): share where the submitted patch fails exactly as the trained fix does", "", "| Arm | Lookalikes (G3) | Other groups |", "|---|---|---|"]
    for a in arms:
        f = lambda r: bool(r["outcome"].get("same_failures_as_old_fix")); g3 = [t for t in of if lab[t]["group"] == "G3"]; ot = [t for t in of if lab[t]["group"] != "G3"]
        P.append(f"| {a} | {100 * np.mean([score(a, t, f) for t in g3]) if g3 else float('nan'):.1f}% | {100 * np.mean([score(a, t, f) for t in ot]) if ot else float('nan'):.1f}% |")
P += ["", "## After a contradiction: episodes in which at least one test did not come out as predicted", "", "| Arm | Episodes with a contradiction | First patch correct after a contradiction | First patch correct with no contradiction |", "|---|---|---|---|"]
for a in arms:
    R = [runs[a][s][t] for s in runs[a] for t in tasks]; c = [r for r in R if any(not h["as_predicted"] for h in r["tests"])]; n = [r for r in R if all(h["as_predicted"] for h in r["tests"])]
    P.append(f"| {a} | {len(c)} of {len(R)} | {100 * np.mean([r['outcome']['first_patch_correct'] for r in c]) if c else float('nan'):.1f}% | {100 * np.mean([r['outcome']['first_patch_correct'] for r in n]) if n else float('nan'):.1f}% |")
for a in arms:
    if (next(iter(next(iter(runs[a].values())).values()))["inserts"][0]["meta"] or {}).get("kind") != "bank": continue
    R = [(s, runs[a][s][t]) for s in sorted(runs[a]) for t in tasks]; use = {}; rows = {}
    for s, r in R:
        m = r["inserts"][0]["meta"]; k = (s, m["diagnostic"]); use[k] = use.get(k, 0) + 1; b = "use 1-5" if use[k] <= 5 else "use 6-15" if use[k] <= 15 else "use 16+"; st = r["inserts"][-1]["meta"]["status"]
        for key in (("by use", b), ("by status at the patch", st), ("by diagnostic", m["diagnostic"])): rows.setdefault(key, []).append(r["outcome"]["first_patch_correct"])
    P += ["", f"## {a}: correctness by repeated use, status and diagnostic", "", "| Split | Value | Episodes | First patch correct |", "|---|---|---|---|"] + [f"| {k[0]} | {k[1]} | {len(v)} | {100 * np.mean(v):.1f}% |" for k, v in sorted(rows.items())]
# ---- the frozen rules of docs/v07_protocol.md ----
NR = "not repeats (G2+G3+G4)"; C = lambda x, y, g=NR: J["contrasts"].get(f"{x} minus {y} | {g}")
def rule(name, text, c, test):
    if c is None: return {"rule": name, "text": text, "result": "not computable (an arm or group is missing)"}
    return {"rule": name, "text": text, "difference": c["difference"], "ci_repositories": c["ci_repositories"], "ci_families": c["ci_families"], "better_worse": [c["better"], c["worse"]], "result": "PASS" if test(c) else "FAIL"}
big = lambda th: lambda c: c["difference"] >= th and c["ci_repositories"][0] > 0
RULES = [rule("P1", "experience helps on unfamiliar repositories: D minus A at least +10 points on repositories that are not repeats, interval (repositories) above 0", C("D experience + bank", "A unchanged"), big(10)),
         rule("R1", "recognition: D minus A at least +10 points on renamed repeats, interval above 0", C("D experience + bank", "A unchanged", "G1"), big(10)),
         rule("S1", "verified experience beats final patches: C minus B at least +5 points on repositories that are not repeats, interval above 0", C("C experience", "B final patches"), big(5)),
         rule("S2", "the bank adds to the same student: D minus F at least +5 points on repositories that are not repeats, and better on more repositories than worse", C("D experience + bank", "F bank disabled"), lambda c: c["difference"] >= 5 and c["better"] > c["worse"]),
         rule("S3", "the bank beats ordinary retrieval: D minus E at least +5 points on repositories that are not repeats, and better on more than worse", C("D experience + bank", "E experience + nearest example"), lambda c: c["difference"] >= 5 and c["better"] > c["worse"]),
         rule("S4", "the content of the diagnostic matters: D minus W (wrong diagnostic) at least +5 points on repositories that are not repeats, and better on more than worse", C("D experience + bank", "W wrong diagnostic"), lambda c: c["difference"] >= 5 and c["better"] > c["worse"])]
if "D experience + bank" in runs and "A unchanged" in runs:
    rg = lambda a, g: 100 * float(np.mean([score(a, t, lambda r: len(r["outcome"]["regressions"]) > 0) for t in tasks if dict(GROUPS)[g](lab[t])])) if any(dict(GROUPS)[g](lab[t]) for t in tasks) else None
    for name, g, text in [("P2", NR, "no excess of regressions: share of repositories that are not repeats where D's patch breaks a hidden test is at most 10 points above A's"), ("S5", "G3", "the old fix is not carried onto lookalikes: share of lookalikes where D's patch breaks a hidden test is at most 10 points above A's")]:
        d, a = (rg("D experience + bank", g), rg("A unchanged", g)) if g in dict(GROUPS) else (None, None)
        RULES.append({"rule": name, "text": text, "D": None if d is None else round(d, 2), "A": None if a is None else round(a, 2), "result": "not computable" if d is None else "PASS" if d <= a + 10 else "FAIL"})
res = {r["rule"]: r["result"] for r in RULES}
verdict = ("PASS: experience helps on unfamiliar repositories" + ("" if res.get("P2") == "PASS" else ", WITH an excess of regressions (P2 fails)") if res.get("P1") == "PASS" else
           "RECOGNITION RESULT: the gain is confined to repeats" if res.get("R1") == "PASS" else "NULL: no gain on unfamiliar repositories or on repeats" if res.get("P1") == "FAIL" else "not computable")
J["rules"] = RULES; J["verdict"] = verdict
P += ["", "## Frozen rules (docs/v07_protocol.md)", "", "| Rule | What it says | Measured | Result |", "|---|---|---|---|"]
for r in RULES: P.append(f"| {r['rule']} | {r['text']} | " + (f"{r['difference']:+.1f} ({r['ci_repositories'][0]:+.1f} to {r['ci_repositories'][1]:+.1f}); better {r['better_worse'][0]}, worse {r['better_worse'][1]}" if "difference" in r else f"D {r['D']}%, A {r['A']}%" if r.get("D") is not None else "") + f" | **{r['result']}** |")
P += ["", f"**Verdict by the frozen rules: {verdict}**"]
P += ["", "## Per repository (first patch correct in how many seeds)", "", "| Repository | Group | Family | " + " | ".join(a.split(" ")[0] for a in arms) + " |", "|---|---|---|" + "---|" * len(arms)]
for t in tasks: P.append(f"| {t} | {lab[t]['group']} | {lab[t]['template']} | " + " | ".join(f"{sum(runs[a][s][t]['outcome']['first_patch_correct'] for s in runs[a])}/{len(runs[a])}" for a in arms) + " |")
open(prefix + "_tables.md", "w").write("\n".join(P) + "\n"); json.dump(J, open(prefix + "_summary.json", "w"), indent=1); print("\n".join(P[:P.index("## Per repository (first patch correct in how many seeds)")]))
