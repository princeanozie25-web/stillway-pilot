"""Dispatch-3 for any number of legs (v0.3).  Same rules as stillway2/world3.py, which stays frozen.

What changes against world3.py
  * `lmax` is a parameter of the world (world3.py fixes it at 4).  The frame, the order (2 gate fields and
    one parcel field per station) and the observation grow with it.
  * The exact planner uses its value table (4 joint gate states per leg) in place of listing every remaining
    route choice, so long jobs stay cheap.  tests/test_world_n.py checks it against world3.py (lmax = 4, same
    random draws, every observation and every valid set equal) and against the plain-Python reference
    that lists every route choice (up to 10 legs).

Observation layout (width 20 + 18 * lmax; equal to world3.py at lmax = 4):
  [0:4] slot kind   [4:4+lmax] which leg the slot is about   [+2] gates   [+4] closed bay   [+2] paint
  then 4 numbers per order field (present, value one-hot), then 13 numbers per leg
  (exists, travelled, has parcel, route 0: trip one-hot + gate, route 1: trip one-hot + gate).
"""
from __future__ import annotations

from typing import Optional

import torch

from stillway2.world3 import EFF_T, INIT, WAIT, ROUTE, DELIVER, N_ACT, LEGDIM, _mix, _mix_t, _u_mod100

JOINT = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]])            # joint gate states, index = gate0 * 2 + gate1


def obs_width(lmax: int) -> int:
    return 20 + 18 * lmax


def lmax_of(width: int) -> int:
    assert (width - 20) % 18 == 0
    return (width - 20) // 18


def layout(lmax: int) -> dict:
    """Column offsets of the observation."""
    nf = 2 + lmax
    return {"leg": 4, "gates": 4 + lmax, "closed": 6 + lmax, "paint": 10 + lmax, "fields": 12 + lmax, "nf": nf,
            "legs": 12 + lmax + 4 * nf, "width": obs_width(lmax)}


def bucket_n(L, eff, tg, parcel, salt: int = 20261121) -> torch.Tensor:
    """Family bucket 0..99.  Equal to world3.bucket_t for jobs of up to 4 legs."""
    lmax = eff.shape[1]; key = L.clone().long()
    for i in range(lmax):
        a, b = eff[:, i, 0] * 2 + tg[:, i, 0], eff[:, i, 1] * 2 + tg[:, i, 1]
        pair = torch.minimum(a, b) * 8 + torch.maximum(a, b)
        ex = i < L
        key = torch.where(ex, (key * 64 + pair) * 2 + parcel[:, i].long(), key * 128 if i < 4 else key)
    s = _mix(salt); s = s - (1 << 64) if s >= (1 << 63) else s
    return _u_mod100(_mix_t(key ^ torch.tensor(s)))


class WorldN:
    def __init__(self, batch: int, spec: dict, gen: torch.Generator, lmax: int = 4):
        self.B, self.s, self.gen, self.lmax = batch, dict(spec), gen, lmax
        self.NF = 2 + lmax; self.lay = layout(lmax)
        self.K = self.s["K"]; self.T = 1 + lmax * (self.K + 2)
        self.reset()

    def _r(self, *shape): return torch.rand(*shape, generator=self.gen)
    def _ri(self, hi, *shape): return torch.randint(0, hi, shape, generator=self.gen)

    def _sample_layout(self, n):
        s, M = self.s, self.lmax
        Lc = torch.tensor(s["L"]); L = Lc[self._ri(len(Lc), n)]
        eff = self._ri(4, n, M, 2); g = self._ri(2, n, M)
        cross = self._r(n, M) < s["cross"]
        tg = torch.stack([g, torch.where(cross, 1 - g, g)], -1)
        if s.get("force_cross"):
            j = (self._r(n) * L).long().clamp(max=M - 1)
            tg[torch.arange(n), j, 1] = 1 - tg[torch.arange(n), j, 0]
        ex = torch.arange(M)[None, :] < L[:, None]
        parcel = (self._r(n, M) < 0.6) & ex
        return L, eff, tg, parcel

    def reset(self):
        B, s, M = self.B, self.s, self.lmax
        L, eff, tg, parcel = self._sample_layout(B)
        if s["split"] is not None:
            lo, hi = {"train": (0, 60), "dev": (60, 70), "final": (70, 100)}[s["split"]]
            for _ in range(2000):
                b = bucket_n(L, eff, tg, parcel); bad = (b < lo) | (b >= hi)
                if not bad.any(): break
                L2, e2, t2, p2 = self._sample_layout(B)
                L = torch.where(bad, L2, L); eff = torch.where(bad[:, None, None], e2, eff)
                tg = torch.where(bad[:, None, None], t2, tg); parcel = torch.where(bad[:, None], p2, parcel)
            assert not bad.any()
        self.L, self.eff, self.tg, self.parcel = L, eff, tg, parcel
        self.gates = self._ri(2, B, 2)
        self.decor = self._ri(4, B); self.decor0 = self.decor.clone()
        self.closed = torch.where(self._r(B) < 0.25, self._ri(3, B), torch.full((B,), -1))
        qn = self._r(B, 2) < 0.25
        self.q = torch.where(qn, torch.zeros(B, 2, dtype=torch.long), 1 + self._ri(2, B, 2))
        self.p = self._ri(3, B, M)
        self.wait_on = self._r(B, M, max(1, self.K)) < s["p_wait"]
        self.cur = torch.zeros(B, dtype=torch.long); self.t = -1
        self.delivered = torch.full((B, M), -1); self.deliver_ok = torch.ones(B, M, dtype=torch.bool)

    def slot(self, t: int):
        if t == 0: return INIT, 0
        leg, pos = divmod(t - 1, self.K + 2)
        return (WAIT if pos < self.K else (ROUTE if pos == self.K else DELIVER)), leg

    def active(self, t: int) -> torch.Tensor:
        kind, leg = self.slot(t)
        if kind == INIT: return torch.ones(self.B, dtype=torch.bool)
        ex = leg < self.L
        if kind == WAIT: return ex & self.wait_on[:, leg, (t - 1) % (self.K + 2)]
        if kind == ROUTE: return ex
        return ex & self.parcel[:, leg]

    def next_obs(self, script: Optional[dict] = None):
        self.t += 1
        t, B, s, M, NF, lay = self.t, self.B, self.s, self.lmax, self.NF, self.lay
        kind, leg = self.slot(t); act = self.active(t); ar = torch.arange(B)
        has = torch.zeros(B, NF, dtype=torch.bool)
        if kind == INIT:
            has[:] = True
        else:
            m = act & (self._r(B) < s["rev"]) & (self.cur < self.L)
            j = (self.cur + (self._r(B) * (self.L - self.cur).clamp(min=1)).long()).clamp(max=M - 1)
            sw = torch.zeros(B, M, dtype=torch.bool); sw[ar[m], j[m]] = True
            self.eff = torch.where(sw[:, :, None], self.eff.flip(-1), self.eff)
            self.tg = torch.where(sw[:, :, None], self.tg.flip(-1), self.tg)
            for g in (0, 1):
                m = act & (self._r(B) < s["gflip"])
                self.gates[:, g] = torch.where(m, 1 - self.gates[:, g], self.gates[:, g])
            m = act & (self._r(B) < s["decor"]); self.decor = torch.where(m, self._ri(4, B), self.decor)
            m = act & (self._r(B) < s["close"]); self.closed = torch.where(m, self._ri(4, B) - 1, self.closed)
            m = act & (self._r(B) < s["msg"]); f = self._ri(NF, B); v = self._ri(3, B)
            re = act & (self._r(B) < s["reissue"])
            if re.any():
                qn = self._r(B, 2) < 0.25
                self.q = torch.where(re[:, None], torch.where(qn, torch.zeros(B, 2, dtype=torch.long), 1 + self._ri(2, B, 2)), self.q)
                self.p = torch.where(re[:, None], self._ri(3, B, M), self.p)
            show = m.clone()
            if script is not None:
                rows = script["rows"] & act
                m = torch.where(rows, torch.ones_like(m), m); f = torch.where(rows, script["field"], f); v = torch.where(rows, script["value"], v)
                show = torch.where(rows, torch.full_like(m, bool(script.get("show", True))), show)
            for k in range(NF):
                mk = m & (f == k)
                if k < 2: self.q[:, k] = torch.where(mk, v, self.q[:, k])
                else: self.p[:, k - 2] = torch.where(mk, v, self.p[:, k - 2])
                has[:, k] = mk & show
            if s.get("noop_msg", 0) > 0:
                mn = act & (self._r(B) < s["noop_msg"]); fn = self._ri(NF, B)
                has[ar[mn], fn[mn]] = True
            full = act & ((self._r(B) < s["full"]) | re)
            if script is not None and script.get("full_rows") is not None:
                full = full | (script["full_rows"] & act)
            has = has | full[:, None]
        obs = torch.zeros(B, lay["width"])
        obs[:, kind] = 1.0
        obs[ar, 4 + (torch.full((B,), leg) if kind in (ROUTE, DELIVER) else self.cur.clamp(max=M - 1))] = 1.0
        obs[:, lay["gates"]:lay["gates"] + 2] = self.gates.float()
        obs[ar, lay["closed"] + self.closed + 1] = 1.0
        obs[:, lay["paint"]] = (self.decor & 1).float(); obs[:, lay["paint"] + 1] = ((self.decor >> 1) & 1).float()
        vals = torch.cat([self.q, self.p], 1); F0 = lay["fields"]
        for k in range(NF):
            obs[:, F0 + 4 * k] = has[:, k].float()
            obs[ar[has[:, k]], F0 + 4 * k + 1 + vals[has[:, k], k]] = 1.0
        for i in range(M):
            o = lay["legs"] + LEGDIM * i; ex = i < self.L
            obs[:, o] = ex.float(); obs[:, o + 1] = (i < self.cur).float(); obs[:, o + 2] = self.parcel[:, i].float()
            for r in (0, 1):
                obs[ar, o + 3 + 5 * r + self.eff[:, i, r]] = 1.0
                obs[:, o + 3 + 5 * r + 4] = self.tg[:, i, r].float()
            obs[~ex, o + 1:o + LEGDIM] = 0.0
        return obs, act

    # -- exact planner ---------------------------------------------------------------------------------
    def terminal_table(self) -> torch.Tensor:
        """(B,4): gate requirements met if the job ended with the gates in each joint state."""
        return ((self.q[:, None, :] > 0) & (JOINT[None] == self.q[:, None, :] - 1)).sum(2)

    def _next_state(self, i: int, r: int) -> torch.Tensor:
        """(B,4): joint gate state after taking route r of leg i from each joint state."""
        B = self.B; e = self.eff[:, i, r][:, None].expand(B, 4); tgt = self.tg[:, i, r][:, None].expand(B, 4)
        gs = JOINT[None].expand(B, 4, 2); cur_g = gs.gather(2, tgt[:, :, None]).squeeze(2)
        ng = gs.scatter(2, tgt[:, :, None], EFF_T[e, cur_g][:, :, None])
        return ng[:, :, 0] * 2 + ng[:, :, 1]

    def dp_tables(self) -> torch.Tensor:
        """(B, lmax+1, 4): entry [i, s] = most gate requirements that can be met at the end when standing
        before leg i with the gates in joint state s.  Entry [lmax] (and every i >= L) is the terminal table."""
        V = self.terminal_table(); out = torch.zeros(self.B, self.lmax + 1, 4, dtype=torch.long); out[:, self.lmax] = V
        for i in range(self.lmax - 1, -1, -1):
            ex = (i < self.L)[:, None]
            cand = [V.gather(1, self._next_state(i, r)) for r in (0, 1)]
            V = torch.where(ex, torch.maximum(cand[0], cand[1]), V); out[:, i] = V
        return out

    def best_counts(self) -> torch.Tensor:
        """(B,2): for each route of the current leg, the most gate requirements that can still be met."""
        B, ar = self.B, torch.arange(self.B); dp = self.dp_tables(); c = self.cur.clamp(max=self.lmax - 1)
        s = self.gates[:, 0] * 2 + self.gates[:, 1]; out = []
        for r in (0, 1):
            e = self.eff[ar, c, r]; tgt = self.tg[ar, c, r]; g = self.gates.clone()
            g[ar, tgt] = EFF_T[e, g[ar, tgt]]
            out.append(dp[ar, c + 1, g[:, 0] * 2 + g[:, 1]])
        best = torch.stack(out, 1)
        done = self.cur >= self.L
        return torch.where(done[:, None], dp[ar, self.lmax, s][:, None].expand(B, 2), best)

    def valid_mask(self) -> torch.Tensor:
        kind, leg = self.slot(self.t); v = torch.zeros(self.B, N_ACT, dtype=torch.bool)
        if kind == ROUTE:
            b = self.best_counts(); v[:, 0:2] = b == b.max(1, keepdim=True).values
        elif kind == DELIVER:
            d = self.p[:, leg]; d = torch.where(d == self.closed, (d + 1) % 3, d)
            v[torch.arange(self.B), 2 + d] = True
        return v

    def stage_mask(self) -> torch.Tensor:
        kind, _ = self.slot(self.t); m = torch.zeros(N_ACT, dtype=torch.bool)
        if kind == ROUTE: m[0:2] = True
        elif kind == DELIVER: m[2:5] = True
        return m

    def env_action(self, valid: torch.Tensor) -> torch.Tensor:
        w = (valid if self.s["env"] == "expert" else self.stage_mask()[None, :].expand(self.B, -1)).float()
        return torch.multinomial(w, 1, generator=self.gen).squeeze(1)

    def apply(self, action: torch.Tensor, act: torch.Tensor):
        kind, leg = self.slot(self.t); ar = torch.arange(self.B)
        if kind == ROUTE:
            r = action.clamp(0, 1); e = self.eff[ar, leg, r]; tgt = self.tg[ar, leg, r]
            new = EFF_T[e, self.gates[ar, tgt]]
            self.gates[ar, tgt] = torch.where(act, new, self.gates[ar, tgt])
            self.cur = torch.where(act, self.cur + 1, self.cur)
        elif kind == DELIVER:
            d = (action - 2).clamp(0, 2)
            want = self.p[:, leg]; want = torch.where(want == self.closed, (want + 1) % 3, want)
            self.delivered[:, leg] = torch.where(act, d, self.delivered[:, leg])
            self.deliver_ok[:, leg] = torch.where(act, d == want, self.deliver_ok[:, leg])

    def gates_ok(self) -> torch.Tensor:
        return (self.q == 0) | (self.gates == self.q - 1)

    def clone(self) -> "WorldN":
        w = WorldN.__new__(WorldN); w.__dict__.update(self.__dict__)
        for k, v in self.__dict__.items():
            if isinstance(v, torch.Tensor): setattr(w, k, v.clone())
        w.s = dict(self.s); return w


# training and development distributions for v0.3
from stillway2.world3 import SPECS as SPECS2                       # noqa: E402

SPECS = {
    # T23: exactly the v0.2 training distribution (2 or 3 legs, same-gate legs, training families)
    "t23": SPECS2["train"], "t23_stress": SPECS2["train_stress"],
    # T24x: 2 to 4 legs, cross-gate legs allowed, training families
    "t24x": {**SPECS2["train"], "L": (2, 3, 4), "cross": 0.3}, "t24x_stress": {**SPECS2["train_stress"], "L": (2, 3, 4), "cross": 0.3},
    "dev23": SPECS2["dev"], "dev24x": {**SPECS2["dev"], "L": (2, 3, 4), "cross": 0.3},
}
