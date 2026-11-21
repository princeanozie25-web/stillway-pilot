# v0.5 specification: the program-search bank on rule sets I did not write

Frozen in one git commit with `v05/blind.py` **before any dataset was downloaded**; the commit history shows the order. Prince's instruction of 21 November 2026: go with the recommendation of `results/v04/BEYOND_THE_BRIEF.md`.

## Why

Every result so far is in a world I wrote. v0.4's addendum found that searching for programs and checking them against the logs beat gradient learning there. The languages were also mine. This test asks whether that holds on decision rules written by other people.

## What is tested, and what is not

Tested: the bank's learner. Given audited decisions of an unknown rule, find a program, answer every case, say where it is unsure, choose the next audit.

Not tested: registers, procedures, sessions, the versioned bank, the rule library across related policies. These datasets are single rules over different attributes; no family of related policies is available. That gap stays open.

## Datasets

Eight public tables from the UCI repository. Chosen now, by one rule: classic rule-generated or fully enumerated categorical tables that I can name from memory. Each is used as an auditor: a learner asks for the decision of a case.

| Name | File | Cases |
|---|---|---|
| car | `car.data` | 1,728 (complete grid) |
| nursery | `nursery.data` | 12,960 (complete grid) |
| balance | `balance-scale.data` | 625 (complete grid) |
| monks1, monks2, monks3 | `monks-1.test`, `monks-2.test`, `monks-3.test` | 432 each (complete grid) |
| lenses | `lenses.data` | 24 (complete grid) |
| tictactoe | `tic-tac-toe.data` | 958 (all legal end boards) |

**What I already know about them** (from the literature, not from looking now): MONK-1 is roughly "attribute 1 equals attribute 2, or attribute 5 is 1"; MONK-2 is "exactly two attributes take their first value"; MONK-3 is a two-clause rule; balance compares two products; car and nursery come from hierarchical decision models; tic-tac-toe is "x has three in a row". I did not shape the language to them: it is the v0.4 language with the domain-specific tests removed. I expect it to do badly on balance (arithmetic), MONK-2 (counting) and tic-tac-toe with two tests per rule (a win needs three).

## The language and the search (fixed)

- A test is `attribute = value` or `attribute != value`. No ordering of values is used.
- A rule is a conjunction of at most 2 tests with a decision. A program is a decision list of rules and a default.
- Search: greedy. The rule that covers most audited cases with no exception goes first. A program must reproduce every audited case; if the language cannot, it is flagged.
- A committee of 7 programs (random tie-breaks, scoring on random 70% subsamples). Best guess: majority. Cautious: answer only when unanimous.
- Chosen audits: the unaudited cases the committee disagrees on most.
- Secondary setting, labelled as such: 3 tests per rule, on the datasets with at most 2,000 cases.

## Comparators (same audits, same one-hot inputs)

| Learner | What it is |
|---|---|
| net | 5 networks, two hidden layers of 64, 300 Adam steps; majority; cautious = unanimous |
| program+net | the program search with the network's answers as proposals for unaudited cases (a tie-break among rules equally good on the evidence) |
| tree | scikit-learn decision tree, default settings |
| forest | scikit-learn random forest, 50 trees; cautious = unanimous |
| index | audited cases only |

## Protocol

Budgets 16, 32, 64, ... doubling up to the whole table (capped at 4,096 audits). Five seeds. Passive (random order) and chosen audits. After each budget every learner answers every case in the table. Recorded: share right over all cases and over unaudited cases; in cautious mode the shares answered, wrong and abstained; rules per program; whether the programs reproduce the evidence.

## Pass rules, fixed now

"Reaches 99%" = the first budget at which 99% of all cases are right, median over seeds; never reaching it is worse than reaching it.

| Rule | Passes if |
|---|---|
| R1. Fewer audits than the network | with passive audits, program reaches 99% with no more audits than net, on at least 5 of 8 datasets |
| R2. Fewer silent errors than the network | averaged over the budgets below the full table, program's cautious wrong share is at most half of net's, on at least 5 of 8 datasets |
| R3. Against a decision tree | program reaches 99% with no more audits than tree, on at least 4 of 8 datasets |
| R4. Choosing audits helps | for program, chosen audits reach 99% with fewer audits than passive, on at least 5 of 8 datasets |
| R5. A network as proposer earns its place | program+net reaches 99% no later than program on at least 5 of 8, and strictly earlier on at least 2 |

Reading the outcome:

- R1 and R2 pass: the v0.4 addendum's result holds on rules I did not write, against networks.
- R3 fails: the learner has no edge over a standard decision tree. The stack's contribution would then be the bank around the learner (registers, versions, verification, abstention), not the learner.
- R1 fails: the addendum's result was a product of my own languages. Say so and stop recommending the stack on this evidence.

## Honesty notes

- Internal test on public data. The rules are other people's; the choice of datasets, language and comparators is mine.
- Tree and forest are standard tools, not tuned. The network is small and not tuned.
- Downloads: eight text files, about 1.3 MB in total, from `archive.ics.uci.edu`, into `data/external/uci/`. Read as text; scripts that read them run with `python -I`.
