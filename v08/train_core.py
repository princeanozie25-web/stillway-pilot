"""Train one small core.   python v08/train_core.py MODE SEED OUT.safetensors [--tokens N] [--batch B] [--passes K] [--n N_RECORDS] [--device mps|cpu]

MODE base | exec | shuf | obsonly | reconly (see stillway8/model.py).  base and obsonly read the careful records; the
others read the careful records plus the slipped record of every job on which the teacher slipped.  The initial weights
depend only on SEED, so the arms of a seed start identical."""
import argparse, json, os, sys, time
sys.path.insert(0, ".")
import torch
from stillway8 import expert as E
from stillway8.model import Core, train, save

ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("seed", type=int); ap.add_argument("out"); ap.add_argument("--tokens", type=float, default=80e6); ap.add_argument("--batch", type=int, default=64)
ap.add_argument("--passes", type=int, default=1); ap.add_argument("--n", type=int, default=0); ap.add_argument("--device", default="mps"); ap.add_argument("--ctx", type=int, default=384); ap.add_argument("--lr", type=float, default=2e-3)
ap.add_argument("--data", default="data/v08/pretrain/records.jsonl"); ap.add_argument("--init", default=""); ap.add_argument("--layers", type=int, default=5); ap.add_argument("--d", type=int, default=128)
ap.add_argument("--weight-obs", type=float, default=1.0)
ap.add_argument("--limit-proj", type=int, default=0); ap.add_argument("--limit-tab", type=int, default=0)      # keep only training jobs whose index is below the limit (the limited-experience regime)
a = ap.parse_args(); want_slips = a.mode not in ("base", "obsonly"); keep = lambda r: not (a.limit_proj or a.limit_tab) or r["i"] < (a.limit_proj if r["dom"] == "proj" else a.limit_tab)
jobs = sum(1 for _ in open(a.data)); jobs = min(jobs, a.n) if a.n else jobs
X = torch.zeros(jobs * (2 if want_slips else 1), a.ctx, dtype=torch.int16); K = torch.zeros(X.shape, dtype=torch.uint8); ntok = 0; nact = 0; nobs = 0; cut = 0; i = 0; slipped = 0; wrong = 0; kept = 0
for n, line in enumerate(open(a.data)):
    if n >= jobs: break
    r = json.loads(line)
    if not keep(r): continue
    kept += 1
    for q in [r["clean"]] + ([r["noisy"]] if want_slips and r.get("noisy") and r["noisy"] != r["clean"] else []):
        w = q[0].split(); t = E.ids(w)[:a.ctx]; k = [int(c) for c in q[1]][:a.ctx]; cut += len(w) > a.ctx; X[i, :len(t)] = torch.tensor(t, dtype=torch.int16); K[i, :len(k)] = torch.tensor(k, dtype=torch.uint8)
        ntok += len(t); nact += k.count(1); nobs += k.count(2); wrong += k.count(3); slipped += q is not r["clean"]; i += 1
X = X[:i].clone(); K = K[:i].clone(); rows = range(i)
torch.manual_seed(a.seed); model = Core(len(E.VOCAB), d=a.d, layers=a.layers, ctx=a.ctx, passes=a.passes)
if a.init:
    from safetensors.torch import load_file
    model.load_state_dict(load_file(a.init))
t0 = time.time(); hist, steps, examples = train(model, X, K, int(a.tokens), a.batch, a.lr, a.seed, a.mode, a.device, weight_obs=a.weight_obs, log=lambda h: print(json.dumps(h), flush=True) if h["step"] % 1000 == 1 else None)
peak = torch.mps.driver_allocated_memory() if a.device == "mps" else 0
info = {"mode": a.mode, "seed": a.seed, "token_budget": int(a.tokens), "steps": steps, "examples_drawn": examples, "batch": a.batch, "ctx": a.ctx, "passes": a.passes, "lr": a.lr, "weight_obs": a.weight_obs, "jobs": kept, "limit_proj": a.limit_proj, "limit_tab": a.limit_tab, "records": len(rows), "records_with_a_failure_and_recovery": slipped, "wrong_action_tokens_not_trained": wrong, "record_tokens": ntok, "action_targets_in_data": nact, "observation_targets_in_data": nobs,
        "records_cut_to_context": cut, "tokens_processed": hist[-1]["tokens"], "train_seconds": round(time.time() - t0, 1), "device": a.device, "params": model.n_params(), "mps_driver_bytes": peak, "final": hist[-1], "init": a.init}
save(model.cpu(), a.out, {"train": info}); json.dump({**info, "history": hist}, open(a.out.replace(".safetensors", ".json"), "w"), indent=1); print(json.dumps(info))
