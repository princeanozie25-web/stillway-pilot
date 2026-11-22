# v0.8 tables: results/v08/codex_hold_rev2, view: seed 1 of core/base, core/exec, core/shuf, expl/obsonly, expl/reconly

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 1 | 119 | 37.8 | 37.0 | 78.2 | 62.4 | 57.6 | 7.68 | 12.41 | 2.244 | 867 | 0.388 | 0.610 | 1.12 |
| exec | 1 | 119 | 52.1 | 42.9 | 75.6 | 44.4 | 78.4 | 7.57 | 14.13 | 2.387 | 850 | 0.399 | 0.549 | 0.63 |
| obsonly | 1 | 119 | 55.5 | 55.5 | 84.9 | 45.5 | 99.8 | 6.74 | 10.78 | 0.879 | 638 | 0.316 | 0.403 | 0.72 |
| reconly | 1 | 119 | 38.7 | 36.1 | 68.9 | 56.1 | 55.3 | 7.85 | 15.08 | 3.935 | 930 | 0.455 | 0.551 | 0.65 |
| shuf | 1 | 119 | 33.6 | 24.4 | 66.4 | 53.2 | 46.5 | 8.00 | 15.71 | 5.175 | 976 | 0.461 | 0.598 | 0.69 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 1 | 101 | 93.1 | 93.1 | 83.2 | 2.4 | 495.4 | 3.57 | 6.43 | 0.128 | 117 | 0.129 | 0.136 | 0.17 |
| exec | 1 | 101 | 100.0 | 94.1 | 88.1 | 0.0 | 530.5 | 3.58 | 6.45 | 0.109 | 120 | 0.128 | 0.137 | 0.19 |
| obsonly | 1 | 101 | 94.1 | 94.1 | 88.1 | 6.7 | 513.2 | 3.52 | 6.32 | 0.116 | 114 | 0.128 | 0.135 | 0.15 |
| reconly | 1 | 101 | 100.0 | 93.1 | 88.1 | 0.0 | 531.0 | 3.59 | 6.47 | 0.119 | 121 | 0.128 | 0.137 | 0.18 |
| shuf | 1 | 101 | 100.0 | 92.1 | 88.1 | 0.0 | 530.0 | 3.60 | 6.45 | 0.129 | 121 | 0.128 | 0.137 | 0.18 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 1 | 220 | 63.2 | 62.7 | 80.5 | 33.9 | 143.2 | 5.80 | 9.66 | 0.813 | 522 | 0.171 | 0.465 | 1.12 |
| exec | 1 | 220 | 74.1 | 66.4 | 81.4 | 22.3 | 166.2 | 5.74 | 10.60 | 0.975 | 515 | 0.175 | 0.539 | 0.63 |
| obsonly | 1 | 220 | 73.2 | 73.2 | 86.4 | 27.4 | 190.2 | 5.26 | 8.73 | 0.429 | 397 | 0.136 | 0.391 | 0.72 |
| reconly | 1 | 220 | 66.8 | 62.3 | 77.7 | 26.9 | 143.9 | 5.90 | 11.13 | 1.313 | 559 | 0.176 | 0.539 | 0.65 |
| shuf | 1 | 220 | 64.1 | 55.5 | 76.4 | 25.0 | 134.2 | 5.98 | 11.45 | 1.560 | 584 | 0.176 | 0.540 | 0.69 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| base | 1 | 37.8 / 57.6 | 93.1 / 495.4 |
| exec | 1 | 52.1 / 78.4 | 100.0 / 530.5 |
| obsonly | 1 | 55.5 / 99.8 | 94.1 / 513.2 |
| reconly | 1 | 38.7 / 55.3 | 100.0 / 531.0 |
| shuf | 1 | 33.6 / 46.5 | 100.0 / 530.0 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | base | exec | obsonly | reconly | shuf |
|---|---|---|---|---|---|---|---|
| proj | altered | 20 | 20.0 (85 / 76) | 50.0 (85 / 41) | 45.0 (95 / 53) | 25.0 (80 / 69) | 25.0 (60 / 58) |
| proj | familiar | 40 | 40.0 (75 / 47) | 57.5 (78 / 26) | 65.0 (92 / 30) | 37.5 (78 / 52) | 37.5 (65 / 42) |
| proj | later | 10 | 0.0 (90 / 100) | 0.0 (80 / 100) | 0.0 (80 / 100) | 0.0 (60 / 100) | 0.0 (80 / 100) |
| proj | newmech | 25 | 12.0 (92 / 87) | 20.0 (88 / 77) | 32.0 (96 / 67) | 16.0 (60 / 73) | 20.0 (64 / 69) |
| proj | unans | 12 | 83.3 (17 / 100) | 100.0 (0 / 0) | 91.7 (8 / 100) | 83.3 (17 / 100) | 25.0 (42 / 100) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | later | 10 | 50.0 (50 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 25 | 92.0 (100 / 8) | 100.0 (100 / 0) | 76.0 (100 / 24) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | stale | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 12 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | base | exec | obsonly | reconly | shuf |
|---|---|---|---|---|---|
| deep-direct | 18.6 | 32.6 | 34.9 | 18.6 | 27.9 |
| deep-indirect | 50.0 | 40.0 | 30.0 | 60.0 | 40.0 |
| local | 23.8 | 47.6 | 59.5 | 23.8 | 21.4 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| exec vs base | proj | 10 | 1.362 (1.039 to 1.869) | +14.3 (+5.3 to +24.2) | 1.362 / +14.3 |
| exec vs base | tab | 13 | 1.071 (0.980 to 1.284) | +6.9 (+0.0 to +18.3) | 1.071 / +6.9 |
| exec vs base | all | 21 | 1.161 (0.995 to 1.450) | +10.9 (+4.6 to +19.4) | 1.161 / +10.9 |
| obsonly vs base | proj | 10 | 1.732 (1.185 to 2.659) | +17.6 (+4.7 to +31.1) | 1.732 / +17.6 |
| obsonly vs base | tab | 13 | 1.036 (0.925 to 1.253) | +1.0 (-7.8 to +14.0) | 1.036 / +1.0 |
| obsonly vs base | all | 21 | 1.328 (1.067 to 1.767) | +10.0 (+0.5 to +21.8) | 1.328 / +10.0 |
| reconly vs base | proj | 10 | 0.961 (0.800 to 1.152) | +0.8 (-6.5 to +6.4) | 0.961 / +0.8 |
| reconly vs base | tab | 13 | 1.072 (0.976 to 1.288) | +6.9 (+0.0 to +18.3) | 1.072 / +6.9 |
| reconly vs base | all | 21 | 1.005 (0.919 to 1.141) | +3.6 (-1.7 to +10.2) | 1.005 / +3.6 |
| shuf vs base | proj | 10 | 0.807 (0.468 to 1.287) | -4.2 (-20.5 to +9.1) | 0.807 / -4.2 |
| shuf vs base | tab | 13 | 1.070 (0.989 to 1.270) | +6.9 (+0.0 to +18.3) | 1.070 / +6.9 |
| shuf vs base | all | 21 | 0.937 (0.768 to 1.154) | +0.9 (-7.9 to +10.3) | 0.937 / +0.9 |
| exec vs shuf | proj | 10 | 1.687 (0.986 to 3.005) | +18.5 (+0.0 to +39.3) | 1.687 / +18.5 |
| exec vs shuf | tab | 13 | 1.001 (0.989 to 1.014) | +0.0 (+0.0 to +0.0) | 1.001 / +0.0 |
| exec vs shuf | all | 21 | 1.238 (1.002 to 1.537) | +10.0 (+0.0 to +20.1) | 1.238 / +10.0 |
