#!/bin/zsh
# The whole development experiment, resumable: every step skips work whose output file already exists.
#   ./v07/run_dev.sh            (about 4 hours on an M1 Max)
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
$PY v07/report.py $OUT/graded results/v07/dev
echo PIPELINE DONE
