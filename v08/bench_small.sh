#!/bin/zsh
# The small benchmark: the 80 fixture jobs through the sandboxed runner with a core, the teacher's procedure and the
# search script; graded; tables.   ./v08/bench_small.sh [CKPT]      (default artifacts/v08/demo_core.safetensors)
set -eu
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.; CK=${1:-artifacts/v08/demo_core.safetensors}; D=results/v08/bench_small; P=data/v08/fixture/public.jsonl; H=data/v08/fixture/hidden.jsonl
rm -rf $D; mkdir -p $D
$PY v08/run_core.py $CK $P $D/core_s0.jsonl | tail -1
$PY v08/run_core.py teacher $P $D/teacher_s0.jsonl --hidden $H | tail -1
$PY v08/ref_search.py $P $D/search_s0.jsonl
$PY v08/grade.py $P $H $D/core_s0.jsonl $D/teacher_s0.jsonl $D/search_s0.jsonl
$PY v08/report.py $D $D/bench --primary core:teacher | sed -n '1,22p'
echo "full tables: $D/bench_tables.md"
