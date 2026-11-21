"""Certificate-guided repair: retrain a v0.3 core on the cases its own certificate finds.

    python -m stillway3.repair runs/v3r24_s1 --alphabet all --out runs/v3r24fix_s1

Each round:  read the tables off the network, run the closure (stillway3/certify.py), turn EVERY wrong
decision into a real job (gate requirements, the legs behind the current one, the gates), label it with the
exact planner, and train on those jobs mixed with ordinary training batches.  Stop when the closure is clean
or after --rounds rounds.
Option --rehearsal N (default 0, off): also train on N randomly chosen RIGHT entries of the current closure.
Tried on the hardest seed (v3r24_s5): clean after 6 rounds with it, 7 without, at twice the cost per round.
The frozen repaired cores were made without it.

What this uses that plain training does not: exact-planner labels on jobs chosen by the certificate.  Those
jobs can be longer than any training job (their length is the depth at which the closure found the fault);
the longest one used is recorded.  No final family is touched: the jobs are built from the closure, not sampled.
"""
from __future__ import annotations

import argparse, json, os, time

import torch
import torch.nn.functional as F

from stillway2.train3 import set_ce
from .certify import TRIPS, certify, extract
from .model import load_reg, save_reg
from .train import batch_eval, rollout
from .world import SPECS, WorldN

PLAIN = dict(cross=0.0, split=None, K=0, p_wait=0.0, rev=0, gflip=0, decor=0, close=0, msg=0, full=0, reissue=0, env="random")


def witness_world(wits, gen) -> WorldN:
    n = len(wits); M = max(2, max(1 + len(w["legs_after"]) for w in wits))
    w = WorldN(n, {**PLAIN, "L": (2,)}, gen, lmax=M)
    for i, wt in enumerate(wits):
        legs = [wt["current_leg"]] + wt["legs_after"]; w.L[i] = len(legs)
        for j, (a, b) in enumerate(legs):
            w.eff[i, j, 0], w.tg[i, j, 0] = TRIPS[a]; w.eff[i, j, 1], w.tg[i, j, 1] = TRIPS[b]
        w.q[i] = torch.tensor(wt["gate_requirements"]); w.gates[i] = torch.tensor(wt["gates"])
    w.parcel[:] = False
    return w


def witness_loss(model, w, aid):
    ids = torch.full((w.B, w.NF), -1); obs, _ = w.next_obs(); ids = model.write(ids, obs)
    obs, act = w.next_obs(); assert bool(act.all())
    logits, ax, cm = model.heads(ids, obs, want_aux=True); valid = w.valid_mask()
    loss = set_ce(logits, valid, w.stage_mask(), torch.ones(w.B)); dp = w.dp_tables()
    for (j, c, m) in ax:
        if m.any(): loss = loss + aid * F.cross_entropy(model.dp_head(c[m]).view(-1, 3), dp[m, j].reshape(-1))
    return loss + model.cfg.beta * cm


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--out", required=True); ap.add_argument("--alphabet", default="all")
    ap.add_argument("--rounds", type=int, default=30); ap.add_argument("--steps", type=int, default=300); ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--batch", type=int, default=512); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--rehearsal", type=int, default=0)
    a = ap.parse_args(); torch.set_num_threads(1)
    src = a.run.rstrip("/"); man = json.load(open(os.path.join(src, "manifest.json"))); data = man["args"]["data"]; aid = man["args"]["aid"]
    model = load_reg(os.path.join(src, "checkpoint.pt")); gen = torch.Generator().manual_seed(1000 + a.seed + man["args"]["seed"])
    torch.manual_seed(1000 + a.seed + man["args"]["seed"])
    import random; pyrng = random.Random(1000 + a.seed + man["args"]["seed"])
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.0); t0 = time.time(); log = []; pool = []; longest = 0; it = 0
    for rnd in range(a.rounds + 1):
        model.eval(); c = certify(extract(model), a.alphabet, max_witness=10 ** 9, rehearsal=a.rehearsal, rng=pyrng)
        row = {"round": rnd, "pairs": c["pairs"], "codes_used": c["codes_used"], "route_checks": c["route_checks"], "route_wrong": c["route_wrong"],
               "pool": len(pool), "sec": round(time.time() - t0, 1)}
        log.append(row); print(json.dumps(row), flush=True)
        if c["route_wrong"] == 0 or rnd == a.rounds: break
        pool += c["witnesses"]; longest = max(longest, max(1 + len(w["legs_after"]) for w in c["witnesses"]))
        for _ in range(a.steps):
            it += 1; model.train()
            pick = [pool[i] for i in torch.randint(0, len(pool), (min(a.batch, 4 * len(pool)),), generator=gen).tolist()]
            lw = witness_loss(model, witness_world(pick, gen), aid)
            if c.get("rehearsal"):
                keep = [c["rehearsal"][i] for i in torch.randint(0, len(c["rehearsal"]), (a.batch,), generator=gen).tolist()]
                lw = lw + witness_loss(model, witness_world(keep, gen), aid)
            w = WorldN(a.batch, SPECS[[data, data + "_stress"][it % 2]], gen, lmax=4)
            loss, aux, commit, _, _ = rollout(model, w, aid)
            total = loss + aux + model.cfg.beta * commit + lw
            opt.zero_grad(); total.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
    model.eval(); os.makedirs(a.out, exist_ok=True); sha = save_reg(model, os.path.join(a.out, "checkpoint.pt"), {"repaired_from": man["checkpoint_sha256"]})
    dev = {"t23": "dev23", "t24x": "dev24x"}[data]
    json.dump({"name": os.path.basename(a.out.rstrip("/")), "args": {**man["args"], "repair": vars(a)}, "config": man["config"], "checkpoint_sha256": sha,
               "repaired_from": {"run": man["name"], "checkpoint_sha256": man["checkpoint_sha256"]}, "alphabet": a.alphabet,
               "repair_rounds": log, "repair_gradient_steps": it, "witness_jobs_in_pool": len(pool), "longest_witness_job_legs": longest,
               "clean": log[-1]["route_wrong"] == 0, "wall_seconds": round(time.time() - t0, 1),
               "dev_after": batch_eval(model, SPECS[dev], 2000, 9)[0], "train_after": batch_eval(model, SPECS[data], 2000, 7)[0],
               "supervision": man["supervision"] + "; certificate-guided repair: exact-planner labels on jobs built from the closure's wrong decisions",
               "memory": man["memory"], "world": man["world"]}, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    print("saved", a.out, sha, "clean" if log[-1]["route_wrong"] == 0 else "NOT clean")


if __name__ == "__main__":
    main()
