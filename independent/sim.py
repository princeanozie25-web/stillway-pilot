#!/usr/bin/env python3
"""Clean-room Dispatch-2 simulator and exact planner.

Written from docs/evaluator_spec.md alone (sections 1 to 3 and the event
encoding table). Standard library only.

Usage: python3 independent/sim.py
Reads  fixtures/dev/dev_in.jsonl and fixtures/dev/dev_out.jsonl
Writes independent/outcomes.jsonl
"""
import json
import os
import sys
from collections import Counter

STAGES = ["INIT", "PLAN", "LEG1", "DOCK", "LEG2", "BAY"]
ACTION_ORDER = ["L", "R", "D0", "D1", "B0", "B1", "B2"]
ROUTES = ["L", "R"]


def apply_trip(trip, gate):
    """K keep, T toggle, O force open (1), C force closed (0)."""
    if trip == "K":
        return gate
    if trip == "T":
        return 1 - gate
    if trip == "O":
        return 1
    if trip == "C":
        return 0
    raise ValueError("unknown trip %r" % (trip,))


class World:
    def __init__(self, ep):
        lay = ep["layout"]
        self.leg1 = {"L": lay["leg1"]["L"], "R": lay["leg1"]["R"]}
        self.leg2 = {"L": lay["leg2"]["L"], "R": lay["leg2"]["R"]}
        self.gate = ep["gate0"]
        self.decor = ep.get("decor", 0)
        self.closed_bay = ep.get("closed_bay")  # None means no bay closed
        o = ep["order"]
        self.order = {"dock": o["dock"], "gate": o["gate"], "bay": o["bay"]}
        if self.gate not in (0, 1) or self.order["gate"] not in (0, 1):
            raise ValueError("gate values must be 0 or 1")

    def apply_event(self, ev):
        name = ev[0]
        if name == "rev":
            leg = {1: self.leg1, 2: self.leg2}[ev[1]]
            leg["L"], leg["R"] = leg["R"], leg["L"]
        elif name == "gflip":
            self.gate = 1 - self.gate
        elif name == "decor":
            self.decor = ev[1]
        elif name == "close":
            self.closed_bay = None if ev[1] == -1 else ev[1]
        elif name == "msg":
            field, v = ev[1], ev[2]
            if field not in self.order:
                raise ValueError("unknown order field %r" % (field,))
            self.order[field] = v
        elif name == "full":
            pass  # only changes what is shown, not the world
        else:
            raise ValueError("unknown event %r" % (ev,))

    # ---- exact planner: valid sets, judged against the world as it is now
    def valid(self, stage):
        need = self.order["gate"]
        if stage == "LEG1":
            ok = []
            for r in ROUTES:
                g1 = apply_trip(self.leg1[r], self.gate)
                if any(apply_trip(self.leg2[r2], g1) == need for r2 in ROUTES):
                    ok.append(r)
            return ok if ok else list(ROUTES)
        if stage == "LEG2":
            ok = [r for r in ROUTES if apply_trip(self.leg2[r], self.gate) == need]
            return ok if ok else list(ROUTES)
        if stage == "DOCK":
            return ["D%d" % self.order["dock"]]
        if stage == "BAY":
            b = self.order["bay"]
            if self.closed_bay is not None and b == self.closed_bay:
                b = (b + 1) % 3
            return ["B%d" % b]
        raise ValueError(stage)

    def act(self, stage, action):
        if stage == "LEG1":
            self.gate = apply_trip(self.leg1[action], self.gate)
        elif stage == "LEG2":
            self.gate = apply_trip(self.leg2[action], self.gate)


def simulate(ep):
    w = World(ep)
    by_stage = {s: [] for s in STAGES}
    for e in ep.get("events", []):
        if e["stage"] not in by_stage:
            raise ValueError("unknown stage %r" % (e["stage"],))
        by_stage[e["stage"]].append(e["event"])  # listed order kept per stage

    valid_sets, actions = [], []
    gate_arrival = dock = bay = None
    commit_stage = None
    for stage in STAGES:
        for ev in by_stage[stage]:
            w.apply_event(ev)
        if stage in ("INIT", "PLAN"):
            continue
        v = sorted(w.valid(stage), key=ACTION_ORDER.index)
        a = v[0]  # lowest-index valid action in the fixed order
        valid_sets.append(v)
        actions.append(a)
        if stage in ("LEG1", "LEG2") and commit_stage is None and len(v) == 1:
            commit_stage = stage
        w.act(stage, a)
        if stage == "LEG2":
            gate_arrival = w.gate
        elif stage == "DOCK":
            dock = int(a[1])
        elif stage == "BAY":
            bay = int(a[1])
    return {
        "valid": valid_sets,
        "actions": actions,
        "gate_arrival": gate_arrival,
        "dock": dock,
        "bay": bay,
        "commit_stage": commit_stage,
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    inputs = [
        os.path.join(root, "fixtures", "dev", "dev_in.jsonl"),
        os.path.join(root, "fixtures", "dev", "dev_out.jsonl"),
    ]
    out_path = os.path.join(here, "outcomes.jsonl")
    n = 0
    kinds = Counter()
    init_events = 0
    with open(out_path, "w") as out:
        for path in inputs:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    item = json.loads(line)
                    kind = item.get("kind")
                    kinds[kind] += 1
                    if kind == "episode":
                        runs = [("episode", item["episode"])]
                    elif kind == "pair":
                        runs = [("a", item["a"]), ("b", item["b"])]
                    else:
                        continue
                    for run, ep in runs:
                        init_events += sum(
                            1 for e in ep.get("events", []) if e["stage"] == "INIT"
                        )
                        rec = {"id": item["id"], "run": run}
                        rec.update(simulate(ep))
                        out.write(json.dumps(rec) + "\n")
                        n += 1
    sys.stderr.write(
        "runs written: %d\nitem kinds: %s\nevents at INIT: %d\n"
        % (n, dict(kinds), init_events)
    )


if __name__ == "__main__":
    main()
