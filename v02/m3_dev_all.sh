#!/bin/bash
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
RUNS="v2_iit_s1 v2_iit_s2 v2_iit_s3 v2_iit_s4 v2_iit_s5 v2_plain_s1 v2_plain_s2"
for n in $RUNS; do while [ ! -f runs/$n/checkpoint.pt ]; do sleep 20; done; done
for n in $RUNS; do $PY v02/m3_eval.py runs/$n dev > logs/v02_m3_dev_$n.log 2>&1 & done; wait
echo "M3 dev done $(date +%H:%M)" >> logs/v02_queue.log
