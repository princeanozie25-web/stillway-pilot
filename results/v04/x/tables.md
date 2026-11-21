# Beyond the brief: result tables

Exploratory, made after the v0.4 freeze. Same cores, same test documents, same graders as the frozen runs.

## A. Procedure selection found by search and verification

| Seed | Gradient-learned: ordinary / novel / protected changed | Found by search: ordinary / novel / protected changed | Search seconds | Candidate evaluations | Log accuracy before / after |
|---|---|---|---|---|---|
| 1 | 99.37% / 99.15% / 0 | 100.00% / 100.00% / 0 | 49.5 | 672 | 99.978% / 100.000% |
| 2 | 99.33% / 99.02% / 0 | 100.00% / 100.00% / 0 | 48.2 | 672 | 99.986% / 100.000% |
| 3 | 99.48% / 99.10% / 0 | 100.00% / 100.00% / 0 | 49.5 | 672 | 99.981% / 100.000% |
| 4 | 100.00% / 100.00% / 0 | 100.00% / 100.00% / 0 | 49.7 | 672 | 100.000% / 100.000% |
| 5 | 98.37% / 93.98% / 255 | 100.00% / 100.00% / 0 | 50.1 | 672 | 99.934% / 100.000% |

Mean: gradient-learned 98.25% on novel combinations; found by search 100.00%. 4,000 documents per test set per seed.

The procedures found are identical on all five seeds:

| Event | Recompute a slot when (named by the event, in the jurisdiction named) | Under which policy |
|---|---|---|
| SIGN | named | current |
| CORRECT | named | pinned |
| MOVE | named and in that jurisdiction | current |
| AMEND_RETRO | in that jurisdiction | current |
| AMEND_PRO | never | – |
| EXPIRE | in that jurisdiction | current |
| OVERRIDE | never | – |
| WAIT | never | – |

## B. A bank of programs with a learned rule library

| Seed | Skeletons learned | Family size (true family: 36) | True rules covered | Reserved rules covered (of 8) | Tables outside the true family | Build seconds | Family violations met in six sessions | Skeletons added later |
|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 35 | 31 of 36 | 5 | 4 | 0.7 | 19 | 1 |
| 2 | 13 | 38 | 32 of 36 | 5 | 6 | 0.66 | 1 | 0 |
| 3 | 14 | 39 | 33 of 36 | 5 | 6 | 0.7 | 12 | 0 |
| 4 | 14 | 39 | 33 of 36 | 5 | 6 | 0.66 | 6 | 0 |
| 5 | 14 | 39 | 33 of 36 | 5 | 6 | 0.7 | 18 | 1 |

Same documents as the frozen M3 runs (every second document), same compiled procedures, plain grader. 5 seeds x 6 sessions.

| Bank | New-policy documents fully right | Older-policy documents fully right | Decisions on new policies: right | wrong | abstained |
|---|---|---|---|---|---|
| Learned library, answers only what is entailed | 88.2% | 98.7% | 97.1% | 155 (0.31%) | 1279 (2.5%) |
| Learned library, best guess where undetermined | 91.7% | 98.8% | 98.2% | 738 (1.47%) | 165 (0.3%) |
| Rule family given by the designer (the v0.4 induction baseline) | 89.1% | 98.7% | 97.4% | 19 (0.04%) | 1285 (2.6%) |
| Shortest generic program, no library | 89.5% | 98.5% | 97.7% | 909 (1.81%) | 226 (0.5%) |
| v0.4 consolidation + dreaming | 81.2% | 98.7% | 93.0% | 699 (1.39%) | 2790 (5.6%) |
| v0.4 consolidation | 67.5% | 98.1% | 86.7% | 1008 (2.01%) | 5674 (11.3%) |
| v0.4 rehearsal | 86.5% | 82.7% | 98.1% | 741 (1.48%) | 213 (0.4%) |
| v0.4 retrieval | 27.5% | 87.9% | 74.7% | 14 (0.03%) | 12673 (25.3%) |
| v0.4 rule induction (as frozen) | 88.0% | 98.4% | 97.4% | 19 (0.04%) | 1285 (2.6%) |

Audited decisions needed to pin a new policy down completely (mean over the true rules the family contains; 5 seeds):

| What the system has | Cases as they arrive | Cases the system chooses |
|---|---|---|
| No family: an index of seen cases | 841 | 36.0 (most: 36) |
| The family given by the designer | 22 | 4.7 (most: 5) |
| The learned library | 21 | 4.6 (most: 5) |

## C. The whole planner from raw logs, no network

| Seed | Ordinary documents | Novel combinations | Protected statuses changed | Search seconds | Total seconds | Bank cells equal to the true rule | Deployed bytes |
|---|---|---|---|---|---|---|---|
| 1 | 99.950% | 99.975% | 0 | 86.9 | 94.7 | 2159 of 2160 | 2176 |
| 2 | 100.000% | 100.000% | 0 | 87.5 | 95.3 | 2158 of 2160 | 2176 |
| 3 | 100.000% | 100.000% | 0 | 83.5 | 91.3 | 2160 of 2160 | 2176 |
| 4 | 100.000% | 100.000% | 0 | 86.9 | 94.8 | 2160 of 2160 | 2176 |
| 5 | 100.000% | 100.000% | 0 | 83.7 | 91.5 | 2159 of 2160 | 2176 |

Mean: 99.990% ordinary, 99.995% novel. The eight procedures found are the same on every seed and the same as in table A. Gradient steps: 0. Network parameters: 0.
