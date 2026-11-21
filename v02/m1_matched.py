"""M1: plain memory against quotient memory on the SAME histories.

    python v02/m1_matched.py runs/f_iit_s4 [N_PER_FAMILY=20000]

Counts over two different reachable machines cannot say how many jobs were repaired.  So here each sampled
history is run three times from the same start: plain memory, the original v0.1 maps (unchanged, identity
on an unknown state), and maps rebuilt on the 36-pattern machine.  A history = at every stage one
observation drawn uniformly from the 36-pattern alphabet of its family (the extractor's own distribution;
far harsher than a normal job).  Per job (all four decisions) the three runs are compared:
  repaired     plain memory makes a wrong decision, quotient memory makes none
  broken       plain memory makes none, quotient memory makes one
  tie-break    both make no wrong decision but choose a different valid action somewhere
"""
import glob, json, os, sys, time
import numpy as np, torch
from stillway2.automaton import Alphabet, MSGS36, pack
from stillway.model import load_checkpoint
from stillway.world import ALL_LAYOUTS, STAGE_ACTIONS, N_STAGES, family_of
from stillway.fixtures import SPLIT

run = sys.argv[1].rstrip("/"); name = os.path.basename(run); N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
torch.set_num_threads(int(os.environ.get("THREADS", "4"))); rng = np.random.default_rng(20261121)
model = load_checkpoint(os.path.join(run, "checkpoint.pt")); S = model.cfg.n_slots
old = json.load(open(f"results/v02/maps20/{name}/maps20.json"))
fresh = {}
for p in glob.glob(f"results/v02/expanded/{name}/chunk_*.json"):
    for f, v in json.load(open(p)).items():
        if "fresh_maps" in v: fresh[f] = v["fresh_maps"]

def canon(ids, mp):
    p = pack(ids.numpy()); u, inv = np.unique(p, return_inverse=True)
    hit = np.array([str(int(x)) in mp for x in u]); rep = np.array([int(mp.get(str(int(x)), x)) for x in u], dtype=np.int64)[inv]
    out = np.zeros((len(p), S), dtype=np.int64); x = rep.copy()
    for s in range(S - 1, -1, -1): out[:, s] = x % 64 - 1; x //= 64
    return torch.from_numpy(out), int((~hit)[inv].sum())

tot = {}; t0 = time.time()
def add(split, key, n): tot.setdefault(split, {}).setdefault(key, 0); tot[split][key] += int(n)
for f in sorted(old):
    L = [e for e in ALL_LAYOUTS if family_of(e) == f]; al = Alphabet(L, MSGS36); sp = SPLIT[f]
    ids = {k: torch.full((N, S), -1) for k in ("raw", "old", "fresh")}; order = np.zeros(N, dtype=np.int64)
    ok = {k: np.ones(N, dtype=bool) for k in ids}; same_act = {k: np.ones(N, dtype=bool) for k in ("old", "fresh")}
    miss = {"old": 0, "fresh": 0}
    for s in range(N_STAGES):
        mi = rng.choice(al.full_idx, N) if s == 0 else rng.integers(0, al.M, N); pi = rng.integers(0, al.P, N)
        obs = al.obs(s)[torch.from_numpy(pi * al.M + mi)]
        order = al.msg_order[mi] if s == 0 else al.new_order[order, mi]
        acts = {}
        for k in ids:
            logits, new = model.infer(ids[k], obs)
            if s in STAGE_ACTIONS:
                cols = list(STAGE_ACTIONS[s]); a = np.array(cols)[logits[:, cols].argmax(1).numpy()]; acts[k] = a
                ok[k] &= ((al.valid[s][order, pi] >> a.astype(np.uint8)) & 1).astype(bool)
            if k == "raw": ids[k] = new
            else:
                mp = (old if k == "old" else fresh.get(f, {}))
                ids[k], m_ = canon(new, mp[f][s] if k == "old" else (mp[s] if mp else {})); miss[k] += m_
        if acts:
            for k in same_act: same_act[k] &= acts[k] == acts["raw"]
    add(sp, "jobs", N); add(sp, "plain_jobs_with_a_wrong_decision", (~ok["raw"]).sum())
    for k in ("old", "fresh"):
        add(sp, f"{k}_jobs_with_a_wrong_decision", (~ok[k]).sum()); add(sp, f"{k}_repaired", (~ok["raw"] & ok[k]).sum())
        add(sp, f"{k}_broken", (ok["raw"] & ~ok[k]).sum()); add(sp, f"{k}_tie_break_only", (ok["raw"] & ok[k] & ~same_act[k]).sum())
        add(sp, f"{k}_identical", (ok["raw"] & ok[k] & same_act[k]).sum()); add(sp, f"{k}_still_wrong", (~ok["raw"] & ~ok[k]).sum())
        add(sp, f"{k}_steps_on_unknown_state", miss[k])
tot["all"] = {k: sum(tot[s].get(k, 0) for s in tot) for k in tot["train"]}
out = {"run": name, "histories_per_family": N, "alphabet": "36 patterns, uniform per stage within the family", "seconds": round(time.time() - t0, 1), "by_split": tot}
os.makedirs("results/v02/matched", exist_ok=True); json.dump(out, open(f"results/v02/matched/{name}.json", "w"), indent=1)
print(json.dumps(tot["all"]))
