#!/bin/zsh
# v0.6 round 2 on the three spent families (development).   ./v06/run_r2_dev.sh
cd "$(dirname "$0")/.."; PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}
for fam in family_codex.json data/external/cldr/family_cardinal.json data/external/cldr/family_ordinal.json; do
  for i in 0 1 2 3; do $PY -I v06/family2.py $fam --shard $i --of 4 > logs/v06r2_$(basename $fam .json)_$i.log 2>&1 & done; wait
done
echo R2 DEV DONE
