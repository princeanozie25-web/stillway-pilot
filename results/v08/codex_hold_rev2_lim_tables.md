# v0.8 tables: results/v08/codex_hold_rev2/lim

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 357 | 37.8 | 36.4 | 74.2 | 59.6 | 59.6 | 7.41 | 12.13 | 2.652 | 802 | 0.385 | 0.666 | 1.08 |
| exec | 3 | 357 | 52.4 | 48.2 | 62.2 | 32.0 | 79.5 | 7.42 | 14.04 | 2.171 | 841 | 0.388 | 0.547 | 0.77 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 303 | 91.7 | 90.4 | 84.5 | 5.5 | 446.7 | 3.82 | 6.92 | 0.277 | 149 | 0.128 | 0.136 | 0.67 |
| exec | 3 | 303 | 100.0 | 96.7 | 88.1 | 0.0 | 539.8 | 3.56 | 6.39 | 0.083 | 117 | 0.128 | 0.135 | 0.18 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 660 | 62.6 | 61.2 | 78.9 | 33.0 | 143.0 | 5.76 | 9.74 | 1.053 | 502 | 0.233 | 0.455 | 1.08 |
| exec | 3 | 660 | 74.2 | 70.5 | 74.1 | 14.5 | 168.1 | 5.65 | 10.53 | 0.880 | 509 | 0.172 | 0.537 | 0.77 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 35.3 / 54.0 | 93.1 / 473.2 |
| base | 2 | 35.3 / 56.7 | 87.1 / 432.9 |
| base | 3 | 42.9 / 68.2 | 95.0 / 435.6 |
| exec | 1 | 51.3 / 75.5 | 100.0 / 541.5 |
| exec | 2 | 48.7 / 73.0 | 100.0 / 538.0 |
| exec | 3 | 57.1 / 90.6 | 100.0 / 540.0 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec |
|---|---|---|---|---|
| proj | altered | 20 | 26.7 (72 / 63) | 46.7 (67 / 30) |
| proj | familiar | 40 | 43.3 (84 / 49) | 54.2 (72 / 24) |
| proj | later | 10 | 0.0 (60 / 100) | 0.0 (50 / 100) |
| proj | newmech | 25 | 4.0 (80 / 95) | 29.3 (60 / 51) |
| proj | unans | 12 | 77.8 (19 / 100) | 100.0 (0 / 0) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | later | 10 | 63.3 (63 / 0) | 100.0 (100 / 0) |
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
| local | 23.0 | 43.7 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| exec vs base | proj | 10 | 1.334 (1.080 to 1.769) | +14.6 (+7.1 to +22.6) | 1.398 / +16.0; 1.288 / +13.4; 1.328 / +14.3 |
| exec vs base | tab | 13 | 1.208 (1.000 to 1.656) | +8.3 (+0.0 to +19.4) | 1.144 / +6.9; 1.243 / +12.9; 1.240 / +5.0 |
| exec vs base | all | 21 | 1.176 (1.030 to 1.404) | +11.7 (+5.6 to +18.5) | 1.169 / +11.8; 1.176 / +13.2; 1.187 / +10.0 |

## Frozen primary rule

WIN: over all jobs, verified jobs per minute of exec at least 1.10 times base with the interval above 1.00, and in each domain a verified share no more than 2 points lower.
NO WIN: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.

- all: ratio 1.176 (1.030 to 1.404); verified +11.7 points (+5.6 to +18.5)
- proj: ratio 1.334 (1.080 to 1.769); verified +14.6 points (+7.1 to +22.6)
- tab: ratio 1.208 (1.000 to 1.656); verified +8.3 points (+0.0 to +19.4)

**Verdict: WIN**
