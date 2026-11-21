#!/bin/bash
# final_eval.sh dev|sealed : evaluate every final run, 8 at a time (waits for training to finish first)
PY=~/Developer/voxcpm-venv/bin/python
tag=$1
while pgrep -f "stillway.train" > /dev/null || pgrep -f runqueue.sh > /dev/null; do sleep 20; done
if [ "$tag" = dev ]; then for r in runs/f_cont_s? runs/f_contiit_s?; do [ -d "${r}_posthoc" ] || PYTHONPATH=. $PY -m stillway.posthoc $r > logs/posthoc_$(basename $r).log 2>&1; done; fi
ls -d runs/f_* | xargs -n 1 basename | xargs -P 8 -I{} ./pipe.sh {} $tag
PYTHONPATH=. $PY tools_aggregate.py $([ "$tag" = sealed ] && echo --sealed) > logs/aggregate_$tag.log 2>&1
echo "final_eval $tag finished at $(date +%H:%M)" >> logs/queue.log
