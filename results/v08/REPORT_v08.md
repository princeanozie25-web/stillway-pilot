# Stillway v0.8: execution and memory

Fable, for Prince Anozie, 22 November 2026. Branch `v0.8`. One-page memo: `docs/v08_memo.md`. Frozen protocol: `docs/v08_protocol.md`. Exploratory log: `docs/v08_exploratory_log.md`.

**The question.** Does learning from actual executions, from the first training step, help a small model choose, check and reuse scripts cheaply enough to matter?

**The short answer.** It helps the model get more jobs right. On this evidence it does not make a small model the cheap way to do these jobs.

- A one-million-parameter core trained to predict what execution returns verified **80.1%** of fresh jobs against **68.5%** for the same core trained on goals, observations and correct scripts alone (three seeds each, same compute). A control that predicts shuffled outcomes scored 68.3%, so the gain comes from the real outcomes.
- The frozen rule asked for 10% more verified jobs per minute. Measured: **16% more**, with an interval from 0.999 to 1.408 times the baseline. The interval touches 1, so the verdict by the rule written beforehand is **inconclusive**.
- A fixed 20-line search script with no model verified 100% of the same jobs five times faster. The learnt core only costs less per verified job when one operation costs more than about 24 ms.
- A bank of tested procedures, promoted from one day's verified experience and run as scripts, doubled verified project jobs the next day (36% to 74%) at no overnight cost. Overnight weight updates changed the next day's verified jobs by between −1 and +4 per 100 and each lost 6 to 11 jobs the core used to get right. The bank was wrong on 28 of 30 jobs where the visible checks could not tell two repairs apart, unless it was made to ask.

## Status of every result

| Result | Status |
|---|---|
| v0.7 final run: 42 raw files, 4,032 records, returned to Codex ungraded | **Done; grades pending** |
| v0.6 round 2 addendum by the holder's groups | **Frozen run, labels released** |
| M2: single operations against composed scripts, Qwen 1.5B, 48 jobs | **Measured once**, development jobs, small sample |
| M3: exec against base on the author-made holdout, three seeds | **Frozen** (protocol and nine cores locked before the run) |
| M3 on Codex's independently authored holdout | **Pending** (brief sent; no jobs received yet) |
| M3 limited-experience regime, three seeds | **Pre-specified secondary** |
| M3 arms that separate prediction from failure records | **Exploratory**, one seed |
| M4 audit mixing | **Frozen selection rule**, one run on a fresh family |
| M4 bank, overnight updates, day 2 | **Measurement**, settings chosen on a dry run with a pilot core; day 2 redrawn before the real run |
| M4 guarded bank | **Exploratory**, added after seeing the trap result |
| M5 latent updates | **Exploratory**, one seed, development set |

---

## 1. What was built (milestone 1)

**A local script runner.** Every arm of every experiment gets the same operations (`stillway8/opsrt.py`), the same permissions and the same observations. A script is one or more operations; it runs in a fresh process under `sandbox-exec` inside a disposable copy of the workspace: no network, no writes outside the workspace, 5 s of CPU, 1 MB files, 10 s wall clock. Operations are counted one by one, inside scripts too. Graders are outside the runner: `v08/grade.py` is the only script that opens a hidden file.

**Two domains.**

| | proj | tab |
|---|---|---|
| Workspace | a small Python project: six modules in a chain under shuffled names, up to two unused stand-ins, two visible checks | a ledger, a statement, notes, a summary of group totals |
| Job | one line may be wrong; repair it. Trace the imports to find which modules are in use | resolve each difference as its note says; recompute the totals affected |
| Leave it alone | both checks already pass | nothing differs and the summary is right |
| Inspect one more fact | when a failed check shows only a total or a first key, the stage output must be probed before deciding where the fault is | the note on each differing record |
| Ask for evidence | an expected value that no one-line change can meet | a difference with no note |

**Pairs built into every evaluation set:** familiar faults; the same project with the same first report and a different cause (altered precondition); several differences whose notes call for different actions (scattered exceptions); faults upstream that look local, and books where only the dependent total is stale (lookalikes); fault transitions never used in training.

**Splitting order.** Source projects and books are divided by a hash of their content first, mechanisms second, cosmetic variations last (`stillway8/dataset.py`). Hashes of generators, splits and files are in `data/v08/MANIFEST.json`.

**Experience records** (`stillway8/experience.py`) hold the goal, the visible initial state and its hash, every script with the effect predicted before execution, the observed effect and the files it changed, the final diff, the independent verdict, compute and time, and the candidate memory entry with its provenance. Failures and recoveries are kept.

| Shipped | Command |
|---|---|
| Replay one experience in a fresh sandbox and grade it | `python v08/replay.py results/v08/examples/success_proj.json --hidden data/v08/fixture/hidden.jsonl` |
| A small benchmark (80 jobs: a core, the teacher's procedure, the search script) | `./v08/bench_small.sh` |
| One fully replayable success per domain | `results/v08/examples/success_proj.json`, `success_tab.json` |
| A plausible script that passes every visible check and fails the independent test | `results/v08/examples/plausible_proj.json` (two changes that satisfy both checks; hidden inputs disagree), `plausible_tab.json` (accept every difference, recompute) |
| Experience dataset | `data/v08/experience/teacher_fixture.jsonl` (80, of which 35 with a failure and recovery); the core's own, with its predictions: `results/v08/m4/day1_experiences.jsonl` (306) |

**Training-data generation cost, recorded apart.** 372,802 training jobs, each worked by the teacher through the same operations. For the 181 of 400 parts with a cost log: 2,197 CPU-seconds and 1.42 million operations for the careful records of 172,926 jobs, plus 813 CPU-seconds and 0.50 million operations for the records on which the teacher slipped (used only by the execution-aware arms). Scaled to the whole set: about 79 CPU-minutes, and 29 more for the slips.

**google-research/harness2** was read at commit `6868817` (Apache-2.0). No code from it is used. It optimises prompts and skills around hosted agents and needs Linux, hosted models and an unsandboxed executor, so it does not fit a one-million-parameter core. Three of its ideas are implemented locally and measured: scripts that compose tool calls, a ledger that counts executions apart from model calls, and a library of adopted procedures with their evidence. Details: `docs/v08_harness2_notes.md`.

## 2. Closing the previous runs (milestone 0)

- **v0.7.** All 16 arms were run once on Codex's 96 public cases from commit `3db7a18` with the lock intact (ALL MATCH before and after, nine adapters included). 42 raw files, 4,032 records, hash list, failure log and deviations were committed at `cea985b` on branch `v0.7` and sent for blind grading. I have not looked at an outcome. The bank-family adapter's 19% smaller training-token exposure is restated in the return note. Nothing derived from v0.7 grades is used in v0.8.
- **v0.6 round 2.** The addendum by the holder's groups is at `33f7b76` on branch `v0.6r2` (`docs/v06r2_codex2_addendum.md`); the locked files are unchanged. The saving is on local amendments (median 618 audits to the exact table against 1,600 from scratch). Scattered amendments and far policies need the full table. Four audits on repeats and 724 against 1,600 on amendments are medians. Locality is carried forward as a hypothesis only.

## 3. Single operations against composed scripts (milestone 2)

One frozen model (Qwen2.5-Coder-1.5B-Instruct at the v0.7 pin), the same operations, the same 48 development jobs, the same limits (14 model calls, 60 operations, 90 s, 220 new tokens per call). The only difference is what one reply may be: exactly one operation call, or a Python script that calls the same operations with loops and conditions.

| All 48 jobs | One operation per call | Composed scripts |
|---|---|---|
| Verified jobs (eventual success) | 7 (14.6%) | 11 (22.9%) |
| First-attempt success | 14.6% | 20.8% |
| Said done and was wrong | 1 | 13 |
| Asked for evidence on an answerable job | 23 | 8 |
| Ran out of limits | 17 | 16 |
| **Verified jobs per minute** | **1.34** | **1.33** |
| Model calls per job | 7.33 | 6.90 |
| Operations per job, inside scripts too | 6.7 | 21.0 |
| Model tokens, all jobs | 444,381 | 484,684 |
| Extra editing attempts per job | 0.15 | 3.90 |
| Illegal or failed operations | 15 | 142 |
| End-to-end seconds per job: mean / median / 90th percentile | 6.5 / 3.1 / 13.4 | 10.3 / 4.9 / 22.5 |

- Rate ratio, scripts over single operations: 0.99 (interval over jobs 0.48 to 2.52). Eventual success: +8.3 points (−2.1 to +20.8).
- Scripts did three times the operations per job and finished more jobs, but each reply took longer to write and more of the finished jobs were wrong. **No efficiency claim follows.** The sample cannot tell a useful gain from none.
- Full tables per domain: `results/v08/m2_tables.md`. This result is separate from everything about training below.

## 4. The small core (milestone 3)

### 4.1 What it is

| | |
|---|---|
| Architecture | decoder-only transformer, width 128, 5 layers, 4 heads, context 384, tied embeddings (`stillway8/model.py`) |
| Parameters | **1,067,136, all active** |
| Checkpoint | 4,274,832 bytes (32-bit floats) |
| Memory | 230 MB resident for the whole inference process on one CPU thread; 8.3 GB of GPU allocator at the end of a training run (three runs shared the GPU) |
| Vocabulary | 206 tokens: 15 operations, module names m0..m7, 23 setting values, keys, groups, numbers n0..n63, markers |
| It can express | one script at a time (one or more operations with arguments from the vocabulary), then DONE or ASK |
| It cannot express | free text, a new operation, a loop, a number above 63 |

Both arms have exactly this vocabulary, architecture, initial weights per seed, job generators and inference runner.

### 4.2 The arms and what each was trained on

| | base | exec | shuf (control) |
|---|---|---|---|
| Records | the teacher's careful record of each of 372,802 jobs | the same, plus 94,510 records in which the teacher acted wrongly, saw the failed check and recovered | as exec |
| Loss | action tokens | action tokens (never the wrong action) and every observation token | as exec, observation targets permuted within the batch |
| Token positions processed | 80.0 million | 80.0 million | 80.0 million |
| Optimiser steps (seed 1) | 11,904 | 10,445 | 10,442 |
| Examples drawn (seed 1) | 761,856 | 668,480 | 668,288 |
| Extra data-generation work | none | the slipped records: about 37% more teacher seconds | as exec |

Compute is matched by token positions. The execution-aware records are longer, so those arms take about 12% fewer steps and examples. The table for all nine cores is in the protocol, section 10.

**Overfit test (development).** Each arm, trained on 400 training jobs alone and run on those jobs through the sandbox, verified 400 of 400. Both arms can express and solve the elementary tasks.

### 4.3 The frozen comparison on the holdout

320 jobs no model had been run on, from source projects and books in no other split; nine cores locked beforehand (`results/v08/LOCK_v08.json`); one run on an idle machine; raw records committed before grading.

| Seeds pooled (960 job runs per arm) | base | **exec** | shuf | teacher's procedure | search script |
|---|---|---|---|---|---|
| Verified | 658 (68.5%) | **769 (80.1%)** | 656 (68.3%) | 100% | 100% |
| Said done and was wrong | 224 | 113 | 142 | 0 | 0 |
| Asked on an answerable job | 24 | 41 | 112 | 0 | 0 |
| Ran out of limits | 54 | 37 | 50 | 0 | 0 |
| First-attempt success | 68.2% | 75.9% | 61.9% | 100% | n/a |
| Error among answers | 28.2% | 14.1% | 20.4% | 0% | 0% |
| **Verified jobs per minute** | 156.8 | **181.6** | 140.9 | 281.2 | 906.3 |
| Scripts per job | 5.68 | 5.68 | 5.99 | 5.30 | 1 |
| Operations per job | 9.6 | 10.4 | 11.6 | 8.7 | 27.3 |
| Failed edits per solved job | 0.74 | 0.73 | 1.44 | 0 | n/a |
| Model tokens per job | 488 | 490 | 579 | n/a | 0 |
| Latency per job: median / 90th percentile / maximum, s | 0.136 / 0.460 / 1.13 | 0.137 / 0.542 / 0.92 | 0.139 / 0.553 / 1.11 | 0.118 / 0.368 / 0.44 | 0.072 / 0.098 / 0.12 |

**By domain and seed** (verified % / verified jobs per minute):

| | proj seed 1 | seed 2 | seed 3 | tab seed 1 | seed 2 | seed 3 |
|---|---|---|---|---|---|---|
| base | 47.1 / 73 | 36.5 / 55 | 42.4 / 62 | 98.0 / 545 | 99.3 / 550 | 98.7 / 543 |
| exec | 64.1 / 97 | 68.8 / 107 | 54.7 / 78 | 100 / 554 | 100 / 548 | 100 / 546 |
| shuf | 44.7 / 62 | 42.9 / 55 | 34.7 / 47 | 100 / 549 | 100 / 547 | 98.7 / 535 |

**The frozen rule.** WIN needs, over all jobs, at least 1.10 times the baseline's verified jobs per minute with the 95% interval above 1.00, and a verified share no more than 2 points lower in each domain. Intervals resample task families.

| exec against base | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|
| **All jobs** | **1.158 (0.999 to 1.408)** | +11.6 (+4.9 to +18.9) | 1.115 / +10.0; 1.293 / +17.5; 1.077 / +7.2 |
| proj | 1.477 (1.107 to 2.211) | +20.6 (+10.5 to +30.9) | 1.325 / +17.1; 1.944 / +32.4; 1.254 / +12.4 |
| tab | 1.006 (0.991 to 1.027) | +1.3 (0.0 to +3.6) | 1.017 / +2.0; 0.996 / +0.7; 1.004 / +1.3 |

**Verdict: INCONCLUSIVE.** The point estimate clears 1.10 and neither domain is worse, but the lower end of the interval is 0.999, not above 1.00. I report the verdict the rule gives. What is not in doubt on this holdout is the verified share: every seed, both domains, interval clear of zero.

**The control.** shuf against base: rate ratio 0.899 (0.801 to 0.988), verified share −0.2 points (−6.0 to +5.2). exec against shuf: 1.289 (1.092 to 1.628), +11.8 points (+2.9 to +22.0). The extra loss and the failure records without true outcomes bought nothing.

**Where the difference is** (project jobs, verified %, seeds pooled):

| Group | base | exec | shuf |
|---|---|---|---|
| Familiar fault, new project (60) | 49.4 | 74.4 | 33.9 |
| Altered precondition (30) | 37.8 | 61.1 | 40.0 |
| Fault transition never trained (40) | 3.3 | 24.2 | 5.0 |
| Unanswerable: ask (20) | 45.0 | 68.3 | 75.0 |
| Nothing wrong: leave alone (20) | 100 | 100 | 100 |
| Fault in the last stage (local) | 21.4 | 65.8 | 17.1 |
| Fault upstream, reported directly | 35.3 | 53.2 | 23.4 |
| Fault upstream, looks local | 43.1 | 47.2 | 50.0 |

- The largest gain is where the repair has to be worked out from the probed rows (local faults: 21% to 66%) and on transitions never trained (3% to 24%).
- Upstream faults that look local are no better (43% against 47%): both arms are near a coin toss there.
- Table jobs are near the ceiling for every arm; scattered exceptions 95.0% (base) against 100% (exec).

**Does the core recognise its own failures in advance?** No. On day 1 of milestone 4 the exec core wrote down its predicted effect before every script. After an edit of its own it predicted a pass in 203 of 210 project checks that passed and a failure in 3 of 286 that failed. Its predictions are not a usable confidence signal. What prediction training changed is which repair it picks, not whether it knows the pick is wrong.

### 4.4 The limited-experience regime (pre-specified secondary)

[[LIM]]

### 4.5 Prediction or failure records? (exploratory, one seed)

[[EXPL]]

### 4.6 What a verified job costs

| Project jobs, holdout | Seconds per job | Operations per job | Verified % | Seconds per verified job if an operation is free | if an operation costs 0.05 s | 0.5 s | 5 s |
|---|---|---|---|---|---|---|---|
| base | 0.398 | 12.6 | 42.0 | 0.95 | 2.45 | 15.9 | 151 |
| exec | 0.402 | 14.0 | 62.5 | 0.64 | 1.76 | 11.8 | 112 |
| teacher's procedure | 0.316 | 10.9 | 100 | 0.32 | 0.86 | 5.8 | 55 |
| search script | 0.088 | 45.8 | 100 | 0.09 | 2.38 | 23.0 | 229 |

- Wall time here is dominated by starting a sandboxed process per script (about 45 ms), not by operations. That favours one long script.
- The exec core costs less per verified job than the search script once an operation costs more than **24 ms**. Below that, search is cheaper, and on these jobs it is never wrong while the core is wrong on 22% of project jobs.
- The procedure the core imitates would cross at 7 ms. The gap between 7 and 24 is the core's errors.
- Training one core: about 19 minutes of shared GPU for 80 million token positions. Inference: 0.26 s per job (0.40 on project jobs, 0.11 on table jobs), of which the model is 0.018 s and the sandboxed executions the rest.

## 5. What yesterday's experience buys tomorrow (milestone 4)

Selected core: exec, seed 1. **Later mechanisms** were never a fault in pretraining: the project settings `col` and `by`, and two table rules.

### 5.1 Day 1 and the night

- **Day 1** (234 jobs): the frozen core verified 162. The other 72 were then worked by the teacher (24 s, 740 operations: teacher cost, kept apart). 306 experiences were kept, the core's with its predictions.
- **Bank version 1**: 17 procedures, each promoted because at least two verified experiences proposed it, each citing them. 13.7 kB. Promotion and the gate took under 0.1 s.
- **The gate** (when to try which procedure) is learnt separately from the procedures, from the same log: for each first observation, the procedures to try in order of logged success, while success rate times the cost of the fallback exceeds the cost of a try.
- **Weight updates**, each 3 million token positions from the same checkpoint:

| Update | Trained on | Earlier skills (320 development jobs), verified % | Later skills (60 fresh jobs), verified % |
|---|---|---|---|
| none (frozen core) | | 76.9 | 50.0 |
| naive | day-1 records only | 70.3 | 58.3 |
| replay | day-1 records + 20,000 pretraining records, one to one | 74.1 | 55.0 |
| sleep-inspired | as replay + 400 dreams (fresh variations of the later mechanisms, each verified by execution; 7,278 operations) | 71.2 | 65.0 |

- **Promotion check** (earlier skills no more than 2 points down, later skills up): the sleep-inspired update lost 5.7 points on earlier skills and was **not promoted**; the rollback is the frozen core. Ordinary replay would also have failed it (−2.8). Checkpoints of all three are kept (`results/v08/m4/core_*.safetensors`).
- The dreams are what raised later skills (65% against 55%), and they are also what cost earlier ones: a core taught that a wrong total can mean the wrong column starts trying that on old faults.

### 5.2 Day 2 (280 fresh jobs from other sources)

**Project jobs, verified %** (answered % / error among answers %):

| Arm | Retention: earlier skills (80) | Transfer: later mechanisms (50) | Traps (30) | Whole day (160) | Verified jobs per minute, whole day | Operations per job |
|---|---|---|---|---|---|---|
| Frozen core | 58.8 (89 / 42) | 0.0 (82 / 100) | 33.3 (80 / 58) | 35.6 | 47 | 16.4 |
| **Core + bank** | **83.8** (91 / 16) | **100** (100 / 0) | **6.7** (100 / 93) | **74.4** | **312** | 17.8 |
| Core + bank, operations priced at 0.5 s | 68.8 | 100 | 6.7 | 66.9 | 202 | 17.2 |
| Update only: naive | 46.2 | 22.0 | 23.3 | 34.4 | 49 | 15.8 |
| Update only: replay | 55.0 | 4.0 | 56.7 | 39.4 | 55 | 15.9 |
| Update only: sleep-inspired (not promoted; shown for information) | 50.0 | 38.0 | 33.3 | 43.1 | 62 | 15.3 |
| Replay + bank | 83.8 | 100 | 6.7 | 74.4 | 314 | 17.7 |
| Sleep-inspired + bank | 85.0 | 100 | 6.7 | 75.0 | 315 | 17.8 |
| Core + guarded bank (exploratory) | 88.8 (91 / 11) | 100 | 0.0 (0 answered: asked 30 times) | 75.6 | 257 (machine busy) | 77.0 |
| Teacher's procedure | 100 | 100 | 100 | 100 | 193 | 10.6 |
| Search script | 100 | 100 | 20.0 | 85.0 | 579 | 47.2 |

**Table jobs** were at 98% to 100% for every arm, later rules included: the frozen core applied "void means drop" to a case it had never seen, and the other later rule needs no change at all. The bank cut scripts per job from 3.7 to 2.1 and raised verified jobs per minute from 504 to 794.

**What the bank did, whole day, 280 jobs:** it finished 219 jobs itself, 28 of them wrongly (all traps); it tried and handed on 15 with the workspace restored (1.1 wasted operations per job); it declined 46.

**Harm and gain on the retention set (160 jobs), against the frozen core:**

| Arm | Core right, arm wrong | Arm right, core wrong |
|---|---|---|
| Core + bank | 0 | 21 |
| Naive update | 11 | 0 |
| Replay update | 6 | 2 |
| Sleep-inspired update | 10 | 2 |
| Sleep-inspired + bank | 1 | 23 |

**Reading it.**

- **Useful reuse.** A procedure promoted from two verified experiences repaired all 50 jobs of mechanisms the core had never been trained on, in one script each. Weight updates alone reached 4% to 38%.
- **Wrong reuse.** On traps the bank's procedure made the visible checks pass with the wrong line 28 times in 30. The frozen core was wrong on 58% of its answers there and the search script on 80%. Visible checks cannot protect any of them.
- **Abstention and requests for evidence.** A guarded procedure that tries every promoted change before committing, and asks when more than one satisfies the checks, asked on all 30 traps and was wrong on none, and lost nothing elsewhere. It spends four times the operations (77 against 18 per job). It was written after seeing the trap result, so it is exploratory.
- **What survives without retrieval.** Little: between −1 and +4 verified jobs per 100 over the whole day (project jobs alone: −1 to +8 points), with 6 to 11 earlier jobs lost.
- **Replay against sleep at matched cost.** The sleep-inspired update transferred more (38% against 4% on later project faults) and forgot more (10 against 6 earlier jobs lost). By its own promotion check it should not be installed. I attribute no gain to Sleep.

**Break-even.** Promoting procedures and learning the gate cost under 0.1 s, so the bank pays for itself on the first job (0.31 s per job down to 0.11 s). The updates cost 41 to 192 s overnight (corpus, training, validation) and barely change seconds per job: alone they would need 2,300 to 9,200 jobs to recover the night in time, and they buy between −1 and +4 verified jobs per 100.

### 5.3 The prediction from v0.6 round 2: mix some audits away from the exception

After the holder released the labels, the locked raw output showed that every dip below the old rule after recognition sits in one level of the bank (`amend`), which over-extends an exception when every audit is sent next to it. The test (`v08/m4_audit_mix.py`): the frozen `amend` level, the same audit budget, three ways of choosing the next audits. The share of random audits was chosen on a development family by a rule written into the script (commit `6543140`) before the final family was drawn.

| Local amendments, fresh family (12 policies, 5 seeds) | Local only (frozen behaviour) | **Mixed, 20% random (chosen on development)** | Random only |
|---|---|---|---|
| Mean shortfall below the old table from 64 audits on, points | 0.449 | **0.123** | 0.015 |
| Worst single cell from 64 audits on, points | −11.8 | −4.1 | −0.7 |
| Median audits until every case is right | 618 | 618 | 1,600 |
| Median audits to 99% | 256 | 256 | 1,024 |

- Paired over the 12 policies: shortfall −0.33 points (interval −0.69 to −0.07); better on 8, equal on 3, worse on 1. On Codex's spent family: 1.07 to 0.23, with the same cost at every size.
- **The prediction holds for local amendments**: about three quarters of the interim regression goes, and the overall median learning cost is unchanged. One qualification: on the largest amendments (160 to 240 cases) of the fresh family the median cost rose one grid step, 724 to 1,024 audits.
- Scattered amendments gain nothing from mixing, and random-only is the worst choice for them.

## 6. Latent updates, the larger reference and the demo (milestone 5)

### 6.1 Direct action against shared-weight latent passes

[[LAT]]

### 6.2 A larger coding model as a reference

Qwen2.5-Coder-1.5B-Instruct (1.5 billion parameters, 3.1 GB) through the same operations, with the manual and one worked example per domain in its prompt, verified 11 of 48 development jobs in script mode (4 of 24 project jobs, 7 of 24 table jobs) at 1.3 verified jobs per minute and about 10,000 prompt tokens per job. On the same kind of jobs the one-million-parameter exec core verifies about 80% at about 180 per minute. This is a reference for the application, not a fair fight: the small core was trained on 372,802 jobs of exactly this world and the large model on none. A larger local model was not tried; the 32 GB laptop could hold a 7-billion-parameter model in 16-bit floats but not at a speed that fits this run, so that comparison is missing.

### 6.3 The demo

`python v08/demo.py --smoke` (about 10 s; transcript in `results/v08/demo_smoke.txt`). A goal goes in; the core proposes a script and writes the effect it predicts; the script runs in the sandbox; the observed effect and the changed files are shown; at the end the diff, the independent verdict, the experience written and what the bank now holds. Session 2 is the same project with the fault moved: the bank's stored procedure is tried first, execution shows it does not apply, the workspace is restored, and the core works the job itself. `python v08/demo.py` steps through any fixture job with a prompt before each execution; `--workspace DIR` takes your own job folder.

The default seed was chosen so that the core solves both project sessions. Over 40 seeds it solved session 1 in 16 and session 2 in 7; the docstring says so.

## 7. Limits

- **The holdout is author-made.** I wrote its generator. Codex's independently authored holdout is the stronger test and has not arrived.
- **A generated world.** Faults are one line from a fixed table; a job is well posed by construction; numbers stop at 63. Nothing here shows that the result carries to real repositories or real ledgers.
- **Visible checks decide too much.** Where they pin the repair down, a search script wins; where they do not, everything that trusts them is wrong. The interesting region, expensive checks that under-determine, is only touched by the trap set.
- **Timing depends on my runner.** A process per script costs about 45 ms. A runner that kept a process alive would change every jobs-per-minute figure, though not the verified shares.
- **One development look at the primary cores** (seed 1, development set) happened before the lock; nothing was changed after it.
- **Milestone 4's settings were chosen on a dry run** that used a pilot core and another draw of day 2. The real day 2 was drawn afresh. The guarded bank came after the result.
- **Family-clustered intervals rest on 8 project families**, which is why they are wide.

## 8. Deliverables

| | Where |
|---|---|
| Pinned commit | branch `v0.8` (the final commit is named in the memo) |
| Environment manifest | `results/v08/ENVIRONMENT.json` |
| Checkpoints and hashes | `artifacts/v08/*.safetensors` (+ `.json` training logs), `results/v08/LOCK_v08.json`, `results/v08/CHECKPOINTS.sha256` |
| Data provenance | `data/v08/MANIFEST.json`; job sets under `data/v08/` |
| One-command smoke demo | `python v08/demo.py --smoke` |
| Per-task outcomes and costs | `results/v08/hold/core/*.graded.jsonl`, `results/v08/m2/`, `results/v08/m4/day2/` |
| Tables | `results/v08/hold_core_tables.md`, `m2_tables.md`, `m4_tables.md`, `m4_audit_mix_*.md`, `hold_op_price.md` |
| Decision memo | `docs/v08_memo.md` |
