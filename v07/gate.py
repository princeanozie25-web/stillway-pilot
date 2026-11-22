"""A familiarity gate, added after development (not in the brief).   python v07/gate.py            fix the threshold from training data only
                                                                      python v07/gate.py GRADED_DIR OUT.md   score the gated arms from graded records
The gate decides BEFORE the episode which student answers: the trained one if the repository resembles a training
repository (TF-IDF similarity to the nearest training repository at or above the threshold), otherwise the unchanged one.
One episode is run either way, so the inference budget is the same as every other arm.
Threshold rule (training repositories only): for each training repository take its similarity to the nearest repository of
the SAME design and to the nearest repository of ANY OTHER design, in both cases looking only at repositories under a
DIFFERENT naming scheme (a new repository never shares a naming scheme with training); the threshold is the value that best
separates the two sets (highest balanced accuracy; midpoint of the widest tied interval).
First version of the rule (commit d5e4ca2) let the other-design neighbour share the naming scheme; shared names then
outweighed design (balanced accuracy 0.50), so the rule was corrected here, still before any development score was computed."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import bank as BK
R = BK.Retriever(); GATE = "artifacts/v07/gate.json"
def sims(repo): return (R.M @ R.vec.transform([BK.query_text(repo)]).T).toarray().ravel()
if len(sys.argv) == 1:
    same, other = [], []
    for i, t in enumerate(R.tasks):
        s = sims(t["repo"]); same.append(max(s[j] for j, u in enumerate(R.tasks) if u["skin"] != t["skin"] and u["template"] == t["template"])); other.append(max(s[j] for j, u in enumerate(R.tasks) if u["template"] != t["template"] and u["skin"] != t["skin"]))
    same, other = np.array(same), np.array(other); cand = np.unique(np.concatenate([same, other])); mids = (cand[:-1] + cand[1:]) / 2; acc = np.array([((same >= c).mean() + (other < c).mean()) / 2 for c in mids]); best = np.flatnonzero(acc == acc.max())
    tau = float((mids[best[0]] + mids[best[-1]]) / 2)
    json.dump({"threshold": round(tau, 4), "rule": "best balanced accuracy between same-design and other-design nearest similarities under a different naming scheme, training repositories only", "balanced_accuracy_on_training": round(float(acc.max()), 4),
               "same_design_similarity": {"min": round(float(same.min()), 3), "median": round(float(np.median(same)), 3)}, "other_design_similarity": {"median": round(float(np.median(other)), 3), "max": round(float(other.max()), 3)}}, open(GATE, "w"), indent=1)
    print(open(GATE).read()); sys.exit()
gdir, out = sys.argv[1], sys.argv[2]; tau = json.load(open(GATE))["threshold"]; runs = {}
for f in sorted(glob.glob(os.path.join(gdir, "*.jsonl"))):
    rows = [json.loads(l) for l in open(f)]; runs[(rows[0]["adapter"], rows[0]["insert_arm"], rows[0]["seed"])] = {r["task"]: r for r in rows}
A = runs[("base", "plain", 0)]; tasks = sorted(A); lab = {t: A[t]["labels"] for t in tasks}; seeds = sorted({k[2] for k in runs if k[0] != "base"}); ok = lambda r: r["outcome"]["first_patch_correct"]; reg = lambda r: len(r["outcome"]["regressions"]) > 0
pub = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(os.path.join(sys.argv[3] if len(sys.argv) > 3 else "data/v07/dev/public", "*.json"))}; sim = {t: float(sims(pub[t]["repo"]).max()) for t in tasks}; fam = {t: sim[t] >= tau for t in tasks}
groups = ["all", "not repeats"] + sorted({l["group"] for l in lab.values()}); member = lambda t, g: g == "all" or (g == "not repeats" and lab[t]["group"] != "G1") or lab[t]["group"] == g
P = ["# v0.7: familiarity gate (added after development; threshold from training data only)", "", f"Threshold {tau}. A repository at or above it goes to the trained student, below it to the unchanged student. One episode either way.", "",
     "## Where the gate sends repositories", "", "| Group | Repositories | Sent to the trained student | Median similarity to the nearest training repository |", "|---|---|---|---|"]
for g in groups: ts = [t for t in tasks if member(t, g)]; P.append(f"| {g} | {len(ts)} | {sum(fam[t] for t in ts)} | {np.median([sim[t] for t in ts]):.3f} |")
ARMS = [("A unchanged", None), ("F bank disabled", ("experience_x", "plain")), ("D bank", ("experience_x", "bank")), ("C experience", ("experience", "plain")), ("B final patches", ("patches", "plain"))]
def score(key, t, gated, f): return float(f(A[t])) if key is None or (gated and not fam[t]) else float(np.mean([f(runs[key + (s,)][t]) for s in seeds]))
rng = np.random.default_rng(7)
def ci(d): d = np.array(d); return np.percentile(d[rng.integers(0, len(d), (10000, len(d)))].mean(1), [2.5, 97.5])
for title, f in [("First patch correct (% of repositories, mean over seeds)", ok), ("Patch broke a hidden test that passed before (% of repositories)", reg)]:
    P += ["", "## " + title, "", "| Arm | " + " | ".join(groups) + " |", "|---|" + "---|" * len(groups)]
    for name, key in ARMS:
        for gated in ([False] if key is None else [False, True]):
            P.append(f"| {'gate + ' if gated else ''}{name} | " + " | ".join(f"{100 * np.mean([score(key, t, gated, f) for t in tasks if member(t, g)]):.1f}" for g in groups) + " |")
P += ["", "## Gated arm minus the unchanged student, paired per repository (percentage points; 95% interval by resampling repositories)", "", "| Arm | Group | Difference | Interval | Better / same / worse |", "|---|---|---|---|---|"]
for name, key in ARMS[1:]:
    for g in groups:
        d = [score(key, t, True, ok) - float(ok(A[t])) for t in tasks if member(t, g)]; lo, hi = ci(d); P.append(f"| gate + {name} | {g} | {100 * np.mean(d):+.1f} | {100 * lo:+.1f} to {100 * hi:+.1f} | {sum(x > 0 for x in d)} / {sum(x == 0 for x in d)} / {sum(x < 0 for x in d)} |")
open(out, "w").write("\n".join(P) + "\n"); print("\n".join(P))
