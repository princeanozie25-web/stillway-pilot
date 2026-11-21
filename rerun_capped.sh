#!/bin/bash
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.; n=$1
CAP=600 THREADS=1 $PY tools_eval_capped.py runs/$n --sealed > logs/eval_sealed_$n.log 2>&1
