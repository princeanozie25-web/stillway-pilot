# v0.8 tables: results/v08/codex_hold_rev2, view: mem/ with core/base_s1 and core/exec_s1, jobs of group later removed

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bank | 1 | 109 | 88.1 | 85.3 | 82.6 | 6.7 | 298.7 | 3.06 | 20.55 | 0.219 | 212 | 0.079 | 0.408 | 0.69 |
| bankguard | 1 | 109 | 94.5 | 92.7 | 84.4 | 1.1 | 346.8 | 2.39 | 71.45 | 0.078 | 130 | 0.102 | 0.415 | 0.69 |
| base | 1 | 109 | 41.3 | 40.4 | 77.1 | 58.3 | 62.9 | 7.68 | 12.43 | 2.000 | 873 | 0.388 | 0.650 | 1.12 |
| exec | 1 | 109 | 56.9 | 46.8 | 75.2 | 39.0 | 87.7 | 7.44 | 13.72 | 1.968 | 821 | 0.388 | 0.548 | 0.63 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bank | 1 | 91 | 100.0 | 86.8 | 86.8 | 0.0 | 927.4 | 1.79 | 8.10 | 0.000 | 20 | 0.043 | 0.126 | 0.13 |
| bankguard | 1 | 91 | 100.0 | 86.8 | 86.8 | 0.0 | 922.7 | 1.79 | 8.10 | 0.000 | 20 | 0.043 | 0.128 | 0.13 |
| base | 1 | 91 | 97.8 | 97.8 | 86.8 | 2.5 | 540.3 | 3.47 | 6.31 | 0.022 | 113 | 0.129 | 0.135 | 0.14 |
| exec | 1 | 91 | 100.0 | 93.4 | 86.8 | 0.0 | 538.8 | 3.54 | 6.44 | 0.066 | 120 | 0.128 | 0.137 | 0.19 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bank | 1 | 200 | 93.5 | 86.0 | 84.5 | 3.6 | 445.7 | 2.48 | 14.88 | 0.112 | 125 | 0.076 | 0.385 | 0.69 |
| bankguard | 1 | 200 | 97.0 | 90.0 | 85.5 | 0.6 | 490.3 | 2.12 | 42.62 | 0.041 | 80 | 0.100 | 0.156 | 0.69 |
| base | 1 | 200 | 67.0 | 66.5 | 81.5 | 31.3 | 152.3 | 5.76 | 9.64 | 0.687 | 527 | 0.138 | 0.462 | 1.12 |
| exec | 1 | 200 | 76.5 | 68.0 | 80.5 | 19.9 | 174.7 | 5.67 | 10.40 | 0.837 | 502 | 0.175 | 0.538 | 0.63 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| bank | 1 | 88.1 / 298.7 | 100.0 / 927.4 |
| bankguard | 1 | 94.5 / 346.8 | 100.0 / 922.7 |
| base | 1 | 41.3 / 62.9 | 97.8 / 540.3 |
| exec | 1 | 56.9 / 87.7 | 100.0 / 538.8 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | bank | bankguard | base | exec |
|---|---|---|---|---|---|---|
| proj | altered | 20 | 85.0 (90 / 6) | 85.0 (90 / 6) | 20.0 (85 / 76) | 50.0 (85 / 41) |
| proj | familiar | 40 | 82.5 (88 / 6) | 92.5 (92 / 0) | 40.0 (75 / 47) | 57.5 (78 / 26) |
| proj | newmech | 25 | 88.0 (100 / 12) | 100.0 (100 / 0) | 12.0 (92 / 87) | 20.0 (88 / 77) |
| proj | unans | 12 | 100.0 (0 / 0) | 100.0 (0 / 0) | 83.3 (17 / 100) | 100.0 (0 / 0) |
| proj | valid | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 30 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
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
| local | 100.0 | 100.0 | 31.2 | 62.5 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| bank vs exec | proj | 8 | 3.405 (1.651 to 7.021) | +31.2 (+12.1 to +47.3) | 3.405 / +31.2 |
| bank vs exec | tab | 11 | 1.721 (1.113 to 3.159) | +0.0 (+0.0 to +0.0) | 1.721 / +0.0 |
| bank vs exec | all | 17 | 2.551 (1.509 to 4.575) | +17.0 (+3.2 to +30.4) | 2.551 / +17.0 |
| bankguard vs exec | proj | 8 | 3.953 (1.909 to 7.423) | +37.6 (+16.3 to +53.8) | 3.953 / +37.6 |
| bankguard vs exec | tab | 11 | 1.713 (1.106 to 3.154) | +0.0 (+0.0 to +0.0) | 1.713 / +0.0 |
| bankguard vs exec | all | 17 | 2.806 (1.606 to 4.870) | +20.5 (+6.0 to +35.8) | 2.806 / +20.5 |
| base vs exec | proj | 8 | 0.717 (0.513 to 0.943) | -15.6 (-26.4 to -6.4) | 0.717 / -15.6 |
| base vs exec | tab | 11 | 1.003 (0.972 to 1.028) | -2.2 (-6.7 to +0.0) | 1.003 / -2.2 |
| base vs exec | all | 17 | 0.871 (0.712 to 1.008) | -9.5 (-16.7 to -3.6) | 0.871 / -9.5 |
