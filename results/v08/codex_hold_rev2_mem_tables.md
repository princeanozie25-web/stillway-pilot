# v0.8 tables: results/v08/codex_hold_rev2, view: mem/bank_s1, mem/bankguard_s1 with core/base_s1 and core/exec_s1

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bank | 1 | 119 | 89.1 | 86.6 | 84.0 | 6.0 | 317.4 | 2.88 | 19.92 | 0.198 | 194 | 0.078 | 0.393 | 0.69 |
| bankguard | 1 | 119 | 95.0 | 93.3 | 85.7 | 1.0 | 359.1 | 2.28 | 72.71 | 0.071 | 119 | 0.102 | 0.413 | 0.69 |
| base | 1 | 119 | 37.8 | 37.0 | 78.2 | 62.4 | 57.6 | 7.68 | 12.41 | 2.244 | 867 | 0.388 | 0.610 | 1.12 |
| exec | 1 | 119 | 52.1 | 42.9 | 75.6 | 44.4 | 78.4 | 7.57 | 14.13 | 2.387 | 850 | 0.399 | 0.549 | 0.63 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bank | 1 | 101 | 100.0 | 83.2 | 88.1 | 0.0 | 872.1 | 1.91 | 8.19 | 0.050 | 23 | 0.043 | 0.127 | 0.18 |
| bankguard | 1 | 101 | 100.0 | 83.2 | 88.1 | 0.0 | 869.6 | 1.91 | 8.19 | 0.050 | 23 | 0.043 | 0.129 | 0.17 |
| base | 1 | 101 | 93.1 | 93.1 | 83.2 | 2.4 | 495.4 | 3.57 | 6.43 | 0.128 | 117 | 0.129 | 0.136 | 0.17 |
| exec | 1 | 101 | 100.0 | 94.1 | 88.1 | 0.0 | 530.5 | 3.58 | 6.45 | 0.109 | 120 | 0.128 | 0.137 | 0.19 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bank | 1 | 220 | 94.1 | 85.0 | 85.9 | 3.2 | 460.2 | 2.44 | 14.53 | 0.126 | 116 | 0.076 | 0.383 | 0.69 |
| bankguard | 1 | 220 | 97.3 | 88.6 | 86.8 | 0.5 | 496.7 | 2.11 | 43.09 | 0.061 | 75 | 0.100 | 0.167 | 0.69 |
| base | 1 | 220 | 63.2 | 62.7 | 80.5 | 33.9 | 143.2 | 5.80 | 9.66 | 0.813 | 522 | 0.171 | 0.465 | 1.12 |
| exec | 1 | 220 | 74.1 | 66.4 | 81.4 | 22.3 | 166.2 | 5.74 | 10.60 | 0.975 | 515 | 0.175 | 0.539 | 0.63 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| bank | 1 | 89.1 / 317.4 | 100.0 / 872.1 |
| bankguard | 1 | 95.0 / 359.1 | 100.0 / 869.6 |
| base | 1 | 37.8 / 57.6 | 93.1 / 495.4 |
| exec | 1 | 52.1 / 78.4 | 100.0 / 530.5 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | bank | bankguard | base | exec |
|---|---|---|---|---|---|---|
| proj | altered | 20 | 85.0 (90 / 6) | 85.0 (90 / 6) | 20.0 (85 / 76) | 50.0 (85 / 41) |
| proj | familiar | 40 | 82.5 (88 / 6) | 92.5 (92 / 0) | 40.0 (75 / 47) | 57.5 (78 / 26) |
| proj | later | 10 | 100.0 (100 / 0) | 100.0 (100 / 0) | 0.0 (90 / 100) | 0.0 (80 / 100) |
| proj | newmech | 25 | 88.0 (100 / 12) | 100.0 (100 / 0) | 12.0 (92 / 87) | 20.0 (88 / 77) |
| proj | unans | 12 | 100.0 (0 / 0) | 100.0 (0 / 0) | 83.3 (17 / 100) | 100.0 (0 / 0) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | later | 10 | 100.0 (100 / 0) | 100.0 (100 / 0) | 50.0 (50 / 0) | 100.0 (100 / 0) |
| tab | scattered | 25 | 100.0 (100 / 0) | 100.0 (100 / 0) | 92.0 (100 / 8) | 100.0 (100 / 0) |
| tab | stale | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 12 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | bank | bankguard | base | exec |
|---|---|---|---|---|
| deep-direct | 69.8 | 86.0 | 18.6 | 32.6 |
| deep-indirect | 100.0 | 100.0 | 50.0 | 40.0 |
| local | 100.0 | 100.0 | 23.8 | 47.6 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| bank vs exec | proj | 10 | 4.046 (2.030 to 8.953) | +37.0 (+18.6 to +55.5) | 4.046 / +37.0 |
| bank vs exec | tab | 13 | 1.644 (1.088 to 2.797) | +0.0 (+0.0 to +0.0) | 1.644 / +0.0 |
| bank vs exec | all | 21 | 2.769 (1.545 to 4.967) | +20.0 (+6.5 to +34.9) | 2.769 / +20.0 |
| bankguard vs exec | proj | 10 | 4.578 (2.239 to 9.495) | +42.9 (+23.4 to +61.8) | 4.578 / +42.9 |
| bankguard vs exec | tab | 13 | 1.639 (1.083 to 2.801) | +0.0 (+0.0 to +0.0) | 1.639 / +0.0 |
| bankguard vs exec | all | 21 | 2.989 (1.703 to 5.102) | +23.2 (+8.6 to +38.6) | 2.989 / +23.2 |
| base vs exec | proj | 10 | 0.734 (0.535 to 0.962) | -14.3 (-24.2 to -5.3) | 0.734 / -14.3 |
| base vs exec | tab | 13 | 0.934 (0.779 to 1.021) | -6.9 (-18.3 to +0.0) | 0.934 / -6.9 |
| base vs exec | all | 21 | 0.861 (0.690 to 1.005) | -10.9 (-19.4 to -4.6) | 0.861 / -10.9 |
