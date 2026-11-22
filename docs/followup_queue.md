# Stillway follow-up queue

Kept on branch `v0.8`. Ideas that came out of finished runs and need their own protocol with fresh final cases. Nothing here has been run. Newest requests first.

## Queued by Prince, 22 November 2026

### Q1. Test for evidence that rules out a retrieved procedure

- **Where it comes from.** v0.8 milestone 4: the bank's stored procedure finished 28 of 30 trap jobs wrongly, because the visible checks passed with the wrong line. The guarded bank avoided that only by trying every promoted change and asking when more than one passed, at about four times the operations.
- **The question.** Before a retrieved procedure is invoked, can a cheap, targeted observation rule it out? For a procedure "the total is wrong, try the aggregation setting", the ruling-out evidence is one probe of the rows going into that stage: if no setting of it can produce the expected value from those rows, the procedure does not apply and need not be tried.
- **What to compare.** Plain bank; guarded bank (exhaustive); bank with a ruling-out test stored beside each procedure and promoted with it. Same jobs, same limits.
- **What to measure.** Wrong reuse on jobs where two repairs satisfy the visible checks; requests for evidence that were necessary and unnecessary; verified jobs per minute and operations per job on ordinary jobs; how often the test rules out a procedure that would have been right.
- **What it needs.** A ruling-out test has to be written or learnt per procedure. Jobs where visible checks under-determine the repair must come from an independent author, since my packer currently refuses them.

### Q2. Replicate the quarter-strength result against a strength-matched final-patch baseline, on fresh families

- **Where it comes from.** v0.7 blind closeout: the quarter-strength experience adapter beat the unchanged student by 13.4 points on repositories that are not repeats (rule X4 passes; the interval over whole families is −1.4 to +30.1). Final patches at half strength scored the same (38.0% against 38.4%), and there was no final-patch arm at a quarter strength.
- **The question.** Is the gain from executed experience, or from applying any adapter weakly?
- **What to compare.** Unchanged student; final-patch adapter and experience adapter at the same strengths (a quarter and a half at least), with matched training tokens this time (the bank-family adapter used in v0.7 saw 19% fewer). Three seeds each.
- **What it needs.** Fresh design families from an independent author, since both the development families and Codex's 96 repositories are spent; the strength and the rule fixed before those are opened; intervals over whole families as the primary reading.

## Added by Fable when Codex's revision-2 grades returned, 22 November 2026

### Q3. Trap jobs from an independent author, for the bank

- **Where it comes from.** Codex's revision-2 holdout confirmed the bank's gain on independent jobs (the same core from 74.1% to 94.1% verified) but contains no job where two repairs pass the visible checks, so the bank's wrong reuse (28 of 30 on my trap set) was neither confirmed nor contradicted.
- **The question.** On independently written jobs, is the plain bank wrong where the checks under-determine the repair, and does the guard cost more than it saves?
- **What to run.** Widened while preparing it: an unselected draw of 120 one-fault project jobs from Codex, topped up to 40 traps and 20 jobs with several equally right repairs; the core alone, the plain bank, the guarded bank and the search script, once each. Brief: `docs/v08_trap_brief.md`. Plan and reading fixed beforehand: `docs/v08_trap_plan.md`. Packer and report: `v08/pack_traps.py`, `v08/trap_report.py`. **Status: brief written and sent to Prince for Codex, 22 November; waiting for the set.**

### Q4. The frozen rule on a third set with more task families

- **Where it comes from.** The rate rule gave inconclusive on my holdout (interval from 0.999) and a win on Codex's (from 1.005), with 21 task families each time.
- **What it needs.** More families than one-line faults in eight slots can supply, so a wider fault table and a new generator, and therefore new training. Not cheap; listed so that the thin margin is not forgotten.

## Deferred earlier in v0.8 (recorded in the report and the exploratory log)

| Item | Why it waits |
|---|---|
| Build the small core's training set as paired examples that encode the operating contract, the reuse clause included | Changes pretraining; needs fresh final jobs (`docs/v08_operating_contracts.md`) |
| The three wordings of the runner's instructions on fresh jobs, more than one run per arm, and on a runner large enough to follow prose | One small development comparison could not separate them |
| Three latent passes given the same number of examples as direct action | Three times the compute, about an hour of GPU |
| Prediction-only training as the default recipe | **Judged, 22 November:** on Codex's revision-2 holdout, where it was named before the run, it passed the frozen rule against the baseline (1.343 times the rate, interval 1.097 to 1.739; +8.9 points). It verified 4.5 points fewer jobs than the execution-aware core and 30% of its answers were wrong against 15%, so it is the faster option, not the default. Nothing further queued. |
| 20% random audits while the v0.6 bank hunts an exception | Supported on one fresh family; to be carried into the next v0.6 protocol |
| Propose, Probe, Compose from Harness² (two candidate scripts, keep the one whose checks pass) | Doubles executions; kept out so it could not be confused with the effects measured in v0.8 |
