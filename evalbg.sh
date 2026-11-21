#!/bin/bash
# evalbg.sh NAME [extra args]  -> evaluate one run in the background, log in logs/eval_NAME.log
PY=~/Developer/voxcpm-venv/bin/python
name=$1; shift
THREADS=1 nohup $PY -m stillway.evaluate "runs/$name" "$@" > "logs/eval_$name.log" 2>&1 &
echo "evaluating $name"
