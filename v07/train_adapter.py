"""Train one adapter.   python v07/train_adapter.py DATASET SEED [UPDATES] [TOKENS_PER_UPDATE]
Every arm gets the same number of optimiser updates and the same token budget per update (examples are added to a batch until the
budget is reached), so updates and training tokens are matched across arms.  Writes artifacts/v07/adapters/<dataset>_s<seed>.safetensors."""
import json, math, os, random, sys, time
import torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import episode as E
from stillway7.student import Student
name, seed = sys.argv[1], int(sys.argv[2]); U = int(sys.argv[3]) if len(sys.argv) > 3 else 300; T = int(sys.argv[4]) if len(sys.argv) > 4 else 4096; LR = 2e-4; WARM = 10
rows = [json.loads(l) for l in open(f"data/v07/training/{name}.jsonl")]; rng = random.Random(seed); torch.manual_seed(seed)
s = Student(); s.add_adapter(r=16, alpha=32, seed=seed); params = s.adapter_params()
for p in params: p.requires_grad_(True)
opt = torch.optim.AdamW(params, lr=LR, weight_decay=0.0); s.model.train(); queue = []; log = []; t0 = time.time(); tokens = 0; seen = 0; passes = 0
def batch():
    global queue, passes
    out = []; n = 0
    while True:
        if not queue: queue = rows[:]; rng.shuffle(queue); passes += 1
        if out and n + queue[-1]["tokens"] > T: return out
        r = queue.pop(); out.append(r); n += r["tokens"]
for u in range(U):
    for g in opt.param_groups: g["lr"] = LR * min(1.0, (u + 1) / WARM) * (0.5 * (1 + math.cos(math.pi * u / U)))
    b = batch(); loss, n = s.loss([s.chat(E.SYSTEM, r["user"]) for r in b], [r["target"] for r in b]); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(params, 1.0); opt.step()
    tokens += sum(r["tokens"] for r in b); seen += len(b); log.append(round(float(loss), 4))
    if u % 20 == 0 or u == U - 1: print(name, seed, "update", u, "loss", log[-1], "examples", seen, "tokens", tokens, round(time.time() - t0), "s", flush=True)
os.makedirs("artifacts/v07/adapters", exist_ok=True); path = f"artifacts/v07/adapters/{name}_s{seed}.safetensors"
meta = {"dataset": name, "updates": U, "token_budget_per_update": T, "training_tokens": tokens, "examples_seen": seen, "passes_started": passes, "learning_rate": LR, "method": "low-rank adapters (rank 16) on all attention and MLP projections; AdamW; base frozen", "seconds": round(time.time() - t0, 1)}
h = s.save_adapter(path, meta); json.dump(dict(meta, seed=seed, sha256=h, loss_first10=log[:10], loss_last10=log[-10:], loss_curve=log), open(path.replace(".safetensors", ".json"), "w")); print("saved", path, h[:16], meta)
