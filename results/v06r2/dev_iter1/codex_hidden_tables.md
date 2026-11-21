# v0.6 round 2 tables: codex_hidden

20 new policies, 1440 cases, 3 seeds, passive audits, budgets [4, 8, 16, 32, 64, 128, 256, 512, 724, 1024, 1440].

## amended copy: 2 policies (cases differing from the nearest past policy: 8 to 194)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 724 | 1024 | 28.1 / 35.4 / 56.9 / 94.9 | 26.66 / 24.2 | 27.0 |
| recognise | never | never | 95.1 / 99.4 / 99.4 / nan | 3.32 / 0.0 | 93.0 |
| amend | 394 | 1232 | 59.4 / 84.7 / 93.5 / 98.8 | 10.61 / 9.6 | 44.2 |
| parts | 618 | 1440 | 57.5 / 76.2 / 89.6 / 98.9 | 10.26 / 16.0 | 44.1 |
| bank3 | 366 | 1232 | 77.1 / 85.7 / 93.3 / 99.2 | 7.17 / 7.4 | 65.1 |
| index | 1440 | 1440 | 28.0 / 34.5 / 38.9 / 56.7 | 0.00 / 80.8 | 27.9 |

bank3 used: amend 59%, parts 23%, recognise 18%.

## far: new shape: 6 policies (cases differing from the nearest past policy: 950 to 1052)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 618 | 1024 | 43.4 / 55.5 / 75.4 / 98.0 | 19.34 / 16.6 | 39.1 |
| recognise | never | never | nan / nan / nan / nan | 74.31 / 0.0 | 25.7 |
| amend | 618 | 1232 | 41.4 / 54.7 / 73.8 / 96.5 | 20.27 / 17.4 | 37.7 |
| parts | 1232 | 1440 | 39.6 / 51.2 / 66.8 / 90.3 | 21.75 / 19.9 | 37.3 |
| bank3 | 618 | 1024 | 42.3 / 55.3 / 76.7 / 97.9 | 20.29 / 15.7 | 36.6 |
| index | 1440 | 1440 | 41.5 / 48.2 / 53.1 / 67.0 | 0.00 / 80.8 | 40.0 |

bank3 used: amend 53%, scratch 33%, parts 14%, recognise 1%.

## far: variant: 6 policies (cases differing from the nearest past policy: 412 to 788)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 512 | 874 | 40.6 / 57.8 / 84.5 / 99.3 | 17.94 / 15.3 | 36.6 |
| recognise | never | never | 52.8 / nan / nan / nan | 54.55 / 0.0 | 43.1 |
| amend | 512 | 1024 | 46.5 / 63.9 / 88.4 / 98.5 | 16.15 / 13.7 | 39.5 |
| parts | 724 | 1440 | 41.3 / 55.7 / 77.0 / 97.5 | 16.61 / 20.4 | 36.9 |
| bank3 | 512 | 724 | 46.0 / 62.6 / 87.4 / 99.3 | 16.82 / 13.2 | 39.1 |
| index | 1440 | 1440 | 32.5 / 39.8 / 44.3 / 60.7 | 0.00 / 80.8 | 28.9 |

bank3 used: amend 70%, scratch 19%, parts 8%, recognise 3%.

## repeat: 6 policies (cases differing from the nearest past policy: 0 to 0)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 724 | 1024 | 34.4 / 46.8 / 70.7 / 96.3 | 22.24 / 19.9 | 31.9 |
| recognise | 4 | 4 | 100.0 / 100.0 / 100.0 / 100.0 | 0.00 / 1.7 | 91.8 |
| amend | 64 | 128 | 72.6 / 95.2 / 99.9 / 100.0 | 5.53 / 6.7 | 58.5 |
| parts | 512 | 1024 | 52.3 / 70.7 / 89.6 / 99.2 | 10.61 / 18.4 | 46.5 |
| bank3 | 4 | 4 | 100.0 / 100.0 / 100.0 / 100.0 | 0.19 / 1.8 | 89.1 |
| index | 1440 | 1440 | 31.7 / 37.5 / 41.7 / 58.8 | 0.00 / 80.8 | 27.8 |

bank3 used: recognise 99%, amend 1%.

## Pass rules (frozen in `docs/v06r2_spec.md`)

| Rule | Measured | Result |
|---|---|---|
| M1. A repeat is found exactly within 16 audits, with no cautious error | audits to every case right: 4; cautious wrong 0.177% | FAIL |
| M2a. An amended copy never collapses: at every budget at least as right as its original table, less 2 points (on 80% of amended copies) | holds on 0 of 2 | FAIL |
| M2b. An amended copy is learned exactly with fewer audits than from scratch | bank3 1232; scratch 1024 | FAIL |
| M2c. Cautious errors on amended copies stay at or below 1% | 7.17% | FAIL |
| M3. On policies far from every past one the bank does no harm: audits to 99% within one doubling of scratch, and never more than 3 points below scratch at any budget | bank3 512; scratch 512; largest shortfall -0.1 points | PASS |
| M4. On policies far from every past one the bank helps: fewer audits to 99% than scratch | bank3 512; scratch 512 | FAIL |
| M5. The bank's cautious errors are no higher than scratch's on far policies | bank3 18.56%; scratch 18.64% | PASS |

## Per policy: audits to 99% / to every case right (median of seeds)

| Policy | Group | Distance | scratch | amend | parts | bank3 |
|---|---|---|---|---|---|---|
| p037 | far: variant | 412 | 512 / 724 | 512 / 1024 | 512 / 1024 | 512 / 724 |
| p038 | far: variant | 508 | 512 / 512 | 512 / 1024 | 724 / 1440 | 512 / 512 |
| p039 | far: variant | 680 | 256 / 1024 | 256 / 724 | 724 / 1440 | 256 / 724 |
| p040 | repeat | 0 | 724 / 1024 | 64 / 128 | 512 / 1024 | 8 / 8 |
| p041 | far: new shape | 1028 | 724 / 1024 | 1024 / 1440 | 1440 / 1440 | 724 / 1024 |
| p042 | far: variant | 788 | 724 / 724 | 1024 / 1440 | 1024 / 1440 | 724 / 724 |
| p043 | far: new shape | 970 | 724 / 1024 | 1024 / 1024 | 1440 / 1440 | 724 / 1024 |
| p044 | far: new shape | 1048 | 512 / 1024 | 512 / 1440 | 1024 / 1440 | 512 / 1024 |
| p045 | repeat | 0 | 724 / 1024 | 128 / 128 | 512 / 1024 | 4 / 4 |
| p046 | amended copy | 8 | 724 / 1024 | 64 / 1440 | 724 / 1440 | 8 / 1440 |
| p047 | amended copy | 194 | 724 / 1024 | 724 / 1024 | 512 / 1440 | 724 / 1024 |
| p048 | far: new shape | 1052 | 256 / 1024 | 512 / 1024 | 1024 / 1440 | 512 / 1024 |
| p049 | repeat | 0 | 512 / 1024 | 64 / 512 | 512 / 1024 | 4 / 4 |
| p050 | far: new shape | 1040 | 512 / 1440 | 512 / 1440 | 1024 / 1440 | 512 / 1440 |
| p051 | repeat | 0 | 256 / 1024 | 64 / 64 | 512 / 724 | 8 / 8 |
| p052 | repeat | 0 | 724 / 1024 | 64 / 128 | 724 / 1024 | 4 / 4 |
| p053 | repeat | 0 | 724 / 1024 | 64 / 128 | 724 / 1440 | 4 / 4 |
| p054 | far: variant | 672 | 724 / 1024 | 724 / 1024 | 1024 / 1440 | 724 / 1024 |
| p055 | far: new shape | 950 | 724 / 1024 | 724 / 1024 | 1440 / 1440 | 724 / 1024 |
| p056 | far: variant | 576 | 256 / 1440 | 256 / 1440 | 512 / 1024 | 256 / 1440 |
