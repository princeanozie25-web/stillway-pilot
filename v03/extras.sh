#!/bin/bash
# extras.sh SEED : arm M evaluation (frozen v0.2 scripts), and the exploratory runs (outcome-trained cores, shift)
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.; seed=$1
while pgrep -f "v03/train_m.py" > /dev/null || pgrep -f "final_one.sh" > /dev/null; do sleep 10; done
for s in 1 2 3; do ./v03/m_eval.sh v3m_s$s & done
for s in 1 2 3; do ( $PY v03/eval_edits.py runs/v3o_s$s final $seed > logs/f2_v3o_s$s.log 2>&1; $PY v03/confirm.py runs/v3o_s$s > logs/f3_v3o_s$s.log 2>&1 ) & done
$PY v03/shift.py runs/v3r24fix_s1 300 final > logs/shift_v3r24fix_s1.log 2>&1 &
wait
echo "extras done $(date +%H:%M)" >> logs/v03_queue.log
