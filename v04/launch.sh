#!/bin/bash
# launch.sh NAME SCRIPT [args] : run one v0.4 job in the background, log in logs/v04_NAME.log
PY=${PY:-~/Developer/voxcpm-venv/bin/python}; name=$1; shift
PYTHONPATH=. nohup $PY "$@" > "logs/v04_$name.log" 2>&1 &
echo "started $name"
