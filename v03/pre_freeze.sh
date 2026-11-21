#!/bin/bash
# pre_freeze.sh : certificate-guided repair for every discrete-carry core, then certificates for all of them.
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
{
for s in 1 2 3 4 5; do
  echo "runs/v3r23_s$s --alphabet same --out runs/v3r23fix_s$s"
  echo "runs/v3r24_s$s --alphabet all --out runs/v3r24fix_s$s"
done
} | xargs -P 6 -L 1 sh -c '$0 -m stillway3.repair "$@" > logs/repair_$(basename $5).log 2>&1' $PY
for r in runs/v3r23_s? runs/v3r24_s? runs/v3r23fix_s? runs/v3r24fix_s? runs/v3n23_s? runs/v3n24_s?; do
  $PY -m stillway3.certify $r --out results/v03/cert > logs/cert_$(basename $r).log 2>&1
done
echo "pre_freeze done $(date +%H:%M)" >> logs/v03_queue.log
