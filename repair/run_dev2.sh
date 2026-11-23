#!/bin/zsh
# Development runs after the small model's plain baseline: guard on the small model, plain on the two larger ones, guard on
# the larger Qwen; then the grader on everything.   repair/run_dev2.sh
cd "$(dirname "$0")/.." || exit 1
OUT=results/repair/dev; PYV=$HOME/Developer/voxcpm-venv/bin/python; P=data/repair/dev/public.jsonl; H=data/repair/dev/hidden.jsonl
$PYV repair/agent_guard.py qwen3.5:2b $P $OUT/qwen3_5_2b.guard.jsonl --respond $H >> logs/repair_dev_guard_qwen3_5_2b.log 2>&1; ollama stop qwen3.5:2b > /dev/null 2>&1
$PYV repair/agent.py qwen3.5:9b-mlx $P $OUT/qwen3_5_9b-mlx.plain.jsonl >> logs/repair_dev_qwen3_5_9b-mlx.log 2>&1
$PYV repair/agent_guard.py qwen3.5:9b-mlx $P $OUT/qwen3_5_9b-mlx.guard.jsonl --respond $H >> logs/repair_dev_guard_qwen3_5_9b-mlx.log 2>&1; ollama stop qwen3.5:9b-mlx > /dev/null 2>&1
$PYV repair/agent.py gemma4:12b-mlx $P $OUT/gemma4_12b-mlx.plain.jsonl >> logs/repair_dev_gemma4_12b-mlx.log 2>&1; ollama stop gemma4:12b-mlx > /dev/null 2>&1
for f in $OUT/*.plain.jsonl $OUT/*.guard.jsonl; do $PYV repair/grade.py $P $H $f ${f%.jsonl}.graded.jsonl > logs/repair_dev_grade_$(basename ${f%.jsonl}).log 2>&1; done
echo ALL_DONE
