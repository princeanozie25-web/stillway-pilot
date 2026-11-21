#!/bin/bash
# final_all.sh SEED : every final test of docs/v03_spec.md section 5 for every frozen register core, 7 at a time.
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.; seed=$1
ls -d runs/v3[rcn]2*_s? | xargs -P 7 -n 1 -I{} ./v03/final_one.sh {} $seed
for r in runs/v3r23fix_s1 runs/v3r24fix_s1 runs/v3r24fix_s2; do $PY v03/latency.py $r > logs/f5_$(basename $r).log 2>&1; done
$PY tests/test_regcore.py runs/v3r2*_s? > logs/f4_regcore.log 2>&1
echo "final_all done $(date +%H:%M)" >> logs/v03_queue.log
