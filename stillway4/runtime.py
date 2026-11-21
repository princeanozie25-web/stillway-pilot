"""Batch-one runtimes for the approvals workflow (v0.4, M4).  Plain Python, integers only, no torch.

TableRuntime   the procedural arm compiled to tables: the procedure tables read off the trained router and codes,
               and one 36-entry status table per policy read off the bank.  This is what would be deployed.
Tracker        non-neural: an incremental dependency tracker with every policy's rule given explicitly.
Replay         non-neural: the rule engine replaying the whole event history at every step.
All three take the same event records and return the 5 statuses after each event.  State is a plain dict, so
a job can be saved (json), reloaded and resumed.
"""
from __future__ import annotations

import json

SIGN, CORRECT, MOVE, AMEND_RETRO, AMEND_PRO, EXPIRE, OVERRIDE, WAIT = range(8)
PENDING, VALID, INVALID, ABSTAIN = range(4)
S, NJ = 5, 4


def fact_index(lvl, age, tag, evid): return (((lvl - 1) * 2 + age) * 3 + tag) * 2 + evid


def compile_procedures(tables: dict) -> dict:
    """Gate weights (3 numbers per code: slot named, in jurisdiction named, bias) -> a 4-entry truth table per code."""
    gates = [[(w[0] * a + w[1] * b + w[2]) > 0 for a in (0, 1) for b in (0, 1)] for w in tables["gate_weights"]]
    return {"code_of_kind": tables["code_of_kind"], "gate": gates, "source": tables["source_of_code"]}


class TableRuntime:
    def __init__(self, proc: dict, bank: dict, expired=(), lookup=None):
        """proc: compile_procedures(...).  bank: {policy ID: [36 statuses]} for the IDs the pinned bank knows.
        expired: IDs the registry maps to the EXPIRED policy.  lookup: optional {(policy ID, fact index): status} retrieval index."""
        self.p, self.bank, self.expired, self.lookup = proc, bank, set(expired), lookup

    @staticmethod
    def new_job(): return {"jur": [-1] * S, "facts": [None] * S, "pj": [-1] * NJ, "pin": [-1] * S, "stat": [PENDING] * S, "uses": []}

    def status(self, pid, f):
        if f is None: return PENDING
        if pid in self.expired or pid == 0: return ABSTAIN
        fi = fact_index(*f)
        if self.lookup is not None:
            r = self.lookup.get((pid, fi))
            if r is not None: return r
        t = self.bank.get(pid)
        return ABSTAIN if t is None else t[fi]

    def step(self, job, e):
        k, sl, jj, pid = e["kind"], e["slot"], e["jur"], e["pid"]
        if e["lvl"] >= 0: job["facts"][sl] = (e["lvl"], e["age"], e["tag"], e["evid"])            # registers, by rule
        if sl >= 0 and jj >= 0: job["jur"][sl] = jj
        if sl < 0 and jj >= 0 and pid >= 0: job["pj"][jj] = pid
        if e["ostat"] >= 0: job["stat"][sl] = e["ostat"]
        c = self.p["code_of_kind"][k]; g = self.p["gate"][c]; src = self.p["source"][c]
        for i in range(S):                                                                     # bounded: at most S recomputations
            if g[(i == sl) * 2 + (jj >= 0 and job["jur"][i] == jj)]:
                p = (job["pj"][job["jur"][i]] if job["jur"][i] >= 0 else -1) if src == 0 else (job["pin"][i] if src == 1 else pid)
                job["pin"][i] = p; job["stat"][i] = self.status(p, job["facts"][i]); job["uses"].append((c, i, p))
        return list(job["stat"])


class Tracker:
    """Explicit rules: policies = {policy ID: (threshold, waiver, stale_ok, conflict_invalid)}; ID 0 and IDs in `expired` are EXPIRED."""
    def __init__(self, policies: dict, expired=()): self.pol, self.expired = policies, set(expired)
    new_job = staticmethod(TableRuntime.new_job)

    def status(self, pid, f):
        if f is None: return PENDING
        if pid == 0 or pid in self.expired or pid not in self.pol: return ABSTAIN
        th, w, st, cf = self.pol[pid]; lvl, age, tag, evid = f
        if w and tag == w: return VALID
        if evid: return INVALID if cf else ABSTAIN
        return VALID if lvl >= th and (age == 0 or st) else INVALID

    def step(self, job, e):
        k, sl, jj = e["kind"], e["slot"], e["jur"]
        if k in (SIGN, CORRECT):
            job["facts"][sl] = (e["lvl"], e["age"], e["tag"], e["evid"])
            if k == SIGN: job["pin"][sl] = job["pj"][job["jur"][sl]]
            job["stat"][sl] = self.status(job["pin"][sl], job["facts"][sl])
        elif k == MOVE:
            job["jur"][sl] = jj
            if job["facts"][sl] is not None: job["pin"][sl] = job["pj"][jj]; job["stat"][sl] = self.status(job["pin"][sl], job["facts"][sl])
        elif k in (AMEND_RETRO, EXPIRE):
            job["pj"][jj] = e["pid"] if k == AMEND_RETRO else 0
            for i in range(S):
                if job["jur"][i] == jj and job["facts"][i] is not None: job["pin"][i] = job["pj"][jj]; job["stat"][i] = self.status(job["pin"][i], job["facts"][i])
        elif k == AMEND_PRO: job["pj"][jj] = e["pid"]
        elif k == OVERRIDE: job["stat"][sl] = e["ostat"]
        return list(job["stat"])


class Replay(Tracker):
    """The same rules with no saved state: every step replays the whole history."""
    @staticmethod
    def new_job(): return {"history": []}

    def step(self, job, e):
        job["history"].append(e); j = TableRuntime.new_job()
        for x in job["history"]: out = Tracker.step(self, j, x)
        return out


def save_job(job) -> str: return json.dumps(job)
def load_job(s: str): j = json.loads(s); j["facts"] = [None if f is None else tuple(f) for f in j.get("facts", [])] if "facts" in j else None; return j if "facts" in j and j["facts"] is not None else json.loads(s)
