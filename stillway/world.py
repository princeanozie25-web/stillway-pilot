"""Dispatch-2: a deterministic two-station dispatch world.  This file is the SPEC.

Everything here is plain Python on purpose: it is the reference that the scorer
trusts.  The fast batched copy in vworld.py is tested against it.

Story of one episode
--------------------
A carrier leaves the depot with two parcels.
  leg 1: depot -> station 1 by route L or R      (irreversible)
  dock : hand parcel 1 to dock 0 or 1 at station 1
  leg 2: station 1 -> station 2 by route L or R  (irreversible)
  bay  : hand parcel 2 to bay 0, 1 or 2 at station 2
Each route has a trip that acts on ONE shared gate:
  K keep, T toggle, O force open (1), C force closed (0).
The downstream station needs the gate in a given state when the carrier arrives
after leg 2.  That need (the "gate obligation") is in the work order.

The work order = (dock for parcel 1, required gate state, bay for parcel 2).
Closed-book episodes show it once, at INIT.  After that it lives only in the
planner's saved memory.  Open-book episodes re-show it at every stage (this is
the "matched restart" condition: no memory is needed).

Stages:  0 INIT  1 PLAN  2 LEG1  3 DOCK  4 LEG2  5 BAY
Events can change the world before the observation of any stage >= 1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Optional, Sequence, Tuple

EFFECT_NAMES = "KTOC"
K, T, O, C = 0, 1, 2, 3
# EFF[effect][gate_before] -> gate_after
EFF = ((0, 1), (1, 0), (1, 1), (0, 0))

INIT, PLAN, LEG1, DOCK, LEG2, BAY = range(6)
STAGE_NAMES = ["INIT", "PLAN", "LEG1", "DOCK", "LEG2", "BAY"]
N_STAGES = 6

ACTIONS = ["L", "R", "D0", "D1", "B0", "B1", "B2"]
A_L, A_R, A_D0, A_D1, A_B0, A_B1, A_B2 = range(7)
N_ACTIONS = 7
STAGE_ACTIONS: Dict[int, Tuple[int, ...]] = {
    LEG1: (A_L, A_R),
    LEG2: (A_L, A_R),
    DOCK: (A_D0, A_D1),
    BAY: (A_B0, A_B1, A_B2),
}
NO_BAY = -1  # no bay closed

OBS_DIM = 37


# ----------------------------------------------------------------------------
# Work order and world state
# ----------------------------------------------------------------------------
@dataclass
class Order:
    dock: int            # 0/1   parcel 1 destination
    gate: Optional[int]  # 0/1   required gate state on arrival at station 2 (None = not instructed)
    bay: int             # 0..2  parcel 2 destination (the unrelated obligation)

    def copy(self) -> "Order":
        return Order(self.dock, self.gate, self.bay)

    def as_tuple(self):
        return (self.dock, self.gate, self.bay)


@dataclass
class Obs:
    """What a planner is allowed to see at one stage."""
    stage: int
    effects: Tuple[int, int, int, int]  # (leg1 L, leg1 R, leg2 L, leg2 R)
    gate: int
    closed_bay: int                     # NO_BAY or 0..2
    decor: int                          # 0..3, has no effect on anything
    msg_dock: Optional[int] = None      # work-order fields visible at this stage
    msg_gate: Optional[int] = None
    msg_bay: Optional[int] = None

    def vector(self) -> List[float]:
        v = [0.0] * OBS_DIM
        v[self.stage] = 1.0
        for i, e in enumerate(self.effects):
            v[6 + 4 * i + e] = 1.0
        v[22] = float(self.gate)
        v[23 + (self.closed_bay + 1)] = 1.0
        v[27] = float(self.decor & 1)
        v[28] = float((self.decor >> 1) & 1)
        if self.msg_dock is not None:
            v[29] = 1.0
            v[30] = float(self.msg_dock)
        if self.msg_gate is not None:
            v[31] = 1.0
            v[32] = float(self.msg_gate)
        if self.msg_bay is not None:
            v[33] = 1.0
            v[34 + self.msg_bay] = 1.0
        return v

    def to_json(self) -> dict:
        return {
            "stage": STAGE_NAMES[self.stage],
            "leg1": {"L": EFFECT_NAMES[self.effects[0]], "R": EFFECT_NAMES[self.effects[1]]},
            "leg2": {"L": EFFECT_NAMES[self.effects[2]], "R": EFFECT_NAMES[self.effects[3]]},
            "gate": self.gate,
            "closed_bay": None if self.closed_bay == NO_BAY else self.closed_bay,
            "decor": self.decor,
            "message": {"dock": self.msg_dock, "gate": self.msg_gate, "bay": self.msg_bay},
        }


# ----------------------------------------------------------------------------
# The exact planner (specification of correct behaviour)
# ----------------------------------------------------------------------------
def target_bay(bay: int, closed_bay: int) -> int:
    """Parcel 2 goes to its bay, or to the next bay round if that bay is closed."""
    return bay if bay != closed_bay else (bay + 1) % 3


def reachable_gates(stage: int, effects: Sequence[int], gate: int) -> set:
    """Gate states still reachable on arrival at station 2, from this stage."""
    if stage <= LEG1:
        return {EFF[effects[2 + r2]][EFF[effects[r1]][gate]] for r1 in (0, 1) for r2 in (0, 1)}
    if stage <= LEG2:
        return {EFF[effects[2 + r2]][gate] for r2 in (0, 1)}
    return {gate}


def valid_actions(stage: int, effects: Sequence[int], gate: int, closed_bay: int, order: Order) -> Tuple[int, ...]:
    """Set of correct actions at an action stage, given what is true NOW.

    The planner cannot foresee later events, so validity is judged against the
    current layout only.  If the gate obligation cannot be met any more (or was
    never instructed), every route is valid.
    """
    if stage == LEG1:
        if order.gate is None:
            return (A_L, A_R)
        ok = [r1 for r1 in (0, 1)
              if any(EFF[effects[2 + r2]][EFF[effects[r1]][gate]] == order.gate for r2 in (0, 1))]
        return tuple(ok) if ok else (A_L, A_R)
    if stage == LEG2:
        if order.gate is None:
            return (A_L, A_R)
        ok = [r2 for r2 in (0, 1) if EFF[effects[2 + r2]][gate] == order.gate]
        return tuple(ok) if ok else (A_L, A_R)
    if stage == DOCK:
        return (A_D0 + order.dock,)
    if stage == BAY:
        return (A_B0 + target_bay(order.bay, closed_bay),)
    return ()


def gate_decisive(stage: int, effects: Sequence[int], gate: int, order: Order) -> bool:
    """True when a wrong route at this stage would lose the gate obligation."""
    if stage not in (LEG1, LEG2) or order.gate is None:
        return False
    return len(valid_actions(stage, effects, gate, NO_BAY, order)) == 1


# ----------------------------------------------------------------------------
# Episodes (fixtures) and the simulator
# ----------------------------------------------------------------------------
@dataclass
class Episode:
    effects: Tuple[int, int, int, int]
    gate0: int
    order: Order
    decor: int = 0
    closed_bay: int = NO_BAY
    book: str = "closed"                 # "closed" or "open"
    # events[stage] = list of events applied before that stage's observation.
    #   ("rev", leg)          swap L and R wiring of leg 1 or 2
    #   ("gflip",)            an outside fault flips the gate
    #   ("decor", value)      repaint (no effect)
    #   ("close", bay|-1)     close a bay / reopen all
    #   ("msg", field, value) operator revises one work-order field ("dock"|"gate"|"bay")
    #   ("full",)             operator re-issues the whole current work order
    events: Dict[int, List[tuple]] = field(default_factory=dict)
    id: str = ""

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "family": family_of(self.effects),
            "layout": {
                "leg1": {"L": EFFECT_NAMES[self.effects[0]], "R": EFFECT_NAMES[self.effects[1]]},
                "leg2": {"L": EFFECT_NAMES[self.effects[2]], "R": EFFECT_NAMES[self.effects[3]]},
            },
            "gate0": self.gate0,
            "decor": self.decor,
            "closed_bay": None if self.closed_bay == NO_BAY else self.closed_bay,
            "order": {"dock": self.order.dock, "gate": self.order.gate, "bay": self.order.bay},
            "book": self.book,
            "events": [{"stage": STAGE_NAMES[s], "event": list(ev)} for s in sorted(self.events) for ev in self.events[s]],
        }

    @staticmethod
    def from_json(d: dict) -> "Episode":
        eff = tuple(EFFECT_NAMES.index(d["layout"][leg][r]) for leg in ("leg1", "leg2") for r in ("L", "R"))
        ev: Dict[int, List[tuple]] = {}
        for item in d.get("events", []):
            ev.setdefault(STAGE_NAMES.index(item["stage"]), []).append(tuple(item["event"]))
        o = d["order"]
        return Episode(eff, d["gate0"], Order(o["dock"], o["gate"], o["bay"]), d.get("decor", 0),
                       NO_BAY if d.get("closed_bay") is None else d["closed_bay"], d.get("book", "closed"), ev, d.get("id", ""))


class Sim:
    """Steps one episode.  Only the simulator applies actions."""

    def __init__(self, ep: Episode):
        self.ep = ep
        self.effects = list(ep.effects)
        self.gate = ep.gate0
        self.decor = ep.decor
        self.closed_bay = ep.closed_bay
        self.order = ep.order.copy()   # the operator's true current order
        self.stage = -1
        self.dock_done: Optional[int] = None
        self.bay_done: Optional[int] = None
        self.routes: List[int] = []

    def next_obs(self) -> Obs:
        """Advance to the next stage, apply its events, return the observation."""
        self.stage += 1
        s = self.stage
        md = mg = mb = None
        if s == INIT:
            md, mg, mb = self.order.dock, self.order.gate, self.order.bay
        for ev in self.ep.events.get(s, []):
            kind = ev[0]
            if kind == "rev":
                i = 0 if ev[1] == 1 else 2
                self.effects[i], self.effects[i + 1] = self.effects[i + 1], self.effects[i]
            elif kind == "gflip":
                self.gate = 1 - self.gate
            elif kind == "decor":
                self.decor = ev[1]
            elif kind == "close":
                self.closed_bay = ev[1]
            elif kind == "msg":
                if ev[1] == "dock":
                    self.order.dock = ev[2]; md = ev[2]
                elif ev[1] == "gate":
                    self.order.gate = ev[2]; mg = ev[2]
                elif ev[1] == "bay":
                    self.order.bay = ev[2]; mb = ev[2]
            elif kind == "full":
                md, mg, mb = self.order.dock, self.order.gate, self.order.bay
            else:
                raise ValueError(f"unknown event {ev}")
        if self.ep.book == "open":
            md, mg, mb = self.order.dock, self.order.gate, self.order.bay
        return Obs(s, tuple(self.effects), self.gate, self.closed_bay, self.decor, md, mg, mb)

    def valid(self) -> Tuple[int, ...]:
        return valid_actions(self.stage, self.effects, self.gate, self.closed_bay, self.order)

    def decisive(self) -> bool:
        return gate_decisive(self.stage, self.effects, self.gate, self.order)

    def apply(self, action: int) -> None:
        s = self.stage
        if s not in STAGE_ACTIONS:
            return
        if action not in STAGE_ACTIONS[s]:
            raise ValueError(f"action {action} is not allowed at stage {STAGE_NAMES[s]}")
        if s == LEG1:
            self.gate = EFF[self.effects[action]][self.gate]; self.routes.append(action)
        elif s == LEG2:
            self.gate = EFF[self.effects[2 + action]][self.gate]; self.routes.append(action)
        elif s == DOCK:
            self.dock_done = action - A_D0
        elif s == BAY:
            self.bay_done = action - A_B0


# ----------------------------------------------------------------------------
# Layout families (the unit that is held out)
# ----------------------------------------------------------------------------
def leg_type(a: int, b: int) -> str:
    lo, hi = min(a, b), max(a, b)
    return EFFECT_NAMES[lo] + EFFECT_NAMES[hi]


def family_of(effects: Sequence[int]) -> str:
    """Family = the mechanisms on each leg, ignoring which side they are wired to."""
    return leg_type(effects[0], effects[1]) + "-" + leg_type(effects[2], effects[3])


def is_normal(effects: Sequence[int]) -> bool:
    """Normal orientation: on each leg the lower effect letter is wired to L."""
    return effects[0] <= effects[1] and effects[2] <= effects[3]


def reverse(effects: Sequence[int], legs: Sequence[int]) -> Tuple[int, int, int, int]:
    e = list(effects)
    if 1 in legs:
        e[0], e[1] = e[1], e[0]
    if 2 in legs:
        e[2], e[3] = e[3], e[2]
    return tuple(e)


ALL_LAYOUTS: List[Tuple[int, int, int, int]] = [tuple(x) for x in product(range(4), repeat=4)]
ALL_FAMILIES: List[str] = sorted({family_of(e) for e in ALL_LAYOUTS})
ALL_ORDERS: List[Tuple[int, int, int]] = [(d, q, b) for d in (0, 1) for q in (0, 1) for b in (0, 1, 2)]


def gate_plans(effects: Sequence[int], gate0: int, q: int) -> set:
    """All (route1, route2) pairs that end with the gate in state q."""
    return {(r1, r2) for r1 in (0, 1) for r2 in (0, 1)
            if EFF[effects[2 + r2]][EFF[effects[r1]][gate0]] == q}
