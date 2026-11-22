"""Train one small core.   python v08/train_core.py MODE SEED OUT.safetensors [--steps N] [--batch B] [--passes K] [--n N_RECORDS] [--device mps|cpu]

MODE base | exec | shuf (see stillway8/model.py).  base reads the careful records; exec and shuf read the records with
slips and recoveries.  The initial weights depend only on SEED, so the arms of a seed start identical."""
import argparse, json, os, sys, time
sys.path.insert(0, ".")
import torch
from stillway8 import expert as E
from stillway8.model import Core, train, save

ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("seed", type=int); ap.add_argument("out"); ap.add_argument("--steps", type=int, default=6000); ap.add_argument("--batch", type=int, default=64)
ap.add_argument("--passes", type=int, default=1); ap.add_argument("--n", type=int, default=0); ap.add_argument("--device", default="mps"); ap.add_argument("--ctx", type=int, default=320); ap.add_argument("--lr", type=float, default=2e-3)
ap.add_argument("--data", default="data/v08/pretrain/records.jsonl"); ap.add_argument("--init", default=""); ap.add_argument("--layers", type=int, default=5); ap.add_argument("--d", type=int, default=128)
a = ap.parse_args(); field = "clean" if a.mode == "base" else "noisy"
rows = [json.loads(l) for l in open(a.data)]; rows = rows[:a.n] if a.n else rows
X = torch.zeros(len(rows), a.ctx, dtype=torch.long); K = torch.zeros(len(rows), a.ctx, dtype=torch.long); ntok = 0; nact = 0; nobs = 0; cut = 0
for i, r in enumerate(rows):
    t = E.ids(r[field][0].split())[:a.ctx]; k = [int(c) for c in r[field][1]][:a.ctx]; cut += len(r[field][0].split()) > a.ctx
    X[i, :len(t)] = torch.tensor(t); K[i, :len(k)] = torch.tensor(k); ntok += len(t); nact += k.count(1); nobs += k.count(2)
torch.manual_seed(a.seed); model = Core(len(E.VOCAB), d=a.d, layers=a.layers, ctx=a.ctx, passes=a.passes)
if a.init:
    from safetensors.torch import load_file
    model.load_state_dict(load_file(a.init))
t0 = time.time(); hist = train(model, X, K, a.steps, a.batch, a.lr, a.seed, a.mode, a.device, log=lambda h: print(json.dumps(h), flush=True) if h["step"] % 500 == 0 or h["step"] == a.steps - 1 else None)
peak = torch.mps.driver_allocated_memory() if a.device == "mps" else 0
info = {"mode": a.mode, "seed": a.seed, "steps": a.steps, "batch": a.batch, "ctx": a.ctx, "passes": a.passes, "lr": a.lr, "records": len(rows), "record_tokens": ntok, "action_targets_in_data": nact, "observation_targets_in_data": nobs,
        "records_cut_to_context": cut, "tokens_processed": a.steps * a.batch * (a.ctx - 1) * a.passes, "train_seconds": round(time.time() - t0, 1), "device": a.device, "params": model.n_params(), "mps_driver_bytes": peak, "final": hist[-1], "init": a.init}
save(model.cpu(), a.out, {"train": info}); json.dump({**info, "history": hist}, open(a.out.replace(".safetensors", ".json"), "w"), indent=1); print(json.dumps(info))
