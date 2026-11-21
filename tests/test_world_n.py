"""WorldN (any number of legs) against the frozen world3.py and against the plain-Python reference.

    PYTHONPATH=. python tests/test_world_n.py
"""
import torch
from stillway2.world3 import World3, SPECS, ROUTE, DELIVER, ref_valid_routes, ref_dock, bucket, signature
from stillway3.world import WorldN, bucket_n, SPECS as SPECS3


def same_as_world3():
    n_obs = n_valid = 0
    for name, spec in list(SPECS.items()) + [("final_cross", {**SPECS["train_stress"], "split": "final", "L": (2, 3, 4), "cross": 0.4}),
                                             ("force_cross", {**SPECS["dev"], "split": None, "force_cross": True, "noop_msg": 0.2})]:
        for seed in (1, 2, 3):
            a = World3(400, {**spec, "env": "random"}, torch.Generator().manual_seed(seed))
            b = WorldN(400, {**spec, "env": "random"}, torch.Generator().manual_seed(seed), lmax=4)
            ga = torch.Generator().manual_seed(99)
            for t in range(a.T):
                oa, aa = a.next_obs(); ob, ab = b.next_obs(); kind, _ = a.slot(t)
                assert torch.equal(oa, ob) and torch.equal(aa, ab), (name, seed, t); n_obs += len(oa)
                if kind in (ROUTE, DELIVER):
                    va, vb = a.valid_mask(), b.valid_mask()
                    assert torch.equal(va[aa], vb[aa]), (name, seed, t); n_valid += int(aa.sum())
                    if kind == ROUTE:
                        live = aa & (a.cur < a.L)
                        assert torch.equal(a.best_counts()[live], b.best_counts()[live])
                        assert torch.equal(a.dp_tables(), b.dp_tables()[:, :4])
                    act = torch.multinomial(a.stage_mask()[None].expand(400, -1).float(), 1, generator=ga).squeeze(1)
                    a.apply(act, aa); b.apply(act, ab)
            assert torch.equal(a.gates, b.gates) and torch.equal(a.deliver_ok, b.deliver_ok)
    return n_obs, n_valid


def against_reference(lmax, legs, n=300, seed=5):
    spec = {**SPECS["train_stress"], "L": legs, "cross": 0.4, "split": None, "env": "random"}
    w = WorldN(n, spec, torch.Generator().manual_seed(seed), lmax=lmax); checked = 0
    for t in range(w.T):
        obs, act = w.next_obs(); kind, leg = w.slot(t)
        if kind not in (ROUTE, DELIVER): continue
        v = w.valid_mask()
        for i in act.nonzero().squeeze(1).tolist():
            if kind == ROUTE:
                ref = ref_valid_routes(int(w.L[i]), w.eff[i].tolist(), w.tg[i].tolist(), w.gates[i].tolist(), w.q[i].tolist(), int(w.cur[i]))
                assert tuple(v[i, :2].nonzero().squeeze(1).tolist()) == ref, (lmax, t, i)
            else:
                assert v[i, 2:].nonzero().item() == ref_dock(int(w.p[i, leg]), int(w.closed[i]))
            checked += 1
        w.apply(w.env_action(v), act)
    return checked


def buckets():
    g = torch.Generator().manual_seed(3)
    w = WorldN(500, {**SPECS["train"], "split": None, "L": (2, 3, 4), "cross": 0.5, "env": "random"}, g, lmax=8)
    b = bucket_n(w.L, w.eff, w.tg, w.parcel)
    for i in range(500):
        assert int(b[i]) == bucket(signature(int(w.L[i]), w.eff[i, :4].tolist(), w.tg[i, :4].tolist(), w.parcel[i, :4].tolist())), i
    for split in ("train", "dev", "final"):                       # long jobs: the split is honoured and non-empty
        w = WorldN(300, {**SPECS["train"], "split": split, "L": (5, 6, 7, 8), "cross": 0.3, "env": "random"}, g, lmax=8)
        b = bucket_n(w.L, w.eff, w.tg, w.parcel); lo, hi = {"train": (0, 60), "dev": (60, 70), "final": (70, 100)}[split]
        assert ((b >= lo) & (b < hi)).all()
    return 500


if __name__ == "__main__":
    a, b = same_as_world3(); print("equal to world3.py at lmax=4:", a, "observations,", b, "action stages")
    tot = 0
    for lmax, legs in ((4, (2, 3, 4)), (8, (5, 6, 7, 8)), (10, (9, 10))):
        tot += against_reference(lmax, legs, n=300 if lmax < 10 else 60)
    print("equal to the plain reference:", tot, "action stages up to 10 legs")
    print("family buckets equal to world3.py for up to 4 legs:", buckets(), "jobs")
    print("OK")
