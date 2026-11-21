"""v0.3 core: the register rule, and the tables against the network.

    PYTHONPATH=. python tests/test_regcore.py runs/v3r24_s1
"""
import sys
import torch
from stillway2.world3 import DELIVER, ROUTE, SPECS
from stillway3.certify import TablePlanner, extract
from stillway3.model import RegCore, load_reg
from stillway3.world import WorldN, layout


def register_rule():
    """Registers always equal the order of record, whatever the events (stress profile, several lengths)."""
    n = 0
    for lmax, legs in ((4, (2, 3, 4)), (8, (5, 8))):
        spec = {**SPECS["train_stress"], "L": legs, "cross": 0.3, "split": None, "noop_msg": 0.2, "env": "random"}
        for seed in (1, 2, 3):
            w = WorldN(500, spec, torch.Generator().manual_seed(seed), lmax=lmax); ids = torch.full((500, w.NF), -1)
            for t in range(w.T):
                obs, act = w.next_obs(); ids = torch.where(act[:, None], RegCore.write(ids, obs), ids)
                assert torch.equal(ids, torch.cat([w.q, w.p], 1)), (lmax, seed, t); n += int(act.sum())
                if w.slot(t)[0] in (ROUTE, DELIVER): w.apply(w.env_action(w.valid_mask()), act)
    return n


@torch.no_grad()
def tables_equal_network(model, lmax=8, legs=(2, 3, 5, 8), n=1500):
    """The integer tables and the network propose the same action at every action stage of sampled jobs."""
    tp = TablePlanner(extract(model)); steps = 0
    spec = {**SPECS["train_stress"], "L": legs, "cross": 0.3, "split": None, "env": "random"}
    w = WorldN(n, spec, torch.Generator().manual_seed(4), lmax=lmax); ids = torch.full((n, w.NF), -1)
    for t in range(w.T):
        obs, act = w.next_obs(); kind, leg = w.slot(t)
        logits, new = model.infer(ids, obs); ids = torch.where(act[:, None], new, ids)
        if kind not in (ROUTE, DELIVER): continue
        for i in act.nonzero().squeeze(1).tolist():
            if kind == ROUTE:
                ahead = [(int(w.eff[i, j, 0]) * 2 + int(w.tg[i, j, 0]), int(w.eff[i, j, 1]) * 2 + int(w.tg[i, j, 1])) for j in range(leg, int(w.L[i]))]
                a = tp.route(ids[i, :2].tolist(), w.gates[i].tolist(), ahead); assert a == int(logits[i, :2].argmax()), (t, i)
            else:
                assert tp.dock(int(ids[i, 2 + leg]), int(w.closed[i])) == int(logits[i, 2:].argmax()), (t, i)
            steps += 1
        w.apply(w.env_action(w.valid_mask()), act)
    return steps


if __name__ == "__main__":
    print("register rule: registers equal the order of record at", register_rule(), "job steps")
    for run in sys.argv[1:]:
        print(run, "tables equal the network at", tables_equal_network(load_reg(run.rstrip("/") + "/checkpoint.pt")), "action stages")
    print("OK")
