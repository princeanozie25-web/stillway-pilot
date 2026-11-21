"""Does the certificate predict the simulator?   python v03/confirm.py runs/v3r24fix_s1 [JOBS=100000]

For each alphabet, fresh jobs of 2 to 16 legs (uniform), every family, ordinary events, run through the NETWORK
in the simulator.  Counted: action stages, wrong actions, jobs with a wrong action.
Prediction to check: a core whose closure is clean on an alphabet makes no wrong action on that alphabet.
"""
import json, os, sys, torch
from stillway2.model3 import act_argmax
from stillway2.world3 import DELIVER, ROUTE, SPECS
from stillway3.certify import certify, extract
from stillway3.model import load_reg
from stillway3.world import WorldN

run = sys.argv[1].rstrip("/"); name = os.path.basename(run); JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
torch.set_num_threads(int(os.environ.get("THREADS", "1"))); model = load_reg(os.path.join(run, "checkpoint.pt")); out = {"run": name, "checkpoint_sha256": model.sha256}
tab = extract(model) if model.cfg.carry == "vq" else None
for alpha, cross in (("same", 0.0), ("all", 0.3)):
    cert = certify(tab, alpha, 0) if tab else None
    spec = {**SPECS["dev"], "split": None, "L": tuple(range(2, 17)), "cross": cross, "env": "model"}
    stages = wrong = bad_jobs = 0; by_len = {}
    with torch.no_grad():
        for b in range(JOBS // 10000):
            w = WorldN(10000, spec, torch.Generator().manual_seed(777000 + 10 * b + (cross > 0)), lmax=16)
            ids = torch.full((10000, w.NF), -1); ok = torch.ones(10000, dtype=torch.bool)
            for t in range(w.T):
                obs, act = w.next_obs(); kind, _ = w.slot(t)
                logits, new = model.infer(ids, obs); ids = torch.where(act[:, None], new, ids)
                if kind in (ROUTE, DELIVER):
                    a = act_argmax(logits, kind); v = w.valid_mask()[torch.arange(10000), a]
                    stages += int(act.sum()); wrong += int((act & ~v).sum()); ok &= v | ~act; w.apply(a, act)
            bad_jobs += int((~ok).sum())
            for L in range(2, 17):
                m = w.L == L; x = by_len.setdefault(L, [0, 0]); x[0] += int(m.sum()); x[1] += int((m & ~ok).sum())
    out[alpha] = {"certificate_route_wrong": cert["route_wrong"] if cert else None, "certificate_route_checks": cert["route_checks"] if cert else None,
                  "jobs": JOBS, "action_stages": stages, "wrong_actions": wrong, "jobs_with_a_wrong_action": bad_jobs,
                  "jobs_wrong_by_legs": {L: x[1] / max(1, x[0]) for L, x in by_len.items()},
                  "prediction_holds": None if cert is None else (wrong == 0 if cert["route_wrong"] == 0 else True)}
    print(name, alpha, {k: out[alpha][k] for k in ("certificate_route_wrong", "action_stages", "wrong_actions", "jobs_with_a_wrong_action", "prediction_holds")}, flush=True)
os.makedirs("results/v03/confirm", exist_ok=True); json.dump(out, open(f"results/v03/confirm/{name}.json", "w"), indent=1)
