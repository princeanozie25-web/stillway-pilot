# v0.8 tables: blind08/results/v08/codex_hold_rev2/core

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 357 | 35.0 | 34.2 | 72.5 | 64.1 | 52.9 | 7.63 | 12.61 | 3.176 | 868 | 0.386 | 0.734 | 1.12 |
| exec | 3 | 357 | 53.8 | 49.3 | 65.3 | 33.0 | 80.4 | 7.49 | 14.02 | 2.130 | 848 | 0.389 | 0.605 | 0.76 |
| search | 1 | 119 | 100.0 | 15.1 | 89.9 | 0.0 | 690.5 | 1.00 | 46.55 | 0.899 | 0 | 0.086 | 0.102 | 0.11 |
| shuf | 3 | 357 | 29.4 | 21.3 | 58.3 | 56.2 | 38.5 | 8.28 | 16.71 | 6.543 | 1068 | 0.465 | 0.608 | 1.10 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 303 | 92.7 | 90.1 | 85.8 | 5.8 | 475.6 | 3.68 | 6.69 | 0.171 | 130 | 0.129 | 0.136 | 0.51 |
| exec | 3 | 303 | 100.0 | 96.0 | 88.1 | 0.0 | 531.5 | 3.56 | 6.41 | 0.089 | 118 | 0.128 | 0.138 | 0.20 |
| search | 1 | 101 | 100.0 | 100.0 | 88.1 | 0.0 | 1429.4 | 1.00 | 6.45 | 0.119 | 0 | 0.042 | 0.044 | 0.05 |
| shuf | 3 | 303 | 100.0 | 89.4 | 88.1 | 0.0 | 525.0 | 3.63 | 6.50 | 0.139 | 124 | 0.128 | 0.167 | 0.18 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 660 | 61.5 | 59.8 | 78.6 | 34.9 | 137.5 | 5.82 | 9.89 | 1.096 | 529 | 0.171 | 0.460 | 1.12 |
| exec | 3 | 660 | 75.0 | 70.8 | 75.8 | 15.4 | 167.4 | 5.69 | 10.53 | 0.881 | 513 | 0.173 | 0.542 | 0.76 |
| search | 1 | 220 | 100.0 | 54.1 | 89.1 | 0.0 | 905.4 | 1.00 | 28.14 | 0.541 | 0 | 0.073 | 0.099 | 0.11 |
| shuf | 3 | 660 | 61.8 | 52.6 | 72.0 | 24.6 | 123.4 | 6.15 | 12.02 | 1.787 | 634 | 0.176 | 0.548 | 1.10 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 37.8 / 57.6 | 93.1 / 495.4 |
| base | 2 | 31.9 / 46.8 | 94.1 / 447.4 |
| base | 3 | 35.3 / 54.7 | 91.1 / 487.5 |
| exec | 1 | 52.1 / 78.4 | 100.0 / 530.5 |
| exec | 2 | 57.1 / 87.2 | 100.0 / 537.2 |
| exec | 3 | 52.1 / 75.9 | 100.0 / 527.0 |
| search | 0 | 100.0 / 690.5 | 100.0 / 1429.4 |
| shuf | 1 | 33.6 / 46.5 | 100.0 / 530.0 |
| shuf | 2 | 31.1 / 38.4 | 100.0 / 522.4 |
| shuf | 3 | 23.5 / 30.9 | 100.0 / 522.8 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec | search | shuf |
|---|---|---|---|---|---|---|
| proj | altered | 20 | 23.3 (87 / 73) | 46.7 (72 / 35) | 100.0 (100 / 0) | 20.0 (55 / 64) |
| proj | familiar | 40 | 32.5 (74 / 56) | 60.8 (74 / 18) | 100.0 (100 / 0) | 27.5 (59 / 54) |
| proj | later | 10 | 0.0 (83 / 100) | 0.0 (50 / 100) | 100.0 (100 / 0) | 0.0 (47 / 100) |
| proj | newmech | 25 | 5.3 (71 / 92) | 25.3 (67 / 62) | 100.0 (100 / 0) | 13.3 (56 / 76) |
| proj | unans | 12 | 88.9 (11 / 100) | 100.0 (0 / 0) | 100.0 (0 / 0) | 38.9 (33 / 100) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | later | 10 | 76.7 (77 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 25 | 80.0 (100 / 20) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | stale | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 12 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | exec | search | shuf |
|---|---|---|---|---|
| deep-direct | 20.9 | 36.4 | 100.0 | 22.5 |
| deep-indirect | 40.0 | 40.0 | 100.0 | 36.7 |
| local | 14.3 | 48.4 | 100.0 | 11.9 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| exec vs base | proj | 10 | 1.520 (1.045 to 2.490) | +18.8 (+7.5 to +30.1) | 1.362 / +14.3; 1.865 / +25.2; 1.388 / +16.8 |
| exec vs base | tab | 13 | 1.118 (0.991 to 1.346) | +7.3 (+0.0 to +16.3) | 1.071 / +6.9; 1.201 / +5.9; 1.081 / +8.9 |
| exec vs base | all | 21 | 1.217 (1.005 to 1.574) | +13.5 (+5.9 to +22.4) | 1.161 / +10.9; 1.346 / +16.4; 1.154 / +13.2 |
| shuf vs base | proj | 10 | 0.727 (0.477 to 1.001) | -5.6 (-18.6 to +3.1) | 0.807 / -4.2; 0.821 / -0.8; 0.565 / -11.8 |
| shuf vs base | tab | 13 | 1.104 (0.998 to 1.305) | +7.3 (+0.0 to +16.3) | 1.070 / +6.9; 1.167 / +5.9; 1.072 / +8.9 |
| shuf vs base | all | 21 | 0.897 (0.759 to 1.048) | +0.3 (-6.8 to +7.3) | 0.937 / +0.9; 0.919 / +2.3; 0.838 / -2.3 |
| exec vs shuf | proj | 10 | 2.091 (1.285 to 3.697) | +24.4 (+8.7 to +41.3) | 1.687 / +18.5; 2.271 / +26.1; 2.457 / +28.6 |
| exec vs shuf | tab | 13 | 1.012 (0.991 to 1.038) | +0.0 (+0.0 to +0.0) | 1.001 / +0.0; 1.028 / +0.0; 1.008 / +0.0 |
| exec vs shuf | all | 21 | 1.357 (1.094 to 1.738) | +13.2 (+4.2 to +22.7) | 1.238 / +10.0; 1.464 / +14.1; 1.378 / +15.5 |

## Frozen primary rule

WIN: over all jobs, verified jobs per minute of exec at least 1.10 times base with the interval above 1.00, and in each domain a verified share no more than 2 points lower.
NO WIN: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.

- all: ratio 1.217 (1.005 to 1.574); verified +13.5 points (+5.9 to +22.4)
- proj: ratio 1.520 (1.045 to 2.490); verified +18.8 points (+7.5 to +30.1)
- tab: ratio 1.118 (0.991 to 1.346); verified +7.3 points (+0.0 to +16.3)

**Verdict: WIN**
