# v0.8 tables: results/v08/codex_hold_rev2, view: lim/, jobs of group later removed

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 327 | 41.3 | 39.8 | 75.5 | 56.7 | 65.5 | 7.38 | 12.10 | 2.356 | 797 | 0.385 | 0.666 | 1.08 |
| exec | 3 | 327 | 57.2 | 52.6 | 63.3 | 27.1 | 88.9 | 7.31 | 13.66 | 1.802 | 816 | 0.386 | 0.545 | 0.77 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 273 | 94.9 | 94.9 | 86.8 | 5.9 | 527.1 | 3.47 | 6.27 | 0.054 | 113 | 0.128 | 0.135 | 0.14 |
| exec | 3 | 273 | 100.0 | 96.3 | 86.8 | 0.0 | 549.1 | 3.51 | 6.38 | 0.037 | 117 | 0.128 | 0.135 | 0.18 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 600 | 65.7 | 64.8 | 80.7 | 31.8 | 154.3 | 5.60 | 9.45 | 0.843 | 486 | 0.138 | 0.408 | 1.08 |
| exec | 3 | 600 | 76.7 | 72.5 | 74.0 | 12.6 | 176.8 | 5.58 | 10.35 | 0.754 | 498 | 0.172 | 0.536 | 0.77 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 38.5 / 60.0 | 96.7 / 536.4 |
| base | 2 | 38.5 / 62.2 | 90.1 / 500.9 |
| base | 3 | 46.8 / 74.4 | 97.8 / 544.0 |
| exec | 1 | 56.0 / 84.2 | 100.0 / 551.3 |
| exec | 2 | 53.2 / 81.9 | 100.0 / 546.6 |
| exec | 3 | 62.4 / 101.2 | 100.0 / 549.4 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec |
|---|---|---|---|---|
| proj | altered | 20 | 26.7 (72 / 63) | 46.7 (67 / 30) |
| proj | familiar | 40 | 43.3 (84 / 49) | 54.2 (72 / 24) |
| proj | newmech | 25 | 4.0 (80 / 95) | 29.3 (60 / 51) |
| proj | unans | 12 | 77.8 (19 / 100) | 100.0 (0 / 0) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 25 | 81.3 (100 / 19) | 100.0 (100 / 0) |
| tab | stale | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 12 | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | exec |
|---|---|---|
| deep-direct | 23.3 | 34.9 |
| deep-indirect | 40.0 | 50.0 |
| local | 30.2 | 57.3 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| exec vs base | proj | 8 | 1.357 (1.098 to 1.782) | +15.9 (+8.2 to +24.3) | 1.404 / +17.4; 1.317 / +14.7; 1.361 / +15.6 |
| exec vs base | tab | 11 | 1.042 (0.999 to 1.143) | +5.1 (+0.0 to +14.7) | 1.028 / +3.3; 1.091 / +9.9; 1.010 / +2.2 |
| exec vs base | all | 17 | 1.146 (1.024 to 1.316) | +11.0 (+5.3 to +17.5) | 1.136 / +11.0; 1.153 / +12.5; 1.152 / +9.5 |

## Frozen primary rule

WIN: over all jobs, verified jobs per minute of exec at least 1.10 times base with the interval above 1.00, and in each domain a verified share no more than 2 points lower.
NO WIN: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.

- all: ratio 1.146 (1.024 to 1.316); verified +11.0 points (+5.3 to +17.5)
- proj: ratio 1.357 (1.098 to 1.782); verified +15.9 points (+8.2 to +24.3)
- tab: ratio 1.042 (0.999 to 1.143); verified +5.1 points (+0.0 to +14.7)

**Verdict: WIN**
