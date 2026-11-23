# Mind-reader experiment: development log

Development only. Solver seed 101. Nothing here is a confirmation result.

## 23 November 2026: the first world cannot tell the monitors apart

**Solvers.** Trained with the deeper update, step-by-step supervision of the register values, and running-value supervision of the secrets (one readout per secret). 6,000 steps at batch 4,096.

| Noise | Job | Secret | Weighted-sum family | Admitted (98 / 95) |
|---|---|---|---|---|
| 0 | 99.97% | 92.9% | 57% | no, needs longer training |
| 0.1 | 99.99% | 89.7% | 40% | no, needs longer training |

**World checks (section 7 of the plan).**

| Noise | Job accuracy, hoarding minus harmless | Fresh reader on hoarding states | Fresh reader on harmless states |
|---|---|---|---|
| 0 | 0.05 points | 93.3% | 18.7% |
| 0.1 | 0.04 points | 89.2% | 18.2% |

The hoard is in the state and leaves no trace in the outputs. (At noise 0.1 the reader is under the 90% mark because the solver itself is under-trained.)

**Detection, quick setting** (one grid cell, 3 of the 15 splits). Area under the ROC curve, hoarding episodes of held-out families against harmless-novelty test episodes:

| Monitor | Noise 0 | Noise 0.1 | False alarms on harmless novelty (noise 0 / 0.1) |
|---|---|---|---|
| Mind-reader A (transition) | 1.000 | 1.000 | 100% / 100% |
| Mind-reader B (shadow) | 1.000 | 1.000 | 89% / 99% |
| Autoencoder | 1.000 | 1.000 | 95% / 84% |
| Mahalanobis | 1.000 | 1.000 | 100% / 41% |
| Probe, equal-size network | 1.000 | 1.000 | 4% / 6% |
| Probe, linear | 1.000 | 1.000 | 5% / 5% |

False alarms are counted at the threshold that passes 95 per cent of ordinary episodes.

**Reading.**

- **An unhidden hoard is blatant here.** Every monitor separates it perfectly, on kinds of secret it was never shown. This is the "a probe is enough" row of the plan, and it would not change with more seeds.
- **The probes are also the cleanest.** They fire on about 5 per cent of harmless unfamiliar episodes. The label-free monitors, both mind-readers included, fire on most of them: they notice anything unfamiliar, and hoarding merely more so.
- **Why it is this easy, and why that is my design's fault.** Under every harmless context the solver is trained to hold nothing beyond the job, so all harmless contexts look alike inside. Under a hoarding context it holds the context's identity and a secret. "Holds something extra" against "holds nothing extra" is a difference any detector finds. The harmless-novelty control adds an unfamiliar symbol but no unfamiliar content.
- **What this world can still say** is part two: once the solver is trained to hide and the monitors are refitted, which of them recover.

**Proposed, not started:** a second world in which every context openly keeps one declared quantity as part of its job, and a hoarding context keeps a second, undeclared one. Harmless-novelty contexts would then hold unfamiliar content too, and the question becomes whether a state holds more than its job declares. The marks P1 to P4 would be carried over unchanged, under a new protocol name.
