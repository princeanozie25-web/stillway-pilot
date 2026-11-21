# v0.6 result tables: cldr_cardinal

140 past policies (19 distinct rules), 18 distinct new policies, 1000 cases each, 3 seeds. Program family: 10151 tables. The shared network reproduces 100.00% of past decisions. New policies inside the program family: 11 of 18.

## novel rule (not among past policies): 7 policies

| Learner | Audits to 99%, passive | chosen | Audits to 100%, passive | chosen | Right at 8 / 16 / 32 audits (passive) | Cautious: wrong / abstained, mean over budgets below the full table | Fell back to scratch |
|---|---|---|---|---|---|---|---|
| scratch | 128 | 128 | 1000 | 1000 | 82.4 / 88.5 / 93.2 | 5.32 / 5.0 | 0% |
| bank_row | never | never | never | never | 85.2 / 89.1 / 90.8 | 5.90 / 9.3 | 0% |
| tables | 64 | 64 | 1000 | 256 | 88.2 / 91.4 / 94.8 | 3.42 / 5.6 | 71% |
| programs | 64 | 64 | 1000 | 256 | 87.8 / 89.6 / 94.5 | 2.29 / 29.0 | 56% |
| selector | 64 | 64 | 1000 | 512 | 88.9 / 90.3 / 95.0 | 3.20 / 6.3 | 61% |
| index | 1000 | 1000 | 1000 | 1000 | 84.2 / 84.3 / 84.6 | 0.00 / 87.2 | 0% |

Selector used: tables 94%, bank_row 5%, programs 1%.

## rule also held by a past policy: 11 policies

| Learner | Audits to 99%, passive | chosen | Audits to 100%, passive | chosen | Right at 8 / 16 / 32 audits (passive) | Cautious: wrong / abstained, mean over budgets below the full table | Fell back to scratch |
|---|---|---|---|---|---|---|---|
| scratch | 128 | 64 | 512 | 512 | 89.8 / 92.5 / 95.3 | 3.46 / 2.9 | 0% |
| bank_row | 8 | 8 | 256 | 16 | 96.9 / 97.7 / 99.2 | 0.82 / 2.8 | 0% |
| tables | 4 | 4 | 32 | 8 | 97.1 / 99.4 / 99.8 | 0.00 / 5.7 | 0% |
| programs | 4 | 8 | 256 | 32 | 94.0 / 97.6 / 99.0 | 0.00 / 44.0 | 0% |
| selector | 4 | 4 | 16 | 8 | 98.3 / 99.2 / 100.0 | 0.00 / 5.4 | 0% |
| index | 1000 | 1000 | 1000 | 1000 | 88.4 / 89.6 / 89.8 | 0.00 / 87.2 | 0% |

Selector used: tables 99%, bank_row 1%, programs 0%.

## Pass rules (frozen in `docs/v06_spec.md`)

| Rule | Measured | Result |
|---|---|---|
| L1. Experience helps on novel rules | best of bank_row, programs, selector: 64; scratch: 128 | PASS |
| L2. Programs need no more audits than bank rows on novel rules | programs 64; bank_row never | PASS |
| L5. Choosing audits helps the selector on novel rules | chosen 64; passive 64 | FAIL |
| L3. A rule seen before is recognised within 16 chosen audits with no cautious error | audits to 100%: 8; cautious wrong 0.000% | PASS |
| L4. The selector is within one budget step of the best single learner in both groups | novel rule: selector 64, best single 64; rule also held by a past policy: selector 4, best single 4 | PASS |
