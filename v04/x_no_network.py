"""BEYOND THE BRIEF (exploratory, after the freeze): the whole approvals planner induced from raw logs, with no network.

    python v04/x_no_network.py SEED        # plain Python; torch is used only to regenerate the seed's logged documents

Input: the same 20,000 logged documents every v0.4 arm trained on (events, and the 5 statuses after every event).
Nothing else: no rules, no policy contents, no hand-written procedure, no gradient step.
Given (as in the procedural arm): the register schema and the executor ("recompute these slots under this policy").
Found by search:
  procedures   for each of the 8 event kinds, one of 48 candidates (which slots to recompute: any truth table over
               "named by the event" and "in the jurisdiction named"; under which policy: current, pinned, named)
  bank         for each policy ID, a table: the status logged whenever a slot was recomputed under that ID with those facts
The two are found together: for a candidate procedure, the bank it implies is read off the logs by vote, the logs
are replayed, and the candidate that reproduces the logged statuses best is kept (ties: the one that recomputes
fewest slots).  Then the result is scored once on the frozen test sets by the plain grader.
"""
import json, os, sys, time
from collections import Counter, defaultdict
from itertools import product
import torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4 import approvals as A
from stillway4.arms import make_data
from stillway4.grader import grade
from stillway4.runtime import TableRuntime, fact_index

seed = int(sys.argv[1]); man = json.load(open(f"runs/v4f_proc_s_s{seed}/manifest.json")); salt = man["args"]["salt"]; uni, data = make_data(seed, salt=salt); t0 = time.time()
def docs_of(d, n): return [A.record(d, i) for i in range(n)], d["labels"][:n].tolist()
logs, labels = docs_of(data["train"], 1500)
CANDS = sorted(((sum(tt), tt, s) for tt in product((0, 1), repeat=4) for s in range(3)), key=lambda c: (c[0], c[2], c[1]))        # 48 per kind, fewest slots first
proc = {"code_of_kind": list(range(8)), "gate": [[False] * 4 for _ in range(8)], "source": [0] * 8}


def replay(docs, labs, bank, vote=False):
    """Replay documents through the executor.  vote=True: collect, for every recomputation, the logged status (to build the bank).
    Otherwise return the share of logged statuses reproduced."""
    rt = TableRuntime(proc, bank); votes = defaultdict(Counter); ok = n = 0
    for doc, lab in zip(docs, labs):
        job = rt.new_job()
        for t, e in enumerate(doc["events"]):
            u0 = len(job["uses"]); out = rt.step(job, e)
            if vote:
                for (_, i, p) in job["uses"][u0:]:
                    if p > 0 and job["facts"][i] is not None: votes[(p, fact_index(*job["facts"][i]))][lab[t][i]] += 1
            else: ok += sum(a == b for a, b in zip(out, lab[t])); n += 5
    return votes if vote else ok / n


def bank_from(votes):
    b = {}
    for (p, f), c in votes.items(): b.setdefault(p, [A.ABSTAIN] * 36)[f] = c.most_common(1)[0][0]
    return b


def score(): return replay(logs, labels, bank_from(replay(logs, labels, {}, vote=True)))

history = [score()]; evals = 0
for sweep in (1, 2, 3):
    changed = False
    for k in range(8):
        best = None; keep = (list(proc["gate"][k]), proc["source"][k])
        for (n1, tt, s) in CANDS:
            proc["gate"][k] = [bool(x) for x in tt]; proc["source"][k] = s; acc = score(); evals += 1
            if best is None or acc > best[0] + 1e-12: best = (acc, [bool(x) for x in tt], s)
        proc["gate"][k], proc["source"][k] = best[1], best[2]; changed |= (best[1], best[2]) != keep
    history.append(score()); print("sweep", sweep, "logged statuses reproduced:", round(history[-1], 6), flush=True)
    if not changed: break
search_seconds = time.time() - t0
all_docs, all_labs = docs_of(data["train"], len(data["train"]["tenant"])); bank = bank_from(replay(all_docs, all_labs, {}, vote=True)); rt = TableRuntime(proc, bank)       # the bank from all 20,000 logged documents
pol = {p: A.RULES[int(uni.pid_rule[p])].tolist() for p in range(1, len(uni.pid_rule))}
truth_cells = sum(1 for p in bank for f in range(36) if bank[p][f] == int(A.status_fn(uni.pid_rule[p:p + 1], A.ALL_FACTS[f:f + 1, 0], A.ALL_FACTS[f:f + 1, 1], A.ALL_FACTS[f:f + 1, 2], A.ALL_FACTS[f:f + 1, 3])[0]))
res = {"seed": seed, "logged_documents_for_search": 1500, "logged_documents_for_the_bank": len(all_docs), "candidates_per_event_kind": len(CANDS), "candidate_evaluations": evals, "search_seconds": round(search_seconds, 1),
       "logged_statuses_reproduced_by_sweep": history, "bank": {"policies": len(bank), "cells_equal_to_the_true_rule": truth_cells, "cells": 36 * len(bank)},
       "procedures": [{"kind": A.KIND_NAMES[k], "recompute_when(00,01,10,11)=[named,in_jurisdiction]": [int(x) for x in proc["gate"][k]], "policy_source": ["current", "pinned", "named"][proc["source"][k]]} for k in range(8)],
       "given": "register schema; the executor; an expired or unknown policy abstains", "found_by_search": "all 8 procedures and all policy tables", "gradient_steps": 0, "network_parameters": 0,
       "deployed_bytes": 36 * len(bank) + 8 * 2}
for k in ("test_iid", "test_novel"):
    ok = prot = 0; n = len(data[k]["tenant"])
    for i in range(n):
        d = A.record(data[k], i); job = rt.new_job(); g = grade(d, pol, [rt.step(job, e) for e in d["events"]]); ok += g["success"]; prot += g["protected_changed"]
    res[k] = {"documents": n, "success": ok / n, "protected_changed": prot}
res["total_seconds"] = round(time.time() - t0, 1); json.dump({"proc": proc, "bank": bank}, open(f"results/v04/x/no_network_planner_s{seed}.json", "w")); json.dump(res, open(f"results/v04/x/no_network_s{seed}.json", "w"), indent=1)
print("seed", seed, {k: (res[k]["success"], res[k]["protected_changed"]) for k in ("test_iid", "test_novel")}, "search s", res["search_seconds"], "bank cells right", truth_cells, "of", 36 * len(bank))
for r in res["procedures"]: print("  ", r["kind"], r["recompute_when(00,01,10,11)=[named,in_jurisdiction]"], r["policy_source"])
