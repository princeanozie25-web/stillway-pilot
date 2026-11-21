#!/bin/bash
# One-command smoke replay of a correction with the frozen v0.2 checkpoint and editor.
#   ./smoke.sh            (uses ~/Developer/voxcpm-venv/bin/python, or set PY=/path/to/python with torch installed)
PY=${PY:-~/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.
$PY - <<'PYEOF'
import json, sys
sys.path.insert(0, "v02")
from run_fixture import load, run_fixture
ok_all = True
for name in ("success_three_legs", "failure_four_legs", "failure_cross_gate", "declined_on_plain_core"):
    rec = json.load(open(f"fixtures3/{name}.json")); model, sw = load("runs/" + rec["core"]); t = run_fixture(model, sw, rec["fixture"])
    valid = all(s.get("action_valid", True) for s in t["steps"]); want = rec["recorded"]["predictor_edit"]
    same = t["final_gates"] == want["final_gates"] and t["abstained"] == want["abstained"]
    ok_all &= same
    e = rec["fixture"]["edit"]; print(f"{name:26s} core {rec['core']:12s} edit field {e['field']} -> {e['value']}: "
          f"{'DECLINED by the editor' if t['abstained'] else ('all steps valid' if valid else 'a step was wrong')}; gates {t['final_gates']}; requirements met {t['gate_requirements_met']}; "
          f"{'matches the recorded run' if same else 'DIFFERS from the recorded run'}")
print("SMOKE PASS: every replay matches its recorded outcome" if ok_all else "SMOKE FAIL"); sys.exit(0 if ok_all else 1)
PYEOF
