# Stillway v0.8: execution and memory

A local script runner, a one-million-parameter core trained from random initialisation on executed experience, and a memory bank of tested procedures. Report: `results/v08/REPORT_v08.md`. One-page memo: `docs/v08_memo.md`. Frozen protocol: `docs/v08_protocol.md`. What was found along the way: `docs/v08_exploratory_log.md`.

## One-command checks

| Command | What it does | Time |
|---|---|---|
| `python v08/demo.py --smoke` | Two sessions with the small core: proposed script, predicted effect, execution, what entered memory; then the same project with an altered precondition | about 10 s |
| `python v08/replay.py results/v08/examples/success_proj.json --hidden data/v08/fixture/hidden.jsonl` | Replays one stored experience in a fresh sandbox and grades the result | 1 s |
| `./v08/bench_small.sh` | The small benchmark: the 80 fixture jobs with the frozen core, the teacher's procedure and the search script, graded, with tables | about 2 min |

Set `PY=/path/to/python` if it is not `~/Developer/voxcpm-venv/bin/python` (Python 3.12, `torch` 2.14, `safetensors`, `numpy`; macOS for `sandbox-exec`). Run from the repository root with `PYTHONPATH=.`.

## Layout

| Path | What |
|---|---|
| `stillway8/opsrt.py` | The operations, as they run inside a workspace: one file, no imports from this repository. A script is lines of operations or Python that calls them. |
| `stillway8/runner.py` | Disposable workspaces, the sandbox, the ledger of scripts and operations |
| `stillway8/world.py`, `dataset.py` | The two task worlds, their generators, the splits and the held-out mechanisms |
| `stillway8/expert.py` | The teacher (careful procedure, slips and recoveries) and the token format |
| `stillway8/grade.py`, `v08/grade.py` | The independent grader; the only code that reads a hidden file |
| `stillway8/model.py`, `agent.py` | The core, its training loop, cached decoding, the loop that works one job |
| `stillway8/experience.py`, `bank.py` | Experience records and replay; the bank, promotion, the gate, compiled procedures |
| `v08/build_data.py`, `train_core.py`, `run_core.py`, `report.py`, `run_m3.sh` | Data, training, inference, tables for the core |
| `v08/overfit.py` | The development overfit test |
| `v08/ref_search.py` | A fixed search script with no model, as a reference |
| `v08/m2_harness.py` | One frozen model, one operation per call against composed scripts |
| `v08/m4_memory.py`, `m4_day2.sh`, `m4_report.py`, `m4_audit_mix.py` | Day 1, the night, day 2; the audit-mixing test |
| `v08/demo.py`, `replay.py`, `make_examples.py` | The demo, replay of an experience, the two worked examples |
| `v08/pack_holdout.py`, `docs/v08_holdout_brief.md` | For the independent holdout author |

## Data and records

| Path | What |
|---|---|
| `data/v08/MANIFEST.json` | Hashes of generators, splits and files; the cost of generating the training records |
| `data/v08/{dev,hold,fixture,day1,day2}/public.jsonl`, `hidden.jsonl` | Job sets: what a runner sees, and what only the grader reads |
| `data/v08/pretrain/records.jsonl` | Not in git (about 500 MB); rebuilt exactly by `python v08/build_data.py pretrain 480000 120000 9` |
| `artifacts/v08/*.safetensors` + `.json` | Checkpoints with their training logs |
| `results/v08/<set>/<tag>/*.jsonl` | Raw records per arm and seed; `.graded.jsonl` adds the independent outcome |
| `results/v08/examples/` | One replayable success per domain; one plausible script per domain that passes every visible check and fails the independent test |

## Reproducing from nothing

```
python v08/build_data.py eval                              # evaluation sets, every job checked by execution
python v08/build_data.py pretrain 480000 120000 9          # training records (about 40 minutes on 9 cores)
python v08/overfit.py prepare                              # then train and run as in docs/v08_protocol.md
./v08/run_m3.sh all dev                                    # 3 arms x 3 seeds: train, run, grade, tables
python v08/m4_memory.py sets && python v08/m4_memory.py day1 CKPT && python v08/m4_memory.py night CKPT exec && ./v08/m4_day2.sh CKPT
```

Checkpoints retrained elsewhere will not match the stored hashes bit for bit; the records in `results/v08/` were produced by the stored ones.
