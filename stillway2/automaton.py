"""v0.2 copy of stillway/automaton.py with the operator-message alphabet as a parameter.

v0.1 listed 20 message patterns (nothing, one field, or all three).  The simulator also accepts
two fields revised at the same stage, so the schema permits 3 x 3 x 4 = 36 patterns.  MSGS36 is
enumerated from the field domains.  MSGS20 is the v0.1 list, unchanged and in the same order.
Everything else is the v0.1 code.

Exhaustive extraction of the finite-state machine a discrete planner implements.

Because the planner passes only code IDs between steps and the world is finite,
we do not have to sample.  We enumerate:

  * every code state the planner can reach, stage by stage, and
  * for each one, EVERY observation it could be shown next
    (every allowed layout x gate x closed bay x decoration x operator message).

The environment here is adversarial: any observation may follow any other.
That is a superset of what the simulator can produce, so a pass here covers
every real history (reversals, gate faults, closures, revisions, at any stage).

Outputs
-------
certificate : number of (state, observation) pairs checked against the exact
              planner and the list of violations (with a witness trace each).
dictionary  : which work orders each code state can stand for.
quotients   : behavioural classes (states no future observation can tell apart)
              and specification classes (states that mean the same to the exact planner).
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch

from stillway.model import Core
from stillway.world import (ALL_ORDERS, EFFECT_NAMES, N_ACTIONS, N_STAGES, NO_BAY, OBS_DIM, Order, STAGE_ACTIONS,
                    STAGE_NAMES, valid_actions)

ORDER_INDEX = {o: i for i, o in enumerate(ALL_ORDERS)}

# operator messages: nothing, one revised field, or a whole re-issued order
MSGS20: List[Tuple[Optional[int], Optional[int], Optional[int]]] = [(None, None, None)]
MSGS20 += [(0, None, None), (1, None, None), (None, 0, None), (None, 1, None), (None, None, 0), (None, None, 1), (None, None, 2)]
MSGS20 += [o for o in ALL_ORDERS]
DOCK_DOMAIN, GATE_DOMAIN, BAY_DOMAIN = (None, 0, 1), (None, 0, 1), (None, 0, 1, 2)
MSGS36 = [(d, q, b) for d in DOCK_DOMAIN for q in GATE_DOMAIN for b in BAY_DOMAIN]     # every mask and value
assert len(MSGS36) == 36 and set(MSGS20) <= set(MSGS36) and len(set(MSGS36)) == 36


def relevant_key(stage: int, order: Tuple[int, int, int]) -> tuple:
    """What the exact planner still needs from the order after `stage` has been processed."""
    d, q, b = order
    if stage <= 2: return (d, q, b)
    if stage == 3: return (q, b)
    if stage == 4: return (b,)
    return ()


def pack(ids: np.ndarray) -> np.ndarray:
    """(N,S) code ids in -1..K-1 -> one int per row."""
    out = np.zeros(ids.shape[0], dtype=np.int64)
    for s in range(ids.shape[1]):
        out = out * 64 + (ids[:, s] + 1)
    return out


def unpack(x: int, n_slots: int) -> List[int]:
    out = []
    for _ in range(n_slots):
        out.append(int(x % 64) - 1)
        x //= 64
    return out[::-1]


class Alphabet:
    def __init__(self, layouts: Sequence[Tuple[int, int, int, int]], msgs=None):
        MSGS = self.msgs = list(msgs if msgs is not None else MSGS20)
        self.full_idx = [i for i, m in enumerate(MSGS) if None not in m]
        self.layouts = [tuple(l) for l in layouts]
        phys = [(e, g, c, dec) for e in self.layouts for g in (0, 1) for c in (NO_BAY, 0, 1, 2) for dec in range(4)]
        self.phys = phys
        self.P, self.M = len(phys), len(MSGS)
        self.A = self.P * self.M
        # order transition: new_order[o, m]
        self.new_order = np.zeros((len(ALL_ORDERS), self.M), dtype=np.int64)
        for oi, (d, q, b) in enumerate(ALL_ORDERS):
            for mi, (md, mq, mb) in enumerate(MSGS):
                self.new_order[oi, mi] = ORDER_INDEX[(d if md is None else md, q if mq is None else mq, b if mb is None else mb)]
        self.msg_order = np.array([ORDER_INDEX[m] if None not in m else -1 for m in MSGS])
        # valid-action bitmask per action stage: valid[stage][order, phys]
        self.valid: Dict[int, np.ndarray] = {}
        for s in STAGE_ACTIONS:
            v = np.zeros((len(ALL_ORDERS), self.P), dtype=np.uint8)
            for oi, (d, q, b) in enumerate(ALL_ORDERS):
                o = Order(d, q, b)
                for pi, (e, g, c, dec) in enumerate(phys):
                    bits = 0
                    for a in valid_actions(s, e, g, c, o):
                        bits |= 1 << a
                    v[oi, pi] = bits
            self.valid[s] = v
        # observation matrix without the stage one-hot: (P, M, OBS_DIM)
        base = np.zeros((self.P, self.M, OBS_DIM), dtype=np.float32)
        for pi, (e, g, c, dec) in enumerate(phys):
            for i, ef in enumerate(e):
                base[pi, :, 6 + 4 * i + ef] = 1
            base[pi, :, 22] = g
            base[pi, :, 23 + c + 1] = 1
            base[pi, :, 27] = dec & 1
            base[pi, :, 28] = (dec >> 1) & 1
        for mi, (md, mq, mb) in enumerate(MSGS):
            if md is not None: base[:, mi, 29] = 1; base[:, mi, 30] = md
            if mq is not None: base[:, mi, 31] = 1; base[:, mi, 32] = mq
            if mb is not None: base[:, mi, 33] = 1; base[:, mi, 34 + mb] = 1
        self.base = torch.from_numpy(base.reshape(self.A, OBS_DIM))

    def obs(self, stage: int) -> torch.Tensor:
        o = self.base.clone()
        o[:, stage] = 1
        return o

    def describe(self, stage: int, a: int) -> dict:
        pi, mi = divmod(a, self.M)
        e, g, c, dec = self.phys[pi]
        return {"stage": STAGE_NAMES[stage], "leg1": EFFECT_NAMES[e[0]] + EFFECT_NAMES[e[1]],
                "leg2": EFFECT_NAMES[e[2]] + EFFECT_NAMES[e[3]], "gate": g,
                "closed_bay": None if c == NO_BAY else c, "decor": dec, "message": self.msgs[mi]}


class Machine:
    """The extracted machine.  stage_codes[s] = packed code states reachable after stage s."""

    def __init__(self, model: Core, layouts, canon: Optional[List[Dict[int, int]]] = None, verbose: bool = False,
                 max_states: int = 4000, msgs=None, canon_stats: Optional[dict] = None):
        self.model, self.alpha = model, Alphabet(layouts, msgs)
        self.canon_stats = canon_stats            # if given: counts map hits and misses (identity fallback) per stage
        self.canon = canon                 # optional per-stage map packed code -> packed representative
        self.S = model.cfg.n_slots
        self.stage_codes: List[np.ndarray] = []
        self.act: List[Optional[np.ndarray]] = []    # act[s][i, a]   action proposed in state i (of stage s-1) on obs a
        self.nxt: List[np.ndarray] = []              # nxt[s][i, a]   index into stage_codes[s]
        self.pairs: List[set] = []                   # reachable (code index, order index) after stage s
        self.parent: List[dict] = []                 # witness: (ci, oi) -> (prev ci, prev oi, obs index)
        self.violations: List[dict] = []
        self.checked = 0
        self.exploded = False
        t0 = time.time()
        al = self.alpha
        prev_codes = np.array([pack(np.full((1, self.S), -1))[0]])
        prev_pairs = {(0, -1)}
        for s in range(N_STAGES):
            obs = al.obs(s)
            n_prev = len(prev_codes)
            acts = np.zeros((n_prev, al.A), dtype=np.int8)
            nxt_packed = np.zeros((n_prev, al.A), dtype=np.int64)
            per = max(1, 262144 // al.A)                                   # states per forward batch
            cols = list(STAGE_ACTIONS[s]) if s in STAGE_ACTIONS else None
            for i0 in range(0, n_prev, per):
                chunk = prev_codes[i0:i0 + per]
                ids = torch.tensor([unpack(int(pc), self.S) for pc in chunk]).repeat_interleave(al.A, dim=0)
                logits, new = self._infer(ids, obs.repeat(len(chunk), 1))
                if cols is not None:
                    acts[i0:i0 + len(chunk)] = np.array(cols, dtype=np.int8)[logits[:, cols].argmax(1).numpy()].reshape(len(chunk), al.A)
                p = pack(new.numpy())
                if canon is not None:
                    cm = canon[s]
                    u, inv = np.unique(p, return_inverse=True)
                    if canon_stats is not None:
                        miss = np.array([int(x) not in cm for x in u])
                        cnt = np.bincount(inv, minlength=len(u))
                        st_ = canon_stats.setdefault(s, {"transitions": 0, "missing_transitions": 0, "missing_codes": set()})
                        st_["transitions"] += int(cnt.sum()); st_["missing_transitions"] += int(cnt[miss].sum())
                        st_["missing_codes"].update(int(x) for x in u[miss])
                    p = np.array([cm.get(int(x), int(x)) for x in u], dtype=np.int64)[inv]
                nxt_packed[i0:i0 + len(chunk)] = p.reshape(len(chunk), al.A)
            # which observations are allowed at this stage
            msg_ok = np.zeros(al.M, dtype=bool)
            msg_ok[al.full_idx if s == 0 else slice(None)] = True
            a_ok = np.tile(msg_ok, al.P)                                   # (A,)
            a_idx = np.nonzero(a_ok)[0]
            p_of = a_idx // al.M
            m_of = a_idx % al.M
            # reachable next pairs + correctness check
            new_pairs: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
            reach_codes: Dict[int, int] = {}
            pending = []
            for (ci, oi) in sorted(prev_pairs):
                o_new = al.msg_order[m_of] if oi < 0 else al.new_order[oi, m_of]
                if s in STAGE_ACTIONS:
                    vbits = al.valid[s][o_new, p_of]
                    ok = (vbits >> acts[ci, a_idx].astype(np.uint8)) & 1
                    self.checked += len(a_idx)
                    bad = np.nonzero(ok == 0)[0]
                    if len(bad):
                        self.violations.append({"stage": s, "state": (ci, oi), "n_bad": int(len(bad)),
                                                "example_obs": int(a_idx[bad[0]]), "order_now": int(o_new[bad[0]]),
                                                "proposed": int(acts[ci, a_idx[bad[0]]])})
                key = nxt_packed[ci, a_idx] * 16 + o_new
                u, first = np.unique(key, return_index=True)
                pending.append((ci, oi, u, a_idx[first]))
            for (ci, oi, u, firsts) in pending:
                for k, a in zip(u.tolist(), firsts.tolist()):
                    pc, o2 = divmod(k, 16)
                    if pc not in reach_codes:
                        reach_codes[pc] = len(reach_codes)
                    pr = (reach_codes[pc], o2)
                    if pr not in new_pairs:
                        new_pairs[pr] = (ci, oi, a)
            codes = np.array(sorted(reach_codes, key=reach_codes.get), dtype=np.int64)
            # index table for transitions
            lut = {int(c): i for i, c in enumerate(codes)}
            u, inv = np.unique(nxt_packed, return_inverse=True)
            nxt = np.array([lut.get(int(x), -1) for x in u], dtype=np.int32)[inv].reshape(nxt_packed.shape)
            self.stage_codes.append(codes); self.act.append(acts if s in STAGE_ACTIONS else None); self.nxt.append(nxt)
            self.pairs.append(set(new_pairs)); self.parent.append(new_pairs)
            self.a_ok = a_ok
            if verbose:
                print(f"  stage {STAGE_NAMES[s]}: {len(codes)} code states, {len(new_pairs)} (state, order) pairs, "
                      f"{self.checked:,} checks, {sum(v['n_bad'] for v in self.violations):,} bad, {time.time() - t0:.0f}s", flush=True)
            if len(codes) > max_states:
                self.exploded = True
                break
            prev_codes, prev_pairs = codes, set(new_pairs)
        self.seconds = time.time() - t0

    def _infer(self, ids, obs):
        outs_l, outs_n = [], []
        for i in range(0, obs.shape[0], 32768):
            l, n = self.model.infer(ids[i:i + 32768], obs[i:i + 32768])
            outs_l.append(l); outs_n.append(n)
        return torch.cat(outs_l), torch.cat(outs_n)

    # ---- reports -----------------------------------------------------------
    def n_bad(self) -> int:
        return sum(v["n_bad"] for v in self.violations)

    def witness(self, stage: int, pair: Tuple[int, int]) -> List[dict]:
        """A history that reaches this (state, order) pair."""
        trace = []
        s, pr = stage, pair
        while s >= 0:
            ci, oi, a = self.parent[s][pr]
            trace.append(self.alpha.describe(s, a))
            pr = (ci, oi); s -= 1
        return trace[::-1]

    def orders_of(self, stage: int) -> Dict[int, set]:
        """Dictionary: code index -> the set of work orders it can stand for at this stage."""
        d: Dict[int, set] = {}
        for (ci, oi) in self.pairs[stage]:
            d.setdefault(ci, set()).add(oi)
        return d

    def spec_classes(self, stage: int) -> Dict[int, object]:
        """code index -> the exact planner's meaning of that state, or 'AMBIGUOUS' if one code
        state stands for orders the exact planner must tell apart."""
        out = {}
        for ci, os_ in self.orders_of(stage).items():
            keys = {relevant_key(stage, ALL_ORDERS[o]) for o in os_}
            out[ci] = next(iter(keys)) if len(keys) == 1 else "AMBIGUOUS"
        return out

    def behaviour_classes(self) -> List[np.ndarray]:
        """Bisimulation quotient.  cls[s][i] = class of code state i after stage s.  Two states are in
        one class exactly when no future sequence of allowed observations makes them act differently."""
        cls: List[Optional[np.ndarray]] = [None] * N_STAGES
        last = len(self.stage_codes) - 1
        cls[last] = np.zeros(len(self.stage_codes[last]), dtype=np.int64)
        for s in range(last - 1, -1, -1):
            # the future of a state after stage s is its row in the stage s+1 tables
            ok = np.nonzero(np.tile(np.ones(self.alpha.M, dtype=bool), self.alpha.P))[0]
            nxt_cls = cls[s + 1][self.nxt[s + 1][:, ok]]
            sig = {}
            out = np.zeros(len(self.stage_codes[s]), dtype=np.int64)
            for i in range(len(self.stage_codes[s])):
                h = hashlib.sha1(nxt_cls[i].tobytes())
                if self.act[s + 1] is not None:
                    h.update(self.act[s + 1][i, ok].tobytes())
                out[i] = sig.setdefault(h.digest(), len(sig))
            cls[s] = out
        return cls

    def summary(self) -> dict:
        cls = self.behaviour_classes()
        rows = []
        for s in range(len(self.stage_codes)):
            sc = self.spec_classes(s)
            n_codes = len(self.stage_codes[s])
            n_beh = int(cls[s].max()) + 1
            n_spec = len({v for v in sc.values() if v != "AMBIGUOUS"})
            amb = sum(v == "AMBIGUOUS" for v in sc.values())
            rows.append({"stage": STAGE_NAMES[s], "code_states": n_codes, "behaviour_classes": n_beh,
                         "spec_classes": n_spec, "ambiguous_states": amb,
                         "silent_bits": round(math.log2(n_codes) - math.log2(n_beh), 3),
                         "tiebreak_bits": round(math.log2(n_beh) - math.log2(max(1, n_spec)), 3)})
        return {"layouts": len(self.alpha.layouts), "observations_per_stage": int(self.alpha.A),
                "pairs_checked": int(self.checked), "violating_pairs": int(self.n_bad()),
                "violating_states": len(self.violations), "state_explosion": self.exploded,
                "seconds": round(self.seconds, 1), "stages": rows}

    def spec_canon(self) -> List[Dict[int, int]]:
        """Specification quotient: map every code state to ONE representative per meaning."""
        maps = []
        for s in range(len(self.stage_codes)):
            sc = self.spec_classes(s)
            rep: Dict[object, int] = {}
            m = {}
            for ci in range(len(self.stage_codes[s])):
                k = sc[ci]
                if k == "AMBIGUOUS":
                    continue
                rep.setdefault(k, int(self.stage_codes[s][ci]))
                m[int(self.stage_codes[s][ci])] = rep[k]
            maps.append(m)
        return maps

    def behaviour_canon(self) -> List[Dict[int, int]]:
        cls = self.behaviour_classes()
        maps = []
        for s in range(len(self.stage_codes)):
            rep: Dict[int, int] = {}
            m = {}
            for ci in range(len(self.stage_codes[s])):
                rep.setdefault(int(cls[s][ci]), int(self.stage_codes[s][ci]))
                m[int(self.stage_codes[s][ci])] = rep[int(cls[s][ci])]
            maps.append(m)
        return maps
