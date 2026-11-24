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
