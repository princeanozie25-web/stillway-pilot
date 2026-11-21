"""Failure fixtures for v0.4: made from the final artifacts, each replayable.

    python v04/fixtures.py make          # writes results/v04/fixtures/*.json
    python v04/fixtures.py check         # replays every fixture and compares with the recorded outcome
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4.gates import Gates, certify, plan_route, read_tables
from stillway4.grader import expected, grade
OUT = "results/v04/fixtures"; os.makedirs(OUT, exist_ok=True)
RULES = [(th, w, st, cf) for th in (1, 2, 3) for w in (0, 1, 2) for st in (0, 1) for cf in (0, 1)]; FIELDS = ("kind", "slot", "jur", "lvl", "age", "tag", "evid", "pid", "ostat")


def make():
    g = Gates(3); clo = g.exact_closure(); ex = g.compile_exact(clo)
    # 1. a mutated exact table: one reachable route entry with a single valid choice flipped
    n, l, s = [int(x[0]) for x in np.nonzero(ex["valid"] != 3)]; mut = dict(ex); mut["route"] = ex["route"].copy(); mut["route"][n, l, s] ^= 1; c = certify(mut, ex, want_wrong=1); w = c["witnesses"][0]
    json.dump({"what": "exact 3-gate tables with one route entry flipped; the checker must report it and give a failing job", "gates": 3, "flipped_entry": {"vector": n, "leg": l, "gate_state": s},
               "checker": {"route_wrong": c["route_wrong"], "witness": w}, "brute_force_valid_routes": list(g.brute_valid(w["requirements"], w["gates"], w["legs"])), "proposed_by_mutated_tables": w["proposed_route"]},
              open(f"{OUT}/m1_mutation_g3.json", "w"), indent=1)
    # 2. a learned table set that is not clean (protocol 1 pilot, three gates)
    p = "runs/v4r_g3_w128_s1/tables.bin"
    if os.path.exists(p):
        t = read_tables(p); c = certify(t, ex, want_wrong=5)
        json.dump({"what": "learned 3-gate tables from the protocol-1 pilot (181 of 500 value vectors had no code): not certified", "tables": p, "pairs": c["pairs"], "route_checks": c["route_checks"], "route_wrong": c["route_wrong"],
                   "witnesses": [{**w, "brute_force_valid_routes": list(g.brute_valid(w["requirements"], w["gates"], w["legs"])), "table_route": plan_route(t, w["requirements"], w["gates"], w["legs"])} for w in c["witnesses"]]},
                  open(f"{OUT}/m1_unclean_learned_g3.json", "w"), indent=1)
    # 3. approvals: the first novel-combination document a learned arm gets wrong, from raw outputs
    for arm in ("proc", "cont", "text"):
        p = f"runs/v4f_{arm}_s_s1/raw_outputs.npz"
        if not os.path.exists(p): continue
        z = np.load(p); pol = {i: (RULES[int(r)] if r >= 0 else None) for i, r in enumerate(z["pid_rule"]) if i > 0}
        for i in range(len(z["test_novel_out"])):
            doc = {"events": [dict(zip(FIELDS, map(int, e))) for e in z["test_novel_events"][i]]}; o = z["test_novel_out"][i].tolist(); gr = grade(doc, pol, o)
            if not gr["success"]:
                want, touched = expected(doc, pol); used = sorted({e["pid"] for e in doc["events"] if e["pid"] > 0})
                json.dump({"what": f"first novel-combination test document the {arm} arm (size s, seed 1) gets wrong", "source": p, "document_index": i, "document": doc, "policies": {str(k): pol[k] for k in used},
                           "reported": o, "expected": want, "grade": gr}, open(f"{OUT}/m2_{arm}_failure.json", "w"), indent=1); break
    # 4. sleep: a new-policy document after the last sleep that retrieval gets wrong and consolidation+dreaming gets right
    p = "results/v04/m3/v4f_proc_s_s1/raw_outputs.npz"
    if os.path.exists(p):
        z = np.load(p); pol = {i: (RULES[int(r)] if r >= 0 else None) for i, r in enumerate(z["s6_pid_rule"]) if i > 0}
        for i in range(len(z["s6_learn_events"])):
            doc = {"events": [dict(zip(FIELDS, map(int, e))) for e in z["s6_learn_events"][i]]}; a, b = z["s6_learn_retrieval_out"][i].tolist(), z["s6_learn_dreaming_out"][i].tolist()
            if not grade(doc, pol, a)["success"] and grade(doc, pol, b)["success"]:
                used = sorted({e["pid"] for e in doc["events"] if e["pid"] > 0})
                json.dump({"what": "after the sixth sleep: a document on that session's new policies; retrieval fails, consolidation+dreaming succeeds", "source": p, "document_index": i, "document": doc,
                           "policies": {str(k): pol[k] for k in used}, "retrieval_reported": a, "dreaming_reported": b, "expected": expected(doc, pol)[0]}, open(f"{OUT}/m3_retrieval_failure.json", "w"), indent=1); break
    print("fixtures:", sorted(os.listdir(OUT)))


def check():
    ok = True
    for f in sorted(os.listdir(OUT)):
        d = json.load(open(f"{OUT}/{f}"))
        if f.startswith("m1_mutation"):
            g = Gates(d["gates"]); w = d["checker"]["witness"]; good = w["proposed_route"] not in g.brute_valid(w["requirements"], w["gates"], w["legs"])
        elif f.startswith("m1_unclean"):
            g = Gates(3); t = read_tables(d["tables"]); good = all(plan_route(t, w["requirements"], w["gates"], w["legs"]) not in g.brute_valid(w["requirements"], w["gates"], w["legs"]) for w in d["witnesses"])
        else:
            pol = {int(k): v for k, v in d["policies"].items()}; rep = d.get("reported", d.get("retrieval_reported")); good = not grade(d["document"], pol, rep)["success"]
            if "dreaming_reported" in d: good = good and grade(d["document"], pol, d["dreaming_reported"])["success"]
        ok &= good; print(f"{f:34s} {'failure reproduced' if good else 'NOT reproduced'}")
    print("FIXTURES OK" if ok else "FIXTURES FAIL"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    make() if sys.argv[1] == "make" else check()
