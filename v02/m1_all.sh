#!/bin/bash
# M1 for every primary seed: recover the original 20-pattern maps, then run the 36-pattern certificate.
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
for s in 4 1 2 3 5; do
  r=runs/f_iit_s$s
  if [ ! -f results/v02/maps20/f_iit_s$s/recover_report.json ]; then
    v02/par.sh 8 v02/m1_recover_maps.py $r; $PY v02/m1_recover_maps.py $r merge > logs/v02_recover_merge_s$s.log 2>&1
  fi
  v02/par.sh 8 v02/m1_expanded.py $r; $PY v02/m1_expanded.py $r merge > logs/v02_expanded_merge_s$s.log 2>&1
  echo "M1 seed $s done $(date +%H:%M)" >> logs/v02_queue.log
done
