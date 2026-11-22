#!/bin/zsh
# Milestone 3 in one place.   ./v08/run_m3.sh train | eval SPLIT | all SPLIT
#   train       every arm in ARMS for every seed in SEEDS, STEPS optimiser steps each (skips checkpoints that exist)
#   eval SPLIT  every checkpoint through the sandboxed runner on data/v08/SPLIT/public.jsonl, one job at a time; then grade and report
# Environment: PY (python), ARMS (default "base exec shuf"), SEEDS (default "1 2 3"), STEPS (default 8000), TAG (default core)
set -eu
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; ARMS=(${=ARMS:-base exec shuf}); SEEDS=(${=SEEDS:-1 2 3}); STEPS=${STEPS:-8000}; TAG=${TAG:-core}; EXTRA=(${=EXTRA:-})
export PYTHONPATH=.; mkdir -p artifacts/v08 logs
train() {
  for s in $SEEDS; do for a in $ARMS; do
    out=artifacts/v08/${TAG}_${a}_s${s}.safetensors
    [[ -f $out ]] || $PY v08/train_core.py $a $s $out --steps $STEPS $EXTRA >> logs/v08_train_${TAG}.log 2>&1
  done; done
}
evaluate() {
  split=$1; dir=results/v08/$split/$TAG; mkdir -p $dir
  for s in $SEEDS; do for a in $ARMS; do
    $PY v08/run_core.py artifacts/v08/${TAG}_${a}_s${s}.safetensors data/v08/$split/public.jsonl $dir/${a}_s${s}.jsonl >> logs/v08_eval_${TAG}_${split}.log 2>&1
  done; done
  [[ -f $dir/teacher_s0.jsonl ]] || $PY v08/run_core.py teacher data/v08/$split/public.jsonl $dir/teacher_s0.jsonl --hidden data/v08/$split/hidden.jsonl >> logs/v08_eval_${TAG}_${split}.log 2>&1
  [[ -f $dir/search_s0.jsonl ]] || $PY v08/ref_search.py data/v08/$split/public.jsonl $dir/search_s0.jsonl >> logs/v08_eval_${TAG}_${split}.log 2>&1
}
grade() { split=$1; dir=results/v08/$split/$TAG; $PY v08/grade.py data/v08/$split/public.jsonl data/v08/$split/hidden.jsonl $dir/*_s[0-9].jsonl; $PY v08/report.py $dir results/v08/${split}_${TAG} ${=REPORT:-} > /dev/null; echo "tables: results/v08/${split}_${TAG}_tables.md"; }
case $1 in
  train) train;;
  eval) evaluate $2;;
  grade) grade $2;;
  all) train; evaluate $2; grade $2;;
esac
