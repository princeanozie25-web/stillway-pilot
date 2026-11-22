# Stillway v0.7: learn a diagnostic from verified experience

A small local coding student, taught from executed bug-fixing experience, tested on whether that experience helps it fix unfamiliar repositories on the first patch. Report: `results/v07/REPORT_v07.md`. One-page memo: `docs/v07_memo.md`. Frozen protocol: `docs/v07_protocol.md`.

**Status, 22 November 2026:** development is finished and everything is locked (`results/v07/LOCK_v07.json`, SHA-256 `deed5cff683e67fb…fa71aef`). The final set is Codex's and has not been opened. Development verdict by the frozen rules: a recognition result (a large gain on repeats and on the same cause in a new setting; none on lookalikes or on mechanisms absent from training). Found after the plan was fixed: the same adapter at a quarter to a half of its strength does help on unfamiliar repositories; that is a separate rule on the final set.

## Before and after in one command

```
./v07/replay.sh
```

Runs the unchanged student and every trained arm on the 72 development repositories, grades them against the hidden tests and writes the tables to `results/v07/replay/`. About 100 minutes per seed on an M1 Max (`SEEDS="1" ./v07/replay.sh` for one seed).

Checked on 22 November with one seed on six repositories: all 16 arm runs completed, 94 of 96 episodes came out word for word as stored and all 96 graded outcomes matched. The two differences come from batching (six repositories in a batch instead of eight). On any other packed set: `./v07/replay.sh PUBLIC_DIR HIDDEN_DIR OUT_DIR`.

## What you need

| Thing | Where |
|---|---|
| Python 3.12 with `torch` 2.14, `transformers` 5.20, `safetensors`, `scikit-learn`, `numpy` | Set `PY=/path/to/python` if it is not `~/Developer/voxcpm-venv/bin/python` |
| The pinned student, 3.1 GB | `python v07/fetch_model.py` downloads `Qwen/Qwen2.5-Coder-1.5B-Instruct` at revision `2e1fd397` and checks the hashes in `results/v07/MODEL_PIN.json` |
| The nine adapters, 74 MB each | GitHub release `v0.7-adapters` on this repository; put them in `artifacts/v07/adapters/`. Or retrain: `python v07/train_adapter.py DATASET SEED` (about 17 minutes each). |
| macOS | Tests run under `sandbox-exec` (no network, no writes outside a temporary folder) |

`python v07/check_lock.py` compares everything on disk with the lock (`--model` also hashes the base weights).

## Layout

| Path | What |
|---|---|
| `stillway7/templates_train.py`, `templates_dev.py` | 12 training designs and 12 development designs, each a small package with one bug, visible tests, hidden tests, a fix, and the teacher's tests |
| `stillway7/tasks.py`, `v07/build_tasks.py` | Builds 120 training and 72 development repositories and checks every one by execution |
| `stillway7/sandbox.py` | Runs a test script or a test file in a fresh copy of a repository; applies a one-function patch |
| `stillway7/student.py` | The pinned model, the low-rank adapter (written by hand; no adapter library), generation, the training loss |
| `stillway7/episode.py` | One episode: two tests with predictions, one patch; the limits; grading |
| `stillway7/bank.py`, `procedures.py`, `v07/build_bank.py` | The versioned diagnostic bank, nearest-example retrieval, the insert each arm gets |
| `v07/build_training.py`, `train_adapter.py` | The three training sets and the adapters |
| `v07/run_arm.py` | The student side. Never reads hidden tests or labels. |
| `v07/grade.py` | The grader. The only script that reads hidden files. |
| `v07/report.py` | Tables, intervals and the frozen rules |
| `v07/analyse_dev.py`, `gate.py`, `costs.py` | Extra tables, the familiarity gate, costs |
| `v07/x_strength.py`, `x_strength_report.py` | Any adapter at reduced strength; the dose table |
| `v07/pack_final.py` | Turns the final-set holder's folders into runner and grader files, checking each by execution |
| `v07/run_dev.sh`, `run_exact.sh`, `replay.sh` | Whole development experiment; exact repeats; before and after |

## Data and records

| Path | What |
|---|---|
| `data/v07/train/` | 120 training repositories with fixes and the teacher's executed tests |
| `data/v07/dev/public/`, `data/v07/dev/hidden/` | 72 development repositories, split into what the student sees and what only the grader reads |
| `data/v07/training/*.jsonl` | The three training sets |
| `artifacts/v07/bank.json` | The bank: 3 diagnostics, each with version 1 (prior procedure and scope) and version 2 (adds a local exception and what to do when contradicted), and the evidence behind each |
| `results/v07/records/teacher_traces.jsonl` | The teacher's executed record for each training repository, failed and contradicted attempts included |
| `results/v07/records/dev/` | Every episode of every arm and seed, ungraded; `graded/` adds the hidden outcome |
| `results/v07/records/exact/` | The same on the 120 training repositories themselves (exact repeats, seed 1) |
| `results/v07/records/x_strength/` | The adapters at 0.25, 0.5 and 0.75 strength on the development repositories |
| `results/v07/dev_tables.md`, `dev_extra.md`, `dev_gate.md`, `exact_tables.md`, `x_strength.md` | Tables. `dev_tables.md` is built from the development and reduced-strength records together: `python v07/report.py results/v07/records/dev/graded,results/v07/records/x_strength/graded results/v07/dev` |
| `results/v07/COSTS.json` | Teacher, execution and training costs, reported apart from the arms |

Each episode record holds: repository id, accessible files, code hash, each proposed test with its prediction (written before execution), the observed output and whether it matched, the insert shown, the patch with its changed lines, generation and tool time, and after grading the outcome of every hidden and visible test.

## Reproducing from nothing

```
python v07/fetch_model.py && python v07/smoke_model.py     # pin and smoke test
python v07/build_tasks.py                                  # 192 repositories, checked by execution
python v07/build_bank.py && python v07/build_training.py   # bank and training sets
./v07/run_dev.sh                                           # trains 9 adapters, runs and grades every arm (about 5 hours)
```

Adapters retrained on another machine will not match the locked hashes bit for bit; the records in `results/v07/records/` were produced by the locked ones.
