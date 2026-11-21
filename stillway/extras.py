"""Things a discrete state makes possible, built on the extracted machines.

  Dictionary        every reachable code state -> what it means (which work orders it stands for)
  typed_patch       write a correction straight into saved memory: decode, change one field, re-encode
  CanonicalPlanner  'quotient memory': after every step, replace the state by the one
                    representative of its class, so anything that never matters is erased
  membership        a state that is not in the certified reachable set raises an alarm
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Sequence

from .automaton import pack, relevant_key, unpack
from .model import NeuralPlanner
from .planners import Planner
from .world import ALL_ORDERS, Episode, Obs, STAGE_NAMES, family_of

import numpy as np


class Dictionary:
    def __init__(self, path: str, n_slots: int):
        self.d = json.load(open(path))          # family -> [stage] -> {packed: [meaning, spec_rep, beh_rep]}
        self.S = n_slots
        self.encode: Dict[tuple, int] = {}      # (family, stage, meaning) -> representative packed code
        for f, stages in self.d.items():
            for st, table in enumerate(stages):
                for packed, (meaning, spec_rep, beh_rep) in table.items():
                    if meaning is not None:
                        self.encode.setdefault((f, st, tuple(meaning)), spec_rep)

    @staticmethod
    def _p(state: Sequence[int]) -> str:
        return str(int(pack(np.array([state]))[0]))

    def lookup(self, family: str, stage: int, state: Sequence[int]):
        return self.d.get(family, [{}] * 6)[stage].get(self._p(state))

    def known(self, family, stage, state) -> bool:
        return self.lookup(family, stage, state) is not None

    def meaning(self, family, stage, state) -> Optional[tuple]:
        e = self.lookup(family, stage, state)
        return None if e is None or e[0] is None else tuple(e[0])

    def canon(self, family, stage, state, kind: str) -> Optional[List[int]]:
        e = self.lookup(family, stage, state)
        if e is None:
            return None
        rep = e[1] if kind == "spec" else e[2]
        return None if rep is None else unpack(int(rep), self.S)

    def patch(self, family: str, stage: int, state: Sequence[int], field: str, value: int) -> Optional[List[int]]:
        """Typed edit of saved memory.  Only defined while all three fields are still in memory (stage <= LEG1)."""
        m = self.meaning(family, stage, state)
        if m is None or len(m) != 3:
            return None
        m = list(m)
        m[{"dock": 0, "gate": 1, "bay": 2}[field]] = value
        rep = self.encode.get((family, stage, tuple(m)))
        return None if rep is None else unpack(int(rep), self.S)


class CanonicalPlanner(Planner):
    """Quotient memory.  kind='spec': one state per meaning.  kind='behaviour': one state per bisimulation class."""

    def __init__(self, base: NeuralPlanner, dic: Dictionary, kind: str = "spec"):
        self.base, self.dic, self.kind = base, dic, kind
        self.name = base.name + "+quotient_" + kind
        self.n_slots, self.blank = base.n_slots, base.blank
        self.unknown = 0
        self.steps = 0

    def advance(self, state, obs: Obs):
        new = self.base.advance(state, obs)
        self.steps += 1
        c = self.dic.canon(family_of(obs.effects), obs.stage, new, self.kind)
        if c is None:
            self.unknown += 1          # outside the certified set: alarm, leave the state as it is
            return new
        return c

    def propose(self, state, obs):
        return self.base.propose(state, obs)
