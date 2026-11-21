#!/bin/bash
# cert_all.sh : certificates for every discrete-carry core (and the exploratory outcome-trained cores)
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
ls -d runs/v3r2*_s? runs/v3n2*_s? | xargs -P 6 -I{} sh -c "$PY -m stillway3.certify {} --out results/v03/cert > logs/cert_\$(basename {}).log 2>&1"
ls -d runs/v3o_s? | xargs -P 3 -I{} sh -c "$PY -m stillway3.certify {} --out results/v03/cert_o > logs/cert_\$(basename {}).log 2>&1"
echo "cert_all done $(date +%H:%M)" >> logs/v03_queue.log
