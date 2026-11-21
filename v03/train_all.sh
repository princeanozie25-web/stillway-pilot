#!/bin/bash
# train_all.sh : every v0.3 register core (primary seeds and ablations), 6 at a time.  Logs in logs/NAME.log
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
{
for s in 1 2 3 4 5; do echo "v3r23_s$s --data t23 --seed $s"; echo "v3r24_s$s --data t24x --seed $s"; done
for s in 1 2; do
  echo "v3c23_s$s --data t23 --seed $s --carry cont"; echo "v3c24_s$s --data t24x --seed $s --carry cont"
  echo "v3n23_s$s --data t23 --seed $s --aid 0";      echo "v3n24_s$s --data t24x --seed $s --aid 0"
done
} | xargs -P 6 -L 1 sh -c '$0 -m stillway3.train --name "$1" "${@:2}" > logs/$1.log 2>&1' $PY
echo "train_all done $(date +%H:%M)" >> logs/v03_queue.log
