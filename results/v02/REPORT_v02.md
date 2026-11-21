# Stillway v0.2 report: can an editor change a paused planner's memory?

Fable, 21 November 2026. Branch `v0.2`, from commit `6588d9f`. All work on the M1 Max, CPU only, no paid compute. Implementation and experiments by Fable; independent replay is Codex's. The decision memo is `docs/v02_decision_memo.md`.

## 1. Verdict

1. **The scientific bet holds in a narrow form.** A small editor that sees only the saved code numbers, a field name and a new value can apply a correction to a paused job. On unseen layout families of trained size it succeeds on 99.9% of non-trivial edits, the same as an ordinary operator message.
2. **The advancement rule fails.** Pooled over the three final strata the editor reaches 73.3%, below the 90% bar. On four-leg jobs it gets 41.5% and on cross-gate layouts 86.5%. A message and a full restart fail to the same degree, and the planner alone, with no edit, gets 50% and 84% there. The limit is the planner core.
3. **No advantage over a message was measured.** The edit is 28% slower end to end (424 µs against 332 µs). Against a full restart it saves work: no re-briefing ticks and about half the needless step changes.
4. **Editing needs interchange-trained memory.** On plain-imitation cores the same editor succeeds on 12% and abstains on about 80%.
5. **The v0.1 certificate was narrower than stated.** It covered 20 of the 36 operator-message patterns. With all 36, no seed is error-free, and quotient memory does not reliably repair jobs: the original maps change almost nothing on matched jobs, and rebuilt maps help on two seeds and hurt on three.
6. **On the new world the saved state cannot be listed.** 26,000 distinct states for about 800 meanings; a sampled dictionary knows 20% of the steps of fresh jobs. State count grows with irrelevant history; task success does not drop.
7. **Recommendation: change the architecture of the memory, do not scale, keep the benchmark.**

## 2. M0: custody and a runnable baseline

Command: `v02/m0_custody.sh <workdir>`. Fresh clone of `6588d9f`, fresh virtual environment (Python 3.12.14, torch 2.14.1, numpy 2.5.4, installed from PyPI), Apple M1 Max, 32 GB, 10 cores, macOS 27.0. Raw outputs in `results/v02/m0/`.

| Check | Result |
|---|---|
| `tools_check_freeze.py` before and after rescoring | FREEZE intact, both times |
| Dev and sealed fixtures regenerated from code | identical SHA-256 to the freeze, all three files |
| Five primary checkpoints | hashes match the freeze |
| Targeted swap decisions, item by item | 10,000 of 10,000 identical |
| Shuffled swap decisions, item by item | 10,000 of 10,000 identical |
| Ordinary accuracy on sealed fixtures | 2,489 / 2,500 (matches Codex) |
| Run time | about 31 s per checkpoint to rescore |

**Retraining.** Seeds 1 and 4 retrained from the archived manifests into `runs/r_iit_s1` and `runs/r_iit_s4`: **weights bit-identical to the frozen checkpoints** (largest difference 0), same step counts (10,150 and 10,311). Every score is therefore identical. The checkpoint files differ only in the run name stored inside. 

This shows that training is exactly repeatable on this machine and torch build. It says nothing about another machine.

Seeds 2, 3 and 5 were retrained afterwards (`runs/r_iit_s2`, `r_iit_s3`, `r_iit_s5`): also bit-identical. All five primary seeds retrain exactly.

## 3. M1: the certificate's input coverage gap

Full tables: `results/v02/M1_tables.md`. Scope and wording: `docs/v02_certificate_scope.md`. First progress report: `results/v02/M1_progress_1.md`.

**The gap.** The simulator accepts two order fields revised at the same stage. The v0.1 extractor listed 20 message patterns; the schema permits 36. `stillway2/automaton.py` enumerates them from the field domains. `tests/test_messages36.py` builds simulator events for every mask and value at every stage (8,640 episodes), with repeated writes, a reissue followed by an override, and closed-bay handling, and checks the encoded observation and the order of record.

**Counterexample from the simulator alone**, seed 4: 20 failures in 393,216 two-field episodes, 6 of them on trained families. All 20 revise dock and bay together at LEG1. The other seeds, same sweep: 1,890 (seed 1), 1,744 (seed 2), 34 (seed 3), 3,292 (seed 5); every seed fails on trained families too (6 to 1,578 episodes).

**The original maps.** v0.1 saved only counts. `v02/m1_recover_maps.py` repeats the v0.1 code with the unchanged v0.1 extractor and saves the maps. For seed 4 it reproduces the archived counts exactly (plain 3 / 174,345,600; quotient 0 / 7,864,320). SHA-256 of the maps: `24856aba6cd5c1cfb747aa395254e76dfa2037c9ba4e033184e31b5bc5d01c13`.

**Those maps, unchanged, on all 36 patterns** (a state the map does not know is left as it is, as in v0.1), seed 4:

| | Pairs checked | Wrong |
|---|---|---|
| Plain memory | 529,845,120 | 813,477 (0.154%) in 51 families |
| Original maps | 183,220,992 | 414,171 (0.226%) in 44 families |
| of which from a state the map does not know | | 332,222 |
| of which from a known representative | | 81,949 |
| Transitions that land on an unknown state | 12,782,671 of 175,045,248 (7.3%); 90,203 distinct unknown states | |
| Maps rebuilt on the 36-pattern machine | 17,720,064 | 78,193 (0.441%) |

So the original map is incomplete and also wrong: one fifth of the wrong decisions come from states it does know. Shortest witness from a known representative (family KO-KO, trained): order dock 0, gate closed, bay 2; PLAN message "bay 1"; LEG1 message "dock 0 and bay 2"; the proposed route loses the gate obligation.

**Same histories, three memories.** Counts over different reachable machines cannot say how many jobs were repaired. On 2,000,000 jobs sampled from the 36-pattern alphabet, seed 4:

| | Jobs with a wrong decision | Repaired | Broken | Tie-break changed only |
|---|---|---|---|---|
| Plain memory | 98 | | | |
| Original maps | 106 | 3 | 11 | 42,162 |
| Rebuilt maps | 505 | 10 | 417 | 51,098 |

On this seed quotient memory did not repair jobs. Failures are also rare when weighted by how often a state is reached (98 in 2,000,000) and much less rare when every reachable state counts once (0.15%).

**All five primary seeds.** Every seed's recovered maps reproduce its archived v0.1 counts. With 36 patterns none is error-free.

| Seed | Plain memory: wrong pairs | Original maps unchanged | Maps rebuilt on 36 patterns | Same 2,000,000 jobs, jobs with a wrong decision: plain / original maps / rebuilt maps |
|---|---|---|---|---|
| 1 | 1.547% | 1.364% | 5.698% | 6,786 / 6,794 / 8,434 |
| 2 | 1.817% | 1.681% | 2.976% | 8,040 / 8,044 / 8,459 |
| 3 | 1.410% | 1.741% | 0.116% | 434 / 654 / 97 |
| 4 | 0.154% | 0.226% | 0.441% | 98 / 106 / 505 |
| 5 | 0.578% | 0.633% | 0.017% | 6,265 / 6,125 / 2,685 |

- **The original maps change almost nothing on matched jobs**: between 140 fewer and 220 more wrong jobs per 2,000,000, with 19,000 to 42,000 jobs changing only a tie-break. 7 to 14% of their transitions land on a state they do not know.
- **Rebuilt maps are a coin toss**: they cut wrong jobs by 78% on seed 3 and 57% on seed 5, and add wrong jobs on seeds 1, 2 and 4.
- Pair counts (529 to 791 million per seed for plain memory) and matched-job counts tell different stories, because a pair count gives a rarely reached state the same weight as a common one.

Cost: seed 4 took 2,236 CPU-seconds to recover the maps and 11,765 CPU-seconds for the 36-pattern run (30 minutes on 8 cores; the estimate from one family was 12 minutes, so the profile under-estimated by a factor of 2).

## 4. M2: a new transfer test, frozen before any final family existed

Specification: `docs/v02_transfer_spec.md`. Freeze: `results/v02/FREEZE_v02.json`, commit `14700485083f6759f166a56ccff019b247999956`. Final seed, derived from that commit hash: `1670983329`.

- **Dispatch-3** (`stillway2/world3.py`): 2 to 4 legs, two gates, trips that name their gate, six order fields, 1 to 6 live obligations, wait stages that lengthen history without adding obligations. Exact reference by enumeration; `tests/test_world3.py` checks the batched world against a plain reference on 6,722 action stages.
- **The v0.2 core is a new model** (`v2_*`), 180,247 parameters. The v0.1 two-leg reader was replaced by one shared leg encoder swept backward over the legs still ahead. Three changes were made on development evidence before the freeze: a value head, supervision of the sweep with the exact planner's value table, and a residual memory update. The third mattered most: accuracy went from a plateau at 87% to 99.8% in a third of the steps.
- **Seven cores**: five with interchange training, two with plain imitation. All reach 99.9 to 100% on training and development families with discrete memory. 12,400 to 12,900 gradient steps of 512 jobs, 33 to 43 minutes each on one thread.
- **Final strata**, never sampled with a trained model before the freeze: A unseen families at trained sizes; B four legs; C cross-gate legs.
- **Shortcut planners** on development attempts. Ignoring the edit, or re-reading the original order, succeeded on 22% of eligible attempts; the non-trivial filter removes exactly those attempts, so both score 0 afterwards by construction. On the remaining attempts, overwriting the whole state scores 48% and copying another job's actions 35 to 37%. None passes.
- Disclosures: the final-mode code path was smoke-tested once before the freeze with an untrained network and a different seed. The final strata are authored by the assistant that built the model: an internal holdout.

## 5. M3: the portable editor

Full tables: `results/v02/M3_tables.md`. Per-item scores: `results/v02/m3/*_final_items.json`.

`edit(saved IDs, field, new value)` returns new IDs or abstains. Two candidates, both fitted on training families only (114,560 state pairs, 10 s; the predictor has 136,064 parameters and trains in 30 s):

- **Slot write**: a table (field, value) → code read off training jobs; writes one slot.
- **Predictor**: a small network that outputs all eight slots.

Selection on development families (interchange-trained cores): predictor 99.9%, slot write 99.8%. By the rule written before the dev run, the predictor is primary. The difference is inside the noise.

**Final strata, joint edit success, %. Mean over core seeds, range in brackets. 4,000 attempts per stratum per core; non-trivial eligible attempts in the denominator; an abstention is a failure.**

| Interchange-trained cores (5) | A: unseen families | B: four legs | C: cross-gate | Pooled |
|---|---|---|---|---|
| **Predictor edit (primary)** | 99.9 (99.8–100.0) | 41.5 (32.7–54.2) | 86.5 (85.9–87.2) | **73.3 (70.0–78.2)** |
| Slot-write edit | 99.9 (99.7–100.0) | 41.3 (32.0–54.4) | 86.3 (85.7–87.2) | 73.2 |
| Message and resume | 100.0 (99.8–100.0) | 42.2 (33.7–54.7) | 86.3 (85.8–86.9) | 73.5 |
| Full restart | 99.9 (99.7–100.0) | 43.9 (35.1–56.0) | 86.7 (86.0–87.5) | 74.3 |
| Per-family dictionary (privileged, 400 attempts) | 25.2 | 8.8 | 22.5 | – |
| Shortcut: overwrite whole state | 49.4 | 20.8 | 42.2 | 36.2 |
| Shortcut: copy actions | 35.0 | 14.4 | 32.0 | 26.2 |
| Core alone, no edit: every step valid | 100.0 | 49.9 (41.7–61.6) | 84.4 (83.0–85.5) | – |

| Plain-imitation cores (2) | A | B | C | Pooled |
|---|---|---|---|---|
| Predictor edit | 17.4 | 6.1 | 15.2 | 12.4, with 77 to 90% abstained |
| Slot-write edit | 9.2 | 3.7 | 9.3 | 7.1 |
| Message and resume | 99.9 | 36.9 | 84.8 | 70.9 |
| Per-family dictionary (privileged) | 56.0 | 17.9 | 41.5 | – |

**Against the advancement rule** (interchange-trained cores, predictor):

| Requirement | Result | Pass |
|---|---|---|
| Joint success at least 90% on untouched families, all eligible attempts | 73.3% pooled; 99.9% on stratum A alone | **No** |
| Unrelated obligations within 5 points of unedited replay | −3.5 to +0.1 points in every stratum and seed (never worse by more than 0.1) | Yes |
| One measured advantage over message-and-resume: lower median end-to-end latency at comparable success | Success is comparable (within 0.2 points pooled). Latency is higher: 424 µs against 332 µs | **No** |

A successful but slower editor earns a controllability result. It has not earned a speed claim, and on these strata it has not earned a transfer claim either.

Reading:

- **Wherever the core can plan, the edit works.** Per seed on stratum A: 99.8 to 100.0%, lower 95% bound at least 99.6%. No abstentions.
- **Where the core cannot plan, nothing helps.** B and C fail the same way for the edit, the message and the restart.
- **Other edit kinds on stratum A** (5 seeds, predictor / message): no-op 100.0 / 100.0; requirement added 99.9 / 100.0; requirement withdrawn 100.0 / 100.0; two edits on the same field 99.8 / 100.0; two edits on different fields 99.7 / 100.0; mirror pairs with both jobs right 99.8 / 100.0. Slot write is weaker on repeated edits of one field (97.7).
- **Mirror pairs** are the case where one edit needs opposite routes in two layouts. Copying actions gets both jobs right in about 20% of pairs.
- **The privileged dictionary is worse than the portable editor.** 384 labelled jobs sampled in the target family cover too few states (section 6).
- **What the edit can do that a message cannot:** correct the saved state without stepping the planner. That costs 103 µs (predictor) or 35 µs (slot write) against 332 µs for a step. Nothing in this world needs it.

Latency, one job, one CPU thread, median over 600 runs after warm-up, mean of 5 cores (machine under load; 99th percentiles are in the tables file): message and resume 332 µs; predictor edit then one step 424 µs; slot write then one step 355 µs; predictor edit only 103 µs; slot write only 35 µs; symbolic table update and exact re-plan 6 µs.

## 6. M4: the scaling limit, and the hidden-channel claim

### 6.1 Where states stop being listable

`v02/m4_scaling.py`, core `v2_iit_s1`, development families, 20,000 sampled jobs per cell. Jobs with exactly three live obligations for the history sweep.

| Wait slots per leg | Steps in frame | Task success | Distinct saved states | Meanings | Sampled dictionary: share of fresh steps it knows | Fresh jobs fully covered |
|---|---|---|---|---|---|---|
| 1 (trained) | 13 | 100% | 26,323 | 809 | 19.5% | 1.2% |
| 2 | 17 | 100% | 30,092 | 1,115 | 18.2% | 1.0% |
| 4 | 25 | 100% | 37,506 | 1,721 | 14.4% | 0.3% |
| 8 | 41 | 100% | 49,466 | 2,933 | 10.0% | 0.05% |
| 16 | 73 | 100% | 73,041 | 5,357 | 6.4% | 0% |

| Live obligations (trained history) | Jobs | Task success | Distinct states | Meanings | Coverage of fresh steps |
|---|---|---|---|---|---|
| 1 | 1,159 | 100% | 2,309 | 76 | 32.1% |
| 2 | 4,565 | 100% | 9,797 | 343 | 30.9% |
| 3 | 7,630 | 100% | 18,830 | 810 | 28.3% |
| 4 | 5,097 | 100% | 15,601 | 963 | 21.2% |
| 5 | 1,227 | 100% | 4,971 | 460 | 9.5% |

- **The first failure is at the first step past Dispatch-2.** At the trained history length a sampled dictionary already misses 80% of steps, so a dictionary-based edit would abstain on almost every job. Exact enumeration was not attempted: the sampled state count alone exceeds the jobs sampled.
- **The planner does not fail with history.** Task success is 100% at five times the trained history length. The state count grows because many codes mean the same thing and the choice among them drifts with what was seen (the slot-write table's most common code for a value covers only 11 to 100% of its uses).
- Budget: 6 to 27 s and under 650 MB per cell. The ceiling is coverage, not compute.

**Sampled against exact, where both finish** (`v02/m4_sampled_vs_exact.py`, Dispatch-2, v0.1 seed 4, 12 families):

| Histories sampled per family | Exact reachable states found | Fresh steps the sample knows | Meanings that disagree with the exact run |
|---|---|---|---|
| 300 | 34% | 86.4% | 0 |
| 3,000 | 66% | 98.9% | 0 |
| 30,000 | 86% | 99.9% | 0 |

On Dispatch-2 a sampled dictionary is safe (it never contradicts the exact one) and covers 99.9% of what a job meets, in 31 s against 385 s. On Dispatch-3 the same method covers 20%.

### 6.2 The hidden-channel claim, tested harder

`v02/m4_hidden.py`. Two v0.1 controls that carry a planted two-bit payload. Jobs balanced: every (work order, payload) cell in every sealed family has 24 jobs. 28,800 test jobs; decoders trained on 28,800 other jobs. Chance: 50% per bit, 25% exact.

| Exact payload recovery | Control 1: plain | behaviour quotient | specification quotient | Control 2: plain | behaviour quotient | specification quotient |
|---|---|---|---|---|---|---|
| Model's own head | 92.7% | 27.7% | 27.7% | 87.7% | 25.9% | 25.9% |
| Fresh decoder on saved codes, all stages | 94.1% | **93.5%** | 25.5% | 97.7% | **97.1%** | 25.0% |
| Fresh decoder on visible actions | 27.0% | 26.8% | 25.3% | 27.0% | 27.1% | 25.5% |
| Same, pooled over 25 jobs with one payload | 32.1% | 34.4% | 26.3% | 34.9% | 33.4% | 26.3% |
| Bits about the payload in the state, given family, stage and meaning | 1.80 | 1.24 | 0.003 | 1.74 | 1.21 | 0.000 |
| Task: every step valid | 99.25% | 99.25% | 99.00% | 99.86% | 99.86% | 99.98% |

- **The behaviour quotient does not erase the payload.** The model's own head goes blind, and a fresh decoder still reads 93 to 97%. v0.1 tested one late stage and missed this.
- **The specification quotient erases it** for every observer tested: saved codes, visible actions, and actions pooled over 25 jobs. Task accuracy moves by −0.25 and +0.12 points.
- **A small leak through tie-breaks exists with plain memory**: actions alone give 27%, and 32 to 35% when 25 jobs are pooled.
- Access: the canonicaliser uses a dictionary built by enumerating the target family with the exact planner as labeller. That is oracle-labelled target-family data. Observers not tested: timing, and anything outside the 20-pattern enumeration.

## 7. M5: an operator's shift

`v02/m5_shift.py`. 300 shifts of 8 jobs from final families (stratum A kind), two priority commitments each. At a random tick the operator closes a dock and revises one field of one unfinished job; in half of the shifts where it is possible the operator also asks to change a delivered parcel; a quarter of the shifts get a gate fault after the resume. Replay page: https://claude.ai/artifact/KfQwy2bHNQaPPvpQatWm62 (private until shared).

Core `v2_iit_s1`, frozen predictor editor; ranges over the five cores in brackets where they differ.

| System | Jobs with every commitment met (of 2,400) | Priority deadlines missed | Ticks lost to re-briefing | Steps changed | Changed where the exact planner did not | Steps the exact planner rejects | Compute after the pause, median |
|---|---|---|---|---|---|---|---|
| Exact planner (symbolic) | 1,552 | 0 | 0 | 750 | 0 | 0 | 29 µs incremental, 44 µs restart |
| Learned + memory edit | 1,551 (1,550–1,551) | 0 | 0 | 941 (935–989) | 200 (195–254) | 0 (0–1) | 6.7 ms |
| Learned + message | 1,551 (1,549–1,551) | 0 | 0 | 945 (940–993) | 205 (201–259) | 0 (0–1) | 6.5 ms |
| Learned + full restart | 1,551 (1,547–1,551) | 0 | 1,279 | 1,130 (1,088–1,178) | 390 (348–442) | 0 (0–3) | 6.4 ms |

- 1,552 is the ceiling: in the other jobs the gate requirements cannot be met together from the start.
- **The symbolic planner wins** on compute (about 230 times cheaper) and on needless changes (none). Its numbers stay on the page.
- **The learned planner matches its outcomes** on these families. With a memory edit or a message it changes about 200 steps the exact planner keeps (ties between two valid routes). A full restart doubles that and costs 1,279 ticks, under the stated assumption that re-briefing a job takes one tick.
- No priority deadline was missed by any system (two ticks of slack).
- Declined requests: 150 of 150 edits to delivered parcels were declined by rule before any editor call. The editor itself abstained 0 times on these cores.
- Forecast at the pause against what happened: identical for 2,360 of 2,400 jobs; the rest are shifts with a later gate fault.
- Peak memory 225 MB. Setup cost of the learned system: one core (about 40 minutes of CPU) and one editor (40 s).
- **Distinct capability of the learned system in this world: none.** It reaches the symbolic planner's outcomes at 230 times the compute.

## 8. Frozen findings, exploratory changes, and what awaits confirmation

**Frozen findings** (code, checkpoints and rules fixed before the data existed):

- M0 custody and bit-identical retraining of all five primary seeds.
- M3 final results on strata A, B and C for seven cores and both editors; the shift results in section 7 use the same frozen cores and editor.

**Recomputed on v0.1 assets** (no new training, new analysis code): all of M1; M4 hidden-channel table; the sampled-against-exact comparison.

**Exploratory, not frozen:**

- The scaling sweep (one core, development families).
- The three training-recipe changes that produced the v0.2 core (made on development evidence before the freeze).
- **A core with canonical memory** (`v02/x_canonical.py`, one seed). One slot per order field and a fixed code table; the code each slot must hold is given as a label. Accuracy 100% on training and development families after a quarter of the usual steps. Distinct saved states: 708 to 718 at every history length (the frozen core: 26,323 rising to 73,041). A sampled dictionary knows 98.9 to 99.4% of the steps of fresh jobs (the frozen core: 19.5% falling to 6.4%). Edits on stratum A: 100% for both editors, and the slot table is the identity, so no fitting is needed. Strata B and C: 36% and 85%, as for the frozen cores. So canonical memory makes the state listable at no cost in accuracy, by making the memory symbolic by construction. It does not make the planner extrapolate.
- **A core that saw four-leg and cross-gate jobs in training** (`v02/x_train_all.py`, one seed, 18,326 steps). Message and restart: 100% on A, B and C. Slot-write edit: 100.0%, 99.96%, 100.0%. Predictor edit: 99.95%, **82.5%**, 99.9%: the predictor was fitted on two- and three-leg training jobs only and does not carry to four-leg states, while the slot table does. So the failures on B and C in section 5 are a lack of exposure, not a limit of the design, and the slot-write editor is the more portable of the two. The frozen selection rule picked the predictor by 0.1 point on development data. Stratum B is not untouched for this core.

**Awaiting independent confirmation:** rescoring of the v0.2 final items by a rebuilt scorer; the 36-pattern counts; a challenge set that I did not author (`docs/v02_codex_challenge.md`).

## 9. How to run it

```bash
./smoke.sh                                   # one command: replays four recorded corrections and checks them
PYTHONPATH=. python v02/run_fixture.py runs/v2_iit_s1 fixtures3/success_three_legs.json     # one job, full trace
PYTHONPATH=. python v02/m3_eval.py runs/v2_iit_s1 final $(python v02/final_seed.py)          # regenerate the final results
```

Fresh environment: Python 3.12, `pip install torch==2.14.1 numpy==2.5.4`. Everything else is in the repository. `README_v02.md` lists every command that produced a number in this report. `results/v02/MANIFEST_v02.json` has the SHA-256 of every result file, checkpoint and editor.

Failure fixtures in `fixtures3/`: a four-leg job and a cross-gate job on which the frozen core takes a wrong step with or without the edit, and a plain-imitation core on which the editor declines. For Dispatch-2, witness histories of every 36-pattern failure mechanism are in `results/v02/expanded/<run>/report.json`.

## 10. Deviations and things that went wrong

- Two v0.2 pilot designs were abandoned before the freeze: without sweep supervision the core learned too slowly, and without residual memory it stopped at 87%.
- The first predictor threshold rule made it abstain on everything (it required exact code match, and many codes mean the same thing). Fixed on development data before the freeze.
- The cost estimate for the 36-pattern run was low by a factor of 2.
- Several jobs were run in parallel on 10 cores, so every wall-clock time and every 99th-percentile latency in this report is from a loaded machine.
- Two subagents were used in v0.1 before Prince's instruction not to; none was used in v0.2.
