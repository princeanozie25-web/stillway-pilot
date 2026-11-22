# v0.7 blind closeout

Fable, for Prince Anozie, 22 November 2026. This closes v0.7. The tables are Codex's, produced by the frozen `v07/report.py` on Codex's private grading of the 42 raw files I returned ungraded (commit `cea985b`). They are archived as received in `results/v07/blind/` with their hashes. I did not grade, and I have not seen the hidden half or the graded records, only these tables.

**Verdict by the frozen rules: recognition result.** The gain from experience is confined to repeats. This is the verdict I locked on development data and expected on the final set.

## The primary rules, first

| Rule | Measured on Codex's 96 repositories | Result |
|---|---|---|
| **P1.** Experience + bank minus unchanged, repositories that are not repeats (72), at least +10 points with the interval above 0 | **−8.8 points** (repositories −21.8 to +4.2; whole families −32.4 to +14.8); better on 17, worse on 17 | **Fail** |
| **P2.** Regressions: share of non-repeats where the patch breaks a hidden test, at most 10 points above the unchanged student | 44.0% against 4.2% | **Fail** |
| R1. Recognition: the same difference on renamed repeats (24) | +80.6 points (+68.1 to +91.7) | Pass |

First patch correct, % of repositories:

| | Unchanged | Final patches | Experience | Experience + bank |
|---|---|---|---|---|
| Renamed repeats (24) | 8.3 | 100 | 94.4 | 88.9 |
| Same cause, new setting (24) | 8.3 | 52.8 | 41.7 | 45.8 |
| Lookalikes (24) | 33.3 | 29.2 | 6.9 | 1.4 |
| Mechanisms never trained (24) | 33.3 | 12.5 | 6.9 | 1.4 |
| **All that are not repeats (72)** | **25.0** | 31.5 | 18.5 | **16.2** |

- Every secondary rule fails. Executed experience was worse than final patches on non-repeats (−13.0 points, −19.4 to −6.9). The bank made the experience-trained student worse (−6.5, −12.0 to −1.4). A deliberately wrong diagnostic cost nothing (−1.9).
- On lookalikes the experience + bank student broke a hidden test in 87.5% of repositories; the unchanged student in 4.2%.

## The reduced-strength rules, separately

These were added after development results were seen. They are reported beside the verdict and cannot change it.

| Rule | Measured | Result |
|---|---|---|
| **X4.** Quarter-strength experience adapter minus unchanged, non-repeats, at least +10 points with the repository interval above 0 | **+13.4 points** (repositories +3.2 to +24.1; whole families −1.4 to +30.1); better on 20, worse on 7 | **Pass** |
| X5. Its regressions at most 10 points above the unchanged student | 9.7% against 4.2% | Pass |
| X1. Half-strength experience adapter minus unchanged, non-repeats | +4.6 (−6.9 to +15.7) | Fail |
| X2. At half strength, experience beats final patches by 5 points | −8.3 (−16.7 to 0.0) | Fail |
| X3. Half-strength regressions | 23.6% against 4.2% | Fail |

What the quarter-strength pass does and does not show:

- It replicated on a set I had never seen, by the rule written before that set was opened: 38.4% of non-repeats fixed against 25.0%, with few regressions.
- **The interval over whole families includes zero** (−1.4 to +30.1). The rule was written on repositories, so it passes; the family interval is the more cautious reading.
- **It is not evidence that experience is what helps.** Final patches at half strength fixed 38.0% of non-repeats, the same as the quarter-strength experience adapter, and there was no final-patch arm at a quarter strength. The comparison that would separate "a weak adapter helps" from "weak experience helps" was not in the protocol.

## My two predictions, written into the protocol before the set was opened

| Prediction | Outcome |
|---|---|
| The frozen verdict will be the same as on development data: a recognition result | Right |
| The quarter-strength gain will be smaller than on development data (+11.1 points) | Wrong: +13.4 |

## Carried forward, unchanged

- The bank-family adapter (used by the experience + bank arms and by every reduced-strength experience arm) saw 19% fewer training tokens than the final-patch and experience adapters. Any comparison of it with the other two carries that mismatch, including the quarter-strength result.
- Nothing in v0.7 was tuned, retrained or rerun after the grades. Anything these grades suggest goes to a later protocol with fresh final cases: see the follow-up queue (`docs/followup_queue.md` on branch `v0.8`), where the quarter-strength replication against a strength-matched final-patch baseline on fresh families is entered.
