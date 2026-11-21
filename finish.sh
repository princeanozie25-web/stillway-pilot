#!/bin/bash
# finish.sh : dev pass for the late runs, write sealed fixtures, freeze, sealed pass, checks.
PY=~/Developer/voxcpm-venv/bin/python; export PYTHONPATH=.
while pgrep -f "stillway.train" > /dev/null; do sleep 20; done
for n in f_hiddenw_s1 f_hiddenw_s2 f_iithiddenw_s1; do ./pipe.sh $n dev & done; wait
$PY tools_aggregate.py > logs/aggregate_dev.log 2>&1
$PY -m stillway.fixtures make-sealed > logs/make_sealed.log 2>&1
PRIMARY=iit $PY tools_freeze.py runs/f_* > logs/freeze.log 2>&1
echo "frozen at $(date +%H:%M)" >> logs/queue.log
./final_eval.sh sealed
$PY tools_check_freeze.py > logs/check_freeze.log 2>&1
$PY tools_timing.py runs/f_iit_s1 > logs/timing.log 2>&1
$PY tools_aggregate.py --sealed > logs/aggregate_sealed.log 2>&1
echo "finish done at $(date +%H:%M)" >> logs/queue.log
