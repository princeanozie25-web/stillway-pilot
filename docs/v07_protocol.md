# v0.7 protocol, frozen on development data before the final set is opened

Fable, 22 November 2026. For Prince Anozie, Astra and Codex. This file, the adapters, the bank and the code are fixed by hash in `results/v07/LOCK_v07.json`. I have not seen any final repository. Nothing here may change once the final set is opened; anything that does is listed in the report as a change after the freeze.

## 1. Question

Does experience from previous bugs increase the share of unfamiliar repositories fixed on the first submitted patch, under the same inference budget?

"Unfamiliar" means every final repository that is not a renamed repeat of a training design: changed preconditions, lookalikes and absent mechanisms together. Renamed repeats are reported separately and never counted towards the answer.

## 2. What is fixed

| Thing | Fixed as |
|---|---|
| Student | `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revision `2e1fd397`, weights SHA-256 `c1b9b30e…bc13a8`, Apache-2.0, 32-bit floats, no quantisation, Apple M1 Max GPU |
| Adapters | 9 low-rank adapters (3 training sets, 3 seeds), rank 16, 18.5 million weights each, 300 updates of at most 2,048 tokens. Hashes in the lock. |
| Bank | `artifacts/v07/bank.json`, 3 diagnostics, both versions of each kept |
| Episode | Two test scripts, each with a prediction written before it runs; then one patch (one function replaced by name). 160 new tokens per test, 320 for the patch, 3,072 prompt tokens, 400 for an insert. Greedy decoding. Identical for every arm. |
| Tools | Each test runs in a fresh copy of the savepoint: 5 seconds, 400 characters of output, no network, no writes outside its folder |
| Grading | `v07/grade.py`: the first patch applied to a fresh savepoint; correct only if every hidden test and every visible test passes. A patch that cannot be parsed or applied is a failure. |

Arms, all run on every final repository:

| Arm | Student | Insert at test time |
|---|---|---|
| A unchanged | no adapter (1 run; decoding is deterministic) | none |
| B final patches | trained on the reference fixes only | none |
| C experience | trained on the teacher's executed traces (tests, predictions, observed output, contradicted attempts, fix) | none |
| D experience + bank | trained on the same traces with mixed inserts | the diagnostic for the nearest training repository, current version, reopened when a prediction is contradicted |
| D1 | same adapter as D | version 1 of the diagnostic (prior procedure and scope only) |
| E nearest example | same adapter as D | the nearest past training example (ordinary retrieval) |
| F bank disabled | same adapter as D | none |
| W wrong diagnostic | same adapter as D | a deliberately wrong diagnostic |
| AD unchanged + bank | no adapter | the same diagnostic as D (added 22 November, before the lock) |
| AE unchanged + nearest example | no adapter | the same example as E (added 22 November, before the lock) |

B, C and the D-family adapter each have seeds 1, 2 and 3. All arms and all seeds are run once and reported.

## 3. Unit of analysis and uncertainty

- The unit is the repository. A trained arm's score on a repository is its mean first-patch success over the three seeds.
- Differences are paired per repository. Two 95% intervals are reported: resampling repositories (used by the rules), and resampling whole families of repositories (reported beside it; wider, and the honest one when a group has few families).
- Group names are read from the holder's `meta.json`. Any repository that fails the packer's checks is dropped by the holder before I see the set, and the count is reported.

## 4. The smallest meaningful improvement: +10 percentage points

Chosen on development data, for these reasons:

- The unchanged student fixes 25% of the 48 development repositories that are not repeats. Ten points is two more repositories in every twenty.
- One student's three seeds range from 13 to 19 of 48 on those repositories (12.5 points). A smaller difference cannot be told from the choice of seed.
- With 48 repositories the 95% interval of a paired difference is about 17 points either side. With 60 to 80 final repositories outside the repeat group it will be about 13 to 15, so the rule also asks for the interval to exclude zero.

For comparisons between two trained students that share most of their behaviour (the bank against no bank), the threshold is +5 points with more repositories better than worse. That is the threshold written in `docs/v07_dev_plan.md` before any trained arm was evaluated.

## 5. Frozen rules

Computed by `python v07/report.py GRADED_DIR PREFIX`, which prints them and writes them to `PREFIX_summary.json`.

| Rule | Statement |
|---|---|
| **P1** (primary) | D minus A is at least +10 points on unfamiliar repositories, and the 95% interval (resampling repositories) lies above zero |
| **P2** | The share of unfamiliar repositories where D's patch breaks a hidden test that passed before is at most 10 points above A's |
| **R1** | D minus A is at least +10 points on renamed repeats, interval above zero |
| S1 | C minus B at least +5 points on unfamiliar repositories, interval above zero (verified experience against final patches) |
| S2 | D minus F at least +5 points on unfamiliar repositories, better on more repositories than worse (the bank against the same student without it) |
| S3 | D minus E at least +5 points, better on more than worse (the bank against ordinary retrieval) |
| S4 | D minus W at least +5 points, better on more than worse (the right diagnostic against a wrong one) |
| S5 | The share of lookalikes where D's patch breaks a hidden test is at most 10 points above A's |

**Verdict**

| Outcome | Condition | What it earns (from the brief) |
|---|---|---|
| Passing run | P1 passes. If P2 fails it is reported as "pass with an excess of regressions". | A matched-tools comparison with a larger model |
| Recognition result | P1 fails and R1 passes | A recognition result |
| Null | P1 and R1 both fail | A closeout with witnesses |

S1 to S5 do not change the verdict. They say which part of the system the result belongs to.

## 6. What the development data showed (72 repositories, 3 seeds)

Full tables: `results/v07/dev_tables.md`, `results/v07/dev_extra.md`.

| First patch correct | All 72 | Unfamiliar (48) | Renamed repeats (24) | Changed preconditions (16) | Lookalikes (16) | Absent mechanisms (16) |
|---|---|---|---|---|---|---|
| A unchanged | 19.4% | 25.0% | 8.3% | 25.0% | 25.0% | 25.0% |
| B final patches | 46.8% | 20.1% | 100.0% | 50.0% | 8.3% | 2.1% |
| C experience | 48.6% | 25.0% | 95.8% | 62.5% | 6.2% | 6.2% |
| AD unchanged + bank | 19.4% | 22.9% | 12.5% | 25.0% | 18.8% | 25.0% |
| AE unchanged + nearest example | 8.3% | 4.2% | 16.7% | 0.0% | 6.2% | 6.2% |
| D experience + bank | 50.9% | 31.2% | 90.3% | 72.9% | 6.2% | 14.6% |
| F bank disabled | 48.6% | 27.1% | 91.7% | 60.4% | 8.3% | 12.5% |
| E nearest example | 48.6% | 27.1% | 91.7% | 60.4% | 6.2% | 14.6% |
| W wrong diagnostic | 48.6% | 27.8% | 90.3% | 62.5% | 6.2% | 14.6% |

Exact repeats, inspected separately (the 120 training repositories themselves, seed 1, `results/v07/exact_tables.md`): A 12.5%, B 100%, C 93.3%, F 90.0%, D 86.7%.

Rules on development data: P1 fails (+6.2 points, interval -10.4 to +22.9). R1 passes (+81.9). P2 fails (34.7% against 2.1%). S1 to S5 all fail. Development verdict: **recognition result**.

## 7. What I expect on the final set

Written so it can be held against me.

- P1 fails. R1 passes by a wide margin.
- Changed preconditions: the trained students gain 25 to 50 points over the unchanged one.
- Lookalikes and absent mechanisms: every trained student is below the unchanged one, and on lookalikes more than half of D's patches break a hidden test.
- S2 and S4 fail: the bank adds less than 5 points, and a wrong diagnostic costs less than 5.

## 8. Decisions already taken on development data

1. **Sleep promotion is not tested.** The condition set in advance was D minus F of at least +5 points on unfamiliar repositories. Measured: +4.2 (interval -2.1 to +10.4; better on 10, worse on 5), and it comes from one seed of three (-1, +1, +6 repositories). There is no transferred procedure to promote.
2. **A contradiction gate was considered and rejected** (hand the patch to the unchanged student when a prediction is contradicted): 75% of the bank arm's episodes contain a contradiction and 39.5% of those are still fixed, twice the unchanged student's rate.
3. **A familiarity gate was built and does nothing** (`v07/gate.py`, `results/v07/dev_gate.md`): the trained student answers only when the repository resembles a training repository, with the threshold set from training data alone. 71 of 72 development repositories pass the gate, absent mechanisms included. It is not an arm on the final set.
4. The prompt was changed twice on 12 training repositories before any development repository was run (`docs/v07_dev_plan.md`).

## 9. Known mismatches between arms

- **Training tokens.** Every adapter had 300 updates with a budget of 2,048 tokens. The D-family training examples are longer, so fewer fit: about 383,000 tokens for that adapter against about 475,000 for B and C (19% fewer). Updates and budget match; tokens used do not.
- **Teacher cost** is outside every arm's budget and is reported separately (`results/v07/COSTS.json`): the teacher (Fable, a far larger model) wrote all designs, tests, fixes and the diagnostics' wording.
- **Prompt length.** Arms with an insert read up to 400 more prompt tokens. New tokens and tool calls are the same.
- A has one run; the others have three seeds.

## 10. How the final run goes

1. I send the lock. Codex publishes group counts and confirms the unit of analysis.
2. Codex packs the set (`python v07/pack_final.py SOURCE OUT`) and sends `OUT/public` only.
3. I check the lock (`python v07/check_lock.py`), then run every arm and seed once (`v07/run_arm.py`), hash the raw records and commit them before grading.
4. Codex grades (`python v07/grade.py PUBLIC HIDDEN RECORDS`) and runs `python v07/report.py RECORDS/graded PREFIX`. The grader is the only script that reads hidden files.
5. Or, in one command on a machine that holds both halves: `./v07/replay.sh PUBLIC HIDDEN OUT`.
