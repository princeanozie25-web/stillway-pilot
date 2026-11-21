"""Dispatch route planning for G gates (v0.4, M1): exact reverse dynamic program, its compiled tables,
and the closure certificate for a learned table set.

World (route core of Dispatch-3, any number of gates G):
  * G gates, each 0 (closed) or 1 (open).  Joint state index s = sum(gate_g << (G-1-g)).
  * A trip is (effect, gate): effect 0 keep, 1 toggle, 2 open, 3 close.  Trip index t = effect * G + gate; NT = 4G.
  * A leg has two routes, each one trip.  Leg kind = trip_a * NT + trip_b; NL = NT * NT.
  * Requirements q_g in {0 none, 1 must end closed, 2 must end open}.  Requirement index = sum(q_g * 3^(G-1-g)).
  * Exact planner: at a leg, a route is valid when it keeps the largest reachable number of requirements met.
Deliveries, waits and events are not part of this module: v0.3 showed they never enter a route decision when
the order is held in registers written by rule.

Exact value vector: T[s] = most requirements that can still be met from joint state s over the legs behind.
One leg further back: T'[s] = max(T[next(s, trip_a)], T[next(s, trip_b)]).

Table file format (the SAME for exact and learned tables; read by v04/runner.c):
  int32 x 6: magic 0x53544c57, G, n_codes, NL, NS, code_bytes (2 or 4)
  term [3^G] codes, cell [n_codes * NL] codes, route [n_codes * NL * NS] uint8 (the route proposed: 0 or 1)
"""
from __future__ import annotations

import os, resource, struct, time
from itertools import product

import numpy as np

MAGIC = 0x53544C57


class Gates:
    def __init__(self, G: int):
        self.G, self.NS, self.NT = G, 2 ** G, 4 * G; self.NL = self.NT * self.NT; self.NQ = 3 ** G
        st = np.array(list(product((0, 1), repeat=G)), dtype=np.int64); self.states = st; w = 2 ** np.arange(G - 1, -1, -1)
        nx = []
        for e in range(4):
            for g in range(G):
                s = st.copy(); s[:, g] = [s[:, g], 1 - s[:, g], np.ones(self.NS, np.int64), np.zeros(self.NS, np.int64)][e]; nx.append((s * w).sum(1))
        self.NX = np.array(nx)                                           # (NT, NS): joint state after a trip
        self.reqs = np.array(list(product(range(3), repeat=G)), dtype=np.int64)       # (NQ, G)
        self.term = ((self.reqs[:, None, :] > 0) & (st[None] == self.reqs[:, None, :] - 1)).sum(2).astype(np.uint8)   # (NQ, NS)

    def back(self, T: np.ndarray, a: int, b: int) -> np.ndarray:
        return np.maximum(T[:, self.NX[a]], T[:, self.NX[b]])

    # -- exact reverse dynamic program, to a fixed point --------------------------------------------------
    def exact_closure(self, max_seconds: float = 3600.0, max_bytes: float = 4e9, ckpt: str | None = None) -> dict:
        """Every value vector that can occur behind a leg of any job.  Returns vectors (N, NS), growth by depth, cost."""
        t0 = time.time(); V = np.unique(self.term, axis=0); ids = {v.tobytes(): i for i, v in enumerate(V)}; allv = [V]; front = V
        growth = [len(V)]; pairs = [(a, b) for a in range(self.NT) for b in range(a, self.NT)]; complete = True
        while len(front):
            new = []
            for (a, b) in pairs:
                for w in np.unique(self.back(front, a, b), axis=0):
                    k = w.tobytes()
                    if k not in ids: ids[k] = len(ids); new.append(w)
                rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                if time.time() - t0 > max_seconds or rss > max_bytes: complete = False; break
            front = np.array(new, dtype=np.uint8) if new else np.zeros((0, self.NS), np.uint8)
            if len(front): allv.append(front); growth.append(len(front))
            if ckpt: np.savez_compressed(ckpt, vectors=np.concatenate(allv), frontier=front, growth=np.array(growth), complete=complete)
            if not complete: break
        V = np.concatenate(allv)
        return {"G": self.G, "vectors": V, "ids": ids, "growth_by_depth": growth, "depth": len(growth) - 1, "complete": complete,
                "seconds": time.time() - t0, "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}

    def compile_exact(self, clo: dict) -> dict:
        """Integer tables of the exact planner: term (NQ), cell (N, NL), valid (N, NL, NS) bit 0 = route 0 valid, bit 1 = route 1 valid."""
        t0 = time.time(); V, ids = clo["vectors"], clo["ids"]; N = len(V)
        cell = np.zeros((N, self.NL), np.int32); valid = np.zeros((N, self.NL, self.NS), np.uint8)
        for a in range(self.NT):
            va = V[:, self.NX[a]]
            for b in range(self.NT):
                vb = V[:, self.NX[b]]; W = np.maximum(va, vb); u, inv = np.unique(W, axis=0, return_inverse=True)
                cell[:, a * self.NT + b] = np.array([ids[x.tobytes()] for x in u], np.int32)[inv.ravel()]
                valid[:, a * self.NT + b] = (va >= vb).astype(np.uint8) | ((vb >= va).astype(np.uint8) << 1)
        term = np.array([ids[x.tobytes()] for x in self.term], np.int32)
        return {"G": self.G, "n_codes": N, "term": term, "cell": cell, "valid": valid, "route": (valid == 2).astype(np.uint8), "compile_seconds": time.time() - t0}

    # -- brute force, independent of value vectors (for witnesses and mutation tests) ---------------------
    def brute_valid(self, q, gates_s: int, legs) -> tuple:
        """Valid routes at the first leg by listing every route choice.  legs: [leg kind, ...]."""
        def best(s, rest):
            if not rest: return int(self.term[q][s])
            a, b = divmod(rest[0], self.NT); return max(best(self.NX[a][s], rest[1:]), best(self.NX[b][s], rest[1:]))
        a, b = divmod(legs[0], self.NT); va, vb = best(self.NX[a][gates_s], legs[1:]), best(self.NX[b][gates_s], legs[1:])
        return tuple(r for r, v in ((0, va), (1, vb)) if v == max(va, vb))


def write_tables(path: str, G: int, term, cell, route) -> int:
    n = cell.shape[0]; cb = 2 if n <= 65535 else 4; dt = np.uint16 if cb == 2 else np.uint32
    with open(path, "wb") as f:
        f.write(struct.pack("<6i", MAGIC, G, n, cell.shape[1], 2 ** G, cb))
        f.write(np.ascontiguousarray(term, dtype=dt).tobytes()); f.write(np.ascontiguousarray(cell, dtype=dt).tobytes()); f.write(np.ascontiguousarray(route, dtype=np.uint8).tobytes())
    return os.path.getsize(path)


def read_tables(path: str) -> dict:
    b = open(path, "rb").read(); magic, G, n, NL, NS, cb = struct.unpack("<6i", b[:24]); assert magic == MAGIC
    dt = np.uint16 if cb == 2 else np.uint32; o = 24; NQ = 3 ** G
    term = np.frombuffer(b, dt, NQ, o).astype(np.int64); o += NQ * cb
    cell = np.frombuffer(b, dt, n * NL, o).astype(np.int64).reshape(n, NL); o += n * NL * cb
    return {"G": G, "n_codes": n, "term": term, "cell": cell, "route": np.frombuffer(b, np.uint8, n * NL * NS, o).reshape(n, NL, NS)}


def plan_route(tab: dict, q: int, gates_s: int, legs) -> int:
    c = tab["term"][q]
    for l in reversed(legs[1:]): c = tab["cell"][c][l]
    return int(tab["route"][c][legs[0]][gates_s])


def certify(tab: dict, exact: dict, alphabet=None, max_seconds: float = 3600.0, max_bytes: float = 4e9, ckpt: str | None = None, want_wrong: int = 0) -> dict:
    """Closure over (code, exact vector id) pairs for a table set against the exact tables.
    alphabet: array of leg kinds (default: all).  want_wrong > 0: also return that many wrong entries with shortest witness jobs."""
    t0 = time.time(); N = exact["n_codes"]; legs = np.arange(exact["cell"].shape[1]) if alphabet is None else np.asarray(alphabet)
    key = np.unique(tab["term"].astype(np.int64) * N + exact["term"]); seen = {int(k): (-1, int(q)) for q, k in enumerate(tab["term"].astype(np.int64) * N + exact["term"])}
    seen = {int(k): seen[int(k)] for k in key}; front = key; growth = [len(front)]; complete = True
    while len(front):
        c, v = front // N, front % N
        nk = (tab["cell"][c][:, legs].astype(np.int64) * N + exact["cell"][v][:, legs]).ravel(); par = np.repeat(front, len(legs)); lg = np.tile(legs, len(front))
        u, first = np.unique(nk, return_index=True); new = []
        for k, i in zip(u.tolist(), first.tolist()):
            if k not in seen: seen[k] = (int(par[i]), int(lg[i])); new.append(k)
        front = np.array(new, dtype=np.int64)
        if len(front): growth.append(len(front))
        if ckpt: np.savez_compressed(ckpt, pairs=np.fromiter(seen.keys(), np.int64), frontier=front, growth=np.array(growth))
        if time.time() - t0 > max_seconds or resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > max_bytes: complete = False; break
    pairs = np.fromiter(seen.keys(), np.int64); c, v = pairs // N, pairs % N; checks = wrong = 0; decisive = 0; wrong_list = []; first_wrong_depth = None
    for i0 in range(0, len(pairs), 4096):                                   # chunked so memory stays bounded
        cc, vv = c[i0:i0 + 4096], v[i0:i0 + 4096]
        r = tab["route"][cc][:, legs]; ok = (exact["valid"][vv][:, legs] >> r) & 1
        checks += ok.size; wrong += int((ok == 0).sum()); decisive += int((exact["valid"][vv][:, legs] != 3).sum())
        if want_wrong and len(wrong_list) < want_wrong:
            for a, b, s in zip(*np.nonzero(ok == 0)):
                if len(wrong_list) >= want_wrong: break
                wrong_list.append((int(pairs[i0 + a]), int(legs[b]), int(s)))
    def path(k):
        out = []
        while seen[k][0] != -1: out.append(seen[k][1]); k = seen[k][0]
        return seen[k][1], out                                              # (requirement index, legs from the current one outwards)
    wit = []
    for (k, leg, s) in wrong_list:
        q, tail = path(k); wit.append({"requirements": int(q), "gates": int(s), "legs": [int(leg)] + [int(x) for x in tail],
                                       "proposed_route": int(tab["route"][k // N][leg][s]), "valid_mask": int(exact["valid"][k % N][leg][s])})
    return {"complete": complete, "pairs": len(pairs), "growth_by_depth": growth, "depth": len(growth) - 1, "codes_used": int(len(np.unique(c))),
            "exact_vectors_reached": int(len(np.unique(v))), "route_checks": checks, "route_wrong": wrong, "entries_with_one_valid_route": decisive,
            "witnesses": wit, "shortest_witness_legs": min((len(w["legs"]) for w in wit), default=None),
            "seconds": time.time() - t0, "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "pair_keys": pairs, "parents": seen}
