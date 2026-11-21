"""v0.3 arm M: the v0.2 core, unchanged, with ONE extra training rule (restart consistency).

    python v03/train_m.py --name v3m_s1 --iit 1.0 --seed 1 --cons 1.0

Rule.  After every step, the saved state must equal the state a restart would write: memory wiped, the whole
current order of record shown, in the surroundings (stage, layout, gates, bay, paint) of ANOTHER job.
The rule uses no label for the memory.  It needs only what a restart needs: the order of record.
Both directions are trained (the running state towards the restart's codes, and the restart towards the
running state's codes).  The rule's weight rises from 0 to --cons over --cons-ramp steps, starting --cons-delay
steps after the quantiser is switched on (at full weight from the first step it broke the planner: first try,
21 Nov, all three seeds fell to 50-64% and were stopped).  Architecture, data, schedule and every other loss are those of stillway2/train3.py.
No frozen file is changed.
"""
from __future__ import annotations

import argparse, json, os, sys, time

import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway2 import train3
from stillway2.model3 import Config3, Core3, save3
from stillway2.train3 import batch_eval3, set_ce
from stillway2.world3 import DELIVER, NF, ROUTE, SPECS, World3

CONS_W = 0.0


def code_logits(model, z):
    cb = model.codebook.detach().clone()                         # the quantiser updates the codebook in place
    return -(z.pow(2).sum(-1, keepdim=True) - 2 * torch.einsum("bsd,skd->bsk", z, cb) + cb.pow(2).sum(-1)[None])


def restart_obs(obs, vals, gen):
    """obs (n,92) of n jobs, vals (n,6) their orders -> the obs of other jobs with the full order of these shown."""
    n = obs.shape[0]; o = obs[torch.randperm(n, generator=gen)].clone(); ar = torch.arange(n)
    o[:, 16:16 + 4 * NF] = 0.0
    for k in range(NF):
        o[:, 16 + 4 * k] = 1.0; o[ar, 16 + 4 * k + 1 + vals[:, k]] = 1.0
    return o


def advance(model, w, mem, quant, t0, t1):
    loss = torch.zeros(()); commit = torch.zeros(()); aux = torch.zeros(()); zs = []
    S, D = model.cfg.n_slots, model.cfg.code_dim
    for t in range(t0, t1):
        obs, act = w.next_obs(); kind, _ = w.slot(t)
        if not act.any(): continue
        idx = act.nonzero().squeeze(1)
        h, logits, z_e = model.step(mem[idx], obs[idx])
        if model.leg_h:
            dp = w.dp_tables()[idx]
            for (i, hi, m) in model.leg_h:
                if m.any(): aux = aux + train3.DP_W * F.cross_entropy(model.dp_head(hi[m]).view(-1, 3), dp[m, i].reshape(-1)) / max(1, len(model.leg_h))
        if kind in (ROUTE, DELIVER):
            valid = w.valid_mask(); loss = loss + set_ce(logits, valid[idx], w.stage_mask(), torch.ones(len(idx)))
            if kind == ROUTE:
                aux = aux + train3.VALUE_W * F.cross_entropy(model.value_head(h).view(-1, 3), w.best_counts()[idx].clamp(min=0).reshape(-1))
            w.apply(w.env_action(valid), act)
        zs.append(z_e.detach())
        if quant and CONS_W > 0 and len(idx) > 1:
            vals = torch.cat([w.q, w.p], 1)[idx]
            _, _, z_r = model.step(torch.zeros(len(idx), S * D), restart_obs(obs[idx], vals, w.gen))
            le, lr = code_logits(model, z_e), code_logits(model, z_r)
            aux = aux + CONS_W * (F.cross_entropy(le.reshape(-1, le.shape[-1]), lr.argmax(-1).reshape(-1).detach())
                                  + F.cross_entropy(lr.reshape(-1, lr.shape[-1]), le.argmax(-1).reshape(-1).detach()))
        if quant:
            _, st, c = model.quantize_train(z_e); commit = commit + c
        else:
            st = z_e.reshape(len(idx), -1)
        mem = mem.index_copy(0, idx, st)
    return loss, commit, mem, zs, aux


def main():
    global CONS_W
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True); ap.add_argument("--iit", type=float, default=1.0); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cons", type=float, default=1.0); ap.add_argument("--batch", type=int, default=512); ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--warmup", type=int, default=30000); ap.add_argument("--min-warmup", type=int, default=3000)
    ap.add_argument("--switch-loss", type=float, default=0.04); ap.add_argument("--post", type=int, default=12000)
    ap.add_argument("--cons-delay", type=int, default=1000); ap.add_argument("--cons-ramp", type=int, default=3000)
    a = ap.parse_args(); CONS_W = 0.0
    train3.advance = advance                                     # rollout_loss in train3 calls the module-level advance
    torch.set_num_threads(1); torch.manual_seed(a.seed); gen = torch.Generator().manual_seed(a.seed)
    cfg = Config3(); model = Core3(cfg); opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.0)
    out = os.path.join("runs", a.name); os.makedirs(out, exist_ok=True)
    profs = ["train", "train_stress"]; it, switch, ema, log, t0 = 0, None, 1.0, [], time.time()
    while True:
        it += 1; model.train(); w = World3(a.batch, SPECS[profs[it % 2]], gen); phase2 = switch is not None
        # the rule is switched on gradually, after the quantiser has settled
        CONS_W = a.cons * min(1.0, max(0.0, (it - switch - a.cons_delay) / a.cons_ramp)) if phase2 else 0.0
        loss, commit, iit_loss, zs = train3.rollout_loss(model, w, phase2, a.iit if phase2 else 0.0)
        ema = 0.98 * ema + 0.02 * loss.item()
        if switch is None and ((it >= a.min_warmup and ema < a.switch_loss) or it >= a.warmup):
            switch = it; model.init_codebook(zs.reshape(-1, cfg.n_slots, cfg.code_dim))
        total = loss + cfg.beta * commit + iit_loss
        opt.zero_grad(); total.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        last = switch is not None and it >= switch + a.post
        if it % 500 == 0 or last:
            c = not phase2
            row = {"step": it, "phase": 2 if phase2 else 1, "loss": round(loss.item(), 4), "ema": round(ema, 4), "aux": round(float(iit_loss), 4), "cons_w": round(CONS_W, 3),
                   "sec": round(time.time() - t0, 1), "train": batch_eval3(model, SPECS["train"], 1500, 7, c),
                   "dev": batch_eval3(model, SPECS["dev"], 1500, 9, c), "dev_plain": batch_eval3(model, SPECS["dev_plain"], 1500, 10, c)}
            log.append(row); print(json.dumps(row), flush=True)
        if last: break
    model.eval(); sha = save3(model, os.path.join(out, "checkpoint.pt"), {"args": vars(a)})
    json.dump({"name": a.name, "args": vars(a), "config": cfg.__dict__, "checkpoint_sha256": sha, "parameters": model.n_params(), "gradient_steps": it,
               "phase2_started_at_step": switch, "wall_seconds": round(time.time() - t0, 1), "arm": "M: v0.2 core + restart consistency",
               "supervision": "as v0.2 (valid action sets, value head, sweep head, interchange training) plus restart consistency (weight %.2f); no label for the memory" % a.cons,
               "torch": torch.__version__, "log": log}, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    print("saved", out, sha)


if __name__ == "__main__":
    main()
