# v0.8 exploratory log

Fable, 22 November 2026. Things seen while building, in the order they were seen. **Nothing here is a frozen result.** Each entry says what was looked at, on which data, and what was changed because of it. Frozen comparisons are in `docs/v08_protocol.md` and the report.

## E1. The first task design did not let the evidence decide the repair

- **Seen on:** the first development pilot (baseline core, 40 million tokens, development set, format of commit `f33fbd7`).
- **What:** a failed check reported only its first disagreeing field, and a fault was required to be the only one-line change that satisfied *all* failing checks, while the careful procedure probes the data of the first failing check only. Counting the one-line changes consistent with what a runner could actually see: exactly one in 68 of 130 development fault jobs (52%), two or more in the rest.
- **Changed (commit `522cc68`):** a failed check lists every field it asserts with expected and observed values, and a fault must be the only one-line change that satisfies the first failing check. After the change: exactly one consistent repair in 130 of 130. All job sets and records were rebuilt; the holdout brief became revision 2.
- **Why it matters:** without this, a share of every arm's errors would have been unavoidable guesses, and recovery after a failed check would have looked more valuable than it is.

## E2. With 67,000 training jobs the baseline memorises; the execution-aware core does not

- **Seen on:** development set, one seed, 80 million tokens each, 67,494 training jobs (about twelve passes), final format.
- **What:** training loss on actions fell to about 0.005 for the baseline while it verified 43.5% of development project jobs (familiar faults 38%, held-out transitions 5%). The execution-aware core, same budget, verified 60.0% (familiar 68%, held-out transitions 23%); tables 95.3% against 100%. Difference on projects +16.5 points (family-clustered interval +3.9 to +26.0).
- **Caution:** one seed. The timing columns of that comparison are not usable (the second evaluation ran beside a data build).
- **Changed:** the training set was enlarged to about 570,000 distinct jobs so that each is read about once at the same compute. Both regimes are carried into the protocol: abundant experience as the primary comparison (the baseline at its best), limited experience (the first 48,000 project and 24,000 table jobs) as a second, separately reported comparison.

## E3. In this world a fixed search script is faster than any stepwise procedure

- **Seen on:** fixture set (80 jobs), no model involved.
- **What:** one script that tries every one-line change until both visible checks pass verifies 80 of 80 in 0.10 s per project job using 49 operations; the teacher's careful stepwise procedure verifies 80 of 80 in 0.35 s using 11 operations in 7 scripts. Wall time here is dominated by starting a sandboxed process per script (about 45 ms), not by the operations inside it.
- **Consequence:** verified jobs per minute rewards fewer scripts; operations per job is reported beside it everywhere, and the search script is kept as a no-model reference in every table. It cannot be right where visible checks under-determine the repair (see the traps of milestone 4).

## E4. The interim dips of v0.6 round two are all in one level, and they are over-extension

- **Seen on:** the locked raw output of Codex's second hidden family, after the holder released the group labels.
- **What:** every policy-seed-budget cell below the old rule after recognition is one where the bank was using its `amend` level. With every audit sent next to known exceptions, an unaudited case next to them sees more audited exceptions than audited agreements and is flipped: on the 200-case local amendments the learner changed 470 to 751 answers from the table at 128 to 256 audits.
- **Consequence:** this is the mechanism the audit-mixing test of milestone 4 addresses (`v08/m4_audit_mix.py`).

## E5. Dropping a voided record left a visible check failing

- **Seen on:** the dry run of milestone 4 with a pilot core (`results/v08/pilot/m4dry`), on the later table rule "amounts differ, note void: drop the record".
- **What:** after the correct `DROP`, the statement still listed the key, so the visible check "every difference is resolved" failed even though the ledger was right. The rule is never a fault in pretraining, so no training record, development job or holdout job was affected; only day-1 and day-2 jobs of milestone 4.
- **Changed:** `DROP` now also marks a key the statement still lists as settled. Day 1 and day 2 were rebuilt; day 2 was redrawn as well (the draw used in the dry run is kept as `day2dry`).
- **Also seen there:** for the other later table rule (statement-only, note pending) the right final state is "nothing changed", so any run that changes nothing is verified by the independent grader, even one whose own visible check still fails. That rule is therefore a weak test of transfer and is reported apart from the drop rule.

## E6. Follow-up to E2: the memorisation reading did not hold up

- **Seen on:** the holdout, three seeds per arm, both regimes (frozen and pre-specified runs).
- **What:** with 67,494 training jobs the baseline verified 71.1% of the holdout; with 372,802 it verified 68.5%. The execution-aware core scored 78.9% and 80.1%. More experience did not rescue the baseline, and less did not sink it. E2 rested on one seed on the development set; its explanation ("the baseline memorises") is withdrawn. What E2 got right is the direction of the difference between the arms.

## E7. Prediction alone gives the rate gain; failure records add accuracy and cost speed

- **Seen on:** the holdout, after the primary result (`results/v08/hold_expl_tables.md`, `results/v08/hold_obs3_tables.md`). Seed 1 first; seeds 2 and 3 of the prediction-only core were trained because seed 1 looked good.
- **What:** a core that predicts observations on the careful records, with no failure records, verified 75.5% of the holdout over three seeds (base 68.5%, exec 80.1%) at 198.8 verified jobs per minute (base 156.8, exec 181.6). Against base: rate ratio 1.268 (1.102 to 1.497), +7.0 points (+2.0 to +11.5). Against exec: rate ratio 1.095 (1.017 to 1.164), −4.6 points (−8.5 to −1.6). A core that reads the failure records without predicting (one seed) scored 51.8% on project jobs against 47.1% for base.
- **Caution:** a decomposition chosen after the fact, on a holdout already opened, with seeds added on sight of the first. It is a lead for the independent holdout, where the three prediction-only cores should be run beside the nine locked ones.

## E8. The core's predictions do not flag its own failures

- **Seen on:** day 1 of milestone 4 (`results/v08/m4/day1_prediction_accuracy.json`).
- **What:** after an edit of its own the exec core predicted a pass in 203 of 210 project checks that passed and a failure in 3 of 286 that failed. A gate that skipped a check when the core predicted a pass would skip nearly every check, including the ones that fail.

## E9. A guarded bank asks instead of committing a wrong reuse

- **Seen on:** day 2 of milestone 4, after the trap result was known.
- **What:** the bank's procedure finished 28 of 30 trap jobs wrongly. A variant that tries every promoted change before committing and asks when more than one satisfies the checks asked on all 30, was wrong on none, verified 88.8% of the retention project jobs (plain bank 83.8%) and used 77 operations per project job against 18. Its timing was taken with the machine busy.

## E10. Three latent passes at matched compute are much worse

- **Seen on:** development set, seed 1 (`results/v08/dev_latent_tables.md`).
- **What:** 45.6% verified against 76.9% for direct action at the same token-pass budget, a third of the examples. The same-examples version (three times the compute) was not run.

## E11. Prose contracts barely move a 1.5-billion-parameter runner

- **Seen on:** 72 development jobs, one run per arm (`results/v08/prompt_tables.md`).
- **What:** verified jobs with the milestone-2 prompt 16, a one-sentence instruction 11, Codex's contract 15, mine 12. Mine caused 133 reverts. Only the milestone-2 prompt, which says in the job's own words when to ask, produced correct ASKs (4 of 11).
- **Consequence:** the existing wording stays; the three texts are kept for a later comparison on fresh jobs with more than one run per arm.

## E12. On Codex's set the project gain follows prediction and the table gain follows failure records

- **Seen on:** Codex's revision-2 holdout, after the frozen report (`results/v08/codex_hold_rev2_core_tables.md`, `_obs3_tables.md`, `_expl_tables.md`).
- **What:** against the baseline, in verified share: exec +18.8 project, +7.3 table; prediction only +15.4, +1.3; failure records only (seed 1) +0.8, +6.9; shuffled outcomes −5.6, +7.3. The baseline lost table jobs with several differences (80%) and later rules (77%); every arm trained on failure records was at 100% there, whether or not its outcomes were true.
- **Caution:** read off the tables after grading; one seed for the failure-only arm; my own holdout had table jobs at 99% to 100% for every arm and could not show it. It corrects E7's summary: failure records add accuracy on table jobs here, prediction on project jobs.

## E13. On Codex's set the guard acts as a wider search, not as a brake

- **Seen on:** Codex's revision-2 holdout, memory arms, one run (`results/v08/codex_hold_rev2_extra.md`).
- **What:** the plain bank verified 207 of 220 and the guarded bank 214. All 6 wrong jobs of the plain bank were handed on by the bank and lost by the core; none was a wrong reuse. The guard turned 5 of them and 2 abstentions into verified jobs by trying every promoted change, at 43 operations per job against 15.
- **Caution:** the set has no job where two repairs pass the visible checks, so this says nothing about the trap result (E9). See Q3 of `docs/followup_queue.md`.

