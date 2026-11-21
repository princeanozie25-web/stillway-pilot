#!/bin/bash
# m1_queue.sh : M1 learned readers.  One line per run: G width n_codes seed lmax.  5 at a time, one-hour budget each.
PY=${PY:-~/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.
run() { $PY -m stillway4.reader --G $1 --width $2 --n-codes $3 --seed $4 --lmax $5 --budget 3600 > logs/v04_m1_g$1_w$2_s$4.log 2>&1; }
export -f run; export PY
{
echo "3 128 1024 1 5"; echo "3 256 1024 1 5"; echo "3 512 1024 1 5"; echo "4 512 32768 1 7"
for s in 1 2 3 4 5; do for w in 128 256 512; do echo "2 $w 64 $s 4"; done; done
} | xargs -P 5 -L 1 bash -c 'run $0 $1 $2 $3 $4'
echo "m1_queue done $(date +%H:%M)" >> logs/v04_queue.log
