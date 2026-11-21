"""Hand-scored worked fixtures: one normal/reversed pair and one swap, scored for every hand planner."""
import json
from stillway.world import *
from stillway.planners import HAND_PLANNERS
from stillway.scorer import run_episode, run_swap, select_slots, score_item
from stillway.fixtures import SPLIT, reversal_eligible

e_norm = (K, K, K, T)          # leg 1: both routes keep the gate.  leg 2: L keeps, R toggles.
e_rev = reverse(e_norm, [2])   # leg 2 reversed: L toggles, R keeps.
print("family", family_of(e_norm), "split", SPLIT[family_of(e_norm)], "eligible", reversal_eligible(e_norm, 1, 1, [2]))
order = Order(1, 1, 2)         # parcel 1 -> dock 1, gate must be OPEN on arrival, parcel 2 -> bay 2
A = Episode(e_norm, 1, order.copy(), id="worked-normal")
B = Episode(e_rev, 1, order.copy(), id="worked-reversed")
pair = {"kind": "pair", "class": "wiring_reversal", "a": A.to_json(), "b": B.to_json()}
Aq = Episode(e_norm, 1, Order(1, 0, 2), id="worked-normal-closed")
rs = {"kind": "pair", "class": "route_swap", "a": A.to_json(), "b": Aq.to_json()}
T = Episode(e_rev, 1, Order(1, 1, 2), id="worked-target")      # reversed wiring, wants gate OPEN
S = Episode(e_norm, 1, Order(0, 0, 0), id="worked-donor")      # normal wiring, wants gate CLOSED
swap = {"kind": "swap", "class": "swap", "target": T.to_json(), "donor": S.to_json(), "pause_after": "PLAN",
        "expect": {"gate": 0, "dock": 1, "bay": 2}}
out = {"pair": pair, "route_swap": rs, "swap": swap, "scores": {}}
for name, p in HAND_PLANNERS.items():
    ra, rb = run_episode(p, A, keep_log=True), run_episode(p, B, keep_log=True)
    acts = lambda r: [s["proposed"] for s in r["log"] if s["proposed"]]
    slots = {"reference": [1], "impostor_lookup_lr": [1], "impostor_memoryless": [0], "impostor_plan_cache": [0, 1], "impostor_entangled": [0]}[name]
    sw = run_swap(p, T, S, 1, slots, swap["expect"])
    row = {"normal_actions": acts(ra), "normal_credit": ra["all_valid"], "reversed_actions": acts(rb), "reversed_credit": rb["all_valid"],
           "wiring_reversal_pair_credit": score_item(p, pair)["credit"], "route_swap_pair_credit": score_item(p, rs)["credit"],
           "swap_slots": slots, "swap_routes": ["LR"[x] for x in sw["routes"]], "swap_gate_arrival": sw["gate_arrival"],
           "swap_dock": sw["dock_done"], "swap_bay": sw["bay_done"], "swap_credit": sw["credit"]}
    out["scores"][name] = row
    print(name, json.dumps(row))
json.dump(out, open("fixtures/dev/worked_example.json", "w"), indent=1)
