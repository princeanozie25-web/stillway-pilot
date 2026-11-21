"""Fixture generator and the train / dev / sealed split.

Split rule (frozen, nothing up the sleeve): hash each family name with SHA-256
under a fixed salt, sort by hash; first 60 families train, next 15 dev-holdout,
last 25 sealed.  A family is the pair of mechanisms on each leg, so a held-out
family is a combination of mechanisms the model never trained on.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from typing import Dict, List, Sequence, Tuple

from .world import (ALL_FAMILIES, ALL_LAYOUTS, EFF, Episode, NO_BAY, Order, family_of, gate_plans, is_normal, reverse,
                    target_bay)

SALT = "stillway/dispatch-2/v0.1/"
N_TRAIN, N_DEV = 60, 15

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def split_families() -> Dict[str, str]:
    order = sorted(ALL_FAMILIES, key=lambda f: hashlib.sha256((SALT + f).encode()).hexdigest())
    out = {}
    for i, f in enumerate(order):
        out[f] = "train" if i < N_TRAIN else ("dev" if i < N_TRAIN + N_DEV else "sealed")
    return out


SPLIT = split_families()


def families(split: str) -> List[str]:
    return sorted(f for f, s in SPLIT.items() if s == split)


def layouts_of(fams: Sequence[str]) -> List[Tuple[int, int, int, int]]:
    fs = set(fams)
    return [e for e in ALL_LAYOUTS if family_of(e) in fs]


def mirror(plans: set, legs: Sequence[int]) -> set:
    return {((1 - a) if 1 in legs else a, (1 - b) if 2 in legs else b) for (a, b) in plans}


def reversal_eligible(effects, gate0: int, q: int, legs: Sequence[int]) -> bool:
    """A reversal of `legs` is a real test for obligation q when q is reachable in both
    worlds and NO planner that ignores which side the trips are wired to can meet q in both.

    Such a wiring-blind planner picks the same first route in both worlds, then picks the
    second route from the gate it sees (it may react to the gate, so this is closed-loop).
    Version 1 of this rule only compared fixed route plans; the lookup impostor then got 4%
    credit by repairing on leg 2, so the rule was tightened (see docs/evaluator_spec.md)."""
    a, b = effects, reverse(effects, legs)
    if not gate_plans(a, gate0, q) or not gate_plans(b, gate0, q):
        return False
    for r1 in (0, 1):
        ga, gb = EFF[a[r1]][gate0], EFF[b[r1]][gate0]
        for r2a in (0, 1):
            for r2b in (0, 1):
                if ga == gb and r2a != r2b:
                    continue   # same view, so a blind planner must act the same
                if EFF[a[2 + r2a]][ga] == q and EFF[b[2 + r2b]][gb] == q:
                    return False
    return True


def swap_eligible(effects, gate0: int, legs: Sequence[int]) -> bool:
    """Both directions of a swap pair must be reversal-eligible (for q=0 and q=1)."""
    return reversal_eligible(effects, gate0, 0, legs) and reversal_eligible(effects, gate0, 1, legs)


LEG_SETS = ([1], [2], [1, 2])


def eligibility_report(fams: Sequence[str]) -> dict:
    lay = layouts_of(fams)
    tot = ok = 0
    for e in lay:
        for g in (0, 1):
            for legs in LEG_SETS:
                tot += 1
                ok += swap_eligible(e, g, legs)
    lay_ok = sum(any(swap_eligible(e, g, legs) for g in (0, 1) for legs in LEG_SETS) for e in lay)
    return {"layout_gate_reversal_combos": tot, "eligible": ok, "fraction": ok / max(1, tot),
            "layouts": len(lay), "layouts_with_an_eligible_pair": lay_ok}


class Gen:
    def __init__(self, fams: Sequence[str], seed: int, tag: str):
        self.fams = list(fams)
        self.lay = layouts_of(fams)
        self.rng = random.Random(seed)
        self.tag = tag
        self.n = 0

    def _id(self, cls):
        self.n += 1
        return f"{self.tag}-{cls}-{self.n:05d}"

    def _order(self):
        r = self.rng
        return Order(r.randrange(2), r.randrange(2), r.randrange(3))

    def _closed(self):
        return self.rng.randrange(3) if self.rng.random() < 0.25 else NO_BAY

    def _item(self, cls, kind, fam, **kw):
        return {"id": self._id(cls), "class": cls, "kind": kind, "family": fam, "split": self.tag, **kw}

    # ---- single episodes -------------------------------------------------
    def plain(self):
        r = self.rng
        e = r.choice(self.lay)
        ep = Episode(e, r.randrange(2), self._order(), r.randrange(4), self._closed())
        return self._item("plain", "episode", family_of(e), episode=ep.to_json())

    def dynamic(self):
        r = self.rng
        e = r.choice(self.lay)
        ev: Dict[int, list] = {}
        for s in range(1, 6):
            if r.random() < 0.20: ev.setdefault(s, []).append(("rev", r.choice([1, 2])))
            if r.random() < 0.12: ev.setdefault(s, []).append(("gflip",))
            if r.random() < 0.20: ev.setdefault(s, []).append(("decor", r.randrange(4)))
            if r.random() < 0.12: ev.setdefault(s, []).append(("close", r.choice([NO_BAY, 0, 1, 2])))
            if r.random() < 0.15:
                f = r.choice(["dock", "gate", "bay"])
                ev.setdefault(s, []).append(("msg", f, r.randrange(3 if f == "bay" else 2)))
            if r.random() < 0.05: ev.setdefault(s, []).append(("full",))
        ep = Episode(e, r.randrange(2), self._order(), r.randrange(4), self._closed(), "closed", ev)
        return self._item("dynamic", "episode", family_of(e), episode=ep.to_json())

    # ---- pairs -----------------------------------------------------------
    def _pick(self, pred, normal_only=False):
        r = self.rng
        for _ in range(100000):
            e = r.choice(self.lay)
            if normal_only and not is_normal(e):
                continue
            g, q = r.randrange(2), r.randrange(2)
            legs = r.choice(LEG_SETS)
            if pred(e, g, q, legs):
                return e, g, q, legs
        raise RuntimeError("no eligible layout: the missing condition must be reported")

    def route_swap(self):
        """Same normal layout, same observations after INIT, opposite gate obligation."""
        r = self.rng
        e, g, q, _ = self._pick(lambda e, g, q, legs: 0 < len(gate_plans(e, g, q)) < 4, normal_only=True)
        d, b, dec, cl = r.randrange(2), r.randrange(3), r.randrange(4), self._closed()
        a = Episode(e, g, Order(d, q, b), dec, cl)
        bb = Episode(e, g, Order(d, 1 - q, b), dec, cl)
        return self._item("route_swap", "pair", family_of(e), a=a.to_json(), b=bb.to_json())

    def wiring_reversal(self):
        """Same order; layout in normal orientation vs reversed from the start."""
        r = self.rng
        e, g, q, legs = self._pick(lambda e, g, q, legs: reversal_eligible(e, g, q, legs), normal_only=True)
        o, dec, cl = Order(r.randrange(2), q, r.randrange(3)), r.randrange(4), self._closed()
        a = Episode(e, g, o, dec, cl)
        bb = Episode(reverse(e, legs), g, o.copy(), dec, cl)
        return self._item("wiring_reversal", "pair", family_of(e), a=a.to_json(), b=bb.to_json(), rev_legs=legs)

    def midplan_reversal(self):
        """Same start; in run b the wiring is reversed AFTER the work order was given."""
        r = self.rng
        e, g, q, legs = self._pick(lambda e, g, q, legs: reversal_eligible(e, g, q, legs))
        o, dec, cl = Order(r.randrange(2), q, r.randrange(3)), r.randrange(4), self._closed()
        stage = r.choice([1, 2])
        a = Episode(e, g, o, dec, cl)
        bb = Episode(e, g, o.copy(), dec, cl, "closed", {stage: [("rev", l) for l in legs]})
        return self._item("midplan_reversal", "pair", family_of(e), a=a.to_json(), b=bb.to_json(), rev_legs=legs)

    def open_revision(self):
        """Open book (the full current order is shown at every stage); run b revises the gate obligation."""
        r = self.rng
        e, g, q, _ = self._pick(lambda e, g, q, legs: 0 < len(gate_plans(e, g, q)) < 4, normal_only=True)
        d, b, dec, cl = r.randrange(2), r.randrange(3), r.randrange(4), self._closed()
        a = Episode(e, g, Order(d, q, b), dec, cl, "open")
        bb = Episode(e, g, Order(d, q, b), dec, cl, "open", {1: [("msg", "gate", 1 - q)]})
        return self._item("open_revision", "pair", family_of(e), a=a.to_json(), b=bb.to_json())

    # ---- the decisive paired replay ---------------------------------------
    def swap_pair(self):
        """Two items (both directions).  Donor and target have opposite gate obligations,
        reversed wiring, the same stage, and independently drawn unrelated obligations."""
        r = self.rng
        e, g, q, legs = self._pick(lambda e, g, q, legs: swap_eligible(e, g, legs))
        cl = self._closed()
        dT, bT = r.randrange(2), r.randrange(3)
        while True:
            dS, bS = r.randrange(2), r.randrange(3)
            # the unrelated obligations must differ in what they make the carrier DO
            if (dS, target_bay(bS, cl)) != (dT, target_bay(bT, cl)):
                break
        T = Episode(e, g, Order(dT, q, bT), r.randrange(4), cl)
        S = Episode(reverse(e, legs), g, Order(dS, 1 - q, bS), r.randrange(4), cl)
        pid = self._id("pair")
        fam = family_of(e)
        one = self._item("swap", "swap", fam, pair=pid, target=T.to_json(), donor=S.to_json(), pause_after="PLAN",
                         rev_legs=legs, expect={"gate": 1 - q, "dock": dT, "bay": target_bay(bT, cl)})
        two = self._item("swap", "swap", fam, pair=pid, target=S.to_json(), donor=T.to_json(), pause_after="PLAN",
                         rev_legs=legs, expect={"gate": q, "dock": dS, "bay": target_bay(bS, cl)})
        return [one, two]


def make_set(fams: Sequence[str], seed: int, tag: str, n_each: int, n_swap_pairs: int) -> List[dict]:
    g = Gen(fams, seed, tag)
    items: List[dict] = []
    for _ in range(n_each):
        items += [g.plain(), g.dynamic(), g.route_swap(), g.wiring_reversal(), g.midplan_reversal(), g.open_revision()]
    for _ in range(n_swap_pairs):
        items += g.swap_pair()
    return items


def write_jsonl(path: str, items: Sequence[dict]) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for it in items:
            f.write(json.dumps(it, sort_keys=True) + "\n")
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def read_jsonl(path: str) -> List[dict]:
    return [json.loads(l) for l in open(path)]


DEV_IN = os.path.join(ROOT, "fixtures", "dev", "dev_in.jsonl")      # families seen in training
DEV_OUT = os.path.join(ROOT, "fixtures", "dev", "dev_out.jsonl")    # dev-holdout families
SEALED = os.path.join(ROOT, "fixtures", "sealed", "sealed.jsonl")
FREEZE = os.path.join(ROOT, "FREEZE.json")


def load_sealed() -> List[dict]:
    """Sealed fixtures open only after the checkpoint, slot-selection rule and scorer are frozen."""
    if not os.path.exists(FREEZE):
        raise PermissionError("sealed fixtures are closed until FREEZE.json exists")
    return read_jsonl(SEALED)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "make-dev":
        h1 = write_jsonl(DEV_IN, make_set(families("train"), 1101, "dev_in", 300, 400))
        h2 = write_jsonl(DEV_OUT, make_set(families("dev"), 1102, "dev_out", 300, 400))
        print(json.dumps({"dev_in_sha256": h1, "dev_out_sha256": h2,
                          "eligibility_train": eligibility_report(families("train")),
                          "eligibility_dev": eligibility_report(families("dev"))}, indent=1))
    elif cmd == "make-sealed":
        # the seed is derived from the sealed family list, so it is fixed by the split rule
        seed = int(hashlib.sha256(("sealed|" + "|".join(families("sealed"))).encode()).hexdigest()[:8], 16)
        h = write_jsonl(SEALED, make_set(families("sealed"), seed, "sealed", 500, 1000))
        print(json.dumps({"sealed_sha256": h, "eligibility_sealed": eligibility_report(families("sealed"))}, indent=1))
    elif cmd == "split":
        print(json.dumps({s: families(s) for s in ("train", "dev", "sealed")}, indent=1))
