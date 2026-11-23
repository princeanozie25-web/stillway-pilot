"""A guard that asks one focused question.  Follow-up Q5, built to Codex's execution brief (docs/v08_q5_codex_brief.md).
bank.py is not changed.

The guard of bank.compile(guard=True) tries every one-line change of every promoted entry against the two visible
checks, undoing each; one passing change is committed, more than one ends in a bare ASK.  Here the second case goes on:

  1. A sound equivalence rule (`canon`).  Two settings get the same form only if they give the same report on every legal
     input of this bounded world (values 1 to 9).  Surviving changes with the same form are one kind.  One kind left:
     commit it, ask nothing.
  2. Otherwise, a disposable probe.  Make up legal inputs and run one change of each kind on each, in a scratch copy of
     the project (TRIAL); the workspace is not touched.  Look for an input and a field on which two kinds differ.  The
     search stops at the first input that separates every kind, or after MINSCAN inputs once some difference is known,
     or at LIMIT inputs.
  3. No difference within LIMIT inputs: record the search limit and fall back to the bare ASK.  Kinds that the rule does
     not prove equal are never committed on the strength of probes alone.
  4. A difference: put ONE question (QUESTION): these rows, this field, the values two named candidates give.  The run
     pauses with ASK and nothing changed.
  5. On resuming with the owner's value for that field (ANSWER): drop every surviving change whose own value differs
     (the value may differ from both named ones), then go to 1.  At most BUDGET questions per job; after that, or when
     no change agrees with the owner, the bare ASK.

The public specification of a job is its two visible checks; every surviving change already passes both, so there is
nothing further in it to consult, and each question says so in its `source` field.
The same text serves the bank's stored procedure (`compile_q`), a search script with no model (`search_q`) and the
procedure that resumes a paused job (`resume_q`).  Everything it knows comes from the public files and the answers."""
import json
from stillway8.bank import VARIANTS

BUDGET, LIMIT, MINSCAN = 2, 60, 15

DECIDE = '''
import json as _j, random as _r
_CMP = {"gt": lambda a, b: a > b, "ge": lambda a, b: a >= b, "lt": lambda a, b: a < b, "le": lambda a, b: a <= b}
_ROLE = {"norm": "clean", "dedupe": "clean", "cmp": "filter", "thr": "filter", "col": "agg", "func": "agg", "by": "order", "dir": "order"}
_FIELDS = ["count", "groups", "total", "first"]
def canon(c):
    P = tuple(v for v in range(1, 10) if _CMP[c["cmp"]](v, int(c["thr"][1:])))        # the values the filter lets through
    if not P: return ("empty",)                                # nothing passes: the report is 0, 0, 0, "-" whatever else is set
    one = len(P) == 1
    if c["func"] == "count" or (c["func"] == "sum" and c["col"] == "val" and P == (1,)): agg = ("count",)       # the column is not read; a sum of ones is a count
    elif one and c["col"] == "val" and c["func"] in ("mean", "max", "min"): agg = ("the one value",)
    else: agg = (c["col"], c["func"])
    return (c["norm"], c["dedupe"], P, agg, ("key" if one else c["by"], c["dir"]))     # with one value passing, ordering by value is ordering by key
def _made_up(rng, thrs):
    n = rng.randint(3, 5); rows = []
    def key():
        k = rng.choice("abcdef")
        if rng.random() < 0.3: k = k.upper()
        return k + (" " if rng.random() < 0.3 else "")
    for _ in range(n): rows.append([key(), rng.choice(thrs) if rng.random() < 0.3 else rng.randint(1, 9), rng.randint(1, 9)])
    if rng.random() < 0.45:                                    # a repeated record, sometimes written differently
        i = rng.randrange(n); b = rows[i][0].strip(); rows[rng.choice([x for x in range(n) if x != i])] = [rng.choice([rows[i][0], rows[i][0], b + " ", b.upper()]), rows[i][1], rows[i][2]]
    rng.shuffle(rows); return rows
def decide(surv, cur, mods, rnd):
    kinds = {}
    for s, v in surv: kinds.setdefault(canon(dict(cur, **{s: v})), []).append([s, v])
    kinds = list(kinds.values()); reps = [k[0] for k in kinds]
    note(_j.dumps({"round": rnd, "surviving": len(surv), "kinds": len(reps)}))
    if len(reps) == 1:
        s, v = reps[0]; patch(mods[_ROLE[s]], s, v)
        if check("c0") == "PASS" and check("c1") == "PASS": return "PASS"
        revert(); note(_j.dumps({"fallback": "the chosen change no longer passes the visible checks"})); return "ASK"
    if rnd > BUDGET: note(_j.dumps({"fallback": "question budget exhausted", "kinds_left": len(reps)})); return "ASK"
    thrs = sorted({int(v[1:]) for s, v in surv if s == "thr"} | {int(cur["thr"][1:])}); rng = _r.Random(f"{JOB}:{rnd}"); best = None; n = 0
    while n < LIMIT and not (best and (best[0] == len(reps) or n >= MINSCAN)):
        rows = _made_up(rng, thrs); n += 1; out = [_j.loads(trial(mods[_ROLE[s]], s, v, _j.dumps(rows, separators=(",", ":")))) for s, v in reps]
        for f in _FIELDS:
            d = len({o[f] for o in out})
            if d > 1 and (not best or d > best[0]): best = (d, rows, f, out)
    if not best: note(_j.dumps({"fallback": "no difference found", "search_limit_inputs": LIMIT, "probe_executions": n * len(reps), "kinds_left": len(reps)})); return "ASK"
    d, rows, f, out = best; j = next(k for k in range(1, len(reps)) if out[k][f] != out[0][f])
    question(_j.dumps({"id": JOB, "round": rnd, "rows": rows, "field": f, "predictions": [out[0][f], out[j][f]], "candidates": [reps[0], reps[j]], "outputs": [out[0], out[j]],
                       "survivors": [[s, v, out[i][f]] for i, k in enumerate(kinds) for s, v in k], "cur": cur, "mods": mods, "kinds": len(reps), "values_on_field": d, "inputs_tried": n, "probe_executions": n * len(reps),
                       "source": "no public specification covers these rows; both visible checks already pass for every surviving change"}, separators=(",", ":"), sort_keys=True))
    return "ASK"
'''


def _head(job_id): return f"JOB = {job_id!r}; BUDGET = {BUDGET}; LIMIT = {LIMIT}; MINSCAN = {MINSCAN}\n" + DECIDE


def compile_q(bank, gate, entry_module, job_id):
    """The guarded proj procedure of bank.compile with `decide` in place of the bare ASK.  Sets `result`."""
    table = {sig: [(o["role"], o["slot"], VARIANTS[o["slot"]]) for o in order] for sig, order in gate["by_first_observation"].items()}; leave = any(e.get("leave") and e["dom"] == "proj" for e in bank["entries"])
    every = [(e["role"], e["slot"], VARIANTS[e["slot"]]) for e in bank["entries"] if e["dom"] == "proj" and not e.get("leave")]
    return _head(job_id) + f'''ALL = {every!r}; GATE = {table!r}; LEAVE = {leave!r}
c = [check("c0"), check("c1")]; result = "DECLINE"
def mm(x): w = x.split(); return [w[i] for i in range(1, len(w) - 3, 5) if w[i + 2] != w[i + 4]] if w[0] == "FAIL" else []
sig = "+".join(sorted({{f for x in c for f in mm(x)}}))
if not sig: result = "PASS" if LEAVE else "DECLINE"
elif GATE.get(sig):
    mods, todo, seen, found = {{}}, [{entry_module!r}], set(), []
    def find(role):
        while role not in mods and todo:
            m = todo.pop(0)
            if m in seen or m == "none": continue
            seen.add(m); s = show(m).split(); mods[s[1]] = (m, dict(zip(s[2::2], s[3::2]))); todo.extend(deps(m).split())
        return mods.get(role)
    for role, slot, variants in ALL:
        t = find(role)
        if not t: continue
        for v in variants:
            if v == t[1].get(slot): continue
            patch(t[0], slot, v)
            if check("c0") == "PASS" and check("c1") == "PASS": found.append((t[0], slot, v))
            revert()
    if len(found) == 1: patch(*found[0]); result = "PASS"
    elif not found: result = "FAIL"
    else:
        four = [find(r) for r in ("clean", "filter", "agg", "order")]; cur = {{}}; [cur.update(t[1]) for t in four if t]
        result = decide(sorted([s, v] for _, s, v in found), cur, {{r: mods[r][0] for r in ("clean", "filter", "agg", "order") if r in mods}}, 1) if len(cur) == 8 else "ASK"
'''


def search_q(entry_module, job_id):
    """The search script of v08/ref_search.py made to collect every passing change, then `decide`.  No model, no bank.  Prints END."""
    return _head(job_id) + f'''SL = {{"clean": {{"norm": ["none", "strip", "lower", "both"], "dedupe": ["off", "on"]}}, "filter": {{"cmp": ["gt", "ge", "lt", "le"], "thr": ["n%d" % i for i in range(1, 10)]}},
      "agg": {{"col": ["val", "qty"], "func": ["sum", "mean", "max", "min", "count"]}}, "order": {{"by": ["key", "val"], "dir": ["asc", "desc"]}}}}
ok = lambda: check("c0") == "PASS" and check("c1") == "PASS"
end = "DONE"
if not ok():
    seen, todo, mods, found = set(), [{entry_module!r}], {{}}, []
    while todo:
        m = todo.pop()
        if m in seen or m == "none": continue
        seen.add(m); s = show(m).split(); mods[m] = (s[1], dict(zip(s[2::2], s[3::2]))); todo += deps(m).split()
    for m, (role, cur) in sorted(mods.items()):
        for slot, vs in SL.get(role, {{}}).items():
            for v in vs:
                if v == cur.get(slot): continue
                patch(m, slot, v)
                if ok(): found.append((m, slot, v))
                revert()
    if len(found) == 1: patch(*found[0])
    elif not found: end = "ASK"
    else:
        cur = {{}}; [cur.update(c) for r, c in mods.values() if r in SL]; by_role = {{r: m for m, (r, c) in mods.items() if r in SL}}
        end = "DONE" if len(cur) == 8 and decide(sorted([s, v] for _, s, v in found), cur, by_role, 1) == "PASS" else "ASK"
print("END", end)
'''


def resume_q(state, answer):
    """The procedure that carries a paused job on, given the owner's answer to its pending question.  Sets `result`."""
    return _head(state["id"]) + f'''SURV = {state["survivors"]!r}; CUR = {state["cur"]!r}; MODS = {state["mods"]!r}; GIVEN = {answer!r}
answer(_j.dumps(GIVEN, separators=(",", ":"), sort_keys=True))
surv = [[s, v] for s, v, p in SURV if type(p) is type(GIVEN["value"]) and p == GIVEN["value"]]
if surv: result = decide(surv, CUR, MODS, {state["round"] + 1})
else: note(_j.dumps({{"fallback": "the answer agrees with no surviving change"}})); result = "ASK"
'''


def parse(lines):
    """From ledger lines ('OP args'): the pending question (a dict or None), the notes, and the number of probe executions."""
    q, notes, trials = None, [], 0
    for l in lines:
        if l.startswith("QUESTION "): q = json.loads(l[9:])
        elif l.startswith("NOTE "): notes.append(json.loads(l[5:]))
        elif l.startswith("TRIAL "): trials += 1
    return q, notes, trials


def answer_ok(state, a):
    """Does this answer belong to the pending question, and is its value a legal scalar for the field?"""
    if not isinstance(a, dict) or set(a) != {"id", "round", "field", "value"} or a["id"] != state["id"] or a["round"] != state["round"] or a["field"] != state["field"]: return False
    v = a["value"]
    if a["field"] == "first": return isinstance(v, str) and (v == "-" or (len(v.strip()) == 1 and v.strip().lower() in "abcdef" and v in (v.strip(), v.strip() + " ")))
    return type(v) is int and 0 <= v <= 63
