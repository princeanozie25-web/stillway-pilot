# v0.6 round 2 tables: cldr_cardinal

18 new policies, 1000 cases, 3 seeds, passive audits, budgets [4, 8, 16, 32, 64, 128, 256, 512, 724, 1000].

## amended copy: 5 policies (cases differing from the nearest past policy: 1 to 109)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 128 | 1000 | 87.0 / 93.3 / 98.6 / 99.7 | 3.87 / 3.5 | 85.6 |
| recognise | 4 | never | 97.7 / 99.3 / 99.4 / 99.9 | 0.27 / 10.3 | 94.3 |
| amend | 4 | 1000 | 95.2 / 96.2 / 98.0 / 99.5 | 0.07 / 53.9 | 94.9 |
| parts | 64 | 1000 | 89.0 / 96.6 / 99.3 / 99.8 | 3.25 / 1.1 | 88.1 |
| bank3 | 4 | 1000 | 95.2 / 96.2 / 98.0 / 99.6 | 0.07 / 54.1 | 94.9 |
| bank3a | 4 | 512 | 93.8 / 95.5 / 89.8 / 99.6 | 0.01 / 66.6 | 86.6 |
| index | 1000 | 1000 | 88.8 / 89.0 / 90.1 / 94.2 | 0.00 / 80.6 | 88.7 |

bank3a used: amend 72%, recognise 27%, scratch 1%.

## far: 2 policies (cases differing from the nearest past policy: 160 to 610)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 128 | 192 | 76.0 / 90.0 / 99.5 / 100.0 | 6.04 / 8.0 | 62.1 |
| recognise | never | never | 75.1 / nan / nan / nan | 14.23 / 26.9 | 71.5 |
| amend | 618 | 756 | 57.0 / 75.8 / 92.4 / 99.2 | 0.00 / 78.1 | 53.8 |
| parts | 192 | 192 | 72.5 / 91.2 / 99.1 / 100.0 | 8.69 / 3.2 | 66.1 |
| bank3 | 320 | 320 | 62.0 / 88.3 / 97.0 / 100.0 | 0.00 / 71.8 | 61.3 |
| bank3a | 192 | 192 | 76.3 / 89.0 / 90.6 / 99.7 | 0.00 / 76.4 | 64.0 |
| index | 1000 | 1000 | 72.7 / 73.5 / 76.2 / 86.7 | 0.00 / 80.6 | 61.8 |

bank3a used: scratch 52%, amend 43%, recognise 3%, parts 2%.

## repeat: 11 policies (cases differing from the nearest past policy: 0 to 0)

| Learner | Audits to 99% | Audits to every case right | Right at 8 / 32 / 128 / 512 audits | Cautious: wrong / abstained (mean, budgets below the full table) | Lowest share right at any budget (mean over policies of the per-policy minimum) |
|---|---|---|---|---|---|
| scratch | 128 | 512 | 89.7 / 95.2 / 99.1 / 99.9 | 3.35 / 2.3 | 86.4 |
| recognise | 4 | 16 | 96.6 / 99.7 / 100.0 / 100.0 | 0.00 / 5.2 | 95.7 |
| amend | 4 | 16 | 96.6 / 99.7 / 100.0 / 100.0 | 0.00 / 43.9 | 95.7 |
| parts | 8 | 512 | 95.6 / 99.0 / 99.6 / 99.9 | 1.61 / 0.6 | 92.5 |
| bank3 | 4 | 16 | 96.6 / 99.7 / 100.0 / 100.0 | 0.00 / 43.9 | 95.7 |
| bank3a | 4 | 8 | 99.5 / 100.0 / 100.0 / 100.0 | 0.00 / 49.1 | 95.7 |
| index | 1000 | 1000 | 87.3 / 89.8 / 90.8 / 95.0 | 0.00 / 80.6 | 86.1 |

bank3a used: recognise 100%.

## Pass rules (frozen in `docs/v06r2_spec.md`)

| Rule | Measured | Result |
|---|---|---|
| M1. A repeat is found exactly within 16 audits, with no cautious error | audits to every case right: 8; cautious wrong 0.000% | PASS |
| M2a. An amended copy never collapses: from 16 audits on, at least as right as its original table, less 2 points (on 80% of amended copies) | holds on 2 of 5 | FAIL |
| M2b. An amended copy is learned exactly with fewer audits than from scratch | bank3a 512; scratch 1000 | PASS |
| M2c. Cautious errors on amended copies stay at or below 1% | 0.01% | PASS |
| M3. On policies far from every past one the bank does no harm: audits to 99% within one doubling of scratch, and from 16 audits on never more than 3 points below scratch | bank3a 192; scratch 128; largest shortfall -8.8 points | FAIL |
| M4. On policies far from every past one the bank helps: fewer audits to 99% than scratch | bank3a 192; scratch 128 | FAIL |
| M5. The bank's cautious errors are no higher than scratch's on far policies | bank3a 0.00%; scratch 6.04% | PASS |

## Per policy: audits to 99% / to every case right (median of seeds)

| Policy | Group | Distance | scratch | amend | parts | bank3 | bank3a |
|---|---|---|---|---|---|---|---|
| am/as/bn/csw/doi/kab/kok/ln/mg/pt/tg/ti/vi | repeat | 0 | 4 / 1000 | 4 / 1000 | 4 / 1000 | 4 / 8 |
| an/asa/ast/az/ce/cgg/ckb/da/el/en/es/et/fi/fo/fur/hu/jgo/kk/kl/ksb/lb/lij/mn/ne/nn/pt-PT/rof/rwk/sc/scn/sdh/seh/so/ss/sv/ug/uz/vun/xh/xog/yi | repeat | 0 | 4 / 512 | 4 / 4 | 4 / 512 | 4 / 4 |
| ar | repeat | 0 | 256 / never | 4 / 4 | 256 / 1000 | 4 / 4 |
| blo | repeat | 0 | 4 / never | 4 / 1000 | 4 / 1000 | 4 / 8 |
| ceb/fil/tl | far | 610 | 128 / 128 | 512 / 512 | 128 / 128 | 128 / 128 |
| ga | amended copy | 7 | 4 / never | 4 / 1000 | 4 / 1000 | 4 / 1000 |
| gv | far | 160 | 128 / 256 | 724 / 1000 | 256 / 256 | 256 / 256 |
| id/jw/kea/ms/nqo/osa/tpi/wo/yo/yue | repeat | 0 | 4 / 4 | 4 / 724 | 4 / 4 | 4 / 16 |
| is | repeat | 0 | 128 / 256 | 16 / 16 | 8 / 8 | 8 / 8 |
| iu/naq/se/sma/smn | repeat | 0 | 4 / 512 | 4 / 512 | 4 / 512 | 4 / 8 |
| mo | repeat | 0 | 256 / 1000 | 16 / 16 | 128 / 1000 | 8 / 8 |
| mt | amended copy | 109 | 256 / 1000 | 512 / 1000 | 64 / 1000 | 512 / 512 |
| ru | repeat | 0 | 128 / 256 | 4 / 4 | 16 / 16 | 4 / 4 |
| sgs | amended copy | 1 | 128 / 1000 | 4 / 1000 | 32 / 1000 | 4 / 512 |
| shi | amended copy | 7 | 128 / 1000 | 4 / 1000 | 128 / 1000 | 4 / 256 |
| sl | repeat | 0 | 256 / 512 | 64 / 64 | 64 / 256 | 8 / 8 |
| sr | repeat | 0 | 128 / 256 | 8 / 8 | 32 / 32 | 8 / 8 |
| tzm | amended copy | 89 | 256 / 724 | 512 / 1000 | 256 / 512 | 256 / 512 |
