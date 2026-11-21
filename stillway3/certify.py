"""Certificate for a v0.3 core, for jobs of ANY number of legs.

    python -m stillway3.certify runs/v3r23_s1 [--witness 20]

Idea.  The reader carries one of at most 64 codes from leg to leg, and the exact planner carries one value
table (4 joint gate states x counts 0..2).  Run both together:
  start     every pair of gate requirements (3 x 3)        -> (code, exact table)
  one leg   every (code, exact table) x every leg kind     -> (code, exact table)
until no new (code, exact table) pair appears.  The set is finite, so this ends.  Every pair that can occur
behind the current leg of any job, however long, is then in the list.  For every such pair, every kind of
current leg and every gate state, the route the planner proposes is compared with the exact planner.

What a clean result covers: every job of every length built from the leg kinds in the alphabet, every gate
requirement, every gate state, every event (events change the observation or a register, and the route
depends on nothing else).  Deliveries are a 12-entry table (3 docks x 4 closed-bay states), checked in full.
Registers are written by rule; tests/test_regcore.py checks the rule.

Alphabets:  "same"  both routes of a leg act on one gate (32 leg kinds, the v0.2 training distribution)
            "all"   every pair of trips (64 leg kinds)

Margins.  `min_margin` is the smallest gap to a tie over everything the closure touches: between the two
nearest codes (term, cell) and between the two routes.  A route gap of zero is harmless when both routes are
valid; `route_when_one_route_is_valid` is the gap where it matters.

The check is made on TABLES read off the network (stillway3.certify.extract).  The same tables run as a
planner without the network (TablePlanner); tests/test_regcore.py checks that tables and network agree on
sampled jobs, and `margins` reports how far every decision is from a tie.
"""
from __future__ import annotations

import argparse, json, os, sys, time
from itertools import product

import torch

from stillway2.world3 import DELIVER, ROUTE, ref_dock, ref_valid_routes

EFF = ((0, 1), (1, 0), (1, 1), (0, 0)); JOINT = [(0, 0), (0, 1), (1, 0), (1, 1)]
TRIPS = [(e, g) for e in range(4) for g in range(2)]                       # trip index = effect * 2 + gate
LEGS_ALL = [(a, b) for a in range(8) for b in range(8)]                    # leg kind index = a * 8 + b
LEGS_SAME = [(a, b) for (a, b) in LEGS_ALL if TRIPS[a][1] == TRIPS[b][1]]


def nxt(s: int, trip: int) -> int:
    e, g = TRIPS[trip]; x = list(JOINT[s]); x[g] = EFF[e][x[g]]; return x[0] * 2 + x[1]


def term_table(q0: int, q1: int):
    return tuple(int(q0 > 0 and g[0] == q0 - 1) + int(q1 > 0 and g[1] == q1 - 1) for g in JOINT)


def back(T, leg):
    a, b = leg; return tuple(max(T[nxt(s, a)], T[nxt(s, b)]) for s in range(4))


def valid_routes(T, leg, s):
    va, vb = T[nxt(s, leg[0])], T[nxt(s, leg[1])]; m = max(va, vb)
    return tuple(r for r, v in ((0, va), (1, vb)) if v == m)


def desc_vec(leg) -> torch.Tensor:
    v = torch.zeros(10)
    for r, t in enumerate(leg):
        e, g = TRIPS[t]; v[5 * r + e] = 1.0; v[5 * r + 4] = float(g)
    return v


@torch.no_grad()
def extract(model) -> dict:
    """Read the four learned functions off the network as integer tables, with the margin of every entry."""
    model.eval(); K = model.cfg.n_codes; cb = model.codebook
    def snap(z):
        z = torch.tanh(z); d = torch.cdist(z, cb); top = d.topk(2, largest=False)
        return top.indices[:, 0], (top.values[:, 1] - top.values[:, 0])
    r = torch.arange(4)
    z = model.term(torch.cat([model.emb_req(r.repeat_interleave(4)), model.emb_req(r.repeat(4))], 1))
    term, m_term = snap(z)
    D = torch.stack([desc_vec(l) for l in LEGS_ALL])                                        # (64,10)
    cin = torch.cat([cb[:, None, :].expand(K, 64, -1), D[None].expand(K, 64, -1)], 2).reshape(K * 64, -1)
    cell, m_cell = snap(model.cell(cin))
    G = torch.tensor(JOINT).float()
    rin = torch.cat([cb[:, None, None, :].expand(K, 64, 4, -1), D[None, :, None, :].expand(K, 64, 4, -1), G[None, None].expand(K, 64, 4, -1)], 3).reshape(K * 256, -1)
    rl = model.route(rin)
    if model.cfg.route_out != 2:
        from .model import expected_count; rl = expected_count(rl)
    din = torch.cat([model.emb_par(r.repeat_interleave(4)), torch.eye(4).repeat(4, 1)], 1)
    dl = model.deliver(din); d2 = dl.topk(2, dim=1).values
    return {"term": term.view(4, 4).tolist(), "cell": cell.view(K, 64).tolist(), "route": rl.argmax(1).view(K, 64, 4).tolist(),
            "deliver": dl.argmax(1).view(4, 4).tolist(), "n_codes": K,
            "margin": {"term": m_term.view(4, 4), "cell": m_cell.view(K, 64), "route": (rl[:, 0] - rl[:, 1]).abs().view(K, 64, 4), "deliver": (d2[:, 0] - d2[:, 1]).view(4, 4)}}


def certify(tab: dict, alphabet: str = "all", max_witness: int = 20, rehearsal: int = 0, rng=None) -> dict:
    """rehearsal > 0: also return that many randomly chosen RIGHT entries as jobs (used by the repair loop)."""
    legs = LEGS_ALL if alphabet == "all" else LEGS_SAME
    t0 = time.time(); parent = {}; front = []
    for q0, q1 in product(range(3), repeat=2):
        p = (tab["term"][q0][q1], term_table(q0, q1))
        if p not in parent: parent[p] = (None, (q0, q1)); front.append(p)
    depth = 0; by_depth = [len(front)]
    while front:
        new = []
        for (c, T) in front:
            for leg in legs:
                p = (tab["cell"][c][leg[0] * 8 + leg[1]], back(T, leg))
                if p not in parent: parent[p] = ((c, T), leg); new.append(p)
        front = new
        if new: depth += 1; by_depth.append(len(new))
    def path(p):
        out = []
        while parent[p][0] is not None: out.append(parent[p][1]); p = parent[p][0]
        return parent[p][1], out                                       # (gate requirements, legs from the current leg outwards)
    def job(c, T, leg, s, a):
        q, tail = path((c, T))
        return {"gate_requirements": list(q), "current_leg": list(leg), "legs_after": [list(l) for l in tail], "gates": list(JOINT[s]),
                "proposed_route": a, "valid_routes": list(valid_routes(T, leg, s))}
    right = []
    checks = wrong = 0; witnesses = []; min_margin = {"term": float("inf"), "cell": float("inf"), "route": float("inf"), "route_when_one_route_is_valid": float("inf")}
    mg = tab.get("margin")
    for (c, T) in parent:
        for leg in legs:
            li = leg[0] * 8 + leg[1]
            if mg is not None: min_margin["cell"] = min(min_margin["cell"], float(mg["cell"][c][li]))
            for s in range(4):
                checks += 1; a = tab["route"][c][li][s]
                if mg is not None:
                    min_margin["route"] = min(min_margin["route"], float(mg["route"][c][li][s]))
                    if len(valid_routes(T, leg, s)) == 1: min_margin["route_when_one_route_is_valid"] = min(min_margin["route_when_one_route_is_valid"], float(mg["route"][c][li][s]))
                if a not in valid_routes(T, leg, s):
                    wrong += 1
                    if len(witnesses) < max_witness: witnesses.append(job(c, T, leg, s, a))
                elif rehearsal: right.append((c, T, leg, s, a))
    if mg is not None:
        for q0, q1 in product(range(3), repeat=2): min_margin["term"] = min(min_margin["term"], float(mg["term"][q0][q1]))
    dchecks = dwrong = 0
    for p in range(3):
        for cl in range(4):                                            # closed-bay one-hot index: 0 = none, 1..3 = bay 0..2
            dchecks += 1; dwrong += tab["deliver"][p][cl] != ref_dock(p, cl - 1)
    codes = {}
    for (c, T) in parent: codes.setdefault(c, set()).add(T)
    return {"alphabet": alphabet, "leg_kinds": len(legs), "pairs": len(parent), "pairs_by_depth": by_depth, "closure_depth": depth,
            "codes_used": len(codes), "exact_tables_reached": len({T for (_, T) in parent}), "codes_standing_for_two_tables": sum(1 for v in codes.values() if len(v) > 1),
            "route_checks": checks, "route_wrong": wrong, "deliver_checks": dchecks, "deliver_wrong": dwrong,
            "min_margin": {k: (round(v, 5) if v != float("inf") else None) for k, v in min_margin.items()},
            "witnesses": witnesses, "seconds": round(time.time() - t0, 2),
            **({"rehearsal": [job(*right[i]) for i in rng.sample(range(len(right)), min(rehearsal, len(right)))]} if rehearsal else {})}


class TablePlanner:
    """The certified tables run as a planner.  No network, integers only."""
    def __init__(self, tab: dict): self.t = tab

    def route(self, q, gates, legs_ahead):
        """q: gate-requirement registers; legs_ahead: [(trip a, trip b), ...] starting with the current leg."""
        c = self.t["term"][q[0]][q[1]]
        for (a, b) in reversed(legs_ahead[1:]): c = self.t["cell"][c][a * 8 + b]
        a, b = legs_ahead[0]
        return self.t["route"][c][a * 8 + b][gates[0] * 2 + gates[1]]

    def dock(self, parcel, closed): return self.t["deliver"][parcel][closed + 1]


@torch.no_grad()
def replay_witness(model, wit: dict) -> dict:
    """Build the witness as a real job, show it to the NETWORK through the simulator, compare with the plain reference."""
    from .world import WorldN
    legs = [tuple(wit["current_leg"])] + [tuple(l) for l in wit["legs_after"]]; L = len(legs); M = max(L, 2)
    spec = dict(L=(L,), cross=0.0, split=None, K=0, p_wait=0.0, rev=0, gflip=0, decor=0, close=0, msg=0, full=0, reissue=0, env="model")
    w = WorldN(1, spec, torch.Generator().manual_seed(0), lmax=M)
    for i, (a, b) in enumerate(legs):
        w.eff[0, i, 0], w.tg[0, i, 0] = TRIPS[a]; w.eff[0, i, 1], w.tg[0, i, 1] = TRIPS[b]
    w.parcel[:] = False; w.q[0] = torch.tensor(wit["gate_requirements"]); w.gates[0] = torch.tensor(wit["gates"])
    ids = torch.full((1, w.NF), -1); obs, _ = w.next_obs(); _, ids = model.infer(ids, obs)
    obs, act = w.next_obs(); assert w.slot(w.t)[0] == ROUTE and bool(act[0])
    logits, _ = model.infer(ids, obs); a = int(logits[0, :2].argmax())
    ref = ref_valid_routes(L, w.eff[0].tolist(), w.tg[0].tolist(), wit["gates"], wit["gate_requirements"], 0)
    return {"legs": L, "network_route": a, "reference_valid": list(ref), "network_wrong": a not in ref, "table_route": wit["proposed_route"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--witness", type=int, default=20); ap.add_argument("--out", default="results/v03/cert")
    a = ap.parse_args(); from .model import load_reg
    run = a.run.rstrip("/"); name = os.path.basename(run); model = load_reg(os.path.join(run, "checkpoint.pt"))
    if model.cfg.carry != "vq": sys.exit("continuous carry: no finite machine to list")
    tab = extract(model); out = {"run": name, "checkpoint_sha256": model.sha256}
    for alpha in ("same", "all"):
        c = certify(tab, alpha, a.witness); c["witness_replays"] = [replay_witness(model, w) for w in c["witnesses"]]
        out[alpha] = c
        print(name, alpha, {k: c[k] for k in ("pairs", "closure_depth", "codes_used", "exact_tables_reached", "route_checks", "route_wrong", "deliver_wrong", "min_margin")},
              "witnesses confirmed on the network:", sum(r["network_wrong"] for r in c["witness_replays"]), "of", len(c["witness_replays"]), flush=True)
    os.makedirs(a.out, exist_ok=True)
    json.dump({k: v for k, v in tab.items() if k != "margin"}, open(os.path.join(a.out, f"{name}_tables.json"), "w"))
    json.dump(out, open(os.path.join(a.out, f"{name}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
