#!/bin/bash
# One-command runner for v0.4.
#   ./run_v04.sh            smoke: checks the frozen artifacts in a few minutes (default)
#   ./run_v04.sh demo       the demo trace: yesterday's bank, a new order and a local correction, sleep, restart, an unseen
#                           combination under the revised policy, compared with every baseline
#   ./run_v04.sh all SALT   every final run again from scratch (hours): training, sleep, interventions; then ./v04/final_bench.sh
# Set PY=/path/to/python (torch 2.14.1, numpy 2.5.4).  The certificate checks in "smoke" step 1 need only numpy.
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.; export PY; mode=${1:-smoke}
if [ "$mode" = "demo" ]; then exec $PY v04/demo.py runs/v4f_proc_s_s1 3; fi
if [ "$mode" = "all" ]; then ./v04/final_all.sh ${2:?give the salt from v04/final_seed.py} && ./v04/final_bench.sh && $PY v04/report.py && $PY v04/manifest_runs.py; exit $?; fi
set -e
echo "== 1. freeze"; $PY v04/check_freeze.py
echo "== 2. schema: legal messages enumerated, register rule"; $PY tests/test_schema.py | tail -2
echo "== 3. certificate of a learned three-gate table set, and the mutation test"
$PY - <<'PYEOF'
import numpy as np
from stillway4.gates import Gates, certify, read_tables
g = Gates(3); ex = g.compile_exact(g.exact_closure()); t = read_tables("runs/v4f_r_g3_w128_s1/tables.bin"); c = certify(t, ex)
print(f"learned tables, 3 gates: {c['pairs']} pairs, {c['route_checks']} checks, {c['route_wrong']} wrong")
n, l, s = [int(x[0]) for x in np.nonzero(ex["valid"] != 3)]; m = dict(ex); m["route"] = ex["route"].copy(); m["route"][n, l, s] ^= 1; c2 = certify(m, ex, want_wrong=1); w = c2["witnesses"][0]
print(f"mutated exact tables: {c2['route_wrong']} wrong; failing job has {len(w['legs'])} leg(s); listing every route choice confirms it: {w['proposed_route'] not in g.brute_valid(w['requirements'], w['gates'], w['legs'])}")
assert c["route_wrong"] == 0 and c2["route_wrong"] >= 1
PYEOF
echo "== 4. failure fixtures replay"; $PY v04/fixtures.py check
echo "== 5. regrade raw outputs with the plain grader (first 200 documents of each set)"; $PY v04/regrade.py runs/v4f_proc_s_s1/raw_outputs.npz 200
echo "== 6. the demo trace against every baseline"; $PY v04/demo.py runs/v4f_proc_s_s1 3
echo "SMOKE PASS"
