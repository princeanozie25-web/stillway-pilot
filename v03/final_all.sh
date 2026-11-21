#!/bin/bash
# final_all.sh SEED : every final test of docs/v03_spec.md section 5 for every frozen register core, 7 at a time.
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.; seed=$1
ls -d runs/v3[rcn]2*_s? | xargs -P 7 -I{} sh -c "$PY v03/eval_edits.py {} v02final > logs/f1_\$(basename {}).log 2>&1; $PY v03/eval_edits.py {} final $seed > logs/f2_\$(basename {}).log 2>&1; $PY v03/confirm.py {} > logs/f3_\$(basename {}).log 2>&1"
for r in runs/v3r23fix_s1 runs/v3r24fix_s1 runs/v3r24fix_s2; do $PY v03/latency.py $r > logs/f5_$(basename $r).log 2>&1; done
$PY tests/test_regcore.py runs/v3r2*_s? > logs/f4_regcore.log 2>&1
echo "final_all done $(date +%H:%M)" >> logs/v03_queue.log
