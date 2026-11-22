# v0.8 tables: results/v08/dev/latent

## proj: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direct | 1 | 170 | 58.2 | 47.1 | 85.3 | 41.4 | 85.6 | 7.79 | 14.67 | 2.323 | 848 | 0.394 | 0.559 | 0.64 |
| latent3 | 1 | 170 | 28.8 | 24.7 | 90.0 | 69.9 | 34.5 | 8.22 | 16.93 | 7.531 | 984 | 0.592 | 0.616 | 0.92 |

## tab: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direct | 1 | 150 | 98.0 | 96.0 | 86.7 | 2.3 | 545.3 | 3.49 | 6.33 | 0.020 | 116 | 0.128 | 0.134 | 0.18 |
| latent3 | 1 | 150 | 64.7 | 63.3 | 86.0 | 39.5 | 299.2 | 3.63 | 6.53 | 0.639 | 130 | 0.143 | 0.199 | 0.21 |

## all: every arm, seeds pooled

| Arm | Seeds | Jobs | Verified % | First attempt % | Answered % | Error among answers % | Verified jobs / min | Scripts / job | Operations / job | Failed edits / solved job | Tokens / job | Latency median s | p90 s | max s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direct | 1 | 320 | 76.9 | 70.0 | 85.9 | 22.9 | 172.5 | 5.77 | 10.76 | 0.947 | 505 | 0.134 | 0.539 | 0.64 |
| latent3 | 1 | 320 | 45.6 | 42.8 | 88.1 | 56.0 | 83.7 | 6.07 | 12.05 | 2.952 | 584 | 0.200 | 0.607 | 0.92 |

## Each seed: verified % / verified jobs per minute

| Arm | Seed | proj | tab |
|---|---|---|---|
| direct | 1 | 58.2 / 85.6 | 98.0 / 545.3 |
| latent3 | 1 | 28.8 / 34.5 | 64.7 / 299.2 |

## By group: verified % (answered % / error among answers %), seeds pooled

| Domain | Group | Jobs | direct | latent3 |
|---|---|---|---|---|
| proj | altered | 30 | 70.0 (97 / 28) | 13.3 (83 / 84) |
| proj | familiar | 60 | 65.0 (92 / 29) | 23.3 (93 / 75) |
| proj | newmech | 40 | 12.5 (88 / 86) | 20.0 (88 / 77) |
| proj | unans | 20 | 70.0 (30 / 100) | 15.0 (85 / 100) |
| proj | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) |
| tab | familiar | 50 | 100.0 (100 / 0) | 70.0 (100 / 30) |
| tab | scattered | 40 | 92.5 (100 / 8) | 20.0 (95 / 79) |
| tab | stale | 20 | 100.0 (100 / 0) | 75.0 (100 / 25) |
| tab | unans | 20 | 100.0 (0 / 0) | 95.0 (5 / 100) |
| tab | valid | 20 | 100.0 (100 / 0) | 100.0 (100 / 0) |

## proj faults by route: verified %

local = the fault is in agg or order; deep-direct = upstream and the failing check reports count or groups; deep-indirect = upstream but the check only reports total or first (looks like a local fault).

| Route | direct | latent3 |
|---|---|---|
| deep-direct | 45.7 | 18.6 |
| deep-indirect | 41.7 | 12.5 |
| local | 63.9 | 27.8 |

## Paired contrasts (first arm against second)

Rate ratio = verified jobs per minute of the first arm divided by the second. Intervals are 95%, resampling task families.

| Contrast | Domain | Families | Rate ratio (interval) | Verified share, points (interval) | Each seed: ratio / points |
|---|---|---|---|---|---|
| latent3 vs direct | proj | 8 | 0.403 (0.217 to 0.616) | -29.4 (-47.9 to -14.2) | 0.403 / -29.4 |
| latent3 vs direct | tab | 32 | 0.549 (0.382 to 0.663) | -33.3 (-51.3 to -21.0) | 0.549 / -33.3 |
| latent3 vs direct | all | 38 | 0.486 (0.348 to 0.603) | -31.3 (-44.7 to -21.3) | 0.486 / -31.2 |
