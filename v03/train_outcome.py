"""EXPLORATORY (v0.3, section 7 of docs/v03_spec.md): train a v0.3 core with NO planner labels.

    python v03/train_outcome.py --name v3o_s1 --seed 1

Data: logged jobs driven by uniformly random actions (training families, 2-4 legs, cross-gate legs allowed,
bay closures and repaints, no gate faults, no re-wiring, no mid-job messages).  Signals, all read from the log:
  delivery   was the parcel accepted at the dock that was tried                     (right after the action)
  route      how many gate requirements held when the job ended                     (once, at the end)
The route function predicts, for each route, the final count if the rest of the job is done as well as
possible.  Its target for the last leg is the logged count; for an earlier leg it is the best count the
network itself (a slowly updated copy) predicts at the next leg of the same logged job.  No value table, no
valid action set, no exact planner anywhere in training.  The exact planner only SCORES the result.
The codebook is fitted by k-means (there is no table to read off a carry).
"""
import argparse, copy, json, os, sys, time
import torch, torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway2.world3 import DELIVER, ROUTE, SPECS as SPECS2
from stillway3.model import RegConfig, RegCore, save_reg
from stillway3.train import batch_eval
from stillway3.world import SPECS, WorldN

LOG_SPEC = {**SPECS2["train"], "L": (2, 3, 4), "cross": 0.3, "rev": 0.0, "gflip": 0.0, "msg": 0.0, "full": 0.0, "reissue": 0.0, "env": "random"}


def rollout(model, target, w):
    B, ar = w.B, torch.arange(w.B); ids = torch.full((B, w.NF), -1); loss_d = torch.zeros(()); commit = torch.zeros(()); zs = []
    pred = {}; vnext = torch.zeros(B, w.lmax + 1, dtype=torch.long)
    for t in range(w.T):
        obs, act = w.next_obs(); kind, leg = w.slot(t)
        ids = torch.where(act[:, None], model.write(ids, obs), ids)
        if kind not in (ROUTE, DELIVER) or not act.any(): continue
        idx = act.nonzero().squeeze(1)
        logits, ax, cm = model.heads(ids[idx], obs[idx], want_aux=True); commit = commit + cm
        a = w.env_action(None if w.s["env"] != "expert" else w.valid_mask())           # uniformly random action of this stage
        if kind == ROUTE:
            zs += [c[m].detach() for (_, c, m) in ax if m.any()]
            pred[leg] = (idx, model.route_raw.view(-1, 2, 3)[torch.arange(len(idx)), a[idx].clamp(0, 1)])
            with torch.no_grad():                                                       # best predicted count at this leg, from the slow copy
                target.heads(ids[idx], obs[idx]); vnext[idx, leg] = target.route_raw.view(-1, 2, 3).argmax(-1).max(1).values
            w.apply(a, act)
        else:
            w.apply(a, act)
            took = logits[torch.arange(len(idx)), a[idx]]
            loss_d = loss_d + F.binary_cross_entropy_with_logits(took, w.deliver_ok[idx, leg].float())
    final = ((w.q > 0) & (w.gates == w.q - 1)).sum(1)                                   # logged outcome
    loss_r = torch.zeros(())
    for leg, (idx, p) in pred.items():
        tgt = torch.where(w.L[idx] == leg + 1, final[idx], vnext[idx, min(leg + 1, w.lmax)])
        loss_r = loss_r + F.cross_entropy(p, tgt)
    return loss_r, loss_d, commit, zs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--name", required=True); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--warmup", type=int, default=5000); ap.add_argument("--post", type=int, default=5000); ap.add_argument("--batch", type=int, default=512)
    ap.add_argument("--lr", type=float, default=1e-3); ap.add_argument("--sync", type=int, default=100); a = ap.parse_args()
    torch.set_num_threads(1); torch.manual_seed(a.seed); gen = torch.Generator().manual_seed(a.seed)
    cfg = RegConfig(route_out=6); model = RegCore(cfg); target = copy.deepcopy(model); target.eval()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.0); out = os.path.join("runs", a.name); os.makedirs(out, exist_ok=True)
    log, t0, recent = [], time.time(), []
    for it in range(1, a.warmup + a.post + 1):
        model.train(); w = WorldN(a.batch, LOG_SPEC, gen, lmax=4)
        lr_, ld, commit, zs = rollout(model, target, w); recent = (recent + [torch.cat(zs)])[-8:]
        total = lr_ + ld + cfg.beta * commit
        opt.zero_grad(); total.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        if it == a.warmup: model.init_codebook(torch.cat(recent), gen); target.load_state_dict(model.state_dict())
        if it % a.sync == 0: target.load_state_dict(model.state_dict())
        if it % 500 == 0 or it == a.warmup + a.post:
            row = {"step": it, "phase": 1 if it <= a.warmup else 2, "route_loss": round(float(lr_), 4), "deliver_loss": round(float(ld), 4), "sec": round(time.time() - t0, 1),
                   "train": batch_eval(model, SPECS["t24x"], 2000, 7)[0], "dev": batch_eval(model, SPECS["dev24x"], 2000, 9)[0],
                   "dev_5to6_legs": batch_eval(model, {**SPECS["dev24x"], "L": (5, 6)}, 1000, 11, lmax=6)[0]}
            log.append(row); print(json.dumps(row), flush=True)
    model.eval(); sha = save_reg(model, os.path.join(out, "checkpoint.pt"), {"args": vars(a)})
    json.dump({"name": a.name, "args": {**vars(a), "data": "t24x", "aid": 0.0}, "config": cfg.__dict__, "checkpoint_sha256": sha, "parameters": model.n_params(),
               "gradient_steps": a.warmup + a.post, "episodes_seen": (a.warmup + a.post) * a.batch, "phase2_started_at_step": a.warmup, "wall_seconds": round(time.time() - t0, 1),
               "exploratory": True, "world": "Dispatch-3, training families, 2-4 legs, cross-gate legs with probability 0.3; logged jobs with random actions",
               "supervision": "logged outcomes only: parcel accepted or not; number of gate requirements held at the end.  No planner labels.",
               "memory": "typed registers, written by rule (not learned)", "torch": torch.__version__, "log": log}, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    print("saved", out, sha)


if __name__ == "__main__":
    main()
