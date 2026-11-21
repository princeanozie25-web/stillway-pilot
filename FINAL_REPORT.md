# Stillway pilot: combined final report, v0.1 to v0.6

For Codex, for independent replay. From Fable (the assistant that built it), for Prince Anozie, Stillway Labs. 21 November 2026.

**Part 1 (sections 1 to 10 and the appendices) covers v0.1 to v0.3 and is unchanged. Part 2, at the end, covers v0.4 to v0.6.**

This file stands alone. It covers three versions built in one session on one machine: what was claimed, what was later corrected, what stands now, and how to check each claim without trusting the author. The detailed reports are `REPORT.md` (v0.1), `results/v02/REPORT_v02.md` and `results/v03/REPORT_v03.md`.

## 1. What you are asked to do

1. Replay the cheap checks in section 7 and compare with the expected outputs printed there.
2. Rebuild the scorers and the certificate check from the rules in the appendices and the three challenge files, without importing mine.
3. Attack the claims in section 5 that are marked **stands**. Section 8 lists where I think they are weakest.
4. Report every disagreement, however small. Two of my own v0.1 claims were wrong and were found this way.

## 2. Summary

**The question.** Can a trained planner be paused, corrected and resumed, and can what it saves between steps be inspected, edited and certified?

**The answer after three versions.**

| Version | What it tested | Outcome |
|---|---|---|
| v0.1 | A planner with four integers of saved memory in a two-leg world (Dispatch-2). Does swapping part of the memory move one obligation and leave the other alone? | Passed its frozen rule on five seeds on sealed families. Its exhaustive certificate was later found to cover 20 of 36 input patterns. |
| v0.2 | Astra's coverage gap; a new world with 2 to 4 legs and two gates (Dispatch-3); an editor that rewrites saved memory. | The gap was real and three v0.1 claims were corrected. The editor equals an ordinary message and failed its transfer bar (73.3% against 90%). Saved states could not be listed. Recommendation: change the memory architecture. |
| v0.3 | That change: typed registers, a reader that carries one discrete code from leg to leg, and a certificate for every job length. | The transfer failure is fixed (96.0% on the same items, 100% on four-leg jobs). Four of five repaired planners are proven correct for every job length. An edit is still a message. The learned planner still only ties the exact one. |

**What has never been shown, in any version:** that a learned planner beats a hand-written one. Every test is in a world where the exact planner can be written by hand.

## 3. Repository, environment, custody

Repository: `https://github.com/princeanozie25-web/stillway-pilot` (public).

| Ref | Commit | Content |
|---|---|---|
| `main` | `6588d9ff44731c0daf8120d5cc12ba1c2c45282a` | v0.1 |
| `v0.2`, tag `v0.2-local` | `9807263d70ecb526e9ad756b40b9ec058e2cbfd3` | v0.2 on top of v0.1 |
| tag `v0.3-local` | `337e9df0bf51986e001d497726f7e6c3fa699590` | v0.3 on top of v0.2 |
| `v0.3` (head) | one commit after the tag | adds this file and `v03/check_all_freezes.sh`, and corrects one sentence on margins in two v0.3 documents (section 9) |

Each version only adds files. v0.1 and v0.2 files are untouched on later branches; the three freeze checks in section 7 verify that.

| Freeze | File | Commit that added it | Final seed derived from it |
|---|---|---|---|
| v0.1 | `FREEZE.json` | in `6588d9f` (frozen 03:55, before the sealed fixtures were opened) | sealed split by SHA-256 of family names |
| v0.2 | `results/v02/FREEZE_v02.json` | `14700485083f6759f166a56ccff019b247999956` | 1670983329 |
| v0.3 | `results/v03/FREEZE_v03.json` | `de80fd794802d422353707c0fa8ff49950e1a7cf` | 850390379 |

For v0.2 and v0.3 the final seed is the first 8 hex digits of SHA-256 of `stillway-v0.X-final|<freeze commit hash>`, so no final job could be generated before the freeze commit existed.

Environment for every number: Apple M1 Max, 32 GB, 10 cores, macOS 27.0, CPU only, one thread per job, several jobs in parallel. Python 3.12.14, torch 2.14.1, numpy 2.5.4. No paid compute. Nothing is downloaded at run time.

Hash manifests: `results/v02/MANIFEST_v02.json` (173 files), `results/v03/MANIFEST_v03.json` (354 files), `results/v03/ADDENDUM.json` (checkpoints that finished after the v0.3 freeze commit).

## 4. The three versions

### 4.1 v0.1: Dispatch-2 and the swap test

- **World.** Two legs, each with routes L and R; each route keeps, toggles, opens or closes one gate. A work order (dock, gate state, bay) is shown once and then lives only in saved memory. 256 layouts in 100 families, split 60 train, 15 dev, 25 sealed by hashing family names. Rules: `docs/evaluator_spec.md`; code: `stillway/world.py`.
- **Planner.** 128-wide recurrent core, 194,313 parameters. Between steps it passes four integers (4 slots of 32 codes) and nothing else.
- **Evaluator.** Pair credit, a paired memory-swap replay with shuffled-donor control, four impostor planners scored before any model existed, eligibility rules that no wiring-blind planner can pass.
- **Frozen rule and result** (discrete memory with interchange training, 5 seeds, sealed families):

| Requirement | Threshold | Result |
|---|---|---|
| Ordinary accuracy on held-out families | at least 90% | 99.6% (97.8 to 100.0) |
| Targeted swap minus shuffled swap | at least +10 points | +48.9 (99.3% against 50.4%) |
| Drop in the unrelated obligation | at most 5 points | 0.0 on every seed |

- **Other findings on sealed families.** Plain imitation reaches the same accuracy and fails the swap (37.2%). Continuous memory with interchange training passes too (98.1%), so discreteness is not what buys the swap. A planner trained in a world that never changes holds the route, not the goal (42.2% on mid-plan reversal against 99.1%).
- **The exhaustive check.** Every reachable code state of a family against every observation in a fixed list, compared with the exact planner. This is the part that was later found incomplete (section 4.2).

### 4.2 v0.2: the coverage gap, a new world, an editor

**M0, custody.** A fresh clone of `6588d9f` in a fresh environment reproduces the freeze, the fixtures and all 20,000 swap decisions item by item. Ordinary accuracy 2,489 of 2,500. All five primary seeds retrain to bit-identical weights.

**M1, the gap Astra found.** The v0.1 extractor listed 20 operator-message patterns; the schema permits 36 (two fields revised at one stage were missing).

| Seed | Simulator only: failures in 393,216 two-field episodes | Wrong pairs, all 36 patterns, plain memory | Same 2,000,000 jobs, jobs with a wrong decision: plain / original quotient maps / rebuilt maps |
|---|---|---|---|
| 1 | 1,890 | 1.547% | 6,786 / 6,794 / 8,434 |
| 2 | 1,744 | 1.817% | 8,040 / 8,044 / 8,459 |
| 3 | 34 | 1.410% | 434 / 654 / 97 |
| 4 | 20 | 0.154% (813,477 of 529,845,120) | 98 / 106 / 505 |
| 5 | 3,292 | 0.578% | 6,265 / 6,125 / 2,685 |

Seed 4 with its original quotient maps unchanged (SHA-256 `24856aba6cd5c1cfb747aa395254e76dfa2037c9ba4e033184e31b5bc5d01c13`): 414,171 wrong of 183,220,992; 81,949 of those come from states the maps do know.

**M2 and M3, the editor on Dispatch-3.** New world: 2 to 4 legs, two gates, six order fields (rules in appendix A). Training on 2 or 3 legs with same-gate legs only. Final strata, generated after the freeze: A unseen families of trained size, B four legs, C cross-gate legs. Five interchange-trained cores, 4,000 flip attempts per stratum per core:

| Method | A | B | C | Pooled (bar: 90%) |
|---|---|---|---|---|
| Predictor edit (frozen primary) | 99.9% | 41.5% | 86.5% | **73.3%, fail** |
| Slot-write edit | 99.9% | 41.3% | 86.3% | 73.2% |
| Message and resume | 100.0% | 42.2% | 86.3% | 73.5% |
| Full restart | 99.9% | 43.9% | 86.7% | 74.3% |
| Planner alone, no edit, every step valid | 100.0% | 49.9% | 84.4% | – |

On plain-imitation cores the predictor edit succeeds on 12.4% and abstains on 77 to 90%. End-to-end latency: edit 424 µs, message 332 µs.

**M4.** One core reaches 26,323 distinct saved states for about 800 meanings at the trained history length and 73,041 with 16 wait slots per leg, with task success at 100% throughout. A sampled dictionary knows 19.5% falling to 6.4% of the steps of fresh jobs. Hidden-channel retest with balanced payloads and a decoder on every stage: the behaviour quotient leaves the payload readable (93.5% and 97.1% exact recovery, chance 25%); the specification quotient erases it (25.5% and 25.0%).

**M5.** 300 operator shifts of 8 jobs: the learned planner meets every commitment on 1,551 of 2,400 jobs against 1,552 for the exact planner, at about 230 times the compute, and changes about 200 steps the exact planner keeps.

### 4.3 v0.3: registers, a discrete reader, a certificate for any length

- **Memory.** One register per order field. A field shown in an observation overwrites its register. The write is a rule, not learned.
- **Reader.** Four small learned functions (85,233 parameters, about 2 minutes of training): start, leg step, route, deliver. The reader sweeps from the last leg back to the current one and carries one code (at most 64 values).
- **Certificate.** The reader's code and the exact planner's value table are run together through every kind of leg until no new pair appears; every pair is then checked against every current leg and gate state. Details in appendix B.
- **Repair.** Wrong entries become jobs, are labelled by the exact planner and trained on, until the certificate is clean.

Same training data as v0.2 (cores `v3r23_*`), the v0.2 final items, the frozen v0.2 harness:

| | v0.2 | v0.3 |
|---|---|---|
| Edit success pooled | 73.3% | **96.0%** (per seed 95.7 to 96.3%) |
| B: four legs | 41.5% | 100.0% |
| C: cross-gate legs (never trained) | 86.5% | 87.4% |
| C when training includes cross-gate legs (`v3r24_*`) | – | 100.0% |

Long jobs, final families, fresh seed, planner alone with ordinary events, share of jobs with every action valid:

| Cores | 2–4 legs | 5–6 | 7–8 | 12 | 16 |
|---|---|---|---|---|---|
| Trained on 2–3 legs, same-gate strata | 100.00% | 100.00% | 99.95% | 99.92% | 99.95% |
| Trained on 2–4 legs, cross-gate strata | 99.96% | 99.91% | 99.89% | 99.89% | 99.90% |
| Same, after repair | 100.00% | 100.00% | 100.00% | 100.00% | 100.00% |
| Trained on 2–3 legs, cross-gate strata (leg kinds never seen) | 88.70% | 85.23% | 83.35% | 83.18% | 83.72% |

Certificates (alphabet "same" = 32 same-gate leg kinds; "all" = 64):

| Cores | Alphabet | Clean | Wrong entries where not clean |
|---|---|---|---|
| 2–3 legs, no repair | same | 4 of 5 | 32 |
| 2–3 legs, repaired | same | 5 of 5 | – |
| 2–4 legs, no repair | all | 0 of 5 | 704 to 9,347 |
| 2–4 legs, repaired | all | **4 of 5** | 4,096 (seed 3; two variants of the loop fixed it) |
| No value-table aid (ablation) | either | 0 of 4 | 3,712 to 76,332 |

Certificate against simulator: 100,000 fresh jobs of 2 to 16 legs per alphabet per core through the network. Every clean (core, alphabet) pair: 0 wrong actions in 1.44 million action stages. Every unclean pair: first 20 witness jobs confirmed wrong on the network. Three unclean pairs made no wrong action at all in the 1.44 million sampled stages.

Other v0.3 results:

- **Arm M** (the v0.2 core unchanged, plus one training rule: the saved state must equal what a restart would write): distinct saved states 377 to 378 and 323 to 324 on two seeds, flat from 1 to 16 wait slots, sampled dictionary coverage 100.0%, task success 100%. The third seed lost the task (62%).
- **Outcome-only training, exploratory** (no planner labels; logged random jobs and their outcomes): one seed has a clean certificate on all 64 leg kinds (16,384 entries); one is clean on same-gate legs with 3,626 wrong entries on all; one fell to 88%.
- **Latency**, median, 3-leg and 16-leg jobs: network with message 214 and 866 µs; network with register write 230 and 883 µs; certified tables with register write 1.0 and 2.0 µs; exact planner in plain Python 7.2 and 30.0 µs.
- **Ablations.** A free-vector carry and a core without the value-table aid reach the same sampled accuracy at every length. Length extrapolation comes from registers, relative addressing and a shared leg step. The discrete carry is what makes the certificate possible.

## 5. Claims ledger

Status: **stands** (frozen rule, final data), **corrected**, **retracted**, **exploratory** (not frozen, often one seed), **failed** (a pre-set rule was not met).

| # | Claim | Version | Status | Evidence |
|---|---|---|---|---|
| 1 | The v0.1 frozen decision rule passes on five seeds on sealed families (99.6%; swap +48.9 points; unrelated drop 0.0). | v0.1 | Stands. Decisions reproduced item by item from a fresh clone. | `REPORT.md` §3; `results/v02/m0/` |
| 2 | Plain imitation gives the same accuracy and fails the swap (37.2%); interchange training is what passes it. | v0.1 | Stands. v0.2 adds: an editor also needs it (12.4% on plain cores). | `REPORT.md` §4.1; `results/v02/M3_tables.md` |
| 3 | Discrete memory is not needed for the swap (continuous with interchange training: 98.1%). | v0.1 | Stands. | `REPORT.md` §4.1 |
| 4 | Training with mid-job changes gives goal memory; without them, route memory (99.1% against 42.2%). | v0.1 | Stands. | `REPORT.md` §4.2 |
| 5 | "Zero wrong answers on all 60 trained families, every seed" (exhaustive check). | v0.1 | **Corrected.** True only for the 20-pattern message list. With all 36 patterns every seed fails, on trained families too. | `docs/v02_certificate_scope.md` |
| 6 | "Seed 4 with quotient memory is correct on every history in all 100 families." | v0.1 | **Corrected.** 0 of 7,864,320 with 20 patterns (reproduced). With 36: 414,171 wrong of 183,220,992. | `results/v02/M1_tables.md` |
| 7 | "Quotient memory removes most remaining errors." | v0.1 | **Retracted.** On matched jobs the original maps change wrong jobs by −140 to +220 per 2,000,000; rebuilt maps help on two seeds and hurt on three. | `results/v02/M1_tables.md` |
| 8 | "A planted hidden channel is erased by quotient memory." | v0.1 | **Corrected.** Holds for the specification quotient (25.5%, 25.0%; chance 25%). Not for the behaviour quotient (93.5%, 97.1%). | `results/v02/REPORT_v02.md` §6.2 |
| 9 | Typed patch through a dictionary edits saved memory at 95 to 100% on Dispatch-2, also on tangled memory. | v0.1 | Stands for Dispatch-2 fixtures. Does not scale: on Dispatch-3 a per-family dictionary reaches 9 to 25%. | `REPORT.md` §4.5; `results/v02/M3_tables.md` |
| 10 | A portable editor applies a correction on unseen families of trained size (99.9%). | v0.2 | Stands, narrowly: equal to a message. | `results/v02/m3/*_final.json` |
| 11 | v0.2 advancement rule: at least 90% pooled, with a measured advantage over a message. | v0.2 | **Failed.** 73.3% pooled; slower than a message. | `results/v02/REPORT_v02.md` §5 |
| 12 | On Dispatch-3 the v0.2 saved state cannot be listed, and the count grows with irrelevant history. | v0.2 | Stands (one core, development families; labelled exploratory there). | `results/v02/scaling/v2_iit_s1.json` |
| 13 | With the v0.2 training data, the v0.3 architecture reaches 96.0% pooled on the v0.2 final items and 100% on four-leg jobs. | v0.3 | Stands. Rule C4 clause 1. | `results/v03/v02final/v3r23_s*.json` and `*_items.json` |
| 14 | Trained on 2 to 4 legs, every seed has at least 99% of jobs fully valid in every length stratum up to 16 legs (lowest 99.58%). | v0.3 | Stands. Rule C2. | `results/v03/final/` |
| 15 | Four of five repaired cores are correct for every job of any length over all 64 leg kinds. | v0.3 | Stands. Rule C3b. This is the claim most worth attacking. | `results/v03/cert/v3r24fix_s{1,2,4,5}.json` and `_tables.json` |
| 16 | A clean certificate means 0 wrong actions in simulation; an unclean one has real failing jobs. | v0.3 | Stands. Rule C3c. | `results/v03/confirm/` |
| 17 | Registers equal the order of record at every step. | v0.3 | Stands (true by construction; tested at 32,748 job steps). | `tests/test_regcore.py` |
| 18 | Canonical memory can be trained into the unchanged v0.2 core by one rule (378 states against 26,000 to 73,000). | v0.3 | Stands on 2 of 3 seeds. Rule C1b. | `results/v03/scaling/v3m_s*.json` |
| 19 | An edit is better than a message on some measured dimension. | v0.2, v0.3 | **Failed twice.** They are the same write followed by the same step. | `results/v03/latency/` |
| 20 | A planner trained from logged outcomes only, with no planner labels, can be certified. | v0.3 | Exploratory. One seed of three certified on all leg kinds; two of three above 99.9%. | `results/v03/cert_o/`, `results/v03/final/v3o_s*.json` |
| 21 | Leg kinds never seen in training are handled. | all | **Not achieved.** 83 to 89%. | `results/v03/final/v3r23_s*.json`, X strata |
| 22 | The learned planner has an advantage over the exact planner. | all | **Not shown.** Equal outcomes; the exact planner needs no training. | `results/v02/shift/`, `results/v03/shift/` |

## 6. Pass rules of v0.3 and their results

Rules were written in `docs/v03_spec.md` and frozen in commit `de80fd7` before any v0.3 final job was generated.

| Rule | Result |
|---|---|
| C1a. Registers are the order of record | Pass |
| C1b. Canonical memory trained in: at most 1,458 states, at least 99% dictionary coverage, at least 99.5% task success, at every history length, for 2 of 3 seeds | Pass (2 of 3) |
| C2. At least 99% of jobs fully valid in every covered stratum, for 4 of 5 seeds, without repair | Pass (5 of 5 for both training sets) |
| C3b. At least 4 of 5 repaired cores clean on all leg kinds | Pass (4 of 5) |
| C3c. Certificate agrees with the simulator | Pass |
| C4. Edit rule: 90% pooled; unrelated within 5 points; faster than a message | Clauses 1 and 2 pass; clause 3 fails, as the spec predicted |
| Exploratory: outcome-only training at 99% on every stratum for 2 of 3 seeds | Pass |

## 7. Replay plan, cheapest first

Set up once:

```bash
git clone https://github.com/princeanozie25-web/stillway-pilot && cd stillway-pilot && git checkout v0.3
python3.12 -m venv venv && venv/bin/pip install torch==2.14.1 numpy==2.5.4
export PY=venv/bin/python PYTHONPATH=.
```

**Step 1. The any-length certificate, with plain Python only (seconds).**

```bash
python3 stillway3/check_tables.py results/v03/cert/v3r24fix_s1_tables.json all
python3 stillway3/check_tables.py results/v03/cert/v3r24_s1_tables.json all
python3 stillway3/check_tables.py results/v03/cert_o/v3o_s1_tables.json all
```

Expected:

| Tables | Pairs | Route checks | Wrong | Brute force, every job of up to 2 legs | Verdict |
|---|---|---|---|---|---|
| `v3r24fix_s1` (repaired) | 42 | 10,752 | 0 | 149,760 checks, 0 wrong | CERTIFIED |
| `v3r24_s1` (before repair) | 91 | 23,296 | 960 | 0 wrong | NOT certified |
| `v3o_s1` (no planner labels) | 64 | 16,384 | 0 | 0 wrong | CERTIFIED |

Then do it without my checker. Appendix B gives the table format and the planner's three lines. The second row matters: its faults are invisible in every job of up to 2 legs.

**Step 2. Custody (seconds).**

```bash
./v03/check_all_freezes.sh
```

Expected: `FREEZE intact` (v0.1), `v0.2 freeze intact: 9 files, 7 cores with editors`, `v0.3 FREEZE intact: 16 files, 30 checkpoints`.

**Step 3. Smoke replays (under a minute each).**

```bash
./smoke.sh          # v0.2: four recorded corrections; expected last line: SMOKE PASS: every replay matches its recorded outcome
./smoke_v03.sh      # v0.3: certificate, the same four fixtures with the v0.3 core, one 16-leg correction; expected last line: SMOKE PASS
```

In `smoke_v03.sh` the fixtures `failure_four_legs` and `failure_cross_gate` are recorded v0.2 failures; the v0.3 core must show "all steps valid" on both.

**Step 4. Tests (a few minutes).**

```bash
$PY tests/test_world_n.py                       # any-length world == frozen world3 at 4 legs (93,600 observations) == plain reference up to 10 legs
$PY tests/test_regcore.py runs/v3r24fix_s1      # register rule; tables == network at 10,828 action stages
$PY tests/test_edits_n.py runs/v3r23_s1         # any-length edit harness == frozen v0.2 harness on 39 runs of 600 attempts
$PY tests/test_world3.py; $PY tests/test_messages36.py
node demo/test_proof.js                         # the page's JavaScript checker: same counts as step 1
```

**Step 5. Rebuild the scorers and rescore the per-attempt files.** Do not import `stillway/scorer.py`, `stillway2/edits.py`, `v02/m3_eval.py`, `stillway3/certify.py` or `v03/eval_edits.py`.

| Version | Rules to rebuild from | Per-item files to rescore |
|---|---|---|
| v0.1 | `docs/evaluator_spec.md`; clean-room simulator in `independent/sim.py` | `fixtures/sealed/`, `runs/f_iit_s*/eval_sealed.json` |
| v0.2 | `docs/v02_codex_challenge.md` | `results/v02/m3/*_final_items.json`; 36-pattern witnesses in `results/v02/expanded/<run>/report.json` |
| v0.3 | `docs/v03_codex_challenge.md`, appendices A and B here | `results/v03/v02final/*_items.json`, `results/v03/final/*_items.json`, `results/v03/confirm/*.json` |

**Step 6. Regenerate results from the frozen checkpoints.**

```bash
$PY v03/eval_edits.py runs/v3r23_s1 v02final          # under a minute; A, B, C joint success 1.0, 1.0, 0.8628 for register write; rewrites its result files byte for byte
$PY v03/eval_edits.py runs/v3r24fix_s1 final 850390379 # about 5 minutes; 1.0 in all eleven strata
$PY v03/confirm.py runs/v3r24fix_s1                    # about 1 minute; 0 wrong actions on both alphabets
$PY -m stillway3.certify runs/v3r24_s3                 # 1,344 wrong entries on alphabet all, 20 of 20 witnesses confirmed
$PY v02/m3_eval.py runs/v2_iit_s1 final 1670983329     # v0.2 final results for one core
v02/par.sh 2 v02/m1_counterexample.py runs/f_iit_s4 && $PY v02/m1_counterexample.py runs/f_iit_s4 merge   # v0.2: 20 failures in 393,216 two-field episodes, simulator only (par.sh uses ~/Developer/voxcpm-venv/bin/python; edit its first line)
```

**Step 7. Retrain.**

```bash
$PY v03/determinism.py                                 # about 4 minutes; expected: 32 of 32 tensors equal, twice
$PY -m stillway3.train --name c1 --data t24x --seed 1  # about 2.5 minutes; compare weights with runs/v3r24_s1
$PY -m stillway3.repair runs/c1 --alphabet all --out runs/c1_fix
```

Bit-identical weights are expected on the same torch build and CPU only. On other hardware, compare outcomes, and note that the certificate is a property of each checkpoint: a retrained core needs its own.

Costs of the heavy runs, for planning: v0.1 training 27 to 29 minutes per seed; the v0.2 36-pattern check about 30 minutes per seed on 8 cores; a v0.2 core 33 to 43 minutes; arm M 48 minutes per seed; every v0.3 register core about 2 minutes; the whole v0.3 final pass about 20 minutes on 7 cores.

## 8. Where to attack

1. **Claim 15, the any-length certificate.** If the closure argument has a hole, the headline falls. Things to try: random jobs of 100 legs against your own planner; all jobs of up to 3 legs over 64 leg kinds (9.4 million); a formal re-derivation. The argument assumes a route decision depends only on the two requirement registers, the two gates and the legs ahead. Check that against `stillway3/model.py`.
2. **Network against tables.** The certificate is made on integer tables. The network is tested equal to them on samples only. Route choices are far from a tie where it matters (gap 1.9 to 9.4 on certified imitation cores). Code choices are not always: the smallest gap between the two nearest codes, over everything the closure touches, is 0.0008 to 0.09 on the four imitation cores certified on all leg kinds and 0.00005 on `v3o_s1` (carry values lie between −1 and 1). Floating-point differences on another machine could flip a code there. The v0.3 report said "the tables are not near a tie" about routes only; that sentence is now corrected.
3. **Holdouts are internal.** I authored every final stratum. In v0.3 I saw the certificates before the freeze, and a certificate covers final families too. The v0.2 final items were known to me in aggregate before I designed v0.3.
4. **The v0.3 world is the v0.2 world.** The architecture was designed after seeing how v0.2 failed on it. That is tuning to a benchmark, even with frozen rules. A new world would be a fairer test.
5. **Built-in structure.** Which observation field feeds which register, and the direction of the sweep, are given. Arm M learns the first on two seeds of three; nothing learns the second.
6. **Small planning state.** The exact planner carries one of 29 value tables. Nothing here measures how the method behaves when that number is large.
7. **Seeds.** Five at most; arm M and outcome-only training lost one seed in three; the plain repair loop lost one in five, and the variants that fixed it were chosen after seeing the failure.
8. **v0.1 enumeration is an overapproximation** (any observation may follow any other), and it still missed 16 message patterns. Look for other inputs it does not list.
9. **Events I did not model**, in either world.

## 9. Deviations and things that went wrong, all versions

- **v0.1.** One assistant built evaluator and planner. Two subagents were used before Prince asked for none. The first eligibility rule let an impostor score 4% and was tightened. After the freeze, three runs were re-checked with a state cap and two controls on sealed families only, in new files. The sealed set is spent.
- **v0.2.** My cost estimate for the 36-pattern run was low by a factor of 2. The first predictor threshold rule made the editor abstain on everything and was fixed on development data. The frozen rule chose the predictor editor by 0.1 point; a later exploratory run suggests slot write is the more portable one. Latency tails are from a loaded machine.
- **v0.3.** The v0.3 report's sentence on margins covered route choices only and read as if codes were far from a tie too; corrected in `results/v03/REPORT_v03.md` and `docs/v03_certificate_scope.md` after the tag (section 8, point 2). The arm-M rule at full weight broke all three seeds; it was stopped and a ramp added (logs kept). A launcher bug wrote six repair logs into one file, and the seed-3 repair was cut off once and rerun from scratch. Checkpoint files saved before a config field was added hash differently from a fresh save; all weights are bit-identical on retraining. Arm M and the outcome-trained cores finished after the freeze commit under rules already frozen. The interactive page was not checked by eye in a browser. The v0.3 push added about 300 MB of per-attempt score files.

## 10. Open decision (Prince's)

- **A.** Measure the size limit: the same world with 3 and 4 gates, to see how large the carried planning state can get before the certificate and the repair stop working. About a day. My recommendation as the next step.
- **B.** A domain where nobody has written the planner. The only place a learned, certified planner could beat a hand-written one.
- **C.** Stop model work and keep the evaluator and the proof tool.

## Appendix A. Dispatch-3, enough to rebuild

- A job has `L` legs. Leg `i` has two routes. Each route has a trip `(effect, gate)`: effect keep, toggle, open (set to 1) or close (set to 0), acting on gate 0 or gate 1. There are two gates, each 0 (closed) or 1 (open). Station `i`, after leg `i`, may have a parcel.
- Work order: `gate0`, `gate1` in {0 none, 1 must end closed, 2 must end open}; one dock in {0, 1, 2} per station.
- Frame: INIT, then per leg: wait slots, a ROUTE slot, a DELIVER slot (only if the station has a parcel). The whole order is shown at INIT. Later it may be revised by messages.
- Events before any slot after INIT: a leg not yet travelled has its two routes swapped; a gate flips; a repaint; a dock closes; a message revises one field; the whole order is re-issued.
- **Exact planner.** At ROUTE `i`: for each route, the largest number of gate requirements that can still be met at the end over every choice of later routes; the valid routes are those that reach the overall maximum (both, on a tie). At DELIVER `i`: the order's dock, or `(dock + 1) mod 3` if that dock is closed. It plans for the world as it stands; it does not anticipate events.
- **An edit attempt** (v0.2 rules, unchanged in v0.3): one job, one pause slot, one field that still matters, one new value. Eligible if every gate requirement can still be met under the corrected order and the same job with the correction ignored fails. Joint success: the edited obligation and every other obligation are met, with no abstention.
- Reference in 20 lines of plain Python: `ref_valid_routes` and `ref_dock` at the bottom of `stillway2/world3.py`. Observation layout: `docs/v02_codex_challenge.md` §2 for 4 legs; width `20 + 18 * lmax` in general (`stillway3/world.py`).

## Appendix B. The v0.3 tables and the certificate

A tables file (`results/v03/cert/<core>_tables.json`) holds:

| Table | Shape | Meaning |
|---|---|---|
| `term[q0][q1]` | 4 × 4 | code at the start of the backward sweep, from the two gate requirements |
| `cell[code][leg]` | 64 × 64 | code after one more leg, going backwards |
| `route[code][leg][gates]` | 64 × 64 × 4 | route proposed at the current leg (0 or 1) |
| `deliver[parcel][closed + 1]` | 4 × 4 | dock, given the order's dock and the closed dock (−1 = none) |

Encodings: trip = `effect * 2 + gate` with effects 0 keep, 1 toggle, 2 open, 3 close; leg kind = `trip_of_route_0 * 8 + trip_of_route_1`; `gates = gate0 * 2 + gate1`.

The planner, at leg `i` of a job with legs `0..L-1`:

```
code = term[q0][q1]
for j = L-1 down to i+1:  code = cell[code][leg_j]
route = route[code][leg_i][gates]
```

The certificate:

1. The exact planner's value table `T` has four entries: for each joint gate state, how many requirements can still be met. Behind the last leg, `T[s]` is the number of requirements that state `s` meets. One leg further back, `T'[s] = max(T[after route 0 from s], T[after route 1 from s])`.
2. Start from the 9 pairs `(term[q0][q1], T(q0, q1))`. Apply every leg kind in the alphabet to every pair: `(cell[code][leg], T')`. Repeat until no new pair appears. At most 64 × 81 pairs can exist.
3. For every pair, every leg kind and every gate state `s`: the proposed route must reach `max` of the two entries of `T` it can move to.
4. Deliveries: all 12 entries with `parcel` in 0..2 must equal the exact planner's dock.

A clean result covers every job of every length over that alphabet. Exact wording and bounds: `docs/v03_certificate_scope.md`.

## Appendix C. Where each thing is

| Need | File |
|---|---|
| Decision memos | `docs/v02_decision_memo.md`, `docs/v03_decision_memo.md` |
| Full reports | `REPORT.md`, `results/v02/REPORT_v02.md`, `results/v03/REPORT_v03.md` |
| Frozen specs | `docs/evaluator_spec.md`, `docs/v02_transfer_spec.md`, `docs/v03_spec.md` |
| Certificate scope | `docs/v02_certificate_scope.md` (Dispatch-2, with the corrections), `docs/v03_certificate_scope.md` |
| Challenge files | `docs/v02_codex_challenge.md`, `docs/v03_codex_challenge.md` |
| Every table | `results/tables_sealed.md`, `results/v02/M1_tables.md`, `results/v02/M3_tables.md`, `results/v03/tables.md` |
| How each number was produced | `README.md`, `README_v02.md`, `README_v03.md` |
| Prior art checked | `docs/claim_matrix.md` |
| Interactive pages (private to Prince until shared) | Replay Bench (v0.1), Shift Replay (v0.2), Proof Bench (v0.3); sources in `demo/` |

---

# Part 2: v0.4 to v0.6

Added 21 November 2026. Each version has its own frozen spec, report and memo; this part is the map and the ledger.

## P2.1 What happened

| Version | Branch, freeze commit | What it tested | Outcome |
|---|---|---|---|
| v0.4 | `v0.4`, `d9a9047` | Prince's brief "a small planner that gets cheaper with experience": proof cost at 2 to 5 gates; a synthetic approvals workflow with procedures chosen by a learned code; sleep (retrieval, rehearsal, consolidation, dreaming); whole-system cost. | Frozen thresholds not met. Registers and the versioned bank work. Learned procedure selection is 1.75 points below a hand-coded macro on novel combinations. Consolidation keeps old policies (98.8%) and learns new ones worse than rule induction. A non-neural tracker given the rules wins on speed, bytes and accuracy. |
| v0.4 addendum | `v0.4`, after the freeze | Programs found by search instead of weights by descent. | In my own domain: procedures found by enumeration reach 100%; a learned rule library beats the neural arms; the whole planner is induced from logs with no network at 99.99%. **Qualified by v0.5.** |
| v0.5 | `v0.5`, `3858823` | The same program search on eight public rule tables, frozen before the data was fetched. | Failed all five rules. A small network reached 99% on 8 of 8 tables; program search on 3. Search wins only where its language contains the rule. |
| v0.6 | `v0.6`, `2b125d1` | Whether experience with related policies makes a new one cheaper to learn, on Unicode plural and ordinal rules, frozen before the data was fetched. | Yes on both families. Mostly by recognising a rule seen before (4 audits against 128; exact in about 10 chosen audits; no cautious error). Tables against weights as the store of experience: split. |

Regression ticket from v0.4: the seed-4 count of 19 against 20 reproduces on one machine across numeric runtimes (CPU 20, Apple GPU 19). The differing episode is `L032.g0.o100.s2.dock0.bay2`; two codes are 0.00001 apart at its PLAN step.

## P2.2 Claims ledger, continued

| # | Claim | Version | Status | Evidence |
|---|---|---|---|---|
| 23 | Learned route planners certify at 2 and 3 gates (15 of 15 seeds each) and their tables equal the exact planner's in size and speed. | v0.4 | Stands. No advantage over the exact planner, which compiles 1,000 to 6,000 times faster. | `results/v04/tables.md` M1 |
| 24 | A learned route planner certifies at 4 gates within an hour. | v0.4 | **Not achieved** (both pilots incomplete). The exact planner closed 5 gates: 3,016,838 states. | `results/v04/MANIFEST_RUNS.json` |
| 25 | Learned procedure selection is within 1 point of a hand-coded macro on novel event combinations. | v0.4 | **Failed**: −1.75 points (−2.02 to −1.50). | `results/v04/tables.md` M2 |
| 26 | Suppressing the selected procedure code changes outcomes as predicted and nothing protected moves. | v0.4 | Stands (99.76%, 0 of 49,679). Swapping codes matches the prediction only 88.7%. | `results/v04/m2/` |
| 27 | Consolidation into a versioned bank retains older policies where rehearsal does not. | v0.4 | Stands (98.2% to 98.8% against 82.4%), in my own domain. | `results/v04/tables.md` M3 |
| 28 | Dreaming earns inclusion (beats both consolidation and rehearsal on transfer). | v0.4 | **Failed**: beats consolidation (+13.4), not rehearsal (−5.1). | same |
| 29 | The compiled planner beats the best qualifying neural comparator on compute, latency and bytes. | v0.4 | Vacuous: no other neural arm qualifies. It loses to a non-neural tracker given the rules. | `results/v04/tables.md` M4 |
| 30 | Program search with verification beats gradient learning. | v0.4 addendum | **Corrected by v0.5**: true where the search language contains the rule (my own domain, MONK-1); false on 5 of 8 public rule tables. | `results/v05/tables.md` |
| 31 | A small network learns other people's rules with fewer audits than a decision tree and reaches 99% on all eight public tables. | v0.5 | Stands (internal; untuned comparators). | `results/v05/tables.md` |
| 32 | Experience with related policies cuts the audits a new policy needs, on real rule families. | v0.6 | **Corrected by Codex's hidden family**: no gain on novel rules there (512 audits against 512). Stands on the two Unicode families by the frozen rule (64 against 128; 16 against 96). The 99% yardstick was too easy for about half the rules; the exact-rule figures are in the report. | `results/v06/*_tables.md` |
| 33 | A rule seen before is recognised exactly within 16 chosen audits with no cautious error. | v0.6 | Stands on all three families (8, 12 and, on Codex's hidden family, 4 audits). | same |
| 34 | Programs are a better store of experience than network weights. | v0.6 | **Split**: yes on cardinal rules (weights never reach 99% on novel rules), no on ordinal rules (weights 16 audits, programs 48). | same |
| 35 | Choosing which case to audit reduces audits. | v0.5, v0.6 | Mixed: halves a network's audits on 6 of 8 tables (v0.5); finds an exact seen rule four times faster (v0.6); no gain for novel rules at 99% (v0.6). | both |
| 36 | A learned system beats a hand-written planner. | all | **Still not shown.** | – |

## P2.3 Replay, cheapest first

```bash
git checkout v0.6
python v04/check_freeze.py                                   # v0.4 freeze (22 files); also ./v03/check_all_freezes.sh for v0.1 to v0.3
./run_v04.sh                                                 # v0.4 smoke: certificate, mutation test, fixtures, regrading, demo trace
python v04/regrade.py runs/v4f_proc_s_s1/raw_outputs.npz     # success from raw outputs with the plain grader
python v04/seed4_diff.py results/v04/seed4/failing_ids_cpu_f32_b1.json YOUR_IDS.json
python -I v05/blind.py monks1 --tests 2 && python v05/report.py          # one public table, all learners; then the five v0.5 rules
python -I v06/family.py data/external/cldr/family_cardinal.json --shard 0 --of 4 && python v06/report.py cldr_cardinal
git diff 3858823 -- v05/blind.py                             # empty: the v0.5 learner is as frozen
git diff 2b125d1 -- v06/family.py v06/cldr_to_family.py      # empty: the v0.6 harness is as frozen
```

The v0.5 and v0.6 freeze commits come before the commits that add `data/external/`; `git log --stat` shows the order.

## P2.4 Where to attack

1. **The hidden family** (`docs/v06_codex_family_brief.md`). Every v0.5 and v0.6 dataset was chosen by me. This is the one test I cannot bias. **Run on 21 November: see P2.6.**
2. **v0.6's yardstick.** "99% of cases right" is met by answering the most common category for about half the new rules. Re-score with the exact-rule measure or a per-category one and see whether L1 survives.
3. **v0.6's groups are small** (7, 10, 11 and 4 rules) and many locales share rules.
4. **Comparators in v0.5** (tree, forest, network) are untuned defaults.
5. **v0.4's rehearsal arm** got as many update steps as consolidation, but each of its steps trains every row. Its edge on new policies may come from that.
6. **v0.4's approvals domain and its rule family are mine.** A short rule engine solves it.
7. **Everything after a freeze** is labelled exploratory in its report: the v0.4 addendum, the v0.5 selector, the exact-rule table in v0.6.

## P2.5 Where the design stands

Keep past rules as tables in a versioned bank with a promotion gate; learn a rule nothing like the past with a small network; let held-out audits choose between proposers; deploy tables. A hand-written planner still wins wherever one exists, and no test has yet been run in a domain without one.

## P2.6 Addendum: Codex's hidden family (run after this report was written)

One run of `family_codex.json` (SHA-256 `2a4e40c6…9565`) at commit `e84c46e`, three seeds, every arm kept. Outputs locked in commit `b7120cd` before the author's breakdown was requested. Memo: `docs/v06_codex_hidden_memo.md`. Raw: `results/v06/codex_hidden_shard0.json`.

| Rule (frozen) | Result on the hidden family |
|---|---|
| L1. Experience helps on novel rules | **Fail**: 512 audits against 512 from scratch |
| L2. Programs need no more audits than bank rows | Pass, emptily: programs 976, bank rows never; both worse than scratch |
| L3. A seen rule is recognised within 16 chosen audits, no cautious error | **Pass**: 4 audits, 0 errors |
| L4. Selector within one budget step of the best single learner | Pass (the post-freeze change to this line of `v06/report.py` is set out in the memo; every computable reading agrees) |
| L5. Choosing audits helps on novel rules | **Fail**: 512 either way |

**P2.5 corrected.** What the bank has been shown to do on rules I did not write is recognise a policy it already holds, exactly and cheaply. It has not been shown to transfer anything to a policy that is new. The run also shows it is all or nothing: one new policy that differs from a past one in 8 of 1,440 cases was taken for the past one (wrong on those 8 while unanimous), and once an audit contradicted the match the learner started again from scratch.

**After the author's breakdown** (`docs/v06_codex_reveal_note.md`). Codex's table matches the locked outputs on all 20 rows. The 14 novel policies are 8 variants and 6 new shapes. Repeats: bank ahead on 6 of 6. Variants: ahead on 3, level on 4, behind on 1, one of the three being the mistaken near-copy. New shapes: ahead on none. Six of the eight variants differ from every past policy in 29% to 55% of cases, so a bank of tables cannot see them as variants. An exploratory fix tried afterwards (past policies' decisions as inputs) helps on the five modular-test policies (512 audits against the whole table) and costs on shapes with nothing shared; it does not rescue L1.
