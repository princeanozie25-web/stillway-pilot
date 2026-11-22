"""Two worked examples for the report.   python v08/make_examples.py
  results/v08/examples/success_*.json    the teacher's careful record on one fixture job of each domain; replayable
  results/v08/examples/plausible_*.json  a script that passes every visible check and fails the independent test"""
import itertools, json, os, sys
sys.path.insert(0, ".")
from stillway8 import agent, experience as X, expert as E, world as W
from stillway8.grade import grade
from stillway8.runner import Session

pub = [json.loads(l) for l in open("data/v08/fixture/public.jsonl")]; hid = {h["id"]: h for h in map(json.loads, open("data/v08/fixture/hidden.jsonl"))}; os.makedirs("results/v08/examples", exist_ok=True)
def run(p, scripts, end, source):
    q = [" ; ".join(s).split() + ["EXEC"] for s in scripts] + [[end]]; r = agent.episode(None, p, propose=lambda toks: q.pop(0)); v = grade(p, hid[p["id"]], agent.final_files(p, r), r["end"]); return X.build(p, r, v, source)
def teacher(p):
    s = Session(p, fast=True); steps, end = E.teach(s, p, hid[p["id"]]); s.close(); return [x["script"] for x in steps], end
for dom in ("proj", "tab"):
    p = next(p for p in pub if p["dom"] == dom and hid[p["id"]]["group"] == ("familiar" if dom == "proj" else "scattered")); sc, end = teacher(p); e = run(p, sc, end, "teacher")
    assert e["verdict"]["outcome"] == "verified"; json.dump(e, open(f"results/v08/examples/success_{dom}.json", "w"), indent=1); print("success", dom, e["experience"], e["compute"]["ops"], "operations")
# tab: mark every difference as explained, recalculate, both visible checks pass, the ledger is wrong
for p in pub:
    h = hid[p["id"]]
    if p["dom"] != "tab" or h["kind"] != "diff" or h["untouched_verifies"]: continue
    s = Session(p, fast=True); d = s.run("DIFF")["obs"][0]; s.close(); items = [x.split() for x in d.split("d ")[1:]]
    sc = [["DIFF"], [("SKIP " if i[1] == "onlyS" else "KEEP ") + i[0] for i in items] + [f"RECALC {g}" for g in W.GROUPS] + ["CHECK c0", "CHECK c1"]]; e = run(p, sc, "DONE", "constructed: accept every difference")
    if e["steps"][-1]["obs"][-2:] == ["PASS", "PASS"] and e["verdict"]["outcome"] == "wrong": json.dump(e, open("results/v08/examples/plausible_tab.json", "w"), indent=1); print("plausible tab", e["experience"], e["verdict"]); break
# proj: two one-line changes that together satisfy both visible checks and fail the hidden inputs
found = False
for p in pub:
    h = hid[p["id"]]
    if p["dom"] != "proj" or h["kind"] != "bug" or found: continue
    cur = dict(h["true"]); cur[h["slot"]] = h["wrong"]; checks = json.loads(p["files"]["checks.json"]); rows = lambda t: [dict(key=a, val=int(b), qty=int(c)) for a, b, c in (l.split(",") for l in t.splitlines()[1:])]
    vis = [(rows(p["files"][c["data"]]), c["expect"]) for c in checks.values()]; hidt = [(rows(t["csv"]), t["expect"]) for t in h["tests"]]
    for (s1, v1), (s2, v2) in itertools.combinations(W.patches(cur), 2):
        c = dict(cur, **{s1: v1, s2: v2})
        if s1 == s2 or c == h["true"]: continue
        if all(W.stages(c, d)["report"][f] == e[f] for d, e in vis for f in e) and not all(W.stages(c, d)["report"] == e for d, e in hidt):
            n = h["names"]; sc = [["CHECK c0", "CHECK c1"], [f"PATCH {n[W.SLOT_ROLE[s1]]} {s1} {v1}", f"PATCH {n[W.SLOT_ROLE[s2]]} {s2} {v2}", "CHECK c0", "CHECK c1"]]; e = run(p, sc, "DONE", "constructed: two changes that satisfy the visible checks")
            assert e["steps"][-1]["obs"][-2:] == ["PASS", "PASS"] and e["verdict"]["outcome"] == "wrong", e["steps"][-1]
            e["note"] = f"the real fault was {h['slot']} = {h['wrong']} (should be {h['right']})"; json.dump(e, open("results/v08/examples/plausible_proj.json", "w"), indent=1); print("plausible proj", e["experience"], e["verdict"]["detail"]); found = True; break
