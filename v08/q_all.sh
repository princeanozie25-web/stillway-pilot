#!/bin/bash
# The questioning-guard pipeline on a set whose hidden half is at hand (development, or a replay with the returned answers).
#   v08/q_all.sh PUBLIC OUTDIR HIDDEN                 development: the stand-in respondent answers
#   v08/q_all.sh PUBLIC OUTDIR - ANSWERS1 ANSWERS2    replay: the two answer files that were returned
# Reference arms (bank, bankguard, search) are run by v08/run_core.py and v08/ref_search.py as in the trap set.
set -e
PUB=$1; D=$2; HID=$3; export PYTHONPATH=.; P=${PYTHON:-$HOME/Developer/voxcpm-venv/bin/python}; C=artifacts/v08/core_exec_s1.safetensors; BK=results/v08/m4/bank_v1.json; mkdir -p $D
[ -f $D/bank_s1.jsonl ] || $P v08/run_core.py $C $PUB $D/bank_s1.jsonl --bank $BK
[ -f $D/bankguard_s1.jsonl ] || $P v08/run_core.py $C $PUB $D/bankguard_s1.jsonl --bank $BK --guard
[ -f $D/search_s0.jsonl ] || $P v08/ref_search.py $PUB $D/search_s0.jsonl
$P v08/run_q.py round1 bankq $PUB $D --ckpt $C --bank $BK
$P v08/run_q.py round1 searchq $PUB $D
for R in 1 2; do
  $P v08/run_q.py questions $D $R
  if [ "$HID" = "-" ]; then A=$([ $R = 1 ] && echo $4 || echo $5); else A=$D/answers_r$R.jsonl; $P v08/q_dev_answer.py $HID $D/questions_r$R.jsonl $A; fi
  $P v08/run_q.py resume bankq $PUB $D $R $A
  $P v08/run_q.py resume searchq $PUB $D $R $A
done
cp $D/bankq.r3.jsonl $D/bankq_s1.jsonl; cp $D/searchq.r3.jsonl $D/searchq_s0.jsonl
echo ALLDONE
