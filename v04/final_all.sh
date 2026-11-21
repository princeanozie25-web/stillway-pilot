#!/bin/bash
# final_all.sh SALT : the final runs of docs/v04_spec.md section 6.  5 at a time, one-hour budget per run.
# Timing benchmarks are NOT run here: v04/final_bench.sh runs them afterwards on an idle machine.
PY=${PY:-$HOME/Developer/voxcpm-venv/bin/python}; export PYTHONPATH=.; export PY; SALT=$1; export SALT
cat > /tmp/v04_final_one.sh <<'EOS'
#!/bin/bash
case $1 in
  reader) $PY -m stillway4.reader --G $2 --width $3 --n-codes $4 --seed $5 --lmax $6 --budget 3600 --name v4f_r_g$2_w$3_s$5 > logs/v04_f_r_g$2_w$3_s$5.log 2>&1 ;;
  text)   $PY -m stillway4.scratchpad --size s --seed $2 --salt $SALT --budget 3600 --name v4f_text_s_s$2 > logs/v04_f_text_s$2.log 2>&1 ;;
  g5)     $PY -c "
import json, time
from stillway4.gates import Gates
c = Gates(5).exact_closure(max_seconds=3600, max_bytes=4e9, ckpt='results/v04/m1/exact_g5_frontier.npz')
json.dump({k: (v if not hasattr(v, 'shape') else list(v.shape)) for k, v in c.items() if k != 'ids'}, open('results/v04/m1/exact_g5.json', 'w'), indent=1)" > logs/v04_f_g5.log 2>&1 ;;
  *)      $PY -m stillway4.arms --arm $1 --size s --seed $2 --salt $SALT --budget 3600 --name v4f_$1_s_s$2 > logs/v04_f_$1_s$2.log 2>&1
          if [ "$1" = "proc" ]; then
            $PY -m stillway4.sleep runs/v4f_proc_s_s$2 --seed $2 > logs/v04_f_sleep_s$2.log 2>&1
            $PY v04/m2_interventions.py runs/v4f_proc_s_s$2 > logs/v04_f_iv_s$2.log 2>&1
          fi ;;
esac
EOS
chmod +x /tmp/v04_final_one.sh; mkdir -p results/v04/m1 results/v04/m2 results/v04/m3 results/v04/m4
{
for s in 1 2 3 4 5; do echo "proc $s"; done
echo "g5"
for s in 1 2 3 4 5; do echo "macro $s"; echo "cont $s"; echo "vq $s"; echo "text $s"; done
for s in 1 2 3 4 5; do for w in 128 256 512; do echo "reader 3 $w 1024 $s 5"; echo "reader 2 $w 64 $s 4"; done; done
} | xargs -P ${PAR:-5} -L 1 /tmp/v04_final_one.sh
echo "final_all done $(date +%H:%M)" >> logs/v04_queue.log
