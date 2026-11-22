# v0.8 tables: results/v08/codex_hold_rev2, view: core/base_s1-3, core/exec_s1-3, expl/obsonly_s1-3, jobs of group later removed

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 327 | 38.2 | 37.3 | 71.6 | 60.3 | 57.6 | 7.65 | 12.67 | 2.912 | 878 | 0.386 | 0.741 | 1.12 |
| exec | 3 | 327 | 58.7 | 53.8 | 66.7 | 28.4 | 90.4 | 7.35 | 13.57 | 1.745 | 816 | 0.386 | 0.592 | 0.76 |
| obsonly | 3 | 327 | 55.0 | 54.7 | 83.8 | 46.0 | 100.7 | 6.67 | 10.65 | 0.850 | 628 | 0.314 | 0.399 | 0.72 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 273 | 94.5 | 94.5 | 86.8 | 6.3 | 523.5 | 3.47 | 6.29 | 0.058 | 113 | 0.129 | 0.135 | 0.14 |
| exec | 3 | 273 | 100.0 | 95.6 | 86.8 | 0.0 | 540.4 | 3.52 | 6.40 | 0.044 | 118 | 0.128 | 0.138 | 0.20 |
| obsonly | 3 | 273 | 93.4 | 93.4 | 86.8 | 7.6 | 519.3 | 3.47 | 6.29 | 0.071 | 113 | 0.128 | 0.135 | 0.15 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 600 | 63.8 | 63.3 | 78.5 | 33.1 | 143.8 | 5.75 | 9.77 | 0.990 | 530 | 0.138 | 0.457 | 1.12 |
| exec | 3 | 600 | 77.5 | 72.8 | 75.8 | 13.6 | 176.9 | 5.61 | 10.31 | 0.746 | 499 | 0.173 | 0.539 | 0.76 |
| obsonly | 3 | 600 | 72.5 | 72.3 | 85.2 | 28.2 | 190.9 | 5.22 | 8.67 | 0.393 | 394 | 0.138 | 0.390 | 0.72 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 41.3 / 62.9 | 97.8 / 540.3 |
| base | 2 | 34.9 / 50.8 | 95.6 / 529.5 |
| base | 3 | 38.5 / 59.4 | 90.1 / 500.7 |
| exec | 1 | 56.9 / 87.7 | 100.0 / 538.8 |
| exec | 2 | 62.4 / 98.5 | 100.0 / 546.4 |
| exec | 3 | 56.9 / 85.3 | 100.0 / 536.1 |
| obsonly | 1 | 60.6 / 109.5 | 93.4 / 519.2 |
| obsonly | 2 | 55.0 / 99.1 | 95.6 / 533.1 |
| obsonly | 3 | 49.5 / 93.2 | 91.2 / 505.6 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec | obsonly |
|---|---|---|---|---|---|
| proj | altered | 20 | 23.3 (87 / 73) | 46.7 (72 / 35) | 48.3 (88 / 45) |
| proj | familiar | 40 | 32.5 (74 / 56) | 60.8 (74 / 18) | 57.5 (90 / 36) |
| proj | newmech | 25 | 5.3 (71 / 92) | 25.3 (67 / 62) | 18.7 (97 / 81) |
| proj | unans | 12 | 88.9 (11 / 100) | 100.0 (0 / 0) | 88.9 (11 / 100) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 25 | 80.0 (100 / 20) | 100.0 (100 / 0) | 76.0 (100 / 24) |
| tab | stale | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 12 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | exec | obsonly |
|---|---|---|---|
| deep-direct | 20.9 | 36.4 | 36.4 |
| deep-indirect | 40.0 | 40.0 | 36.7 |
| local | 18.8 | 63.5 | 56.2 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| obsonly vs base | proj | 8 | 1.749 (1.209 to 2.817) | +16.8 (+6.1 to +28.9) | 1.741 / +19.3; 1.952 / +20.2; 1.570 / +11.0 |
| obsonly vs base | tab | 11 | 0.992 (0.971 to 1.006) | -1.1 (-3.2 to +0.0) | 0.961 / -4.4; 1.007 / +0.0; 1.010 / +1.1 |
| obsonly vs base | all | 17 | 1.328 (1.071 to 1.737) | +8.7 (+1.4 to +17.8) | 1.294 / +8.5; 1.396 / +11.0; 1.295 / +6.5 |
| exec vs base | proj | 8 | 1.570 (1.090 to 2.551) | +20.5 (+8.9 to +32.9) | 1.395 / +15.6; 1.941 / +27.5; 1.436 / +18.3 |
| exec vs base | tab | 11 | 1.032 (0.990 to 1.128) | +5.5 (+0.0 to +14.3) | 0.997 / +2.2; 1.032 / +4.4; 1.071 / +9.9 |
| exec vs base | all | 17 | 1.230 (1.016 to 1.603) | +13.7 (+5.8 to +22.9) | 1.148 / +9.5; 1.355 / +17.0; 1.198 / +14.5 |

## Frozen primary rule

WIN: over all jobs, verified jobs per minute of obsonly at least 1.10 times base with the interval above 1.00, and in each domain a verified share no more than 2 points lower.
NO WIN: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.

- all: ratio 1.328 (1.071 to 1.737); verified +8.7 points (+1.4 to +17.8)
- proj: ratio 1.749 (1.209 to 2.817); verified +16.8 points (+6.1 to +28.9)
- tab: ratio 0.992 (0.971 to 1.006); verified -1.1 points (-3.2 to +0.0)

**Verdict: WIN**
