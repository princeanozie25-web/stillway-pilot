#!/bin/zsh
# The whole development experiment, resumable: every step skips work whose output file already exists.
#   ./v07/run_dev.sh            (about 9 hours on an M1 Max)
set -e
cd "$(dirname "$0")/.."
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.
U=${U:-300}; T=${T:-2048}; PUB=data/v07/dev/public; HID=data/v07/dev/hidden; OUT=results/v07/records/dev
$PY v07/run_arm.py $PUB $OUT base 0 plain bank example
$PY v07/grade.py $PUB $HID $OUT
for seed in 1 2 3; do
  for ds in patches experience experience_x; do
    [ -f artifacts/v07/adapters/${ds}_s${seed}.safetensors ] || $PY v07/train_adapter.py $ds $seed $U $T
  done
  $PY v07/run_arm.py $PUB $OUT patches $seed plain
  $PY v07/run_arm.py $PUB $OUT experience $seed plain
  $PY v07/run_arm.py $PUB $OUT experience_x $seed plain bank example wrong bank_v1
  $PY v07/grade.py $PUB $HID $OUT
done
# reduced strength (added after development): the three adapters at 0.5, the D-family adapter at 0.25 and 0.75
X=results/v07/records/x_strength
for seed in 1 2 3; do
  $PY v07/x_strength.py $PUB $X experience_x $seed 0.5 plain bank; $PY v07/x_strength.py $PUB $X patches $seed 0.5 plain; $PY v07/x_strength.py $PUB $X experience $seed 0.5 plain
  $PY v07/x_strength.py $PUB $X experience_x $seed 0.25 plain; $PY v07/x_strength.py $PUB $X experience_x $seed 0.75 plain
done
$PY v07/grade.py $PUB $HID $X
$PY v07/report.py $OUT/graded,$X/graded results/v07/dev
$PY v07/analyse_dev.py $OUT/graded results/v07/dev_extra.md; $PY v07/gate.py $OUT/graded results/v07/dev_gate.md; $PY v07/x_strength_report.py
echo PIPELINE DONE
