# v0.8 tables: results/v08/bench_small

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| core | 1 | 43 | 53.5 | 48.8 | 79.1 | 47.1 | 62.8 | 7.98 | 14.60 | 2.348 | 862 | 0.559 | 0.683 | 0.77 |
| search | 1 | 43 | 100.0 | 11.6 | 88.4 | 0.0 | 551.2 | 1.00 | 50.84 | 0.884 | 0 | 0.109 | 0.126 | 0.14 |
| teacher | 1 | 43 | 100.0 | 100.0 | 88.4 | 0.0 | 150.8 | 7.02 | 11.05 | 0.000 | 621 | 0.448 | 0.529 | 0.54 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| core | 1 | 37 | 97.3 | 97.3 | 86.5 | 3.1 | 438.8 | 3.46 | 6.22 | 0.000 | 113 | 0.158 | 0.166 | 0.17 |
| search | 1 | 37 | 100.0 | 100.0 | 86.5 | 0.0 | 1126.5 | 1.00 | 6.35 | 0.189 | 0 | 0.053 | 0.057 | 0.06 |
| teacher | 1 | 37 | 100.0 | 100.0 | 86.5 | 0.0 | 497.0 | 3.46 | 6.22 | 0.000 | 113 | 0.142 | 0.150 | 0.16 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| core | 1 | 80 | 73.8 | 71.2 | 82.5 | 25.8 | 131.6 | 5.89 | 10.72 | 0.915 | 515 | 0.168 | 0.671 | 0.77 |
| search | 1 | 80 | 100.0 | 52.5 | 87.5 | 0.0 | 721.6 | 1.00 | 30.26 | 0.562 | 0 | 0.089 | 0.121 | 0.14 |
| teacher | 1 | 80 | 100.0 | 100.0 | 87.5 | 0.0 | 222.5 | 5.38 | 8.81 | 0.000 | 386 | 0.153 | 0.464 | 0.54 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| core | 0 | 53.5 / 62.8 | 97.3 / 438.8 |
| search | 0 | 100.0 / 551.2 | 100.0 / 1126.5 |
| teacher | 0 | 100.0 / 150.8 | 100.0 / 497.0 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | core | search | teacher |
|---|---|---|---|---|---|
| proj | altered | 8 | 37.5 (88 / 57) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| proj | familiar | 15 | 60.0 (100 / 40) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| proj | newmech | 10 | 10.0 (70 / 86) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| proj | unans | 5 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| proj | valid | 5 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 12 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | scattered | 10 | 90.0 (100 / 10) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | stale | 5 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | unans | 5 | 100.0 (0 / 0) | 100.0 (0 / 0) | 100.0 (0 / 0) |
| tab | valid | 5 | 100.0 (100 / 0) | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | core | search | teacher |
|---|---|---|---|
| deep-direct | 30.0 | 100.0 | 100.0 |
| deep-indirect | 50.0 | 100.0 | 100.0 |
| local | 57.1 | 100.0 | 100.0 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| core vs teacher | proj | 8 | 0.416 (0.230 to 0.654) | -46.5 (-68.6 to -21.6) | 0.416 / -46.5 |
| core vs teacher | tab | 17 | 0.883 (0.810 to 0.917) | -2.7 (-11.1 to +0.0) | 0.883 / -2.7 |
| core vs teacher | all | 23 | 0.591 (0.404 to 0.790) | -26.2 (-46.7 to -8.3) | 0.591 / -26.2 |
| search vs teacher | proj | 8 | 3.655 (2.766 to 4.248) | +0.0 (+0.0 to +0.0) | 3.655 / +0.0 |
| search vs teacher | tab | 17 | 2.267 (1.870 to 2.761) | +0.0 (+0.0 to +0.0) | 2.267 / +0.0 |
| search vs teacher | all | 23 | 3.244 (2.436 to 3.897) | +0.0 (+0.0 to +0.0) | 3.244 / +0.0 |
