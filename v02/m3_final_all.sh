#!/bin/bash
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
SEED=$($PY v02/final_seed.py)
for n in v2_iit_s1 v2_iit_s2 v2_iit_s3 v2_iit_s4 v2_iit_s5 v2_plain_s1 v2_plain_s2; do $PY v02/m3_eval.py runs/$n final $SEED > logs/v02_m3_final_$n.log 2>&1 & done; wait
echo "M3 final done $(date +%H:%M) seed $SEED" >> logs/v02_queue.log
