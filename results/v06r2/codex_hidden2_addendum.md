# v0.6 round 2, codex_hidden2: addendum by the holder's groups

Attached to the results locked at commit a79545b; the locked files are unchanged. The group labels were released by the holder after the lock.
30 new policies, 1600 cases each, 3 seeds, budgets 4, 8, 16, 32, 64, 128, 256, 512, 724, 1024, 1600. bank3a is the system under test and chooses its audits; scratch and bank3 audit at random.

| Group (holder's label) | Policies | Cases changed from the nearest past policy |
|---|---|---|
| repeat | p038 p046 p048 p051 p062 p065 | 0, 0, 0, 0, 0, 0 |
| local amendment | p037 p040 p041 p043 p052 p055 p059 p061 | 50, 8, 200, 200, 50, 8, 1, 1 |
| scattered amendment | p047 p049 p057 p058 | 1, 8, 50, 200 |
| far variant | p044 p045 p053 p056 p060 p066 | 672, 1020, 1000, 1056, 1085, 800 |
| new shape | p039 p042 p050 p054 p063 p064 | 1136, 1032, 1104, 1130, 1048, 1096 |

## Exact-learning cost: audits until every case is right

Each cell: median over policies of the per-policy median over seeds, then (smallest to largest over every policy and seed). Budgets are a grid, so a cost is the first grid point that reaches the mark.

| Group | scratch | recognise | amend | parts | bank3 | bank3a | index |
|---|---|---|---|---|---|---|---|
| repeat | 1600 (1024 to 1600) | 4 (4 to 8) | 4 (4 to 8) | 1024 (512 to 1600) | 4 (4 to 8) | 4 (4 to 8) | 1600 (1600 to 1600) |
| local amendment | 1600 (1600 to 1600) | never (never to never) | 1600 (512 to 1600) | 1600 (724 to 1600) | 1600 (512 to 1600) | 618 (128 to 1600) | 1600 (1600 to 1600) |
| scattered amendment | 1600 (1600 to 1600) | never (never to never) | 1600 (512 to 1600) | 1600 (1024 to 1600) | 1600 (512 to 1600) | 1600 (64 to 1600) | 1600 (1600 to 1600) |
| far variant | 1600 (1024 to 1600) | never (never to never) | 1600 (1600 to 1600) | 1600 (1600 to 1600) | 1600 (1024 to 1600) | 1600 (1024 to 1600) | 1600 (1600 to 1600) |
| new shape | 1600 (1600 to 1600) | never (never to never) | 1600 (1600 to 1600) | 1600 (1600 to 1600) | 1600 (1600 to 1600) | 1600 (1600 to 1600) | 1600 (1600 to 1600) |

## Audits until 99% of cases are right

Each cell: median over policies of the per-policy median over seeds, then (smallest to largest over every policy and seed). Budgets are a grid, so a cost is the first grid point that reaches the mark.

| Group | scratch | recognise | amend | parts | bank3 | bank3a | index |
|---|---|---|---|---|---|---|---|
| repeat | 1024 (1024 to 1600) | 4 (4 to 8) | 4 (4 to 8) | 724 (512 to 1024) | 4 (4 to 8) | 4 (4 to 8) | 1600 (1600 to 1600) |
| local amendment | 1600 (724 to 1600) | never (4 to never) | 364 (4 to 1600) | 874 (512 to 1600) | 364 (4 to 1600) | 130 (4 to 724) | 1600 (1600 to 1600) |
| scattered amendment | 1312 (724 to 1600) | never (4 to never) | 802 (4 to 1600) | 1312 (724 to 1600) | 802 (4 to 1600) | 802 (4 to 1600) | 1600 (1600 to 1600) |
| far variant | 1024 (724 to 1600) | never (never to never) | 1600 (1600 to 1600) | 1600 (724 to 1600) | 1024 (724 to 1600) | 1024 (724 to 1600) | 1600 (1600 to 1600) |
| new shape | 1600 (1600 to 1600) | never (never to never) | 1600 (1600 to 1600) | 1600 (1600 to 1600) | 1600 (1600 to 1600) | 1600 (1600 to 1600) | 1600 (1600 to 1600) |

## Exact-learning cost of bank3a by amendment size

| Group | Cases changed | Policy | bank3a, each seed | scratch, each seed |
|---|---|---|---|---|
| local amendment | 1 | p059 | 256, 1600, 1600 | 1600, 1600, 1600 |
| local amendment | 1 | p061 | 724, 1600, 512 | 1600, 1600, 1600 |
| local amendment | 8 | p040 | 1600, 256, 128 | 1600, 1600, 1600 |
| local amendment | 8 | p055 | 724, 512, 256 | 1600, 1600, 1600 |
| local amendment | 50 | p037 | 256, 256, 724 | 1600, 1600, 1600 |
| local amendment | 50 | p052 | 512, 256, 512 | 1600, 1600, 1600 |
| local amendment | 200 | p041 | 724, 724, 724 | 1600, 1600, 1600 |
| local amendment | 200 | p043 | 724, 724, 724 | 1600, 1600, 1600 |
| scattered amendment | 1 | p047 | 64, 1024, 1600 | 1600, 1600, 1600 |
| scattered amendment | 8 | p049 | 1600, 1600, 1600 | 1600, 1600, 1600 |
| scattered amendment | 50 | p057 | 1600, 1600, 1600 | 1600, 1600, 1600 |
| scattered amendment | 200 | p058 | 1600, 1600, 1600 | 1600, 1600, 1600 |

## Worst interim accuracy against keeping the old rule

Keeping the old rule means answering every case with the nearest past policy: it is right on (cases - cases changed) / cases. Worst interim is the lowest share of cases right at any budget before the full table.
Columns: mean old-rule accuracy; then for each learner the mean over policies of the per-policy worst (over seeds and budgets below 1,600), the single worst cell, and the share of policy-seed-budget cells that fall below the old rule.

| Group | Old rule, % right | scratch: mean worst / single worst / cells below old rule | bank3: mean worst / single worst / cells below old rule | bank3a: mean worst / single worst / cells below old rule |
|---|---|---|---|---|
| repeat | 100.00 | 28.35 / 24.44 / 98% | 87.11 / 59.50 / 1% | 87.11 / 59.50 / 1% |
| local amendment | 95.95 | 28.71 / 22.50 / 92% | 69.19 / 52.81 / 8% | 61.77 / 28.00 / 14% |
| scattered amendment | 95.95 | 24.13 / 21.19 / 93% | 59.47 / 16.50 / 29% | 59.52 / 16.50 / 22% |
| far variant | 41.32 | 27.01 / 25.31 / 31% | 24.68 / 21.00 / 23% | 24.95 / 23.56 / 26% |
| new shape | 31.81 | 23.55 / 21.88 / 39% | 22.84 / 21.50 / 41% | 23.02 / 21.50 / 37% |

### bank3a against the old rule at each budget (mean % right minus old-rule % right; lowest single cell in brackets)

| Group | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 724 | 1024 | 1600 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| repeat | -4.30 (-40.50) | +0.00 (+0.00) | +0.00 (+0.00) | +0.00 (+0.00) | +0.00 (+0.00) | +0.00 (+0.00) | +0.00 (+0.00) | +0.00 (+0.00) | +0.00 (+0.00) | +0.00 (+0.00) | +0.00 (+0.00) |
| local amendment | -8.91 (-43.25) | -2.45 (-59.50) | +0.18 (-0.19) | +0.26 (-1.44) | -0.67 (-6.06) | -2.05 (-13.12) | -1.97 (-22.25) | +3.72 (+0.00) | +4.02 (+0.00) | +4.03 (+0.00) | +4.05 (+0.06) |
| scattered amendment | -20.85 (-71.00) | -7.69 (-57.50) | -0.43 (-2.06) | -0.56 (-4.69) | -0.46 (-4.63) | -0.37 (-4.06) | +0.28 (+0.00) | +1.12 (+0.00) | +1.72 (+0.00) | +2.44 (+0.00) | +4.05 (+0.06) |
| far variant | -11.44 (-30.38) | -6.38 (-16.19) | -1.86 (-25.13) | +6.55 (-7.63) | +13.22 (+0.56) | +23.67 (+1.50) | +38.58 (+9.44) | +50.41 (+18.75) | +54.95 (+24.19) | +57.53 (+33.69) | +58.68 (+42.00) |
| new shape | -6.64 (-13.69) | -5.98 (-12.06) | -3.69 (-9.06) | -1.27 (-8.06) | +2.46 (-4.44) | +8.56 (-1.50) | +19.18 (+6.06) | +37.91 (+20.94) | +48.33 (+30.38) | +59.07 (+42.12) | +68.19 (+64.50) |

## Cautious mode, bank3a: answer coverage % / error among answered cases %

Coverage is the share of cases answered. Error is wrong answers divided by answers given, pooled over the group's policies and seeds; n/a where nothing was answered.

| Group | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 724 | 1024 | 1600 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| repeat | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 |
| local amendment | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 48.0 / 0.48 | 57.1 / 0.31 | 66.0 / 0.10 | 82.3 / 0.04 | 86.1 / 0.02 | 91.0 / 0.01 | 100.0 / 0.00 |
| scattered amendment | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 36.0 / 0.26 | 61.4 / 0.59 | 71.4 / 0.72 | 81.3 / 0.67 | 88.8 / 1.04 | 90.0 / 0.35 | 100.0 / 0.00 |
| far variant | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 4.0 / 0.00 | 8.0 / 0.00 | 16.0 / 0.00 | 35.1 / 0.37 | 64.2 / 0.31 | 94.2 / 0.22 | 100.0 / 0.00 |
| new shape | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 4.0 / 0.00 | 8.0 / 0.00 | 16.0 / 0.00 | 32.0 / 0.00 | 45.2 / 0.00 | 64.0 / 0.00 | 100.0 / 0.00 |

## Cautious mode, bank3: answer coverage % / error among answered cases %

Coverage is the share of cases answered. Error is wrong answers divided by answers given, pooled over the group's policies and seeds; n/a where nothing was answered.

| Group | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 724 | 1024 | 1600 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| repeat | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 | 100.0 / 0.00 |
| local amendment | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 51.9 / 0.65 | 76.4 / 0.81 | 93.9 / 0.68 | 92.1 / 0.09 | 91.9 / 0.01 | 93.4 / 0.01 | 100.0 / 0.00 |
| scattered amendment | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 36.0 / 0.26 | 53.8 / 0.24 | 64.1 / 0.48 | 79.5 / 0.62 | 82.6 / 0.45 | 87.8 / 0.24 | 100.0 / 0.00 |
| far variant | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 4.0 / 0.00 | 8.0 / 0.00 | 16.0 / 0.00 | 32.0 / 0.00 | 67.3 / 0.68 | 94.5 / 0.21 | 100.0 / 0.00 |
| new shape | 0.2 / 0.00 | 0.5 / 0.00 | 1.0 / 0.00 | 2.0 / 0.00 | 4.0 / 0.00 | 8.0 / 0.00 | 16.0 / 0.00 | 32.0 / 0.00 | 45.2 / 0.00 | 64.0 / 0.00 | 100.0 / 0.00 |

## Cautious mode, scratch: answer coverage % / error among answered cases %

Coverage is the share of cases answered. Error is wrong answers divided by answers given, pooled over the group's policies and seeds; n/a where nothing was answered.

| Group | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 724 | 1024 | 1600 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| repeat | 69.2 / 65.66 | 69.6 / 62.99 | 69.6 / 59.21 | 70.4 / 53.08 | 65.0 / 41.20 | 63.9 / 25.81 | 71.3 / 15.17 | 83.5 / 3.62 | 92.1 / 0.78 | 98.4 / 0.05 | 100.0 / 0.00 |
| local amendment | 71.7 / 67.17 | 68.4 / 62.58 | 68.9 / 58.74 | 69.5 / 52.68 | 66.8 / 44.25 | 63.3 / 32.49 | 65.9 / 21.03 | 74.9 / 7.58 | 85.3 / 2.41 | 94.9 / 0.44 | 100.0 / 0.00 |
| scattered amendment | 70.9 / 69.80 | 69.9 / 66.03 | 70.2 / 62.10 | 68.8 / 56.15 | 63.6 / 45.72 | 60.0 / 27.36 | 68.9 / 15.09 | 80.3 / 6.07 | 88.0 / 3.05 | 94.7 / 1.56 | 100.0 / 0.00 |
| far variant | 72.4 / 68.94 | 70.2 / 65.40 | 70.1 / 60.91 | 70.8 / 51.98 | 67.0 / 42.81 | 63.9 / 28.62 | 68.2 / 15.52 | 81.2 / 4.50 | 89.8 / 1.32 | 97.2 / 0.14 | 100.0 / 0.00 |
| new shape | 75.1 / 74.06 | 70.6 / 73.15 | 68.9 / 71.48 | 68.1 / 68.38 | 57.4 / 61.96 | 50.1 / 49.06 | 52.3 / 32.54 | 63.4 / 16.15 | 74.5 / 8.98 | 86.7 / 3.46 | 99.9 / 0.00 |
