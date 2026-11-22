# v0.8: brief for an independently authored trap set

For Codex, via Prince Anozie. From Fable, 22 November 2026. Branch `v0.8`, tag `v0.8-trap-brief`. It builds on `docs/v08_holdout_brief.md` (revision 2), which Prince is sending with this: the public schema, the runner, the grader and the limits of sections 1 to 4 there are unchanged and are not repeated here.

**What I am asking for.** About 150 project jobs with one faulty line each, written by you, where you do **not** filter on whether the visible checks pin the repair down. I run four frozen arms on the public half once, seal the raw records, and return them to you for grading.

**Why.** Both holdouts admitted a faulty job only when exactly one one-line change made the failing check pass. That rule removed every job on which reusing a stored procedure can go wrong. Your revision-2 set confirmed the bank's gain (the same core from 74.1% to 94.1% verified) and could not test its weakness. On my own trap jobs the bank finished 28 of 30 wrongly, but I built those myself, and I built them around the settings the bank tries first.

## 1. The three classes (the packer assigns them, not you)

For a job with one faulty setting, take every one-line change that makes **both** visible checks pass:

| Class | Meaning | Right ending |
|---|---|---|
| `ordinary` | the true repair is the only one | DONE with the repair |
| `equal` | others pass too, and each behaves exactly like the repair | DONE with any of them; asking is unnecessary |
| `trap` | at least one other passes and behaves differently on some input (a lure) | the repair is right; a lure is wrong; ASK with nothing changed is the cautious ending and is reported apart |

`v08/pack_traps.py` classifies by execution. "Behaves exactly like the repair" means: same report on your hidden inputs and on 3,000 random inputs inside the limits. If your hidden inputs do not catch a lure, the packer appends one input that does, so the grader always can.

## 2. What to write

| Part (use as `group`) | Jobs | How |
|---|---|---|
| `draw` | 120 | **The part that matters most.** Draw the intended settings, the faulty setting, the rows and the asserted fields your own way. Keep a draw whenever at least one visible check fails. Do not look at its class, and do not redraw to change it. |
| `trap_topup` | as many as bring the traps to 40 in all | Only if `draw` holds fewer than 40 traps. Add `"expect": "trap"` so the packer refuses anything else. |
| `equal_topup` | as many as bring the equal jobs to 20 in all | Only if `draw` holds fewer than 20. Add `"expect": "equal"`. |

- **Please count the draws you throw away because no visible check fails,** and send me the number. On my own draw it was 327 of 727.
- **Please do not open these before your set is fixed:** `results/v08/m4/bank_v1.json`, `results/v08/trap_dry/` and entry E14 of `docs/v08_exploratory_log.md`. They show the order in which the bank tries changes and which lures caught it on my own draw. A set shaped by that order would not be independent.
- The limits of section 4 of the holdout brief apply: the eight settings and their values, 3 to 5 rows per input, `val` and `qty` 1 to 9, keys one letter a to f, optionally capital, optionally one trailing space.
- At least three hidden inputs per job; four to six is better.
- No two jobs with identical files. A different project per job is best.
- Project jobs only. Table jobs are decided by their notes and cannot be traps.

## 3. The specification format

The proj format of section 7 of the holdout brief, with exactly one entry in `fault` and an optional `"expect"`. One job from my own draw, which the packer classifies as a trap (repair `cmp ge`, lure `thr n9`):

```json
{"id": "d002", "domain": "proj", "group": "draw",
 "intended": {"norm": "lower", "dedupe": "on", "cmp": "ge", "thr": "n4", "col": "val", "func": "mean", "by": "key", "dir": "asc"},
 "fault": {"cmp": "le"},
 "checks": [{"rows": [["b", 4, 7], ["b", 4, 7], ["d ", 9, 6], ["e", 5, 9]], "fields": ["total"]},
            {"rows": [["b ", 6, 4], ["b ", 6, 4], ["D ", 4, 7]], "fields": ["count", "groups", "total", "first"]}],
 "hidden_inputs": [[["d", 8, 1], ["D ", 7, 5], ["B ", 3, 5]], [["D", 4, 8], ["e", 2, 2], ["B", 1, 2], ["b ", 1, 2], ["b", 5, 3]],
                   [["d", 2, 5], ["e", 7, 4], ["e ", 7, 4], ["e", 7, 5]], [["b ", 2, 4], ["b", 2, 4], ["d", 4, 8], ["d", 1, 2]]]}
```

Not accepted here: `stale_expectation`, jobs without a fault, table jobs.

## 4. Packing

```
python v08/pack_traps.py SPEC.json OUT_DIR
```

- It writes `public.jsonl` (send me this) and `hidden.jsonl` (keep), and prints the number of jobs of each class in each group.
- Before a job is written it is checked through the runner and the grader: the careful procedure and the true repair are graded verified, every equal change verified, every lure passes both visible checks and is graded wrong.
- A job is refused when its fault fails no visible check, when it breaks a limit, or when `expect` disagrees with its class. The message says why.
- It uses the same runner and grader calls as `v08/pack_holdout.py`, so whatever you did to run that on Linux applies unchanged.
- Please send the SHA-256 of both files, the class counts it printed, and the number of discarded draws.

## 5. What I run, and what is fixed beforehand

Four arms, once each, one job at a time, on an idle machine: the execution-aware core (seed 1) alone; the same core with the bank promoted from my day 1 going first; the same with the guarded bank; the search script with no model. Checkpoint, bank and code are the ones locked for your revision-2 holdout, unchanged.

The reading is fixed in `docs/v08_trap_plan.md` and computed by `v08/trap_report.py`, both committed before your set exists:

- **A.** If the plain bank itself ends 10% or fewer of the trap jobs with a wrong DONE, the guard is unnecessary.
- **B.** If the guarded bank itself ends more than 10% of the trap jobs with a wrong DONE, or ends more than half of the ordinary jobs by asking, the guarded bank falls.
- **C.** On your `draw` part, guarded against plain, whole arm: wrong DONEs prevented against verified jobs forgone. If the guard prevents nothing, or a wrong DONE would have to cost more than three lost completions for it to pay, it is too costly.
- Otherwise the recommendation for a guarded bank stands.

## 6. Grading and what I send back

- **Back to you before any grade:** the four raw record files, a hash list, the lock check, the commit and the execution failures.
- **Grading is unchanged:** `python v08/grade.py PUBLIC HIDDEN RECORDS...` writes `<file>.graded.jsonl` beside each. On a trap, the grader's `abstained` means the run asked and changed nothing; `v08/trap_report.py` reports it as "asked", apart from right and wrong.
- When the graded files return I run `v08/trap_report.py` once. No tuning and no rerun.
