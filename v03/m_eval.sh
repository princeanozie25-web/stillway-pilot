#!/bin/bash
# m_eval.sh NAME : arm M evaluation with the frozen v0.2 scripts (scaling protocol and development edit attempts).
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.; n=$1; mkdir -p results/v03/scaling results/v03/m_dev
THREADS=1 $PY v02/m4_scaling.py runs/$n > logs/m4_$n.log 2>&1 && mv results/v02/scaling/$n.json results/v03/scaling/$n.json
$PY v02/m3_eval.py runs/$n dev > logs/m3dev_$n.log 2>&1 && mv results/v02/m3/${n}_dev.json results/v03/m_dev/ && mv results/v02/m3/${n}_dev_items.json results/v03/m_dev/
echo "m_eval $n done $(date +%H:%M)" >> logs/v03_queue.log
