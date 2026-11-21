"""Export a checkpoint for the browser demo, plus test vectors to prove the JS engine matches PyTorch.

    python demo/export.py runs/NAME
Writes demo/model.json (weights, base64 float32) and demo/testvec.json.
"""
import base64, json, os, sys
import numpy as np, torch
from stillway.model import load_checkpoint, stage_argmax
from stillway.vworld import PROFILES, VWorld
from stillway.world import ALL_LAYOUTS, N_STAGES, STAGE_ACTIONS

run = sys.argv[1].rstrip("/")
m = load_checkpoint(os.path.join(run, "checkpoint.pt"))
assert m.cfg.reader == "sweep" and m.cfg.effect_embed == "onehot" and m.cfg.quantizer == "vq"
sd = m.state_dict()
def b64(t): return {"shape": list(t.shape), "data": base64.b64encode(t.detach().float().numpy().astype("<f4").tobytes()).decode()}
keys = ["enc_g.0.weight", "enc_g.0.bias", "enc_g.2.weight", "enc_g.2.bias", "enc_leg.0.weight", "enc_leg.0.bias", "enc_leg.2.weight",
        "enc_leg.2.bias", "mem_in.weight", "mem_in.bias", "cell.weight_ih", "cell.weight_hh", "cell.bias_ih", "cell.bias_hh",
        "head.weight", "head.bias", "to_slots.weight", "to_slots.bias", "codebook"]
out = {"cfg": m.cfg.__dict__, "sha256": m.sha256, "run": os.path.basename(run), "active": m.active.int().tolist(),
       "w": {k: b64(sd[k]) for k in keys}}
json.dump(out, open("demo/model.json", "w"))
# test vectors: full closed-loop episodes under heavy events
gen = torch.Generator().manual_seed(99); n = 3000
w = VWorld(torch.tensor(ALL_LAYOUTS), n, PROFILES["stress"], gen)
ids = torch.full((n, m.cfg.n_slots), -1); vec = []
with torch.no_grad():
    for s in range(N_STAGES):
        obs = w.next_obs(); logits, new = m.infer(ids, obs)
        a = stage_argmax(logits, s) if s in STAGE_ACTIONS else torch.full((n,), -1)
        for i in range(n):
            vec.append([ids[i].tolist(), [int(x) for x in obs[i].tolist()], int(a[i]), new[i].tolist()])
        ids = new
        if s in STAGE_ACTIONS: w.apply(a)
json.dump(vec, open("demo/testvec.json", "w"))
print("exported", len(vec), "test steps;", os.path.getsize("demo/model.json") // 1024, "KB")
