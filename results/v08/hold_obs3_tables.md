# v0.8 tables: results/v08/hold/obs3

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 510 | 42.0 | 41.4 | 79.4 | 53.8 | 63.2 | 7.63 | 12.56 | 2.252 | 820 | 0.389 | 0.696 | 1.13 |
| exec | 3 | 510 | 62.5 | 56.3 | 76.1 | 28.4 | 93.4 | 7.61 | 13.98 | 1.724 | 821 | 0.393 | 0.559 | 0.92 |
| obsonly | 3 | 510 | 56.1 | 56.1 | 88.8 | 44.8 | 101.0 | 6.76 | 10.69 | 0.741 | 600 | 0.384 | 0.426 | 0.77 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 450 | 98.7 | 98.7 | 86.7 | 1.5 | 545.9 | 3.47 | 6.19 | 0.016 | 112 | 0.129 | 0.135 | 0.14 |
| exec | 3 | 450 | 100.0 | 98.2 | 86.7 | 0.0 | 549.0 | 3.48 | 6.23 | 0.018 | 114 | 0.129 | 0.136 | 0.18 |
| obsonly | 3 | 450 | 97.6 | 97.6 | 86.7 | 2.8 | 539.6 | 3.47 | 6.19 | 0.025 | 112 | 0.128 | 0.136 | 0.15 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 3 | 960 | 68.5 | 68.2 | 82.8 | 28.2 | 156.8 | 5.68 | 9.58 | 0.743 | 488 | 0.136 | 0.460 | 1.13 |
| exec | 3 | 960 | 80.1 | 75.9 | 81.0 | 14.1 | 181.6 | 5.68 | 10.35 | 0.726 | 490 | 0.137 | 0.542 | 0.92 |
| obsonly | 3 | 960 | 75.5 | 75.5 | 87.8 | 25.4 | 198.8 | 5.22 | 8.58 | 0.308 | 371 | 0.138 | 0.394 | 0.77 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 47.1 / 73.4 | 98.0 / 544.6 |
| base | 2 | 36.5 / 54.9 | 99.3 / 549.8 |
| base | 3 | 42.4 / 61.8 | 98.7 / 543.4 |
| exec | 1 | 64.1 / 97.3 | 100.0 / 553.7 |
| exec | 2 | 68.8 / 106.8 | 100.0 / 547.5 |
| exec | 3 | 54.7 / 77.5 | 100.0 / 545.8 |
| obsonly | 1 | 62.9 / 112.4 | 97.3 / 529.3 |
| obsonly | 2 | 56.5 / 101.3 | 98.0 / 541.2 |
| obsonly | 3 | 48.8 / 88.9 | 97.3 / 548.6 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec | obsonly |
|---|---|---|---|---|---|
| proj | altered | 30 | 37.8 (90 / 58) | 61.1 (87 / 29) | 56.7 (98 / 42) |
| proj | familiar | 60 | 49.4 (84 / 41) | 74.4 (84 / 12) | 66.1 (94 / 30) |
| proj | newmech | 40 | 3.3 (71 / 95) | 24.2 (69 / 65) | 16.7 (93 / 82) |
| proj | unans | 20 | 45.0 (45 / 100) | 68.3 (25 / 100) | 60.0 (40 / 100) |
| proj | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 50 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 40 | 95.0 (100 / 5) | 100.0 (100 / 0) | 90.8 (100 / 9) |
| tab | stale | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 20 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | exec | obsonly |
|---|---|---|---|
| deep-direct | 35.3 | 53.2 | 50.7 |
| deep-indirect | 43.1 | 47.2 | 47.2 |
| local | 21.4 | 65.8 | 46.2 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| obsonly vs base | proj | 8 | 1.597 (1.275 to 2.231) | +14.1 (+8.0 to +19.4) | 1.532 / +15.9; 1.844 / +20.0; 1.439 / +6.5 |
| obsonly vs base | tab | 30 | 0.988 (0.957 to 1.010) | -1.1 (-4.0 to +1.0) | 0.972 / -0.7; 0.984 / -1.3; 1.010 / -1.3 |
| obsonly vs base | all | 36 | 1.268 (1.102 to 1.497) | +7.0 (+2.0 to +11.5) | 1.235 / +8.1; 1.322 / +10.0; 1.248 / +2.8 |
| exec vs base | proj | 8 | 1.477 (1.107 to 2.211) | +20.6 (+10.5 to +30.9) | 1.325 / +17.1; 1.944 / +32.4; 1.254 / +12.4 |
| exec vs base | tab | 30 | 1.006 (0.991 to 1.027) | +1.3 (+0.0 to +3.6) | 1.017 / +2.0; 0.996 / +0.7; 1.004 / +1.3 |
| exec vs base | all | 36 | 1.158 (0.999 to 1.408) | +11.6 (+4.9 to +18.9) | 1.115 / +10.0; 1.293 / +17.5; 1.077 / +7.2 |
