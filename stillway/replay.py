"""The decisive paired replay and its controls.

For every swap fixture (target, donor, pause after PLAN) we run:

  unchanged x2   resume the saved state twice: same proposals, same outcome?
  targeted       copy the SELECTED slots donor -> target        (primary endpoint)
  shuffled       same slots, but from a random other run         (control for the primary endpoint)
  same_goal      same slots from a donor with the SAME gate obligation (should change nothing)
  complement     copy the NON-selected slots from the true donor (nonspecific disruption)
  blank          wipe the memory                                 (does behaviour depend on memory?)
  transplant     copy the WHOLE state                            (diagnostic only)
  decor          repaint a decoration after the pause            (unnecessary plan changes)
  message        tell the planner the revised obligation through the normal input
  restart        wipe memory and re-issue the full revised order (matched restart)

Credit for targeted / shuffled / transplant / message / restart is the same three-part test:
gate on arrival == donor's obligation, parcel 1 at the target's dock, parcel 2 at the target's bay.
"""
from __future__ import annotations

import json
import random
from typing import Dict, List, Sequence

import numpy as np

from .planners import Planner
from .scorer import run_episode, run_swap, state_at
from .world import Episode, STAGE_NAMES


def _three(r: dict, expect: dict) -> dict:
    g = r["gate_arrival"] == expect["gate"]
    d = r["dock_done"] == expect["dock"]
    b = r["bay_done"] == expect["bay"]
    return {"credit": bool(g and d and b), "gate": bool(g), "dock": bool(d), "bay": bool(b)}


def replay_item(planner: Planner, item: dict, slots: Sequence[int], pool: Sequence[dict], rng: random.Random) -> dict:
    T, S = Episode.from_json(item["target"]), Episode.from_json(item["donor"])
    p = STAGE_NAMES.index(item["pause_after"])
    exp = item["expect"]
    own = {"gate": T.order.gate, "dock": exp["dock"], "bay": exp["bay"]}       # the target's own obligations
    n = planner.n_slots
    comp = [i for i in range(n) if i not in slots]
    row = {"id": item["id"], "family": item["family"], "pair": item["pair"]}

    base = run_episode(planner, T)
    again = run_episode(planner, T, p, lambda st: planner.restore(json.loads(json.dumps(planner.save(st)))))
    row["unchanged"] = _three(base, own)
    row["unchanged"]["all_valid"] = bool(base["all_valid"])
    row["resume_same"] = bool(base["routes"] == again["routes"] and base["dock_done"] == again["dock_done"]
                              and base["bay_done"] == again["bay_done"] and base["states"] == again["states"])
    row["donor_unchanged_valid"] = bool(run_episode(planner, S)["all_valid"])

    row["targeted"] = _three(run_swap(planner, T, S, p, slots, exp), exp)
    other = rng.choice(pool)
    row["shuffled"] = _three(run_swap(planner, T, Episode.from_json(other["donor"]), p, slots, exp), exp)
    same = rng.choice([o for o in pool if o["donor"]["order"]["gate"] == T.order.gate])
    row["same_goal"] = _three(run_swap(planner, T, Episode.from_json(same["donor"]), p, slots, own), own)
    if comp:
        r = run_swap(planner, T, S, p, comp, exp)
        row["complement"] = {"gate_follows_donor": bool(r["gate_arrival"] == exp["gate"]),
                             "gate_stays_target": bool(r["gate_arrival"] == T.order.gate),
                             "dock_kept": bool(r["dock_done"] == exp["dock"]), "bay_kept": bool(r["bay_done"] == exp["bay"])}
    row["blank"] = _three(run_episode(planner, T, p, lambda st: list(planner.blank)), own)
    row["transplant"] = _three(run_swap(planner, T, S, p, list(range(n)), exp), exp)

    # decoration repaint right after the pause: nothing about the plan should change
    Td = Episode.from_json(item["target"])
    Td.events = {p + 1: [("decor", (T.decor + 1 + rng.randrange(3)) % 4)]}
    rd = run_episode(planner, Td)
    ham = [sum(x != y for x, y in zip(a, b)) for a, b in zip(base["states"][p + 1:], rd["states"][p + 1:])]
    row["decor"] = {"same_actions": bool(rd["routes"] == base["routes"] and rd["dock_done"] == base["dock_done"]
                                         and rd["bay_done"] == base["bay_done"]),
                    "still_valid": bool(rd["all_valid"]), "slots_changed_next": int(ham[0]), "slots_changed_mean": float(np.mean(ham))}

    # the revised obligation arrives as an ordinary operator message
    Tm = Episode.from_json(item["target"])
    Tm.events = {p + 1: [("msg", "gate", exp["gate"])]}
    rm = run_episode(planner, Tm)
    row["message"] = _three(rm, exp)
    hm = sum(x != y for x, y in zip(base["states"][p + 1], rm["states"][p + 1]))
    row["message"]["slots_changed"] = int(hm)

    # matched restart: memory wiped, the whole revised order is re-issued
    Tr = Episode.from_json(item["target"])
    Tr.events = {p + 1: [("msg", "gate", exp["gate"]), ("full",)]}
    row["restart"] = _three(run_episode(planner, Tr, p, lambda st: list(planner.blank)), exp)
    return row


def replay_all(planner: Planner, items: Sequence[dict], slots: Sequence[int], seed: int = 0) -> List[dict]:
    rng = random.Random(seed)
    swaps = [i for i in items if i["kind"] == "swap"]
    return [replay_item(planner, it, slots, swaps, rng) for it in swaps]


def _rate(rows, key, field="credit"):
    return float(np.mean([r[key][field] for r in rows]))


def cluster_boot(values: np.ndarray, clusters: Sequence[str], n_boot: int = 4000, seed: int = 0):
    """Mean with a 95% interval from resampling whole layout families."""
    rng = np.random.default_rng(seed)
    names = sorted(set(clusters))
    idx = {c: np.array([i for i, x in enumerate(clusters) if x == c]) for c in names}
    means = []
    for _ in range(n_boot):
        pick = rng.choice(len(names), len(names), replace=True)
        v = np.concatenate([values[idx[names[k]]] for k in pick])
        means.append(v.mean())
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(values.mean()), float(lo), float(hi)


def summarise(rows: List[dict]) -> dict:
    fam = [r["family"] for r in rows]
    t = np.array([r["targeted"]["credit"] for r in rows], dtype=float)
    s = np.array([r["shuffled"]["credit"] for r in rows], dtype=float)
    diff = cluster_boot(t - s, fam)
    tgt = cluster_boot(t, fam)
    unrel_swap = np.array([r["targeted"]["dock"] and r["targeted"]["bay"] for r in rows], dtype=float)
    unrel_base = np.array([r["unchanged"]["dock"] and r["unchanged"]["bay"] for r in rows], dtype=float)
    drop = cluster_boot(unrel_base - unrel_swap, fam)
    out = {
        "n_items": len(rows), "n_pairs": len({r["pair"] for r in rows}), "n_families": len(set(fam)),
        "primary_targeted_credit": {"mean": tgt[0], "ci95": [tgt[1], tgt[2]]},
        "shuffled_credit": float(s.mean()),
        "paired_improvement_over_shuffled": {"mean": diff[0], "ci95": [diff[1], diff[2]]},
        "unrelated_obligation_drop_vs_unchanged": {"mean": drop[0], "ci95": [drop[1], drop[2]]},
        "both_unmodified_runs_valid": float(np.mean([r["unchanged"]["all_valid"] and r["donor_unchanged_valid"] for r in rows])),
        "resume_twice_identical": float(np.mean([r["resume_same"] for r in rows])),
        "targeted_parts": {k: _rate(rows, "targeted", k) for k in ("gate", "dock", "bay")},
        "same_goal_donor_stable": _rate(rows, "same_goal"),
        "blank_memory": {k: _rate(rows, "blank", k) for k in ("credit", "gate", "dock", "bay")},
        "whole_state_transplant": {k: _rate(rows, "transplant", k) for k in ("credit", "gate", "dock", "bay")},
        "decor": {"same_actions": _rate(rows, "decor", "same_actions"), "still_valid": _rate(rows, "decor", "still_valid"),
                  "slots_changed_next_step": _rate(rows, "decor", "slots_changed_next"),
                  "slots_changed_mean": _rate(rows, "decor", "slots_changed_mean")},
        "message_revision": {"credit": _rate(rows, "message"), "slots_changed": _rate(rows, "message", "slots_changed")},
        "restart_full_order": _rate(rows, "restart"),
    }
    if "complement" in rows[0]:
        out["complement_slots"] = {k: _rate(rows, "complement", k) for k in rows[0]["complement"]}
    return out
