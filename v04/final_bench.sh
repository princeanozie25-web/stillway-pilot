#!/bin/bash
# final_bench.sh : every timing measurement of v0.4, one after another, on an idle machine.
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.
for G in 2 3 4; do $PY v04/m1_bench.py exact $G > logs/v04_b_exact_g$G.log 2>&1; done
for r in runs/v4f_r_g2_w128_s1 runs/v4f_r_g2_w256_s1 runs/v4f_r_g2_w512_s1 runs/v4f_r_g3_w128_s1 runs/v4f_r_g3_w256_s1 runs/v4f_r_g3_w512_s1; do
  [ -f $r/tables.bin ] && $PY v04/m1_bench.py $r > logs/v04_b_$(basename $r).log 2>&1
done
for s in 1 2 3 4 5; do [ -f results/v04/m3/v4f_proc_s_s$s/snapshot_v6.pt ] && $PY v04/m4_bench.py $s > logs/v04_b_m4_s$s.log 2>&1; done
$PY v04/demo.py runs/v4f_proc_s_s1 3 > logs/v04_b_demo.log 2>&1
$PY v04/fixtures.py make > logs/v04_b_fixtures.log 2>&1
echo "final_bench done $(date +%H:%M)" >> logs/v04_queue.log
