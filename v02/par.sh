#!/bin/bash
# par.sh N SCRIPT ARGS... : run SCRIPT ARGS I N for I in 0..N-1 in parallel, then exit when all are done
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
n=$1; shift; tag=$(basename "$1" .py)
for i in $(seq 0 $((n-1))); do nohup $PY "$@" $i $n > logs/v02_${tag}_$i.log 2>&1 & done; wait
echo "$tag done $(date +%H:%M)" >> logs/v02_queue.log
