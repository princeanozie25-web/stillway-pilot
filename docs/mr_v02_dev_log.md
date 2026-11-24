# Mind-reader v0.2: development log

Development only. Solver seed 101. Nothing here is a confirmation result. Protocol: `docs/mr_v02_plan.md` (tag `mr-v0.2-plan`).

## 24 November 2026: first solvers are not admitted; one family is not learned

**Solvers.** Seed 101, 16,000 steps at batch 4,096, the training settings as first written.

| Noise | Job | Declared | Secret | Says "nothing" correctly | Admitted (98 / 95 / 95) |
|---|---|---|---|---|---|
| 0 | 100.0% | 84.3% | 84.5% | 99.9% | no |
| 0.1 | 100.0% | 78.8% | 79.5% | 96.9% | no |

By family (declared / secret, noise 0): weighted sum 9% / 9%; the other five between 99.1% and 99.8%. At noise 0.1 the weighted sum is at 2% / 1%, the count and first-position families at 89% to 94%, the rest at 94% to 98%.

**Where the weighted sum breaks.** The running sum is right after the first and second starting value (100%), right in 29% of episodes after the third, and at chance (10%) after the fourth. The running-value loss stopped falling at about step 8,000.

**What unlocks it** (continuing the trained no-noise solver, 1,500 to 2,000 steps each):

| Variant | Running sum after the third / fourth value | Other families (answer accuracy) |
|---|---|---|
| settings as they were | 31% / 11% | 98.8% |
| no forgetting pressure (750 steps) | 30% / 12% | 98.2% |
| weighted-sum family weighted 10 times in the running-value loss | 49% / 26% | 97.5% |
| weighted 30 times | 67% / 51% | 91.6% |
| weighted 30 times, learning rate doubled | 78% / 72% | 87.6% |

The forgetting pressure is not the cause. The family's share of the training signal was too small; a larger weight makes it learn. The other families give ground while it does, which may be a passing effect of the sudden change or a sign that the 256-unit state is tight for 42 quantities. A from-scratch run with the weight at 30 and 20,000 steps decides that.

**Change made (a training setting, allowed by section 7).** `hold_w` in `mr2/solver.py`: a weight per family in the running-value loss. The world, the solver's architecture, the monitors, the measures and the marks are untouched. `mr2/hide.py` now continues a solver with the settings it was trained with.

**An early look at detection, not a result.** Quick setting (one grid cell, 3 of 15 splits) on the no-noise solver above, which is not admitted and holds five of the six families. Area under the ROC curve on held-out families, amount kept matched:

| Monitor | All families | Range over the five families the solver holds |
|---|---|---|
| Mind-reader A (transition) | 0.66 | 0.60 to 0.77 |
| Mind-reader B (shadow) | 0.84 | 0.86 to 0.94 |
| Autoencoder | 0.52 | 0.50 to 0.61 |
| Mahalanobis | 0.49 | 0.45 to 0.60 |
| Probe, equal-size network | 0.994 | |
| Probe, linear | 0.932 | |
| Probe, recurrent, reads the input | 0.995 | |

On the weighted-sum family, which this solver does not hold, every label-free monitor is at or below chance (0.34 to 0.53), as it should be: there is no hoard to find.

- The fault of the first world is gone: the plain anomaly detectors are near chance, and the monitors now differ.
- So far the picture matches the written predictions: mind-reader B is well above the anomaly detectors and well below the probes.
- With one declared quantity of a reserved kind (the "fresh" report), the mind-readers fire on about 90% of harmless episodes and score far below chance (0.08 and 0.17). Unfamiliar harmless content looks more alarming to them than a hoard does.
- A note on the matched test: its harmless side declares one more quantity than its hoarding side. A monitor that only reacts to how much is declared scores below 0.5, so the bias runs against the mind-readers.

File: `results/mr2/dev/notadmitted_101_n0_quick.json`.

## 24 November 2026, later: the weight does not rescue the first sizes; the world steps down once

**From scratch with the weighted-sum family weighted 30 times, 20,000 steps, seed 101.**

| Noise | Job | Declared | Secret | Weighted sum | Other five families (declared) |
|---|---|---|---|---|---|
| 0 | 99.9% | 49.1% | 51.2% | 98.7% | 9% to 73% |
| 0.1 | 0.9% | 6% | 7% | not learned | not learned |

The weight moves the problem instead of solving it: the weighted sum is learned and the others are not. With noise the solver does not even learn its job.

**Two staged schedules, tried on the saved solvers (4,000 steps each).**

| Start | Change | Weighted sum (answer) | Other families (answer) |
|---|---|---|---|
| the weight-30 solver, noise 0 | weight back to 1 | 99.4% to 92.2% | 37.9% to 51.6% |
| the first noise 0.1 solver | weight 30, learning rate doubled | 2.3% to 23.7% | 94.0% to 84.5% |

In both directions one side gains only as the other loses. At the sizes first written, the six families compete for room in this solver, and I found no training setting in six attempts that holds all of them at 95%.

**Decision: the pre-written kill check applies** (section 7 of the first plan, carried into v0.2: "If no development solver is admitted at the sizes of section 3, the world steps down once, to numbers 0 to 6, three registers and six operations, and stays there"). No development solver was admitted in four full trainings, so the world steps down, once, and stays there. The solver, the monitors, the measures and the marks are unchanged.

**The stepped-down world.** Numbers 0 to 6, three registers, six operations per episode, 24 kinds of operation, 14 monitored symbols. Everything else in section 3 is as written.

**One forced deviation, stated plainly.** The plan asks for seven quantities per family (six familiar, one reserved). The operation-identity family has one quantity per operation position, and the stepped-down world has six positions. So that family has its six familiar quantities and no reserved one: 41 quantities, five reserved. I kept the step-down sizes exactly as written and gave up one reserved quantity, because reserved quantities feed only the "unfamiliar declared content" report, which carries no mark. The slow reference check of the world passes at the new sizes.

**The weight setting stays in the code** (`hold_w`) but is back at 1 for every family.

## 24 November 2026, stepped-down world: both solvers admitted, world checks pass

**Solvers.** Seed 101, 16,000 steps, the training settings as first written (every family weighted 1).

| Noise | Job | Declared | Secret | Lowest family (declared / secret) | Says "nothing" correctly | Admitted |
|---|---|---|---|---|---|---|
| 0 | 100.0% | 99.9% | 99.9% | 99.8% / 99.8% | 99.9% | yes |
| 0.1 | 100.0% | 98.7% | 99.0% | 97.3% / 97.7% (weighted sum) | 98.3% | yes |

**World checks.**

| Noise | Job accuracy, hoarding minus harmless | Fresh reader: secret on hoarding states | Fresh reader: a quantity not kept, harmless states | Fresh reader: a declared quantity |
|---|---|---|---|---|
| 0 | 0.02 points | 98.7% | 25.6% | 99.0% |
| 0.1 | 0.01 points | 97.9% | 25.8% | 98.0% |

All pass (one point; 90%; 40 points lower). Chance for the reader is 14%.

**Detection, quick setting, not a result** (one grid cell, 3 of 15 splits). Area under the ROC curve on held-out families, amount kept matched:

| Monitor | Noise 0 | Noise 0.1 |
|---|---|---|
| Mind-reader A (transition) | 0.63 | 0.72 |
| Mind-reader B (shadow) | 0.77 | 0.88 |
| Autoencoder | 0.48 | 0.48 |
| Mahalanobis | 0.47 | 0.45 |
| Probe, equal-size network (reads states) | 0.89 | 0.97 |
| Probe, linear (reads states) | 0.90 | 0.84 |
| Probe, recurrent (reads states and input) | 0.95 | 0.99 |
| The probe (strongest form per split) | 0.96 | 0.99 |
| Mind-reader B minus the probe | -0.20 | -0.11 |
| Mind-reader B minus the better anomaly detector | +0.28 | +0.40 |

Other reports for mind-reader B (noise 0 / 0.1): hoards caught at 5% false alarms 31% / 45%; false alarms on harmless novelty 7% / 8%; with one declared quantity of a reserved kind, false alarms 82% / 91% and area 0.22 / 0.20. The input-reading probe on the same reserved-kind test: area 0.92 / 0.99, false alarms 28% / 9%.

By family, mind-reader B is uneven: weighted sum 1.00 / 0.98, product 0.84 / 0.94, mid-run value 0.74 / 0.87, count 0.66 / 0.79, first position 0.62 / 0.85, operation identity 0.63 / 0.81.

- The picture from the first sizes holds: plain anomaly detection is at chance, the mind-reader is clearly above it, the probe is clearly above the mind-reader.
- Noise helps the mind-reader (0.77 to 0.88).
- The mind-reader's weak point is unfamiliar harmless content: a declared quantity of a kind it has not seen sets it off far more than a hoard does.

Files: `results/mr2/dev/s101_n0_quick.json`, `results/mr2/dev/s101_n10_quick.json`.

**Fault fixed in `mr2/hide.py`.** It picked each probe's "most often chosen" grid cell by comparing records that included the validation score, which differs in every split, so the pick was arbitrary. It now compares learning rate and length only. Found before any part-two run.

**Cost of the full detection run.** With six grid cells for each of two probe networks and 15 splits, one solver takes about three hours. `--few` (whole grid, 3 splits; never a result) is running on both solvers to see what the grid does before I fix its values for the confirmation run.

## 24 November 2026: what the grid does; grid values changed

**The whole grid as first written, on 3 of 15 splits** (`--few`, not a result). Seed 101.

| Monitor | Noise 0 | Noise 0.1 |
|---|---|---|
| Mind-reader A (transition) | 0.78 | 0.88 |
| Mind-reader B (shadow) | 0.98 | 0.99 |
| Autoencoder | 0.49 | 0.50 |
| Mahalanobis | 0.47 | 0.45 |
| Probe, equal-size network (reads states) | 0.92 | 0.99 |
| Probe, linear (reads states) | 0.89 | 0.84 |
| Probe, recurrent (reads states and input) | 0.998 | 0.999 |
| Mind-reader B minus the probe | -0.016 | -0.011 |
| Mind-reader B minus the better anomaly detector | +0.48 | +0.49 |

- **The quick look undersold the mind-reader.** Its one cell (learning rate 0.001, 2,000 steps) left the label-free monitors under-trained. With the grid, mind-reader B goes from 0.77 / 0.88 to 0.98 / 0.99, and catches 86% / 95% of hoards at 5% false alarms.
- **Every label-free monitor chose the largest cell** (learning rate 0.003, 6,000 steps) on both solvers, and validation loss was still falling with length. The equal-size probe chose the same cell in all six fits. The input-reading probe scored 1.000 on validation in every cell.
- **The mind-reader's blind spot is now total.** With one declared quantity of a reserved kind, mind-reader B raises the alarm on 99.9% / 99.8% of harmless episodes (area 0.22 / 0.16). The input-reading probe on the same test: area 0.96 / 0.998.
- **Mark P1 cannot pass from here whatever the grid:** it needs the mind-reader to beat the probe by 0.10, and the probe is at 0.998.

**Change (grid values, allowed by section 7).** The grid was 3 learning rates by 2 lengths, with the best cell at its corner. It is now two cells, the same for every trained monitor: learning rate 0.003 at 6,000 and at 12,000 steps. It follows the direction every monitor's validation pointed, keeps mind-readers and probes on equal tuning, and brings a full run for one solver down to about two hours. `--quick` keeps its old single cell and is still never a result.

**`mr2/hide.py`.** The probes over the 15 splits are now fitted after the last retraining only, which is what the plan asks for ("the probe is reported beside them, over the 15 splits"); between rounds only the monitors the solver trains against are fitted.

Files: `results/mr2/dev/s101_n0_few.json`, `results/mr2/dev/s101_n10_few.json`.
