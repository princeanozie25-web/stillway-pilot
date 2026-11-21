#!/bin/bash
# two-field counterexample sweep for the other primary seeds (after the heavy M1 runs)
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
while pgrep -f "m1_all.sh|m1_post.sh" > /dev/null; do sleep 30; done
for s in 1 2 3 5; do v02/par.sh 4 v02/m1_counterexample.py runs/f_iit_s$s; $PY v02/m1_counterexample.py runs/f_iit_s$s merge > logs/v02_cx_merge_s$s.log 2>&1; done
$PY v02/m1_report.py > logs/v02_m1_report.log 2>&1
echo "M1 counterexamples + report done $(date +%H:%M)" >> logs/v02_queue.log
