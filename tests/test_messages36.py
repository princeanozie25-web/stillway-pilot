"""M1 coverage tests: every operator-message mask and value, built as simulator events.

For each of the 36 patterns (dock in {absent,0,1} x gate in {absent,0,1} x bay in {absent,0,1,2}), at each
stage from PLAN to BAY, this test builds the events, steps the simulator, and checks
  1. the observation shows exactly the revised fields with the new values,
  2. the operator's current order is the old order with those fields replaced,
  3. the extractor's 36-pattern alphabet contains that exact encoded observation, with the same order update.
It also covers: repeated writes to one field in one stage (last wins), a full reissue followed by an
override, an override followed by a full reissue, and closed-bay handling of the parcel-2 target.
"""
import itertools, torch
from stillway.world import *
from stillway2.automaton import Alphabet, MSGS20, MSGS36, ORDER_INDEX

LAY = (K, T, O, C)

def events_for(msg, order_before):
    d, q, b = msg
    ev = []
    if d is not None: ev.append(("msg", "dock", d))
    if q is not None: ev.append(("msg", "gate", q))
    if b is not None: ev.append(("msg", "bay", b))
    return ev

def test_all_36_patterns():
    assert len(MSGS36) == 36 and len(set(MSGS36)) == 36 and set(MSGS20) < set(MSGS36)
    assert sum(1 for m in MSGS36 if sum(x is not None for x in m) == 2) == 16     # the 16 patterns v0.1 missed
    al = Alphabet([LAY], MSGS36); n = 0
    for stage in range(1, 6):
        obs_table = al.obs(stage)
        for msg in MSGS36:
            for start in ALL_ORDERS:
                for closed in (NO_BAY, 0, 1, 2):
                    ep = Episode(LAY, 1, Order(*start), 2, closed, "closed", {stage: events_for(msg, start)})
                    sim = Sim(ep)
                    for s in range(stage + 1): obs = sim.next_obs()
                    want = tuple(m if m is not None else o for m, o in zip(msg, start))
                    assert sim.order.as_tuple() == want
                    assert (obs.msg_dock, obs.msg_gate, obs.msg_bay) == msg
                    # the same observation must be a row of the extractor's alphabet, with the same order update
                    pi = al.phys.index((obs.effects, obs.gate, obs.closed_bay, obs.decor)); mi = al.msgs.index(msg)
                    assert obs_table[pi * al.M + mi].tolist() == obs.vector()
                    assert al.new_order[ORDER_INDEX[start], mi] == ORDER_INDEX[want]
                    if stage == BAY:
                        assert sim.valid() == (A_B0 + target_bay(want[2], closed),)
                    n += 1
    return n

def test_repeated_and_reissue():
    base = Order(0, 0, 0)
    # repeated writes to one field in one stage: the last one wins and is the one shown
    sim = Sim(Episode(LAY, 0, base.copy(), events={1: [("msg", "bay", 1), ("msg", "bay", 2)]})); sim.next_obs(); o = sim.next_obs()
    assert sim.order.bay == 2 and (o.msg_dock, o.msg_gate, o.msg_bay) == (None, None, 2)
    # a full reissue followed by an override: all three shown, with the overriding value
    sim = Sim(Episode(LAY, 0, base.copy(), events={1: [("full",), ("msg", "gate", 1)]})); sim.next_obs(); o = sim.next_obs()
    assert sim.order.as_tuple() == (0, 1, 0) and (o.msg_dock, o.msg_gate, o.msg_bay) == (0, 1, 0)
    # an override followed by a full reissue: same observation
    sim = Sim(Episode(LAY, 0, base.copy(), events={1: [("msg", "gate", 1), ("full",)]})); sim.next_obs(); o2 = sim.next_obs()
    assert o2.vector() == o.vector()
    # revisions at two different stages accumulate
    sim = Sim(Episode(LAY, 0, base.copy(), events={1: [("msg", "dock", 1)], 2: [("msg", "bay", 2), ("msg", "gate", 1)]}))
    for _ in range(3): o = sim.next_obs()
    assert sim.order.as_tuple() == (1, 1, 2) and (o.msg_dock, o.msg_gate, o.msg_bay) == (None, 1, 2)
    # closed bay: parcel 2 goes to the next bay round, also right after a bay revision
    for b, c in itertools.product(range(3), (NO_BAY, 0, 1, 2)):
        sim = Sim(Episode(LAY, 0, base.copy(), events={5: [("close", c), ("msg", "bay", b)]}))
        for _ in range(6): sim.next_obs()
        assert sim.valid() == (A_B0 + (b if b != c else (b + 1) % 3),)

if __name__ == "__main__":
    n = test_all_36_patterns(); test_repeated_and_reissue()
    print(f"36 patterns x 5 stages x 12 starting orders x 4 closed-bay states = {n} simulator episodes checked against the alphabet; special cases pass")
