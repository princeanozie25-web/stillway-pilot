"""Train a v0.3 core (typed registers + discrete-carry reader) by imitation of the exact planner.

    python -m stillway3.train --name v3r23_s1 --data t23 --seed 1            # the v0.2 training distribution
    python -m stillway3.train --name v3r24_s1 --data t24x --seed 1           # 2-4 legs, cross-gate legs allowed
    options:  --carry cont   (ablation: free vector carried from leg to leg)
              --aid 0        (ablation: no value-table aid; valid action sets only)

Two phases as before: continuous carry until the task loss is low, then the codebook is fitted to the carries
seen and the carry is snapped to a code for --post more steps.  Training families only.
"""
from __future__ import annotations

import argparse, json, os, time

import torch
import torch.nn.functional as F

from stillway2.train3 import set_ce
from stillway2.world3 import DELIVER, ROUTE
from .model import RegConfig, RegCore, save_reg
from .world import SPECS, WorldN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rollout(model, w, aid):
    B = w.B; ids = torch.full((B, w.NF), -1); loss = torch.zeros(()); aux = torch.zeros(()); commit = torch.zeros(()); zs = []; labs = []
    for t in range(w.T):
        obs, act = w.next_obs(); kind, _ = w.slot(t)
        ids = torch.where(act[:, None], model.write(ids, obs), ids)
        if kind not in (ROUTE, DELIVER) or not act.any(): continue
        idx = act.nonzero().squeeze(1)
        logits, ax, cm = model.heads(ids[idx], obs[idx], want_aux=True); commit = commit + cm
        valid = w.valid_mask(); loss = loss + set_ce(logits, valid[idx], w.stage_mask(), torch.ones(len(idx)))
        if kind == ROUTE:
            dp = w.dp_tables()[idx]
            for (j, c, m) in ax:
                if not m.any(): continue
                zs.append(c[m].detach())
                with torch.no_grad(): labs.append((model.dp_head(c[m]).view(-1, 4, 3).argmax(-1) * torch.tensor([27, 9, 3, 1])).sum(1))
                if aid > 0: aux = aux + aid * F.cross_entropy(model.dp_head(c[m]).view(-1, 3), dp[m, j].reshape(-1))
        w.apply(w.env_action(valid), act)
    return loss, aux, commit, zs, labs


@torch.no_grad()
def batch_eval(model, spec, n, seed, lmax=4):
    """Closed loop with the model's own actions.  Returns (share of jobs with every action valid, share of valid actions)."""
    from stillway2.model3 import act_argmax
    model.eval(); w = WorldN(n, {**spec, "env": "model"}, torch.Generator().manual_seed(seed), lmax=lmax)
    ids = torch.full((n, w.NF), -1); ok = torch.ones(n, dtype=torch.bool); good = tot = 0
    for t in range(w.T):
        obs, act = w.next_obs(); kind, _ = w.slot(t)
        logits, new = model.infer(ids, obs); ids = torch.where(act[:, None], new, ids)
        if kind in (ROUTE, DELIVER):
            a = act_argmax(logits, kind); v = w.valid_mask()[torch.arange(n), a]
            ok &= v | ~act; good += int((v & act).sum()); tot += int(act.sum()); w.apply(a, act)
    return ok.float().mean().item(), good / max(1, tot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True); ap.add_argument("--data", default="t23"); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--carry", default="vq"); ap.add_argument("--aid", type=float, default=1.0); ap.add_argument("--n-codes", type=int, default=64); ap.add_argument("--init", default="table")
    ap.add_argument("--batch", type=int, default=512); ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--warmup", type=int, default=12000); ap.add_argument("--min-warmup", type=int, default=1500)
    ap.add_argument("--switch-loss", type=float, default=0.01); ap.add_argument("--post", type=int, default=3000)
    a = ap.parse_args()
    if a.aid <= 0: a.init = "kmeans"                               # without the aid there is no table to read off a carry
    torch.set_num_threads(1); torch.manual_seed(a.seed); gen = torch.Generator().manual_seed(a.seed)
    cfg = RegConfig(carry=a.carry, n_codes=a.n_codes); model = RegCore(cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.0)
    out = os.path.join(ROOT, "runs", a.name); os.makedirs(out, exist_ok=True)
    profs = [a.data, a.data + "_stress"]; dev = {"t23": "dev23", "t24x": "dev24x"}[a.data]
    it, switch, ema, log, t0, recent = 0, None, 1.0, [], time.time(), []
    while True:
        it += 1; model.train(); w = WorldN(a.batch, SPECS[profs[it % 2]], gen, lmax=4)
        loss, aux, commit, zs, labs = rollout(model, w, a.aid)
        ema = 0.98 * ema + 0.02 * loss.item(); recent = (recent + [(torch.cat(zs), torch.cat(labs))])[-8:]
        total = loss + aux + cfg.beta * commit
        opt.zero_grad(); total.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        if switch is None and ((it >= a.min_warmup and ema < a.switch_loss) or it >= a.warmup):
            switch = it
            if a.carry == "vq":
                model.init_codebook(torch.cat([r[0] for r in recent]), gen, labels=torch.cat([r[1] for r in recent]) if a.init == "table" else None)
        last = switch is not None and it >= switch + a.post
        if it % 500 == 0 or last:
            row = {"step": it, "phase": 1 if switch is None or it == switch else 2, "loss": round(float(loss), 5), "ema": round(ema, 5), "aux": round(float(aux), 4),
                   "commit": round(float(commit), 5), "sec": round(time.time() - t0, 1),
                   "train": batch_eval(model, SPECS[a.data], 2000, 7)[0], "dev": batch_eval(model, SPECS[dev], 2000, 9)[0],
                   "dev_5to6_legs": batch_eval(model, {**SPECS[dev], "L": (5, 6)}, 1000, 11, lmax=6)[0]}
            log.append(row); print(json.dumps(row), flush=True)
        if last: break
    model.eval(); sha = save_reg(model, os.path.join(out, "checkpoint.pt"), {"args": vars(a)})
    json.dump({"name": a.name, "args": vars(a), "config": cfg.__dict__, "checkpoint_sha256": sha, "parameters": model.n_params(), "gradient_steps": it,
               "episodes_seen": it * a.batch, "phase2_started_at_step": switch, "wall_seconds": round(time.time() - t0, 1),
               "world": {"t23": "Dispatch-3, training families, 2-3 legs, same-gate legs (the v0.2 training distribution)",
                         "t24x": "Dispatch-3, training families, 2-4 legs, cross-gate legs with probability 0.3 per leg"}[a.data],
               "supervision": "set-valued valid actions from the exact planner" + ("; training aid: the exact planner's value table after each sweep step" if a.aid > 0 else "; no other signal"),
               "memory": "typed registers, written by rule (not learned)", "torch": torch.__version__, "log": log},
              open(os.path.join(out, "manifest.json"), "w"), indent=1)
    print("saved", out, sha)


if __name__ == "__main__":
    main()
