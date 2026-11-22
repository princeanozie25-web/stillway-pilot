"""A reference with no model: one fixed script per job that composes the same operations.   python v08/ref_search.py PUBLIC.jsonl OUT.jsonl

proj: run both checks; if one fails, walk the imports from the entry module, then try every one-line change in the modules
      in use until both visible checks pass (undoing each failure); if none does, ask.
tab:  read the differences and their notes, apply the written rules, recalculate, check.
It shows what exhaustive execution costs in operations and time, and where visible checks alone are enough."""
import hashlib, json, sys, time
sys.path.insert(0, ".")
from stillway8.runner import Session
from stillway8.agent import EDITS

PROJ = '''
SL = {"clean": {"norm": ["none", "strip", "lower", "both"], "dedupe": ["off", "on"]}, "filter": {"cmp": ["gt", "ge", "lt", "le"], "thr": ["n%d" % i for i in range(1, 10)]},
      "agg": {"col": ["val", "qty"], "func": ["sum", "mean", "max", "min", "count"]}, "order": {"by": ["key", "val"], "dir": ["asc", "desc"]}}
ok = lambda: check("c0") == "PASS" and check("c1") == "PASS"
end = "DONE"
if not ok():
    seen, todo, mods = set(), [ENTRY], {}
    while todo:
        m = todo.pop()
        if m in seen or m == "none": continue
        seen.add(m); s = show(m).split(); mods[m] = (s[1], dict(zip(s[2::2], s[3::2]))); todo += deps(m).split()
    end = "ASK"
    for m, (role, cur) in sorted(mods.items()):
        for slot, vs in SL.get(role, {}).items():
            for v in vs:
                if v == cur.get(slot) or end == "DONE": continue
                patch(m, slot, v)
                if ok(): end = "DONE"
                else: revert()
print("END", end)
'''
TAB = '''
RULES = {("amt", "stmt_newer"): "copy", ("amt", "ledger_newer"): "keep", ("amt", "void"): "drop", ("onlyL", "pending"): "keep", ("onlyL", "void"): "drop", ("onlyS", "grp"): "add", ("onlyS", "dupstmt"): "skip", ("onlyS", "pending"): "skip"}
d = diff(); c = check("c0"); items = [x.split() for x in d.split("d ")[1:]] if d != "none" else []; groups = set([c.split()[1]] if c.startswith("FAIL") else []); notes = [fact(i[0]) for i in items]; end = "DONE"
if "nonote" in notes: end = "ASK"
else:
    for i, n in zip(items, notes):
        kind = i[1] if i[1] == "onlyS" else i[2]; act = RULES[(kind, n.split()[0])]
        if act == "add": add(i[0], n.split()[1]); groups.add(n.split()[1])
        else:
            globals()[act](i[0])
            if act in ("copy", "drop"): groups.add(i[1])
    for g in sorted(groups): recalc(g)
    if items or groups: check("c0"); check("c1")
print("END", end)
'''

jobs = [json.loads(l) for l in open(sys.argv[1])]
with open(sys.argv[2], "w") as f:
    for p in jobs:
        t0 = time.time(); s = Session(p); code = PROJ.replace("ENTRY", repr(p.get("entry"))) if p["dom"] == "proj" else TAB; r = s.run(code, mode="py"); final = s.files(); end = (r["stdout"].split("END ")[-1].strip() if "END " in r["stdout"] else "BUDGET")
        steps = [{"script": [f"{l['op']} {' '.join(l['args'])}".strip() for l in r["ledger"]], "obs": r["obs"], "s": r["s"], "error": r["error"]}]
        rec = {"id": p["id"], "dom": p["dom"], "end": end, "why": r["error"], "steps": steps, "changed": {n: t for n, t in final.items() if p["files"].get(n) != t}, "diff": s.diff(), "calls": 1, "ops": s.ops(),
               "edit_scripts": 1 if any(l.split()[0] in EDITS for l in steps[0]["script"]) else 0, "failed_checks": sum(o.startswith("FAIL") for o in r["obs"]), "bad_ops": sum(o in ("BAD", "ERR") for o in r["obs"]), "tokens_out": 0, "tokens_in": 0,
               "model_s": 0.0, "exec_s": r["s"], "wall_s": round(time.time() - t0, 4), "final_hash": hashlib.sha256(json.dumps(final, sort_keys=True).encode()).hexdigest()[:16]}
        s.close(); f.write(json.dumps(rec, sort_keys=True) + "\n")
print("done", len(jobs))
