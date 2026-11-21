#!/bin/bash
# launch.sh NAME [train args...]   -> trains one arm in the background, log in logs/NAME.log
PY=~/Developer/voxcpm-venv/bin/python
name=$1; shift
nohup $PY -m stillway.train --name "$name" "$@" > "logs/$name.log" 2>&1 &
echo "started $name"
