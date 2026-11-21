# v0.6 note: Codex's breakdown of the hidden family, read against the locked results

For Prince Anozie, Astra and Codex, 21 November 2026. From Fable. Written after the outputs were locked (commit `b7120cd`) and the memo sent (`622bb68`). The locked memo `docs/v06_codex_hidden_memo.md` is unchanged; this note adds to it.

## 1. The breakdown agrees with the locked outputs

Codex's table is saved as received in `data/external/codex/reveal_2026-11-21.tsv`. All 20 rows check out (`python -I v06/x_reveal_check.py`): the distance to the nearest past policy, which past policy that is, and both audit columns match the family file and my locked raw file. One tie: p056 is equally close to p010 and p036.

## 2. What the frozen "novel" group was hiding

My harness had two groups, seen and novel. Codex wrote three. The 14 "novel" policies are 8 variants and 6 new shapes, and they behave differently.

Median audits to 99% of cases right, passive audits, from the locked file (`results/v06/codex_hidden_by_reveal.md`):

| Codex's group | Policies | Cases differing from the nearest past policy | Scratch | Selector (the bank) | Bank needs fewer / same / more audits |
|---|---|---|---|---|---|
| Repeat | 6 | 0 | 1,440 | 6 | 6 / 0 / 0 |
| Variant | 8 | 8 to 788 | 512 | 384 | 3 / 4 / 1 |
| New shape | 6 | 950 to 1,052 | 976 | 976 | 0 / 4 / 2 |

- **Repeats:** the bank's one clear result. 4 to 8 audits against 256 to 1,440.
- **New shapes:** nothing transfers, and the bank costs a little on two of six. Bank rows (network weights) level off at 51% right.
- **Variants:** a small early gain and no reliable gain at the yardstick. Of the three wins, one is p046, the near-copy the bank mistook for its original. Without p046 the selector is ahead of scratch by about 5 points in the middle of the curve (84.7% against 79.4% right at 128 audits) and level by 512. L1 still fails; the locked verdict does not change.

## 3. Answers to the four questions I asked

1. **What each new policy is:** 6 repeats, 8 variants, 6 new shapes, as above.
2. **p046 is an amended copy**, as the outputs suggested: 8 cases away from p024. One other variant is close in table terms: p047, 194 cases (13%) from p002. The bank gave it nothing. **The other six variants differ from every past policy in 412 to 788 cases (29% to 55%).** They are variants of a rule's parameters, not of its table. A bank that stores tables cannot see that kinship.
3. **What the unlearned policies share:** modular tests. p041, p043 and p055 are the three "distance and modular test" shapes, and p047 is a modular variant. In the locked run every one of the eight policies with a modular test needed the whole table from scratch. That is a limit of my scratch learner (a small network on one-hot attributes), separate from the bank.
4. **Kinds of test:** threshold counts, pair comparisons, modular tests, max and offset, order statistics, distance. None can be written as two equality tests, which is why the program language found zero rules for the median past policy.

## 4. One fix tried after the reveal (exploratory; this family is now spent as a blind test)

`v06/x_features.py`. Hand the learner what every past policy decides for a case, as extra inputs to the same small network ("feat"). The idea: if past policies already compute a feature the new rule needs, the network can reuse it. Also "patch" (the past table that agrees with most audits, audited cases overwritten) and "pick" (held-out audits choose between patch, feat and scratch). Fresh audit orders, 3 seeds, scratch rerun alongside on the same audits.

| Hidden family, by shape | Policies | Scratch | Feat | Pick |
|---|---|---|---|---|
| Modular tests | 5 | 1,440 | **512** | 8 |
| Distance and modular test | 3 | 1,440 | 1,440 | 1,440 |
| Max and offset | 3 | 1,440 | 1,440 | 1,440 |
| Threshold count | 3 | 512 | 512 | 512 |
| Pair comparisons | 3 | 256 | 512 | 256 |
| Order statistic | 3 | 512 | 1,440 | 512 |

- **It transfers where a hard feature is shared.** On all five modular-test policies feat needs 512 audits where scratch needs the whole table. On p047, the variant the frozen bank could not help, feat is 91% right at 128 audits against 55% for scratch.
- **It costs where nothing is shared.** Feat is slower on all three order-statistic policies and all three pair-comparison policies. About seven times more inputs (166 against 22) is a price.
- **Held-out choice removes most of the cost.** Pick against scratch, policies with fewer / same / more audits: repeats 6 / 0 / 0, variants 2 / 5 / 1, new shapes 0 / 6 / 0.
- **Patch stops the collapse on p046** (99.4% right throughout, rising as the 8 changed cases are audited) but stays silently wrong on those cases until each is audited.
- **Unicode families, same script:** on novel rules feat needs fewer / same / more audits than scratch on 3 / 3 / 1 cardinal rules and 3 / 6 / 1 ordinal rules (median 16 audits against 96 on ordinals).

**This does not rescue L1.** At the 99% yardstick, on Codex's 14 non-repeat policies, pick is ahead on 2, level on 11, behind on 1. What it shows is narrower: transfer exists when the new rule needs something that is hard to learn from raw attributes and that past policies already compute. It was designed after seeing which shapes exist, on data I had already seen results for.

## 5. Where this leaves the claims

| Claim | After the reveal |
|---|---|
| The bank recognises a policy it already holds, cheaply and without silent error | Stands. Three families of three; all six repeats here. |
| The bank makes a new policy cheaper to learn | Not shown on rules I did not write. No effect on new shapes. On variants, an early gain of a few points that is gone by the yardstick. |
| Tables are the right store of experience | Only for repeats. Six of eight variants are near in rule terms and far in table terms. |
| Network weights (one row per policy) as the store | Fails: levels off near 75% on variants and 51% on new shapes; never 99%. |
| The 99% yardstick | Too coarse to see an amended copy: p046 passes as its original with 8 wrong answers given unanimously. |

Two limits of my own harness, now visible: the scratch baseline cannot learn modular tests short of the full table (so 8 of 20 policies sit at the ceiling for every learner), and budgets jump from 512 to 1,440, which hides any difference in that range.

## 6. What I would freeze next, if you want another round

A bank with three levels of reuse, tested on a second hidden family whose group labels stay sealed until the outputs are locked:

1. **Recognise:** exact table match (as now).
2. **Amend:** nearest past table plus audited exceptions, reported as "past policy X with N changes", abstaining near a contradiction instead of answering unanimously.
3. **Reuse parts:** past decisions as inputs, with held-out audits choosing against scratch.

Pass rules set per group in advance: repeats, amended copies at graded distances (1, 8, 50, 200 cases), parameter variants, new shapes. An exact-rule yardstick alongside 99%, and budgets filled in between 512 and the full table. This needs Codex's time for the second family; that is the only thing I need from you.

## 7. Files

| File | What |
|---|---|
| `data/external/codex/reveal_2026-11-21.tsv` | The breakdown as received |
| `results/v06/codex_hidden_reveal_check.json` | Row-by-row check against the file and the locked outputs |
| `results/v06/codex_hidden_by_reveal.md` | Locked results regrouped by Codex's groups and shapes |
| `results/v06/x_features_codex_hidden.md`, `x_features_cldr_cardinal.md`, `x_features_cldr_ordinal.md` | The exploratory test, with raw shard files beside them |
| `v06/x_reveal_check.py`, `v06/x_reveal_groups.py`, `v06/x_features.py` | Scripts, all added after the lock |
