"""Dispatch-3: the batched world must agree with the plain-Python reference planner, and the two
implementations of the family hash must agree."""
import torch
from stillway2.world3 import *

def run(spec_name="train_stress", n=400, seed=0, **over):
    gen = torch.Generator().manual_seed(seed)
    spec = {**SPECS[spec_name], **over}
    w = World3(n, spec, gen); checks = 0
    b = bucket_t(w.L, w.eff, w.tg, w.parcel)
    for i in range(n):
        sig = signature(int(w.L[i]), w.eff[i].tolist(), w.tg[i].tolist(), w.parcel[i].tolist())
        assert bucket(sig) == int(b[i]), "hash implementations disagree"
        if spec["split"]: assert split_of(sig) == spec["split"]
    for t in range(w.T):
        obs, act = w.next_obs()
        kind, leg = w.slot(t)
        assert obs.shape == (n, OBS3) and torch.isfinite(obs).all()
        if kind in (ROUTE, DELIVER):
            v = w.valid_mask()
            for i in act.nonzero().flatten().tolist():
                if kind == ROUTE:
                    ref = ref_valid_routes(int(w.L[i]), w.eff[i].tolist(), w.tg[i].tolist(), w.gates[i].tolist(), w.q[i].tolist(), int(w.cur[i]))
                    assert tuple(v[i, :2].nonzero().flatten().tolist()) == ref and int(w.cur[i]) == leg
                else:
                    assert v[i].nonzero().flatten().tolist() == [2 + ref_dock(int(w.p[i, leg]), int(w.closed[i]))]
                checks += 1
            w.apply(w.env_action(v), act)
    return checks

if __name__ == "__main__":
    c = run() + run("train", seed=1) + run("dev", seed=2) + run("train", seed=3, L=(2, 3, 4), cross=0.5, split=None, K=3)
    print("world3 agrees with the reference planner on", c, "action stages; hash implementations agree")
