"""Table for the strength test.   python v07/x_strength_report.py     (writes results/v07/x_strength.md)"""
import glob, json, os, sys
import numpy as np
runs = {}; NAME = {"patches": "final patches (B)", "experience": "experience (C)", "experience_x": "experience, D-family"}
for f in sorted(glob.glob("results/v07/records/dev/graded/*.jsonl") + glob.glob("results/v07/records/x_strength/graded/*.jsonl")):
    rows = [json.loads(l) for l in open(f)]; r0 = rows[0]; ad, _, st = r0["adapter"].partition("@")
    if r0["insert_arm"] not in ("plain", "bank") or (ad == "base" and r0["insert_arm"] != "plain") or (r0["insert_arm"] == "bank" and ad != "experience_x"): continue
    runs.setdefault((ad, float(st) if st else (0.0 if ad == "base" else 1.0), r0["insert_arm"]), {})[r0["seed"]] = {r["task"]: r for r in rows}
A = runs[("base", 0.0, "plain")][0]; tasks = sorted(A); lab = {t: A[t]["labels"]["group"] for t in tasks}
G = [("all", lambda g: True), ("unfamiliar", lambda g: g != "G1"), ("renamed repeats", lambda g: g == "G1"), ("changed preconditions", lambda g: g == "G2"), ("lookalikes", lambda g: g == "G3"), ("absent mechanisms", lambda g: g == "G4")]
order = [("base", 0.0, "plain")] + sorted(k for k in runs if k[0] != "base")
def table(title, f):
    P = ["", "## " + title, "", "| Adapter | Strength | Insert | Seeds | " + " | ".join(g for g, _ in G) + " |", "|---|---|---|---|" + "---|" * len(G)]
    for key in order:
        R = runs[key]; P.append(f"| {'none (unchanged student, A)' if key[0] == 'base' else NAME[key[0]]} | {key[1]:g} | {'bank' if key[2] == 'bank' else 'none'} | {len(R)} | " + " | ".join(f"{100 * np.mean([f(R[s][t]) for s in R for t in tasks if m(lab[t])]):.1f}" for _, m in G) + " |")
    return P
P = ["# v0.7: the trained adapters at reduced strength", "", "The adapter's contribution is multiplied by the strength in every layer: 0 is the unchanged student, 1 the adapter as trained. 72 development repositories.",
     "0.5 was tried first, on the D-family adapter. The other adapters at 0.5, and 0.25 and 0.75, were run afterwards as controls. Only 0.5 is carried to the final set."]
P += table("First patch correct (% of repositories)", lambda r: r["outcome"]["first_patch_correct"]) + table("Patch broke a hidden test that passed before (% of repositories)", lambda r: len(r["outcome"]["regressions"]) > 0)
P += ["", "## Every seed: first-patch successes on the 48 unfamiliar repositories", "", "| Adapter | Strength | Insert | seed 1 | seed 2 | seed 3 |", "|---|---|---|---|---|---|"]
for key in order:
    n = lambda R: sum(R[t]["outcome"]["first_patch_correct"] for t in tasks if lab[t] != "G1")
    P.append(f"| {'none (A)' if key[0] == 'base' else NAME[key[0]]} | {key[1]:g} | {'bank' if key[2] == 'bank' else 'none'} | " + (f"{n(A)} (one run) | | |" if key[0] == "base" else " | ".join(str(n(runs[key][s])) if s in runs[key] else "" for s in (1, 2, 3)) + " |"))
open("results/v07/x_strength.md", "w").write("\n".join(P) + "\n"); print("\n".join(P))
