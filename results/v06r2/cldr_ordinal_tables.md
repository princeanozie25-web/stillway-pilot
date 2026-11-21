# v0.6 round 2 tables: cldr_ordinal

14 new policies, 1000 cases, 3 seeds, passive audits, budgets [4, 8, 16, 32, 64, 128, 256, 512, 724, 1000].

## amended copy: 6 policies (cases differing from the nearest past policy: 1 to 108)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 4 | 1000 | 92.6 / 95.9 / 99.1 / 99.8 | 2.19 / 2.6 | 90.8 |
| recognise | 4 | never | 97.7 / 99.6 / 99.7 / 99.9 | 0.88 / 10.1 | 95.1 |
| amend | 4 | 1000 | 95.5 / 96.9 / 98.2 / 99.6 | 0.09 / 51.9 | 93.9 |
| parts | 4 | 1000 | 95.2 / 97.7 / 99.0 / 99.9 | 1.70 / 0.6 | 94.7 |
| bank3 | 4 | 1000 | 95.5 / 96.9 / 98.2 / 99.6 | 0.09 / 51.9 | 93.9 |
| bank3a | 4 | 384 | 95.8 / 96.9 / 95.8 / 100.0 | 0.01 / 64.8 | 91.7 |
| index | 4 | 1000 | 89.8 / 93.4 / 94.0 / 96.7 | 0.00 / 80.6 | 89.8 |

bank3a used: amend 66%, recognise 33%, parts 1%, scratch 1%.

## far: 4 policies (cases differing from the nearest past policy: 179 to 610)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 128 | 384 | 72.7 / 89.9 / 98.9 / 100.0 | 6.87 / 6.8 | 70.5 |
| recognise | never | never | 82.0 / nan / nan / nan | 9.84 / 22.9 | 75.4 |
| amend | 512 | 862 | 69.5 / 76.3 / 89.2 / 99.5 | 0.01 / 77.6 | 66.0 |
| parts | 96 | 320 | 80.2 / 94.6 / 98.6 / 100.0 | 4.85 / 4.2 | 77.5 |
| bank3 | 128 | 384 | 71.3 / 85.6 / 97.8 / 99.8 | 0.00 / 74.9 | 68.8 |
| bank3a | 384 | 724 | 71.5 / 84.1 / 88.1 / 99.0 | 0.01 / 77.0 | 67.3 |
| index | 1000 | 1000 | 68.7 / 72.8 / 75.6 / 86.1 | 0.00 / 80.6 | 63.2 |

bank3a used: amend 56%, scratch 32%, recognise 8%, parts 4%.

## repeat: 4 policies (cases differing from the nearest past policy: 0 to 0)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 4 | 1000 | 99.8 / 99.8 / 99.7 / 99.8 | 0.19 / 0.1 | 99.7 |
| recognise | 4 | 512 | 99.7 / 99.7 / 99.7 / 99.9 | 0.00 / 8.3 | 99.6 |
| amend | 4 | 512 | 99.7 / 99.7 / 99.7 / 99.9 | 0.00 / 44.1 | 99.6 |
| parts | 4 | 1000 | 99.8 / 99.8 / 99.8 / 99.9 | 0.18 / 0.0 | 99.8 |
| bank3 | 4 | 512 | 99.7 / 99.7 / 99.7 / 99.9 | 0.00 / 44.1 | 99.6 |
| bank3a | 4 | 12 | 99.9 / 100.0 / 100.0 / 100.0 | 0.00 / 54.2 | 99.6 |
| index | 4 | 1000 | 99.8 / 99.8 / 99.8 / 99.9 | 0.00 / 80.6 | 99.8 |

bank3a used: recognise 100%.

## Pass rules (frozen in `docs/v06r2_spec.md`)

| Rule | Measured | Result |
|---|---|---|
| M1. A repeat is found exactly within 16 audits, with no cautious error | audits to every case right: 12; cautious wrong 0.000% | PASS |
| M2a. An amended copy never collapses: from 16 audits on, at least as right as its original table, less 2 points (on 80% of amended copies) | holds on 3 of 6 | FAIL |
| M2b. An amended copy is learned exactly with fewer audits than from scratch | bank3a 384; scratch 1000 | PASS |
| M2c. Cautious errors on amended copies stay at or below 1% | 0.01% | PASS |
| M3. On policies far from every past one the bank does no harm: audits to 99% within one doubling of scratch, and from 16 audits on never more than 3 points below scratch | bank3a 384; scratch 128; largest shortfall -10.8 points | FAIL |
| M4. On policies far from every past one the bank helps: fewer audits to 99% than scratch | bank3a 384; scratch 128 | FAIL |
| M5. The bank's cautious errors are no higher than scratch's on far policies | bank3a 0.01%; scratch 6.87% | PASS |

## Per policy: audits to 99% / to every case right (median of seeds)

| Policy | Group | Distance | scratch | amend | parts | bank3 | bank3a |
|---|---|---|---|---|---|---|---|
| am/an/ar/ast/ce/da/el/et/fi/id/is/mn/pt/ru/sl/sr/tg/tpi/uz/yue | repeat | 0 | 4 / 4 | 4 / 1000 | 4 / 4 | 4 / 8 |
| as/bn | amended copy | 1 | 4 / never | 4 / 724 | 4 / 1000 | 4 / 256 |
| az | far | 610 | 256 / 724 | 512 / 1000 | 256 / 724 | 256 / 724 |
| blo | amended copy | 5 | 4 / never | 4 / 1000 | 4 / 1000 | 4 / 64 |
| en | amended copy | 90 | 128 / 256 | 512 / 1000 | 32 / 32 | 256 / 512 |
| es | far | 189 | 128 / 256 | 512 / 724 | 64 / 128 | 512 / 512 |
| fil/ga/mo/ms/tl/vi | repeat | 0 | 4 / 1000 | 4 / 512 | 4 / 1000 | 4 / 8 |
| hu | amended copy | 1 | 4 / 1000 | 4 / 1000 | 4 / 1000 | 4 / 724 |
| kk | far | 299 | 64 / 512 | 512 / 724 | 128 / 512 | 128 / 724 |
| kok | repeat | 0 | 4 / never | 4 / 8 | 4 / 1000 | 4 / 16 |
| lij/scn | amended copy | 108 | 256 / 1000 | 512 / 1000 | 512 / 512 | 512 / 512 |
| ne | amended copy | 2 | 4 / 1000 | 4 / 724 | 4 / 1000 | 4 / 32 |
| sc | repeat | 0 | 4 / 1000 | 4 / 512 | 4 / 1000 | 4 / 16 |
| sv | far | 179 | 128 / 128 | 512 / 1000 | 16 / 16 | 512 / 724 |
