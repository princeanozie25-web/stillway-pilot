# Exploratory: past policies as inputs, cldr_ordinal

Written after the outputs were locked and the breakdown revealed. 14 new policies, 3 seeds, passive audits, budgets [4, 8, 16, 32, 64, 128, 256, 512, 1000]. Inputs: scratch 30, feat 138.

## Audits to 99% of cases right (median of seeds), per policy

| Policy | Group | Shape | Distance to nearest past | scratch | feat | patch | pick |
|---|---|---|---|---|---|---|---|
| am | seen |  | 0 | 4 | 4 | 4 | 4 |
| as | novel |  | 1 | 4 | 4 | 4 | 4 |
| az | novel |  | 610 | 256 | 512 | 1000 | 512 |
| blo | novel |  | 5 | 4 | 4 | 4 | 4 |
| en | novel |  | 90 | 256 | 16 | 1000 | 32 |
| es | novel |  | 189 | 256 | 32 | 1000 | 64 |
| fil | seen |  | 0 | 4 | 4 | 4 | 4 |
| hu | novel |  | 1 | 4 | 4 | 4 | 4 |
| kk | novel |  | 299 | 64 | 64 | 1000 | 64 |
| kok | seen |  | 0 | 4 | 4 | 4 | 4 |
| lij | novel |  | 108 | 256 | 256 | 1000 | 256 |
| ne | novel |  | 2 | 4 | 4 | 4 | 4 |
| sc | seen |  | 0 | 4 | 4 | 128 | 128 |
| sv | novel |  | 179 | 128 | 16 | 1000 | 32 |

## By group: median audits to 99%; policies on which the learner needs fewer / same / more audits than scratch

| Group | Policies | scratch | feat | patch | pick | feat vs scratch | pick vs scratch |
|---|---|---|---|---|---|---|---|
| seen | 4 | 4 | 4 | 4 | 4 | 0 / 4 / 0 | 0 / 3 / 1 |
| novel | 10 | 96 | 16 | 1000 | 32 | 3 / 6 / 1 | 3 / 6 / 1 |

## Mean share of cases right at each budget (%)

| Group | Learner | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| seen | scratch | 99.8 | 99.8 | 99.8 | 99.8 | 99.7 | 99.7 | 99.8 | 99.9 | 99.9 |
| seen | feat | 99.8 | 99.8 | 99.8 | 99.8 | 99.8 | 99.8 | 99.9 | 99.9 | 100.0 |
| seen | patch | 99.1 | 99.1 | 99.1 | 99.1 | 99.2 | 99.5 | 99.7 | 99.9 | 100.0 |
| seen | pick | 99.1 | 99.1 | 99.1 | 99.2 | 99.2 | 99.5 | 99.7 | 99.9 | 100.0 |
| novel | scratch | 79.9 | 83.8 | 89.5 | 94.7 | 97.7 | 99.1 | 99.7 | 99.9 | 100.0 |
| novel | feat | 82.9 | 89.3 | 94.1 | 96.6 | 98.0 | 99.1 | 99.6 | 99.9 | 100.0 |
| novel | patch | 81.7 | 83.4 | 83.8 | 84.9 | 85.4 | 86.5 | 88.6 | 92.5 | 100.0 |
| novel | pick | 81.9 | 86.2 | 89.2 | 95.6 | 98.1 | 99.0 | 99.7 | 99.9 | 100.0 |

## Cautious mode, mean over budgets below the full table: wrong / abstained (%)

| Group | scratch | feat | pick |
|---|---|---|---|
| seen | 0.19 / 0.1 | 0.19 / 0.0 | 0.66 / 0.0 |
| novel | 4.78 / 4.3 | 3.83 / 2.2 | 5.72 / 1.1 |

Pick used: patch 68%, feat 28%, scratch 4%.
