# v0.6 result tables: cldr_ordinal

69 past policies (18 distinct rules), 14 distinct new policies, 1000 cases each, 3 seeds. Program family: 9229 tables. The shared network reproduces 100.00% of past decisions. New policies inside the program family: 5 of 14.

## novel rule (not among past policies): 10 policies

| Learner | Audits to 99%, passive | chosen | Audits to 100%, passive | chosen | Right at 8 / 16 / 32 audits (passive) | Cautious: wrong / abstained, mean over budgets below the full table | Fell back to scratch |
|---|---|---|---|---|---|---|---|
| scratch | 96 | 64 | 1000 | 756 | 85.2 / 88.2 / 92.5 | 4.94 / 4.5 | 0% |
| bank_row | 16 | 32 | never | never | 86.0 / 87.2 / 88.9 | 8.10 / 7.1 | 0% |
| tables | 96 | 64 | 1000 | 384 | 86.1 / 89.4 / 93.6 | 3.81 / 8.9 | 65% |
| programs | 48 | 64 | 1000 | 756 | 87.3 / 92.0 / 94.9 | 2.40 / 32.8 | 47% |
| selector | 48 | 64 | 756 | 384 | 85.5 / 89.9 / 94.4 | 3.44 / 9.7 | 56% |
| index | 1000 | 1000 | 1000 | 1000 | 83.4 / 83.6 / 85.1 | 0.00 / 87.2 | 0% |

Selector used: tables 90%, bank_row 6%, programs 3%, scratch 0%.

## rule also held by a past policy: 4 policies

| Learner | Audits to 99%, passive | chosen | Audits to 100%, passive | chosen | Right at 8 / 16 / 32 audits (passive) | Cautious: wrong / abstained, mean over budgets below the full table | Fell back to scratch |
|---|---|---|---|---|---|---|---|
| scratch | 4 | 4 | 1000 | 628 | 99.8 / 99.6 / 99.7 | 0.22 / 0.2 | 0% |
| bank_row | 4 | 4 | 756 | 272 | 99.7 / 99.7 / 99.5 | 0.12 / 1.8 | 0% |
| tables | 4 | 4 | 256 | 12 | 99.6 / 99.7 / 99.6 | 0.00 / 9.3 | 0% |
| programs | 4 | 4 | 1000 | 12 | 99.8 / 99.8 / 99.8 | 0.00 / 66.8 | 0% |
| selector | 4 | 4 | 384 | 16 | 99.7 / 99.7 / 99.7 | 0.00 / 10.1 | 0% |
| index | 4 | 4 | 628 | 1000 | 99.8 / 99.8 / 99.8 | 0.00 / 87.2 | 0% |

Selector used: tables 98%, programs 2%.

## Pass rules (frozen in `docs/v06_spec.md`)

| Rule | Measured | Result |
|---|---|---|
| L1. Experience helps on novel rules | best of bank_row, programs, selector: 16; scratch: 96 | PASS |
| L2. Programs need no more audits than bank rows on novel rules | programs 48; bank_row 16 | FAIL |
| L5. Choosing audits helps the selector on novel rules | chosen 64; passive 48 | FAIL |
| L3. A rule seen before is recognised within 16 chosen audits with no cautious error | audits to 100%: 12; cautious wrong 0.000% | PASS |
| L4. The selector is within one budget step of the best single learner in both groups | novel rule: selector 48, best single 16; rule also held by a past policy: selector 4, best single 4 | FAIL |
