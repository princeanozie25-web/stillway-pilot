#!/bin/bash
# One-command smoke check of v0.3.
#   ./smoke_v03.sh        (step 1 needs only Python; steps 2 and 3 need torch: set PY=/path/to/python)
# 1. the certificate of the repaired core, re-checked from its integer tables by the standalone checker
# 2. the four recorded v0.2 fixtures (two of them v0.2 failures) replayed with the v0.3 core and a register write
# 3. one 16-leg job with a correction: network, certified tables and exact planner side by side
PY=${PY:-~/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.
$PY stillway3/check_tables.py results/v03/cert/v3r24fix_s1_tables.json all || exit 1
$PY - <<'PYEOF'
import json, sys, torch
sys.path.insert(0, "v02")
from run_fixture import run_fixture
from stillway3.certify import TablePlanner, back, extract, term_table, valid_routes
from stillway3.editor import RegisterWrite
from stillway3.model import Fixed4, load_reg
from stillway3.world import WorldN
from stillway2.world3 import ROUTE
model = load_reg("runs/v3r24fix_s1/checkpoint.pt"); ed = RegisterWrite(); edit = lambda ids, f, v: ed(ids, f, v); ok = True
for name in ("success_three_legs", "failure_four_legs", "failure_cross_gate", "declined_on_plain_core"):
    rec = json.load(open(f"fixtures3/{name}.json")); fx = dict(rec["fixture"]); fx["edit"] = {**fx["edit"], "method": "slot_write"}
    t = run_fixture(Fixed4(model), edit, fx); valid = all(s.get("action_valid", True) for s in t["steps"]); old = rec["recorded"]["predictor_edit"]
    good = valid and all(t["gate_requirements_met"]) and all(t["parcels_right"]) and not t["abstained"]; ok &= valid and not t["abstained"]
    print(f"{name:24s} v0.2 ({rec['core']}): {'declined' if old['abstained'] else ('all steps valid' if old['all_actions_valid'] else 'a step was wrong')};  "
          f"v0.3 register write: {'all steps valid' if valid else 'A STEP WAS WRONG'}, gates {t['final_gates']}, requirements met {t['gate_requirements_met']}")
# a 16-leg job, paused before leg 9, gate requirement 0 flipped by a register write
spec = dict(L=(16,), cross=0.3, split="final", K=0, p_wait=0.0, rev=0, gflip=0, decor=0, close=0, msg=0, full=0, reissue=0, env="model")
w = WorldN(1, spec, torch.Generator().manual_seed(2026), lmax=16); w.q[0] = torch.tensor([1, 2]); tp = TablePlanner(extract(model)); ids = torch.full((1, w.NF), -1); line = []
with torch.no_grad():
    for t in range(w.T):
        kind, leg = w.slot(t)
        if kind == ROUTE and leg == 8:
            w.q[0, 0] = 2; ids, _ = ed(ids, torch.tensor([0]), torch.tensor([2]))                 # the order changes; only the register is written
        obs, act = w.next_obs()
        if not bool(act[0]): continue
        logits, ids = model.infer(ids, obs)
        if kind == ROUTE:
            legs = [(int(w.eff[0, j, 0]) * 2 + int(w.tg[0, j, 0]), int(w.eff[0, j, 1]) * 2 + int(w.tg[0, j, 1])) for j in range(leg, 16)]; g = w.gates[0].tolist()
            a = int(logits[0, :2].argmax()); b = tp.route(ids[0, :2].tolist(), g, legs); T = term_table(int(w.q[0, 0]), int(w.q[0, 1]))
            for l in reversed(legs[1:]): T = back(T, l)
            v = valid_routes(T, legs[0], g[0] * 2 + g[1]); ok &= a == b and a in v; line.append("LR"[a] + ("" if a == b and a in v else "!")); w.apply(torch.tensor([a]), act)
        elif kind != 0:
            a = 2 + int(logits[0, 2:].argmax()); ok &= bool(w.valid_mask()[0, a]); w.apply(torch.tensor([a]), act)
print("16-leg job, corrected before leg 9: routes", " ".join(line), "| requirements met", w.gates_ok()[0].tolist(), "| network = tables = exact planner at every leg:", ok)
print("SMOKE PASS" if ok else "SMOKE FAIL"); sys.exit(0 if ok else 1)
PYEOF
