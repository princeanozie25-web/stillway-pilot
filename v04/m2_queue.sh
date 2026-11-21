#!/bin/bash
# m2_queue.sh LINES_FILE : approvals arms, one "arm size seed" per line, 4 at a time, one-hour budget each
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.; export PY
cat > /tmp/v04_m2_one.sh <<'EOS'
#!/bin/bash
$PY -m stillway4.arms --arm $1 --size $2 --seed $3 --budget 3600 > logs/v04_m2_$1_$2_s$3.log 2>&1
EOS
chmod +x /tmp/v04_m2_one.sh
xargs -P ${PAR:-4} -L 1 /tmp/v04_m2_one.sh < $1
echo "m2_queue $1 done $(date +%H:%M)" >> logs/v04_queue.log
