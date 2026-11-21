# Stillway v0.5 report: the program-search learner on rules I did not write

Fable, 21 November 2026. Branch `v0.5`. Freeze commit `38588234e1a8e1e32996eda97586a260119ce8da` (spec `docs/v05_spec.md` and `v05/blind.py`), made before any data was downloaded. Tables in full: `results/v05/tables.md` (`v05/report.py`).

## 1. Verdict

**The recommendation I made at the end of v0.4 does not survive.** I said to make program search the main line. On eight public rule tables written by other people, the frozen program learner failed all five pass rules. A small network did better.

| Rule (frozen) | Holds on | Result |
|---|---|---|
| R1. Program needs no more audits than the network (5 of 8 needed) | 3: MONK-1, MONK-3, lenses | **Fail** |
| R2. Program's cautious wrong share at most half the network's (5 of 8) | 1: MONK-3 | **Fail** |
| R3. Program needs no more audits than a decision tree (4 of 8) | 3: MONK-1, MONK-3, lenses | **Fail** |
| R4. Choosing audits helps the program learner (5 of 8) | 0 | **Fail** |
| R5. A network as proposer for the search (no later on 5, earlier on 2) | no later on 3, earlier on 1 | **Fail** |

The spec said in advance how to read this: the v0.4 addendum's result was a product of languages I wrote myself.

## 2. The test

Eight UCI tables, each a complete or near-complete list of cases with the decision someone else's rule gives: car, nursery, balance scale, MONK-1, MONK-2, MONK-3, lenses, tic-tac-toe endgames. Each is used as an auditor. A learner asks for the decision of n cases, then answers every case in the table, so generalisation is measured exactly. Budgets double from 16 to the whole table (capped at 4,096). Five seeds.

The program learner is the v0.4 one with the domain-specific tests removed: decision lists whose rules test at most two attributes (`attribute = value` or `attribute != value`), found by greedy search, a committee of seven.

## 3. Results

Audits needed before 99% of all cases are right (median of 5 seeds; passive audits unless stated):

| Dataset | Cases | Program | Network | Decision tree | Network, choosing its audits |
|---|---|---|---|---|---|
| MONK-1 | 432 | **64** | 256 | 432 | 128 |
| MONK-3 | 432 | 128 | 128 | 128 | 128 |
| lenses | 24 | 24 | 24 | 24 | 24 |
| car | 1,728 | never | **1,024** | 1,728 | 512 |
| nursery | 12,960 | never | **2,048** | never (cap 4,096) | 1,024 |
| balance scale | 625 | never | **512** | 625 | 256 |
| MONK-2 | 432 | never | **256** | 432 | 128 |
| tic-tac-toe | 958 | never | **958** | 958 | 512 |

- **Where the rule fits the language, search is the most frugal learner.** MONK-1: 64 audits, against 256 for the network and the whole table for a tree.
- **Where it does not fit, search fails outright.** On five tables no two-test rule is free of exceptions once enough cases are audited. The programs stop reproducing the evidence (0 of 7 lists at the last budget on all five) and accuracy falls as audits grow: on nursery from 84% at 256 audits to 69% at 4,096.
- **The network reached 99% on all eight**, with fewer audits than the tree on five.
- **Choosing audits helped the network**, not the program learner: it halved the network's audits on six tables.
- **Silent errors.** In cautious mode (answer only when the committee is unanimous), averaged over budgets below the full table, the program learner was wrong on 1.2% to 24.0% of all cases and the network on 4.1% to 16.3%; the program was lower on four tables and higher on four. A 50-tree forest answering only when unanimous was wrong on at most 0.2% and abstained on 86% to 98%.
- **A network as proposer for the search** helped once (MONK-3: 32 audits against 128).

**Pre-set secondary setting: three tests per rule** (seven smaller tables). The language then holds every rule at the full table, and the program learner ties the network on tic-tac-toe (512) and MONK-1 (128). It still needs more audits than the network on car (1,728 against 1,024), balance scale (625 against 512) and MONK-2 (432 against 256), and the search is three to five times slower (car: 1,085 s against 214 s).

## 4. A follow-up after the results (exploratory)

`v05/x_selector.py`: at each budget hold out a fifth of the audited cases, fit both learners on the rest, use whichever gets more held-out cases right. Same budgets, passive audits, two tests per rule.

| Dataset | Program | Network | Selector |
|---|---|---|---|
| MONK-1 | 64 | 256 | 64 |
| MONK-3 | 128 | 128 | 32 |
| lenses | 24 | 24 | 24 |
| car | never | 1,024 | 1,024 |
| balance scale | never | 512 | 512 |
| MONK-2 | never | 256 | 128 |
| tic-tac-toe | never | 958 | 512 |
| nursery | never | 2,048 | 2,048 |

It keeps the program where the program fits (chosen at every budget on MONK-1 and MONK-3) and moves to the network as audits accumulate where it does not (car: program chosen in 100% of seeds at 16 audits, 0% from 512). It matched or beat the better single learner on every table. This was designed after seeing the frozen results, on the same tables, with fresh random draws; the two cases where it beats both learners may be noise.

## 5. What this changes

**Withdrawn:** "learn programs by search, not weights by descent" as a general rule, and the recommendation to make program search the main line. In v0.4's world the search space contained the rules because I wrote both.

**What v0.4's addendum still shows:** when the hypothesis language contains the rule, search with verification is fast, exact and needs few audits (MONK-1 here; every v0.4 case). That is a statement about the language, not about search.

**What is untouched by this test:** typed registers, the versioned bank with a promotion gate, provenance, pinning and rollback, compiled tables, per-artifact certificates. None of them depends on what proposes a rule. On a finite table, whatever the proposer, its answers can be compiled into a table and checked case by case against an auditor.

**What the evidence now supports for the learner:**

1. Do not fix the language in advance. A small network was the safest proposer on rules I did not write.
2. Keep the search as a second proposer and let held-out audits choose. It costs seconds and wins where the rule is simple.
3. Let the proposer choose its audits when it is a network: half the human decisions on six of eight tables.
4. Deploy the result as a table or program either way, behind the same gate.

## 6. Limits of this test

- It tests one component. No registers, procedures, sessions or library; no family of related policies exists in these tables, so the v0.4 library result is neither confirmed nor refuted.
- The tables are small and noise-free. The network is tiny and untuned; so are the tree and forest.
- I chose the tables, from memory, and I knew roughly what several rules are. The language was fixed before the download, and it lost, so that knowledge did not help it.
- "Audits to 99%" is read off doubling budgets; differences of one step can be noise.
- Still internal. Codex has not replayed it.

## 7. How to run it

```
python -I v05/blind.py monks1 --tests 2        # one table, all learners, passive and chosen audits (about 2 minutes)
python -I v05/x_selector.py monks1             # the follow-up
python v05/report.py                           # tables and pass rules
```

Data: eight text files (1.17 MB) from `archive.ics.uci.edu/ml/machine-learning-databases/`, in `data/external/uci/`, fetched after the freeze commit.
