# v0.7 final run: raw outputs returned for blind grading

For Codex, via Prince Anozie. From Fable, 22 November 2026. **Nothing here has been graded and I have not looked at any outcome.** The hidden half never left you.

## What is returned

| Item | Where | Check |
|---|---|---|
| 42 raw record files, 96 records each, 4,032 in all | `results/v07/codex_final_records/*.jsonl` | `RECORDS.sha256` (written by your `check_records.py`), its own SHA-256 `a5c151b8fa158050fcfdcdf525394d27355b7755b5ef3bdc25bec09911a98b2b` |
| Completeness check | your `check_records.py` printed: `4032 records; hash and commit before returning.` | 96 job ids, 42 files, every file holds exactly the 96 ids |
| Lock check, before and after the run | `results/v07/codex_final_LOCK_CHECK.txt` | `lock of 2026-11-22T04:47:09+0000 \| git 859a8a7dbc \| ALL MATCH` (base weights and all nine adapters included) |
| Execution-failure log | `results/v07/codex_final_FAILURES.md` and `.json` (SHA-256 `af07283ed640e1a780b9a7f7113acdad19c491bd53e6c1afe3fd9fb5c821b513`) | from student-side fields only |
| Run log | `logs/v07_final_run.log` (SHA-256 `de2999d23402397e696ace2dc391db1ab4bb0a52092d35e3848d9e2406787274`) | start 06:17:51Z, `RUN_FINAL EXIT 0 at 2026-11-22T11:04:18Z`, no tracebacks, no restart |

- **Commit the run executed from:** `3db7a18ca9e245bfcad7bb6ec930b292be018e4f` on branch `v0.7`, clean tree (only the new outputs were untracked).
- **Runner:** your `run_final.zsh`, unmodified, into the fresh directory `results/v07/codex_final_records`. All 100 entries of `INPUTS.sha256` matched.
- **Settings:** unchanged, adapter strength included. 16 arms; 3 files for the unchanged student and 13 per seed for seeds 1 to 3.
- No record carries a grade, a hidden test or an outcome field.

## Execution failures (recorded without grading)

| | Count |
|---|---|
| Test scripts proposed | 8,064 |
| Test scripts not well formed (not run) | 49 |
| Test executions stopped at the 5-second limit | 19 |
| Test scripts that raised an error (the error text was the observation) | 774 |
| Patches not well formed | 26 |
| Patches well formed that could not be applied | 35 |
| Records missing a test or a patch | 0 |
| Crashes or tracebacks in the run log | 0 |

The per-file table is in `codex_final_FAILURES.md`. The 19 time-limit stops are on a few jobs whose tests loop (for example job008, job033, job072, job084) and occur in runs spread over the whole five hours.

## Deviations

1. **Archive location.** I first unpacked the handoff inside the checkout. I deleted that copy before anything ran and unpacked it again outside the checkout, as your README says. Nothing from the first copy was used.
2. **Order.** v0.6 round two was run first and alone, then this run. Hashing and pushing the v0.6 results (seconds of light CPU) overlapped the first minutes of the first arm file, `base_s0__plain`.
3. **Machine not idle for the last 9 of 42 files.** From 10:07Z, at Prince's instruction to begin v0.8 engineering at once, short CPU jobs ran beside this run: single-process tests, one 70-second two-process data build and one four-minute two-thread training pilot. No GPU work. Files affected: `experience_x_s3__example`, `__wrong`, `__bank_v1` and the six reduced-strength files of seed 3. Their timing fields (`generation_seconds`, `tool_seconds`) may be slightly high. Decoding is greedy, so outputs do not depend on timing, except that a test is cut at 5 seconds: these nine files hold 2 of the 19 time-limit stops (both in `patches@0.5_s3__plain`, one of them on job072, which also hits the limit in an earlier, undisturbed file), so I see no sign that the overlap caused a stop.
4. **No interruption and no resume.**

## Disclosure carried over unchanged

The bank-family adapter (`experience_x`, used by arms D, D1, E, F, W, HF, HD, HQ, HT) saw about 383,000 training tokens against about 475,000 for the final-patch and experience adapters: **19% fewer**, at the same 300 updates and 2,048-token budget. Any comparison of that adapter with the other two carries this mismatch.

## What happens next

You grade with `v07/grade.py`. When the graded files come back I run `v07/report.py` once: repository and family intervals, the primary rule (D against A on unfamiliar repositories) and regression rule P2 first, then HQ, HF and the secondary rules separately. No tuning, no Harness², no adaptive dose and no further training are part of this protocol. Anything suggested by the grades goes into a later development round with fresh final cases.
