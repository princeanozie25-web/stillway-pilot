"""M4: where does the saved state stop being listable?

    python v02/m4_scaling.py runs/v2_iit_s1

Two sweeps on Dispatch-3 development families with the v0.2 core:
  history      K wait slots before every leg (K = 1, 2, 4, 8, 16), every wait slot used, with repaints and
               irrelevant edits (a field re-sent with the value it already has).  Jobs with exactly 3 live obligations.
  obligations  1 to 5 live obligations at the trained history length (K = 1).
For each cell, from N sampled jobs: task success, distinct saved states, distinct meanings (live order
fields per slot), the size and build time of a SAMPLED dictionary, how many of its states stand for two
meanings, and its coverage on N fresh jobs (the share of steps whose state the dictionary knows; the rest
would be abstentions).
"""
import json, os, resource, sys, time
import numpy as np, torch
from stillway2.model3 import load3, act_argmax
from stillway2.world3 import DELIVER, ROUTE, SPECS, World3

run = sys.argv[1].rstrip("/"); name = os.path.basename(run); torch.set_num_threads(int(os.environ.get("THREADS", "2")))
model = load3(os.path.join(run, "checkpoint.pt")); S = model.cfg.n_slots; N = int(os.environ.get("N", "20000"))

def pack(ids):
    out = torch.zeros(len(ids), dtype=torch.long)
    for s in range(ids.shape[1]): out = out * 32 + (ids[:, s] + 1)
    return out

@torch.no_grad()
def sample(spec, n, seed):
    """Run n jobs; return per job: success, live-obligation count, and per slot (state, meaning, active)."""
    gen = torch.Generator().manual_seed(seed); w = World3(n, {**spec, "env": "model"}, gen)
    ids = torch.full((n, S), -1); ok = torch.ones(n, dtype=torch.bool); st, mean, acts = [], [], []
    live0 = (w.q > 0).sum(1) + w.parcel.sum(1)
    for t in range(w.T):
        obs, act = w.next_obs(); kind, leg = w.slot(t)
        logits, new = model.infer(ids, obs); ids = torch.where(act[:, None], new, ids)
        if kind in (ROUTE, DELIVER):
            a = act_argmax(logits, kind); ok &= w.valid_mask()[torch.arange(n), a] | ~act; w.apply(a, act)
        # meaning after this slot: the order fields that can still matter
        gate_live = (w.cur < w.L)[:, None] & (w.q > 0)
        par_live = w.parcel & (w.delivered < 0)
        m = torch.cat([torch.where(gate_live, w.q, torch.zeros_like(w.q)), torch.where(par_live, w.p + 1, torch.zeros_like(w.p))], 1)
        mk = torch.zeros(n, dtype=torch.long)
        for k in range(6): mk = mk * 4 + m[:, k]
        st.append(pack(ids)); mean.append(mk); acts.append(act)
    return ok, live0, torch.stack(st, 1), torch.stack(mean, 1), torch.stack(acts, 1)

def cell(spec, keep=None, seed=0):
    t0 = time.time(); ok, live, st, mean, act = sample(spec, N, 100 + seed)
    sel = torch.ones(N, dtype=torch.bool) if keep is None else keep(live)
    d = {}                                                              # (slot, state) -> set of meanings
    T = st.shape[1]
    for t in range(T):
        m = sel & act[:, t]
        for s_, k_ in zip(st[m, t].tolist(), mean[m, t].tolist()): d.setdefault((t, s_), set()).add(k_)
    build = time.time() - t0
    ok2, live2, st2, mean2, act2 = sample(spec, N, 900 + seed); sel2 = torch.ones(N, dtype=torch.bool) if keep is None else keep(live2)
    steps = known = 0; jobs_all_known = 0
    for i in sel2.nonzero().squeeze(1).tolist():
        allk = True
        for t in act2[i].nonzero().squeeze(1).tolist():
            steps += 1; k = (t, int(st2[i, t])) in d; known += k; allk &= k
        jobs_all_known += allk
    return {"jobs": int(sel.sum()), "slots_in_frame": T, "task_success": float(ok[sel].float().mean()),
            "distinct_states": len({k[1] for k in d}), "dictionary_entries": len(d), "distinct_meanings": len({(k[0], m) for k, v in d.items() for m in v}),
            "ambiguous_entries": sum(1 for v in d.values() if len(v) > 1), "build_seconds": round(build, 1),
            "coverage_of_steps_fresh_jobs": known / max(1, steps), "fresh_jobs_fully_covered": jobs_all_known / max(1, int(sel2.sum())),
            "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6)}

base = {**SPECS["dev"], "rev": 0.0, "gflip": 0.0, "close": 0.0, "msg": 0.0, "full": 0.0}
out = {"run": name, "jobs_sampled_per_cell": N, "history": {}, "obligations": {}}
for K in (1, 2, 4, 8, 16):
    spec = {**base, "K": K, "p_wait": 1.0, "decor": 0.5, "noop_msg": 0.2}
    out["history"][f"K={K}"] = cell(spec, keep=lambda live: live == 3, seed=K); print("history", K, json.dumps(out["history"][f"K={K}"]), flush=True)
for n_ob in (1, 2, 3, 4, 5):
    spec = {**base, "K": 1, "p_wait": 0.5, "decor": 0.2}
    out["obligations"][f"live={n_ob}"] = cell(spec, keep=lambda live, n_ob=n_ob: live == n_ob, seed=50 + n_ob); print("obligations", n_ob, json.dumps(out["obligations"][f"live={n_ob}"]), flush=True)
os.makedirs("results/v02/scaling", exist_ok=True); json.dump(out, open(f"results/v02/scaling/{name}.json", "w"), indent=1)
