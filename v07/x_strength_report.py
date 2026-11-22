"""Table for the exploratory strength test.   python v07/x_strength_report.py     (writes results/v07/x_strength.md)"""
import glob, json, os, sys
import numpy as np
runs = {}
for f in sorted(glob.glob("results/v07/records/dev/graded/*.jsonl") + glob.glob("results/v07/records/x_strength/graded/*.jsonl")):
    rows = [json.loads(l) for l in open(f)]; r0 = rows[0]
    if r0["adapter"] == "base" and r0["insert_arm"] == "plain": key = (0.0, "plain")
    elif r0["adapter"] == "experience_x" and r0["insert_arm"] in ("plain", "bank"): key = (1.0, r0["insert_arm"])
    elif r0["adapter"].startswith("experience_x@"): key = (float(r0["adapter"].split("@")[1]), r0["insert_arm"])
    else: continue
    runs.setdefault(key, {})[r0["seed"]] = {r["task"]: r for r in rows}
A = runs[(0.0, "plain")][0]; tasks = sorted(A); lab = {t: A[t]["labels"]["group"] for t in tasks}
G = [("all", lambda g: True), ("unfamiliar", lambda g: g != "G1"), ("G1 renamed repeats", lambda g: g == "G1"), ("G2 changed preconditions", lambda g: g == "G2"), ("G3 lookalikes", lambda g: g == "G3"), ("G4 absent mechanisms", lambda g: g == "G4")]
def table(title, f):
    P = ["", "## " + title, "", "| Strength | Insert | Seeds | " + " | ".join(g for g, _ in G) + " |", "|---|---|---|" + "---|" * len(G)]
    for key in sorted(runs):
        R = runs[key]; P.append(f"| {key[0]:g}{' (unchanged student)' if key[0] == 0 else ' (trained adapter)' if key[0] == 1 else ''} | {'bank' if key[1] == 'bank' else 'none'} | {len(R)} | " + " | ".join(f"{100 * np.mean([f(R[s][t]) for s in R for t in tasks if m(lab[t])]):.1f}" for _, m in G) + " |")
    return P
P = ["# v0.7 exploratory: the trained adapter at reduced strength", "", "Not an arm of the frozen protocol. The D-family adapter (`experience_x`) with its contribution multiplied by the strength in every layer, on the 72 development repositories."]
P += table("First patch correct (% of repositories)", lambda r: r["outcome"]["first_patch_correct"]) + table("Patch broke a hidden test that passed before (% of repositories)", lambda r: len(r["outcome"]["regressions"]) > 0)
P += ["", "## Every seed: first-patch successes on the 48 unfamiliar repositories", "", "| Strength | Insert | " + " | ".join(f"seed {s}" for s in (1, 2, 3)) + " |", "|---|---|---|---|---|"]
for key in sorted(runs):
    if key[0] == 0: P.append(f"| 0 | none | {sum(A[t]['outcome']['first_patch_correct'] for t in tasks if lab[t] != 'G1')} (one run) | | |"); continue
    P.append(f"| {key[0]:g} | {'bank' if key[1] == 'bank' else 'none'} | " + " | ".join(str(sum(runs[key][s][t]["outcome"]["first_patch_correct"] for t in tasks if lab[t] != "G1")) if s in runs[key] else "" for s in (1, 2, 3)) + " |")
open("results/v07/x_strength.md", "w").write("\n".join(P) + "\n"); print("\n".join(P))
