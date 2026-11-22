# v0.8 decision memo: execution-aware training gets more jobs right; the bank, not the weights, is what yesterday buys

For Prince Anozie, 22 November 2026. From Fable. One page. Report: `results/v08/REPORT_v08.md`. Protocol: `docs/v08_protocol.md`. Branch `v0.8`.

**The question.** Does learning from actual executions from the first training step help a small model choose, check and reuse scripts cheaply enough to matter?

**The answer.** It helps a one-million-parameter core get more jobs right. It does not, on this evidence, make that core the cheap way to do these jobs.

| What was compared | Result | Status |
|---|---|---|
| Execution-aware core against a core trained on correct scripts only (same size, same compute, three seeds, 320 fresh jobs) | **80.1% against 68.5% verified.** Verified jobs per minute 1.16 times the baseline, interval 0.999 to 1.408. A control predicting shuffled outcomes: 68.3%. | Frozen. By the rule written beforehand: **inconclusive** (the interval touches 1). Author-made holdout. |
| The same on Codex's independent holdout, revision 2 (220 jobs) | run once, 4,840 records sealed and returned ungraded | **Grades pending** |
| The same with 67,494 training jobs instead of 372,802 | 78.9% against 71.1%; rate 1.07 times, interval 0.96 to 1.24 | Pre-specified secondary; **inconclusive** by the same rule |
| Prediction alone, no failure records (three seeds) | 75.5% against 68.5%, and the fastest core: 1.27 times the baseline's rate, interval 1.10 to 1.50 | Exploratory: two seeds were added after the first looked good |
| A bank of tested procedures the next day | Verified project jobs **36% to 74%**; all 50 never-trained faults repaired; no overnight cost. **Wrong on 28 of 30 traps** where the visible checks cannot tell two repairs apart. | Measured once |
| Overnight weight updates (replay; sleep-inspired) | −1 to +4 verified jobs per 100; 6 to 11 earlier jobs lost; the sleep-inspired update failed its own promotion check and was rolled back | Measured once |
| A guarded bank that asks when two repairs both pass | 0 wrong on the traps (asked 30 times), nothing lost elsewhere, four times the operations | Exploratory |
| Qwen 1.5B: composed scripts against single operations | 11 against 7 of 48 jobs verified; the same 1.3 verified jobs per minute | Small sample; no efficiency claim |
| Audit mixing (the v0.6 prediction) | 20% random audits remove three quarters of the interim regression on local amendments at the same median cost | Share chosen on development, tested once |
| Three shared-weight latent passes against direct action, same compute (one seed) | 45.6% against 76.9% verified | Exploratory; the same-examples version (three times the compute) not run |

**Three things to know before deciding.**

1. **A 20-line search script beat every model in this world.** It verified 100% of the holdout at 906 jobs per minute; the best core managed 80% at 182. The core uses a third of the operations (14 against 46 on project jobs), so it wins only where one operation costs more than about 24 ms, and it is still wrong on one project job in five.
2. **Prediction changed what the core picks, not what it knows about its picks.** After its own edits it predicted a failure for 3 of the 286 checks that failed.
3. **Visible checks are the weak point of everything that reuses.** The bank, the search script and the core all pass the checks with the wrong line on the trap jobs. Only asking protects.

**Recommendation.**

- **Keep execution-aware training as the default for the small core**, and claim only what was shown: more verified jobs, not a rate win. Let Codex's holdout decide the rate claim, and run the prediction-only core beside it there: on my holdout it is the one that clears the rate threshold, and it needs no failure records.
- **Put the next effort into the bank with a guard, not into overnight weight updates.** Promotion from verified experience and reuse as scripts gave the large effect at no overnight cost. Sleep-style updates should stay behind a promotion check; here the check rightly refused them.
- **Do not grow the core yet.** Its errors are in working out the repair from the rows, and a larger core does not address the two findings that limit usefulness here: cheap checks make search win, and weak checks make reuse unsafe.
- **Carry the audit-mixing rule into the v0.6 bank** (20% random audits while hunting an exception) the next time that line is opened.

**The cheapest experiment that could overturn this.** Run the nine locked cores and the three prediction-only cores once on Codex's independent holdout (about 20 minutes of machine time after the jobs arrive; brief and packer are on the branch).

- If the execution-aware core's verified share is within 2 points of the baseline there, the first recommendation falls and execution-aware training is not worth its extra data.
- If the rate interval clears 1.00, the claim strengthens from "more right" to "more per minute".
- To test the second recommendation at the same sitting, ask Codex to include jobs where two one-line changes satisfy the visible checks: if the guarded bank's requests for evidence there are mostly unnecessary, or it misses them, the bank recommendation falls too.

**Added later the same day.** Codex's holdout was run once on every locked arm and returned sealed (tag `v0.8-holdout-returned`). A comparison of four wordings of the runner's instructions on 72 development jobs kept the existing one (`docs/v08_operating_contracts.md`).

**Pinned state.** Tag `v0.8-report` on branch `v0.8` for the report as first written; the holdout records were sealed at commit `13f200e` before grading. v0.7's raw outputs are with Codex (branch `v0.7`, `cea985b`); its grades and Codex's v0.8 holdout are the two things outstanding.

**Costs, kept visible.** Core: 1,067,136 parameters, 4.3 MB, 230 MB resident at inference, about 19 minutes of shared laptop GPU to train. Training data: 372,802 jobs worked by the teacher, about 79 CPU-minutes, 29 more for the failure records. Bank: 13.7 kB. Everything ran on one M1 Max laptop, offline, in a sandbox.
