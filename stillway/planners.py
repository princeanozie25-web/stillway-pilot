"""Hand-written planners: the reference solution and the impostors.

Every planner (hand-written or learned) exposes the same four operations:

    init(obs)            -> state      start from a work order
    advance(state, obs)  -> state      one planning step
    propose(state, obs)  -> action     what it would do now (stage must be an action stage)
    save(state) / restore(blob)        state is a short list of integers

The protocol at stage s is:  action = propose(state_{s-1}, obs_s);  state_s = advance(state_{s-1}, obs_s).
State is ONLY a list of small integers ("slots").  Nothing else may carry over.
"""
from __future__ import annotations

from typing import List, Sequence

from .world import (A_B0, A_D0, A_L, A_R, ALL_ORDERS, BAY, DOCK, EFF, INIT, LEG1, LEG2, NO_BAY, Obs, Order,
                    STAGE_ACTIONS, target_bay, valid_actions)

State = List[int]


class Planner:
    name = "planner"
    n_slots = 0
    blank: State = []

    def init(self, obs: Obs) -> State:
        return self.advance(list(self.blank), obs)

    def advance(self, state: State, obs: Obs) -> State:
        raise NotImplementedError

    def propose(self, state: State, obs: Obs) -> int:
        raise NotImplementedError

    def save(self, state: State) -> List[int]:
        return [int(x) for x in state]

    def restore(self, blob: Sequence[int]) -> State:
        return [int(x) for x in blob]


def _first(actions) -> int:
    return min(actions)


class Reference(Planner):
    """Exact planner with a symbolic memory of the work order: slots = [dock, gate, bay].

    This is also the 'human-defined symbolic scratchpad' baseline.  -1 means unknown.
    """
    name = "reference"
    n_slots = 3
    blank = [-1, -1, -1]

    def advance(self, state, obs):
        d, q, b = state
        if obs.msg_dock is not None: d = obs.msg_dock
        if obs.msg_gate is not None: q = obs.msg_gate
        if obs.msg_bay is not None: b = obs.msg_bay
        return [d, q, b]

    def propose(self, state, obs):
        d, q, b = self.advance(state, obs)
        order = Order(max(d, 0), None if q < 0 else q, max(b, 0))
        return _first(valid_actions(obs.stage, obs.effects, obs.gate, obs.closed_bay, order))


class LookupLR(Planner):
    """Impostor 1.  Remembers the order perfectly but is blind to which SIDE each trip is wired to.

    It plans as if every leg were in normal orientation (lower effect letter on L),
    i.e. a left/right lookup table learned on normal layouts.
    """
    name = "impostor_lookup_lr"
    n_slots = 3
    blank = [-1, -1, -1]

    def advance(self, state, obs):
        return Reference.advance(self, state, obs)

    def propose(self, state, obs):
        d, q, b = self.advance(state, obs)
        e = obs.effects
        blind = (min(e[0], e[1]), max(e[0], e[1]), min(e[2], e[3]), max(e[2], e[3]))
        order = Order(max(d, 0), None if q < 0 else q, max(b, 0))
        return _first(valid_actions(obs.stage, blind, obs.gate, obs.closed_bay, order))


class Memoryless(Planner):
    """Impostor 2.  Recomputes from the latest observation only.  Carries nothing.

    If the observation shows a work-order field it uses it.  For a field it cannot
    see, it takes the action that is valid for the most possible orders (the best
    any memoryless planner can do).  If this impostor passes a closed-book test,
    the instruction is leaking through the observations.
    """
    name = "impostor_memoryless"
    n_slots = 1
    blank = [0]

    def advance(self, state, obs):
        return [0]

    def propose(self, state, obs):
        votes = {a: 0 for a in STAGE_ACTIONS[obs.stage]}
        for (d, q, b) in ALL_ORDERS:
            if obs.msg_dock is not None and d != obs.msg_dock: continue
            if obs.msg_gate is not None and q != obs.msg_gate: continue
            if obs.msg_bay is not None and b != obs.msg_bay: continue
            for a in valid_actions(obs.stage, obs.effects, obs.gate, obs.closed_bay, Order(d, q, b)):
                votes[a] += 1
        best = max(votes.values())
        return _first([a for a, v in votes.items() if v == best])


class PlanCache(Planner):
    """Impostor 3.  Compiles a full plan when it sees a whole work order and replays it blind.

    Memory = the compiled plan, not the obligation: slots = [route1, route2, dock, bay].
    It models 'plan-coded' memory.  It is right whenever the world stays as it was
    when the plan was compiled, and wrong after a wiring reversal or a gate fault.
    A swap of its route slots transplants the donor's ROUTES, not the donor's goal.
    """
    name = "impostor_plan_cache"
    n_slots = 4
    blank = [0, 0, 0, 0]

    def advance(self, state, obs):
        r1, r2, d, b = state
        if obs.msg_dock is not None: d = obs.msg_dock
        if obs.msg_bay is not None: b = obs.msg_bay
        if obs.msg_gate is not None:
            q, e, g = obs.msg_gate, obs.effects, obs.gate
            if obs.stage <= LEG1:
                plans = [(a, c) for a in (0, 1) for c in (0, 1) if EFF[e[2 + c]][EFF[e[a]][g]] == q]
                if plans: r1, r2 = plans[0]
            elif obs.stage <= LEG2:
                ok = [c for c in (0, 1) if EFF[e[2 + c]][g] == q]
                if ok: r2 = ok[0]
        return [r1, r2, d, b]

    def propose(self, state, obs):
        r1, r2, d, b = self.advance(state, obs)
        if obs.stage == LEG1: return A_L + r1
        if obs.stage == LEG2: return A_L + r2
        if obs.stage == DOCK: return A_D0 + d
        return A_B0 + target_bay(b, obs.closed_bay)


class Entangled(Planner):
    """Impostor 4.  Correct behaviour, but the whole order is packed into ONE slot.

    Any swap of 'the relevant part of memory' moves the whole order, so the
    unrelated obligation is damaged.  It models entangled plan memory.
    """
    name = "impostor_entangled"
    n_slots = 1
    blank = [-1]

    @staticmethod
    def _unpack(x):
        return [-1, -1, -1] if x < 0 else [x // 6, (x // 3) % 2, x % 3]

    def advance(self, state, obs):
        d, q, b = Reference.advance(self, self._unpack(state[0]), obs)
        if min(d, q, b) < 0:
            return [-1]
        return [d * 6 + q * 3 + b]

    def propose(self, state, obs):
        return Reference().propose(self._unpack(state[0]), obs)


HAND_PLANNERS = {p.name: p for p in (Reference(), LookupLR(), Memoryless(), PlanCache(), Entangled())}
