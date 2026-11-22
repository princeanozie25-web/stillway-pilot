#!/bin/zsh
# Day 2 of milestone 4: every arm on data/v08/day2, one job at a time in the sandbox, then grades and tables.   ./v08/m4_day2.sh CKPT
set -eu
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.; CK=$1; O=results/v08/m4; D=$O/day2; P=data/v08/day2/public.jsonl; H=data/v08/day2/hidden.jsonl; mkdir -p $D
run() { [[ -f $D/$1_s0.jsonl ]] || $PY v08/run_core.py $2 $P $D/$1_s0.jsonl ${@:3} >> logs/v08_m4_day2.log 2>&1; }
run core $CK
run core+bank $CK --bank $O/bank_v1.json
run core+bank_priced $CK --bank $O/bank_v1_priced.json
run naive $O/core_naive.safetensors
run replay $O/core_replay.safetensors
run replay+bank $O/core_replay.safetensors --bank $O/bank_v1.json
run sleep $O/core_sleep.safetensors
run sleep+bank $O/core_sleep.safetensors --bank $O/bank_v1.json
run teacher teacher --hidden $H
[[ -f $D/search_s0.jsonl ]] || $PY v08/ref_search.py $P $D/search_s0.jsonl >> logs/v08_m4_day2.log 2>&1
$PY v08/grade.py $P $H $D/*_s0.jsonl
$PY v08/m4_report.py > /dev/null; echo "tables: results/v08/m4_tables.md"
