"""EXPLORATORY (after the freeze): a v0.2 core with CANONICAL memory.

    python v02/x_canonical.py --name v2x_canon_s1 --seed 1

Memory = 6 slots, one per order field, and a FIXED code table: slot f holds code v exactly when field f has
value v.  The code a step writes is supervised with the current order (a label the simulator has), so there
are no synonyms and no spare slots: at most 3^6 = 729 saved states exist, one per order.  Everything else
is the v0.2 core and training world.  Question: is accuracy kept, and is the saved state then listable?
No frozen file is changed.
"""
import argparse, json, os, time
import torch, torch.nn.functional as F
from stillway2.model3 import Config3, Core3, save3
from stillway2.train3 import DP_W, VALUE_W, batch_eval3, set_ce
from stillway2.world3 import DELIVER, ROUTE, SPECS, World3

ap = argparse.ArgumentParser(); ap.add_argument("--name", required=True); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--steps", type=int, default=9000); ap.add_argument("--batch", type=int, default=512); a = ap.parse_args()
torch.set_num_threads(1); torch.manual_seed(a.seed); gen = torch.Generator().manual_seed(a.seed)
cfg = Config3(n_slots=6, n_codes=4, code_dim=16); model = Core3(cfg)
with torch.no_grad():                                           # fixed, well separated codes; never updated
    cb = torch.randn(6, 4, 16); cb = cb / cb.norm(dim=-1, keepdim=True) * 2.0
    model.codebook.copy_(cb); model.active[:, 3] = False; model.quant_on.fill_(1)
opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.0); out = os.path.join("runs", a.name); os.makedirs(out, exist_ok=True)
profs = ["train", "train_stress"]; log = []; t0 = time.time(); S, D = 6, 16
for it in range(1, a.steps + 1):
    model.train(); w = World3(a.batch, SPECS[profs[it % 2]], gen); B = w.B
    mem = torch.zeros(B, S * D); loss = torch.zeros(()); mloss = torch.zeros(()); aux = torch.zeros(())
    own = float(min(1.0, it / 3000.0)) * 0.5                     # share of jobs that carry their OWN written codes forward
    for t in range(w.T):
        obs, act = w.next_obs(); kind, _ = w.slot(t)
        if not act.any(): continue
        idx = act.nonzero().squeeze(1); h, logits, z_e = model.step(mem[idx], obs[idx])
        dp = w.dp_tables()[idx]
        for (i, hi, m) in model.leg_h:
            if m.any(): aux = aux + DP_W * F.cross_entropy(model.dp_head(hi[m]).view(-1, 3), dp[m, i].reshape(-1)) / max(1, len(model.leg_h))
        if kind in (ROUTE, DELIVER):
            valid = w.valid_mask(); loss = loss + set_ce(logits, valid[idx], w.stage_mask(), torch.ones(len(idx)))
            if kind == ROUTE: aux = aux + VALUE_W * F.cross_entropy(model.value_head(h).view(-1, 3), w.best_counts()[idx].clamp(min=0).reshape(-1))
            w.apply(w.env_action(valid), act)
        vals = torch.cat([w.q, w.p], 1)[idx]                     # the order of record after this step
        dist = (z_e.pow(2).sum(-1, keepdim=True) - 2 * torch.einsum("bsd,skd->bsk", z_e, model.codebook) + model.codebook.pow(2).sum(-1)[None])
        mloss = mloss + F.cross_entropy((-dist[:, :, :3]).reshape(-1, 3), vals.reshape(-1))
        true_mem = model.codebook[torch.arange(S)[None, :], vals].reshape(len(idx), -1)
        own_mem = model.codebook[torch.arange(S)[None, :], dist[:, :, :3].argmin(-1)].reshape(len(idx), -1)
        use_own = (torch.rand(len(idx), generator=gen) < own)[:, None]
        mem = mem.index_copy(0, idx, torch.where(use_own, own_mem, true_mem).detach())
    total = loss + mloss + aux; opt.zero_grad(); total.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
    if it % 500 == 0 or it == a.steps:
        row = {"step": it, "loss": round(loss.item(), 4), "mem_loss": round(mloss.item(), 4), "sec": round(time.time() - t0, 1),
               "train": batch_eval3(model, SPECS["train"], 1500, 7), "dev": batch_eval3(model, SPECS["dev"], 1500, 9), "dev_plain": batch_eval3(model, SPECS["dev_plain"], 1500, 10)}
        log.append(row); print(json.dumps(row), flush=True)
model.eval(); sha = save3(model, os.path.join(out, "checkpoint.pt"), {"args": vars(a)})
json.dump({"name": a.name, "args": {**vars(a), "iit": 1.0}, "config": cfg.__dict__, "checkpoint_sha256": sha, "parameters": model.n_params(), "gradient_steps": a.steps,
           "wall_seconds": round(time.time() - t0, 1), "exploratory": True, "supervision": "valid action sets, value head, sweep head, AND the code each slot must hold (the order of record)", "log": log},
          open(os.path.join(out, "manifest.json"), "w"), indent=1); print("saved", out)
