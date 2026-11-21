# Stillway v0.4: how to run it and what produced each number

Start with `docs/v04_decision_memo.md` (one page), then `results/v04/REPORT_v04.md`. Earlier versions are untouched: `README.md`, `README_v02.md`, `README_v03.md`, and `FINAL_REPORT.md` for v0.1 to v0.3.

## One command

```bash
./run_v04.sh          # smoke, a few minutes: freeze, schema, a three-gate certificate and the mutation test, fixtures, regrading, the demo trace
./run_v04.sh demo     # only the demo trace against every baseline
```

Fresh environment: `python3.12 -m venv venv && venv/bin/pip install torch==2.14.1 numpy==2.5.4 matplotlib`, then `PY=venv/bin/python ./run_v04.sh`. A C compiler is needed for `v04/runner.c` (benchmarks only).

## What is where

| Path | What |
|---|---|
| `docs/v04_spec.md` | The frozen contest: design, arms, splits, thresholds, budgets. |
| `docs/v04_certificate_scope.md` | What each certificate covers. |
| `docs/v04_sleep_correspondence.md` | Component-by-component mapping to the Sleep framework. |
| `docs/v04_external_challenge.md` | Format for a challenge authored by someone else; `v04/score_external.py`. |
| `stillway4/gates.py`, `reader.py`, `schema.py` | M1: exact planner for G gates, checker, learned reader, legal messages. |
| `v04/runner.c` | One C program for exact tables, learned tables and the table-free exact planner. |
| `stillway4/approvals.py`, `grader.py` | M2: the approvals workflow and the independent plain-Python grader. |
| `stillway4/arms.py`, `scratchpad.py` | The learned arms. |
| `stillway4/sleep.py` | M3: sessions, bank versions, all update arms, the dream check. |
| `stillway4/runtime.py` | Plain-Python runtimes: compiled tables, dependency tracker, replay engine. |
| `runs/v4f_*` | Final runs (salt 2701878737). `runs/v4a_*`, `v4r*`: pilots. `runs/v4x_*`: exploratory. |
| `results/v04/` | `tables.md`, `summary.json`, `MANIFEST_RUNS.json`, `FREEZE_v04.json`, and per-milestone folders `m1` to `m4`, `seed4`, `runtimes`, `demo`, `fixtures`. |

## Commands that were run

```bash
python v04/seed4_ticket.py                       # regression ticket: failing IDs on four runtimes
python v04/export_runtimes.py runs/v3o_s1 runs/v3r24fix_s1 runs/v3r24fix_s2
./v04/m1_queue.sh; ./v04/m2_queue.sh v04/m2_pilot.txt        # pilots (development data)
python v04/freeze.py && git commit; python v04/final_seed.py  # -> 2701878737
./v04/final_all.sh 2701878737                    # final runs: readers, arms, sleep, interventions (about 95 minutes on this machine)
python v04/x_cont_10x.py 1 2701878737            # exploratory
./v04/final_bench.sh                             # timing, on an idle machine; also the demo trace and the fixtures
python v04/timing_samples.py 1; python v04/report.py; python v04/manifest_runs.py
```

One run of each kind:

```bash
PYTHONPATH=. python -m stillway4.reader --G 3 --width 128 --n-codes 1024 --seed 1 --lmax 5     # train, certify (about 3 minutes)
PYTHONPATH=. python -m stillway4.arms --arm proc --size s --seed 1 --salt 2701878737            # about 20 minutes
PYTHONPATH=. python -m stillway4.sleep runs/v4f_proc_s_s1 --seed 1                               # six sessions, all arms
PYTHONPATH=. python v04/m2_interventions.py runs/v4f_proc_s_s1
PYTHONPATH=. python v04/m4_bench.py 1
python v04/regrade.py runs/v4f_proc_s_s1/raw_outputs.npz                                        # success from raw outputs, plain grader
python v04/seed4_diff.py results/v04/seed4/failing_ids_cpu_f32_b1.json OTHER_MACHINE_IDS.json
```
