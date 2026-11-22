# v0.8: an operating contract for the runner

Fable, for Prince Anozie and Codex, 22 November 2026. Development jobs only. Codex's independent holdout was not used for any of this, and the wording chosen here has not been run on it.

**What was asked.** Prince: draft the system's internal prompts, with Codex and me each giving our best. Codex: draft a compact operating contract of my own, test both drafts and a minimal instruction on development jobs, score verified completions, unnecessary edits, appropriate ASKs and time per solved job, and freeze the chosen wording before any final inference. An arm whose prompt is already frozen keeps it; the draft belongs in a later comparison.

**Where a prompt can act at all.** v0.8 has two kinds of runner.

| Runner | Reads instructions? | Where a contract lives |
|---|---|---|
| The one-million-parameter core | No. It reads a fixed vocabulary of 206 tokens: goals, operations, observations. | In its training records: what the teacher does in each situation. |
| The instruction-following runner (Qwen2.5-Coder-1.5B-Instruct, pinned, script mode) | Yes | In its system text. This is where the drafts were tested. |

## 1. The three wordings

**Minimal.**

> Finish the job using the operations below.

**Codex's draft** (transcribed from Prince's screenshot; the last word was cut off in the image and is my completion).

> Complete the user's task within the stated limits. Use the available evidence to choose your next action. Before editing, identify what you expect to change and what must stay true. When reusing a previous solution, check the assumption that makes it applicable here. Group operations into a script when you can choose them in advance. Pause when an observation could change your next action. If essential evidence is missing, leave the workspace as you found it and return ASK. After a change, check its effects. Return DONE when the available evidence supports completion. Report what you observed and distinguish it from what you predicted.

**My draft.**

> Look before you change anything: run the checks, or the differences and their notes. If nothing is wrong, answer DONE and change nothing. Decide each change from what you observed, one change at a time, and only in a module the job uses. After a change, run the checks again; if the check you were fixing still fails, undo the change before trying anything else. Never send again a call that returned BAD or did not help. Put calls whose arguments you already know into one script, and end the script where the next call depends on a result. Answer DONE only after the checks pass. If a note is missing or no single change fits what you observed, undo your changes and answer ASK.

- **Mine is not independent of Codex's.** I had read Codex's draft in the screenshot before writing. The two agree on most clauses.
- **What mine adds** comes from what the same model did wrong in milestone 2: it repeated calls that had already failed, kept a failed change and stacked another on top, and said DONE on 13 of 48 jobs that were not right. So mine names the operations ("run the checks", "undo") and forbids the repeats.
- **What mine leaves out:** Codex's clause on reusing a previous solution (this runner has no memory to reuse from) and the closing report of observed against predicted.

Each wording is followed by the same reference text (the operations, what they mean, the table rules, what DONE and ASK are) and the same two worked examples. A fourth arm, **frozen**, is the milestone-2 prompt exactly as it was, whose manual has guidance mixed into the reference.

## 2. The comparison

The pinned Qwen model in script mode, the limits of milestone 2 (14 model calls, 60 operations, 90 s per job), 72 development jobs (36 project, 36 table; 22 of them need no change, of which 11 are unanswerable), one greedy run per arm. Raw records were committed before grading. The selection rule was committed before any arm ran (`v08/prompt_compare.py`, commit `bfe9271`).

| 72 development jobs | Frozen (milestone-2 prompt) | Minimal | Codex's contract | My contract |
|---|---|---|---|---|
| **Verified completions** | **16** | 11 | 15 | 12 |
| of which project / table | 5 / 11 | 3 / 8 | 5 / 10 | 5 / 7 |
| Said DONE and was wrong | 19 | 31 | 21 | 23 |
| Unnecessary edits: changed a job that needed none (of 22) | 10 | 13 | 10 | 12 |
| Appropriate ASKs (of 11 unanswerable) | 4 | 0 | 0 | 1 |
| ASK on an answerable job | 13 | 0 | 0 | 8 |
| Ran out of limits | 24 | 30 | 36 | 29 |
| **Seconds per solved job** | **49.6** | 85.4 | 65.9 | 76.1 |
| Model tokens per job | 10,076 | 11,140 | 13,439 | 12,103 |
| Reverts issued | 14 | 0 | 1 | 133 |
| Illegal or failed operations | 176 | 299 | 352 | 279 |

**Chosen by the rule: the frozen wording.** The rule takes the arms within 2 verified jobs of the best (frozen 16, Codex's 15), then the fewer jobs ended wrongly (25 each), then the less time per solved job (49.6 s against 65.9 s).

What the table supports, and what it does not:

- **Neither new contract beat the prompt already in use, and mine did worse than Codex's** (12 against 15 verified). Mine made the model undo compulsively: 133 reverts against 1, and 12 crashed scripts against none.
- **The differences between the three guided arms are within noise.** Frozen and Codex's each verified jobs the other did not (6 and 5). With 72 jobs and one run, 16, 15 and 12 cannot be told apart.
- **A bare instruction is worse on one thing clearly:** it said DONE and was wrong 31 times, against 19 to 23.
- **Only the frozen prompt produced correct ASKs** (4 of 11), and it also asked 13 times when it should not have. Its manual says in the job's own words where ASK applies ("a note nonote means the evidence is missing: answer ASK and change nothing"). Codex's general clause ("if essential evidence is missing ... return ASK") produced no ASK at all, right or wrong.
- **Nobody wrote the closing report** Codex's contract asks for: every job in every arm ended with a bare DONE or ASK, as the two worked examples do.
- For a model of this size, the worked examples and guidance worded in the job's own terms appear to carry more than a paragraph of principles. That is a reading of one small comparison, not a result.

**Frozen for later use:** the three wordings above, exactly as written, and the frozen prompt of milestone 2 as the incumbent. Nothing changes for any arm already run. The next comparison should use fresh jobs, more than one run per arm, and a runner able to follow prose; if Codex's or my wording is to be tried on a larger model, the texts are in `v08/prompt_compare.py`.

## 3. What the contract means for the small core

The core cannot read a contract; it can only have been shown one. Clause by clause, against what v0.8's training records already contain:

| Clause (Codex's wording) | In the core's training records today? | Evidence from v0.8 |
|---|---|---|
| Use the available evidence to choose your next action | Yes: the teacher's next script depends only on what it has observed | The evidence fix of the exploratory log (E1) was made so that this is true |
| Before editing, identify what you expect to change and what must stay true | Partly: the execution-aware arm is trained to predict the observations that follow an edit, including the second check that must keep passing | It predicts a pass after nearly every edit of its own (203 of 210 right when the check passed, 3 of 286 when it failed): it states an expectation but cannot doubt it |
| When reusing a previous solution, check the assumption that makes it applicable | No. Reuse is in the bank, outside the core, and the plain bank does not check | Wrong on 28 of 30 trap jobs; the guarded bank asks instead (exploratory) |
| Group operations into a script when you can choose them in advance; pause when an observation could change your next action | Yes: this is exactly where the teacher ends a script | 5.7 scripts and 10.4 operations per job on my holdout |
| If essential evidence is missing, leave the workspace as you found it and return ASK | Yes: unanswerable jobs, about one training job in nine | 68% of unanswerable project jobs and 100% of unanswerable table jobs on my holdout |
| After a change, check its effects | Yes: every editing script ends with both checks | |
| Return DONE when the available evidence supports completion | Yes | Error among its answers was still 14% on my holdout |
| Report what you observed and distinguish it from what you predicted | Outside the core: the experience record and the demo show predicted and observed side by side | `python v08/demo.py --smoke` |

**Codex's suggestion for the core: paired examples.** Two nearly identical jobs that differ in one fact, where the fact decides the action (a note that says which side is newer; a precondition that makes yesterday's fix apply or not). v0.8 already has pairs of this kind for evaluation (altered preconditions, traps) but generates training jobs independently. Building the training set as such pairs, with the reuse clause included, is a change to pretraining and belongs in the next protocol with fresh final jobs. I have not done it here.
