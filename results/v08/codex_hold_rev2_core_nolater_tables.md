# v0.8 tables: results/v08/codex_hold_rev2, view: core/, jobs of group later removed

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 327 | 38.2 | 37.3 | 71.6 | 60.3 | 57.6 | 7.65 | 12.67 | 2.912 | 878 | 0.386 | 0.741 | 1.12 |
| exec | 3 | 327 | 58.7 | 53.8 | 66.7 | 28.4 | 90.4 | 7.35 | 13.57 | 1.745 | 816 | 0.386 | 0.592 | 0.76 |
| search | 1 | 109 | 100.0 | 13.8 | 89.0 | 0.0 | 689.9 | 1.00 | 46.91 | 0.890 | 0 | 0.086 | 0.102 | 0.11 |
| shuf | 3 | 327 | 32.1 | 23.2 | 59.3 | 53.1 | 42.5 | 8.21 | 16.52 | 5.857 | 1054 | 0.464 | 0.608 | 1.10 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 273 | 94.5 | 94.5 | 86.8 | 6.3 | 523.5 | 3.47 | 6.29 | 0.058 | 113 | 0.129 | 0.135 | 0.14 |
| exec | 3 | 273 | 100.0 | 95.6 | 86.8 | 0.0 | 540.4 | 3.52 | 6.40 | 0.044 | 118 | 0.128 | 0.138 | 0.20 |
| search | 1 | 91 | 100.0 | 100.0 | 86.8 | 0.0 | 1429.2 | 1.00 | 6.44 | 0.132 | 0 | 0.042 | 0.044 | 0.05 |
| shuf | 3 | 273 | 100.0 | 90.5 | 86.8 | 0.0 | 536.4 | 3.57 | 6.46 | 0.095 | 123 | 0.128 | 0.140 | 0.18 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 600 | 63.8 | 63.3 | 78.5 | 33.1 | 143.8 | 5.75 | 9.77 | 0.990 | 530 | 0.138 | 0.457 | 1.12 |
| exec | 3 | 600 | 77.5 | 72.8 | 75.8 | 13.6 | 176.9 | 5.61 | 10.31 | 0.746 | 499 | 0.173 | 0.539 | 0.76 |
| search | 1 | 200 | 100.0 | 53.0 | 88.0 | 0.0 | 902.2 | 1.00 | 28.50 | 0.545 | 0 | 0.073 | 0.099 | 0.11 |
| shuf | 3 | 600 | 63.0 | 53.8 | 71.8 | 23.9 | 126.8 | 6.10 | 11.94 | 1.696 | 630 | 0.176 | 0.548 | 1.10 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 41.3 / 62.9 | 97.8 / 540.3 |
| base | 2 | 34.9 / 50.8 | 95.6 / 529.5 |
| base | 3 | 38.5 / 59.4 | 90.1 / 500.7 |
| exec | 1 | 56.9 / 87.7 | 100.0 / 538.8 |
| exec | 2 | 62.4 / 98.5 | 100.0 / 546.4 |
| exec | 3 | 56.9 / 85.3 | 100.0 / 536.1 |
| search | 0 | 100.0 / 689.9 | 100.0 / 1429.2 |
| shuf | 1 | 36.7 / 51.5 | 100.0 / 539.7 |
| shuf | 2 | 33.9 / 42.5 | 100.0 / 540.3 |
| shuf | 3 | 25.7 / 34.0 | 100.0 / 529.5 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec | search | shuf |
|---|---|---|---|---|---|---|
| proj | altered | 20 | 23.3 (87 / 73) | 46.7 (72 / 35) | 100.0 (100 / 0) | 20.0 (55 / 64) |
| proj | familiar | 40 | 32.5 (74 / 56) | 60.8 (74 / 18) | 100.0 (100 / 0) | 27.5 (59 / 54) |
| proj | newmech | 25 | 5.3 (71 / 92) | 25.3 (67 / 62) | 100.0 (100 / 0) | 13.3 (56 / 76) |
| proj | unans | 12 | 88.9 (11 / 100) | 100.0 (0 / 0) | 100.0 (0 / 0) | 38.9 (33 / 100) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
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
| local | 18.8 | 63.5 | 100.0 | 15.6 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| exec vs base | proj | 8 | 1.570 (1.090 to 2.551) | +20.5 (+8.9 to +32.9) | 1.395 / +15.6; 1.941 / +27.5; 1.436 / +18.3 |
| exec vs base | tab | 11 | 1.032 (0.990 to 1.128) | +5.5 (+0.0 to +14.3) | 0.997 / +2.2; 1.032 / +4.4; 1.071 / +9.9 |
| exec vs base | all | 17 | 1.230 (1.016 to 1.603) | +13.7 (+5.8 to +22.9) | 1.148 / +9.5; 1.355 / +17.0; 1.198 / +14.5 |
| shuf vs base | proj | 8 | 0.738 (0.486 to 1.000) | -6.1 (-20.4 to +3.0) | 0.818 / -4.6; 0.838 / -0.9; 0.572 / -12.8 |
| shuf vs base | tab | 11 | 1.025 (0.995 to 1.096) | +5.5 (+0.0 to +14.3) | 0.999 / +2.2; 1.020 / +4.4; 1.058 / +9.9 |
| shuf vs base | all | 17 | 0.882 (0.747 to 1.023) | -0.8 (-8.0 to +6.4) | 0.910 / -1.5; 0.900 / +1.5; 0.839 / -2.5 |
| exec vs shuf | proj | 8 | 2.128 (1.284 to 3.832) | +26.6 (+9.8 to +44.8) | 1.705 / +20.2; 2.317 / +28.4; 2.511 / +31.2 |
| exec vs shuf | tab | 11 | 1.007 (0.990 to 1.032) | +0.0 (+0.0 to +0.0) | 0.998 / +0.0; 1.011 / +0.0; 1.012 / +0.0 |
| exec vs shuf | all | 17 | 1.395 (1.115 to 1.817) | +14.5 (+4.9 to +25.0) | 1.262 / +11.0; 1.506 / +15.5; 1.429 / +17.0 |

## Frozen primary rule

WIN: over all jobs, verified jobs per minute of exec at least 1.10 times base with the interval above 1.00, and in each domain a verified share no more than 2 points lower.
NO WIN: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.

- all: ratio 1.230 (1.016 to 1.603); verified +13.7 points (+5.8 to +22.9)
- proj: ratio 1.570 (1.090 to 2.551); verified +20.5 points (+8.9 to +32.9)
- tab: ratio 1.032 (0.990 to 1.128); verified +5.5 points (+0.0 to +14.3)

**Verdict: WIN**
