#!/bin/bash
# launch3.sh NAME [args] : train one v0.2 core in the background, log in logs/NAME.log
PY=~/Developer/voxcpm-venv/bin/python; name=$1; shift
PYTHONPATH=. nohup $PY -m stillway2.train3 --name "$name" "$@" > "logs/$name.log" 2>&1 &
echo "started $name"
