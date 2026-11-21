"""M4: a SAMPLED dictionary against exact enumeration, where both finish (Dispatch-2, v0.1 seed 4, 20 patterns).

    python v02/m4_sampled_vs_exact.py runs/f_iit_s4

For 12 families: the exact reachable set and meanings come from the v0.1 extractor.  A sampled dictionary is
built from N histories drawn from the same alphabet (N = 300, 3,000, 30,000).  Reported per N:
  share of the exact reachable states that the sample found,
  sampled states whose meaning disagrees with the exact one, or that look unambiguous but are not,
  on 5,000 fresh histories: the share of steps whose state the sampled dictionary knows (the rest = abstain).
"""
import json, os, sys, time
import numpy as np, torch
from stillway.automaton import Alphabet, Machine, pack, relevant_key
from stillway.model import load_checkpoint
from stillway.world import ALL_LAYOUTS, ALL_ORDERS, N_STAGES, family_of

run = sys.argv[1].rstrip("/"); torch.set_num_threads(2); model = load_checkpoint(os.path.join(run, "checkpoint.pt")); S = model.cfg.n_slots
FAMS = ["KT-KT", "KO-KO", "TT-TT", "CC-CC", "KC-KT", "OC-TO", "KK-KO", "TC-OC", "KT-OC", "TO-TO", "KO-TC", "CC-KT"]; rng = np.random.default_rng(1)

@torch.no_grad()
def sample(al, n):
    ids = torch.full((n, S), -1); order = np.zeros(n, dtype=np.int64); out = []
    for s in range(N_STAGES):
        mi = rng.choice([i for i in range(al.M) if al.msg_order[i] >= 0], n) if s == 0 else rng.integers(0, al.M, n); pi = rng.integers(0, al.P, n)
        order = al.msg_order[mi] if s == 0 else al.new_order[order, mi]
        _, ids = model.infer(ids, al.obs(s)[torch.from_numpy(pi * al.M + mi)])
        out.append((pack(ids.numpy()), order.copy()))
    return out

res = {N: {"exact_states": 0, "found": 0, "meaning_disagreements": 0, "false_unambiguous": 0, "fresh_steps": 0, "fresh_known": 0, "seconds": 0.0} for N in (300, 3000, 30000)}
exact_seconds = 0.0
for f in FAMS:
    L = [e for e in ALL_LAYOUTS if family_of(e) == f]; t0 = time.time(); m = Machine(model, L); exact_seconds += time.time() - t0; al = Alphabet(L)
    exact = []
    for s in range(N_STAGES):
        sc = m.spec_classes(s); exact.append({int(c): sc[i] for i, c in enumerate(m.stage_codes[s])})
    fresh = sample(al, 5000)
    for N in res:
        t0 = time.time(); smp = sample(al, N); d = [dict() for _ in range(N_STAGES)]
        for s in range(N_STAGES):
            for c, o in zip(smp[s][0].tolist(), smp[s][1].tolist()): d[s].setdefault(c, set()).add(relevant_key(s, ALL_ORDERS[o]))
        r = res[N]; r["seconds"] += time.time() - t0
        for s in range(N_STAGES):
            r["exact_states"] += len(exact[s]); r["found"] += len(d[s])
            for c, ms in d[s].items():
                ex = exact[s].get(c)
                if ex is None: r["meaning_disagreements"] += 1                      # a state the exact run never reached: must not happen
                elif ex == "AMBIGUOUS": r["false_unambiguous"] += int(len(ms) == 1)
                elif ms != {ex}: r["meaning_disagreements"] += 1
            r["fresh_steps"] += len(fresh[s][0]); r["fresh_known"] += sum(c in d[s] for c in fresh[s][0].tolist())
out = {"run": os.path.basename(run), "families": FAMS, "exact_enumeration_seconds": round(exact_seconds, 1),
       "sampled": {str(N): {**r, "share_of_exact_states_found": r["found"] / r["exact_states"], "fresh_step_coverage": r["fresh_known"] / r["fresh_steps"], "seconds": round(r["seconds"], 1)} for N, r in res.items()}}
os.makedirs("results/v02/scaling", exist_ok=True); json.dump(out, open("results/v02/scaling/sampled_vs_exact_d2.json", "w"), indent=1); print(json.dumps(out["sampled"], indent=1))
