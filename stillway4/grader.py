"""Blind outcome grader for the approvals workflow.  Plain Python.  Imports nothing from the project.

    from stillway4.grader import expected, grade
    expected(document, policies)          -> the right 5 statuses after every event
    grade(document, policies, outputs)    -> {"success": bool, "first_wrong_step": ..., "protected_changed": n, ...}

document: {"tenant": int, "events": [{"kind","slot","jur","lvl","age","tag","evid","pid","ostat"}, ...]}  (unused fields are -1)
policies: {pid: [threshold, waiver, stale_accepted, conflict_is_invalid]}; pid 0 is the EXPIRED policy and needs no entry.
outputs:  for every event, the 5 statuses the system under test reported.

Written from docs/v04_spec.md section 2, separately from the generator.  It keeps its own state per slot
(a dict per slot) and decides which slots an event may touch on its own, so "protected" statuses can be
checked without trusting anything the system or the generator stored.
"""
SIGN, CORRECT, MOVE, AMEND_RETRO, AMEND_PRO, EXPIRE, OVERRIDE, WAIT = range(8)
PENDING, VALID, INVALID, ABSTAIN = range(4)


def decide(policy, slot):
    if slot["lvl"] == 0: return PENDING
    if policy is None: return ABSTAIN                                  # the EXPIRED policy
    threshold, waiver, stale_ok, conflict_invalid = policy
    if waiver != 0 and slot["tag"] == waiver: return VALID
    if slot["evid"] == 1: return INVALID if conflict_invalid else ABSTAIN
    if slot["lvl"] >= threshold and (slot["age"] == 0 or stale_ok): return VALID
    return INVALID


def expected(doc, policies):
    slots = [{"jur": None, "lvl": 0, "age": 0, "tag": 0, "evid": 0, "pinned": None, "status": PENDING} for _ in range(5)]
    current = {}; out = []; touched = []
    pol = lambda pid: None if pid == 0 else policies[pid]
    for e in doc["events"]:
        k = e["kind"]; hit = set()
        if k in (SIGN, CORRECT):
            s = slots[e["slot"]]; s.update(lvl=e["lvl"], age=e["age"], tag=e["tag"], evid=e["evid"])
            if k == SIGN: s["pinned"] = current[s["jur"]]
            s["status"] = decide(pol(s["pinned"]), s); hit.add(e["slot"])
        elif k == MOVE:
            s = slots[e["slot"]]; s["jur"] = e["jur"]
            if s["lvl"] > 0: s["pinned"] = current[s["jur"]]; s["status"] = decide(pol(s["pinned"]), s)
            hit.add(e["slot"])
        elif k in (AMEND_RETRO, EXPIRE):
            current[e["jur"]] = e["pid"] if k == AMEND_RETRO else 0
            for i, s in enumerate(slots):
                if s["jur"] == e["jur"] and s["lvl"] > 0: s["pinned"] = current[e["jur"]]; s["status"] = decide(pol(s["pinned"]), s); hit.add(i)
        elif k == AMEND_PRO: current[e["jur"]] = e["pid"]
        elif k == OVERRIDE: slots[e["slot"]]["status"] = e["ostat"]; hit.add(e["slot"])
        out.append([s["status"] for s in slots]); touched.append(sorted(hit))
    return out, touched


def grade(doc, policies, outputs):
    want, touched = expected(doc, policies); first = None; wrong = 0; protected_changed = 0; prev = [PENDING] * 5
    for t, (w, o) in enumerate(zip(want, outputs)):
        o = list(o)
        if o != w:
            wrong += 1
            if first is None: first = t
        protected_changed += sum(1 for i in range(5) if i not in touched[t] and o[i] != prev[i])
        prev = o
    return {"success": wrong == 0 and len(outputs) == len(want), "steps": len(want), "wrong_steps": wrong, "first_wrong_step": first, "protected_changed": protected_changed}
