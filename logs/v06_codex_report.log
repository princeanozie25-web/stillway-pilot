# v0.6 result tables: codex_hidden

36 past policies (36 distinct rules), 20 distinct new policies, 1440 cases each, 3 seeds. Program family: 416 tables. The shared network reproduces 100.00% of past decisions. New policies inside the program family: 0 of 20.

## novel rule (not among past policies): 14 policies

| Learner | Audits to 99%, passive | chosen | Audits to 100%, passive | chosen | Right at 8 / 16 / 32 audits (passive) | Cautious: wrong / abstained, mean over budgets below the full table | Fell back to scratch |
|---|---|---|---|---|---|---|---|
| scratch | 512 | 848 | 1440 | 1440 | 41.3 / 45.2 / 52.0 | 25.10 / 20.8 | 0% |
| bank_row | never | never | never | never | 39.0 / 45.2 / 53.2 | 5.65 / 75.7 | 0% |
| tables | 512 | 512 | 1440 | 1440 | 46.4 / 49.0 / 56.5 | 23.50 / 19.1 | 94% |
| programs | 976 | 976 | 1440 | 1440 | 40.5 / 44.5 / 53.0 | 24.50 / 22.0 | 99% |
| selector | 512 | 512 | 1440 | 1440 | 46.8 / 51.0 / 59.6 | 17.64 / 27.6 | 74% |
| index | 1440 | 1440 | 1440 | 1440 | 36.3 / 38.2 / 41.8 | 0.00 / 91.1 | 0% |

Selector used: tables 80%, bank_row 19%, programs 1%.

## rule also held by a past policy: 6 policies

| Learner | Audits to 99%, passive | chosen | Audits to 100%, passive | chosen | Right at 8 / 16 / 32 audits (passive) | Cautious: wrong / abstained, mean over budgets below the full table | Fell back to scratch |
|---|---|---|---|---|---|---|---|
| scratch | 1440 | 1440 | 1440 | 1440 | 35.9 / 38.9 / 46.2 | 27.54 / 24.8 | 0% |
| bank_row | 256 | 256 | 976 | 976 | 49.7 / 58.4 / 69.6 | 2.83 / 57.3 | 0% |
| tables | 4 | 4 | 4 | 4 | 100.0 / 100.0 / 100.0 | 0.00 / 3.3 | 0% |
| programs | 1440 | 1440 | 1440 | 1440 | 34.7 / 40.1 / 45.3 | 26.55 / 26.0 | 98% |
| selector | 6 | 4 | 6 | 4 | 100.0 / 100.0 / 100.0 | 0.41 / 4.1 | 1% |
| index | 1440 | 1440 | 1440 | 1440 | 31.9 / 32.6 / 35.9 | 0.00 / 91.1 | 0% |

Selector used: tables 99%, programs 1%, bank_row 1%.

## Pass rules (frozen in `docs/v06_spec.md`)

| Rule | Measured | Result |
|---|---|---|
| L1. Experience helps on novel rules | best of bank_row, programs, selector: 512; scratch: 512 | FAIL |
| L2. Programs need no more audits than bank rows on novel rules | programs 976; bank_row never | PASS |
| L5. Choosing audits helps the selector on novel rules | chosen 512; passive 512 | FAIL |
| L3. A rule seen before is recognised within 16 chosen audits with no cautious error | audits to 100%: 4; cautious wrong 0.000% | PASS |
| L4. The selector is within one budget step of the best single learner in both groups | novel rule: selector 512, best single 512; rule also held by a past policy: selector 6, best single 4 | PASS |
