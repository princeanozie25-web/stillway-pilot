# v0.6 round 2 specification: a bank with three levels of reuse, for a second hidden family

Fable, 21 November 2026. Frozen in one commit with `v06/family2.py` and `v06/report2.py`, before the second hidden family exists. Prince approved the round. Brief for its author: `docs/v06r2_codex_family_brief.md`.

## Why

Round 1 (`docs/v06_codex_hidden_memo.md`, `docs/v06_codex_reveal_note.md`) showed the v0.6 bank is all or nothing. It recognises an exact repeat. It mistook a copy with 8 changed cases for its original, threw the match away at the first contradiction, and gave nothing on policies far from every past one. This round tests a bank that reuses a past policy at three levels and says what it has and has not verified.

## The bank (`v06/family2.py`)

| Level | Used when | What it answers |
|---|---|---|
| 1. Recognise | some past table agrees with every audit | the vote of the tables that still fit |
| 2. Amend | the best table agrees with at least 60% of the random audits and at least one audit contradicts it | that table, with local exceptions: an unaudited case takes an exception's decision when more of its audited neighbours (cases differing in at most one attribute) are exceptions than agree with the table |
| 3. Parts | chosen by held-out audits | 5 small networks whose inputs are the attributes plus every past policy's decision for the case |
| Scratch | chosen by held-out audits | 5 small networks on the attributes alone (unchanged from v0.6) |

- **Choosing the level.** Below 20 audits an eligible table level is used as it is. From 20 on, a fifth of the random audits is held out; the better of scratch and parts replaces the table level only if it wins by a margin (two standard errors for recognise and for a table that holds on 85% or more of the audits, shrinking to nothing at 60%).
- **Choosing audits (`bank3a`, the system under test).** While several past tables still fit, audit where they disagree. While amend is in use on a table that holds on at least 85% of the random audits, audit the neighbours of the exceptions found so far. Otherwise audit at random.
- **Cautious mode.** An answer for an unaudited case is given only when a bound supports it at 5%. For a table: (exceptions found + 3) / (random audits looked at), over audits with no other audited exception next to them; a clean match needs 60 audits. For a network: (held-out errors among its unanimous answers + 3) / (held-out unanimous answers).

`bank3` is the same bank with random audits only, reported beside it. Budgets: 4, 8, ..., 512, 724, 1024 and the full table. Three seeds.

## Groups, computed from the file itself

By the number of cases in which a new policy differs from its nearest past policy: **repeat** (0), **amended copy** (up to 15% of the table), **far** (more). The author's sealed labels split these further after the lock; they do not enter the rules.

## Pass rules, fixed now

"Audits to X": per new policy the median over seeds of the first budget at which X holds, then the median over the policies of a group. All for `bank3a`.

| Rule | Passes if |
|---|---|
| M1. A repeat is found | every case right within 16 audits, and no cautious error at any budget |
| M2a. An amended copy never collapses | from 16 audits on, the share right is at least that of the original table less 2 points, on at least 80% of amended copies |
| M2b. An amended copy is learned | every case right with fewer audits than scratch |
| M2c. An amended copy is not passed off as its original | cautious errors at most 1% of cases (mean over budgets below the full table) |
| M3. No harm far away | audits to 99% within one doubling of scratch, and from 16 audits on never more than 3 points below scratch at any budget |
| M4. Help far away | fewer audits to 99% than scratch |
| M5. Fewer silent errors far away | cautious errors no higher than scratch's |

## Development record: this design on the three spent families

Six designs were tried on round 1's hidden family and the two Unicode families (all spent; raw files for each design in `results/v06r2/dev_iter1` to `dev_iter5` and, for the frozen one, `results/v06r2/`). The frozen design gives:

| Rule | Round 1 hidden family | Unicode cardinal | Unicode ordinal |
|---|---|---|---|
| M1 | Pass (4 audits) | Pass (8) | Pass (12) |
| M2a | **Fail** (1 of 2) | **Fail** (2 of 5) | **Fail** (3 of 6) |
| M2b | Pass (576 against 1,024) | Pass (512 against 1,000) | Pass (384 against 1,000) |
| M2c | Pass (0.03%) | Pass (0.01%) | Pass (0.01%) |
| M3 | Pass | **Fail** (192 against 128; 8.8 points short at one budget) | **Fail** (384 against 128; 10.8 points short) |
| M4 | **Fail** (512 against 512) | **Fail** | **Fail** |
| M5 | Pass (0.02% against 18.64%) | Pass (0.00% against 6.04%) | Pass (0.01% against 6.87%) |

So I am freezing a design that I know fails three of its own rules on spent data. I stopped tuning because each fix for one group cost another, and a seventh design chosen on the same three families would say less, not more.

## What I expect on the fresh family

- **M1, M2b, M2c, M5: pass.** These are the claim: repeats are found; an amended copy is completed faster by hunting around the contradiction; and in cautious mode the bank almost never gives a wrong answer, where scratch is wrong on 6% to 19% of cases while unanimous.
- **M2a: at risk.** An amended copy close to the 15% line still drops below its original table for a budget or two when the bank switches level.
- **M3: at risk.** When the family's rules are easy for scratch, the bank holds on to a part-fitting table for too long.
- **M4: fail.** Nothing in three families suggests the bank makes a far policy cheaper to learn. I keep the rule so the claim stays on the table and can fail in the open.
- Scattered copies (if the author includes them): local exceptions should not generalise, so M2b should fail on them and M2c should still hold. The frozen rules pool rule-shaped and scattered copies; the split is reported after the lock.

## Limits

- The middle level's neighbourhood (one attribute different) assumes changes are local in the attributes. A change defined some other way will look scattered.
- The design was tuned on three families, one of them by the same author as the test family.
- Budgets still jump; a difference of one step can be noise.
- The cautious bounds are rules of thumb ("plus three" in place of an exact binomial bound), not proofs.

## How to run

```
python -I v06/family2.py FAMILY.json --shard 0 --of 1 --seeds 3      # about 25 minutes for 20 new policies of 1,440 cases; shards run in parallel
python v06/report2.py NAME [LABELS.tsv]
```
