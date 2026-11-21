# Hidden family: locked results regrouped by the author's breakdown

Group and shape labels are Codex's, given after commit b7120cd. Numbers are from the locked raw file; none was recomputed with new runs.

## Median audits to 99% of cases right, passive audits

| Group | Policies | Distance to nearest past policy (cases of 1,440) | scratch | bank_row | tables | programs | selector | selector vs scratch: fewer / same / more |
|---|---|---|---|---|---|---|---|---|
| Variant | 8 | 8 to 788 | 512 | never | 384 | 976 | 384 | 3 / 4 / 1 |
| Repeat | 6 | 0 to 0 | 1440 | 256 | 4 | 1440 | 6 | 6 / 0 / 0 |
| New shape | 6 | 950 to 1052 | 976 | never | 976 | 976 | 976 | 0 / 4 / 2 |
| shape: Threshold count | 3 | 0 to 508 | 256 | never | 256 | 512 | 256 | 1 / 2 / 0 |
| shape: Pair comparisons | 3 | 0 to 680 | 256 | never | 256 | 512 | 256 | 2 / 1 / 0 |
| shape: Modular tests | 5 | 0 to 194 | 1440 | never | 4 | 1440 | 8 | 4 / 1 / 0 |
| shape: Distance and modular test | 3 | 950 to 1028 | 1440 | never | 1440 | 1440 | 1440 | 0 / 3 / 0 |
| shape: Max and offset | 3 | 0 to 788 | 1440 | never | 512 | 1440 | 512 | 2 / 0 / 1 |
| shape: Order statistic | 3 | 1040 to 1052 | 256 | never | 512 | 512 | 512 | 0 / 1 / 2 |

## Mean share of cases right at each budget, passive (%)

| Group | Learner | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 1440 |
|---|---|---|---|---|---|---|---|---|---|---|
| Variant | scratch | 35.3 | 38.6 | 43.3 | 49.2 | 64.2 | 76.8 | 87.5 | 98.4 | 100.0 |
| Variant | bank_row | 36.8 | 41.7 | 48.8 | 60.3 | 67.0 | 71.5 | 74.8 | 76.6 | 76.4 |
| Variant | tables | 46.1 | 47.8 | 48.7 | 56.2 | 66.7 | 79.6 | 87.9 | 98.4 | 100.0 |
| Variant | programs | 35.4 | 37.7 | 41.6 | 51.3 | 63.7 | 77.7 | 86.9 | 98.1 | 100.0 |
| Variant | selector | 46.8 | 48.4 | 54.5 | 62.9 | 73.7 | 84.3 | 93.3 | 98.2 | 100.0 |
| Repeat | scratch | 33.8 | 35.9 | 38.9 | 46.2 | 57.9 | 71.1 | 79.7 | 97.0 | 100.0 |
| Repeat | bank_row | 42.7 | 49.7 | 58.4 | 69.6 | 81.4 | 92.3 | 94.3 | 95.1 | 97.7 |
| Repeat | tables | 88.1 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| Repeat | programs | 34.5 | 34.7 | 40.1 | 45.3 | 57.5 | 71.4 | 80.9 | 96.8 | 100.0 |
| Repeat | selector | 80.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| New shape | scratch | 40.4 | 44.9 | 47.8 | 55.7 | 64.4 | 74.8 | 84.9 | 98.1 | 100.0 |
| New shape | bank_row | 33.0 | 35.5 | 40.5 | 43.7 | 46.7 | 48.2 | 50.1 | 51.1 | 51.2 |
| New shape | tables | 40.4 | 44.5 | 49.3 | 56.8 | 65.1 | 75.2 | 85.3 | 98.2 | 100.0 |
| New shape | programs | 40.4 | 44.3 | 48.3 | 55.3 | 64.7 | 73.4 | 84.9 | 98.2 | 100.0 |
| New shape | selector | 39.0 | 44.5 | 46.3 | 55.2 | 60.7 | 74.4 | 85.2 | 97.7 | 100.0 |

## Cautious mode, mean over budgets below the full table: wrong / abstained (%), passive

| Group | scratch | bank_row | tables | programs | selector |
|---|---|---|---|---|---|
| Variant | 26.06 / 20.6 | 5.59 / 68.3 | 23.22 / 17.9 | 25.17 / 22.2 | 16.89 / 24.7 |
| Repeat | 27.54 / 24.8 | 2.83 / 57.3 | 0.00 / 3.3 | 26.55 / 26.0 | 0.41 / 4.1 |
| New shape | 23.82 / 21.1 | 5.75 / 85.5 | 23.86 / 20.6 | 23.60 / 21.7 | 18.65 / 31.5 |

## Scratch alone, by rule shape (how hard each shape is with no experience)

| Shape | Policies | Scratch audits to 99%, each policy |
|---|---|---|
| Threshold count | 3 | p037 512, p038 256, p049 256 |
| Pair comparisons | 3 | p039 512, p051 256, p056 256 |
| Modular tests | 5 | p040 1440, p045 1440, p046 1440, p047 1440, p052 1440 |
| Distance and modular test | 3 | p041 1440, p043 1440, p055 1440 |
| Max and offset | 3 | p042 512, p053 1440, p054 1440 |
| Order statistic | 3 | p044 256, p048 256, p050 512 |
