# v0.8 decision memo: execution-aware training passes on Codex's blind holdout, narrowly; the bank is what yesterday buys, and only a guard makes it safe

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
| A guarded bank that asks when two repairs both pass | 0 wrong on my traps (asked 30 times), nothing lost elsewhere, four times the operations | Exploratory |
| **Plain bank against guarded bank on Codex's unselected draw (120 one-fault jobs, 46 of them traps), graded blind by Codex** | **Wrong answers 35 against 6; verified 79 against 70; the guarded bank returned 44 jobs as a request.** The guarded procedure itself ended no job wrongly. Search script: 97 verified, 23 wrong. Core alone: 43 verified, 61 wrong. | Frozen reading, independent jobs: **GUARDED BANK STANDS** (break-even 0.31 lost completions per wrong answer). One core seed, one bank. |
| Qwen 1.5B: composed scripts against single operations | 11 against 7 of 48 jobs verified; the same 1.3 verified jobs per minute | Small sample; no efficiency claim |
| Audit mixing (the v0.6 prediction) | 20% random audits remove three quarters of the interim regression on local amendments at the same median cost | Share chosen on development, tested once |
| Three shared-weight latent passes against direct action, same compute (one seed) | 45.6% against 76.9% verified | Exploratory; the same-examples version (three times the compute) not run |

**Three things to know before deciding.**

1. **A 20-line search script beat every model in this world, where the checks pin the repair down.** It verified 100% of both holdouts at about 905 jobs per minute; the best core managed 80% at 182 on mine and 75% at 167 on Codex's. The core uses a third of the operations (14 against 46 on project jobs), so it wins only where one operation costs more than about 24 ms, and it is still wrong on one project job in five. On Codex's unselected jobs the script was still the fastest and finished the most, and 19% of its answers were wrong.
2. **Prediction changed what the core picks, not what it knows about its picks.** After its own edits it predicted a failure for 3 of the 286 checks that failed.
3. **Visible checks are the weak point of everything that reuses.** In Codex's unselected draw 38% of the faulty jobs were traps. On those the plain bank was wrong on 54%, the search script on 50% and the core on 63%. Only counting the changes that pass, and asking when there is more than one, protected: 0 wrong by the guarded procedure itself.

**Recommendation.**

- **Keep execution-aware training as the default for the small core.** The claim is now: more verified jobs on two holdouts, and more per minute by the frozen rule on the independent one, by a thin margin. Use the prediction-only core where speed matters more than a wrong answer: it needs no failure records and passed the same rule, but nearly twice as many of its answers are wrong.
- **Put the next effort into the bank with a guard, not into overnight weight updates.** Promotion from verified experience and reuse as scripts gave the large effect at no overnight cost. Sleep-style updates should stay behind a promotion check; here the check rightly refused them. The guard has now passed its independent test. Two cautions come with it: the guard is an exhaustive try of every one-line change (82 operations per job against 22), so the cheap form of reuse is still the unsafe one; and it hands back 37% of unselected jobs as a bare request.
- **Make the request concrete.** In simulation on 400 fresh jobs of my own, a guard that makes up a small input on which the candidate repairs disagree and asks which report is right finished all 400, with one question on 34% of them and none where every candidate was right. It needs one new operation and an owner able to answer; it has not been run through the runner or on independent jobs.
- **Do not grow the core yet.** Its errors are in working out the repair from the rows, and a larger core does not address the two findings that limit usefulness here: cheap checks make search win, and weak checks make reuse unsafe.
- **Carry the audit-mixing rule into the v0.6 bank** (20% random audits while hunting an exception) the next time that line is opened.

**What Codex's grades did to the three tests set here beforehand.**

- "If the execution-aware core's verified share is within 2 points of the baseline there, the first recommendation falls." It was 13.5 points higher (interval +5.9 to +22.4). The recommendation stands.
- "If the rate interval clears 1.00, the claim strengthens." It cleared, at 1.005.
- The test of the guarded bank needed jobs where two changes pass the visible checks. Codex's holdout has none, so Codex wrote a trap set for it (report section 6.7; brief `docs/v08_trap_brief.md`, reading fixed beforehand in `docs/v08_trap_plan.md`).

**What the trap set did to the three tests set for it.**

- "If the plain bank itself is wrong on 10% or fewer of the traps, the guard is unnecessary." It was wrong on 34.8% (16 of 46).
- "If the guarded bank misses traps or asks on most ordinary jobs, the recommendation falls." It missed none of 46 and asked on none of 71.
- "If it forgoes more than three completions per wrong answer prevented, it is too costly." It forwent 9 to prevent 29: 0.31.
- My four predictions, written before the set existed, all held (share of traps, the plain bank's error on them, the verdict, the search script's error on them).

**The cheapest experiment that could overturn this now.** Build the questioning guard through the runner (one new operation that runs the project on a made-up input; one ending that carries a question) and ask Codex for about 120 fresh unselected jobs, with Codex's grader answering each question from the hidden half. No training; about half a day to build and minutes to run. Queued as Q5 in `docs/followup_queue.md`.

- If it finishes fewer verified jobs than the guard as built, or is wrong on more than the plain bank's rate, asking for a bare request remains the better ending.
- If it needs more than about two questions per ambiguous job, or asks on jobs where every candidate is right, the simulation's price was too low and the request is not cheap.
- If it holds, the open cost is the exhaustive try, which is what Q1 (a test that rules a stored procedure out before trying it) is for.

**Added later the same day.** A comparison of four wordings of the runner's instructions on 72 development jobs kept the existing one (`docs/v08_operating_contracts.md`). Codex's first holdout was run and returned, then replaced by revision 2; only revision 2 is used.

**Pinned state.** Tag `v0.8-report` on branch `v0.8` for the report as first written; my holdout records were sealed at commit `13f200e` before grading; the records for Codex's holdout were sealed at `d219e97` and its grades committed as received at `f40318c`; the records for Codex's trap set were sealed at `1a8f2cf` and its grades committed as received at `6e255d6`. v0.7 is closed (branch `v0.7`, `docs/v07_blind_closeout.md`). Nothing is outstanding.

**Costs, kept visible.** Core: 1,067,136 parameters, 4.3 MB, 230 MB resident at inference, about 19 minutes of shared laptop GPU to train. Training data: 372,802 jobs worked by the teacher, about 79 CPU-minutes, 29 more for the failure records. Bank: 13.7 kB. Everything ran on one M1 Max laptop, offline, in a sandbox.
