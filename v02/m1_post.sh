#!/bin/bash
# after m1_all.sh: matched-history comparison for the other primary seeds, then retrain seeds 2, 3, 5 (M0)
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
while pgrep -f m1_all.sh > /dev/null; do sleep 30; done
for s in 1 2 3 5; do THREADS=2 $PY v02/m1_matched.py runs/f_iit_s$s 20000 > logs/v02_matched_s$s.log 2>&1 & done; wait
echo "M1 matched done $(date +%H:%M)" >> logs/v02_queue.log
for s in 2 3 5; do $PY -m stillway.train --name r_iit_s$s --iit 1.0 --seed $s > logs/r_iit_s$s.log 2>&1 & done; wait
echo "M0 retrain 2,3,5 done $(date +%H:%M)" >> logs/v02_queue.log
