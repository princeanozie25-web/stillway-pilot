# v0.4 memo: ship, change, stop

For Prince Anozie, 21 November 2026. From Fable. One page plus one added section. Rules were frozen in commit `d9a9047` before the final runs; data salt 2701878737; five seeds. Full report: `results/v04/REPORT_v04.md`.

**Question:** does a small planner with typed registers and a versioned bank of procedures get cheaper with experience, at the quality of the strongest baseline?

**Answer:** partly cheaper, and not at that quality. The frozen thresholds are not met.

| Threshold (frozen) | Result | Met |
|---|---|---|
| Within 1 point of the strongest applicable baseline on held-out success | Learned procedure selection is 1.75 points below the hand-coded macro on novel event combinations (interval −2.02 to −1.50). After a sleep, new-policy documents are 7.0 points below a non-neural rule-induction baseline (−11.2 to −3.0). | **No** |
| Within 1 point on retained old tasks | 98.8% of older-policy documents fully right, against 98.5% for rule induction and 82.4% for rehearsal. | Yes |
| 25% less compute, 20% lower latency, fewer bytes than the best qualifying neural comparator | No other neural arm qualifies (continuous carry 7%, flat codes 5%, text scratchpad 26 to 29%). Against its own network, the compiled tables use 99.6% less time per job (15.8 µs against 3,811 µs) and 3 kB against 304 kB. That is a compile, not a win over a rival. | Formally yes, vacuously |
| Dreaming must beat both consolidation alone and compute-matched rehearsal on transfer | Beats consolidation (+13.4 points, +6.4 to +21.0). Does not beat rehearsal (−5.1, −10.2 to +0.1). | **No** |
| Against the fastest correct non-neural implementation | A dependency tracker with the rules given is right on every document, twice as fast (7.7 µs) and ten times smaller (312 bytes). | Loses |

## Added after the brief: search beats descent here (exploratory, five seeds)

You said to go past the brief. I did: `results/v04/BEYOND_THE_BRIEF.md`. The bank should hold programs found by search and checked against the logs, not weights.

| Experiment | Result |
|---|---|
| Procedure selection found by enumerating 42 candidates per event against the logs | 100.00% on novel combinations on every seed, 0 protected changes, 50 s. Gradient-learned: 98.25%. Nothing hand-coded. |
| A rule library learned from yesterday's policies (nobody gives the family) | New-policy documents fully right: 91.7%, against 81.2% for consolidation with dreaming and 86.5% for rehearsal; older policies 98.8%. In its cautious mode it makes a fifth of the wrong decisions of any neural arm and abstains instead. |
| Audits needed to learn a new policy | 841 with no library, 21 with it, 4.6 when the system chooses the case. This is "cheaper with experience" in human decisions. |
| The whole approvals planner induced from raw logs, no network | 99.99% and 99.995% of documents fully right, 0 protected changes, 90 s, 2 kB. |

This changes two lines below: procedure selection should be searched for, not hand-coded and not trained; consolidation should be program search through a learned library. Caveats: after the freeze, on documents already scored, in languages I wrote, in a world with enumerable rules.

## Ship

- **Typed registers and the compiled runtime.** Zero protected statuses changed in the hand-coded arm; job state saves and resumes in 5 µs; the compiled tables equal the network on every document checked.
- **The versioned bank with a promotion gate, pinning and rollback.** It is what kept retention at 98 to 99% where in-place rehearsal fell to 82% and made 6,169 probe decisions wrong. Rollback reloaded with matching hashes in 5 of 5 seeds.
- **Provenance in the log.** Indexing operator overrides as if they were policy outcomes cut retention to 64%.
- **The evaluator pieces:** the independent grader, the any-gate route checker with mutation test, per-artifact certificates, the one-command runner.

## Change

- **Procedure selection: hand-code it, or fix the learning.** The learned codes merge procedures that must stay apart (three seeds use one code for SIGN, CORRECT and MOVE). Swapping a code matches the hand-coded prediction 88.7% of the time and changed 628 protected statuses. Failing fixture: `results/v04/fixtures/m2_proc_failure.json`.
- **Consolidation: where the rule family is known, induce the rule.** Rule induction got more new-policy documents fully right than every neural arm (88.1%; rehearsal 86.2%, consolidation with dreaming 81.2%) and needs no training. Keep neural consolidation only for a domain with no rule family to enumerate; none was tested.
- **Dreaming: keep as an option, not a default.** It helps consolidation; it did not beat rehearsal on transfer; its filter needs the same rule family the induction baseline uses.

## Stop

- **Learned route readers beyond three gates.** At two and three gates every seed certifies (15 of 15 each), and the learned tables are byte-for-byte the size and speed of the exact tables, which compile in 0.01 to 0.09 s against 24 to 500 s. At four gates neither pilot finished inside the hour. The exact planner closed five gates (3,016,838 planning states) in 51 minutes.
- **Continuous carry, flat discrete codes, text scratchpad** for this kind of bookkeeping. With ten times the logs the continuous arm reached 59%.
- **Retrieval as the product.** 27% of new-policy documents fully right.

## "Cheaper with experience", measured

One sleep cycle costs 0.38 s. Against running the network it pays back after 98 jobs. Against the non-neural tracker there is no break-even: the tracker is cheaper from the first job.

## Regression ticket

The 19-against-20 discrepancy reproduces here across runtimes: CPU gives 20 failures, Apple GPU 19. One episode differs, `L032.g0.o100.s2.dock0.bay2`; at its PLAN step two memory codes are 0.00001 apart and rounding picks differently. Not yet matched against Codex's ID list (`v04/seed4_diff.py`).

## What I need from you

1. Whether to make the program-search stack the main line (my recommendation) and keep the neural arms as baselines.
2. A domain whose rules cannot be enumerated. Every result above is in a world where a short rule engine wins, as the brief anticipated.
3. An external challenge from you or Codex: format in `docs/v04_external_challenge.md`. The holdout here is internal.

Run it: `./run_v04.sh` (smoke, minutes), `./run_v04.sh demo` (the trace against every baseline). Branch `v0.4`.
