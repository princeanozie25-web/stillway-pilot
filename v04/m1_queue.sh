#!/bin/bash
# m1_queue.sh : M1 learned readers, protocol 2 (one code per exact value vector; training on the exact machine;
# then certificate and witness repair).  One line per run: G width n_codes seed lmax machine_share.  One-hour budget each.
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.; export PY
cat > /tmp/v04_m1_one.sh <<'EOF'
#!/bin/bash
$PY -m stillway4.reader --G $1 --width $2 --n-codes $3 --seed $4 --lmax $5 --machine-share $6 --budget 3600 > logs/v04_m1_g$1_w$2_s$4.log 2>&1
EOF
chmod +x /tmp/v04_m1_one.sh
{
echo "4 512 32768 1 7 0.6"; echo "4 128 32768 1 7 0.6"
for s in 1 2 3 4 5; do for w in 128 256 512; do echo "3 $w 1024 $s 5 0.8"; echo "2 $w 64 $s 4 0.8"; done; done
} | xargs -P 6 -L 1 /tmp/v04_m1_one.sh
echo "m1_queue done $(date +%H:%M)" >> logs/v04_queue.log
