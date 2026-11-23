#!/bin/zsh
# Baseline on the development tasks: each model in turn, the same tools and limits, then the grader.   repair/run_dev.sh [OUTDIR]
cd "$(dirname "$0")/.." || exit 1
OUT=${1:-results/repair/dev}; PYV=${PYV:-$HOME/Developer/voxcpm-venv/bin/python}; mkdir -p $OUT logs
for m in qwen3.5:2b qwen3.5:9b-mlx gemma4:12b-mlx; do
  tag=${m//[:.]/_}
  $PYV repair/agent.py $m data/repair/dev/public.jsonl $OUT/$tag.plain.jsonl >> logs/repair_dev_$tag.log 2>&1
  /usr/local/bin/ollama stop $m > /dev/null 2>&1 || ollama stop $m > /dev/null 2>&1
done
for m in qwen3.5:2b qwen3.5:9b-mlx gemma4:12b-mlx; do
  tag=${m//[:.]/_}
  $PYV repair/grade.py data/repair/dev/public.jsonl data/repair/dev/hidden.jsonl $OUT/$tag.plain.jsonl $OUT/$tag.plain.graded.jsonl > logs/repair_dev_grade_$tag.log 2>&1
done
echo ALL_DONE >> logs/repair_dev_done.log
