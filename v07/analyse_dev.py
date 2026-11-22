"""Extra tables from graded records, beyond v07/report.py.   python v07/analyse_dev.py GRADED_DIR OUT.md
Per-seed contrasts, which diagnostic the bank retrieved and whether it was the right one, what happened on lookalikes
after the diagnostic was reopened, and witnesses (repositories the unchanged student fixes and no trained arm does)."""
import glob, json, os, sys
gdir, out = sys.argv[1], sys.argv[2]; runs = {}
for f in sorted(glob.glob(os.path.join(gdir, "*.jsonl"))):
    rows = [json.loads(l) for l in open(f)]; runs[(rows[0]["adapter"], rows[0]["insert_arm"], rows[0]["seed"])] = {r["task"]: r for r in rows}
A = runs[("base", "plain", 0)]; tasks = sorted(A); lab = {t: A[t]["labels"] for t in tasks}; seeds = sorted({k[2] for k in runs if k[0] != "base"}); ok = lambda r: r["outcome"]["first_patch_correct"]
nonrep = [t for t in tasks if lab[t]["group"] != "G1"]; P = ["# v0.7 development: extra tables", ""]
P += ["## The bank's effect, seed by seed (first-patch successes on the 48 repositories that are not repeats)", "", "| Seed | A unchanged | F bank disabled | D bank | W wrong diagnostic | E nearest example | D minus F | D better / worse than F |", "|---|---|---|---|---|---|---|---|"]
for s in seeds:
    g = lambda arm: runs[("experience_x", arm, s)]; n = lambda R: sum(ok(R[t]) for t in nonrep)
    P.append(f"| {s} | {n(A)} | {n(g('plain'))} | {n(g('bank'))} | {n(g('wrong'))} | {n(g('example'))} | {n(g('bank')) - n(g('plain')):+d} | {sum(ok(g('bank')[t]) > ok(g('plain')[t]) for t in nonrep)} / {sum(ok(g('bank')[t]) < ok(g('plain')[t]) for t in nonrep)} |")
P += ["", "## Which diagnostic the bank handed over (arm D, all seeds)", "", "A repository's own symptom is S1, S2 or S3 where it shares a trained symptom; absent mechanisms (G4) have none, so any diagnostic is the wrong one there.", "",
      "| Group | Episodes | Diagnostic matches the repository's symptom | First patch correct when it matches | First patch correct when it does not |", "|---|---|---|---|---|"]
for g in ["G1", "G2", "G3", "G4"]:
    R = [runs[("experience_x", "bank", s)][t] for s in seeds for t in tasks if lab[t]["group"] == g]; m = [r for r in R if r["inserts"][0]["meta"]["diagnostic"] == r["labels"]["symptom"]]; x = [r for r in R if r not in m]
    pc = lambda L: f"{100 * sum(map(ok, L)) / len(L):.0f}% ({sum(map(ok, L))} of {len(L)})" if L else "none"
    P.append(f"| {g} | {len(R)} | {len(m)} of {len(R)} | {pc(m)} | {pc(x)} |")
P += ["", "## Lookalikes (G3): what the student did after its prediction was contradicted", "", "| Arm | Episodes | Contradicted | Submitted the trained fix anyway (fails exactly as the trained fix does) | of those, after a contradiction | Broke a hidden test | Correct |", "|---|---|---|---|---|---|---|"]
for name, key in [("A unchanged", ("base", "plain")), ("B final patches", ("patches", "plain")), ("C experience", ("experience", "plain")), ("F bank disabled", ("experience_x", "plain")), ("D bank", ("experience_x", "bank")), ("D1 bank, version 1 only", ("experience_x", "bank_v1")), ("W wrong diagnostic", ("experience_x", "wrong")), ("E nearest example", ("experience_x", "example"))]:
    R = [runs[key + (s,)][t] for s in ([0] if key[0] == "base" else seeds) for t in tasks if lab[t]["group"] == "G3"]; con = lambda r: any(not h["as_predicted"] for h in r["tests"]); old = [r for r in R if r["outcome"].get("same_failures_as_old_fix")]
    P.append(f"| {name} | {len(R)} | {sum(map(con, R))} | {len(old)} | {sum(map(con, old))} | {sum(len(r['outcome']['regressions']) > 0 for r in R)} | {sum(map(ok, R))} |")
P += ["", "## Witnesses: repositories the unchanged student fixes and trained students mostly do not", ""]
tr = [k for k in runs if k[0] != "base"]
for t in tasks:
    if not ok(A[t]): continue
    wins = sum(ok(runs[k][t]) for k in tr)
    if wins > len(tr) // 6: continue
    d = runs[("experience_x", "bank", seeds[0])][t]; b = runs[("patches", "plain", seeds[0])][t]
    P += [f"### {t} ({lab[t]['group']}, {lab[t]['template']}): unchanged student correct; trained runs correct in {wins} of {len(tr)}", "", "Unchanged student's patch:", "```", A[t]["patch"]["info"]["diff"] if A[t]["patch"]["applied"] else "(not applied)", "```",
          f"D (bank, seed {seeds[0]}): diagnostic handed over {d['inserts'][0]['meta']['diagnostic']}; stated cause: {d['patch'].get('cause')!r}; hidden failures: {[k for k, v in d['outcome']['hidden'].items() if v != 'PASS']}; broke: {d['outcome']['regressions']}", "```", d["patch"]["info"]["diff"] if d["patch"]["applied"] else "(not applied)", "```",
          f"B (final patches, seed {seeds[0]}): hidden failures: {[k for k, v in b['outcome']['hidden'].items() if v != 'PASS']}; broke: {b['outcome']['regressions']}", "```", b["patch"]["info"]["diff"] if b["patch"]["applied"] else "(not applied)", "```", ""]
open(out, "w").write("\n".join(P) + "\n"); print("\n".join(P))
