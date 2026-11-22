#!/bin/zsh
# One command: before and after.  Runs the unchanged student and every trained arm whose adapter is present, grades and reports.
#   ./v07/replay.sh                                   development repositories, into results/v07/replay
#   ./v07/replay.sh PUBLIC_DIR HIDDEN_DIR OUT_DIR     any packed set (see v07/pack_final.py)
#   SEEDS="1" ./v07/replay.sh                         one seed only (about 35 minutes for 72 repositories)
set -e
cd "$(dirname "$0")/.."
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.
PUB=${1:-data/v07/dev/public}; HID=${2:-data/v07/dev/hidden}; OUT=${3:-results/v07/replay}; SEEDS=(${=SEEDS:-1 2 3})
$PY v07/check_lock.py || echo "WARNING: files differ from the lock (results/v07/LOCK_v07.json)"
$PY v07/run_arm.py $PUB $OUT base 0 plain bank example
for seed in $SEEDS; do
  [ -f artifacts/v07/adapters/patches_s${seed}.safetensors ] && $PY v07/run_arm.py $PUB $OUT patches $seed plain
  [ -f artifacts/v07/adapters/experience_s${seed}.safetensors ] && $PY v07/run_arm.py $PUB $OUT experience $seed plain
  [ -f artifacts/v07/adapters/experience_x_s${seed}.safetensors ] && $PY v07/run_arm.py $PUB $OUT experience_x $seed plain bank example wrong bank_v1
  # the same adapters at reduced strength (added after development; docs/v07_protocol.md section 8)
  [ -f artifacts/v07/adapters/patches_s${seed}.safetensors ] && $PY v07/x_strength.py $PUB $OUT patches $seed 0.5 plain
  [ -f artifacts/v07/adapters/experience_s${seed}.safetensors ] && $PY v07/x_strength.py $PUB $OUT experience $seed 0.5 plain
  [ -f artifacts/v07/adapters/experience_x_s${seed}.safetensors ] && $PY v07/x_strength.py $PUB $OUT experience_x $seed 0.5 plain bank
  [ -f artifacts/v07/adapters/experience_x_s${seed}.safetensors ] && $PY v07/x_strength.py $PUB $OUT experience_x $seed 0.25 plain
  [ -f artifacts/v07/adapters/experience_x_s${seed}.safetensors ] && $PY v07/x_strength.py $PUB $OUT experience_x $seed 0.75 plain
done
$PY v07/grade.py $PUB $HID $OUT
$PY v07/report.py $OUT/graded $OUT/replay
