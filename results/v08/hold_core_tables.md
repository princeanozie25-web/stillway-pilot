# v0.8 tables: results/v08/hold/core

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 510 | 42.0 | 41.4 | 79.4 | 53.8 | 63.2 | 7.63 | 12.56 | 2.252 | 820 | 0.389 | 0.696 | 1.13 |
| exec | 3 | 510 | 62.5 | 56.3 | 76.1 | 28.4 | 93.4 | 7.61 | 13.98 | 1.724 | 821 | 0.393 | 0.559 | 0.92 |
| search | 1 | 170 | 100.0 | 12.9 | 88.2 | 0.0 | 685.5 | 1.00 | 45.75 | 0.882 | 0 | 0.087 | 0.103 | 0.12 |
| shuf | 3 | 510 | 40.8 | 31.2 | 59.2 | 46.0 | 54.3 | 8.20 | 16.33 | 4.481 | 987 | 0.465 | 0.616 | 1.11 |
| teacher | 1 | 170 | 100.0 | 100.0 | 88.2 | 0.0 | 189.8 | 6.91 | 10.86 | 0.000 | 612 | 0.360 | 0.427 | 0.44 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 450 | 98.7 | 98.7 | 86.7 | 1.5 | 545.9 | 3.47 | 6.19 | 0.016 | 112 | 0.129 | 0.135 | 0.14 |
| exec | 3 | 450 | 100.0 | 98.2 | 86.7 | 0.0 | 549.0 | 3.48 | 6.23 | 0.018 | 114 | 0.129 | 0.136 | 0.18 |
| search | 1 | 150 | 100.0 | 100.0 | 86.7 | 0.0 | 1427.3 | 1.00 | 6.32 | 0.227 | 0 | 0.042 | 0.043 | 0.05 |
| shuf | 3 | 450 | 99.6 | 96.7 | 86.7 | 0.5 | 543.8 | 3.50 | 6.26 | 0.033 | 116 | 0.129 | 0.137 | 0.18 |
| teacher | 1 | 150 | 100.0 | 100.0 | 86.7 | 0.0 | 618.3 | 3.47 | 6.19 | 0.000 | 112 | 0.117 | 0.118 | 0.12 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 960 | 68.5 | 68.2 | 82.8 | 28.2 | 156.8 | 5.68 | 9.58 | 0.743 | 488 | 0.136 | 0.460 | 1.13 |
| exec | 3 | 960 | 80.1 | 75.9 | 81.0 | 14.1 | 181.6 | 5.68 | 10.35 | 0.726 | 490 | 0.137 | 0.542 | 0.92 |
| search | 1 | 320 | 100.0 | 53.8 | 87.5 | 0.0 | 906.3 | 1.00 | 27.27 | 0.575 | 0 | 0.072 | 0.098 | 0.12 |
| shuf | 3 | 960 | 68.3 | 61.9 | 72.1 | 20.4 | 140.9 | 5.99 | 11.61 | 1.444 | 579 | 0.139 | 0.553 | 1.11 |
| teacher | 1 | 320 | 100.0 | 100.0 | 87.5 | 0.0 | 281.2 | 5.30 | 8.67 | 0.000 | 378 | 0.118 | 0.368 | 0.44 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 47.1 / 73.4 | 98.0 / 544.6 |
| base | 2 | 36.5 / 54.9 | 99.3 / 549.8 |
| base | 3 | 42.4 / 61.8 | 98.7 / 543.4 |
| exec | 1 | 64.1 / 97.3 | 100.0 / 553.7 |
| exec | 2 | 68.8 / 106.8 | 100.0 / 547.5 |
| exec | 3 | 54.7 / 77.5 | 100.0 / 545.8 |
| search | 0 | 100.0 / 685.5 | 100.0 / 1427.3 |
| shuf | 1 | 44.7 / 61.5 | 100.0 / 549.0 |
| shuf | 2 | 42.9 / 54.6 | 100.0 / 547.3 |
| shuf | 3 | 34.7 / 46.9 | 98.7 / 535.1 |
| teacher | 0 | 100.0 / 189.8 | 100.0 / 618.3 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec | search | shuf | teacher |
|---|---|---|---|---|---|---|---|
| proj | altered | 30 | 37.8 (90 / 58) | 61.1 (87 / 29) | 100.0 (100 / 0) | 40.0 (71 / 44) | 100.0 (100 / 0) |
| proj | familiar | 60 | 49.4 (84 / 41) | 74.4 (84 / 12) | 100.0 (100 / 0) | 33.9 (56 / 39) | 100.0 (100 / 0) |
| proj | newmech | 40 | 3.3 (71 / 95) | 24.2 (69 / 65) | 100.0 (100 / 0) | 5.0 (57 / 91) | 100.0 (100 / 0) |
| proj | unans | 20 | 45.0 (45 / 100) | 68.3 (25 / 100) | 100.0 (0 / 0) | 75.0 (17 / 100) | 100.0 (0 / 0) |
| proj | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 50 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 40 | 95.0 (100 / 5) | 100.0 (100 / 0) | 100.0 (100 / 0) | 98.3 (100 / 2) | 100.0 (100 / 0) |
| tab | stale | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 20 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | exec | search | shuf | teacher |
|---|---|---|---|---|---|
| deep-direct | 35.3 | 53.2 | 100.0 | 23.4 | 100.0 |
| deep-indirect | 43.1 | 47.2 | 100.0 | 50.0 | 100.0 |
| local | 21.4 | 65.8 | 100.0 | 17.1 | 100.0 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| exec vs base | proj | 8 | 1.477 (1.107 to 2.211) | +20.6 (+10.5 to +30.9) | 1.325 / +17.1; 1.944 / +32.4; 1.254 / +12.4 |
| exec vs base | tab | 30 | 1.006 (0.991 to 1.027) | +1.3 (+0.0 to +3.6) | 1.017 / +2.0; 0.996 / +0.7; 1.004 / +1.3 |
| exec vs base | all | 36 | 1.158 (0.999 to 1.408) | +11.6 (+4.9 to +18.9) | 1.115 / +10.0; 1.293 / +17.5; 1.077 / +7.2 |
| shuf vs base | proj | 8 | 0.858 (0.619 to 1.088) | -1.2 (-12.2 to +9.2) | 0.839 / -2.4; 0.993 / +6.5; 0.759 / -7.6 |
| shuf vs base | tab | 30 | 0.996 (0.978 to 1.014) | +0.9 (-0.7 to +3.2) | 1.008 / +2.0; 0.995 / +0.7; 0.985 / +0.0 |
| shuf vs base | all | 36 | 0.899 (0.801 to 0.988) | -0.2 (-6.0 to +5.2) | 0.898 / -0.3; 0.917 / +3.8; 0.881 / -4.1 |
| exec vs shuf | proj | 8 | 1.720 (1.242 to 2.914) | +21.8 (+8.5 to +36.5) | 1.580 / +19.4; 1.958 / +25.9; 1.653 / +20.0 |
| exec vs shuf | tab | 30 | 1.010 (1.000 to 1.025) | +0.4 (+0.0 to +1.4) | 1.009 / +0.0; 1.000 / +0.0; 1.020 / +1.3 |
| exec vs shuf | all | 36 | 1.289 (1.092 to 1.628) | +11.8 (+2.9 to +22.0) | 1.242 / +10.3; 1.410 / +13.8; 1.222 / +11.2 |

## Frozen primary rule

WIN: over all jobs, verified jobs per minute of exec at least 1.10 times base with the interval above 1.00, and in each domain a verified share no more than 2 points lower.
NO WIN: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.

- all: ratio 1.158 (0.999 to 1.408); verified +11.6 points (+4.9 to +18.9)
- proj: ratio 1.477 (1.107 to 2.211); verified +20.6 points (+10.5 to +30.9)
- tab: ratio 1.006 (0.991 to 1.027); verified +1.3 points (+0.0 to +3.6)

**Verdict: INCONCLUSIVE**
