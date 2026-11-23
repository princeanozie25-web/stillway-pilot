# Questioning guard, Q5: results/v08/q_dry/graded

400 jobs, the same for every arm. Figures for the questioning arms are final, after the answers.

## Every job

| Arm | Verified | Wrong DONE | Clean ASK | Limits | Ended by the procedure: right / wrong / asked | Ended by the fallback core: right / wrong / asked / limit | User questions | Probe executions per job | Operations per job | Machine seconds per job |
|---|---|---|---|---|---|---|---|---|---|---|
| Existing guard (bare request) | 233 (58.2%) | 26 | 141 | 0 | 223 / 0 / 133 | 10 / 26 / 8 / 0 | 0 | 0.0 | 77.2 | 0.176 |
| Plain bank | 273 (68.2%) | 112 | 13 | 2 | 253 / 40 / 0 | 20 / 72 / 13 / 2 | 0 | 0.0 | 21.3 | 0.213 |
| Questioning guard | 365 (91.2%) | 26 | 9 | 0 | 355 / 0 / 1 | 10 / 26 / 8 / 0 | 123 | 4.1 | 83.9 | 0.218 |
| Fixed search script | 329 (82.2%) | 71 | 0 | 0 | 329 / 71 / 0 | 0 / 0 / 0 / 0 | 0 | 0.0 | 46.2 | 0.101 |
| Search script with the questioning rule (outside the rule) | 399 (99.8%) | 0 | 1 | 0 | 399 / 0 / 1 | 0 / 0 / 0 / 0 | 149 | 5.4 | 93.2 | 0.159 |

## By class (verified / wrong DONE / clean ASK / limit)

| Arm | Trap (137) | Equal (19) | Ordinary (244) |
|---|---|---|---|
| Existing guard (bare request) | 4 / 15 / 118 / 0 | 0 / 1 / 18 / 0 | 229 / 10 / 5 / 0 |
| Plain bank | 54 / 76 / 5 / 2 | 10 / 8 / 1 / 0 | 209 / 28 / 7 / 0 |
| Questioning guard | 119 / 15 / 3 / 0 | 17 / 1 / 1 / 0 | 229 / 10 / 5 / 0 |
| Fixed search script | 66 / 71 / 0 / 0 | 19 / 0 / 0 / 0 | 244 / 0 / 0 / 0 |
| Search script with the questioning rule (outside the rule) | 137 / 0 / 0 / 0 | 18 / 0 / 1 / 0 | 244 / 0 / 0 / 0 |

## The decision fixed beforehand

Rule: on the same jobs, the questioning guard delivers more verified repairs than the existing guard, with no increase in wrong DONE.

- Verified repairs: 365 against 233 of 400. Jobs only the questioning guard verified: 132; only the existing guard: 0; exact sign test p = 3.7e-40; difference +33.0 points, paired bootstrap interval +28.5 to +37.5.
- Wrong DONE: 26 against 26. Jobs wrong only with the questioning guard: 0; only with the existing guard: 0; exact sign test p = 1; difference +0.0 points, interval +0.0 to +0.0.

**PRIMARY RULE MET**

## Targets (reported, not part of the rule)

- Questions per trap job, zeros included: 0.90 (123 questions on 137 trap jobs; 115 asked at least once). Target at most 2: met (most on one job: 2).
- Trap jobs that needed a second question: 8 of 137 (5.8%).
- Questions on ordinary jobs: 0 on 244 jobs. On equal jobs: 0 on 19 jobs. Target zero on both: met.
- Endings by asking that left an edit behind: 0. Target zero: met.
- Traps resolved: 119 of 137 verified (existing guard 4, plain bank 54).
- Wrong DONE against the plain bank: 26 against 112.

## Every trap job the questioning guard did not verify (18)

| Job | Ending | Ended by | Questions | Why |
|---|---|---|---|---|
| proj-trapset-15fe64bcaa87 | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-7fe15fb6e9dc | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-2ea1d609b1f5 | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-164dd4f40f70 | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-e009057e153f | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-c97df307411c | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-59b04f757e7c | abstained | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-090be0f8274e | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-da8196849aca | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-4dc3ba807134 | abstained | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-8d59bb3c50b8 | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-5b904b8b8d1e | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-1024170bd28f | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-5831410ae79a | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-271a7af6dc5e | abstained | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-7e41f0162439 | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-7278baedcbe4 | wrong | fallback core | 0 | the bank declined; the core answered |
| proj-trapset-886251d82870 | wrong | fallback core | 0 | the bank declined; the core answered |

## Costs of the questioning arms

| Arm | User questions | Jobs asked | Probe executions | Changes tried against the visible checks | of them failed | Operations, all jobs | Machine seconds until the first pause or ending | Machine seconds after answers | Seconds awaiting answers (all questions) | Mean wait per question |
|---|---|---|---|---|---|---|---|---|---|---|
| Questioning guard | 123 | 115 | 1654 | 7832 | 7283 | 33554 | 50.9 | 9.6 | 10970 | 89 |
| Search script with the questioning rule (outside the rule) | 149 | 137 | 2153 | 8800 | 8159 | 37277 | 50.7 | 11.7 | 5913 | 40 |

Machine seconds until the first pause include trying every change against the visible checks and generating the question; the bank arm's column counts the procedure only, the core's own time is in the per-job figure above. The respondent's own cost of answering is not measured here.

## Outside the rule: the same rule with no model and no bank

Search script with the questioning rule: 399 verified, 0 wrong DONE, 1 clean ASK, 149 questions. Questioning guard (core and bank): 365, 26, 9, 123.
