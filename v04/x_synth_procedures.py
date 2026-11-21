"""BEYOND THE BRIEF (exploratory, after the freeze): induce the procedure selection by search and verification.

    python v04/x_synth_procedures.py SEED        # uses runs/v4f_proc_s_s<SEED>; writes results/v04/x/procedures_s<SEED>.json

v0.4 M2 learned which procedure an event selects by gradient descent and ended 1.75 points below the hand-coded
macro on novel combinations.  Here the same thing is found by enumeration.  A procedure for one event kind is a
pair: which slots to recompute (a truth table over two facts about a slot: "named by the event", "in the
jurisdiction named by the event") and which policy to recompute them under (current, pinned, named).  There are
14 x 3 = 42 candidates per event kind.  For each kind in turn, every candidate is run on logged training
documents through the frozen executor and status function, and the one that reproduces the logged statuses best is
kept; ties go to the candidate that recomputes fewest slots (protect by default).  Nothing is hand-coded and no
test document is used.  The result is then scored once on the frozen test sets.
"""
import copy, json, os, sys, time
import torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4 import approvals as A
from stillway4.arms import ArmCfg, Proc, evaluate, load, make_data, sub

seed = int(sys.argv[1]); core = f"runs/v4f_proc_s_s{seed}"; man = json.load(open(f"{core}/manifest.json")); salt = man["args"]["salt"]; torch.set_num_threads(1)
model = load(f"{core}/checkpoint.pt"); uni, data = make_data(seed, salt=salt); logs = sub(data["train"], slice(0, 3000)); t0 = time.time()
# the 14 truth tables a linear threshold over (named, in jurisdiction) can give, each with one weight triple
GATES = {}
for wa in (-2.0, 0.0, 2.0):
    for wb in (-2.0, 0.0, 2.0):
        for b in (-3.0, -1.0, 1.0, 3.0):
            tt = tuple(int(wa * a_ + wb * b_ + b > 0) for a_ in (0, 1) for b_ in (0, 1)); GATES.setdefault(tt, (wa, wb, b))
CANDS = sorted(((sum(tt), tt, s) for tt in GATES for s in range(3)))                       # fewest slots recomputed first
m = copy.deepcopy(model)                                                                    # one code per event kind
with torch.no_grad():
    m.router.copy_(torch.full((A.NK, 8), -20.0)); m.router[torch.arange(8), torch.arange(8)] = 20.0
    start = model.tables(); cur = []
    for k in range(A.NK):
        c = start["code_of_kind"][k]; w = start["gate_weights"][c]; tt = tuple(int(w[0] * a_ + w[1] * b_ + w[2] > 0) for a_ in (0, 1) for b_ in (0, 1)); cur.append((tt, start["source_of_code"][c]))

def install(k, tt, s):
    with torch.no_grad():
        m.gate[k] = torch.tensor(GATES[tt]) * 10; m.src[k] = -20.0; m.src[k, s] = 20.0

def score(): return evaluate(m, logs)["status_accuracy"]

for k in range(A.NK):
    tt, s = cur[k]
    if tt not in GATES: tt = min(GATES, key=lambda g: sum(x != y for x, y in zip(g, tt)))   # a learned gate that is not a threshold table: nearest one
    cur[k] = (tt, s); install(k, tt, s)
history = [{"sweep": 0, "log_status_accuracy": score(), "tables": [list(c[0]) + [c[1]] for c in cur]}]; evals = 0
for sweep in (1, 2, 3):
    changed = False
    for k in range(A.NK):
        best = None
        for (n, tt, s) in CANDS:
            install(k, tt, s); acc = score(); evals += 1
            if best is None or acc > best[0] + 1e-12: best = (acc, tt, s)
        if (best[1], best[2]) != cur[k]: changed = True
        cur[k] = (best[1], best[2]); install(k, *cur[k])
    history.append({"sweep": sweep, "log_status_accuracy": score(), "tables": [list(c[0]) + [c[1]] for c in cur]})
    print(json.dumps(history[-1]), flush=True)
    if not changed: break
macro = Proc(ArmCfg(arm="macro", width=model.cfg.width)); mt = macro.tables()
want = [(tuple(int(mt["gate_weights"][c][0] * a_ + mt["gate_weights"][c][1] * b_ + mt["gate_weights"][c][2] > 0) for a_ in (0, 1) for b_ in (0, 1)), mt["source_of_code"][c]) for c in mt["code_of_kind"]]
res = {"seed": seed, "core": core, "candidates_per_event_kind": len(CANDS), "candidate_evaluations": evals, "logged_documents_used": 3000, "seconds": round(time.time() - t0, 1), "history": history,
       "induced": [{"kind": A.KIND_NAMES[k], "recompute_when[named,in_jurisdiction]=(00,01,10,11)": list(cur[k][0]), "policy_source": ["current", "pinned", "named"][cur[k][1]],
                    "same_slots_as_hand_coded": cur[k][0] == want[k][0], "same_source_as_hand_coded": cur[k][1] == want[k][1] or sum(cur[k][0]) == 0} for k in range(A.NK)]}
for name, mm in (("gradient_learned", model), ("induced_by_search", m)):
    res[name] = {}
    for k in ("test_iid", "test_novel"):
        e = evaluate(mm, data[k]); res[name][k] = {"success": e["success"], "status_accuracy": e["status_accuracy"], "protected_changed": e["protected_changed"],
                                                   "by_family": {int(f): [int(((data[k]["family"] == f) & e["doc_ok"]).sum()), int((data[k]["family"] == f).sum())] for f in data[k]["family"].unique().tolist()}}
torch.save({"router": m.router.detach(), "gate": m.gate.detach(), "src": m.src.detach()}, f"results/v04/x/procedures_s{seed}.pt") if os.path.isdir("results/v04/x") else None
os.makedirs("results/v04/x", exist_ok=True); torch.save({"router": m.router.detach(), "gate": m.gate.detach(), "src": m.src.detach()}, f"results/v04/x/procedures_s{seed}.pt")
json.dump(res, open(f"results/v04/x/procedures_s{seed}.json", "w"), indent=1)
print("seed", seed, {n: (round(res[n]["test_iid"]["success"], 4), round(res[n]["test_novel"]["success"], 4), res[n]["test_novel"]["protected_changed"]) for n in ("gradient_learned", "induced_by_search")},
      "same as hand-coded:", sum(r["same_slots_as_hand_coded"] and r["same_source_as_hand_coded"] for r in res["induced"]), "of 8 kinds")
