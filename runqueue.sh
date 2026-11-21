#!/bin/bash
# runqueue.sh QUEUEFILE : wait until no training is running, then train every line of the queue, 8 at a time
PY=~/Developer/voxcpm-venv/bin/python
while pgrep -f "stillway.train" > /dev/null; do sleep 20; done
cat "$1" | xargs -P 8 -L 1 bash -c 'name=$0; '"$PY"' -m stillway.train --name "$name" "$@" > "logs/$name.log" 2>&1'
echo "queue $1 finished at $(date +%H:%M)" >> logs/queue.log
