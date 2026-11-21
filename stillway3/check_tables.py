"""Check a certified planner's tables with nothing but Python.  No torch, no project imports.

    python stillway3/check_tables.py results/v03/cert/v3r24fix_s1_tables.json [same|all]

Written separately from stillway3/certify.py on purpose (other data structures, other order of work), so two
implementations have to agree.  It also re-derives the exact planner here: gates are plain tuples, a trip is
(effect, gate), a job is a list of legs, and the reference lists EVERY route choice of a short job.

The tables file holds four integer tables read off a network:
  term[q0][q1]            -> code          start of the backward sweep, from the two gate requirements (0 none, 1 closed, 2 open)
  cell[code][leg]         -> code          one leg further back      (leg = trip_a * 8 + trip_b, trip = effect * 2 + gate)
  route[code][leg][gates] -> 0 or 1        the route proposed at the current leg (gates = gate0 * 2 + gate1)
  deliver[parcel][closed+1] -> dock

Three checks:
  1. closure      the any-length argument: every (code, exact value table) pair that can occur, every leg, every gate state
  2. brute force  every job of up to 3 legs over the alphabet, every requirement and gate state, against a
                  reference that lists every route choice (no value table involved)
  3. deliveries   all 12 entries
"""
import json, sys
from itertools import product

EFFECT = {0: lambda g: g, 1: lambda g: 1 - g, 2: lambda g: 1, 3: lambda g: 0}          # keep, toggle, open, close


def take(gates, trip):
    effect, gate = divmod(trip, 2); g = list(gates); g[gate] = EFFECT[effect](g[gate]); return tuple(g)


def met(gates, req):
    return sum(1 for k in (0, 1) if req[k] and gates[k] == req[k] - 1)


def best_by_listing(req, gates, legs):
    """Most requirements that can be met, by listing every route choice.  legs: [(trip_a, trip_b), ...]."""
    if not legs: return met(gates, req)
    return max(best_by_listing(req, take(gates, t), legs[1:]) for t in legs[0])


def valid_by_listing(req, gates, legs):
    v = [best_by_listing(req, take(gates, t), legs[1:]) for t in legs[0]]
    return {r for r in (0, 1) if v[r] == max(v)}


def planner_route(tab, req, gates, legs):
    code = tab["term"][req[0]][req[1]]
    for a, b in reversed(legs[1:]): code = tab["cell"][code][a * 8 + b]
    a, b = legs[0]
    return tab["route"][code][a * 8 + b][gates[0] * 2 + gates[1]]


def alphabet(name):
    legs = [(a, b) for a in range(8) for b in range(8)]
    return legs if name == "all" else [(a, b) for a, b in legs if a % 2 == b % 2]


def closure(tab, legs):
    GATES = [(0, 0), (0, 1), (1, 0), (1, 1)]
    def table_of(req): return tuple(met(g, req) for g in GATES)
    def back(T, leg): return tuple(max(T[GATES.index(take(g, leg[0]))], T[GATES.index(take(g, leg[1]))]) for g in GATES)
    seen = {(tab["term"][q0][q1], table_of((q0, q1))) for q0 in range(3) for q1 in range(3)}; todo = list(seen)
    while todo:
        code, T = todo.pop()
        for leg in legs:
            nxt = (tab["cell"][code][leg[0] * 8 + leg[1]], back(T, leg))
            if nxt not in seen: seen.add(nxt); todo.append(nxt)
    checks = wrong = 0
    for code, T in seen:
        for leg in legs:
            for gi, g in enumerate(GATES):
                v = [T[GATES.index(take(g, t))] for t in leg]; checks += 1
                wrong += v[tab["route"][code][leg[0] * 8 + leg[1]][gi]] != max(v)
    return len(seen), checks, wrong


def brute(tab, legs, max_legs=3):
    checks = wrong = 0
    for n in range(1, max_legs + 1):
        for job in product(legs, repeat=n):
            for req in product(range(3), repeat=2):
                for g in product((0, 1), repeat=2):
                    checks += 1; wrong += planner_route(tab, req, g, list(job)) not in valid_by_listing(req, g, list(job))
    return checks, wrong


def main():
    tab = json.load(open(sys.argv[1])); name = sys.argv[2] if len(sys.argv) > 2 else "all"; legs = alphabet(name)
    pairs, c1, w1 = closure(tab, legs)
    print(f"closure ({name}, {len(legs)} leg kinds): {pairs} (code, value table) pairs, {c1} route checks, {w1} wrong")
    depth = 3 if name == "same" else 2                                # all: 64^3 jobs is 9.4 million route listings; 2 legs is enough for a spot check
    c2, w2 = brute(tab, legs, depth)
    print(f"brute force, every job of up to {depth} legs: {c2} checks, {w2} wrong")
    w3 = sum(tab["deliver"][p][c + 1] != (p if p != c else (p + 1) % 3) for p in range(3) for c in (-1, 0, 1, 2))
    print(f"deliveries: 12 checks, {w3} wrong")
    ok = w1 == 0 and w2 == 0 and w3 == 0
    print("CERTIFIED for every number of legs" if ok else "NOT certified"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
