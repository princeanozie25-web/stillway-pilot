# Stillway pilot v0.1: what the saved state actually does

Prince Anozie, Stillway Labs. Built and evaluated by Fable in one night, 20 to 21 November 2026, on the M1 Max. All numbers below are from the **sealed** fixtures unless a line says "dev".

## 1. Verdict

1. **The first deliverable exists.** A trained planner that you can pause, correct and resume, with a test of what its saved state does. It runs in the browser replay bench and from the four-operation interface.
2. **The frozen decision rule passes on all five seeds.** Ordinary accuracy on never-seen layout families is 99.6%. A targeted memory swap gives the predicted outcome 99.3% of the time against 50.4% for a shuffled swap. The unrelated obligation is never damaged.
3. **That pass needs one training ingredient: interchange training.** Plain imitation gives the same 99% accuracy and fails the swap (37%). The memory is correct but tangled.
4. **Discrete memory does not buy the swap.** Continuous memory with the same training passes too (98.1%). What discrete memory buys is that you can list every state the planner can reach and check all of them.
5. **That exhaustive check is the strongest thing here.** On all 60 trained families, every seed has zero wrong answers across 43 to 104 million checked cases. All remaining errors are in families the planner never trained on, and the check gives the exact history for each one. One seed, run with quotient memory, has zero wrong answers in all 100 families, the 25 sealed ones included.
6. **Three results I did not find in prior work**: the test that separates "remembers the goal" from "remembers the route"; quotient memory, which erased a planted hidden channel at no task cost; and a typed patch that edits saved memory without running the network.
7. **No speed claim.** In this toy world the exact planner is about 90 times faster than the network. Resume takes one step and restart takes three. That is the whole saving.

One assistant built both the evaluator and the planner. That is not independent reproduction. Section 9 lists what protects the result anyway and what does not.

## 2. What was built

- **Dispatch-2**: a deterministic two-station world. Two legs, each with routes L and R. Each route has a trip that keeps, toggles, opens or closes one gate. The work order names a dock for parcel 1, the gate state the downstream station needs, and a bay for parcel 2. The order is shown once; then it lives only in saved memory. 256 layouts in 100 families.
- **An exact planner**, a reference solution and four impostors.
- **An evaluator**: fixtures, pair credit, the paired replay, controls, and a split made by hashing family names (60 train, 15 dev, 25 sealed).
- **The planner**: a 128-wide recurrent core, four updates per step, four memory slots with 32 codes each. 194,313 parameters. Between steps it passes four integers and nothing else.
- **An extractor** that enumerates every reachable code state and checks every observation against the exact planner.
- **A dictionary, a typed patch, quotient memory, a monitor and a tamper alarm**, all built on the extracted machine.
- **A replay bench** that runs the checkpoint in the browser.

## 3. The decision rule (frozen at 03:55 before the sealed fixtures were opened)

Primary arm: discrete memory with interchange training. Chosen on development data.

| Requirement | Threshold | Result on sealed fixtures, 5 seeds | Pass |
|---|---|---|---|
| Ordinary accuracy on held-out families | at least 90% | 99.6% (97.8 to 100.0) | Yes |
| Targeted swap minus shuffled swap | at least +10 points, lower 95% bound above 0 | +48.9 points (per seed +46.6 to +49.5; lowest lower bound +41.4) | Yes |
| Drop in unrelated-obligation success | at most 5 points | 0.0 on every seed | Yes |

Per seed, 2,000 swap items (1,000 pairs, both directions) in 16 sealed families. Intervals resample whole families.

| Seed | Targeted | Shuffled | Improvement [95% CI] | Unrelated drop | Both unmodified runs valid |
|---|---|---|---|---|---|
| 1 | 96.8 | 50.2 | +46.6 [+41.4, +50.4] | 0.0 | 92.0 |
| 2 | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 | 100.0 |
| 3 | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 | 100.0 |
| 4 | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 | 100.0 |
| 5 | 99.6 | 50.3 | +49.2 [+46.9, +51.4] | 0.0 | 99.7 |

Eligibility: 124 of 378 (layout, gate, reversal) combinations in the sealed families can form a valid pair (32.8%); 42 of 63 sealed layouts have at least one.

Seed 1 is the weak seed. Its misses are ordinary accuracy misses on four sealed families (section 4.4), not swap failures.

## 4. Findings

### 4.1 All arms on the sealed fixtures

Mean over seeds, range in brackets, percent.

| Arm | Seeds | Ordinary | With random events | Mid-plan reversal pairs | Targeted swap | Shuffled | Improvement | Unrelated drop | Rule |
|---|---|---|---|---|---|---|---|---|---|
| Discrete + interchange training | 5 | 99.6 (97.8–100) | 99.6 (98.4–100) | 99.1 (96.4–100) | 99.3 (96.8–100) | 50.4 | +48.9 | 0.0 | **Pass** |
| Discrete, plain imitation | 3 | 99.1 (97.4–100) | 99.3 (98.0–100) | 98.4 (95.2–100) | 37.2 (36.0–38.5) | 28.4 | +8.8 | 31.8 | Fail |
| Continuous, plain imitation | 3 | 99.3 (97.8–100) | 99.5 (98.8–100) | 98.6 (95.8–100) | 36.9 (28.1–45.8) | 24.0 | +12.9 | 51.6 | Fail |
| Continuous + interchange training | 3 | 99.0 (97.0–100) | 99.3 (97.8–100) | 98.4 (95.2–100) | 98.1 (94.2–100) | 50.3 | +47.8 | 0.0 | **Pass** |
| Continuous, quantised after training | 3 | 99.3 (98.0–100) | 99.5 (98.8–100) | 98.6 (95.8–100) | 36.6 (28.9–44.4) | 24.8 | +11.9 | 51.0 | Fail |
| Continuous + interchange, quantised after | 3 | 99.0 (97.0–100) | 99.3 (97.8–100) | 98.4 (95.2–100) | 98.1 (94.2–100) | 50.3 | +47.8 | 0.0 | **Pass** |
| Discrete, world never changes in training | 2 | 97.0 | 88.1 | 42.2 (23.6–60.8) | 17.1 | 18.6 | −1.4 | 49.8 | Fail |
| Discrete + effect head | 2 | 92.5 | 91.7 | 82.9 | 32.1 | 21.2 | +11.0 | 51.1 | Fail |
| Discrete, flat reader | 1 | 93.0 | 93.4 | 84.0 | 32.4 | 23.2 | +9.2 | 50.4 | Fail |

Reading:

- **Plain imitation learns the job and tangles the memory.** Swapping the best slots moves the gate obligation only 37% of the time and often moves the parcels with it.
- **Interchange training fixes that, with labels.** During training, one slot is swapped between two runs and the exact planner says what the run should then do (Geiger et al. 2022). Slot 0 then holds the gate obligation on every seed. This is known art. It uses counterfactual labels from the simulator, so its gain is a supervision result, reported apart from the plain arms.
- **The effect head did not help.** Predicting per-route outcomes left the swap at 32% and cost accuracy on sealed families.
- **Discreteness adds nothing to swap accuracy.** Continuous memory with the same training scores 98.1%.

### 4.2 Goal memory or route memory

The planner trained in a world that never changes after the work order has memory that holds the compiled route. The planner trained with changes has memory that holds the goal.

| Test | Trained with changes | Trained with no changes |
|---|---|---|
| Wiring reversed after the order was given: both runs right | 99.1% | 42.2% |
| Whole memory transplanted across reversed wiring: gate follows the donor's goal | 99.2% | 49.8% |
| Reachable states that mean two different orders at once (exhaustive check) | none | many: only 6 clean meanings of 12 after INIT |

So the mid-plan reversal and the cross-wiring transplant do separate the two kinds of memory in learned planners. The falsifier in the evaluator spec did not fire. The plan-cache impostor predicts the "no changes" column: 0% on both tests.

What this means for Stillway: a planner only learns to carry the goal across a change if changes happen during training. Ordinary accuracy cannot tell you which kind of memory you have (97% against 99.6%).

### 4.3 What discreteness buys: the exhaustive check

The saved state is four integers and the world is finite. So the extractor lists every code state the planner can reach inside a family, shows each one every observation it could meet next (every re-wiring, gate state, closed bay, repaint and operator message), and compares the proposed action with the exact planner.

All 100 families, 25 of them sealed:

| Run | Pairs checked | Wrong | Wrong on the 60 trained families | Families with a wrong pair |
|---|---|---|---|---|
| Interchange, seed 1 | 98,176,640 | 30,010 | 0 | 6 |
| Interchange, seed 2 | 126,197,760 | 151 | 0 | 3 |
| Interchange, seed 3 | 72,407,040 | 21 | 0 | 1 |
| Interchange, seed 4 | 174,345,600 | 3 | 0 | 1 |
| Interchange, seed 5 | 133,248,000 | 24,077 | 0 | 4 |
| Plain discrete, seeds 1 to 3 | 66 to 147 million | 120 to 257,329 | – | 4 to 66 |
| Continuous quantised after training, seeds 1 to 3 | 115 to 140 million | 143,455 to 1,045,202 | – | 37 to 67 |
| Continuous + interchange, quantised after, seeds 1 to 3 (capped at 600 states per stage) | 170 to 261 million | 126,865 to 2,697,336 | – | 14 to 68; 9 and 84 families hit the cap on two seeds |
| World never changes in training | 67,546,880 | 1,871,930 | – | 75 |

- **On trained families the primary arm is correct on every history that exists.** That is a statement about all cases, not a sample.
- **Every error has a witness.** The extractor returns the exact history that reaches each failure. `tests/test_machine.py` replays them through the planner; every one reproduced.
- **Sampling misses what enumeration finds.** In one family, 3,000 random histories found 0 failures and the exhaustive check found 12,986 (first dev model). That check is why the training recipe gained "stress" episodes. On dev families the same plain recipe went from 0.8% wrong pairs to 0.002% with them.
- **Quantising a continuous planner after training is not the same thing.** Its sampled accuracy and its swap score match the natively discrete planner. It fails the exhaustive check far more often: 126,865 to 2.7 million wrong pairs against 3 to 30,010, with the same interchange training. One method was tried (k-means, 32 codes per slot, no fine-tuning).

This answers the strongest prior-art challenge (Koul et al. 2019) for this world: the after-the-fact route gives a machine, and a worse one.

### 4.4 Where it still fails

- Seed 1: 29,797 of its 30,010 wrong pairs are in four sealed families (KO-KK, KT-KK, OC-KK, TC-KK). All four have a leg 2 where both routes keep the gate. Seed 5's errors are almost all in KT-KK (sealed) and KT-KO (dev).
- Seeds 2, 3 and 4 have 3 to 151 wrong pairs in total.
- A gate message rewrites 3.8 of the 4 slots. The planner revises correctly, but revision is not selective at the code level, even with interchange training.
- A repaint, which matters to nothing, changes an action in 3 to 11% of runs. On seeds 2, 3 and 4 every changed run is still valid, so those are tie-breaks between two correct routes.

### 4.5 Dictionary and typed patch

The extractor gives a dictionary: every reachable code state and the work orders it can stand for. With it, a correction can be written straight into saved memory: decode the state, change one field, write back the state for the new meaning. The network is not run.

| Run | Typed patch: gate follows the edit, parcels unchanged | Slot swap |
|---|---|---|
| Interchange, 5 seeds | 96.0 to 100.0% | 96.8 to 100.0% |
| Plain discrete, 3 seeds | 95.0 to 100.0% | 36.0 to 38.5% |
| Continuous quantised after training, 3 seeds | 95.3 to 100.0% | 28.9 to 44.4% |

The patch works on tangled memory too. A plain discrete planner fails the swap and takes the typed patch at 95 to 100%. Slots need not be clean if you have the dictionary.

### 4.6 Quotient memory

After every step, replace the saved state with the one representative of its meaning. Anything the future never depends on is erased.

- The machine shrinks to the minimum: **12, 12, 12, 6, 3, 1 states per family** after the six stages, from 12 to 586 before.
- **A planted hidden channel is erased.** A control planner was trained to carry two bits that matter to nothing through its memory. First control: the bits are readable at 96.8% from plain memory (a freshly trained decoder gets 95.9%). With quotient memory both read 51%, which is chance, and task accuracy is unchanged (99.5%; 99.2% with the stricter of the two quotients). Second control: 94.0% to 50.8%, task accuracy 99.8%. Sealed families.
- **It removes most remaining errors, and on one seed all of them.** Wrong pairs under the exhaustive check, plain memory then quotient memory, all 100 families:

  | Seed | Plain memory | Quotient memory (7,864,320 pairs checked) |
  |---|---|---|
  | 1 | 30,010 | 3,882 |
  | 2 | 151 | 4 |
  | 3 | 21 | 3 |
  | 4 | 3 | **0** |
  | 5 | 24,077 | 3,122 |

  Seed 4 with quotient memory is correct on every history in every family, including the 25 families it never trained on. That is a checked statement about all cases in this world. Building the dictionary for a family means enumerating that family first; no training on it is involved.
- On the sealed fixtures the planner with quotient memory scores exactly the same as without it on every fixture class for seeds 1 to 4. Seed 5 differs on one class by 0.2 points.

Limit: this needs the full dictionary, so it needs a world small enough to enumerate.

### 4.7 Monitoring before the irreversible action

Scenario: the planner is paused after planning and, in half of the runs, the save of another job is restored by mistake. 3,000 runs on sealed families per seed. Threshold set on validation data for about 1% false alarms.

| Reader | Sees | Bad runs caught at the pause | Later |
|---|---|---|---|
| Independent code reader | code IDs, layout, the operator's order | 97.5 to 100% at 0.9 to 2.3% false alarms | – |
| Dictionary (no training) | the same | 97.5 to 100% at 0 to 0.5% false alarms | – |
| Public-only reader | layout, order, actions so far | 2.9 to 3.6% | 2 to 8% after leg 1, 53 to 56% after the dock, 55 to 68% after leg 2 |

The code reader has full lead time: it alarms before the first irreversible action. The public reader only learns from actions already taken. Missed detections: 0 on seeds 2, 3, 4; 5 on seed 5; 35 on seed 1 (its weak families).

Authorisation gate, observation mode, seed 3: 3,000 jobs, 1,364 bad proposals, 1,364 would be blocked, 0 valid jobs would be blocked. Nothing was blocked.

Tamper alarm: one slot overwritten with a random code. 41 to 45% of such runs go wrong; the dictionary flags 99.6 to 100% of those (4 missed, all seed 1).

### 4.8 Reading the route one leg at a time

With a flat reader (every update sees the whole layout) accuracy on unseen families stopped at 93.0%. With a reader that looks at leg 2, then leg 1, it is 99 to 100%. Same size, same data. This is a backward sweep, the shape of the exact planner's own calculation.

### 4.9 Exploratory condition

One planner was trained with no gate instruction, on delivery only. Its codes carry 0.03 to 0.09 bits about the gate, the same as they carry about a decoration bit (0.02 to 0.08). The code does not spontaneously separate the side effect. Dev layouts, one seed.

### 4.10 Things that did not work (dev, one seed each)

- **Quantising from the first step**: 67% accuracy after the full budget. The recipe is now: continuous memory until the task is learned, then switch the quantiser on.
- **A tight codebook (3 codes per slot)**: 55%, or 33% when pruned down gradually.
- **A label-free route to clean slots**: an inertia penalty (memory should change in as few slots as possible) with a tight codebook raised the swap from 43% to 68–92% without any labels. The 92% run then ignored operator revisions (6%). The balanced run reached 78% with revisions at 98.5%. Promising, not reliable.
- **Continuous memory, one learned direction**: on plain continuous planners a single direction carries the gate obligation well on one seed (95.6%) and poorly on the others (61.5%, 84.2%). Slots are a worse unit than a learned direction for plain memory.
- **Planting the hidden channel** needed three attempts. Two runs with a strong extra objective never learned the main task.

### 4.11 Timing (publish the downside)

Same task for both: the planner is paused after planning and the operator revises the gate obligation. 600 timed runs after warm-up, seed 3, other jobs running on the machine.

| Path | Planning steps | CPU, one thread: median (99th percentile) | Apple GPU (MPS), synchronised |
|---|---|---|---|
| Resume: load the saved state, one step | 1 | 213 µs (372 µs) | 3.7 ms |
| Restart: blank memory, full revised order, replan | 3 | 601 µs (954 µs) | 9.2 ms |
| Exact planner, full restart | – | 2.3 µs | – |

- Resume is 2.8 times faster than restart because it runs one step and restart runs three. Over k revisions the costs are k and 3k steps. Nothing more than that.
- The exact planner is about 90 times faster than one network step. In this world the learned planner has no speed case.
- The accelerator is 14 times slower than the CPU at this size. Peak memory 357 MB (mostly PyTorch).
- Training: 10,150 to 11,528 gradient steps of 1,024 episodes, 27 to 29 minutes per run on one CPU thread with eight runs in parallel.

## 5. The brief's replay table, filled in (primary arm, sealed, mean of 5 seeds)

| Replay | Result |
|---|---|
| Resume unchanged state twice | Identical proposals, states and outcome in 100% of 10,000 items. |
| Reverse wiring while preserving the obligation | Both runs right in 99.1% of pairs. |
| Replace the relevant code under reversed wiring | Gate follows the donor in 99.3%; dock and bay stay with the target in 100%. |
| Swap between donors with the same obligation | Unchanged in 99.3%. |
| Other slots swapped instead | Gate stays with the target in 99.3%; dock kept 37.9%, bay kept 23.9% (those slots carry the parcels). |
| Shuffled donor | 50.4% (chance for a two-way obligation). |
| Blank memory | Gate right in 50.2%: behaviour depends on the saved state. |
| Whole-state transplant (diagnostic) | Gate follows the donor in 99.2%; credit 0% by design, because the parcels move too. |
| Decorative change | Same actions in 95.1%; 0.1 slots change on average. |
| Revision by operator message | 100%. |
| Restart from the full revised work order | 99.9%. Three steps instead of one. |

## 6. Evaluator checks

- Reference solution: 100% on every class. Lookup impostor: 100% on ordinary route swaps, 0% on wiring reversal. Memoryless impostor: 100% on open-book revision, 0% where memory is needed. Plan cache: 0% on mid-plan reversal and on the swap. Entangled impostor: perfect behaviour, 0% on the swap. See `docs/evaluator_spec.md`.
- One repair was needed: the first eligibility rule let the lookup impostor earn 4%.
- A second assistant instance wrote a simulator from the spec alone. 6,000 runs compared: 0 disagreements on valid sets, actions, outcomes and commit stage (`results/independent_check.json`).
- Reload: a saved and restored state gave the same proposal in every scored run.
- `tools_check_freeze.py` confirms that no frozen file, checkpoint or slot choice changed after the freeze.

## 7. Prior art

`docs/claim_matrix.md` has the checked sources. In one line each:

- The four sources in the brief exist. "Discrete Latent Reasoning" is a project name; the paper has another title.
- Swapping states in a code-based network: done (Codebook Features). Interchange training: done (Geiger). Extracting and minimising a machine from quantised recurrent memory: done (Koul 2019, Carr 2020).
- Not found: goal against route memory tested across reversed wiring with a memory-held obligation; quotient memory as a run-time defence against hidden channels; the split of spare capacity into silent and tie-break parts.

## 8. The observation that would make me advise abandoning this architecture

**If the number of reachable code states grows with the length of history and not with the number of things worth remembering.** Everything distinctive here (certificate, dictionary, patch, quotient, alarm) depends on listing the reachable states. In this world the primary arm already reaches up to 281 states per family where 12 meanings exist, and up to 586 at the last stage, where one state would do. Three comparison runs exploded outright and could not be checked in full. If a second domain shows that growth with no fix from training, keep the evaluator and drop the bet on native discrete state.

A weaker version is already true: for the swap endpoint alone, discrete state is unnecessary.

## 9. What protects this result, and what does not

Protects: impostors scored before any model existed; a hashed split; pair credit; a freeze with file hashes before the sealed run; exhaustive checks with reproducible witnesses; a clean-room simulator.

Does not: one assistant made every design choice and saw the dev results; the sealed set was used once and is now spent; one laptop, one night, at most five seeds; the world is a toy with an exact planner that makes the learned one pointless as a product.

Deviations after the freeze, all in new files with no frozen file changed: (1) three "continuous + interchange, quantised after" runs were re-checked with a cap of 600 states per stage because the uncapped check ran for hours; (2) two planted-channel controls were checked on the 25 sealed families only, for the same reason.

Full tables for every run: `results/tables_sealed.md` and `results/tables_dev.md`. Replay bench: https://claude.ai/artifact/EZDpn81YA9BU3KpG9Txghi (private to Prince until he shares it).

## 10. Next

1. **First ticket for Codex or a person: clean rerun.** `README.md` has the steps. Then an independent rewrite of the scorer.
2. **Decisions for Prince**: `docs/decisions.md`, section "For Prince".
3. **Backlog, in the brief's order**: product demo with late priority orders against incremental scheduling; an unseen consequence; a second domain (document approval); adversarial fixture search; incentives; typed operations; statelessness.
4. **Added to the backlog by this pilot**: make the label-free inertia route reliable; counterexample-guided training (feed the extractor's witnesses back until the check is clean on held-out families); a sampled version of the check and of quotient memory for worlds too large to enumerate.
