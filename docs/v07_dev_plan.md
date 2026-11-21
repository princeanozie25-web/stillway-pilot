# v0.7 development plan, written before any trained arm has been evaluated

Fable, 21 November 2026, 20:05. Committed while the first adapter is still training. The final protocol (`docs/v07_protocol.md`) is frozen later, after development results and before the final set is opened; this note fixes the things that must not be chosen after seeing development results.

## What is being run

- Student: `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revision `2e1fd397`, 32-bit floats, Apple GPU. Pin and smoke test: `results/v07/MODEL_PIN.json`, `results/v07/SMOKE_MODEL.json`.
- 120 training repositories from 12 templates and 10 naming schemes; 72 development repositories (24 renamed repeats G1, 16 same cause with changed preconditions G2, 16 lookalikes G3, 16 absent mechanisms G4) in 4 naming schemes never used in training. All 192 are checked by execution (`v07/build_tasks.py`).
- Every arm: the same system text, two proposed tests each with a prediction made before execution, one submitted patch, the same token limits (`stillway7/episode.py`, `LIMITS`).
- Arms: A unchanged; B trained on final patches; C trained on the teacher's executed traces; D, E, F, W share one adapter trained on the same traces with mixed inserts, and differ only in the insert at test time (D bank diagnostic, E nearest past example, F nothing, W a deliberately wrong diagnostic); D1 is D with version 1 of every diagnostic.
- Training: 300 updates, 2,048 tokens per update for every adapter, three seeds.

## Prompt changes already made, and on what data

The prompt was changed twice after looking at the unchanged student on 12 training repositories (a worked format example was added to the system text; files were put before the issue). The unchanged student went from 1 of 12 to 3 of 12. No development repository was used. The prompt is now fixed.

## Fixed now

1. **Primary comparison on development data:** D minus A, first-patch success, on the 48 repositories that are not repeats (G2, G3, G4). Repeats (G1) are always reported separately.
2. **"A procedure transfers"** (the condition for running the sleep test): D minus F is at least +5 percentage points on the 48 non-repeat repositories, and D is better than F on more repositories than it is worse. If this fails, sleep promotion is not tested and the report says so.
3. **Sleep test, if run:** "sleep promotion" moves the bank's effect into the weights. The bank arm (D) is run on the 120 training repositories; episodes whose first patch passes that repository's own tests are kept; the adapter is then trained further to give the same answers with no insert in the prompt. "Rehearsal" trains the same adapter further for the same number of updates and tokens on the plain teacher traces. Both are evaluated on development repositories with no insert, against F (the same adapter before either) and D. (Corrected at 20:10, before any trained arm was evaluated: the first wording made sleep and rehearsal the same thing.)
4. **No development repository, hidden test or label is read by training, retrieval or the bank.** Only `v07/grade.py` and `v07/report.py` read `data/v07/dev/hidden/`.
5. **All seeds and all arms are kept and reported**, including arms that lose.

## What I expect (so it can be held against me)

- The unchanged student fixes few of these (15 of 120 training repositories on the first patch).
- B will do well on repeats and badly on lookalikes and changed preconditions, where the trained fix regresses.
- If the diagnostic helps, it shows on G2 and G3 as fewer regressions for D than for B.
- G4 should show little or no gain for any trained arm.
