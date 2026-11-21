"""Pick representative fixtures (one clean success, real failures) and save them with their recorded outcome.

    python v02/make_fixtures.py SEED      -> fixtures3/*.json
"""
import json, os, sys
import numpy as np
sys.path.insert(0, "v02")
from run_fixture import load, run_fixture
EFFN = "KTOC"; seed = int(sys.argv[1]); r = np.random.default_rng(seed)
iit, sw_i = load("runs/v2_iit_s1"); plain, sw_p = load("runs/v2_plain_s1")

def rand_fx(L, cross):
    trips = []
    for i in range(L):
        g = int(r.integers(0, 2)); trips.append([[EFFN[int(r.integers(0, 4))], g], [EFFN[int(r.integers(0, 4))], (1 - g) if (cross and i == 0) else g]])
    parcel = [bool(r.random() < 0.6) for _ in range(L)]; waits = [bool(r.random() < 0.5) for _ in range(L)]
    order = {"gate0": int(r.integers(1, 3)), "gate1": int(r.integers(0, 3)), "parcels": [int(x) for x in r.integers(0, 3, 4)]}
    return {"legs": L, "trips": trips, "parcel": parcel, "waits": waits, "gates": [int(x) for x in r.integers(0, 2, 2)], "closed": None, "order": order,
            "edit": {"pause_slot": 1 if waits[0] else 2, "field": 0, "value": 3 - order["gate0"], "method": "predictor"}}

def ok(t): return all(s.get("action_valid", True) for s in t["steps"]) and not t["abstained"]
def met(t): return all(t["gate_requirements_met"]) and all(t["parcels_right"])
want = {"success_three_legs": (3, False, lambda e, m, i: ok(e) and met(e) and not met(i)), "failure_four_legs": (4, False, lambda e, m, i: not ok(e) and not ok(m)),
        "failure_cross_gate": (3, True, lambda e, m, i: not ok(e) and not ok(m))}
os.makedirs("fixtures3", exist_ok=True); done = {}
for name, (L, cross, cond) in want.items():
    for _ in range(4000):
        fx = rand_fx(L, cross); e = run_fixture(iit, sw_i, fx); m = run_fixture(iit, sw_i, {**fx, "edit": {**fx["edit"], "method": "message"}})
        i = run_fixture(iit, sw_i, {**fx, "edit": {**fx["edit"], "method": "none", "pause_slot": 99}})   # order corrected never: the edit ignored
        if cond(e, m, i):
            rec = {"core": "v2_iit_s1", "fixture": fx, "recorded": {"predictor_edit": {"all_actions_valid": ok(e), "abstained": e["abstained"], "final_gates": e["final_gates"], "delivered": e["delivered"], "gate_requirements_met": e["gate_requirements_met"], "parcels_right": e["parcels_right"]},
                                                                     "message": {"all_actions_valid": ok(m), "final_gates": m["final_gates"], "delivered": m["delivered"]}}}
            json.dump(rec, open(f"fixtures3/{name}.json", "w"), indent=1); done[name] = True; break
# a tangled (plain-imitation) core: the frozen predictor declines
for _ in range(4000):
    fx = rand_fx(3, False); e = run_fixture(plain, sw_p, fx)
    if e["abstained"]:
        json.dump({"core": "v2_plain_s1", "fixture": fx, "recorded": {"predictor_edit": {"abstained": True, "final_gates": e["final_gates"]}}}, open("fixtures3/declined_on_plain_core.json", "w"), indent=1); done["declined_on_plain_core"] = True; break
print("wrote", sorted(done))
