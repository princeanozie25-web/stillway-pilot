"""Text-scratchpad arm for the approvals workflow (v0.4, M2).

    python -m stillway4.scratchpad --size s --seed 1

Memory between steps is a string of 39 tokens in a fixed grammar: for each of the 5 slots
  jurisdiction, level, age, tag, evidence, pinned policy ID, status        (7 tokens)
then the current policy ID of each of the 4 jurisdictions.  At every step a small transformer reads the scratchpad and
the event (9 tokens) and writes the whole new scratchpad; the statuses are read off it.  At test time it reads its
OWN previous scratchpad.

Given by the designer: the grammar.  Teacher labels (charged): the correct scratchpad after every event, 39 tokens
per step, on top of the 5 statuses every arm gets.  Learned: reading and rewriting.
"""
import argparse, json, os, time
import torch, torch.nn as nn, torch.nn.functional as F
from . import approvals as A
from .arms import make_data, save, sub

S, NJ, T = A.S, A.NJ, A.T; NPID = 64
# token ranges in one vocabulary: field -> (offset, size); value -1 maps to index 0 of its range
RANGES = {"jur": NJ + 1, "lvl": 4, "age": 2, "tag": 3, "evid": 2, "pid": NPID + 1, "stat": 4, "kind": A.NK, "slot": S + 1, "elvl": 4, "eage": 3, "etag": 4, "eevid": 3, "ostat": 5}
OFF = {}; _o = 0
for k_, n_ in RANGES.items(): OFF[k_] = _o; _o += n_
VOCAB = _o; MEM = 7 * S + NJ; EVT = 9; WIDTH = {"s": 64, "m": 128, "l": 224}


def mem_tokens(jur, facts, pin, stat, pj):
    """(.., S), (.., S, 4), (.., S), (.., S), (.., NJ) -> (.., 39) token ids."""
    per = torch.stack([OFF["jur"] + jur + 1, OFF["lvl"] + facts[..., 0], OFF["age"] + facts[..., 1], OFF["tag"] + facts[..., 2], OFF["evid"] + facts[..., 3], OFF["pid"] + pin + 1, OFF["stat"] + stat], -1)
    return torch.cat([per.flatten(-2), OFF["pid"] + pj + 1], -1)


def event_tokens(d, t):
    g = lambda f: d["ev_" + f][:, t]
    return torch.stack([OFF["kind"] + g("kind"), OFF["slot"] + g("slot") + 1, OFF["jur"] + g("jur") + 1, OFF["elvl"] + g("lvl").clamp(min=0), OFF["eage"] + g("age") + 1, OFF["etag"] + g("tag") + 1,
                        OFF["eevid"] + g("evid") + 1, OFF["pid"] + g("pid") + 1, OFF["ostat"] + g("ostat") + 1], 1)


class Scratch(nn.Module):
    def __init__(self, width=64, layers=2):
        super().__init__(); self.width = width; self.emb = nn.Embedding(VOCAB, width); self.pos = nn.Parameter(torch.randn(MEM + EVT, width) * 0.02)
        self.enc = nn.TransformerEncoder(nn.TransformerEncoderLayer(width, 4, 4 * width, dropout=0.0, batch_first=True), layers); self.out = nn.Linear(width, VOCAB)

    def forward(self, mem, ev): return self.out(self.enc(self.emb(torch.cat([mem, ev], 1)) + self.pos)[:, :MEM])      # (B, 39, VOCAB)

    def active_params(self): return sum(p.numel() for p in self.parameters()) - self.emb.weight.numel() + (MEM + EVT) * self.width

    def macs_per_step(self):
        w, n = self.width, MEM + EVT; return len(self.enc.layers) * n * (4 * w * w + 2 * w * 4 * w) + MEM * w * VOCAB


def empty_mem(B):
    z = torch.zeros(B, S, dtype=torch.long); return mem_tokens(z - 1, torch.zeros(B, S, 4, dtype=torch.long), z - 1, z, torch.zeros(B, NJ, dtype=torch.long) - 1)


@torch.no_grad()
def evaluate(model, d, batch=500):
    model.eval(); outs = []
    for i in range(0, len(d["tenant"]), batch):
        x = sub(d, slice(i, i + batch)); mem = empty_mem(len(x["tenant"])); st = []
        for t in range(T):
            mem = model(mem, event_tokens(x, t)).argmax(-1); st.append((mem[:, 6:7 * S:7] - OFF["stat"]).clamp(0, 3))
        outs.append(torch.stack(st, 1))
    st = torch.cat(outs); ok = st == d["labels"]; prev = torch.cat([torch.zeros_like(st[:, :1]), st[:, :-1]], 1)
    return {"success": ok.flatten(1).all(1).float().mean().item(), "status_accuracy": ok.float().mean().item(), "protected_changed": int(((st != prev) & ~d["affected"]).sum()), "slots_recomputed_per_event": None, "outputs": st}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--size", default="s"); ap.add_argument("--seed", type=int, default=1); ap.add_argument("--steps", type=int, default=12000)
    ap.add_argument("--budget", type=float, default=3600.0); ap.add_argument("--salt", type=int, default=0); ap.add_argument("--name", default=""); a = ap.parse_args()
    torch.set_num_threads(1); name = a.name or f"v4a_text_{a.size}_s{a.seed}"; out = f"runs/{name}"; os.makedirs(out, exist_ok=True); uni, data = make_data(a.seed, salt=a.salt)
    torch.manual_seed(a.seed); gen = torch.Generator().manual_seed(a.seed); model = Scratch(WIDTH[a.size]); opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.0); tr = data["train"]; N = len(tr["tenant"])
    target = mem_tokens(tr["jur"], tr["facts"], tr["pin"], tr["labels"], tr["pj"]); prev = torch.cat([empty_mem(N)[:, None], target[:, :-1]], 1); log = []; t0 = time.time(); it = 0
    for it in range(1, a.steps + 1):
        if time.time() - t0 > a.budget: break
        model.train(); i = torch.randint(0, N, (256,), generator=gen); t = int(torch.randint(0, T, (1,), generator=gen)); x = sub(tr, i)
        for g_ in opt.param_groups: g_["lr"] = 1e-3 * (0.1 + 0.9 * min(1.0, (a.steps - it) / (0.5 * a.steps)))
        loss = F.cross_entropy(model(prev[i, t], event_tokens(x, t)).reshape(-1, VOCAB), target[i, t].reshape(-1))
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        if it % 1000 == 0 or it == a.steps:
            e = evaluate(model, sub(data["dev"], slice(0, 1000))); log.append({"step": it, "loss": round(loss.item(), 4), "dev_success": round(e["success"], 4), "dev_status_accuracy": round(e["status_accuracy"], 5), "sec": round(time.time() - t0, 1)}); print(json.dumps(log[-1]), flush=True)
    model.eval(); buf_sha = save_model(model, f"{out}/checkpoint.pt")
    res = {"name": name, "args": vars(a), "arm": "text", "width": model.width, "checkpoint_sha256": buf_sha, "active_parameters_per_decision": model.active_params(), "resident_parameters": sum(p.numel() for p in model.parameters()),
           "multiply_accumulates_per_step": model.macs_per_step(), "train_steps": it, "train_seconds": round(time.time() - t0, 1), "status": "complete" if it >= a.steps else "incomplete: budget", "log": log,
           "training_information": "the same 20,000 logged documents, plus teacher labels: the correct 39-token scratchpad after every event (20,000 x 19 x 39 tokens)", "teacher_label_tokens": N * T * MEM}
    raw = {}
    for k in ("dev", "test_iid", "test_novel"):
        e = evaluate(model, data[k]); res[k] = {x: e[x] for x in ("success", "status_accuracy", "protected_changed", "slots_recomputed_per_event")}; raw[k] = e["outputs"]
        ok = (e["outputs"] == data[k]["labels"]).flatten(1).all(1)
        res[k]["by_family"] = {int(f): [int(((data[k]["family"] == f) & ok).sum()), int((data[k]["family"] == f).sum())] for f in data[k]["family"].unique().tolist()}
    from .arms import save_raw; save_raw(f"{out}/raw_outputs.npz", uni, data, {k: raw[k] for k in ("test_iid", "test_novel")})
    json.dump(res, open(f"{out}/manifest.json", "w"), indent=1); print("saved", out, {k: round(res[k]["success"], 4) for k in ("dev", "test_iid", "test_novel")}, "active params", res["active_parameters_per_decision"], flush=True)


def save_model(model, path):
    import hashlib, io
    buf = io.BytesIO(); torch.save({"width": model.width, "state": model.state_dict()}, buf); data = buf.getvalue(); open(path, "wb").write(data); return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    main()
