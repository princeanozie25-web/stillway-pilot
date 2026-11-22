# v0.8 tables: /tmp/tmpha_6d0no

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 357 | 35.0 | 34.2 | 72.5 | 64.1 | 52.9 | 7.63 | 12.61 | 3.176 | 868 | 0.386 | 0.734 | 1.12 |
| obsonly | 3 | 357 | 50.4 | 50.1 | 83.5 | 50.3 | 91.7 | 6.70 | 10.68 | 0.983 | 631 | 0.313 | 0.402 | 0.72 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 303 | 92.7 | 90.1 | 85.8 | 5.8 | 475.6 | 3.68 | 6.69 | 0.171 | 130 | 0.129 | 0.136 | 0.51 |
| obsonly | 3 | 303 | 94.1 | 94.1 | 88.1 | 6.7 | 513.1 | 3.52 | 6.31 | 0.098 | 114 | 0.128 | 0.135 | 0.15 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 660 | 61.5 | 59.8 | 78.6 | 34.9 | 137.5 | 5.82 | 9.89 | 1.096 | 529 | 0.171 | 0.460 | 1.12 |
| obsonly | 3 | 660 | 70.5 | 70.3 | 85.6 | 29.7 | 184.6 | 5.24 | 8.68 | 0.441 | 393 | 0.138 | 0.390 | 0.72 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 37.8 / 57.6 | 93.1 / 495.4 |
| base | 2 | 31.9 / 46.8 | 94.1 / 447.4 |
| base | 3 | 35.3 / 54.7 | 91.1 / 487.5 |
| obsonly | 1 | 55.5 / 99.8 | 94.1 / 513.2 |
| obsonly | 2 | 50.4 / 90.3 | 96.0 / 525.1 |
| obsonly | 3 | 45.4 / 84.7 | 92.1 / 501.1 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | obsonly |
|---|---|---|---|---|
| proj | altered | 20 | 23.3 (87 / 73) | 48.3 (88 / 45) |
| proj | familiar | 40 | 32.5 (74 / 56) | 57.5 (90 / 36) |
| proj | later | 10 | 0.0 (83 / 100) | 0.0 (80 / 100) |
| proj | newmech | 25 | 5.3 (71 / 92) | 18.7 (97 / 81) |
| proj | unans | 12 | 88.9 (11 / 100) | 88.9 (11 / 100) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | later | 10 | 76.7 (77 / 0) | 100.0 (100 / 0) |
| tab | scattered | 25 | 80.0 (100 / 20) | 76.0 (100 / 24) |
| tab | stale | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 12 | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | obsonly |
|---|---|---|
| deep-direct | 20.9 | 36.4 |
| deep-indirect | 40.0 | 36.7 |
| local | 14.3 | 42.9 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| obsonly vs base | proj | 10 | 1.732 (1.219 to 2.792) | +15.4 (+4.9 to +26.4) | 1.732 / +17.6; 1.931 / +18.5; 1.550 / +10.1 |
| obsonly vs base | tab | 13 | 1.079 (0.976 to 1.303) | +1.3 (-2.6 to +7.2) | 1.036 / +1.0; 1.174 / +2.0; 1.028 / +1.0 |
| obsonly vs base | all | 21 | 1.343 (1.097 to 1.739) | +8.9 (+1.8 to +17.6) | 1.328 / +10.0; 1.425 / +10.9; 1.276 / +5.9 |

## Frozen primary rule

WIN: over all jobs, verified jobs per minute of obsonly at least 1.10 times base with the interval above 1.00, and in each domain a verified share no more than 2 points lower.
NO WIN: the whole interval of the ratio is below 1.10, or in some domain the whole interval of the verified difference is below -2 points. Otherwise INCONCLUSIVE.

- all: ratio 1.343 (1.097 to 1.739); verified +8.9 points (+1.8 to +17.6)
- proj: ratio 1.732 (1.219 to 2.792); verified +15.4 points (+4.9 to +26.4)
- tab: ratio 1.079 (0.976 to 1.303); verified +1.3 points (-2.6 to +7.2)

**Verdict: WIN**
