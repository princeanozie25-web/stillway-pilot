"""v0.3: edit attempts and planner-alone accuracy for one register core.

    python v03/eval_edits.py runs/v3r23_s1 v02final          # the v0.2 final items: frozen v0.2 harness, v0.2 final seed
    python v03/eval_edits.py runs/v3r23_s1 dev               # development families (before the freeze)
    python v03/eval_edits.py runs/v3r23_s1 final SEED        # v0.3 final strata; SEED comes from the v0.3 freeze commit

Methods: message and resume, full restart, register write (the v0.3 editor: nothing fitted), and the four
shortcuts that must fail.  Attempt kinds, eligibility and scoring are those of docs/v02_transfer_spec.md.
Strata of mode `final` (final family buckets only; S = same-gate legs, X = cross-gate legs with probability 0.3):
  S_2to3  S_4  S_5to6  S_7to8  S_12  S_16      X_2to4  X_5to6  X_7to8  X_12  X_16
"""
import json, os, sys, time
import numpy as np, torch
from stillway2.edits import EDIT_SPEC, run_edits as run_edits_v02, summarise
from stillway3.edits import run_edits as run_edits_n
from stillway3.editor import RegisterWrite
from stillway3.model import Fixed4, load_reg
from stillway3.train import batch_eval

run = sys.argv[1].rstrip("/"); mode = sys.argv[2]; name = os.path.basename(run)
torch.set_num_threads(int(os.environ.get("THREADS", "1"))); torch.manual_seed(0)
model = load_reg(os.path.join(run, "checkpoint.pt")); ED = RegisterWrite()
V02_FINAL_SEED = 1670983329                                         # v02/final_seed.py on the v0.2 freeze commit 1470048
if mode == "v02final":
    STRATA = {"A_unseen_families": ({**EDIT_SPEC, "split": "final"}, 4), "B_four_legs": ({**EDIT_SPEC, "L": (4,), "split": None}, 4),
              "C_cross_gate": ({**EDIT_SPEC, "force_cross": True, "split": None}, 4)}
    seed0, N, SECOND = V02_FINAL_SEED, 4000, set(STRATA)
    def run_edits(n, seed, spec, lmax, method, **kw): return run_edits_v02(Fixed4(model), n, seed, spec, method, **kw)
else:
    sp = "dev" if mode == "dev" else "final"; S = {**EDIT_SPEC, "split": sp}; X = {**S, "cross": 0.3}
    if mode == "dev":
        STRATA = {"S_2to3": (S, 4), "S_5to6": ({**S, "L": (5, 6)}, 6), "X_2to4": ({**X, "L": (2, 3, 4)}, 4), "X_5to6": ({**X, "L": (5, 6)}, 6)}
        seed0, N, SECOND = 4242, 1000, {"S_2to3"}
    else:
        STRATA = {"S_2to3": (S, 4), "S_4": ({**S, "L": (4,)}, 4), "S_5to6": ({**S, "L": (5, 6)}, 6), "S_7to8": ({**S, "L": (7, 8)}, 8),
                  "S_12": ({**S, "L": (12,)}, 12), "S_16": ({**S, "L": (16,)}, 16),
                  "X_2to4": ({**X, "L": (2, 3, 4)}, 4), "X_5to6": ({**X, "L": (5, 6)}, 6), "X_7to8": ({**X, "L": (7, 8)}, 8),
                  "X_12": ({**X, "L": (12,)}, 12), "X_16": ({**X, "L": (16,)}, 16)}
        seed0, N, SECOND = int(sys.argv[3]), 2000, {"S_2to3", "S_7to8", "X_2to4", "X_7to8"}
    def run_edits(n, seed, spec, lmax, method, **kw): return run_edits_n(model, n, seed, spec, method, lmax=lmax, **kw)
N = int(os.environ.get("N", N))


def cluster_ci(x, keys, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed); u, inv = np.unique(keys, return_inverse=True)
    sums = np.bincount(inv, weights=x, minlength=len(u)); cnts = np.bincount(inv, minlength=len(u)); means = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(u), len(u)); means.append(sums[pick].sum() / max(1, cnts[pick].sum()))
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))], int(len(u))


def family_key(r):
    L, eff, tg, parcel = r["bucket_sig"]
    lo = torch.minimum(eff[:, :, 0], eff[:, :, 1]) * 4 + torch.maximum(eff[:, :, 0], eff[:, :, 1])
    return (L * 256 + lo[:, 0] * 16 + lo[torch.arange(len(L)), L - 1]).numpy()


_IGN = {}
def one(sname, spec, lmax, method, kind="flip", second=None, pairs=False, seed=0, n=N):
    kw = dict(kind=kind, mirror_pairs=pairs, second=second)
    ref = run_edits(n, seed, spec, lmax, "none", **kw)
    r = run_edits(n, seed, spec, lmax, method, editor=ED if method == "editor" else None, **kw)
    if kind == "flip":                                              # non-trivial attempts only (same rule as v0.2)
        key = (sname, second, pairs, seed, n)
        if key not in _IGN: _IGN[key] = run_edits(n, seed, spec, lmax, "ignore", **kw)["joint"]
        r["eligible_all"] = r["eligible"].clone(); r["eligible"] = r["eligible"] & ~_IGN[key]; r["joint"] = r["joint"] & r["eligible"]
    s = summarise(r, ref); e = r["eligible"].numpy()
    if "eligible_all" in r: s["eligible_before_nontrivial_filter"] = int(r["eligible_all"].sum())
    if e.sum():
        s["joint_ci95"], s["families"] = cluster_ci(r["joint"].numpy()[e].astype(float), family_key(r)[e])
        s["by_legs"] = {int(L): float(r["joint"][r["eligible"] & (r["L"] == L)].float().mean()) for L in r["L"].unique().tolist() if (r["eligible"] & (r["L"] == L)).any()}
    if pairs:
        both = r["eligible"][0::2] & r["eligible"][1::2]
        s["pairs_eligible"] = int(both.sum()); s["pairs_both_right"] = float((r["joint"][0::2] & r["joint"][1::2])[both].float().mean()) if both.any() else 0.0
    return s, r


DYN = dict(rev=0.10, gflip=0.10, decor=0.20, close=0.10, msg=0.15, full=0.05)
STRESS = dict(rev=0.4, gflip=0.4, decor=0.6, close=0.5, msg=0.45, full=0.05, reissue=0.25)
man = json.load(open(os.path.join(run, "manifest.json")))
out = {"run": name, "mode": mode, "checkpoint_sha256": model.sha256, "trained_on": man["world"], "carry": model.cfg.carry, "attempts_per_cell": N, "seed0": seed0, "strata": {}}
METHODS = ["message", "restart", "editor", "ignore", "original", "overwrite", "actioncopy"]; raw = []; t0 = time.time()
for si, (sname, (spec, lmax)) in enumerate(STRATA.items()):
    res = {}; seed = seed0 + 1000 * si
    for m in METHODS:
        s, r = one(sname, spec, lmax, m, seed=seed); res[m] = s
        raw.append({"stratum": sname, "method": m, "kind": "flip", "eligible": r["eligible"].tolist(), "joint": r["joint"].tolist(), "abstained": r["abstained"].tolist(),
                    "edited_ok": r["edited_ok"].tolist(), "unrelated_ok": r["unrelated_ok"].tolist(), "field": r["field"].tolist(), "legs": r["L"].tolist()})
    if sname in SECOND:
        for kind in ("noop", "impose", "withdraw"):
            for m in ("message", "editor"): res[f"{kind}/{m}"] = one(sname, spec, lmax, m, kind=kind, seed=seed + 1, n=N // 2)[0]
        for sec in ("same", "other"):
            for m in ("message", "restart", "editor"): res[f"two_edits_{sec}/{m}"] = one(sname, spec, lmax, m, second=sec, seed=seed + 2, n=N // 2)[0]
        for m in ("message", "editor", "actioncopy"): res[f"mirror_pairs/{m}"] = one(sname, spec, lmax, m, pairs=True, seed=seed + 3, n=N // 2)[0]
    # planner alone (no edit): share of jobs with every action valid, and share of valid actions
    res["planner_alone"] = {k: dict(zip(("jobs_all_valid", "actions_valid"), batch_eval(model, {**spec, **ev}, 2 * N, seed + 500 + j, lmax=lmax)))
                            for j, (k, ev) in enumerate((("no_events", {}), ("with_events", DYN), ("stress_events", STRESS)))}
    out["strata"][sname] = res
    print(sname, {m: (round(res[m]["joint_success"], 4), res[m]["eligible"]) for m in METHODS[:3]}, {m: round(res[m]["joint_success"], 3) for m in METHODS[3:]},
          {k: round(v["jobs_all_valid"], 4) for k, v in res["planner_alone"].items()}, round(time.time() - t0), "s", flush=True)
d = f"results/v03/{mode}"; os.makedirs(d, exist_ok=True)
json.dump(out, open(f"{d}/{name}.json", "w"), indent=1); json.dump(raw, open(f"{d}/{name}_items.json", "w"))
