#!/bin/bash
# final_one.sh RUN SEED : F1, F2 and F3 of docs/v03_spec.md for one frozen core
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.; r=$1; n=$(basename $r)
$PY v03/eval_edits.py $r v02final > logs/f1_$n.log 2>&1
$PY v03/eval_edits.py $r final $2 > logs/f2_$n.log 2>&1
$PY v03/confirm.py $r > logs/f3_$n.log 2>&1
