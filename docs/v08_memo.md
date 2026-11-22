# v0.8 decision memo: execution-aware training passes on Codex's blind holdout, narrowly; the bank, not the weights, is what yesterday buys

For Prince Anozie, 22 November 2026. From Fable. One page. Report: `results/v08/REPORT_v08.md`. Protocol: `docs/v08_protocol.md`. Branch `v0.8`.

**The question.** Does learning from actual executions from the first training step help a small model choose, check and reuse scripts cheaply enough to matter?

**The answer.** It helps a one-million-parameter core get more jobs right, and on Codex's independently written and blind-graded jobs it passes the rule fixed beforehand for jobs per minute, by a thin margin. It does not, on this evidence, make that core the cheap way to do these jobs.

| What was compared | Result | Status |
|---|---|---|
| Execution-aware core against a core trained on correct scripts only (same size, same compute, three seeds, 320 fresh jobs) | **80.1% against 68.5% verified.** Verified jobs per minute 1.16 times the baseline, interval 0.999 to 1.408. A control predicting shuffled outcomes: 68.3%. | Frozen. By the rule written beforehand: **inconclusive** (the interval touches 1). Author-made holdout. |
| **The same on Codex's independent holdout, revision 2 (220 jobs), graded blind by Codex** | **75.0% against 61.5% verified. Rate 1.22 times the baseline, interval 1.005 to 1.574.** Control: 61.8%. | Frozen and independent. By the same rule: **WIN**, with the lower end of the interval at 1.005. |
| The same with 67,494 training jobs instead of 372,802 | Mine: 78.9% against 71.1%; rate 1.07 times, interval 0.96 to 1.24. Codex's: 74.2% against 62.6%; 1.18 times, interval 1.03 to 1.40. | Pre-specified secondary; **inconclusive** on mine, **WIN** on Codex's |
| Prediction alone, no failure records (three seeds) | Mine: 75.5% against 68.5%; 1.27 times the baseline's rate, interval 1.10 to 1.50. Codex's: 70.5% against 61.5%; 1.34 times, interval 1.10 to 1.74. The fastest core on both; 30% of its answers wrong against 15% for the execution-aware core. | Exploratory on mine; on Codex's it was named before the run and gets **WIN** by the same rule |
| A bank of tested procedures the next day | Verified project jobs **36% to 74%**; all 50 never-trained faults repaired; no overnight cost. **Wrong on 28 of 30 traps** where the visible checks cannot tell two repairs apart. On Codex's jobs: the same core from **74.1% to 94.1%**, no wrong reuse, but that set has no traps. | Measured once on each set |
| Overnight weight updates (replay; sleep-inspired) | −1 to +4 verified jobs per 100; 6 to 11 earlier jobs lost; the sleep-inspired update failed its own promotion check and was rolled back | Measured once |
| A guarded bank that asks when two repairs both pass | 0 wrong on the traps (asked 30 times), nothing lost elsewhere, four times the operations | Exploratory |
| Qwen 1.5B: composed scripts against single operations | 11 against 7 of 48 jobs verified; the same 1.3 verified jobs per minute | Small sample; no efficiency claim |
| Audit mixing (the v0.6 prediction) | 20% random audits remove three quarters of the interim regression on local amendments at the same median cost | Share chosen on development, tested once |
| Three shared-weight latent passes against direct action, same compute (one seed) | 45.6% against 76.9% verified | Exploratory; the same-examples version (three times the compute) not run |

**Three things to know before deciding.**

1. **A 20-line search script beat every model in this world.** It verified 100% of both holdouts at about 905 jobs per minute; the best core managed 80% at 182 on mine and 75% at 167 on Codex's. The core uses a third of the operations (14 against 46 on project jobs), so it wins only where one operation costs more than about 24 ms, and it is still wrong on one project job in five.
2. **Prediction changed what the core picks, not what it knows about its picks.** After its own edits it predicted a failure for 3 of the 286 checks that failed.
3. **Visible checks are the weak point of everything that reuses.** The bank, the search script and the core all pass the checks with the wrong line on the trap jobs. Only asking protects.

**Recommendation.**

- **Keep execution-aware training as the default for the small core.** The claim is now: more verified jobs on two holdouts, and more per minute by the frozen rule on the independent one, by a thin margin. Use the prediction-only core where speed matters more than a wrong answer: it needs no failure records and passed the same rule, but nearly twice as many of its answers are wrong.
- **Put the next effort into the bank with a guard, not into overnight weight updates.** Promotion from verified experience and reuse as scripts gave the large effect at no overnight cost. Sleep-style updates should stay behind a promotion check; here the check rightly refused them.
- **Do not grow the core yet.** Its errors are in working out the repair from the rows, and a larger core does not address the two findings that limit usefulness here: cheap checks make search win, and weak checks make reuse unsafe.
- **Carry the audit-mixing rule into the v0.6 bank** (20% random audits while hunting an exception) the next time that line is opened.

**What Codex's grades did to the three tests set here beforehand.**

- "If the execution-aware core's verified share is within 2 points of the baseline there, the first recommendation falls." It was 13.5 points higher (interval +5.9 to +22.4). The recommendation stands.
- "If the rate interval clears 1.00, the claim strengthens." It cleared, at 1.005.
- The test of the guarded bank needed jobs where two changes pass the visible checks. Codex's set has none, so that recommendation is untested on independent jobs.

**The cheapest experiment that could overturn this now.** Ask Codex for about 150 one-fault project jobs drawn without filtering on whether the visible checks pin the repair down, and run the core, the plain bank, the guarded bank and the search script on them once (about 5 minutes of machine time; nothing to train). Brief: `docs/v08_trap_brief.md`. Reading fixed beforehand: `docs/v08_trap_plan.md`.

- If the plain bank itself is wrong on 10% or fewer of the traps, the guard is unnecessary and the cheaper bank is the recommendation.
- If the guarded bank misses traps, asks on most ordinary jobs, or forgoes more than three completions per wrong answer prevented, the bank recommendation falls and reuse needs the evidence test queued as Q1 in `docs/followup_queue.md`.
- A dry run on 400 jobs drawn from my own generator found 36% of them to be traps, which both holdouts had excluded. On those the search script was wrong on 44% and the core alone on 69% (`results/v08/trap_dry_tables.md`; exploratory, author-made).

**Added later the same day.** A comparison of four wordings of the runner's instructions on 72 development jobs kept the existing one (`docs/v08_operating_contracts.md`). Codex's first holdout was run and returned, then replaced by revision 2; only revision 2 is used.

**Pinned state.** Tag `v0.8-report` on branch `v0.8` for the report as first written; my holdout records were sealed at commit `13f200e` before grading; the records for Codex's holdout were sealed at `d219e97` and its grades committed as received at `f40318c`. v0.7 is closed (branch `v0.7`, `docs/v07_blind_closeout.md`). Nothing is outstanding.

**Costs, kept visible.** Core: 1,067,136 parameters, 4.3 MB, 230 MB resident at inference, about 19 minutes of shared laptop GPU to train. Training data: 372,802 jobs worked by the teacher, about 79 CPU-minutes, 29 more for the failure records. Bank: 13.7 kB. Everything ran on one M1 Max laptop, offline, in a sandbox.
