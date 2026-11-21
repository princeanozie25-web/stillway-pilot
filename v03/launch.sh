#!/bin/bash
# launch.sh NAME SCRIPT [args] : run one v0.3 job in the background, log in logs/NAME.log
PY=~/Developer/voxcpm-venv/bin/python; name=$1; shift
PYTHONPATH=. nohup $PY "$@" > "logs/$name.log" 2>&1 &
echo "started $name"
