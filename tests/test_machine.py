"""Check the exhaustive extractor against plain simulation.

1. Every counterexample the extractor reports must reproduce: replaying its witness history
   through the planner step by step gives an action the exact planner rejects.
2. Random histories drawn from the extractor's own alphabet never leave its reachable set,
   and never fail where the extractor reported zero violations.
"""
import random, sys, torch
from stillway.automaton import MSGS, Machine, pack
from stillway.model import NeuralPlanner, load_checkpoint
from stillway.world import *
import numpy as np

def obs_from(desc_stage, e, g, c, dec, msg):
    return Obs(desc_stage, e, g, c, dec, msg[0], msg[1], msg[2])

def main(run, fams):
    torch.set_num_threads(2)
    model = load_checkpoint(run + "/checkpoint.pt"); pl = NeuralPlanner(model)
    rng = random.Random(0)
    for f in fams:
        lay = [e for e in ALL_LAYOUTS if family_of(e) == f]
        m = Machine(model, lay)
        al = m.alpha
        # 1. counterexamples reproduce
        for viol in m.violations[:20]:
            hist = m.witness(viol["stage"] - 1, viol["state"])
            state = list(pl.blank); order = None
            def to_obs(d, stage):
                e = tuple(EFFECT_NAMES.index(ch) for ch in d["leg1"] + d["leg2"])
                return Obs(stage, e, d["gate"], NO_BAY if d["closed_bay"] is None else d["closed_bay"], d["decor"], *d["message"])
            for st, d in enumerate(hist):
                o = to_obs(d, st)
                order = Order(*[x if x is not None else y for x, y in zip(d["message"], order.as_tuple() if order else (0, 0, 0))])
                state = pl.advance(state, o)
            d = al.describe(viol["stage"], viol["example_obs"]); o = to_obs(d, viol["stage"])
            order = Order(*[x if x is not None else y for x, y in zip(d["message"], order.as_tuple())])
            a = pl.propose(state, o)
            assert a == viol["proposed"], "witness does not reproduce the proposal"
            assert a not in valid_actions(o.stage, o.effects, o.gate, o.closed_bay, order), "witness is not a real violation"
        # 2. random histories stay inside the reachable set
        reach = [set(int(c) for c in m.stage_codes[s]) for s in range(N_STAGES)]
        fails = 0
        for _ in range(3000):
            state = list(pl.blank); order = None
            for s in range(N_STAGES):
                e, g, c, dec = rng.choice(al.phys)
                msg = rng.choice([mm for mm in MSGS if None not in mm]) if s == 0 else rng.choice(MSGS)
                o = Obs(s, e, g, c, dec, *msg)
                order = Order(*[x if x is not None else y for x, y in zip(msg, order.as_tuple() if order else (0, 0, 0))])
                if s in STAGE_ACTIONS:
                    fails += pl.propose(state, o) not in valid_actions(s, e, g, c, order)
                state = pl.advance(state, o)
                assert int(pack(np.array([state]))[0]) in reach[s], "simulation reached a state the extractor missed"
        assert not (fails > 0 and m.n_bad() == 0), "simulation found a failure the extractor missed"
        print(f"family {f}: {m.checked:,} pairs checked, {m.n_bad():,} bad, {len(m.violations[:20])} witnesses reproduced, "
              f"3000 random histories: {fails} failing steps, all states inside the reachable set")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
