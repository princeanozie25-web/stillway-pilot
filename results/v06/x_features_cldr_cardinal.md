# Exploratory: past policies as inputs, cldr_cardinal

Written after the outputs were locked and the breakdown revealed. 18 new policies, 3 seeds, passive audits, budgets [4, 8, 16, 32, 64, 128, 256, 512, 1000]. Inputs: scratch 30, feat 144.

## Audits to 99% of cases right (median of seeds), per policy

| Policy | Group | Shape | Distance to nearest past | scratch | feat | patch | pick |
|---|---|---|---|---|---|---|---|
| am | seen |  | 0 | 4 | 4 | 4 | 4 |
| an | seen |  | 0 | 4 | 4 | 4 | 4 |
| ar | seen |  | 0 | 256 | 256 | 4 | 4 |
| blo | seen |  | 0 | 4 | 4 | 4 | 4 |
| ceb | novel |  | 610 | 128 | 64 | 1000 | 128 |
| ga | novel |  | 7 | 4 | 4 | 4 | 4 |
| gv | novel |  | 160 | 256 | 256 | 1000 | 256 |
| id | seen |  | 0 | 4 | 4 | 4 | 4 |
| is | seen |  | 0 | 128 | 16 | 16 | 16 |
| iu | seen |  | 0 | 4 | 4 | 4 | 4 |
| mo | seen |  | 0 | 128 | 256 | 8 | 8 |
| mt | novel |  | 109 | 512 | 128 | 1000 | 128 |
| ru | seen |  | 0 | 128 | 64 | 4 | 4 |
| sgs | novel |  | 1 | 128 | 32 | 4 | 4 |
| shi | novel |  | 7 | 128 | 128 | 4 | 4 |
| sl | seen |  | 0 | 256 | 64 | 16 | 16 |
| sr | seen |  | 0 | 128 | 16 | 8 | 8 |
| tzm | novel |  | 89 | 128 | 256 | 1000 | 128 |

## By group: median audits to 99%; policies on which the learner needs fewer / same / more audits than scratch

| Group | Policies | scratch | feat | patch | pick | feat vs scratch | pick vs scratch |
|---|---|---|---|---|---|---|---|
| seen | 11 | 128 | 16 | 4 | 4 | 4 / 6 / 1 | 6 / 5 / 0 |
| novel | 7 | 128 | 128 | 1000 | 128 | 3 / 3 / 1 | 3 / 4 / 0 |

## Mean share of cases right at each budget (%)

| Group | Learner | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| seen | scratch | 87.9 | 89.7 | 91.7 | 94.1 | 97.6 | 99.2 | 99.8 | 99.9 | 100.0 |
| seen | feat | 90.4 | 94.2 | 97.1 | 98.0 | 99.4 | 99.7 | 99.8 | 100.0 | 100.0 |
| seen | patch | 93.9 | 96.8 | 99.4 | 99.8 | 99.8 | 99.9 | 99.9 | 100.0 | 100.0 |
| seen | pick | 93.9 | 96.8 | 99.4 | 99.8 | 99.8 | 99.9 | 99.9 | 100.0 | 100.0 |
| novel | scratch | 82.4 | 84.4 | 87.2 | 91.0 | 96.1 | 98.6 | 99.5 | 99.9 | 100.0 |
| novel | feat | 84.9 | 86.9 | 90.7 | 94.6 | 97.4 | 98.8 | 99.6 | 99.9 | 100.0 |
| novel | patch | 82.5 | 83.9 | 84.6 | 85.5 | 86.3 | 87.5 | 89.3 | 92.9 | 100.0 |
| novel | pick | 84.7 | 87.3 | 89.0 | 93.3 | 96.8 | 99.1 | 99.5 | 99.8 | 100.0 |

## Cautious mode, mean over budgets below the full table: wrong / abstained (%)

| Group | scratch | feat | pick |
|---|---|---|---|
| seen | 3.83 / 2.5 | 2.32 / 0.8 | 1.30 / 0.0 |
| novel | 5.56 / 4.5 | 5.14 / 1.6 | 5.96 / 0.7 |

Pick used: patch 83%, feat 14%, scratch 3%.
