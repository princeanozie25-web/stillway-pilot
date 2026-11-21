#!/bin/bash
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.; n=$1
sleep 5
THREADS=1 $PY tools_eval_sealedfam.py runs/$n --sealed > logs/eval_sealed_$n.log 2>&1
$PY tools_extras.py runs/$n --sealed > logs/extras_sealed_$n.log 2>&1
$PY tools_hidden.py runs/$n --sealed > logs/hidden_sealed_$n.log 2>&1
