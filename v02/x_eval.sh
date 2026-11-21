#!/bin/bash
# exploratory evaluation of one core: editors + dev, final strata, core accuracy on the strata, scaling sweep
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.; n=$1; SEED=$($PY v02/final_seed.py)
while [ ! -f runs/$n/checkpoint.pt ]; do sleep 20; done
$PY v02/m3_eval.py runs/$n dev > logs/v02_x_dev_$n.log 2>&1
$PY v02/m3_eval.py runs/$n final $SEED > logs/v02_x_final_$n.log 2>&1
THREADS=1 $PY v02/m4_scaling.py runs/$n > logs/v02_x_scaling_$n.log 2>&1
echo "exploratory $n done $(date +%H:%M)" >> logs/v02_queue.log
