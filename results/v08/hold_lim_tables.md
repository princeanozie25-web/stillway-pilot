# v0.8 tables: results/v08/hold/lim

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 510 | 46.3 | 44.9 | 73.1 | 47.5 | 71.1 | 7.54 | 12.16 | 1.682 | 791 | 0.388 | 0.552 | 1.11 |
| exec | 3 | 510 | 60.2 | 53.9 | 77.1 | 31.8 | 88.8 | 7.62 | 14.24 | 1.935 | 823 | 0.397 | 0.552 | 1.01 |
| search | 1 | 170 | 100.0 | 12.9 | 88.2 | 0.0 | 685.7 | 1.00 | 45.75 | 0.882 | 0 | 0.087 | 0.104 | 0.11 |
| teacher | 1 | 170 | 100.0 | 100.0 | 88.2 | 0.0 | 189.6 | 6.91 | 10.86 | 0.000 | 612 | 0.360 | 0.428 | 0.44 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 450 | 99.3 | 99.3 | 86.7 | 0.8 | 551.9 | 3.47 | 6.19 | 0.007 | 112 | 0.129 | 0.135 | 0.14 |
| exec | 3 | 450 | 100.0 | 98.9 | 86.7 | 0.0 | 550.4 | 3.48 | 6.21 | 0.011 | 113 | 0.129 | 0.136 | 0.18 |
| search | 1 | 150 | 100.0 | 100.0 | 86.7 | 0.0 | 1436.8 | 1.00 | 6.32 | 0.227 | 0 | 0.042 | 0.043 | 0.04 |
| teacher | 1 | 150 | 100.0 | 100.0 | 86.7 | 0.0 | 617.8 | 3.47 | 6.19 | 0.000 | 112 | 0.117 | 0.118 | 0.12 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 960 | 71.1 | 70.4 | 79.5 | 23.6 | 165.5 | 5.63 | 9.36 | 0.586 | 473 | 0.135 | 0.458 | 1.11 |
| exec | 3 | 960 | 78.9 | 75.0 | 81.6 | 16.0 | 177.0 | 5.68 | 10.47 | 0.791 | 490 | 0.137 | 0.541 | 1.01 |
| search | 1 | 320 | 100.0 | 53.8 | 87.5 | 0.0 | 908.2 | 1.00 | 27.27 | 0.575 | 0 | 0.072 | 0.099 | 0.11 |
| teacher | 1 | 320 | 100.0 | 100.0 | 87.5 | 0.0 | 280.9 | 5.30 | 8.67 | 0.000 | 378 | 0.119 | 0.370 | 0.44 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 45.9 / 66.9 | 100.0 / 553.2 |
| base | 2 | 44.1 / 70.0 | 98.0 / 545.4 |
| base | 3 | 48.8 / 76.9 | 100.0 / 557.1 |
| exec | 1 | 57.6 / 85.0 | 100.0 / 554.1 |
| exec | 2 | 60.6 / 86.2 | 100.0 / 546.0 |
| exec | 3 | 62.4 / 95.5 | 100.0 / 551.2 |
| search | 0 | 100.0 / 685.7 | 100.0 / 1436.8 |
| teacher | 0 | 100.0 / 189.6 | 100.0 / 617.8 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec | search | teacher |
|---|---|---|---|---|---|---|
| proj | altered | 30 | 44.4 (89 / 50) | 57.8 (88 / 34) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| proj | familiar | 60 | 49.4 (76 / 35) | 69.4 (85 / 18) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| proj | newmech | 40 | 5.8 (67 / 91) | 25.8 (68 / 62) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| proj | unans | 20 | 66.7 (28 / 100) | 65.0 (32 / 100) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| proj | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 50 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 40 | 97.5 (100 / 2) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | stale | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 20 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | exec | search | teacher |
|---|---|---|---|---|
| deep-direct | 38.3 | 52.7 | 100.0 | 100.0 |
| deep-indirect | 40.3 | 54.2 | 100.0 | 100.0 |
| local | 25.6 | 53.8 | 100.0 | 100.0 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| exec vs base | proj | 8 | 1.248 (1.014 to 1.713) | +13.9 (+5.3 to +22.5) | 1.271 / +11.8; 1.231 / +16.5; 1.242 / +13.5 |
| exec vs base | tab | 30 | 0.997 (0.993 to 1.005) | +0.7 (+0.0 to +1.7) | 1.002 / +0.0; 1.001 / +2.0; 0.989 / +0.0 |
| exec vs base | all | 36 | 1.070 (0.960 to 1.241) | +7.7 (+2.3 to +14.1) | 1.098 / +6.2; 1.040 / +9.7; 1.072 / +7.2 |

## Frozen primary rule

WIN: over all jobs, verified jobs per minute of exec at least 1.10 times base with the interval above 1.00, and in each domain a verified share no more than 2 points lower.
NO WIN: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.

- all: ratio 1.070 (0.960 to 1.241); verified +7.7 points (+2.3 to +14.1)
- proj: ratio 1.248 (1.014 to 1.713); verified +13.9 points (+5.3 to +22.5)
- tab: ratio 0.997 (0.993 to 1.005); verified +0.7 points (+0.0 to +1.7)

**Verdict: INCONCLUSIVE**
