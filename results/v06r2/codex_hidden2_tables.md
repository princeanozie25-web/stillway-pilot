# v0.6 round 2 tables: codex_hidden2

30 new policies, 1600 cases, 3 seeds, passive audits, budgets [4, 8, 16, 32, 64, 128, 256, 512, 724, 1024, 1600].

## amended copy: 12 policies (cases differing from the nearest past policy: 1 to 200)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 1600 | 1600 | 34.0 / 41.9 / 59.2 / 85.5 | 24.10 / 26.9 | 30.4 |
| recognise | never | never | 98.0 / 99.1 / 99.8 / 99.9 | 1.87 / 3.3 | 83.0 |
| amend | 364 | 1600 | 94.5 / 95.8 / 96.1 / 97.9 | 0.17 / 52.9 | 83.0 |
| parts | 1024 | 1600 | 43.8 / 57.7 / 76.9 / 95.0 | 15.66 / 22.5 | 37.2 |
| bank3 | 364 | 1600 | 94.4 / 95.8 / 96.1 / 97.9 | 0.17 / 52.9 | 83.0 |
| bank3a | 130 | 724 | 91.8 / 95.9 / 94.5 / 98.8 | 0.13 / 56.6 | 81.1 |
| index | 1600 | 1600 | 25.2 / 26.5 / 31.0 / 49.0 | 0.00 / 82.7 | 25.0 |

bank3a used: amend 62%, recognise 38%, parts 0%.

## far: 12 policies (cases differing from the nearest past policy: 672 to 1136)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 1600 | 1600 | 29.6 / 36.7 / 51.5 / 80.3 | 26.91 / 29.1 | 27.4 |
| recognise | never | never | nan / nan / nan / nan | 60.77 / 18.1 | 25.7 |
| amend | 1600 | 1600 | 29.6 / 35.3 / 47.2 / 70.5 | 0.00 / 82.6 | 26.8 |
| parts | 1600 | 1600 | 31.8 / 39.7 / 51.5 / 75.0 | 26.28 / 29.5 | 28.9 |
| bank3 | 1600 | 1600 | 30.2 / 38.0 / 52.9 / 81.4 | 0.03 / 80.1 | 27.4 |
| bank3a | 1600 | 1600 | 30.4 / 39.2 / 52.7 / 80.7 | 0.03 / 80.1 | 27.2 |
| index | 1600 | 1600 | 25.2 / 26.3 / 30.6 / 48.5 | 0.00 / 82.7 | 25.1 |

bank3a used: scratch 60%, parts 23%, amend 16%, recognise 1%.

## repeat: 6 policies (cases differing from the nearest past policy: 0 to 0)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 1024 | 1600 | 34.6 / 42.9 / 63.6 / 91.2 | 22.57 / 24.7 | 31.7 |
| recognise | 4 | 4 | 100.0 / 100.0 / 100.0 / 100.0 | 0.00 / 0.8 | 95.7 |
| amend | 4 | 4 | 100.0 / 100.0 / 100.0 / 100.0 | 0.00 / 39.6 | 95.7 |
| parts | 724 | 1024 | 43.0 / 59.4 / 79.6 / 98.8 | 14.08 / 21.9 | 38.3 |
| bank3 | 4 | 4 | 100.0 / 100.0 / 100.0 / 100.0 | 0.00 / 39.6 | 95.7 |
| bank3a | 4 | 4 | 100.0 / 100.0 / 100.0 / 100.0 | 0.00 / 39.6 | 95.7 |
| index | 1600 | 1600 | 25.3 / 26.5 / 30.8 / 48.6 | 0.00 / 82.7 | 24.9 |

bank3a used: recognise 100%.

## Pass rules (frozen in `docs/v06r2_spec.md`)

| Rule | Measured | Result |
|---|---|---|
| M1. A repeat is found exactly within 16 audits, with no cautious error | audits to every case right: 4; cautious wrong 0.000% | PASS |
| M2a. An amended copy never collapses: from 16 audits on, at least as right as its original table, less 2 points (on 80% of amended copies) | holds on 10 of 12 | PASS |
| M2b. An amended copy is learned exactly with fewer audits than from scratch | bank3a 724; scratch 1600 | PASS |
| M2c. Cautious errors on amended copies stay at or below 1% | 0.13% | PASS |
| M3. On policies far from every past one the bank does no harm: audits to 99% within one doubling of scratch, and from 16 audits on never more than 3 points below scratch | bank3a 1600; scratch 1600; largest shortfall -0.8 points | PASS |
| M4. On policies far from every past one the bank helps: fewer audits to 99% than scratch | bank3a 1600; scratch 1600 | FAIL |
| M5. The bank's cautious errors are no higher than scratch's on far policies | bank3a 0.03%; scratch 26.91% | PASS |

## Per policy: audits to 99% / to every case right (median of seeds)

| Policy | Group | Distance | scratch | amend | parts | bank3 | bank3a |
|---|---|---|---|---|---|---|---|
| p037 | amended copy | 50 | 1600 / 1600 | 724 / 1600 | 1024 / 1600 | 256 / 256 |
| p038 | repeat | 0 | 1024 / 1600 | 4 / 4 | 512 / 1024 | 4 / 4 |
| p039 | far | 1136 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p040 | amended copy | 8 | 1600 / 1600 | 4 / 1600 | 512 / 1600 | 4 / 256 |
| p041 | amended copy | 200 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 512 / 724 |
| p042 | far | 1032 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p043 | amended copy | 200 | 1024 / 1600 | 1600 / 1600 | 1600 / 1600 | 724 / 724 |
| p044 | far | 672 | 1024 / 1600 | 1600 / 1600 | 1600 / 1600 | 1024 / 1600 |
| p045 | far | 1020 | 1024 / 1600 | 1600 / 1600 | 1600 / 1600 | 1024 / 1600 |
| p046 | repeat | 0 | 1024 / 1600 | 4 / 4 | 724 / 1600 | 4 / 4 |
| p047 | amended copy | 1 | 1024 / 1600 | 4 / 512 | 1024 / 1600 | 4 / 1024 |
| p048 | repeat | 0 | 1024 / 1600 | 4 / 4 | 512 / 512 | 4 / 4 |
| p049 | amended copy | 8 | 1024 / 1600 | 4 / 1600 | 724 / 1600 | 4 / 1600 |
| p050 | far | 1104 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p051 | repeat | 0 | 1024 / 1024 | 4 / 4 | 724 / 1024 | 4 / 4 |
| p052 | amended copy | 50 | 1600 / 1600 | 1024 / 1600 | 1024 / 1600 | 256 / 512 |
| p053 | far | 1000 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p054 | far | 1130 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p055 | amended copy | 8 | 1600 / 1600 | 4 / 1600 | 724 / 1600 | 4 / 512 |
| p056 | far | 1056 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p057 | amended copy | 50 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p058 | amended copy | 200 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p059 | amended copy | 1 | 1024 / 1600 | 4 / 1024 | 512 / 1024 | 4 / 1600 |
| p060 | far | 1085 | 1024 / 1600 | 1600 / 1600 | 1600 / 1600 | 1024 / 1600 |
| p061 | amended copy | 1 | 1024 / 1600 | 4 / 1024 | 724 / 1600 | 4 / 724 |
| p062 | repeat | 0 | 1024 / 1600 | 4 / 4 | 724 / 1024 | 4 / 4 |
| p063 | far | 1048 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p064 | far | 1096 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 | 1600 / 1600 |
| p065 | repeat | 0 | 1024 / 1600 | 4 / 4 | 724 / 1024 | 4 / 4 |
| p066 | far | 800 | 1024 / 1600 | 1600 / 1600 | 724 / 1600 | 1024 / 1600 |
