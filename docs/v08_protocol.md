# v0.8 protocol: does learning from executions help a small core choose, check and reuse scripts?

Fable, 22 November 2026. Written before the holdout split (`data/v08/hold`) was run by any model. Everything in sections 1 to 7 is fixed at the lock (`results/v08/LOCK_v08.json`); development figures are in section 8.

## 1. The question and the arms

A core of about one million parameters is trained from random initialisation to work jobs through a local script runner. Two things could be learnt from the same executed experience:

| Arm | Reads | Loss on |
|---|---|---|
| **base** | the teacher's careful record of every job: goal, observations, correct scripts | the action tokens |
| **exec** | the careful records, plus for every job on which the teacher slipped the record with the wrong action, the failed check and the recovery | the action tokens (never the wrong action) and every observation token: it must predict what execution returns |
| **shuf** (control) | as exec | as exec, with the observation targets permuted within each batch, so the outcomes carry no information |

Exploratory, one seed, reported apart: **obsonly** (careful records, observation loss) and **reconly** (exec's records, action loss only), which separate prediction from failures.

Same architecture, same initial weights per seed, same job generators, same inference runner, same compute.

## 2. The core

Decoder-only transformer, written in `stillway8/model.py`: width 128, 5 layers, 4 heads, context 384 tokens, tied input and output embeddings, vocabulary of 206 tokens. **1,067,136 parameters, all active.** It can express: one script at a time, a script being one or more operations from the fixed list in `stillway8/opsrt.py` with arguments from the vocabulary (module names m0..m7, the 23 setting values, keys, groups, numbers n0..n63), then `DONE` or `ASK`. It cannot write free text, a new operation, a number above 63 or a loop. Both arms have exactly this vocabulary.

## 3. Jobs, splits and what is held out

Two domains (`stillway8/world.py`):

- **proj**: a small Python project, six modules in a chain (load, clean, filter, agg, order, report) under shuffled names, up to two unused stand-ins, two visible checks. At most one line is wrong. The repair is a one-line change. Some jobs have nothing wrong (leave it alone); some have a stale expected value that no one-line change can meet (ask for evidence).
- **tab**: a ledger, a statement, notes and a summary of group totals. Each difference is resolved according to its note, then the affected totals are recomputed. Some books are already right; some differences have no note (ask).

Splitting order (`stillway8/dataset.py`): source projects and source books are divided by a hash of their content (train 60%, dev 10%, hold 10%, day 1 7%, day 2 7%, fixture 6%); then mechanisms are divided into trained, held-out transitions (the `newmech` group, never a training fault) and later mechanisms (never a fault in pretraining at all: the settings `col` and `by`, and two table rules; used only in milestone 4); only then are jobs and their cosmetic variations drawn. Hashes of generators, splits and files: `data/v08/MANIFEST.json`.

A fault job is well posed: exactly one one-line change makes its first failing check pass, and it is the repair. Every evaluation job was worked by the teacher through the runner and graded before use.

Evaluation sets of 320 jobs: proj familiar 60, altered precondition 30 (same project and same first report as a familiar job, different cause), held-out transition 40, valid 20, unanswerable 20; tab familiar 50, scattered exceptions 40, stale total only 20, valid 20, unanswerable 20.

## 4. Training

- Records come from actual executions: the teacher (`stillway8/expert.py`) works each training job through the same operations. With probability 0.3 at a repair decision it acts wrongly first, sees the failed check and recovers.
- **Compute is matched by token positions processed** (padding inside a batch and passes included): 80,000,000 per run. Batch 64, AdamW, learning rate 0.002 with 200 warm-up steps and cosine decay to 5%, weight decay 0.01, gradient clipping 1.0. Batches are drawn from windows of records of similar length. Optimiser steps, examples drawn and tokens are logged per run in the checkpoint's `.json`.
- **Selection rule:** the checkpoint after the last step. No early stopping, no choosing among checkpoints.
- **Two regimes of experience**, both three paired seeds:
  - *abundant* (primary): every training job, each read about once;
  - *limited* (secondary): the first 48,000 proj and 24,000 tab training jobs, read about twelve times.
- Data-generation cost is logged apart (`MANIFEST.json`: seconds and operations for the careful records, and the extra for the slipped ones, which only exec and shuf use).

## 5. The inference runner and its limits

`stillway8/agent.py`, identical for every arm: the core is asked for one script; the runner executes it in a fresh sandboxed process inside a disposable copy of the workspace (no network, no writes outside it, 5 s CPU, 10 s wall clock); the observations are appended; repeat. Limits per job: 16 scripts, 48 operations, 20 s, 40 new tokens per script. Greedy decoding, one CPU thread, one job at a time, machine otherwise idle for the frozen runs. The runner never opens a hidden file.

## 6. Scoring

`v08/grade.py` and `stillway8/grade.py`, outside the runner. proj: the final modules run on the two visible inputs and four hidden ones, all four report fields compared. tab: final ledger and summary equal the truth. Unanswerable jobs: only `ASK` with the work untouched is right.

| Measure | Definition |
|---|---|
| Verified job | outcome `verified` |
| **Verified jobs per minute** | verified jobs / total wall time of all jobs (failed ones included) × 60 |
| First-attempt success | verified with at most one editing script and no `REVERT` |
| Answered, error among answers | share ending in `DONE`; share of those not verified |
| Failed edits per solved job | editing scripts that met a failed check / verified jobs |
| Latency | wall seconds per job: median, 90th percentile, maximum |

References in every table, not arms: the teacher's careful procedure through the same loop, and a fixed search script with no model.

## 7. The frozen rule

Primary comparison: **exec against base, abundant regime, three seeds pooled, on the holdout split.** Intervals: 2,000 bootstrap resamples of task families (the fault's setting for proj, the note rule for tab; valid and unanswerable jobs are their own families), jobs paired across arms and seeds.

- **WIN**: over all jobs, verified jobs per minute of exec at least 1.10 times base with the 95% interval above 1.00, **and** in each domain a verified share no more than 2 points below base.
- **NO WIN**: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below −2 points.
- **INCONCLUSIVE** otherwise.

The 10% threshold and the 2-point margin are the brief's suggestion, adopted unchanged. Reported with it, without changing the verdict: each seed, each domain, each group, exec against shuf, the limited regime under the same rule, failures per solved job, the latency distribution and absolute counts.

The holdout here is **author-made**: I wrote its generator. It is fresh in the sense that no model has been run on it and its source projects and books are disjoint from every other split. Codex's independently authored holdout (`docs/v08_holdout_brief.md`) is scored by the same rule when it arrives and is the stronger test.

## 8. Development record (development split only)

See `docs/v08_exploratory_log.md` for what was found and changed before this lock, and `results/v08/dev_*_tables.md` for the tables.
