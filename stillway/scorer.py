"""The scorer.  It runs a planner on fixtures through the simulator and decides credit.

Fixture kinds
-------------
episode : one run.           Credit = every proposed action is in the exact planner's valid set.
pair    : two runs (a, b).   Credit = BOTH runs get credit.  (Pairs make shortcuts score 0, not 50%.)
swap    : target + donor.    Pause both after a stage, copy chosen memory slots donor -> target,
                             resume the target in the TARGET's world.  Credit = the realised gate
                             equals the DONOR's obligation, parcel 1 reached the target's dock,
                             and parcel 2 reached the target's bay.

The planner never touches the simulator.  The scorer also checks that save/restore
does not change the next proposal (reload check).
"""
from __future__ import annotations

import json
from typing import Callable, Dict, Iterable, List, Optional, Sequence

from .planners import Planner
from .world import ACTIONS, Episode, LEG2, N_STAGES, STAGE_ACTIONS, STAGE_NAMES, Sim, target_bay


def run_episode(planner: Planner, ep: Episode, pause_after: Optional[int] = None,
                edit: Optional[Callable[[List[int]], List[int]]] = None, keep_log: bool = False) -> dict:
    """Run one episode.  If pause_after is set, `edit` rewrites the saved state after that stage."""
    sim = Sim(ep)
    state = list(planner.blank)
    all_valid = True
    reload_ok = True
    first_invalid = None
    decisive_stages = []
    gate_arrival = None
    states = []
    log = []
    for s in range(N_STAGES):
        obs = sim.next_obs()
        action = None
        valid = ()
        if s in STAGE_ACTIONS:
            action = planner.propose(state, obs)
            # reload check: a saved and restored state must give the same proposal
            if planner.propose(planner.restore(json.loads(json.dumps(planner.save(state)))), obs) != action:
                reload_ok = False
            valid = sim.valid()
            if sim.decisive():
                decisive_stages.append(s)
            if action not in valid:
                all_valid = False
                if first_invalid is None:
                    first_invalid = s
        new_state = planner.advance(state, obs)
        if action is not None:
            sim.apply(action)
            if s == LEG2:
                gate_arrival = sim.gate
        state = planner.restore(planner.save(new_state))  # everything goes through save/restore
        if pause_after == s and edit is not None:
            state = planner.restore(planner.save(edit(list(state))))
        states.append(list(state))
        if keep_log:
            log.append({"stage": STAGE_NAMES[s], "obs": obs.to_json(), "state_after": list(state),
                        "proposed": None if action is None else ACTIONS[action],
                        "valid": [ACTIONS[a] for a in valid]})
    truth = sim.order
    out = {
        "all_valid": all_valid,
        "first_invalid": first_invalid,
        "reload_ok": reload_ok,
        "gate_arrival": gate_arrival,
        "dock_done": sim.dock_done,
        "bay_done": sim.bay_done,
        "routes": list(sim.routes),
        "gate_ok": truth.gate is None or gate_arrival == truth.gate,
        "dock_ok": sim.dock_done == truth.dock,
        "bay_ok": sim.bay_done == target_bay(truth.bay, sim.closed_bay),
        "closed_bay_end": sim.closed_bay,
        "commit_stage": decisive_stages[0] if decisive_stages else None,   # earliest irreversible gate decision
        "states": states,
    }
    if keep_log:
        out["log"] = log
    return out


def state_at(planner: Planner, ep: Episode, stage: int) -> List[int]:
    return run_episode(planner, ep)["states"][stage]


def run_swap(planner: Planner, target: Episode, donor: Episode, pause_after: int, slots: Sequence[int],
             expect: dict, donor_state: Optional[List[int]] = None) -> dict:
    """Copy `slots` of the donor's saved state into the target's saved state, resume the target."""
    if donor_state is None:
        donor_state = state_at(planner, donor, pause_after)

    def edit(st):
        for i in slots:
            st[i] = donor_state[i]
        return st

    r = run_episode(planner, target, pause_after, edit)
    r["gate_follows"] = r["gate_arrival"] == expect["gate"]
    r["dock_kept"] = r["dock_done"] == expect["dock"]
    r["bay_kept"] = r["bay_done"] == expect["bay"]
    r["credit"] = bool(r["gate_follows"] and r["dock_kept"] and r["bay_kept"])
    return r


def score_item(planner: Planner, item: dict, slots: Optional[Sequence[int]] = None) -> dict:
    kind = item["kind"]
    if kind == "episode":
        r = run_episode(planner, Episode.from_json(item["episode"]))
        return {"credit": bool(r["all_valid"]), "gate_ok": r["gate_ok"], "dock_ok": r["dock_ok"], "bay_ok": r["bay_ok"],
                "reload_ok": r["reload_ok"]}
    if kind == "pair":
        ra = run_episode(planner, Episode.from_json(item["a"]))
        rb = run_episode(planner, Episode.from_json(item["b"]))
        return {"credit": bool(ra["all_valid"] and rb["all_valid"]), "a": bool(ra["all_valid"]), "b": bool(rb["all_valid"]),
                "reload_ok": ra["reload_ok"] and rb["reload_ok"]}
    if kind == "swap":
        if slots is None:
            raise ValueError("swap fixtures need the frozen slot selection")
        r = run_swap(planner, Episode.from_json(item["target"]), Episode.from_json(item["donor"]),
                     STAGE_NAMES.index(item["pause_after"]), slots, item["expect"])
        return {"credit": r["credit"], "gate_follows": r["gate_follows"], "dock_kept": r["dock_kept"],
                "bay_kept": r["bay_kept"], "reload_ok": r["reload_ok"]}
    raise ValueError(kind)


def score_file(planner: Planner, items: Iterable[dict], slots: Optional[Sequence[int]] = None) -> Dict[str, dict]:
    """Credit rate per fixture class."""
    agg: Dict[str, List[int]] = {}
    reload_ok = True
    for it in items:
        r = score_item(planner, it, slots)
        agg.setdefault(it["class"], []).append(int(r["credit"]))
        reload_ok = reload_ok and r.get("reload_ok", True)
    out = {c: {"n": len(v), "credit": sum(v), "rate": sum(v) / len(v)} for c, v in sorted(agg.items())}
    out["_reload_ok"] = reload_ok
    return out


def select_slots(planner: Planner, swap_items: Sequence[dict]) -> dict:
    """The code-selection rule (frozen): try every non-empty set of slots on DEVELOPMENT swap
    fixtures; keep the set with the highest credit; ties go to the smaller set, then the
    lexicographically first.  Returns the choice and the full table."""
    n = planner.n_slots
    table = []
    cache = {}
    for mask in range(1, 2 ** n):
        slots = [i for i in range(n) if mask >> i & 1]
        ok = 0
        for it in swap_items:
            key = json.dumps(it["donor"], sort_keys=True)
            p = STAGE_NAMES.index(it["pause_after"])
            if key not in cache:
                cache[key] = state_at(planner, Episode.from_json(it["donor"]), p)
            ok += run_swap(planner, Episode.from_json(it["target"]), Episode.from_json(it["donor"]), p, slots,
                           it["expect"], cache[key])["credit"]
        table.append({"slots": slots, "rate": ok / max(1, len(swap_items))})
    best = sorted(table, key=lambda t: (-t["rate"], len(t["slots"]), t["slots"]))[0]
    return {"slots": best["slots"], "dev_rate": best["rate"], "table": table}
