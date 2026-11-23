#!/bin/zsh
# Rerun of both guarded arms.  The first runs are kept under results/repair/dev/void/ and are not results:
#   larger Qwen: Ollama's MLX runner refuses a JSON schema, every model call of the guard failed, and with no example and no
#     probe the guard refused every fix.  agent_guard.py now puts the schema into the prompt for such a model and counts
#     every structured call in the record.
#   small model: the guard repaired a wrongly spelt probe call but asked the user about the unrepaired one; two right patches
#     were refused on an answer about a call that fails for another reason.  guard.py now fixes one program per call on the
#     untouched copy and runs and asks about exactly that program.
# repair/run_dev3.sh
cd "$(dirname "$0")/.." || exit 1
OUT=results/repair/dev; PYV=$HOME/Developer/voxcpm-venv/bin/python; P=data/repair/dev/public.jsonl; H=data/repair/dev/hidden.jsonl
for m in qwen3.5:2b qwen3.5:9b-mlx; do
  n=${m//[.:]/_}; f=$OUT/$n.guard.jsonl
  $PYV repair/agent_guard.py $m $P $f --respond $H >> logs/repair_dev_guard_$n.log 2>&1; ollama stop $m > /dev/null 2>&1
  $PYV repair/grade.py $P $H $f ${f%.jsonl}.graded.jsonl > logs/repair_dev_grade_$n.guard.log 2>&1; tail -1 logs/repair_dev_grade_$n.guard.log
done
echo ALL_DONE
