# v0.6 specification: does experience make a new policy cheaper to learn, on policies I did not write?

Frozen in one commit with `v06/family.py`, `v06/cldr_to_family.py` and `v06/report.py` **before the rule files were downloaded** (only their HTTP headers had been requested, to check they exist). Prince's instructions of 21 November 2026: go with my recommendation; no closeout until the work is done; Codex will author a hidden family.

## Question

v0.4 found that a bank learns a new policy with far fewer audited decisions once it has seen related policies. That was in a world I wrote. v0.5 showed my learner choices do not carry to other people's rules. This test asks the "cheaper with experience" question on a real family of related policies.

## Families

1. **Unicode CLDR plural rules, cardinal** (primary). One policy per locale: integer n → plural category (zero, one, two, few, many, other). Written by the CLDR contributors. Cases: n from 0 to 999, given to learners as three attributes (hundreds, tens and ones digit). File: `cldr-core/supplemental/plurals.json` of `unicode-org/cldr-json`.
2. **CLDR ordinal rules** (second family, same pipeline): `ordinals.json`.
3. **A hidden family authored by Codex** (`docs/v06_codex_family_brief.md`). Run with the same frozen code when it arrives. Not available at the time of this freeze.

Split: a locale is "past" when the first byte of SHA-256 of its code is below 154 (about 60%), otherwise "new". Past policies are known in full. Each distinct new rule is learned from audits. New rules are reported in two groups: **novel** (no past policy has the same rule) and **seen** (some past policy has it).

**What I already know:** the general shape of plural rules for some languages (English, French, Russian, Polish, Arabic and a few others), and that they depend on the last digits of n. The digit attributes reflect that. I have not read the files.

## Learners (fixed; `v06/family.py`)

| Learner | Uses past policies? | What it is |
|---|---|---|
| scratch | no | 5 small networks on the audits alone (the v0.5 default) |
| bank_row | yes, as weights | one network trained on all past policies with a 16-number row per policy; a new policy gets a new row, everything else frozen (the v0.4 consolidation design) |
| tables | yes, as tables | the past rules that are consistent with the audits; falls back to scratch when none is |
| programs | yes, as programs | past rules as decision-list programs (greedy search, rules of at most 2 tests) plus every program within two constant changes of one of them; those consistent with the audits; falls back to scratch when none is |
| selector | yes | holds out a fifth of the audits and uses whichever of the four gets most right |
| index | no | audited cases only |

Best guess: majority. Cautious: answer only when every candidate or committee member agrees. Audits: passive (random n) and chosen (the cases the learner's own candidates disagree on most). Budgets 4, 8, 16, ..., 512, 1000. Three seeds per new rule.

## Pass rules, fixed now

"Audits to 99%": per new rule, the median over seeds of the first budget with 99% of all 1,000 cases right; then the median over the rules of a group.

| Rule | Passes if |
|---|---|
| L1. Experience helps on novel rules | the best of bank_row, programs and selector needs fewer audits to 99% than scratch (passive) |
| L2. Programs against weights as the store of experience | programs needs no more audits to 99% than bank_row on novel rules (passive) |
| L3. A rule seen before is recognised | on seen rules, tables reaches 100% within 16 chosen audits (median) with no cautious error |
| L4. The selector is safe | in both groups its audits to 99% are within one budget step of the best single learner |
| L5. Choosing audits helps | on novel rules the selector needs fewer chosen audits than passive ones |

Reading: if L1 fails, "cheaper with experience" is not supported on this family, whatever my own domain showed. If L2 fails, the v0.4 design (weights) is the better store of experience here and the program library is not.

## Limits stated in advance

- One real family (two with ordinals), small tables, no noise. Many locales share rules, which favours any learner with a memory of past rules.
- The attributes (decimal digits) are my choice and are informed by general knowledge of plural rules.
- Internal: I chose the family. Codex's hidden family is the independent check.
