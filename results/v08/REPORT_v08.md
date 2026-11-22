# Stillway v0.8: execution and memory

Fable, for Prince Anozie, 22 November 2026. Branch `v0.8`. One-page memo: `docs/v08_memo.md`. Frozen protocol: `docs/v08_protocol.md`. Exploratory log: `docs/v08_exploratory_log.md`.

**The question.** Does learning from actual executions, from the first training step, help a small model choose, check and reuse scripts cheaply enough to matter?

**The short answer.** It helps the model get more jobs right, and on Codex's independent holdout it passes the rule written beforehand for jobs per minute. On this evidence it still does not make a small model the cheap way to do these jobs.

- **Graded blind by Codex on 220 jobs Codex wrote (added last, section 6.6):** the execution-aware core verified **75.0%** against **61.5%** for the baseline (three seeds each) and **1.22 times** its verified jobs per minute, interval 1.005 to 1.574. By the frozen rule that is a **WIN**, by a thin margin. The shuffled-outcome control scored 61.8%. The limited-experience regime and the prediction-only core, both named before the run, pass the same rule.
- On my own holdout the same cores gave **80.1%** against **68.5%** and 1.16 times the rate, interval 0.999 to 1.408: **inconclusive** by the same rule. The two holdouts agree on the size of the effect and fall either side of the line. With 67,494 training jobs instead of 372,802 the picture on my holdout is the same (78.9% against 71.1%; also inconclusive).
- A core trained only to predict observations, with no failure records, was the fastest core on both holdouts (1.27 and 1.34 times the baseline's rate). It answers more often and is wrong more often than the execution-aware core.
- A fixed search script of about 20 lines, with no model, verified 100% of both holdouts five times faster. The learnt core only costs less per verified job when one operation costs more than about 24 ms (32 ms on Codex's set). Both holdouts held only jobs whose visible checks pin the repair down; on unselected jobs the same script was wrong on 19% and never asked (next point).
- A bank of tested procedures, promoted from one day's verified experience and run as scripts, doubled verified project jobs the next day (36% to 74%) at no overnight cost, and on Codex's jobs raised the same core from 74.1% to 94.1%. Overnight weight updates changed the next day's verified jobs by between −1 and +4 per 100 and each lost 6 to 11 jobs the core used to get right. The bank was wrong on 28 of 30 of my jobs where the visible checks could not tell two repairs apart, unless it was made to ask; Codex's holdout had no such jobs.
- **Trap set, written and graded blind by Codex (added last, section 6.7):** in 120 unselected one-fault jobs, 46 (38%) were traps, where another one-line change passes both visible checks and is wrong. The plain bank ended 35 of the 120 with a wrong answer, the guarded bank 6, at a price of 9 fewer verified jobs (79 to 70) and 44 jobs returned as a request. By the reading fixed beforehand: **GUARDED BANK STANDS**. The search script was wrong on 23 and the core alone on 61.

## Status of every result

| Result | Status |
|---|---|
| v0.7 final run: 42 raw files, 4,032 records, returned to Codex ungraded | **Done and graded by Codex** (see the closeout row below) |
| v0.6 round 2 addendum by the holder's groups | **Frozen run, labels released** |
| M2: single operations against composed scripts, Qwen 1.5B, 48 jobs | **Measured once**, development jobs, small sample |
| M3: exec against base on the author-made holdout, three seeds | **Frozen** (protocol and nine cores locked before the run) |
| M3 on Codex's independently authored holdout, revision 2 (220 jobs; the set for final inference) | **Frozen, graded blind by Codex**: run once, sealed at `d219e97` before grading, grades received and committed as received at `f40318c`, report run once (section 6.6). Revision 1 was run and returned earlier (`a64d249`) and is not used. |
| Trap set: 137 one-fault project jobs written by Codex, 120 of them an unselected draw | **Frozen reading, graded blind by Codex**: plan and reading fixed before the set existed (`docs/v08_trap_plan.md`), run once, sealed at `1a8f2cf` before grading, grades committed as received at `6e255d6`, report run once (section 6.7). One core seed, one bank. |
| v0.7 blind closeout | **Closed**: recognition result by the frozen rules (branch `v0.7`, `docs/v07_blind_closeout.md`) |
| Operating contracts for the instruction-following runner | **Development comparison**, 72 jobs, one run; the existing wording stays |
| M3 limited-experience regime, three seeds | **Pre-specified secondary** |
| M3 arms that separate prediction from failure records | **Exploratory**: prediction-only three seeds (two added after the first looked good), failure-only one seed |
| M4 audit mixing | **Frozen selection rule**, one run on a fresh family |
| M4 bank, overnight updates, day 2 | **Measurement**, settings chosen on a dry run with a pilot core; day 2 redrawn before the real run |
| M4 guarded bank | **Exploratory** on my jobs, added after seeing the trap result there; then tested unchanged on Codex's trap set (row above) |
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

The same comparison with five and a half times less experience: the first 67,494 training jobs, read about twelve times, same 80 million token positions, three seeds, same holdout, same rule. Run after the primary result, on an idle machine, raw records committed before grading.

| Seeds pooled (960 job runs per arm) | base, limited | exec, limited | base, abundant | exec, abundant |
|---|---|---|---|---|
| Verified, all jobs | 71.1% | **78.9%** | 68.5% | 80.1% |
| Verified, project jobs | 46.3% | 60.2% | 42.0% | 62.5% |
| Verified, table jobs | 99.3% | 100% | 98.7% | 100% |
| Familiar faults / altered precondition / never-trained transition | 49.4 / 44.4 / 5.8 | 69.4 / 57.8 / 25.8 | 49.4 / 37.8 / 3.3 | 74.4 / 61.1 / 24.2 |
| Error among answers | 23.6% | 16.0% | 28.2% | 14.1% |
| Verified jobs per minute | 165.5 | 177.0 | 156.8 | 181.6 |

| exec against base, limited | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|
| All jobs | 1.070 (0.960 to 1.241) | +7.7 (+2.3 to +14.1) | 1.098 / +6.2; 1.040 / +9.7; 1.072 / +7.2 |
| proj | 1.248 (1.014 to 1.713) | +13.9 (+5.3 to +22.5) | 1.271 / +11.8; 1.231 / +16.5; 1.242 / +13.5 |
| tab | 0.997 (0.993 to 1.005) | +0.7 (0.0 to +1.7) | 1.002 / 0.0; 1.001 / +2.0; 0.989 / 0.0 |

- **Verdict by the same rule: INCONCLUSIVE.** The verified share is higher in every seed; the rate ratio is 1.07 with an interval that includes 1.
- The amount of experience made little difference to either arm. A single-seed development pilot had suggested that the baseline memorises with 67,000 jobs and would recover with more; on the holdout with three seeds its score is the same or slightly higher with less data (71.1% against 68.5%). That reading is withdrawn in the exploratory log.

### 4.5 Prediction or failure records? (exploratory, after the primary result)

The exec arm differs from base in two ways at once: it predicts observations, and it reads records with failures and recoveries. Two more kinds of core separate them, abundant regime, same budget, same holdout: **obsonly** (careful records only, predicts observations; three seeds, the second and third added after the first looked interesting) and **reconly** (failure records, no prediction; one seed).

| Holdout, three seeds pooled unless marked | base | obsonly | exec | reconly (seed 1 only) | shuf |
|---|---|---|---|---|---|
| Verified, all jobs | 68.5% | 75.5% | **80.1%** | 74.4% | 68.3% |
| Verified, project jobs | 42.0% | 56.1% | 62.5% | 51.8% | 40.8% |
| First-attempt success | 68.2% | 75.5% | 75.9% | 69.4% | 61.9% |
| Error among answers | 28.2% | 25.4% | 14.1% | 19.8% | 20.4% |
| **Verified jobs per minute** | 156.8 | **198.8** | 181.6 | 164.4 | 140.9 |
| Operations per job | 9.6 | 8.6 | 10.4 | 10.6 | 11.6 |
| Failed edits per solved job | 0.74 | 0.31 | 0.73 | 0.90 | 1.44 |

| Contrast (all jobs, three seeds) | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|
| obsonly against base | 1.268 (1.102 to 1.497) | +7.0 (+2.0 to +11.5) | 1.235 / +8.1; 1.322 / +10.0; 1.248 / +2.8 |
| obsonly against exec | 1.095 (1.017 to 1.164) | −4.6 (−8.5 to −1.6) | |

- **Prediction alone gives the rate gain.** The prediction-only core never retries (its first attempt is its only attempt), so it is the fastest core, and its first attempts are as accurate as the exec core's. Against base it would have met the frozen rule (ratio above 1.10, interval above 1.00, table jobs 1.1 points lower). It was not the frozen comparison, and its second and third seeds were added because the first looked good, so this is a lead, not a result.
- **Failure records buy accuracy and cost speed.** The exec core recovers after a failed edit and ends 4.6 points higher, at 9% fewer verified jobs per minute. Failure records without prediction (one seed) add about 5 points on project jobs with an interval that includes zero.
- If the lead holds on an independent holdout, the cheaper recipe is also the faster one: no slipped records to generate (about a quarter less teacher work).

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

The exec core of seed 1 against a core that applies the same five layers three times before each output (shared weights, the input embedding added back before each further pass), trained from the same initial weights on the same records. Development set, same runner and limits, so the direct core has the same time allowance for retries.

| Development set, seed 1 | Direct | Three latent passes, same compute |
|---|---|---|
| Parameters | 1,067,136 | 1,067,136 |
| Token-pass positions in training | 80.0 million | 80.0 million |
| Examples drawn | 668,480 | 223,424 |
| Verified, difficult jobs (proj, 170) | **58.2%** | 28.8% |
| Verified, routine jobs (tab, 150) | **98.0%** | 64.7% |
| Verified jobs per minute, all | 172.5 | 83.7 |
| Model seconds per job, proj / tab | 0.027 / 0.010 | 0.080 / 0.025 |
| Editing scripts per job, proj | 1.76 | 2.52 |

- At matched compute the latent core is far worse on both kinds of job (−31 points overall, interval −45 to −21) and three times slower per call. It saw a third of the examples.
- **Not run:** the same core given the same examples, which costs three times the compute (about 60 minutes of this laptop's GPU on its own). Without it I cannot say whether latent passes help per example; I can say they do not pay for themselves per unit of compute here.

### 6.2 A larger coding model as a reference

Qwen2.5-Coder-1.5B-Instruct (1.5 billion parameters, 3.1 GB) through the same operations, with the manual and one worked example per domain in its prompt, verified 11 of 48 development jobs in script mode (4 of 24 project jobs, 7 of 24 table jobs) at 1.3 verified jobs per minute and about 10,000 prompt tokens per job. On the same kind of jobs the one-million-parameter exec core verifies about 80% at about 180 per minute. This is a reference for the application, not a fair fight: the small core was trained on 372,802 jobs of exactly this world and the large model on none. A larger local model was not tried; the 32 GB laptop could hold a 7-billion-parameter model in 16-bit floats but not at a speed that fits this run, so that comparison is missing.

### 6.3 The demo

`python v08/demo.py --smoke` (about 10 s; transcript in `results/v08/demo_smoke.txt`). A goal goes in; the core proposes a script and writes the effect it predicts; the script runs in the sandbox; the observed effect and the changed files are shown; at the end the diff, the independent verdict, the experience written and what the bank now holds. Session 2 is the same project with the fault moved: the bank's stored procedure is tried first, execution shows it does not apply, the workspace is restored, and the core works the job itself. `python v08/demo.py` steps through any fixture job with a prompt before each execution; `--workspace DIR` takes your own job folder.

The default seed was chosen so that the core solves both project sessions. Over 40 seeds it solved session 1 in 16 and session 2 in 7; the docstring says so.

### 6.4 Codex's independent holdout: run and returned (added later the same day)

Codex's 220 jobs arrived after this report was first written. The public file's digest matched its commitment. A plan naming every arm and the scoring was committed before anything ran (`docs/v08_codex_holdout_plan.md`); 19 checkpoints, the bank, the code and the public file were locked; each arm and seed ran once on an idle machine; 22 raw files (4,840 records) were sealed with hashes, lock check and failure log at commit `a64d249` and returned (`results/v08/codex_hold/RETURN.md`). I do not hold the hidden half. No sandbox crash or timeout; 316 of 4,840 job runs ended at a limit. **Nothing in this report uses those records.** Codex then replaced the set: revision 2 (220 new jobs, none shared with revision 1) is the one for final inference. The same 22 runs were made on it once under a second lock that agrees with the first on every checkpoint, the bank and the code, and the records were sealed and returned at commit `d219e97` (`results/v08/codex_hold_rev2/RETURN.md`). Its grades have returned: section 6.6.

### 6.5 Operating contracts for the instruction-following runner (development jobs only)

Prince and Codex asked for the runner's instructions to be drafted and tested. Four wordings were compared on 72 development jobs with the pinned Qwen model in script mode: the milestone-2 prompt as it was, a one-sentence instruction, Codex's contract and mine. Verified jobs: 16, 11, 15, 12. By the rule fixed beforehand the existing wording stays. The guided arms cannot be told apart at this sample size; the bare instruction said DONE wrongly most often (31 against 19 to 23); only the existing prompt produced correct ASKs (4 of 11). The small core cannot read a prompt at all: for it, a contract has to be built into its training records, and `docs/v08_operating_contracts.md` sets out clause by clause what is already there and what is not.

### 6.6 Codex's independent holdout, revision 2: graded (added when the grades returned)

**What came back.** `Stillway_v08_rev2_blind_grades.zip` (SHA-256 `e5aeef76…5b55ee0e73`): 22 graded files, a hash list and Codex's own tables. Every graded record equals my sealed record field for field, with the grade and Codex's labels added (4,840 of 4,840). I committed the grades as received (`f40318c`) before computing anything, then ran `v08/report.py` once per folder as the plan of `docs/v08_codex_holdout_plan.md` says. My tables and Codex's agree to every digit. The lock still matches. I have never held the hidden half.

Codex graded on Linux, with the project tests run in a temporary directory in place of the macOS sandbox; timings are the ones in my sealed records.

**The primary cores** (220 jobs, three seeds each; `results/v08/codex_hold_rev2_core_tables.md`):

| | Verified % | project / table | Answered % | Error among answers % | Verified jobs per minute | Operations per job |
|---|---|---|---|---|---|---|
| base | 61.5 | 35.0 / 92.7 | 78.6 | 34.9 | 137.5 | 9.9 |
| **exec** | **75.0** | **53.8 / 100.0** | 75.8 | **15.4** | **167.4** | 10.5 |
| shuf (control) | 61.8 | 29.4 / 100.0 | 72.0 | 24.6 | 123.4 | 12.0 |
| search script, no model | 100.0 | 100.0 / 100.0 | 89.1 | 0.0 | 905.4 | 28.1 |

**The frozen rule, exec against base, every job:**

| | Rate ratio (95% interval over task families) | Verified share, points | Each seed: ratio / points |
|---|---|---|---|
| All jobs | **1.217 (1.005 to 1.574)** | **+13.5 (+5.9 to +22.4)** | 1.161 / +10.9; 1.346 / +16.4; 1.154 / +13.2 |
| Project | 1.520 (1.045 to 2.490) | +18.8 (+7.5 to +30.1) | |
| Table | 1.118 (0.991 to 1.346) | +7.3 (+0.0 to +16.3) | |

**Verdict: WIN.** The ratio is at least 1.10, its interval is above 1.00, and neither domain is lower.

How much weight it bears:

- **The margin is thin.** The lower end of the interval is 1.005. On my own holdout it was 0.999 and the verdict was inconclusive. These are the same effect measured twice (1.16 and 1.22 times the rate; +11.6 and +13.5 points), not a weak result followed by a strong one.
- **The verified share is the solid part.** Every seed, both holdouts, intervals clear of zero.
- **The interval rests on 21 task families** (10 project, 13 table, two shared names).
- **The control behaves as on my holdout.** shuf against base: rate 0.897 (0.759 to 1.048), +0.3 points. exec against shuf: 1.357 (1.094 to 1.738), +13.2 points (+4.2 to +22.7).

**The other comparisons named before the run** (same rule, same set):

| Comparison | Verified % | Rate ratio | Verified share, points | Verdict by the rule |
|---|---|---|---|---|
| Limited experience (67,494 training jobs): exec against base | 74.2 against 62.6 | 1.176 (1.030 to 1.404) | +11.7 (+5.6 to +18.5) | **WIN** |
| Prediction only against base (the exploratory lead, named as the second question) | 70.5 against 61.5 | 1.343 (1.097 to 1.739) | +8.9 (+1.8 to +17.6); table +1.3 (−2.6 to +7.2) | **WIN** |
| Primary without the 20 `later` jobs (second, labelled figure; 600 job runs per arm) | 77.5 against 63.8 | 1.230 (1.016 to 1.603) | +13.7 (+5.8 to +22.9) | WIN |
| Limited experience without `later` | 76.7 against 65.7 | 1.146 (1.024 to 1.316) | +11.0 (+5.3 to +17.5) | WIN |
| Prediction only without `later` | 72.5 against 63.8 | 1.328 (1.071 to 1.737) | +8.7 (+1.4 to +17.8) | WIN |

Tables: `results/v08/codex_hold_rev2_{lim,obs3,expl,mem}_tables.md` and the `_nolater` versions.

**Prediction only against execution-aware** (not a pre-named rule; descriptive): 70.5% against 75.0% verified, −4.5 points (−9.3 to −0.7); rate 1.103 times (1.016 to 1.186). It uses fewer operations (8.7 against 10.5 per job) and answers more often (85.6% against 75.8%), and nearly twice as many of its answers are wrong (29.7% against 15.4%). The same trade appeared on my holdout.

**Where the gain comes from, by domain** (seed 1 arms beside the three-seed ones; descriptive):

| Arm | Trained with true outcomes to predict | Trained on failure records | Project, points against base | Table, points against base |
|---|---|---|---|---|
| exec | yes | yes | +18.8 | +7.3 |
| prediction only | yes | no | +15.4 | +1.3 |
| failure records only (seed 1) | no | yes | +0.8 | +6.9 |
| shuf | shuffled | yes | −5.6 | +7.3 |

On Codex's set the project gain follows prediction of true outcomes, and the table gain follows the failure records, with or without true outcomes. On my holdout table jobs were at 99% to 100% for every arm, so the second half could not be seen there.

**By group, project jobs** (verified %): familiar 32.5 base, 60.8 exec; altered precondition 23.3, 46.7; transitions never trained 5.3, 25.3; mechanisms never trained (`later`) 0, 0; unanswerable 88.9, 100. Project jobs were harder for every core on Codex's set than on mine (exec 53.8% against 62.5%).

**The memory arms, measured once** (exec seed 1; `results/v08/codex_hold_rev2_extra.md`):

| | Verified of 220 | Wrong | Asked on an answerable job | Operations per job | Verified jobs per minute |
|---|---|---|---|---|---|
| exec seed 1 alone | 163 (74.1%) | 40 | 12 | 10.6 | 166.2 |
| + bank | 207 (94.1%) | 6 | 6 | 14.5 | 460.2 |
| + guarded bank | 214 (97.3%) | 1 | 4 | 43.1 | 496.7 |

- The bank was promoted from my day 1, before Codex's jobs existed. It repaired all 10 project jobs with mechanisms no core was trained on, where every core scored 0.
- **No wrong reuse was seen here, and none could have been.** All 6 wrong jobs with the plain bank are jobs the bank handed on and the core then got wrong. Codex's set has no jobs where two repairs pass the visible checks, so the trap result of section 5.2 was neither confirmed nor contradicted.
- The guarded bank's extra 7 jobs come from trying every promoted change, which is a wider search, at three times the operations.

**Against the search script.** It verified 220 of 220 at 905 jobs per minute. On project jobs the execution-aware core costs less per verified job only above 32 ms per operation, the prediction-only core above 22 ms, the core with the plain bank above 4 ms, and the guarded bank never.

**What changes in the conclusions.**

- The claim for execution-aware training moves from "more jobs right" to "more jobs right and, by the frozen rule on an independent set, more per minute", with the thin margin stated beside it.
- Prediction only is no longer an exploratory lead: it passed as a named question on jobs it had no part in choosing.
- The bank result holds on independently written jobs. Its known weakness was not tested there.
- Nothing changes about the search script: in this world it is still the cheap way.

### 6.7 Codex's trap set: jobs whose visible checks may not pin the repair down (added after the grades came back)

Both holdouts refused any job where a second one-line change passed the visible checks, so wrong reuse could not show there. Codex wrote a third set to the brief `docs/v08_trap_brief.md`: 120 consecutive one-fault project jobs kept without that filter (131 further draws had no failing visible check and were not jobs), plus 17 added jobs of the rare "equal" class. The classes were assigned by execution in `v08/pack_traps.py`. The plan, the four arms and the reading were fixed before the set existed (`docs/v08_trap_plan.md`); the set was run once, sealed and graded by Codex. My tables equal Codex's in every cell.

| Class | In the draw of 120 | Meaning |
|---|---|---|
| Ordinary | 71 (59%) | the repair is the only one-line change that passes both visible checks |
| Trap | 46 (38%) | another one-line change passes both and behaves differently on other inputs |
| Equal | 3 (2.5%), 20 with the top-ups | other changes pass and behave like the repair on every input tried |

**The unselected draw, 120 jobs** (execution-aware core seed 1 in every arm that has a core; `results/v08/codex_trap_tables.md`, `codex_trap_extra.md`):

| Arm | Verified | Wrong DONE | Asked, nothing changed | Wrong among its DONE endings | Operations per job | Verified jobs per minute |
|---|---|---|---|---|---|---|
| Core alone | 43 (36%) | 61 (51%) | 15 | 59% | 16.0 | 48 |
| Core with the plain bank | 79 (66%) | 35 (29%) | 6 | 31% | 22.4 | 203 |
| Core with the guarded bank | 70 (58%) | 6 (5%) | 44 (37%) | 8% | 81.8 | 257 |
| Search script, no model | 97 (81%) | 23 (19%) | 0 | 19% | 43.5 | 564 |

The core alone also ran out of limits once.

**By class, all 137 jobs** (verified / wrong DONE / asked):

| Arm | Trap (46) | Ordinary (71) | Equal (20) |
|---|---|---|---|
| Core alone | 7 / 29 / 10 | 36 / 30 / 4 | 1 / 17 / 2 |
| Plain bank | 16 / 25 / 5 | 61 / 9 / 1 | 10 / 9 / 1 |
| Guarded bank | 2 / 3 / 41 | 68 / 3 / 0 | 0 / 3 / 17 |
| Search script | 23 / 23 / 0 | 71 / 0 / 0 | 20 / 0 / 0 |

**The reading fixed beforehand.**

| Step | Measured | Result | Threshold |
|---|---|---|---|
| A | Traps the plain bank itself ended with a wrong DONE | 16 of 46, 34.8% (23 to 49) | 10% or less would make the guard unnecessary |
| B | Traps the guarded bank itself ended with a wrong DONE | 0 of 46 (0 to 8) | more than 10% would fail it |
| B | Ordinary jobs the guarded bank itself ended by asking | 0 of 71 (0 to 5) | more than 50% would fail it |
| C | On the draw, whole arm, guarded against plain | 29 wrong DONEs prevented (35 to 6) for 9 verified jobs forgone (79 to 70): break-even 0.31 | above 3, or nothing prevented, would make it too costly |

**Verdict: GUARDED BANK STANDS.** The guard pays whenever one wrong answer costs more than a third of a lost completion.

**The four predictions written before the set existed all held:** traps 38% of the draw (predicted 25% to 50%); plain bank itself wrong on 34.8% of traps (20% to 45%); this verdict with a break-even below 1 (0.31); search script wrong on 50% of traps (a third to a half, at the upper edge). My own dry run of 400 jobs had given 36%, 28.7%, 0.51 and 44%.

**What the breakdowns add** (descriptive; `results/v08/codex_trap_extra.md`):

- **The guarded procedure itself never ended a job wrongly** (0 of 125 jobs it ended). All 9 wrong answers in that arm came from the 12 jobs the bank declined and the core then finished.
- **When the plain bank committed on a trap it was wrong more often than right**: 16 wrong, 13 right. Its 13 were right because the gate's first choice happened to be the repair.
- **The guard's cost is on jobs where the plain bank was right without knowing why.** On ordinary jobs the guard gained 7 (61 to 68) because it tries every stored change. It gave up 14 verified traps and all 10 verified equal jobs.
- **Unnecessary requests.** The guarded procedure asked on 16 of the 20 equal jobs, where any passing change was right. In an unselected draw these are 1 job in 40.
- **Audit asked for by Codex:** 81 endings by asking across the arms; none changed a file. Codex's own audit says the same.
- **The search script is not safe on unselected jobs.** It finished every job and was wrong on half the traps, 19% of the draw. The statement "100% at five times the speed" holds only where the visible checks pin the repair down.
- **The core alone was wrong on 59% of its answers** in the draw. On the ordinary jobs it verified 51%, close to its 54% on the project jobs of Codex's holdout.
- **By fault slot,** half the traps (27 of 46) are threshold and comparison faults, where a neighbouring threshold or comparison fits two small visible inputs equally well.

**What the guard is, said plainly.** The stored entries cover every one-line change of all eight settings, so the guarded procedure is an exhaustive search over one-line changes that refuses to commit when more than one passes. By the definition of the classes, the search script given the same rule would finish the 71 ordinary jobs, ask on the other 49 and be wrong on none; that is a deduction, not a run. What this set establishes is the rule (count the changes that pass before committing), at 82 operations per job against 22 for the plain bank. The bank's ordering is what made reuse cheap, and the cheap form is the unsafe one.

**A further step, tried in simulation only** (exploratory, author-made, after the grades; `v08/trap_question_sim.py`, `results/v08/trap_question_sim.md`, exploratory log E15). A bare request leaves 37% of the draw unfinished. A guard that makes up a small input on which the remaining candidates disagree, and asks the owner which report is right for it, was simulated on 400 fresh jobs from my own generator (249 ordinary, 13 equal, 138 trap), on the reference semantics, not through the runner:

| | The guard as built | The questioning guard (commits after 30 made-up inputs fail to separate what is left) |
|---|---|---|
| Finished right | 249 (62%) | 400 (100%) |
| Finished wrong | 0 | 0 |
| Left as a bare request | 151 | 0 |
| Jobs with a question | n/a | 138 (34%): the trap jobs and no others |
| Questions per job asked | n/a | 1.17 on average, 3 at most; 2.2 choices per question |
| Questions on equal jobs | asks on all 13 | 0 |
| Project executions per job | 44 | 50 |

It rests on two things this version does not have: an operation that runs the project on an input the solver made up, and an owner who can say what the report should be for 3 to 5 made-up rows. With 3 made-up inputs instead of 30 it finished 11 jobs wrongly.

**Disclosures.**

- I do not hold the hidden half. Classes and outcomes are Codex's grading with the frozen grader; Codex reports substituting an isolated Linux Python for the macOS launcher when executing the generated modules.
- Codex saw the aggregate table of my dry run, which is printed in the plan, and reports that the bank file, the per-job dry-run files and log entry E14 were not opened.
- The machine was not idle during the run (macOS indexing and iCloud sync). Counts are unaffected; seconds per job may be slightly high for every arm.
- Step C and its threshold of 3 were written after my own dry run and before Codex's set existed.
- One core seed and one bank.

**What changes in the conclusions.**

- The guard is no longer exploratory: it was tested unchanged on independent jobs against a reading fixed beforehand, and stands.
- "The search script is the cheap way" now carries a condition: where checks pin the repair down. On unselected jobs it is the fastest and finishes the most, and one answer in five is wrong.
- Nearly two in five unselected faulty jobs in this world cannot be decided from the visible checks by any solver. The right ending there is a request, and the useful request is a concrete one.

## 7. Limits

- **Two holdouts, one generator design.** I wrote the generator of the first. Codex wrote the jobs of the second independently, to the brief I supplied, so both live in the same world of one-line faults.
- **The win on Codex's set is by a hair** (lower end of the interval 1.005, 21 families). A third set could land either side.
- **A generated world.** Faults are one line from a fixed table; a job is well posed by construction; numbers stop at 63. Nothing here shows that the result carries to real repositories or real ledgers.
- **Both holdouts hold only jobs whose checks pin the repair down.** Codex's unselected draw (section 6.7) shows what that leaves out: 38% of faulty jobs there were traps, and the search script was wrong on half of them.
- **The trap set is one core seed, one bank, 120 unselected jobs,** in the same one-line-fault world. "Equal" means equal on 3,000 random inputs inside the world's limits. What a request costs the owner was not measured; the report gives the break-even (0.31) so another price can be applied.
- **Visible checks decide too much.** Where they pin the repair down, a search script wins; where they do not, everything that trusts them is wrong. The interesting region, expensive checks that under-determine, is only touched by the trap set.
- **Timing depends on my runner.** A process per script costs about 45 ms. A runner that kept a process alive would change every jobs-per-minute figure, though not the verified shares.
- **One development look at the primary cores** (seed 1, development set) happened before the lock; nothing was changed after it.
- **Milestone 4's settings were chosen on a dry run** that used a pilot core and another draw of day 2. The real day 2 was drawn afresh. The guarded bank came after the result.
- **Family-clustered intervals rest on 8 project families**, which is why they are wide.
- **The lock** matched when the holdout records were sealed (commit `13f200e`). Three locked files were changed afterwards (`stillway8/agent.py`, `stillway8/bank.py`, `v08/run_core.py`) to add the guarded bank and a job-list option; the loop the core runs in is otherwise the same, and the secondary holdout runs used it.

## 8. Deliverables

| | Where |
|---|---|
| Pinned commit | tag `v0.8-report` on branch `v0.8` |
| Environment manifest | `results/v08/ENVIRONMENT.json` |
| Checkpoints and hashes | `artifacts/v08/*.safetensors` (+ `.json` training logs), `results/v08/LOCK_v08.json`, `results/v08/CHECKPOINTS.sha256` |
| Data provenance | `data/v08/MANIFEST.json`; job sets under `data/v08/` |
| One-command smoke demo | `python v08/demo.py --smoke` |
| Per-task outcomes and costs | `results/v08/hold/core/*.graded.jsonl`, `results/v08/m2/`, `results/v08/m4/day2/` |
| Codex's trap set, graded | `results/v08/codex_trap/` (sealed records, Codex's graded files, tables and audit note), `results/v08/codex_trap_tables.md`, `codex_trap_extra.md`; plan `docs/v08_trap_plan.md`; simulation `results/v08/trap_question_sim.md` |
| Codex's holdout, graded | `results/v08/codex_hold_rev2/` (sealed records, Codex's graded files and tables), `results/v08/codex_hold_rev2_*_tables.md`, `codex_hold_rev2_extra.md` |
| Tables | `results/v08/hold_core_tables.md`, `m2_tables.md`, `m4_tables.md`, `m4_audit_mix_*.md`, `hold_op_price.md` |
| Decision memo | `docs/v08_memo.md` |
