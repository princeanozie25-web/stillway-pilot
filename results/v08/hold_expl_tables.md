# v0.8 tables: results/v08/hold/expl

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 1 | 170 | 47.1 | 45.9 | 79.4 | 48.1 | 73.4 | 7.63 | 12.07 | 1.450 | 805 | 0.389 | 0.543 | 0.94 |
| exec | 1 | 170 | 64.1 | 55.9 | 87.1 | 34.5 | 97.3 | 7.61 | 13.84 | 1.661 | 799 | 0.391 | 0.546 | 0.62 |
| obsonly | 1 | 170 | 62.9 | 62.9 | 86.5 | 35.4 | 112.4 | 6.82 | 10.74 | 0.542 | 608 | 0.387 | 0.457 | 0.77 |
| reconly | 1 | 170 | 51.8 | 44.7 | 72.4 | 40.7 | 75.0 | 7.77 | 14.40 | 2.375 | 859 | 0.447 | 0.590 | 0.77 |
| shuf | 1 | 170 | 44.7 | 35.9 | 62.9 | 44.9 | 61.5 | 8.03 | 15.90 | 3.882 | 932 | 0.461 | 0.610 | 0.91 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 1 | 150 | 98.0 | 98.0 | 86.7 | 2.3 | 544.6 | 3.47 | 6.18 | 0.020 | 112 | 0.129 | 0.135 | 0.14 |
| exec | 1 | 150 | 100.0 | 100.0 | 86.7 | 0.0 | 553.7 | 3.47 | 6.20 | 0.000 | 112 | 0.129 | 0.135 | 0.14 |
| obsonly | 1 | 150 | 97.3 | 97.3 | 86.7 | 3.1 | 529.3 | 3.47 | 6.19 | 0.027 | 112 | 0.130 | 0.138 | 0.14 |
| reconly | 1 | 150 | 100.0 | 97.3 | 86.7 | 0.0 | 547.2 | 3.49 | 6.25 | 0.027 | 115 | 0.129 | 0.136 | 0.18 |
| shuf | 1 | 150 | 100.0 | 98.7 | 86.7 | 0.0 | 549.0 | 3.48 | 6.24 | 0.013 | 114 | 0.128 | 0.137 | 0.18 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 1 | 320 | 70.9 | 70.3 | 82.8 | 25.7 | 166.9 | 5.68 | 9.31 | 0.524 | 480 | 0.135 | 0.458 | 0.94 |
| exec | 1 | 320 | 80.9 | 76.6 | 86.9 | 18.3 | 186.1 | 5.67 | 10.26 | 0.699 | 477 | 0.137 | 0.541 | 0.62 |
| obsonly | 1 | 320 | 79.1 | 79.1 | 86.6 | 20.2 | 206.1 | 5.25 | 8.61 | 0.245 | 375 | 0.139 | 0.395 | 0.77 |
| reconly | 1 | 320 | 74.4 | 69.4 | 79.1 | 19.8 | 164.4 | 5.77 | 10.58 | 0.895 | 510 | 0.136 | 0.539 | 0.77 |
| shuf | 1 | 320 | 70.6 | 65.3 | 74.1 | 20.3 | 149.9 | 5.90 | 11.37 | 1.314 | 548 | 0.139 | 0.543 | 0.91 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 47.1 / 73.4 | 98.0 / 544.6 |
| exec | 1 | 64.1 / 97.3 | 100.0 / 553.7 |
| obsonly | 1 | 62.9 / 112.4 | 97.3 / 529.3 |
| reconly | 1 | 51.8 / 75.0 | 100.0 / 547.2 |
| shuf | 1 | 44.7 / 61.5 | 100.0 / 549.0 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec | obsonly | reconly | shuf |
|---|---|---|---|---|---|---|---|
| proj | altered | 30 | 40.0 (93 / 57) | 73.3 (97 / 24) | 56.7 (93 / 39) | 50.0 (80 / 38) | 43.3 (77 / 43) |
| proj | familiar | 60 | 58.3 (85 / 31) | 75.0 (92 / 18) | 78.3 (92 / 15) | 56.7 (75 / 24) | 38.3 (62 / 38) |
| proj | newmech | 40 | 7.5 (65 / 88) | 25.0 (92 / 73) | 27.5 (90 / 69) | 10.0 (72 / 86) | 7.5 (60 / 88) |
| proj | unans | 20 | 50.0 (50 / 100) | 60.0 (35 / 100) | 60.0 (40 / 100) | 75.0 (25 / 100) | 85.0 (15 / 100) |
| proj | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 50 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 40 | 92.5 (100 / 8) | 100.0 (100 / 0) | 90.0 (100 / 10) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | stale | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 20 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | exec | obsonly | reconly | shuf |
|---|---|---|---|---|---|
| deep-direct | 35.8 | 56.7 | 50.7 | 44.8 | 28.4 |
| deep-indirect | 45.8 | 50.0 | 50.0 | 45.8 | 50.0 |
| local | 38.5 | 69.2 | 74.4 | 30.8 | 20.5 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| exec vs base | proj | 8 | 1.325 (1.057 to 1.740) | +17.1 (+7.4 to +25.0) | 1.325 / +17.1 |
| exec vs base | tab | 30 | 1.017 (0.996 to 1.059) | +2.0 (+0.0 to +6.0) | 1.017 / +2.0 |
| exec vs base | all | 36 | 1.115 (0.988 to 1.314) | +10.0 (+3.6 to +16.9) | 1.115 / +10.0 |
| obsonly vs base | proj | 8 | 1.532 (1.192 to 2.133) | +15.9 (+6.4 to +25.6) | 1.532 / +15.9 |
| obsonly vs base | tab | 30 | 0.972 (0.933 to 1.010) | -0.7 (-4.6 to +3.2) | 0.972 / -0.7 |
| obsonly vs base | all | 36 | 1.235 (1.056 to 1.513) | +8.1 (+1.6 to +15.4) | 1.235 / +8.1 |
| reconly vs base | proj | 8 | 1.022 (0.863 to 1.243) | +4.7 (-5.2 to +14.5) | 1.022 / +4.7 |
| reconly vs base | tab | 30 | 1.005 (0.979 to 1.046) | +2.0 (+0.0 to +6.0) | 1.005 / +2.0 |
| reconly vs base | all | 36 | 0.985 (0.920 to 1.064) | +3.4 (-1.9 to +9.1) | 0.985 / +3.4 |
| shuf vs base | proj | 8 | 0.839 (0.583 to 1.084) | -2.4 (-14.6 to +10.5) | 0.839 / -2.4 |
| shuf vs base | tab | 30 | 1.008 (0.988 to 1.046) | +2.0 (+0.0 to +6.0) | 1.008 / +2.0 |
| shuf vs base | all | 36 | 0.898 (0.788 to 0.991) | -0.3 (-7.5 to +6.6) | 0.898 / -0.3 |
| exec vs shuf | proj | 8 | 1.580 (1.106 to 2.735) | +19.4 (+2.8 to +35.9) | 1.580 / +19.4 |
| exec vs shuf | tab | 30 | 1.009 (1.002 to 1.017) | +0.0 (+0.0 to +0.0) | 1.009 / +0.0 |
| exec vs shuf | all | 36 | 1.242 (1.040 to 1.557) | +10.3 (+0.0 to +21.3) | 1.242 / +10.3 |
