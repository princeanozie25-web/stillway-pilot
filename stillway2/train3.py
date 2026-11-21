"""Train a v0.2 core on Dispatch-3 by imitation of the exact planner (set-valued targets).

    python -m stillway2.train3 --name v2_iit_s1 --iit 1.0 --seed 1

Only families in the TRAIN split, 2 or 3 legs, same-gate legs.  Two phases as in v0.1: continuous memory
until the task loss is low, then the quantiser (and interchange training, if asked) for --post steps.
Interchange training here swaps one field slot between two jobs that can be at different stages, in
different layouts and with different numbers of legs.
"""
from __future__ import annotations

import argparse, json, os, time

import torch
import torch.nn.functional as F

from .model3 import Config3, Core3, act_argmax, save3
from .world3 import DELIVER, NF, ROUTE, SPECS, World3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def set_ce(logits, valid, stage_mask, act):
    lg = logits.masked_fill(~stage_mask[None, :], -1e9)
    logp = F.log_softmax(lg, -1)
    l = -torch.logsumexp(logp.masked_fill(~valid, -1e9), -1)
    return (l * act).sum() / act.sum().clamp(min=1)


def advance(model, w, mem, quant, t0, t1):
    """Run frame slots t0..t1-1.  Returns (loss, commit, mem, slot vectors seen)."""
    B = w.B; loss = torch.zeros(()); commit = torch.zeros(()); aux = torch.zeros(()); zs = []
    for t in range(t0, t1):
        obs, act = w.next_obs()
        kind, _ = w.slot(t)
        if not act.any():
            continue
        idx = act.nonzero().squeeze(1)                              # only jobs that have this slot are stepped
        h, logits, z_e = model.step(mem[idx], obs[idx])
        if kind in (ROUTE, DELIVER):
            valid = w.valid_mask()
            loss = loss + set_ce(logits, valid[idx], w.stage_mask(), torch.ones(len(idx)))
            if kind == ROUTE and VALUE_W > 0:
                # value head: the exact planner's count for each route (richer signal than the valid set alone)
                tgt = w.best_counts()[idx].clamp(min=0)
                aux = aux + VALUE_W * F.cross_entropy(model.value_head(h).view(-1, 3), tgt.reshape(-1))
            w.apply(w.env_action(valid), act)
        zs.append(z_e.detach())
        if quant:
            _, st, c = model.quantize_train(z_e); commit = commit + c
        else:
            st = z_e.reshape(len(idx), -1)
        mem = mem.index_copy(0, idx, st)
    return loss + aux, commit, mem, zs


VALUE_W = 0.5


def rollout_loss(model, w, quant, iit):
    B, S, D = w.B, model.cfg.n_slots, model.cfg.code_dim
    mem = torch.zeros(B, S * D)
    if iit <= 0:
        loss, commit, mem, zs = advance(model, w, mem, quant, 0, w.T)
        return loss, commit, torch.zeros(()), torch.cat(zs)
    ts = int(torch.randint(1, w.T - 1, (1,), generator=w.gen))             # swap after slot ts-1
    l1, c1, mem, z1 = advance(model, w, mem, quant, 0, ts)
    f = int(torch.randint(0, NF, (1,), generator=w.gen)); perm = torch.randperm(B, generator=w.gen)
    m3 = mem.view(B, S, D).clone(); m3[:, f] = mem.view(B, S, D)[perm, f]
    w2 = w.clone()
    if f < 2: w2.q[:, f] = w.q[perm, f]
    else: w2.p[:, f - 2] = w.p[perm, f - 2]
    l2, c2, _, z2 = advance(model, w, mem, quant, ts, w.T)
    l3, c3, _, z3 = advance(model, w2, m3.reshape(B, -1), quant, ts, w.T)
    return l1 + l2, c1 + c2 + c3, iit * l3, torch.cat(z1 + z2)


@torch.no_grad()
def batch_eval3(model, spec, n, seed):
    """Closed-loop run with discrete inference.  Returns the share of jobs with every action valid."""
    model.eval(); gen = torch.Generator().manual_seed(seed)
    w = World3(n, {**spec, "env": "model"}, gen)
    disc = model.cfg.quantizer == "vq"
    ids = torch.full((n, model.cfg.n_slots), -1); mem = torch.zeros(n, model.cfg.n_slots * model.cfg.code_dim)
    ok = torch.ones(n, dtype=torch.bool)
    for t in range(w.T):
        obs, act = w.next_obs(); kind, _ = w.slot(t)
        if disc:
            logits, new = model.infer(ids, obs); ids = torch.where(act[:, None], new, ids)
        else:
            logits, new = model.infer_cont(mem, obs); mem = torch.where(act[:, None], new, mem)
        if kind in (ROUTE, DELIVER):
            a = act_argmax(logits, kind); v = w.valid_mask()
            ok &= v[torch.arange(n), a] | ~act
            w.apply(a, act)
    return ok.float().mean().item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True); ap.add_argument("--quantizer", default="vq")
    ap.add_argument("--iit", type=float, default=0.0); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--batch", type=int, default=512); ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--warmup", type=int, default=30000); ap.add_argument("--min-warmup", type=int, default=3000)
    ap.add_argument("--switch-loss", type=float, default=0.04); ap.add_argument("--post", type=int, default=8000)
    ap.add_argument("--n-slots", type=int, default=8); ap.add_argument("--n-codes", type=int, default=16)
    ap.add_argument("--profile", default="train+train_stress"); ap.add_argument("--max-steps", type=int, default=0)
    a = ap.parse_args()
    torch.set_num_threads(1); torch.manual_seed(a.seed); gen = torch.Generator().manual_seed(a.seed)
    cfg = Config3(n_slots=a.n_slots, n_codes=a.n_codes, quantizer=a.quantizer)
    model = Core3(cfg); opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.0)
    out = os.path.join(ROOT, "runs", a.name); os.makedirs(out, exist_ok=True)
    profs = a.profile.split("+"); use_q = cfg.quantizer == "vq"
    it, switch, ema, log, t0 = 0, None, 1.0, [], time.time()
    while True:
        it += 1; model.train()
        w = World3(a.batch, SPECS[profs[it % len(profs)]], gen)
        phase2 = switch is not None
        loss, commit, iit_loss, zs = rollout_loss(model, w, use_q and phase2, a.iit if phase2 else 0.0)
        ema = 0.98 * ema + 0.02 * loss.item()
        if switch is None and ((it >= a.min_warmup and ema < a.switch_loss) or it >= a.warmup):
            switch = it
            if use_q: model.init_codebook(zs.reshape(-1, cfg.n_slots, cfg.code_dim))
        total = loss + cfg.beta * commit + iit_loss
        opt.zero_grad(); total.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        last = (switch is not None and it >= switch + a.post) or (a.max_steps and it >= a.max_steps)
        if it % 500 == 0 or last:
            row = {"step": it, "phase": 2 if phase2 else 1, "loss": round(loss.item(), 4), "ema": round(ema, 4), "commit": round(commit.item(), 4),
                   "iit": round(float(iit_loss), 4), "sec": round(time.time() - t0, 1)}
            if not use_q or phase2:
                row["train"] = batch_eval3(model, SPECS["train"], 1500, 7); row["dev"] = batch_eval3(model, SPECS["dev"], 1500, 9)
                row["dev_plain"] = batch_eval3(model, SPECS["dev_plain"], 1500, 10)
            log.append(row); print(json.dumps(row), flush=True)
        if last: break
    model.eval(); sha = save3(model, os.path.join(out, "checkpoint.pt"), {"args": vars(a)})
    json.dump({"name": a.name, "args": vars(a), "config": cfg.__dict__, "checkpoint_sha256": sha, "parameters": model.n_params(),
               "gradient_steps": it, "episodes_seen": it * a.batch, "phase2_started_at_step": switch, "wall_seconds": round(time.time() - t0, 1),
               "world": "Dispatch-3, train split, 2-3 legs, same-gate legs", "supervision": "set-valued valid actions from the exact planner; value head: per-route count of reachable gate requirements (weight 0.5)"
               + ("; interchange training with counterfactual labels" if a.iit > 0 else ""), "torch": torch.__version__, "log": log},
              open(os.path.join(out, "manifest.json"), "w"), indent=1)
    print("saved", out, sha)


if __name__ == "__main__":
    main()
