"""Batched copy of the Dispatch-2 world for training and bulk evaluation (torch).

world.py is the spec.  tests/test_vworld.py checks this file against it.
"""
from __future__ import annotations

from typing import Dict, Optional

import torch

from .world import BAY, DOCK, INIT, LEG1, LEG2, N_ACTIONS, OBS_DIM

EFF_T = torch.tensor([[0, 1], [1, 0], [1, 1], [0, 0]])

PROFILES: Dict[str, dict] = {
    # everything can change mid-plan; routes taken at random so the planner sees off-plan gates
    "dynamic": dict(rev=0.10, gflip=0.10, decor=0.20, close=0.10, msg=0.15, full=0.05, open=0.10, env="random"),
    # wiring can change, the gate never faults, the carrier follows valid routes
    "wiring": dict(rev=0.10, gflip=0.0, decor=0.20, close=0.10, msg=0.15, full=0.05, open=0.10, env="expert"),
    # the physical world never changes after INIT and the carrier follows valid routes
    "static": dict(rev=0.0, gflip=0.0, decor=0.20, close=0.10, msg=0.15, full=0.05, open=0.10, env="expert"),
    # the certificate's own distribution: at every stage any re-wiring, gate, closure, repaint and message
    "stress": dict(rev=0.5, gflip=0.5, decor=0.75, close=0.75, msg=0.35, full=0.10, reissue=0.5, open=0.0, env="random"),
    # the same, but mostly single-field revisions, so long chains of small revisions are common
    "stress2": dict(rev=0.5, gflip=0.5, decor=0.75, close=0.75, msg=0.5, full=0.05, reissue=0.15, open=0.0, env="random"),
    # nothing at all happens after INIT (bulk evaluation of plain closed-book episodes)
    "plain": dict(rev=0.0, gflip=0.0, decor=0.0, close=0.0, msg=0.0, full=0.0, open=0.0, env="model"),
    "plain_dynamic": dict(rev=0.10, gflip=0.10, decor=0.20, close=0.10, msg=0.15, full=0.05, open=0.0, env="model"),
}


class VWorld:
    def __init__(self, layouts: torch.Tensor, batch: int, profile: dict, gen: torch.Generator,
                 instructed: bool = True):
        self.layouts, self.B, self.p, self.gen, self.instructed = layouts, batch, profile, gen, instructed
        self.reset()

    def _rand(self, n=None):
        return torch.rand(self.B if n is None else n, generator=self.gen)

    def _randint(self, hi):
        return torch.randint(0, hi, (self.B,), generator=self.gen)

    def reset(self):
        B = self.B
        idx = torch.randint(0, self.layouts.shape[0], (B,), generator=self.gen)
        self.eff = self.layouts[idx].clone()
        self.gate = self._randint(2)
        self.decor = self._randint(4)
        self.decor0 = self.decor.clone()
        self.closed = torch.where(self._rand() < 0.25, self._randint(3), torch.full((B,), -1))
        self.d, self.q, self.b = self._randint(2), self._randint(2), self._randint(3)
        self.open = self._rand() < self.p["open"]
        self.stage = -1

    def next_obs(self) -> torch.Tensor:
        self.stage += 1
        s, B, p = self.stage, self.B, self.p
        md = torch.zeros(B, dtype=torch.bool); mq = md.clone(); mb = md.clone()
        if s == INIT:
            md[:] = True; mq[:] = True; mb[:] = True
        else:
            for leg in (0, 1):
                m = self._rand() < p["rev"]
                i = 2 * leg
                a, b = self.eff[:, i].clone(), self.eff[:, i + 1].clone()
                self.eff[:, i] = torch.where(m, b, a)
                self.eff[:, i + 1] = torch.where(m, a, b)
            m = self._rand() < p["gflip"]
            self.gate = torch.where(m, 1 - self.gate, self.gate)
            m = self._rand() < p["decor"]
            self.decor = torch.where(m, self._randint(4), self.decor)
            m = self._rand() < p["close"]
            self.closed = torch.where(m, self._randint(4) - 1, self.closed)
            m = self._rand() < p["msg"]
            f = self._randint(3)
            m_d, m_q, m_b = m & (f == 0), m & (f == 1), m & (f == 2)
            self.d = torch.where(m_d, self._randint(2), self.d)
            self.q = torch.where(m_q, self._randint(2), self.q)
            self.b = torch.where(m_b, self._randint(3), self.b)
            re = self._rand() < p.get("reissue", 0.0)          # operator re-issues a wholly new order
            self.d = torch.where(re, self._randint(2), self.d)
            self.q = torch.where(re, self._randint(2), self.q)
            self.b = torch.where(re, self._randint(3), self.b)
            full = (self._rand() < p["full"]) | self.open | re
            md, mq, mb = m_d | full, m_q | full, m_b | full
        if not self.instructed:
            mq[:] = False
        obs = torch.zeros(B, OBS_DIM)
        ar = torch.arange(B)
        obs[:, s] = 1.0
        for i in range(4):
            obs[ar, 6 + 4 * i + self.eff[:, i]] = 1.0
        obs[:, 22] = self.gate.float()
        obs[ar, 23 + self.closed + 1] = 1.0
        obs[:, 27] = (self.decor & 1).float()
        obs[:, 28] = ((self.decor >> 1) & 1).float()
        obs[:, 29] = md.float(); obs[:, 30] = (md * self.d).float()
        obs[:, 31] = mq.float(); obs[:, 32] = (mq * self.q).float()
        obs[:, 33] = mb.float()
        obs[ar[mb], 34 + self.b[mb]] = 1.0
        return obs

    def route_ok(self):
        """(B,2) bool: would route r at the current leg still allow the gate obligation?"""
        s, g, q, e = self.stage, self.gate, self.q, self.eff
        if s == LEG1:
            ok = []
            for r1 in (0, 1):
                g1 = EFF_T[e[:, r1], g]
                ok.append((EFF_T[e[:, 2], g1] == q) | (EFF_T[e[:, 3], g1] == q))
            return torch.stack(ok, 1)
        return torch.stack([EFF_T[e[:, 2], g] == q, EFF_T[e[:, 3], g] == q], 1)

    def valid_mask(self) -> torch.Tensor:
        s, B = self.stage, self.B
        v = torch.zeros(B, N_ACTIONS, dtype=torch.bool)
        ar = torch.arange(B)
        if s in (LEG1, LEG2):
            ok = self.route_ok()
            none = ~ok.any(1)
            ok = ok | none[:, None]
            if not self.instructed:
                ok[:] = True
            v[:, 0:2] = ok
        elif s == DOCK:
            v[ar, 2 + self.d] = True
        elif s == BAY:
            tb = torch.where(self.b == self.closed, (self.b + 1) % 3, self.b)
            v[ar, 4 + tb] = True
        return v

    def stage_mask(self) -> torch.Tensor:
        s = self.stage
        m = torch.zeros(N_ACTIONS, dtype=torch.bool)
        if s in (LEG1, LEG2): m[0:2] = True
        elif s == DOCK: m[2:4] = True
        elif s == BAY: m[4:7] = True
        return m

    def env_action(self, model_action: Optional[torch.Tensor], valid: torch.Tensor) -> torch.Tensor:
        """Which action the simulator applies (training only uses random / expert)."""
        mode = self.p["env"]
        if mode == "model":
            return model_action
        sm = self.stage_mask()
        w = (valid if mode == "expert" else sm[None, :].expand(self.B, -1)).float()
        return torch.multinomial(w, 1, generator=self.gen).squeeze(1)

    def apply(self, action: torch.Tensor):
        s = self.stage
        if s == LEG1:
            self.gate = EFF_T[self.eff[torch.arange(self.B), action], self.gate]
        elif s == LEG2:
            self.gate = EFF_T[self.eff[torch.arange(self.B), 2 + action], self.gate]
            self.gate_arrival = self.gate.clone()
