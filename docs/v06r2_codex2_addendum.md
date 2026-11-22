# v0.6 round 2: addendum to the locked run on Codex's second hidden family

For Prince Anozie and Codex, 22 November 2026. From Fable. Attached to the results locked at commit `a79545b`; none of the locked files is changed. Tables: `results/v06r2/codex_hidden2_addendum.md`, written by `python v06/addendum2.py codex_hidden2` from the locked raw file.

**Status: frozen run, labels now released.** The verdict in `docs/v06r2_codex2_memo.md` is unchanged (six of seven frozen rules pass; M4 fails). This addendum regroups the same raw output by the holder's labels. Nothing was rerun or tuned.

## The holder's groups

| Group | Policies |
|---|---|
| Repeat (6) | p038 p046 p048 p051 p062 p065 |
| Local amendment (8) | p037 p040 p041 p043 p052 p055 p059 p061 |
| Scattered amendment (4) | p047 p049 p057 p058 |
| Far variant (6) | p044 p045 p053 p056 p060 p066 |
| New shape (6) | p039 p042 p050 p054 p063 p064 |

## What the regrouping shows

1. **Exact-learning cost.** Medians, with the range over every policy and seed in brackets.

   | Group | From scratch | Bank, chosen audits |
   |---|---|---|
   | Repeat | 1,600 (1,024 to 1,600) | 4 (4 to 8) |
   | Local amendment | 1,600 (all) | 618 (128 to 1,600) |
   | Scattered amendment | 1,600 (all) | 1,600 (64 to 1,600) |
   | Far variant | 1,600 (1,024 to 1,600) | 1,600 (1,024 to 1,600) |
   | New shape | 1,600 (all) | 1,600 (all) |

   The saving on amendments is a saving on **local** amendments. On scattered amendments the bank reaches the exact table early in 2 of 12 runs, both on the one-case amendment p047; the 8, 50 and 200-case scattered amendments need the full table in every seed.

2. **The figures quoted earlier are medians.** Four audits on repeats is a median (range 4 to 8). 724 against 1,600 on amendments was the median over all twelve amended copies to 99% of cases; by the holder's groups the medians to 99% are 130 audits for local amendments (range 4 to 724) and 802 for scattered ones (range 4 to 1,600).

3. **Far policies.** Both the bank and scratch needed the full 1,600 audits to reach 99% on new shapes in every run, and a median of 1,024 (range 724 to 1,600) on far variants. The bank buys nothing there.

4. **Interim regressions against keeping the old rule.** Keeping the old rule is right on 95.95% of cases on average for both kinds of amendment. The bank is below that in 14% of policy-seed-budget cells on local amendments and 22% on scattered ones. The dips come in two places:
   - at 4 and 8 audits, before the past policy is recognised (single worst cell 59.5 points below the old rule);
   - **at 64 to 256 audits on local amendments, after an exception has been found**: the mean is 0.7 to 2.1 points below the old rule and the worst single cells are 6.1, 13.1 and 22.3 points below. From 512 audits on, no cell is below.

   The second dip is the one the v0.8 audit-mixing test is about.

5. **Coverage and error among answers (cautious mode, bank with chosen audits).** On local amendments coverage rises from 48% at 64 audits to 82% at 512 and 91% at 1,024, with error among answered cases 0.48%, 0.04% and 0.01%. On scattered amendments coverage is similar (36%, 81%, 90%) and error among answers is higher and does not fall steadily: 0.26%, 0.67%, 0.35%, peaking at 1.04% at 724 audits. Scratch at 64 audits answers 64% to 67% of cases and is wrong on 44% to 46% of its answers. The full grid is in the tables file.

## How far this goes

- **Locality is a hypothesis, not a result.** Eight local and four scattered amendments, one family, one holder. It is carried into v0.8 as a prediction to test on coding and table work, on fresh policies.
- **The one-case amendments cannot tell the two patterns apart.** p059, p061 (labelled local) and p047 (labelled scattered) each change a single case, so the changed points alone carry no spatial pattern; their costs (64 to 1,600 audits across seeds) say nothing about locality.
- Budgets are a grid of eleven points, so every cost is the first grid point reaching the mark.
- The two defects in the frozen report script noted in the memo are unchanged.
