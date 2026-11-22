"""The memory bank: tested procedures, each citing the experiences that verified it, and a separate gate that learns when
a procedure is worth invoking.

An entry is promoted from candidates (stillway8/experience.py) once at least `min_support` verified experiences propose
it.  proj entry: 'when these fields are reported, try the settings of <slot> in the <role> module in use, keeping the
first that passes both visible checks'.  tab entry: 'a difference of <kind> with note <note> is resolved by <action>'.
A special entry records that a job with nothing failing was left alone.

`compile` writes the bank into one script over the ordinary operations (run with USE in the sandbox).  It leaves the
workspace as it found it unless it reports PASS.  The gate is a table learned from logged outcomes: for each first
observation, which entries to try and in what order; an entry is tried only if its logged success rate times the cost
of the fallback exceeds its own cost."""
import collections, hashlib, json
from stillway8.expert import mismatches

VARIANTS = {"norm": ["none", "strip", "lower", "both"], "dedupe": ["off", "on"], "cmp": ["gt", "ge", "lt", "le"], "thr": [f"n{i}" for i in range(1, 10)], "col": ["val", "qty"], "func": ["sum", "mean", "max", "min", "count"],
            "by": ["key", "val"], "dir": ["asc", "desc"]}


def promote(experiences, min_support=2):
    """Bank entries from a day's experiences.  Returns {'entries': [...], 'rejected': n}."""
    sup = collections.defaultdict(list); leave = []
    for e in experiences:
        c = e.get("memory_candidate")
        if e["verdict"]["outcome"] == "verified" and e["end"] == "DONE" and not e["diff"]: leave.append(e["experience"])
        if not c: continue
        if c["signature"]["dom"] == "proj": sup[("proj", c["procedure"]["role"], c["procedure"]["slot"])].append((tuple(c["signature"]["reported"]), e["experience"]))
        else:
            for k, n, a in c["procedure"]["rules"]: sup[("tab", k, n, a)].append((None, e["experience"]))
    entries = []; rejected = 0
    for key, ev in sorted(sup.items()):
        if len(ev) < min_support: rejected += 1; continue
        if key[0] == "proj": entries.append({"dom": "proj", "role": key[1], "slot": key[2], "support": len(ev), "signatures": dict(collections.Counter("+".join(s) for s, _ in ev)), "provenance": [x for _, x in ev][:20]})
        else: entries.append({"dom": "tab", "kind": key[1], "note": key[2], "action": key[3], "support": len(ev), "provenance": [x for _, x in ev][:20]})
    by = collections.defaultdict(set)                          # a tab rule is kept only if its evidence never disagrees
    for e in entries:
        if e["dom"] == "tab": by[(e["kind"], e["note"])].add(e["action"])
    entries = [e for e in entries if e["dom"] != "tab" or len(by[(e["kind"], e["note"])]) == 1]
    for dom in ("proj", "tab"):
        ev = [x for x in leave if x.startswith(f"x-{dom}")]
        if len(ev) >= min_support: entries.append({"dom": dom, "leave": True, "support": len(ev), "provenance": ev[:20]})
    for i, e in enumerate(entries): e["id"] = f"b{i:02d}-" + hashlib.sha256(json.dumps({k: v for k, v in e.items() if k not in ("support", "provenance", "signatures")}, sort_keys=True).encode()).hexdigest()[:6]
    return {"entries": entries, "rejected_for_low_support": rejected}


def learn_gate(bank, experiences, cost_core, cost_try, price=0.0):
    """For each first observation (the reported fields), the proj entries to try, in order of logged success.

    cost = seconds + price * operations.  cost_core: the mean cost of the fallback (the core alone) per job; cost_try(entry):
    the mean cost of one failed try of an entry.  An entry is tried while p * cost_core > cost_try, p being the share of
    logged verified experiences with this first observation that the entry's slot repaired."""
    seen = collections.defaultdict(collections.Counter)
    for e in experiences:
        c = e.get("memory_candidate")
        if c and c["signature"]["dom"] == "proj": seen["+".join(c["signature"]["reported"])][(c["procedure"]["role"], c["procedure"]["slot"])] += 1
        elif e["goal"].startswith("proj") and e["verdict"]["outcome"] == "verified" and e["steps"]:
            rep = "+".join(sorted({x for o in e["steps"][0]["obs"] for x in mismatches(o)}))
            if rep: seen[rep][None] += 1                          # verified, but nothing the bank could have done (an ASK)
    have = {(e["role"], e["slot"]): e for e in bank["entries"] if e["dom"] == "proj" and not e.get("leave")}; gate = {}
    for sig, cnt in seen.items():
        tot = sum(cnt.values()); order = []
        for key, k in cnt.most_common():
            if key in have and (k / tot) * cost_core(price) > cost_try(have[key], price): order.append({"entry": have[key]["id"], "role": key[0], "slot": key[1], "p": round(k / tot, 3)})
        gate[sig] = order
    return {"price_seconds_per_operation": price, "by_first_observation": gate, "tab": "try the rules whenever every difference is covered"}


def compile(bank, gate, dom, entry_module=None, guard=False):
    """The bank as one script for USE.  Sets `result`: PASS (the job is done), or FAIL / DECLINE (nothing changed).
    guard=True (proj): try every setting of every promoted entry before committing; if more than one one-line change
    satisfies both visible checks the evidence does not decide, nothing is changed and the result is ASK."""
    if dom == "tab":
        rules = {f"{e['kind']} {e['note']}": e["action"] for e in bank["entries"] if e["dom"] == "tab" and not e.get("leave")}; leave = any(e.get("leave") and e["dom"] == "tab" for e in bank["entries"])
        return f'''RULES = {rules!r}; LEAVE = {leave!r}
d = diff(); c = check("c0"); items = [x.split() for x in d.split("d ")[1:]] if d != "none" else []; stale = c.split()[1] if c.startswith("FAIL") else None
result = "DECLINE"
if not items and not stale: result = "PASS" if LEAVE else "DECLINE"
elif not items: result = "DECLINE"
else:
    notes = [fact(i[0]) for i in items]; kinds = [i[1] if i[1] == "onlyS" else i[2] for i in items]
    if all(f"{{k}} {{n.split()[0]}}" in RULES for k, n in zip(kinds, notes)):
        groups = set([stale] if stale else [])
        for i, k, n in zip(items, kinds, notes):
            act = RULES[f"{{k}} {{n.split()[0]}}"]
            if act == "ADD": add(i[0], n.split()[1]); groups.add(n.split()[1])
            else:
                {{"COPY": copy, "KEEP": keep, "DROP": drop, "SKIP": skip}}[act](i[0])
                if act in ("COPY", "DROP"): groups.add(i[1])
        for g in sorted(groups): recalc(g)
        result = "PASS" if check("c0") == "PASS" and check("c1") == "PASS" else "FAIL"
'''
    table = {sig: [(o["role"], o["slot"], VARIANTS[o["slot"]]) for o in order] for sig, order in gate["by_first_observation"].items()}; leave = any(e.get("leave") and e["dom"] == "proj" for e in bank["entries"])
    if guard:
        every = [(e["role"], e["slot"], VARIANTS[e["slot"]]) for e in bank["entries"] if e["dom"] == "proj" and not e.get("leave")]
        return f'''ALL = {every!r}; GATE = {table!r}; LEAVE = {leave!r}
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
    else: result = "ASK" if found else "FAIL"
'''
    return f'''GATE = {table!r}; LEAVE = {leave!r}
c = [check("c0"), check("c1")]; result = "DECLINE"
def mm(x): w = x.split(); return [w[i] for i in range(1, len(w) - 3, 5) if w[i + 2] != w[i + 4]] if w[0] == "FAIL" else []
sig = "+".join(sorted({{f for x in c for f in mm(x)}}))
if not sig: result = "PASS" if LEAVE else "DECLINE"
elif GATE.get(sig):
    mods, todo, seen = {{}}, [{entry_module!r}], set(); result = "FAIL"
    def find(role):
        while role not in mods and todo:
            m = todo.pop(0)
            if m in seen or m == "none": continue
            seen.add(m); s = show(m).split(); mods[s[1]] = (m, dict(zip(s[2::2], s[3::2]))); todo.extend(deps(m).split())
        return mods.get(role)
    for role, slot, variants in GATE[sig]:
        t = find(role)
        if not t or result == "PASS": continue
        for v in variants:
            if v == t[1].get(slot): continue
            patch(t[0], slot, v)
            if check("c0") == "PASS" and check("c1") == "PASS": result = "PASS"; break
            revert()
'''
