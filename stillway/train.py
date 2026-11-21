"""Train one planner core by imitation of the exact planner (set-valued targets).

    python -m stillway.train --name vq_dyn_s1 --quantizer vq --profile dynamic --seed 1

Supervision used: at every action stage the simulator supplies the SET of valid
actions (exact planner).  No rewards.  Optional auxiliary heads are documented in
the manifest.  Only families in the TRAIN split are ever sampled.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import time

import torch
import torch.nn.functional as F

from .fixtures import ROOT, families, layouts_of
from .model import Config, Core, save_checkpoint, stage_argmax
from .vworld import PROFILES, VWorld
from .world import BAY, LEG1, LEG2, N_STAGES, STAGE_ACTIONS


def set_ce(logits: torch.Tensor, valid: torch.Tensor, stage_mask: torch.Tensor) -> torch.Tensor:
    """-log( sum of probability on valid actions ), actions limited to this stage's type."""
    lg = logits.masked_fill(~stage_mask[None, :], -1e9)
    logp = F.log_softmax(lg, -1)
    return -(torch.logsumexp(logp.masked_fill(~valid, -1e9), -1)).mean()


def _rest(model: Core, w: VWorld, mem: torch.Tensor, quant: bool, start: int):
    """Finish an episode from stage `start` with the given memory; return the imitation loss."""
    loss = torch.zeros(())
    for s in range(start, N_STAGES):
        obs = w.next_obs()
        h, logits, z_e = model.step(mem, obs)
        if s in STAGE_ACTIONS:
            valid = w.valid_mask()
            loss = loss + set_ce(logits, valid, w.stage_mask())
            w.apply(w.env_action(None, valid))
        mem = model.quantize_train(z_e)[1] if quant else z_e.reshape(w.B, -1)
    return loss


IIT_SLOT = {"q": 0, "d": 1, "b": 2}     # interchange training: which slot is trained to hold which field


def rollout_loss(model: Core, w: VWorld, quant: bool, aux: str, inertia: float = 0.0, iit: float = 0.0,
                 inertia_msg: float = -1.0):
    """One batch of episodes.  Returns loss terms and the slot vectors seen (for codebook init)."""
    B = w.B
    mem = torch.zeros(B, model.cfg.n_slots * model.cfg.code_dim)
    loss = torch.zeros(()); commit = torch.zeros(()); aux_loss = torch.zeros(())
    zs = []
    S, D = model.cfg.n_slots, model.cfg.code_dim
    iit_stage = int(torch.randint(0, 4, (1,), generator=w.gen)) if iit > 0 else -1
    for s in range(N_STAGES):
        obs = w.next_obs()
        h, logits, z_e = model.step(mem, obs)
        if s in STAGE_ACTIONS:
            valid = w.valid_mask()
            loss = loss + set_ce(logits, valid, w.stage_mask())
            if aux == "sat" and s in (LEG1, LEG2):
                # effect head: for each route, will the gate obligation still be met?  (exact rollouts)
                aux_loss = aux_loss + F.binary_cross_entropy_with_logits(model.aux_head(h), w.route_ok().float())
            if aux == "hidden" and s == BAY:
                # irrelevant balanced property: the two decoration bits shown at INIT
                tgt = torch.stack([(w.decor0 & 1), (w.decor0 >> 1) & 1], 1).float()
                aux_loss = aux_loss + F.binary_cross_entropy_with_logits(model.aux_head(h), tgt)
            w.apply(w.env_action(None, valid))
        zs.append(z_e.detach())
        if inertia > 0 and s > 0:
            # inertia: memory should change in as few slots as possible at each step (group lasso over slots)
            # On steps where the operator sent a message the penalty can be weaker (inertia_msg), so
            # revisions are allowed but still pushed to touch few slots.
            has_msg = (obs[:, 29] + obs[:, 31] + obs[:, 33]) > 0
            lam = torch.where(has_msg, torch.full((B,), inertia_msg if inertia_msg >= 0 else inertia), torch.full((B,), inertia))
            aux_loss = aux_loss + (lam * (z_e - mem.detach().view(B, S, D)).norm(dim=-1).sum(1)).mean()
        if quant:
            _, mem, c = model.quantize_train(z_e)
            commit = commit + c
        else:
            mem = z_e.reshape(B, -1)
        if iit > 0 and s == iit_stage:
            # interchange intervention training (Geiger et al. 2022): swap one slot between two runs
            # and train on what the exact planner says the run should then do.  Uses counterfactual labels.
            # after the dock hand-over (stage 3) the dock field is spent, so only q and b are swapped there
            field = ["q", "b", "d"][int(torch.randint(0, 2 if s == 3 else 3, (1,), generator=w.gen))]
            perm = torch.randperm(B, generator=w.gen)
            m3 = mem.view(B, S, D).clone()
            m3[:, IIT_SLOT[field]] = mem.view(B, S, D)[perm, IIT_SLOT[field]]
            w2 = copy.copy(w)
            for k in ("eff", "gate", "decor", "decor0", "closed", "d", "q", "b", "open"):
                setattr(w2, k, getattr(w, k).clone())
            setattr(w2, field, getattr(w, field)[perm].clone())
            aux_loss = aux_loss + iit * _rest(model, w2, m3.reshape(B, -1), quant, s + 1)
    return loss, commit, aux_loss, torch.cat(zs, 0)


@torch.no_grad()
def batch_eval(model: Core, layouts: torch.Tensor, profile: str, n: int, seed: int, instructed: bool = True) -> dict:
    """Closed-loop accuracy with discrete inference (IDs only between steps)."""
    model.eval()
    gen = torch.Generator().manual_seed(seed)
    w = VWorld(layouts, n, PROFILES[profile], gen, instructed)
    discrete = model.cfg.quantizer == "vq"
    ids = torch.full((n, model.cfg.n_slots), -1)
    mem = torch.zeros(n, model.cfg.n_slots * model.cfg.code_dim)
    ok = torch.ones(n, dtype=torch.bool)
    for s in range(N_STAGES):
        obs = w.next_obs()
        if discrete:
            logits, ids = model.infer(ids, obs)
        else:
            logits, mem = model.infer_cont(mem, obs)
        if s in STAGE_ACTIONS:
            a = stage_argmax(logits, s)
            valid = w.valid_mask()
            ok &= valid[torch.arange(n), a]
            w.apply(a)
    return {"all_valid": ok.float().mean().item()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--quantizer", default="vq")
    ap.add_argument("--profile", default="dynamic+stress+stress2")
    ap.add_argument("--aux", default="none")
    ap.add_argument("--aux-weight", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--warmup", type=int, default=9000, help="latest step at which phase 2 starts")
    ap.add_argument("--min-warmup", type=int, default=2000)
    ap.add_argument("--switch-loss", type=float, default=0.03)
    ap.add_argument("--post", type=int, default=6000, help="steps in phase 2")
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--n-slots", type=int, default=4)
    ap.add_argument("--n-codes", type=int, default=32)
    ap.add_argument("--width", type=int, default=128)
    ap.add_argument("--inertia", type=float, default=0.0)
    ap.add_argument("--iit", type=float, default=0.0)
    ap.add_argument("--inertia-msg", type=float, default=-1.0, help="inertia weight on steps with an operator message")
    ap.add_argument("--k-final", type=int, default=10**6, help="prune each slot's codebook down to this many codes")
    ap.add_argument("--prune-every", type=int, default=60)
    ap.add_argument("--effect-embed", default="onehot")
    ap.add_argument("--reader", default="sweep")
    ap.add_argument("--cosine", action="store_true")
    ap.add_argument("--wd", type=float, default=0.0)
    ap.add_argument("--uninstructed", action="store_true")
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args()

    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    gen = torch.Generator().manual_seed(a.seed)
    cfg = Config(width=a.width, n_slots=a.n_slots, n_codes=a.n_codes, quantizer=a.quantizer, aux=a.aux,
                 effect_embed=a.effect_embed, reader=a.reader)
    model = Core(cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.wd)
    train_lay = torch.tensor(layouts_of(families("train")))
    dev_lay = torch.tensor(layouts_of(families("dev")))
    out = os.path.join(ROOT, "runs", a.name)
    os.makedirs(out, exist_ok=True)
    log = []
    t0 = time.time()
    use_q = cfg.quantizer == "vq"
    # Two phases.  Phase 1: continuous memory until the task loss (running mean) falls below
    # --switch-loss, or --warmup steps at most.  Phase 2: --post more steps, with the quantiser on
    # (discrete arms) and with the inertia penalty if asked.  Continuous arms get the same budget.
    it, switch, ema = 0, None, 1.0
    profs = a.profile.split("+")                           # e.g. "dynamic+stress" alternates batch by batch
    while True:
        it += 1
        model.train()
        w = VWorld(train_lay, a.batch, PROFILES[profs[it % len(profs)]], gen, not a.uninstructed)
        phase2 = switch is not None
        quant = use_q and phase2
        loss, commit, aux_loss, zs = rollout_loss(model, w, quant, a.aux, a.inertia if phase2 else 0.0,
                                                 a.iit if phase2 else 0.0, a.inertia_msg)
        if use_q and phase2 and a.k_final < cfg.n_codes and it % a.prune_every == 0:
            if model.prune_one(a.k_final):
                switch = it                                # the phase-2 budget starts when pruning is done
        ema = 0.98 * ema + 0.02 * loss.item()
        if switch is None and ((it >= a.min_warmup and ema < a.switch_loss) or it >= a.warmup):
            switch = it
            if use_q:
                model.init_codebook(zs.reshape(-1, cfg.n_slots, cfg.code_dim))
        total = loss + cfg.beta * commit + a.aux_weight * aux_loss
        opt.zero_grad(); total.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        last = switch is not None and it >= switch + a.post
        if it % 500 == 0 or last:
            ins = not a.uninstructed
            row = {"step": it, "phase": 2 if switch is not None and it > switch else 1, "loss": round(loss.item(), 4),
                   "commit": round(commit.item(), 4), "aux": round(aux_loss.item(), 4), "sec": round(time.time() - t0, 1)}
            if not use_q or (switch is not None and it > switch):
                row["train_plain"] = batch_eval(model, train_lay, "plain", 2000, 7, ins)["all_valid"]
                row["train_dyn"] = batch_eval(model, train_lay, "plain_dynamic", 2000, 8, ins)["all_valid"]
                row["dev_plain"] = batch_eval(model, dev_lay, "plain", 2000, 9, ins)["all_valid"]
                row["dev_dyn"] = batch_eval(model, dev_lay, "plain_dynamic", 2000, 10, ins)["all_valid"]
            log.append(row)
            print(json.dumps(row), flush=True)
        if last:
            break
    a.steps = it
    model.eval()
    sha = save_checkpoint(model, os.path.join(out, "checkpoint.pt"), {"args": vars(a)})
    manifest = {
        "name": a.name, "args": vars(a), "config": cfg.__dict__, "checkpoint_sha256": sha,
        "parameters": model.n_params(), "train_families": families("train"),
        "episodes_seen": a.steps * a.batch, "gradient_steps": a.steps, "phase2_started_at_step": switch, "wall_seconds": round(time.time() - t0, 1),
        "supervision": "set-valued valid actions from the exact planner at 4 action stages per episode"
                       + {"none": "", "sat": "; plus effect head: per-route obligation outcome from exact rollouts",
                          "hidden": "; plus irrelevant head: INIT decoration bits"}[a.aux]
                       + ("; plus inertia penalty on slot changes (no labels)" if a.inertia > 0 else "")
                       + ("; plus interchange training with counterfactual labels from the exact planner" if a.iit > 0 else ""),
        "simulator_access": "training only; inference uses observations",
        "torch": torch.__version__, "device": "cpu", "threads": a.threads, "log": log,
    }
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    print("saved", out, sha)


if __name__ == "__main__":
    main()
