# Exploratory: past policies as inputs, codex_hidden

Written after the outputs were locked and the breakdown revealed. 20 new policies, 3 seeds, passive audits, budgets [4, 8, 16, 32, 64, 128, 256, 512, 1440]. Inputs: scratch 22, feat 166.

## Audits to 99% of cases right (median of seeds), per policy

| Policy | Group | Shape | Distance to nearest past | scratch | feat | patch | pick |
|---|---|---|---|---|---|---|---|
| p037 | Variant | Threshold count | 412 | 512 | 512 | 1440 | 1440 |
| p038 | Variant | Threshold count | 508 | 512 | 1440 | 1440 | 512 |
| p039 | Variant | Pair comparisons | 680 | 256 | 512 | 1440 | 256 |
| p040 | Repeat | Modular tests | 0 | 1440 | 512 | 4 | 8 |
| p041 | New shape | Distance and modular test | 1028 | 1440 | 1440 | 1440 | 1440 |
| p042 | Variant | Max and offset | 788 | 1440 | 1440 | 1440 | 1440 |
| p043 | New shape | Distance and modular test | 970 | 1440 | 1440 | 1440 | 1440 |
| p044 | New shape | Order statistic | 1048 | 512 | 1440 | 1440 | 512 |
| p045 | Repeat | Modular tests | 0 | 1440 | 512 | 8 | 8 |
| p046 | Variant | Modular tests | 8 | 1440 | 512 | 4 | 4 |
| p047 | Variant | Modular tests | 194 | 1440 | 512 | 1440 | 512 |
| p048 | New shape | Order statistic | 1052 | 512 | 1440 | 1440 | 512 |
| p049 | Repeat | Threshold count | 0 | 256 | 512 | 4 | 4 |
| p050 | New shape | Order statistic | 1040 | 512 | 1440 | 1440 | 512 |
| p051 | Repeat | Pair comparisons | 0 | 256 | 512 | 8 | 8 |
| p052 | Repeat | Modular tests | 0 | 1440 | 512 | 4 | 4 |
| p053 | Repeat | Max and offset | 0 | 1440 | 512 | 4 | 8 |
| p054 | Variant | Max and offset | 672 | 1440 | 1440 | 1440 | 1440 |
| p055 | New shape | Distance and modular test | 950 | 1440 | 1440 | 1440 | 1440 |
| p056 | Variant | Pair comparisons | 576 | 256 | 512 | 1440 | 256 |

## By group: median audits to 99%; policies on which the learner needs fewer / same / more audits than scratch

| Group | Policies | scratch | feat | patch | pick | feat vs scratch | pick vs scratch |
|---|---|---|---|---|---|---|---|
| Variant | 8 | 976 | 512 | 1440 | 512 | 2 / 3 / 3 | 2 / 5 / 1 |
| Repeat | 6 | 1440 | 512 | 4 | 8 | 4 / 0 / 2 | 6 / 0 / 0 |
| New shape | 6 | 976 | 1440 | 1440 | 976 | 0 / 3 / 3 | 0 / 6 / 0 |
| shape: Threshold count | 3 | 512 | 512 | 1440 | 512 | 0 / 1 / 2 | 1 / 1 / 1 |
| shape: Pair comparisons | 3 | 256 | 512 | 1440 | 256 | 0 / 0 / 3 | 1 / 2 / 0 |
| shape: Modular tests | 5 | 1440 | 512 | 4 | 8 | 5 / 0 / 0 | 5 / 0 / 0 |
| shape: Distance and modular test | 3 | 1440 | 1440 | 1440 | 1440 | 0 / 3 / 0 | 0 / 3 / 0 |
| shape: Max and offset | 3 | 1440 | 1440 | 1440 | 1440 | 1 / 2 / 0 | 1 / 2 / 0 |
| shape: Order statistic | 3 | 512 | 1440 | 1440 | 512 | 0 / 0 / 3 | 0 / 3 / 0 |

## Mean share of cases right at each budget (%)

| Group | Learner | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 1440 |
|---|---|---|---|---|---|---|---|---|---|---|
| Variant | scratch | 35.0 | 38.3 | 43.8 | 50.8 | 64.5 | 77.1 | 87.2 | 98.2 | 100.0 |
| Variant | feat | 41.3 | 45.8 | 52.0 | 60.5 | 70.5 | 79.5 | 91.2 | 97.9 | 100.0 |
| Variant | patch | 48.8 | 55.0 | 59.3 | 62.5 | 65.9 | 69.5 | 72.4 | 78.2 | 100.0 |
| Variant | pick | 45.9 | 55.9 | 58.6 | 63.6 | 74.1 | 85.4 | 94.5 | 99.4 | 100.0 |
| Repeat | scratch | 33.8 | 34.9 | 39.0 | 45.6 | 58.9 | 70.5 | 80.6 | 97.4 | 100.0 |
| Repeat | feat | 44.5 | 50.8 | 60.7 | 68.2 | 79.6 | 88.0 | 96.2 | 99.5 | 100.0 |
| Repeat | patch | 78.2 | 97.8 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| Repeat | pick | 72.4 | 95.8 | 98.2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| New shape | scratch | 41.4 | 45.0 | 50.1 | 55.7 | 63.5 | 73.8 | 84.8 | 97.6 | 100.0 |
| New shape | feat | 37.5 | 41.6 | 47.5 | 51.4 | 58.2 | 66.1 | 77.8 | 90.1 | 100.0 |
| New shape | patch | 25.2 | 25.2 | 28.0 | 28.6 | 29.9 | 33.5 | 40.6 | 53.7 | 100.0 |
| New shape | pick | 27.3 | 31.5 | 46.5 | 50.4 | 65.8 | 75.6 | 85.5 | 97.6 | 100.0 |

## Cautious mode, mean over budgets below the full table: wrong / abstained (%)

| Group | scratch | feat | pick |
|---|---|---|---|
| Variant | 25.17 / 21.8 | 19.62 / 22.0 | 23.29 / 8.1 |
| Repeat | 27.54 / 24.8 | 14.82 / 21.1 | 3.77 / 0.7 |
| New shape | 23.83 / 21.0 | 26.67 / 23.6 | 32.15 / 13.9 |

Pick used: patch 52%, scratch 28%, feat 21%.
