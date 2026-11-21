# Stillway v0.4 report: a small planner that gets cheaper with experience

Fable, 21 November 2026. Brief: Prince Anozie. Start commit `69f5216`. Branch `v0.4`. Freeze commit `d9a904773f3dbe1712a679cd785145f407010125`; final data salt 2701878737; seeds 1 to 5. Every table in full: `results/v04/tables.md` (rebuilt by `v04/report.py`). One-page memo: `docs/v04_decision_memo.md`.

## 1. Verdict

The frozen thresholds are not met. Registers and the versioned bank work. Learned procedure selection and neural consolidation each fall short of a simpler competitor.

| Milestone | Outcome |
|---|---|
| Regression ticket | Reproduced here: 20 failures on CPU, 19 on Apple GPU. One episode differs, because two memory codes are 0.00001 apart at one step. |
| M1, proof cost | Learned readers certify at 2 and 3 gates (15 of 15 seeds each). Their tables are identical in size and speed to the exact planner's, which compiles 1,000 to 6,000 times faster. Four gates did not finish in the hour. The exact planner closed five gates. |
| M2, one reusable procedure | Procedural codebook 99.3% (ordinary) and 98.3% (novel combinations); hand-coded macro 100% and 100%. The gap on novel combinations is 1.75 points, outside the 1-point margin. Continuous carry 7%, flat codes 5%, text scratchpad 26 to 29%. |
| M3, sleep | Consolidation keeps older policies (98.2%; 98.8% with dreaming) where rehearsal loses them (82.4%). On new policies it trails rehearsal and a non-neural rule-induction baseline. Retrieval is far behind. |
| M4, whole system | Compiled tables: 15.8 µs per job, 3 kB. The non-neural tracker with rules given: 7.7 µs, 312 bytes, 100% right. No qualifying neural rival exists to beat. |

## 2. Regression ticket: seed 4, 19 against 20

`v04/seed4_ticket.py` reran the v0.2 two-field sweep (393,216 episodes) keeping every failing episode ID, on four numeric runtimes.

| Runtime | Failures | Verdicts that differ from the reference | Forward passes with a different code on identical input |
|---|---|---|---|
| CPU float32, one input per pass (the v0.2 path) | 20 | reference | – |
| CPU float32, 2,048 per pass | 20 | 0 | 220 of 524,557 |
| CPU float64 | 20 | 0 | 115 of 524,537 |
| Apple GPU (MPS) float32 | **19** | **1** | 231 of 524,472 |

- The differing episode is `L032.g0.o100.s2.dock0.bay2` (a sealed family). It fails on CPU and passes on the GPU.
- First divergent step: PLAN, saved state in `[17, 30, 30, 22]`, same observation. Slot 2's two nearest codes are 1.14e-05 apart on CPU and 7.6e-06 on GPU; CPU writes code 24, GPU writes code 8. Logits agree to four decimals; no action is taken at PLAN. The trajectories then differ and CPU's fails at LEG1.
- This is the most fragile of the 20 failures (smallest code gap on its trajectory). No runtime changed an action on identical input; the largest logit difference is 0.00002.
- Both results are kept: `results/v04/seed4/failing_ids_<runtime>.json`, first divergence in `report.json`.
- **Not confirmed against Codex's machine.** I do not have its ID list. `python v04/seed4_diff.py results/v04/seed4/failing_ids_cpu_f32_b1.json <codex ids>` shows the differing ID.

**Outcome-trained tables per runtime** (`v04/export_runtimes.py`): `v3o_s1`, `v3r24fix_s1`, `v3r24fix_s2` exported under torch CPU float32, torch CPU float64, torch MPS float32 and a NumPy float32 forward pass. All 12 exports certify clean. The float64 export of `v3o_s1` differs in 78 route entries (ties between equally good routes), so it has its own hash and its own certificate; the other eleven match their float32 export exactly.

## 3. M0: the contest

- Branch `v0.4`; spec `docs/v04_spec.md`; freeze file `results/v04/FREEZE_v04.json` (22 files); `python v04/check_freeze.py` passes.
- One-command runner: `./run_v04.sh` (smoke), `./run_v04.sh demo`, `./run_v04.sh all SALT`.
- Execution manifest: `results/v04/MANIFEST_RUNS.json`: 108 runs, 99 complete, 9 incomplete, with hashes of every checkpoint, table file, bank version and result file.
- Budget: one hour and one CPU thread per run; closures capped at 4 GB and one hour.
- Holdout: internal. External challenge format and scorer: `docs/v04_external_challenge.md`, `v04/score_external.py`.
- Size: the smallest (s, 74,018 active parameters per decision) met the 1-point rule in the one-seed pilot and was used for the five-seed runs. Sizes m and l are one-seed pilots.

## 4. M1: what the proof costs

Route core of Dispatch for G gates. Exact reverse dynamic program to a fixed point, compiled to tables; learned readers trained, read off as tables and certified against it. One C program (`v04/runner.c`) runs both table files and the table-free exact planner on identical jobs.

| Gates | Reachable planning states (exact value vectors) | Exact closure + compile | Exact table file | Learned readers with a clean certificate | Median time to a clean certificate, widths 128 / 256 / 512 | Entries checked |
|---|---|---|---|---|---|---|
| 2 | 29 | 0.009 s | 11 kB | 15 of 15 | 24 / 34 / 98 s | 7,424 |
| 3 | 500 | 0.085 s | 720 kB | 15 of 15 | 174 / 215 / 467 s | 576,000 |
| 4 | 22,695 | 15.3 s | 105 MB | 0 of 2 pilots | not reached in one hour | – |
| 5 | 3,016,838 | closure only: 3,061 s, 1.55 GB (inside the cap) | not compiled | not attempted | – | – |

Growth of the exact frontier by depth, 5 gates: 243, 3,991, 35,151, 241,401, 1,071,931, 1,077,045, 497,004, 78,400, 10,600, 1,040, 32. Plot: `results/v04/m1/proof_cost.png`.

**Latency per decision, median, warm** (same jobs):

| Gates | Legs | Exact tables | Learned tables | Exact planner, no tables | Network, batch one |
|---|---|---|---|---|---|
| 2 | 16 | 15 ns | 15 ns | 190 ns | 672 µs |
| 3 | 16 | 15 ns | 15 ns | 290 ns | 773 µs |
| 3 | 64 | 105 ns | 105 ns | 1,090 ns | 2,988 µs |
| 4 | 16 | 15 ns | – | 500 ns | – |

- **Learned tables equal exact tables** in bytes (11,178 and 720,078) and in speed, because a certified reader has exactly one code per value vector. Per-call saving against the exact tables: 0.0 ns. Offline cost: 24 to 500 s against 0.009 to 0.09 s. **There is no break-even**: the learned route costs more before the first call and saves nothing after it.
- Against its own network a table set pays back its training after about 36,000 calls at 16 legs (two gates, width 128).
- **The table-free exact planner** needs no file, runs in 190 to 500 ns at 16 legs, and still works at five gates, where tables would not fit.
- **Runtime check:** every closure entry at two gates (7,424) and 400,000 sampled entries at three gates give the table's answer in the C program and in the network, for all six benchmarked readers. All 12,000 benchmark decisions per reader are valid.
- **Mutation test:** one flipped reachable entry gives 1 wrong entry and a one-leg failing job, confirmed by listing every route choice (2, 3 and 4 gates).
- **Two protocols.** Protocol 1 (codes for value vectors seen in sampled jobs, then witness repair) left 181 of 500 three-gate vectors without a code and never converged; kept as a recorded failure. Protocol 2 (one code per exact vector; training on the exact machine itself) is what certifies. It is a supervised copy of the exact tables.
- **Four gates.** Both one-seed pilots (widths 128 and 512) were at 79 to 88% wrong leg-step entries after 2,000 machine-training steps at 36 minutes, produced an incomplete first certificate, and were killed by the operating system at about 55 minutes. Projection: more than 100 CPU-hours if three-gate ratios held; capacity at that size is untested.
- **Legal messages** are enumerated from the schema (`stillway4/schema.py`): 9,472 messages over four schemas, register rule checked on each; the Dispatch-2 schema gives 36.

## 5. M2: one reusable procedure

A synthetic approvals workflow (`docs/v04_spec.md` section 2): 5 signature slots, 4 jurisdictions, opaque policy IDs, 8 event kinds, 36 hidden rules. A short rule engine solves it, so this is a controlled benchmark. All arms train on the same 20,000 logged documents.

| Arm | Ordinary documents | Novel event combinations | Per seed, novel | Protected statuses changed | Active parameters |
|---|---|---|---|---|---|
| Procedural codebook | 99.31% | 98.25% | 99.2, 99.0, 99.1, 100.0, 94.0 | 255 | 74,018 |
| Hand-coded macro, same executor | 100.00% | 100.00% | 100 on every seed | 0 | 74,018 |
| Text scratchpad | 29.01% | 26.28% | 30.5, 39.9, 16.4, 27.3, 17.3 | 106 | 113,782 |
| Continuous carry | 7.31% | 6.64% | 5.8 to 7.2 | 28,805 | 89,568 |
| Flat discrete codes | 4.59% | 4.58% | 3.8 to 6.1 | 11,548 | 114,512 |
| Direct answer | same outputs as continuous carry (same weights, history re-read every step); 9 times the compute | | | | |
| Dependency tracker / replay engine (rules given) | 100% | 100% | – | 0 | none |

- **Procedural codebook minus hand-coded macro:** ordinary −0.69 points (95% interval −0.80 to −0.58); novel combinations **−1.75 (−2.02 to −1.50)**. The 1-point rule fails on novel combinations.
- **Who supplied what.** Registers and the executor are given in both procedural arms. The learned arm also learns which code an event selects, which slots a code recomputes and under which policy. The text arm is given the grammar and 14.8 million teacher tokens. The tracker is given every rule.
- **Sizes.** Procedural m: 99.5% and 99.2% (pilot). Procedural l: 55% (its soft training phase hit the time box). Continuous m and l: 6 to 8%. Flat codes m and l: under 3%.
- **More data (exploratory).** Continuous carry with 200,000 documents: 59.0% and 46.3%.

**Interventions** (2,000 novel-combination documents per seed; the prediction is the hand-coded macro on the same executor under the same intervention):

| Intervention | Outcome changed | Learned arm equals the prediction | Per seed | Protected statuses changed |
|---|---|---|---|---|
| Suppress the selected code | 47.4% | 99.76% | 99.3 to 100.0 | 0 of 49,679 |
| Change one argument | 50.9% | 94.76% | 89.7 to 96.4 | 111 of 40,793 |
| Swap the code for another event's | 37.1% | **88.70%** | 75.6 to 96.6 | **628 of 45,083** |

- The code does work: suppressing it changes the outcome as predicted, and nothing protected moves.
- The codes are not the hand-coded procedures. Seeds 1 to 3 use one code for SIGN, CORRECT and MOVE, although CORRECT must recompute under the slot's pinned policy and the others under the current one. A swapped code therefore does something else than the macro's, and touches slots the macro protects.
- Composition was not attempted: single procedures do not transfer inside the margin.
- Failing fixture: `results/v04/fixtures/m2_proc_failure.json`. Compiled tables equal the network on 2,500 of 2,500 documents.

## 6. M3: sleep

Six sessions per seed. Each brings 3 new policy IDs (half from reserved rules) and one expiry for one tenant; 120 documents arrive; outcomes are logged with provenance; each arm updates; fresh documents are scored. The procedural core is frozen. Mean over 5 seeds and 6 sessions:

| Arm | New policies: decisions right | Facts absent from the log | New-policy documents fully right | Older-policy documents fully right | Probe decisions made wrong by a sleep |
|---|---|---|---|---|---|
| No update | 5.9% | 14.5% | 0.4% | 44.5% | 0 |
| Retrieval | 74.7% | 14.5% | 27.4% | 87.9% | 2 |
| Retrieval, overrides indexed too | 69.8% | 14.5% | 20.1% | 63.6% | 19,506 |
| Rehearsal | 98.1% | 94.4% | 86.2% | 82.4% | 6,169 |
| Consolidation | 86.6% | 83.8% | 67.8% | 98.2% | 9 |
| **Consolidation + dreaming** | 93.0% | 89.9% | 81.2% | **98.8%** | 2 |
| Rule induction (non-neural) | 97.4% | 92.8% | **88.1%** | 98.5% | 0 |
| Rehearsal with the core trained too (ablation) | 97.7% | 93.5% | 22.0% | 17.9% | 192,977 |

Probe decisions: 1,710,000 per arm. Expired policies: every arm that received the expiry notice abstains correctly (99.9%).

Paired differences, documents fully right, families resampled within seed:

| Comparison | New policies | Older policies |
|---|---|---|
| Dreaming minus consolidation | +13.4 [+6.4, +21.0] | +0.5 [+0.2, +0.7] |
| Dreaming minus rehearsal | −5.1 [−10.2, +0.1] | +16.9 [+14.4, +19.8] |
| Dreaming minus rule induction | −7.0 [−11.2, −3.0] | +0.3 [+0.0, +0.5] |
| Dreaming minus retrieval | +53.7 [+49.5, +57.7] | +10.7 [+9.5, +12.0] |

- **Retention is the bank's result.** Frozen old rows, a validation gate and a registry keep older policies at 98 to 99%. In-place rehearsal learns the new ones best among neural arms and breaks old ones (per seed 43% to 99.9%).
- **Dreaming rule:** it must beat both consolidation and rehearsal on transfer. It beats consolidation and not rehearsal. **Not earned.**
- **Seed spread is large** for new policies: dreaming 63.9% to 95.1% across seeds; consolidation 44.4% to 82.3%.
- Dream log: 6,723 candidate labels for 2,241 missing fact combinations; 2,780 confirmed, 3,943 rejected; 1,576 dream cases kept. Candidates promoted / discarded: consolidation 110 / 12, with dreaming 100 / 5.
- Rollback: an older bank version reloads with a matching hash in 5 of 5 seeds. Sleep cost per session: consolidation 0.56 s, with dreaming 0.37 s, rehearsal 7.49 s.
- The consolidation arms keep no index, so their scores are what entered the bank.
- **Update steps were matched** (about 4,900 per run), but a rehearsal step trains every row on every record while a consolidation step trains one row. Rehearsal's advantage on new policies may come from that.
- Correspondence with the Sleep framework: `docs/v04_sleep_correspondence.md`. An adaptation; knowledge seeding by distillation and RL, and gradient-based dream selection, are absent.

## 7. M4: the whole system

Batch one, idle machine, mean of 5 seeds, graded from raw outputs by the plain grader.

| System | W2 success (base policies) | W3 success (after the sixth sleep, 600 documents) | Job, median | CPU per successful job (W2) | Bytes at run time |
|---|---|---|---|---|---|
| Stillway compiled tables | 98.9% | 83.6% (new 68.9%, older 98.4%) | 15.8 µs | 16.1 µs | 3,078 |
| Dependency tracker, rules given | 100% | 100% | 7.7 µs | 7.7 µs | 312 |
| Replay engine, rules given | 100% | 100% | 60.7 µs | 60.8 µs | 312 |
| Retrieval tables | – | 50.0% | 16.1 µs | – | 6,294 |
| Procedural network | 98.9% | 83.6% | 3,811 µs | 3,856 µs | 304,389 |
| Continuous carry network | 6.1% | – | 1,845 µs | 30,786 µs | 366,908 |
| Direct answer network | 5.0% | – | 17,297 µs | 501,220 µs | 366,908 |
| Flat codes network | 3.9% | – | 3,076 µs | 91,403 µs | 536,548 |

Other banks on W3 through the same network: consolidation 81.7% (new 67.4%, older 95.9%), rehearsal 80.6% (80.3%, 81.0%), retrieval 49.6% (17.7%, 81.4%), none 7.4%.

- **Against the thresholds.** Quality: 1.1 points below the tracker on W2 and 16 below on W3: fails. Compute, latency and bytes against the best qualifying neural comparator: no other neural arm qualifies; against the same arm run as a network the tables are 99.6% cheaper and 99 times smaller. Against the fastest correct non-neural implementation: twice as slow, ten times larger, and less accurate.
- p95 per job: tables 17.1 µs, tracker 8.5 µs, network 4,015 µs.
- Fresh process (seed 1): tables load in under a millisecond, first job 0.025 ms, 30 MB resident; the network loads in 0.6 s, first job 4.3 ms, 216 MB.
- Resume against restart (tables): one more event on a saved job 5.0 µs including loading it; replaying 13 events 9.8 µs.
- **Break-even.** A sleep cycle costs 0.38 s. Against the network: 98 jobs. Against the replay engine: 8,352 jobs. Against retrieval tables: 2.3 million jobs (0.2 µs saved per job). Against the tracker: none. Cost per job at 10, 100, 1,000, 10,000, 100,000 jobs per sleep cycle: 37,984, 3,812, 395, 54, 19 µs.
- Raw timing samples: `results/v04/m4/timing_samples_s1.npz` (made after the freeze with the benchmark's own functions).

**The demo** (`./run_v04.sh demo`, seed 1, session 3). Document A arrives today and names a policy introduced today; it runs on yesterday's bank, pinned. Every learned system abstains on the new policy (3 abstentions) and is graded wrong; the tracker with rules given is right. After the sleep and a restart from files, document B (a fact combination absent from the log, with a reserved event combination) is right for consolidation, dreaming, rehearsal and rule induction, and wrong for retrieval and no-update. The bank file's hash matches the recorded version; the compiled tables equal the network; today's three policies were promoted and none was known yesterday.

## 8. Incomplete runs, deviations, things that went wrong

- **Incomplete (9 of 108):** two protocol-2 four-gate readers (killed by the OS at about 55 minutes); five protocol-1 readers (three at three gates, one at two gates, and one at four gates that I stopped when the protocol was replaced); two protocol-2 three-gate pilots from before the fix that returns a failed certificate to machine training. All in `results/v04/MANIFEST_RUNS.json`.
- **Protocol changes before the freeze**, on development data: M1 protocol 2; a failed certificate returns the reader to machine training; consolidation retries discarded candidates; the expiry notice goes to every arm as records.
- **Bugs fixed before the freeze:** reserved event pairs blocked every EXPIRE in training documents; the demo picked the same document twice; the regrading script mishandled expired policies.
- **Made after the freeze** (reporting only, not in the freeze file): `v04/report.py`, `v04/manifest_runs.py`, `v04/fixtures.py`, `v04/final_bench.sh`, `v04/timing_samples.py`, `v04/x_cont_10x.py`, `run_v04.sh`, `v04/check_freeze.py`.
- The benchmark keeps medians and percentiles; raw samples exist for seed 1 only.
- Network latency for the procedural arm is per document divided by 19 events, not per event.
- The external sleep-protocol scorer is not written (`docs/v04_external_challenge.md` says what is missing).
- I read the Sleep framework's blog post and the paper's abstract, not the paper.
- The machine was heavily loaded during training (load average above 100 at one point); training times are upper bounds. Benchmarks ran afterwards on an idle machine.
- No subagents were used.

## 9. What to send an independent grader

| Item | Where |
|---|---|
| Branch, freeze, salt | `v0.4`; `results/v04/FREEZE_v04.json`; 2701878737 |
| Model, table and bank hashes | `results/v04/MANIFEST_RUNS.json` |
| Raw per-job events and reported statuses | `runs/v4f_*/raw_outputs.npz`; `results/v04/m3/*/raw_outputs.npz` |
| Regrade without stored booleans | `python v04/regrade.py <file.npz>` (plain Python and NumPy) |
| Failure fixtures | `results/v04/fixtures/`; `python v04/fixtures.py check` |
| Certificate scope | `docs/v04_certificate_scope.md` |
| Seed-4 ID sets | `results/v04/seed4/` |
| Run commands | `README_v04.md` |

## 10. Added after the brief

`results/v04/BEYOND_THE_BRIEF.md`: three exploratory experiments on the same cores and documents, replacing gradient learning by search with verification. Procedure selection found by enumeration reaches 100.00% on novel combinations on every seed (gradient-learned: 98.25%). A rule library learned from the base policies' logs gives a bank that gets 91.7% of new-policy documents fully right (consolidation with dreaming: 81.2%) and cuts the audits needed for a new policy from 841 to 21, or 4.6 when the system chooses the case. The whole approvals planner induced from raw logs with no network gets 99.99% and 99.995%. Scripts `v04/x_synth_procedures.py`, `v04/x_library.py`, `v04/x_no_network.py`; tables `results/v04/x/tables.md`. None of this is a frozen result.
