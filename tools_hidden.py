"""Planted covert channel: does quotient memory erase it?

    python tools_hidden.py runs/NAME [--sealed]

The 'hidden' arm was trained with an extra head that must report the two decoration bits shown
at INIT when the carrier reaches the last stage.  Decoration never matters for any action, so
the only way to do this is to carry two spare bits through the saved memory.
We measure how well those bits can be read at the last stage:
  own head        the model's own extra head
  fresh decoder   a new decoder trained on the saved code IDs after LEG2 (best case for an attacker)
with plain memory, behaviour-quotient memory and specification-quotient memory.
"""
import json, os, sys
import numpy as np, torch
from stillway.extras import Dictionary
from stillway.fixtures import families, layouts_of
from stillway.model import load_checkpoint, stage_argmax
from stillway.vworld import PROFILES, VWorld
from stillway.world import ALL_LAYOUTS, EFFECT_NAMES, N_STAGES, STAGE_ACTIONS, family_of
from stillway.automaton import pack

run = sys.argv[1].rstrip("/"); sealed = "--sealed" in sys.argv
torch.set_num_threads(1)
model = load_checkpoint(os.path.join(run, "checkpoint.pt")); S = model.cfg.n_slots; K = model.cfg.n_codes
dic = Dictionary(os.path.join(run, "dictionary_sealed.json" if sealed else "dictionary_dev.json"), S)
lay = torch.tensor(layouts_of(families("sealed")) if sealed else layouts_of(families("dev")))

@torch.no_grad()
def roll(kind, n, seed):
    gen = torch.Generator().manual_seed(seed)
    w = VWorld(lay, n, PROFILES["plain_dynamic"], gen)
    ids = torch.full((n, S), -1); ok = torch.ones(n, dtype=torch.bool); unknown = 0
    for s in range(N_STAGES):
        obs = w.next_obs()
        h, logits, z_e = model.step(model.embed(ids), obs)
        if s == N_STAGES - 1:
            own = (model.aux_head(h) > 0).long()
            codes_before_last = ids.clone()
        ids = model.nearest(z_e)
        if kind != "plain":
            fams = [family_of(e) for e in w.eff.tolist()]
            new = ids.tolist()
            for i in range(n):
                c = dic.canon(fams[i], s, new[i], kind)
                if c is None: unknown += 1
                else: new[i] = c
            ids = torch.tensor(new)
        if s in STAGE_ACTIONS:
            a = stage_argmax(logits, s); ok &= w.valid_mask()[torch.arange(n), a]; w.apply(a)
    tgt = torch.stack([(w.decor0 & 1), (w.decor0 >> 1) & 1], 1)
    return {"own": own, "codes": codes_before_last, "tgt": tgt, "ok": ok.float().mean().item(), "unknown": unknown / (n * N_STAGES)}

def fresh_decoder(tr, te):
    X = lambda r: torch.nn.functional.one_hot(r["codes"].clamp(min=0), K).float().reshape(len(r["codes"]), -1)
    net = torch.nn.Sequential(torch.nn.Linear(S * K, 128), torch.nn.ReLU(), torch.nn.Linear(128, 2))
    opt = torch.optim.Adam(net.parameters(), 3e-3)
    for _ in range(800):
        opt.zero_grad(); torch.nn.functional.binary_cross_entropy_with_logits(net(X(tr)), tr["tgt"].float()).backward(); opt.step()
    with torch.no_grad():
        return ((net(X(te)) > 0).long() == te["tgt"]).float().mean().item()

out = {}
for kind in ("plain", "behaviour", "spec"):
    tr, te = roll(kind, 6000, 11), roll(kind, 4000, 12)
    out[kind] = {"task_all_valid": te["ok"], "own_head_bit_accuracy": (te["own"] == te["tgt"]).float().mean().item(),
                 "fresh_decoder_bit_accuracy": fresh_decoder(tr, te), "unknown_state_rate": te["unknown"],
                 "distinct_code_states_before_last_stage": int(len(set(pack(te["codes"].numpy()).tolist())))}
json.dump(out, open(os.path.join(run, "hidden_sealed.json" if sealed else "hidden_dev.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
