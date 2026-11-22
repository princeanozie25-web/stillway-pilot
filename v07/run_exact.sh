#!/bin/zsh
# Exact repeats, inspected separately: every arm on the 120 training repositories themselves (seed 1).
#   ./v07/run_exact.sh        (about 1 hour)
set -e
cd "$(dirname "$0")/.."
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.
PUB=data/v07/train; OUT=results/v07/records/exact; SEED=${SEED:-1}
$PY v07/run_arm.py $PUB $OUT base 0 plain
$PY v07/run_arm.py $PUB $OUT patches $SEED plain
$PY v07/run_arm.py $PUB $OUT experience $SEED plain
$PY v07/run_arm.py $PUB $OUT experience_x $SEED plain bank
$PY v07/grade.py $PUB $PUB $OUT
$PY v07/report.py $OUT/graded results/v07/exact || echo "report failed (grouping); graded records are in $OUT/graded"
echo EXACT DONE
