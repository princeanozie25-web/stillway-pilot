"""Dispatch-3: the transfer world for v0.2.  Batched (torch); a plain-Python reference is at the bottom.

What is new against Dispatch-2
------------------------------
* 2, 3 or 4 legs (Dispatch-2 always had 2).
* Two gates.  Every trip acts on ONE named gate: keep, toggle, open or close it.
  A leg is "same-gate" when both routes act on one gate and "cross-gate" when they act on different gates.
* The work order has six fields: a requirement for each gate (none / closed / open) and a destination
  dock (0,1,2) for the parcel of each station that has one.  So a job has 1 to 6 live obligations.
* Optional WAIT stages before each leg.  They lengthen the history without adding obligations.

A job runs through a fixed frame of slots; a slot that does not apply to a job is skipped (no observation,
no memory update):   INIT, then for each leg i:  K wait slots, ROUTE i, DELIVER i.

Exact planner.  At ROUTE i the valid routes are those from which the largest possible number of gate
requirements can still be met at the end (all remaining route choices are enumerated).  At DELIVER i the
valid dock is the order's dock, or the next dock round if that dock is closed.
"""
from __future__ import annotations

from itertools import product
from typing import Dict, Optional

import torch

EFF_T = torch.tensor([[0, 1], [1, 0], [1, 1], [0, 0]])      # keep, toggle, open, close
EFF_NAMES = "KTOC"
LMAX, NF = 4, 6                                              # fields: q0, q1, p1, p2, p3, p4
FIELD_NAMES = ["gate0", "gate1", "parcel1", "parcel2", "parcel3", "parcel4"]
INIT, WAIT, ROUTE, DELIVER = range(4)
OBS3, GDIM, LEGDIM, N_ACT = 92, 40, 13, 5                    # actions: L, R, D0, D1, D2
MASK64 = (1 << 64) - 1
COMBOS = torch.tensor(list(product((0, 1), repeat=LMAX)))


# ---------------------------------------------------------------------------------------------------------
# Family signature and split.  A family = number of legs, the unordered pair of trips on each leg, and which
# stations have a parcel.  The split is a fixed arithmetic hash (splitmix64) of that signature.
# ---------------------------------------------------------------------------------------------------------
def _mix(x: int) -> int:
    x = (x + 0x9E3779B97F4A7C15) & MASK64
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & MASK64
    return x ^ (x >> 31)


def signature(L: int, eff, tg, parcel) -> int:
    """eff[leg][route], tg[leg][route], parcel[leg] -> integer signature (ignores which side a trip is on)."""
    key = L
    for i in range(LMAX):
        if i < L:
            a, b = eff[i][0] * 2 + tg[i][0], eff[i][1] * 2 + tg[i][1]
            lo, hi = min(a, b), max(a, b)
            key = key * 64 + (lo * 8 + hi)
            key = key * 2 + int(parcel[i])
        else:
            key = key * 128
    return key


def bucket(sig: int, salt: int = 20261121) -> int:
    return _mix(sig ^ _mix(salt)) % 100


def split_of(sig: int) -> str:
    b = bucket(sig)
    return "train" if b < 60 else ("dev" if b < 70 else "final")


def _mix_t(x: torch.Tensor) -> torch.Tensor:
    def lsr(v, k): return (v >> k) & ((1 << (64 - k)) - 1)
    x = x + torch.tensor(0x9E3779B97F4A7C15 - (1 << 64))
    x = (x ^ lsr(x, 30)) * torch.tensor(0xBF58476D1CE4E5B9 - (1 << 64))
    x = (x ^ lsr(x, 27)) * torch.tensor(0x94D049BB133111EB - (1 << 64))
    return x ^ lsr(x, 31)


def bucket_t(L, eff, tg, parcel, salt: int = 20261121) -> torch.Tensor:
    key = L.clone().long()
    for i in range(LMAX):
        a, b = eff[:, i, 0] * 2 + tg[:, i, 0], eff[:, i, 1] * 2 + tg[:, i, 1]
        pair = torch.minimum(a, b) * 8 + torch.maximum(a, b)
        ex = i < L
        key = torch.where(ex, (key * 64 + pair) * 2 + parcel[:, i].long(), key * 128)
    s = _mix(salt); s = s - (1 << 64) if s >= (1 << 63) else s
    h = _mix_t(key ^ torch.tensor(s))
    return _u_mod100(h)


def _u_mod100(h: torch.Tensor) -> torch.Tensor:
    """unsigned 64-bit value mod 100, computed with signed arithmetic."""
    lo = h & 0xFFFFFFFF
    hi = (h >> 32) & 0xFFFFFFFF
    return (hi * (4294967296 % 100) + lo) % 100


# ---------------------------------------------------------------------------------------------------------
# Batched world
# ---------------------------------------------------------------------------------------------------------
SPECS: Dict[str, dict] = {
    # training distribution: 2 or 3 legs, same-gate legs only, training families only
    "train": dict(L=(2, 3), cross=0.0, split="train", K=1, p_wait=0.5, rev=0.10, gflip=0.10, decor=0.20, close=0.10,
                  msg=0.15, full=0.05, reissue=0.0, env="random"),
    "train_stress": dict(L=(2, 3), cross=0.0, split="train", K=1, p_wait=0.5, rev=0.4, gflip=0.4, decor=0.6, close=0.5,
                         msg=0.45, full=0.05, reissue=0.25, env="random"),
    "dev": dict(L=(2, 3), cross=0.0, split="dev", K=1, p_wait=0.5, rev=0.10, gflip=0.10, decor=0.20, close=0.10,
                msg=0.15, full=0.05, reissue=0.0, env="model"),
    "dev_plain": dict(L=(2, 3), cross=0.0, split="dev", K=1, p_wait=0.5, rev=0, gflip=0, decor=0, close=0, msg=0, full=0,
                      reissue=0, env="model"),
}


class World3:
    def __init__(self, batch: int, spec: dict, gen: torch.Generator):
        self.B, self.s, self.gen = batch, dict(spec), gen
        self.K = self.s["K"]
        self.T = 1 + LMAX * (self.K + 2)
        self.reset()

    # -- sampling ----------------------------------------------------------------------------------------
    def _r(self, *shape):
        return torch.rand(*shape, generator=self.gen)

    def _ri(self, hi, *shape):
        return torch.randint(0, hi, shape, generator=self.gen)

    def _sample_layout(self, n):
        s = self.s
        Lc = torch.tensor(s["L"])
        L = Lc[self._ri(len(Lc), n)]
        eff = self._ri(4, n, LMAX, 2)
        g = self._ri(2, n, LMAX)
        cross = self._r(n, LMAX) < s["cross"]
        tg = torch.stack([g, torch.where(cross, 1 - g, g)], -1)
        if s.get("force_cross"):                          # final stratum C: at least one cross-gate leg
            j = (self._r(n) * L).long().clamp(max=LMAX - 1)
            tg[torch.arange(n), j, 1] = 1 - tg[torch.arange(n), j, 0]
        ex = torch.arange(LMAX)[None, :] < L[:, None]
        parcel = (self._r(n, LMAX) < 0.6) & ex
        return L, eff, tg, parcel

    def reset(self):
        B, s = self.B, self.s
        L, eff, tg, parcel = self._sample_layout(B)
        if s["split"] is not None:                         # rejection sampling on the family split
            lo, hi = {"train": (0, 60), "dev": (60, 70), "final": (70, 100)}[s["split"]]
            for _ in range(2000):
                b = bucket_t(L, eff, tg, parcel)
                bad = (b < lo) | (b >= hi)
                if not bad.any():
                    break
                L2, e2, t2, p2 = self._sample_layout(B)
                L = torch.where(bad, L2, L); eff = torch.where(bad[:, None, None], e2, eff)
                tg = torch.where(bad[:, None, None], t2, tg); parcel = torch.where(bad[:, None], p2, parcel)
            assert not bad.any()
        self.L, self.eff, self.tg, self.parcel = L, eff, tg, parcel
        self.gates = self._ri(2, B, 2)
        self.decor = self._ri(4, B); self.decor0 = self.decor.clone()
        self.closed = torch.where(self._r(B) < 0.25, self._ri(3, B), torch.full((B,), -1))
        qn = self._r(B, 2) < 0.25
        self.q = torch.where(qn, torch.zeros(B, 2, dtype=torch.long), 1 + self._ri(2, B, 2))    # 0 none, 1 closed, 2 open
        self.p = self._ri(3, B, LMAX)
        self.wait_on = self._r(B, LMAX, max(1, self.K)) < s["p_wait"]
        self.cur = torch.zeros(B, dtype=torch.long)        # legs already travelled
        self.t = -1
        self.delivered = torch.full((B, LMAX), -1)
        self.deliver_ok = torch.ones(B, LMAX, dtype=torch.bool)

    # -- frame -------------------------------------------------------------------------------------------
    def slot(self, t: int):
        """(kind, leg) of frame slot t."""
        if t == 0:
            return INIT, 0
        leg, pos = divmod(t - 1, self.K + 2)
        return (WAIT if pos < self.K else (ROUTE if pos == self.K else DELIVER)), leg

    def active(self, t: int) -> torch.Tensor:
        kind, leg = self.slot(t)
        if kind == INIT:
            return torch.ones(self.B, dtype=torch.bool)
        ex = leg < self.L
        if kind == WAIT:
            pos = (t - 1) % (self.K + 2)
            return ex & self.wait_on[:, leg, pos]
        if kind == ROUTE:
            return ex
        return ex & self.parcel[:, leg]

    # -- one slot ----------------------------------------------------------------------------------------
    def next_obs(self, script: Optional[dict] = None):
        """Advance to the next frame slot.  Returns (obs (B,OBS3), active (B,) bool).
        `script` can force a message for chosen rows: {"rows": bool (B,), "field": long (B,), "value": long (B,),
        "show": bool}.  With show=False the order changes silently (used by the memory-edit experiments)."""
        self.t += 1
        t, B, s = self.t, self.B, self.s
        kind, leg = self.slot(t)
        act = self.active(t)
        ar = torch.arange(B)
        has = torch.zeros(B, NF, dtype=torch.bool)
        if kind == INIT:
            has[:] = True
        else:
            # re-wire one leg that has not been travelled yet
            m = act & (self._r(B) < s["rev"]) & (self.cur < self.L)
            j = (self.cur + (self._r(B) * (self.L - self.cur).clamp(min=1)).long()).clamp(max=LMAX - 1)
            sw = torch.zeros(B, LMAX, dtype=torch.bool); sw[ar[m], j[m]] = True
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
                self.p = torch.where(re[:, None], self._ri(3, B, LMAX), self.p)
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
            if s.get("noop_msg", 0) > 0:                       # an irrelevant edit: a field is re-sent with the value it already has
                mn = act & (self._r(B) < s["noop_msg"]); fn = self._ri(NF, B)
                has[ar[mn], fn[mn]] = True
            full = act & ((self._r(B) < s["full"]) | re)
            if script is not None and script.get("full_rows") is not None:
                full = full | (script["full_rows"] & act)
            has = has | full[:, None]
        obs = torch.zeros(B, OBS3)
        obs[:, kind] = 1.0
        obs[ar, 4 + (torch.full((B,), leg) if kind in (ROUTE, DELIVER) else self.cur.clamp(max=LMAX - 1))] = 1.0
        obs[:, 8:10] = self.gates.float()
        obs[ar, 10 + self.closed + 1] = 1.0
        obs[:, 14] = (self.decor & 1).float(); obs[:, 15] = ((self.decor >> 1) & 1).float()
        vals = torch.cat([self.q, self.p], 1)                                   # (B,6) each in 0..2
        for k in range(NF):
            obs[:, 16 + 4 * k] = has[:, k].float()
            obs[ar[has[:, k]], 16 + 4 * k + 1 + vals[has[:, k], k]] = 1.0
        for i in range(LMAX):
            o = 40 + LEGDIM * i
            ex = i < self.L
            obs[:, o] = ex.float(); obs[:, o + 1] = (i < self.cur).float(); obs[:, o + 2] = self.parcel[:, i].float()
            for r in (0, 1):
                obs[ar, o + 3 + 5 * r + self.eff[:, i, r]] = 1.0
                obs[:, o + 3 + 5 * r + 4] = self.tg[:, i, r].float()
            obs[~ex, o + 1:o + LEGDIM] = 0.0
        return obs, act

    def best_counts(self):
        """(B,2): for each first route at the current leg, the largest number of gate requirements that can
        still be met at the end.  Enumerates every remaining route choice."""
        B = self.B
        C = COMBOS                                                  # (16, LMAX) every route choice per leg
        g = self.gates[:, None, :].expand(B, 16, 2).clone()         # gates under each of the 16 choices
        for i in range(LMAX):
            live = ((i >= self.cur) & (i < self.L))[:, None]        # (B,1)
            r = C[:, i]                                             # (16,)
            e = self.eff[:, i, :][:, r]; tgt = self.tg[:, i, :][:, r]            # (B,16)
            cur_g = g.gather(2, tgt[:, :, None]).squeeze(2)
            new = torch.where(live, EFF_T[e, cur_g], cur_g)
            g = g.scatter(2, tgt[:, :, None], new[:, :, None])
        sat = ((self.q[:, None, :] > 0) & (g == self.q[:, None, :] - 1)).sum(2)   # (B,16)
        first = C.T[self.cur.clamp(max=LMAX - 1)]                   # (B,16) route taken at the current leg
        best = torch.stack([sat.masked_fill(first != a, -1).max(1).values for a in (0, 1)], 1)
        return best

    def dp_tables(self) -> torch.Tensor:
        """(B, LMAX, 4): the exact planner's value table at each leg.  Entry [i, s] = the largest number of gate
        requirements that can be met at the end if the carrier stands before leg i with gates in joint state
        s (s = gate0 * 2 + gate1).  Used only as a training target for the backward sweep."""
        B = self.B
        g = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]])                     # (4,2) joint states
        V = ((self.q[:, None, :] > 0) & (g[None] == self.q[:, None, :] - 1)).sum(2)          # terminal (B,4)
        out = torch.zeros(B, LMAX, 4, dtype=torch.long)
        for i in range(LMAX - 1, -1, -1):
            ex = (i < self.L)[:, None]
            cand = []
            for r in (0, 1):
                e = self.eff[:, i, r][:, None].expand(B, 4); tgt = self.tg[:, i, r][:, None].expand(B, 4)
                gs = g[None].expand(B, 4, 2)
                cur_g = gs.gather(2, tgt[:, :, None]).squeeze(2)
                ng = gs.scatter(2, tgt[:, :, None], EFF_T[e, cur_g][:, :, None])
                cand.append(V.gather(1, ng[:, :, 0] * 2 + ng[:, :, 1]))
            V = torch.where(ex, torch.maximum(cand[0], cand[1]), V)
            out[:, i] = V
        return out

    def valid_mask(self) -> torch.Tensor:
        kind, leg = self.slot(self.t)
        v = torch.zeros(self.B, N_ACT, dtype=torch.bool)
        if kind == ROUTE:
            b = self.best_counts()
            v[:, 0:2] = b == b.max(1, keepdim=True).values
        elif kind == DELIVER:
            d = self.p[:, leg]
            d = torch.where(d == self.closed, (d + 1) % 3, d)
            v[torch.arange(self.B), 2 + d] = True
        return v

    def stage_mask(self) -> torch.Tensor:
        kind, _ = self.slot(self.t)
        m = torch.zeros(N_ACT, dtype=torch.bool)
        if kind == ROUTE: m[0:2] = True
        elif kind == DELIVER: m[2:5] = True
        return m

    def env_action(self, valid: torch.Tensor) -> torch.Tensor:
        w = (valid if self.s["env"] == "expert" else self.stage_mask()[None, :].expand(self.B, -1)).float()
        return torch.multinomial(w, 1, generator=self.gen).squeeze(1)

    def apply(self, action: torch.Tensor, act: torch.Tensor):
        kind, leg = self.slot(self.t)
        ar = torch.arange(self.B)
        if kind == ROUTE:
            r = action.clamp(0, 1)
            e = self.eff[ar, leg, r]; tgt = self.tg[ar, leg, r]
            new = EFF_T[e, self.gates[ar, tgt]]
            self.gates[ar, tgt] = torch.where(act, new, self.gates[ar, tgt])
            self.cur = torch.where(act, self.cur + 1, self.cur)
        elif kind == DELIVER:
            d = (action - 2).clamp(0, 2)
            want = self.p[:, leg]; want = torch.where(want == self.closed, (want + 1) % 3, want)
            self.delivered[:, leg] = torch.where(act, d, self.delivered[:, leg])
            self.deliver_ok[:, leg] = torch.where(act, d == want, self.deliver_ok[:, leg])

    def gates_ok(self) -> torch.Tensor:
        """(B,2) bool: each gate requirement met right now (True where there is no requirement)."""
        return (self.q == 0) | (self.gates == self.q - 1)

    def clone(self) -> "World3":
        w = World3.__new__(World3)
        w.__dict__.update(self.__dict__)
        for k, v in self.__dict__.items():
            if isinstance(v, torch.Tensor):
                setattr(w, k, v.clone())
        w.s = dict(self.s)
        return w


# ---------------------------------------------------------------------------------------------------------
# Plain-Python reference (the exact planner on one job); used by tests to check the batched code.
# ---------------------------------------------------------------------------------------------------------
def ref_valid_routes(L, eff, tg, gates, q, cur):
    eff_tab = ((0, 1), (1, 0), (1, 1), (0, 0))
    best = {0: -1, 1: -1}
    for combo in product((0, 1), repeat=L - cur):
        g = list(gates)
        for k, r in enumerate(combo):
            i = cur + k
            g[tg[i][r]] = eff_tab[eff[i][r]][g[tg[i][r]]]
        sat = sum(1 for j in (0, 1) if q[j] > 0 and g[j] == q[j] - 1)
        best[combo[0]] = max(best[combo[0]], sat)
    m = max(best.values())
    return tuple(a for a in (0, 1) if best[a] == m)


def ref_dock(p, closed):
    return p if p != closed else (p + 1) % 3
