# Stillway pilot v0.1: a planner you can pause, correct and resume

Start with `REPORT.md`. It has the verdict, the numbers and the open decisions.

## What is here

| Path | What it is |
|---|---|
| `REPORT.md` | The findings, in plain language, with every table. |
| `docs/claim_matrix.md` | Prior art checked on the web, and the comparison that could sink each claim. |
| `docs/evaluator_spec.md` | The scoring contract: schemas, splits, thresholds, worked example, impostor results. |
| `docs/decisions.md` | Decisions made on Prince's behalf, and the ones left for him. |
| `stillway/world.py` | The world and the exact planner. This file is the spec. |
| `stillway/planners.py` | Reference solution and four impostors. |
| `stillway/fixtures.py` | Fixture generator and the hashed train / dev / sealed split. |
| `stillway/scorer.py`, `stillway/replay.py` | Credit rules, the paired replay and its controls. |
| `stillway/model.py`, `stillway/train.py`, `stillway/vworld.py` | The learned planner, training, and a fast copy of the world. |
| `stillway/automaton.py` | Exhaustive extraction of the machine a discrete planner implements. |
| `stillway/extras.py` | Dictionary, typed patch, quotient memory. |
| `stillway/posthoc.py` | Quantise a continuous planner after training (the Koul-style comparison). |
| `fixtures/dev/` | Public development fixtures and the worked example. |
| `fixtures/sealed/` | Sealed fixtures. Opened only after `FREEZE.json` was written. |
| `runs/` | One folder per trained planner: checkpoint, manifest, raw results. |
| `results/` | Aggregated tables and the clean-room cross-check. |
| `independent/` | A clean-room simulator written from the spec alone. |
| `demo/` | The browser replay bench (the checkpoint running in JavaScript). |

## Commands that were run

Python is `~/Developer/voxcpm-venv/bin/python` (Python 3.12, torch 2.14, CPU). Nothing was installed. Run from this folder with `PYTHONPATH=.`.

```bash
python -m stillway.fixtures make-dev                 # public dev fixtures
python tools_score_hand.py                           # reference + impostors on dev fixtures
python tools_worked_example.py                       # the hand-scored worked fixture
python tests/test_vworld.py                          # fast world == spec world
python tests/test_machine.py runs/NAME KT-KT TT-TT   # extractor == plain simulation; witnesses reproduce
python -m stillway.train --name f_iit_s1 --iit 1.0 --seed 1      # one training run (see queue2.txt for all arms)
python -m stillway.posthoc runs/f_cont_s1            # quantise a continuous planner after training
./final_eval.sh dev                                  # every final run on dev fixtures
python -m stillway.fixtures make-sealed              # write the sealed fixtures (not opened by any code yet)
python tools_freeze.py runs/f_*                      # freeze checkpoints, slot choices, scorer hashes
./final_eval.sh sealed                               # the sealed run, once
python tools_check_freeze.py                         # nothing changed since the freeze
python tools_aggregate.py --sealed                   # tables in results/
python tools_compare_independent.py                  # compare with the clean-room simulator
python tools_eval_capped.py runs/NAME --sealed       # post-freeze: same check with a state cap (3 runs)
python tools_eval_sealedfam.py runs/NAME --sealed    # post-freeze: same check on sealed families only (2 runs)
python tools_timing.py runs/f_iit_s3                 # latency
python demo/export.py runs/f_iit_s5 && node demo/verify.js   # JS engine == PyTorch (seed 5: 0 mismatches)
```

## Clean rerun

1. Any Python 3.12 with torch 2.x and numpy.
2. `python -m stillway.fixtures make-dev` must reproduce the SHA-256 values in `FREEZE.json`.
3. Train with the seeds in `runs/*/manifest.json`. CPU, one thread per run. Checkpoint hashes will match only on the same torch build and CPU; outcomes should match in distribution.
4. `./final_eval.sh dev`, then `./final_eval.sh sealed`.

One assistant built the evaluator and the planner in one session. That is not independent reproduction. The clean-room simulator in `independent/` was written by a second assistant instance from the spec alone; it is a cross-check of the spec, also not independent reproduction.
