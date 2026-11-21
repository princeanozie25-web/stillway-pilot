# v0.6 memo: the hidden family from Codex

For Astra, Codex and Prince Anozie, 21 November 2026. From Fable. Outputs locked in commit `b7120cd9b1551806d0075c67d3a3e2bae48ce168` before anyone was asked what the hidden policies are. I have not read the rules in `family_codex.json`; I read its shape only (56 policies, 36 past, 20 new, 1,440 cases, 4 decisions).

## 1. Verdict

**On the family I could not bias, experience did not make a novel policy cheaper to learn.** The frozen rule L1 fails: 512 audits with the bank, 512 from scratch. What held is recognition: a new policy whose rule the bank already holds is identified exactly in 4 audits, where learning it from scratch takes the whole table.

| Rule (frozen in `docs/v06_spec.md`) | Measured | Result |
|---|---|---|
| L1. Experience helps on novel rules | best of bank_row, programs, selector: 512 audits to 99%; scratch: 512 | **Fail** |
| L2. Programs need no more audits than bank rows on novel rules | programs 976; bank rows never reach 99% | Pass (see section 4) |
| L3. A rule seen before is recognised within 16 chosen audits, no cautious error | 4 audits to 100%; cautious wrong 0.000% | **Pass** |
| L4. Selector within one budget step of the best single learner, both groups | novel: 512 against 512; seen: 6 against 4 | Pass (see section 3) |
| L5. Choosing audits helps the selector on novel rules | chosen 512; passive 512 | **Fail** |

For comparison, L1 passed on both Unicode families (64 against 128 audits; 16 against 96). On Codex's it does not.

## 2. What was run

- Input: `family_codex.json`, SHA-256 `2a4e40c66da8c71cb4c0d9b7bead55caefbedf3da72386ca0052658f3bb29565`, checked against the digest Astra gave before anything was run.
- Code: commit `e84c46e5e439a05fea3f338e9b44571f2b4a9454`, clean working tree. `v06/family.py` is byte-identical to the freeze commit `2b125d1`.
- Commands, once each, from the repository root:
  `python -I v06/family.py family_codex.json --shard 0 --of 1 --seeds 3` (2,489 s, no errors), then `python v06/report.py codex_hidden`.
- Nothing was rerun, tuned or dropped. All 6,480 result cells are in the raw file: 20 new policies, 12 curves (6 learners, passive and chosen audits), 9 budgets, 3 seeds.

## 3. The post-freeze change to L4 reporting

One line of `v06/report.py` differs from the freeze commit. It was changed in commit `ea7d3f3`, after the freeze and before Codex's file existed.

```
frozen (2b125d1):   step[selector] <= step[best] + 1      step = position of a budget in the budget list
now (ea7d3f3):      selector <= 2 * best
```

- **Why.** The medians are taken over rules. With an even number of rules a median can fall between two budgets (48 on the ordinal family), which is not in the `step` table, so the frozen line stopped with `KeyError: 48.0`.
- **What it does on this family.** The frozen line would have stopped here too: the selector's median on the six seen rules is 6. Three readings of L4 are in `results/v06/codex_hidden_L4_check.json` (`python v06/l4_check.py codex_hidden`):

| Reading | Novel rules (512 against 512) | Seen rules (6 against 4) | L4 |
|---|---|---|---|
| Frozen code | pass | not computable (KeyError) | not computable |
| Post-freeze code (factor of two) | pass | pass | Pass |
| Spec wording, literal (selector at most the budget one step above the best learner's) | pass | pass | Pass |

- **Where the readings can differ.** At the top of the budget list. The last step here is 512 to 1,440, more than a factor of two, so the post-freeze line is stricter than the frozen wording there. That case did not occur. On all three families the readings that can be computed agree.
- No other line of the report script changed, and no number in the tables depends on this line.

## 4. What the passes and failures mean

**Novel rules (14 policies).** Median audits to 99% of cases right, passive audits:

| scratch | bank rows (weights) | tables | programs | selector |
|---|---|---|---|---|
| 512 | never | 512 | 976 | 512 |

- The same in every seed: scratch 512 and selector 512 in seeds 0, 1 and 2.
- Policy by policy against scratch: the selector needs fewer audits on 3, the same on 8, more on 3. Tables: 4, 6, 4.
- **Bank rows fail outright.** The shared network reproduces 100% of past decisions, and a new row on top of it levels off at 65.6% of cases right. It never reaches 99% on 13 of 14 novel rules.
- **The program language holds none of Codex's rules.** No new policy lies in the program family, and the median program found for a past policy has zero rules. The program learner fell back to scratch 99% of the time. L2 passes only because bank rows are worse still; neither store of experience beat scratch.
- On four novel policies (p041, p043, p047, p055) no learner's median is below the whole table. On p041 and p047 no learner got there in any seed.
- Choosing audits did not help the selector (512 either way) and hurt scratch (848 against 512).

**Seen rules (6 policies).** Tables reach 100% in 4 audits (passive and chosen) with zero cautious errors at every budget. Scratch needs all 1,440 cases on four of the six. Bank rows need 256.

## 5. Two things the frozen rules do not show (found after the run; not pass rules)

**A near-copy of a past policy is taken for the past policy.** p046 is counted as novel, yet the table learner answers 99.44% of its cases correctly from 4 audits in all three seeds. It has matched a past policy that differs from p046 in 8 of 1,440 cases, and in cautious mode it answers those 8 wrongly while unanimous. The 99% yardstick scores this as a success. Without p046 the bank gives almost nothing on novel rules: mean share right at 32 audits is 54.9% for tables against 53.3% for scratch.

**When an audit contradicts the matched policy, the learner throws the match away.** On p046, once the audits include one of the 8 changed cases, the table learner drops from 99.4% right to between 32% and 69% (from 16 audits in one seed, from 64 in another, from 256 in the third), because it falls back to learning from scratch. The bank has no way to hold "that past policy, with these exceptions". My guess is that p046 is an amended copy of a past policy. That guess is from the outputs alone; the breakdown will confirm or refute it.

## 6. What this changes

- **Withdrawn as a general claim:** "experience with related policies cuts the audits a novel policy needs." It holds on the two Unicode families, whose rules recombine a small shared set of tests. It does not hold on a family written by someone else to test it.
- **Still standing:** exact recognition of a seen rule, cheaply and without silent error (three families of three).
- **Not rescued:** network weights as the store of experience (never reach 99% on novel rules here or on cardinal rules), the fixed two-test program language (fits nothing here), choosing audits for novel rules (no gain on any family).
- **The gap the run exposes:** the bank is all or nothing. It either holds the exact rule or starts again. A policy that is an old one with a few changes gets no benefit and, worse, passes as the old one below the yardstick's resolution.

## 7. Questions for the breakdown (asked only now that the outputs are locked)

1. For each new policy p037 to p056: is it an exact repeat, an amended copy of a past policy (and how many cases differ), a recombination of parts of past policies, or new structure?
2. Is p046 an amended copy, as the outputs suggest? Are there others that differ from a past policy in more than 1% of cases?
3. What do p041, p043, p047 and p055 have in common? Nothing learned them short of the full table.
4. What kinds of tests do the rules use (comparisons, counts, interactions of three or more attributes)? The two-test language found nothing.

## 8. Files and hashes

| File | SHA-256 (first 16) |
|---|---|
| `family_codex.json` (input) | `2a4e40c66da8c71c` |
| `results/v06/codex_hidden_shard0.json` (raw, every seed and arm) | `4273c3d41933f2df` |
| `results/v06/codex_hidden_tables.md` | `5d423a227c29428f` |
| `results/v06/codex_hidden_rules.json` | `9be3a13370b461c8` |
| `logs/v06_codex_run.log` | `edb1c1660ac000ec` |
| `results/v06/codex_hidden_L4_check.json` | `ae7eb991adcb6d8c` |
| `results/v06/codex_hidden_per_policy.md` (every seed, per policy) | `f6297b9c0fbafab2` |

Full digests, the code hashes and the report-script diff are in `results/v06/codex_hidden_LOCK.json`. Added after the freeze, all read-only over the raw file: `v06/l4_check.py`, `v06/per_policy.py`, `v06/lock_outputs.py`.

## 9. Limits

- One family, 20 new policies, 3 seeds, one author. Budgets double, so a difference of one step can be noise; here the medians are equal, not close.
- The harness was frozen before the Unicode files were fetched, with plural rules in mind. Its learners were not designed for Codex's attributes, and the result may partly measure that.
- Sections 5 to 7 were written after seeing the results.
