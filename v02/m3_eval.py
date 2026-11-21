"""M3: evaluate the edit methods for one v0.2 core.

    python v02/m3_eval.py runs/v2_iit_s1 dev                 # development families (selection)
    python v02/m3_eval.py runs/v2_iit_s1 final SEED          # final strata; SEED comes from the freeze commit

Editors are fitted on TRAINING families only (stillway2/editors.py).  The predictor's abstention threshold
is set on development data and stored in runs/NAME/editors.pt, so the final run only loads it.

Final strata (none of them was ever sampled before the freeze):
  A  unseen families at trained sizes: 2 or 3 legs, same-gate legs, hash buckets 70-99
  B  4 legs (training never had more than 3)
  C  cross-gate legs: at least one leg whose two routes act on different gates (training had none)
"""
import json, os, sys, time
import numpy as np, torch
from stillway2.edits import EDIT_SPEC, run_edits, summarise
from stillway2.editors import Predictor, SlotWrite, order_states, twin_states
from stillway2.model3 import load3

run = sys.argv[1].rstrip("/"); mode = sys.argv[2]; name = os.path.basename(run)
torch.set_num_threads(int(os.environ.get("THREADS", "1"))); torch.manual_seed(0)
model = load3(os.path.join(run, "checkpoint.pt")); man = json.load(open(os.path.join(run, "manifest.json")))
iit_core = man["args"]["iit"] > 0
STRATA = {"dev": {"dev": dict(EDIT_SPEC)},
          "final": {"A_unseen_families": {**EDIT_SPEC, "split": "final"}, "B_four_legs": {**EDIT_SPEC, "L": (4,), "split": None},
                    "C_cross_gate": {**EDIT_SPEC, "force_cross": True, "split": None}}}[mode]
N = int(os.environ.get("N", "4000")); seed0 = int(sys.argv[3]) if mode == "final" else 4242
ed_path = os.path.join(run, "editors.pt")

# ---- editors -------------------------------------------------------------------------------------------
if mode == "dev":
    t0 = time.time(); data = twin_states(model, 6000, 31337); fit_seconds_data = time.time() - t0
    sw = SlotWrite(model, order_states(model, 12000, 27182))
    pr = Predictor(model); t0 = time.time(); pr.fit(data, steps=6000); fit_seconds_pred = time.time() - t0
    held = twin_states(model, 2000, 99991)                     # training families, other jobs
    # Abstention threshold, set on DEVELOPMENT attempts (other jobs than the reported dev results): the lowest
    # threshold at which at least 99% of the edits the predictor ACCEPTS succeed.  If none reaches 99%, the
    # threshold with the highest joint success (abstentions counted as failures).
    devd = twin_states(model, 3000, 5151, spec={**EDIT_SPEC, "rev": 0.15, "gflip": 0.15, "decor": 0.3, "close": 0.2})
    with torch.no_grad():
        new, _ = pr(devd["pre"], devd["field"], devd["value"]); right = (new == devd["post"]).all(1)
    ign = run_edits(model, 3000, 777, EDIT_SPEC, "ignore")["joint"]; cand = []; best = None
    for tau in [0.0, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99]:
        pr.tau = tau; r_ = run_edits(model, 3000, 777, EDIT_SPEC, "editor", editor=pr); e_ = r_["eligible"] & ~ign
        acc = e_ & ~r_["abstained"]; row = (tau, float(acc.sum() / e_.sum()), float(r_["joint"][acc].float().mean()) if acc.any() else 0.0, float((r_["joint"] & e_).sum() / e_.sum()))
        cand.append(row)
        if best is None and row[2] >= 0.99: best = row
    if best is None: best = max(cand, key=lambda x: x[3])
    pr.tau = best[0]; best = (best[0], best[1])
    torch.save({"slot_table": sw.table, "slot_known": sw.known, "slot_purity": sw.purity, "pred_state": pr.state_dict(), "pred_tau": pr.tau}, ed_path)
    fit_info = {"twin_pairs": int(len(data["pre"])), "twin_seconds": round(fit_seconds_data, 1), "predictor_fit_seconds": round(fit_seconds_pred, 1),
                "predictor_exact_match_train_families_heldout_jobs": pr.exact_match(held), "predictor_exact_match_dev_families": float(right.float().mean()),
                "predictor_tau": pr.tau, "predictor_accept_rate_dev_at_tau": best[1], "predictor_tau_table_tau_accept_acceptedsuccess_joint": cand, "slot_table": sw.table.tolist(),
                "slot_purity": [[round(x, 3) for x in r] for r in sw.purity.tolist()], "slot_known_codes": sw.known.sum(1).tolist(),
                "predictor_parameters": sum(p.numel() for p in pr.parameters())}
else:
    ck = torch.load(ed_path, weights_only=True)
    sw = SlotWrite.__new__(SlotWrite); sw.table, sw.known, sw.purity = ck["slot_table"], ck["slot_known"], ck["slot_purity"]
    pr = Predictor(model); pr.load_state_dict(ck["pred_state"]); pr.tau = ck["pred_tau"]; pr.eval(); fit_info = {"loaded": ed_path}
EDITORS = {"slot_write": sw, "predictor": pr}

# ---- evaluation ----------------------------------------------------------------------------------------
def cluster_ci(x, keys, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed); u, inv = np.unique(keys, return_inverse=True)
    sums = np.bincount(inv, weights=x, minlength=len(u)); cnts = np.bincount(inv, minlength=len(u))
    means = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(u), len(u)); means.append(sums[pick].sum() / max(1, cnts[pick].sum()))
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))], int(len(u))

def family_key(r):
    L, eff, tg, parcel = r["bucket_sig"]
    lo = torch.minimum(eff[:, :, 0], eff[:, :, 1]) * 4 + torch.maximum(eff[:, :, 0], eff[:, :, 1])
    last = lo[torch.arange(len(L)), L - 1]
    return (L * 256 + lo[:, 0] * 16 + last).numpy()               # (legs, first-leg mechanism pair, last-leg mechanism pair)

_IGN = {}
def one(spec, method, kind="flip", editor=None, second=None, pairs=False, seed=0, n=N):
    ref = run_edits(model, n, seed, spec, "none", kind, mirror_pairs=pairs, second=second)
    r = run_edits(model, n, seed, spec, method, kind, editor=editor, mirror_pairs=pairs, second=second)
    if kind == "flip":
        # non-trivial attempts only: the same job with the correction ignored must fail (same for every method)
        key = (id(spec), kind, second, pairs, seed, n)
        if key not in _IGN: _IGN[key] = run_edits(model, n, seed, spec, "ignore", kind, mirror_pairs=pairs, second=second)["joint"]
        r["eligible_all"] = r["eligible"].clone(); r["eligible"] = r["eligible"] & ~_IGN[key]; r["joint"] = r["joint"] & r["eligible"]
    s = summarise(r, ref); e = r["eligible"].numpy()
    if "eligible_all" in r: s["eligible_before_nontrivial_filter"] = int(r["eligible_all"].sum())
    if e.sum():
        s["joint_ci95"], s["families"] = cluster_ci(r["joint"].numpy()[e].astype(float), family_key(r)[e])
        s["by_legs"] = {int(L): float(r["joint"][r["eligible"] & (r["L"] == L)].float().mean()) for L in r["L"].unique().tolist() if (r["eligible"] & (r["L"] == L)).any()}
    if pairs:
        j = (r["joint"] | ~r["eligible"]); both = r["eligible"][0::2] & r["eligible"][1::2]
        s["pairs_eligible"] = int(both.sum()); s["pairs_both_right"] = float((r["joint"][0::2] & r["joint"][1::2])[both].float().mean()) if both.any() else 0.0
    return s, r

out = {"run": name, "mode": mode, "checkpoint_sha256": model.sha256, "core": "interchange-trained" if iit_core else "plain imitation",
       "attempts_per_cell": N, "editors": fit_info, "strata": {}}
METHODS = ["message", "restart", "editor:slot_write", "editor:predictor", "ignore", "original", "overwrite", "actioncopy"]
raw_rows = []
for si, (sname, spec) in enumerate(STRATA.items()):
    res = {}; seed = seed0 + 1000 * si
    for m in METHODS:
        ed = EDITORS[m.split(":")[1]] if m.startswith("editor") else None
        s, r = one(spec, m.split(":")[0], editor=ed, seed=seed); res[m] = s
        raw_rows.append({"stratum": sname, "method": m, "kind": "flip", "eligible": r["eligible"].tolist(), "joint": r["joint"].tolist(),
                         "abstained": r["abstained"].tolist(), "edited_ok": r["edited_ok"].tolist(), "unrelated_ok": r["unrelated_ok"].tolist(),
                         "field": r["field"].tolist(), "legs": r["L"].tolist()})
    for kind in ("noop", "impose", "withdraw"):
        for m in ("message", "editor:slot_write", "editor:predictor"):
            ed = EDITORS[m.split(":")[1]] if m.startswith("editor") else None
            res[f"{kind}/{m}"] = one(spec, m.split(":")[0], kind=kind, editor=ed, seed=seed + 1, n=N // 2)[0]
    for sec in ("same", "other"):
        for m in ("message", "restart", "editor:slot_write", "editor:predictor"):
            ed = EDITORS[m.split(":")[1]] if m.startswith("editor") else None
            res[f"two_edits_{sec}/{m}"] = one(spec, m.split(":")[0], editor=ed, second=sec, seed=seed + 2, n=N // 2)[0]
    for m in ("message", "editor:slot_write", "editor:predictor", "actioncopy"):
        ed = EDITORS[m.split(":")[1]] if m.startswith("editor") else None
        res[f"mirror_pairs/{m}"] = one(spec, m.split(":")[0], editor=ed, pairs=True, seed=seed + 3, n=N // 2)[0]
    out["strata"][sname] = res
    print(sname, {m: (round(res[m]["joint_success"], 3), round(res[m]["abstained"], 3), res[m]["eligible"]) for m in METHODS}, flush=True)

# ---- reference with privileged setup: per-family sampled dictionary (fewer attempts; it is slow to set up) ----
from stillway2.dictref import DictRef
ND = int(os.environ.get("N_DICT", "400"))
for si, (sname, spec) in enumerate(STRATA.items()):
    seed = seed0 + 1000 * si + 77; t0 = time.time()
    dr = DictRef(model, ND, seed, spec); setup = time.time() - t0
    ref = run_edits(model, ND, seed, spec, "none"); rd = run_edits(model, ND, seed, spec, "editor", editor=dr); rm = run_edits(model, ND, seed, spec, "message")
    out["strata"][sname]["dictionary_reference"] = {**summarise(rd, ref), "message_same_attempts": summarise(rm, ref)["joint_success"],
                                                    "setup_seconds": round(setup, 1), "target_family_jobs_sampled_with_labels": dr.jobs_sampled}
    print(sname, "dictionary", json.dumps(out["strata"][sname]["dictionary_reference"]), flush=True)

# ---- latency: one paused job, one correction, batch of one, after warm-up -------------------------------
def latency():
    from stillway2.world3 import World3, ROUTE, DELIVER
    from stillway2.edits import make_plan
    gen = torch.Generator().manual_seed(7); spec = list(STRATA.values())[0]; n = 300
    w = World3(n, {**spec, "env": "model"}, gen); plan = make_plan(w, torch.Generator().manual_seed(8), "flip")
    ids = torch.full((n, model.cfg.n_slots), -1); obs0, _ = w.next_obs(); _, ids = model.infer(ids, obs0)
    obs_plain, act = w.next_obs(); w2 = w.clone(); w2.t -= 1
    obs_msg, _ = w2.next_obs({"rows": torch.ones(n, dtype=torch.bool), "field": plan["field"], "value": plan["value"], "show": True})
    f, v = plan["field"], plan["value"]; T = {k: [] for k in ("core_step_with_message", "slot_write_edit_only", "slot_write_then_core_step", "predictor_edit_only", "predictor_then_core_step")}
    with torch.no_grad():
        for rep in range(3):
            for i in range(n):
                a, b, c, d = ids[i:i + 1], obs_msg[i:i + 1], obs_plain[i:i + 1], (f[i:i + 1], v[i:i + 1])
                t = time.perf_counter(); model.infer(a, b); t1 = time.perf_counter() - t
                t = time.perf_counter(); e, _ = sw(a, *d); t2 = time.perf_counter() - t
                t = time.perf_counter(); e, _ = sw(a, *d); model.infer(e, c); t3 = time.perf_counter() - t
                t = time.perf_counter(); e, _ = pr(a, *d); t4 = time.perf_counter() - t
                t = time.perf_counter(); e, _ = pr(a, *d); model.infer(e, c); t5 = time.perf_counter() - t
                if rep:
                    for k, x in zip(T, (t1, t2, t3, t4, t5)): T[k].append(x * 1e6)
    # symbolic field memory + incremental planning: change one entry of a table, re-plan the next route exactly
    from stillway2.world3 import ref_valid_routes
    jobs = [(int(w.L[i]), w.eff[i].tolist(), w.tg[i].tolist(), w.gates[i].tolist(), w.q[i].tolist(), int(w.cur[i]), int(f[i]), int(v[i])) for i in range(n)]
    T["symbolic_table_update_and_replan"] = []
    for rep in range(3):
        for (L_, e_, t_, g_, q_, c_, f_, v_) in jobs:
            t = time.perf_counter(); order = list(q_)
            if f_ < 2: order[f_] = v_
            ref_valid_routes(L_, e_, t_, g_, order, min(c_, L_ - 1)); dt = time.perf_counter() - t
            if rep: T["symbolic_table_update_and_replan"].append(dt * 1e6)
    q = lambda x, p: float(np.percentile(x, p))
    return {k: {"median_us": round(q(x, 50), 1), "p99_us": round(q(x, 99), 1), "n": len(x)} for k, x in T.items()}
out["latency_cpu_1_thread"] = latency()
os.makedirs("results/v02/m3", exist_ok=True)
json.dump(out, open(f"results/v02/m3/{name}_{mode}.json", "w"), indent=1)
json.dump(raw_rows, open(f"results/v02/m3/{name}_{mode}_items.json", "w"))
print(json.dumps(out["latency_cpu_1_thread"])); print(json.dumps({k: v for k, v in fit_info.items() if k not in ("slot_table", "slot_purity")}))
