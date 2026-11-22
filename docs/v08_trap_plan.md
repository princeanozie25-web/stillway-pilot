# v0.8: plan for the trap set, fixed before it exists

Fable, 22 November 2026. Written before Codex has authored the set (`docs/v08_trap_brief.md`). It is item Q3 of `docs/followup_queue.md`.

**The question.** On independently written jobs whose visible checks do not pin the repair down, is the plain bank wrong often enough to need the guard, and does the guard cost more than it saves?

## 1. Why the design changed from the one in the memo

The memo asked for 40 trap jobs and 40 ordinary ones. While building the packer for them I found two things.

- **With that design only one number was open.** The bank has an entry for all eight settings. The guarded bank tries every change of every entry and asks when more than one passes both checks. So it asks on every trap and on no ordinary job, by construction.
- **Some jobs have several repairs that are all right** (for whole numbers, "greater than 3" and "at least 4" are the same filter). The guard asks on those too, unnecessarily. Both holdouts excluded them.

So the set now has three classes (ordinary, equal, trap) and its main part is an **unselected draw**: Codex keeps every one-fault job in which a visible check fails and does not look at its class. That makes the mix of classes, and the cost of asking, something measured, not something I chose.

## 2. What runs

| Arm | Checkpoint and bank |
|---|---|
| `exec` | execution-aware core, seed 1, alone |
| `bank` | the same core with bank version 1 going first (`results/v08/m4/bank_v1.json`, promoted from my day 1) |
| `bankguard` | the same with the guarded bank |
| `search` | the search script with no model |

- Checkpoint, bank and code are those of the revision-2 lock (`python v08/check_lock3.py`: ALL MATCH when this was written). Nothing is retrained, re-promoted or re-ordered.
- When the public file arrives: check its digest and format, write a lock (the files of the revision-2 lock, `v08/pack_traps.py`, `v08/trap_report.py`, this plan, the public file), then run each arm once, one job at a time, on an idle machine.
- Records are sealed with hashes, lock check and failure log and returned before any grade. `v08/grade.py` is unchanged.

## 3. The reading, in this order

"Itself ends" means the bank's compiled procedure ran and the run ended in that same script. Jobs the bank declines go to the core and are counted in the whole-arm figures only.

| Step | Measured on | Condition | Verdict |
|---|---|---|---|
| A | every trap job | the plain bank itself ends 10% or fewer with a wrong DONE | **GUARD UNNECESSARY**: recommend the plain bank |
| B | every trap job; every ordinary job | the guarded bank itself ends more than 10% of traps with a wrong DONE, or ends more than 50% of ordinary jobs by asking | **GUARDED BANK FALLS** |
| C | the `draw` part, whole arm, guarded against plain | wrong DONEs prevented is zero or less, or verified jobs forgone divided by wrong DONEs prevented is above 3 | **GUARD TOO COSTLY**: reuse needs the evidence test of Q1 |
| else | | | **GUARDED BANK STANDS** |

- A and B are the two conditions written in `docs/v08_memo.md` before any of this work, with "not wrong" set at 10% and "most" at 50%.
- **C was written after my own dry run** (section 5) and before Codex's set exists. Its threshold of 3 is my default for how much worse a wrong DONE is than a lost completion. The report prints the break-even figure itself, so Prince can apply another rate without a rerun.
- B is a check that the guard does what its code says. I expect 0% and 0%.
- Intervals are 95% Wilson intervals over jobs. The verdict uses the point values; the intervals are printed beside them.

## 4. Also reported, not ruled on

- The share of each class in Codex's draw, and how many draws were discarded because no visible check failed.
- For every arm and class: verified, wrong DONE, asked, out of limits, operations and seconds per job.
- The search script and the core alone on traps, as references. Neither ever asks on a trap by design; how often each is wrong there is a limit on the claim "the search script is the cheap way".
- Unnecessary requests: equal jobs the guarded bank itself ended by asking.

## 5. The dry run on my own draw (exploratory, author-made)

To prove the pipeline before Codex spends time on it, I drew 400 unselected one-fault jobs from my own generator (`v08/trap_dry_draw.py`), packed, ran, graded and reported them (`results/v08/trap_dry_tables.md`). It is not the independent test.

| | Ordinary | Equal | Trap |
|---|---|---|---|
| Jobs of 400 | 240 | 17 | 143 |
| Plain bank: verified / wrong / asked | 203 / 31 / 4 | 5 / 12 / 0 | 63 / 76 / 3 |
| of which the bank itself ended: right / wrong / asked | 194 / 0 / 0 | 4 / 0 / 0 | 54 / 41 / 0 |
| Guarded bank: verified / wrong / asked | 226 / 11 / 1 | 1 / 8 / 8 | 1 / 15 / 127 |
| Search script: verified / wrong | 240 / 0 | 17 / 0 | 80 / 63 |
| Core alone: verified / wrong / asked | 93 / 114 / 26 | 3 / 14 / 0 | 34 / 99 / 9 |

By the reading above: A 28.7%, B 0% and 0%, C 85 wrong DONEs prevented for 43 verified jobs forgone (break-even 0.51), verdict GUARDED BANK STANDS. 327 further draws were discarded because the fault showed in no visible check.

## 6. Predictions, written now

- Traps are between a quarter and a half of Codex's draw.
- The plain bank itself ends between 20% and 45% of traps with a wrong DONE.
- Verdict GUARDED BANK STANDS, with a break-even below 1.
- The search script is wrong on a third to a half of the traps.

## 7. What will not be done

No change to the bank, its gate, the guard or the core after the set is seen. No rerun of an arm. No tuning on the set. Anything suggested by its grades goes to a later protocol with fresh jobs.

## 8. Limits

- One core seed and one bank, the ones measured before.
- The guard can only ask or commit. It cannot look for evidence that separates two repairs; that is Q1.
- The world is the same one-line-fault world as before. "Equal" means equal on 3,000 random inputs inside its limits.

## 9. The set arrived (added 22 November, before it was run)

- **What arrived.** `Stillway_v08_trap_public.zip` (SHA-256 `6180853b…9262d7a7`): `public.jsonl`, SHA-256 `c89a389026e6250670aa53298ecdb8032bab6fb5efd29ea1d9464e4574350814`, equal to the digest in Codex's handoff note; Codex's commitment to the hidden half `0553c86cdaa1eb714bd19f35be65b48bfe0338e895a0be481bb055d5b00ef665`. I do not hold the hidden half.
- **Format check from the public half alone.** 137 project jobs, 137 unique ids, each id equal to the hash of its files, every job inside the limits, six modules per project, no content shared with any earlier set of mine or Codex's (0 of 2,754).
- **Codex's note on composition** (`data/v08/codex_trap/HANDOFF.txt`): 120 consecutive visibly failing draws kept out of 251 attempts, 131 discarded because no visible check failed; the draw holds 71 ordinary, 3 equal and 46 trap jobs; 17 equal jobs were added as top-ups; no trap top-up was needed. The public lines are shuffled, and nothing in the public half says which job is which.
- **Codex saw the aggregate dry-run table of section 5** (it is in this plan). It reports that the bank file, the per-job dry-run files and E14 were not consulted.
- **Codex asks for one audit at closeout:** on a trap the grader's `abstained` does not itself show that the workspace was left unchanged, so asked jobs with `detail.unchanged` false are to be listed apart. I will report them; the reading of section 3 is not changed by it.
- **Lock.** `results/v08/LOCK_v08_codex_trap.json`: every file of the revision-2 lock, unchanged, plus the packer, the report script, this plan, the brief and Codex's public file. `python v08/check_lock_trap.py` reported ALL MATCH before the run.
- **The run:** the four arms of section 2, once each, records to `results/v08/codex_trap/run/`, returned before any grade.
