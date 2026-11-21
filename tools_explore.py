"""Exploratory condition: with no gate instruction, does the saved code still track the side effect?

    python tools_explore.py runs/NAME [--uninstructed]

Measures, on dev-holdout layouts, how many bits the code state saved after each stage carries about
  gate      the gate state shown at that stage (the side effect so far)
  decor     the decoration shown at that stage (a property that never matters; the yardstick)
A value near 1 bit for the gate means the code separates open from closed.
"""
import json, math, os, sys
from collections import Counter
import torch
from stillway.automaton import pack
from stillway.fixtures import families, layouts_of
from stillway.model import load_checkpoint, stage_argmax
from stillway.vworld import PROFILES, VWorld
from stillway.world import N_STAGES, STAGE_ACTIONS, STAGE_NAMES

run = sys.argv[1].rstrip("/"); ins = "--uninstructed" not in sys.argv
torch.set_num_threads(1)
model = load_checkpoint(os.path.join(run, "checkpoint.pt")); S = model.cfg.n_slots

def mi(a, b):
    n = len(a); ca, cb, cab = Counter(a), Counter(b), Counter(zip(a, b))
    return sum(c / n * math.log2(c * n / (ca[x] * cb[y])) for (x, y), c in cab.items())

gen = torch.Generator().manual_seed(5); n = 20000
w = VWorld(torch.tensor(layouts_of(families("dev"))), n, PROFILES["plain_dynamic"], gen, ins)
ids = torch.full((n, S), -1); out = {"instructed": ins, "stages": {}}; ok = torch.ones(n, dtype=torch.bool)
with torch.no_grad():
    for s in range(N_STAGES):
        obs = w.next_obs()
        logits, ids = model.infer(ids, obs)
        codes = pack(ids.numpy()).tolist()
        out["stages"][STAGE_NAMES[s]] = {"bits_about_gate": round(mi(codes, w.gate.tolist()), 3),
                                         "bits_about_decor_bit": round(mi(codes, (w.decor & 1).tolist()), 3),
                                         "distinct_code_states": len(set(codes))}
        if s in STAGE_ACTIONS:
            a = stage_argmax(logits, s); ok &= w.valid_mask()[torch.arange(n), a]; w.apply(a)
out["all_valid"] = ok.float().mean().item()
json.dump(out, open(os.path.join(run, "explore.json"), "w"), indent=1); print(json.dumps(out))
