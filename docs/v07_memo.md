# v0.7 memo: at full strength experience taught twelve fixes and cost the rest; at a quarter strength it helped

For Prince Anozie, 22 November 2026. From Fable. One page. Report: `results/v07/REPORT_v07.md`. Protocol: `docs/v07_protocol.md`.

**The question.** Does experience from previous bugs increase the share of unfamiliar repositories a small local student fixes on the first patch, under the same inference budget?

**The answer on development data: not as designed, and yes at a lower dose.** The final set is Codex's and is still sealed; everything is locked for it.

| First patch correct | Unchanged student | Trained on final patches | Trained on experience | Experience + bank |
|---|---|---|---|---|
| Renamed repeats (24) | 8% | 100% | 96% | 90% |
| Same cause, new setting (16) | 25% | 50% | 63% | 73% |
| Lookalikes (16) | 25% | 8% | 6% | 6% |
| Mechanisms never trained (16) | 25% | 2% | 6% | 15% |
| **All unfamiliar (48)** | **25%** | **20%** | **25%** | **31%** |

- I froze +10 points on unfamiliar repositories as the smallest improvement worth having. Measured: +6.2, with an interval from -10 to +23. **It fails.**
- On repeats the gain is +82 points. By the frozen rules that is a **recognition result**.

**What the student is.** Qwen2.5-Coder 1.5B, pinned by hash, running on the laptop, taught with a small adapter. 120 training repositories and 72 development repositories, all generated and all checked by execution. Three seeds of every trained arm.

**The finding I did not plan for.** The trained adapter can be applied at any strength between none and full without retraining. I tried half strength once to see whether the damage was a matter of dose.

| Experience adapter, no bank | Unchanged | Quarter strength | Half | Three-quarters | Full |
|---|---|---|---|---|---|
| Unfamiliar repositories fixed | 25% | 36% | 38% | 31% | 27% |
| Renamed repeats fixed | 8% | 25% | 47% | 82% | 92% |
| Unfamiliar repositories where a passing test was broken | 2% | 6% | 17% | 32% | 35% |

At a quarter strength the student beats the unchanged one on 14 development repositories and loses on none (+11 points on unfamiliar, interval +4 to +19). It was found on development data and picked from this curve, so it proves nothing yet. It is now a separate rule on the final set, written before that set is opened. It cannot change the frozen verdict; if it passes there, whether it earns the larger-model comparison is your call.

**Three more things worth knowing.**

1. **It learned fixes, not diagnosis.** On lookalikes the experience-trained student breaks a test that was passing in 60% to 77% of repositories. The unchanged student breaks none. Handed an integer-division bug, it writes "the loop bound stops one short" and adds one.
2. **The bank is read only where it agrees with the student.** It adds 12 points on the same cause in a new setting and nothing elsewhere. A deliberately wrong diagnostic costs almost nothing. When a test contradicts the diagnostic the bank reopens it, and the student submits the old fix anyway (28 of 48 lookalike episodes).
3. **Executed experience is better material than final patches**, by a little: predictions that match what the code prints (45% against 7%) and +12 points on a new setting. Not enough to pass.

**Not run, by a rule I set beforehand.** Sleep promotion against rehearsal needed the bank to add 5 points. It added 4.2, from one seed of three.

**Beyond the brief.** The unchanged student given the bank's text: no change. A gate that sends only familiar-looking repositories to the trained student: lets through 71 of 72. Final-patch training at half strength: +5 points on unfamiliar, so part of the low-dose gain is not specific to experience. The bank at half strength makes things worse.

**Costs kept apart.** I wrote every design, test, fix and diagnostic; that teacher cost is outside every arm. One mismatch between arms: the bank-family adapter saw 19% fewer training tokens than the other two.

**What happens next.**

- Codex builds the final set to `docs/v07_final_set_brief.md`; I run it once; Codex grades. I expect the same frozen verdict, and a smaller low-dose gain than on development data; both guesses are written into the protocol.
- The final set is the only blind test of the low-dose result, so it is worth Codex's time.
- No claim about general reasoning is made.
