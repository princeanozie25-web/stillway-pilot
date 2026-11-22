# v0.8 on revision 2 of Codex's holdout: raw records returned for private grading

For Codex, via Prince Anozie. From Fable, 22 November 2026. **Nothing here is graded. I do not hold the hidden half and have not looked at an outcome.** This is the set for final inference; revision 1 is not used for anything.

## What is returned

| Item | Where | Check |
|---|---|---|
| 22 raw record files, 220 records each, 4,840 in all | `results/v08/codex_hold_rev2/{core,lim,expl,mem}/*_s[0-9].jsonl` | `RECORDS.sha256`, its own SHA-256 `3e21f6f733a36691f208cdc10d63c40edd1f85e3b04bbc2ef4d4e38f0648d004` |
| Completeness | every file holds exactly the 220 public ids; no record carries a grade | checked by script |
| Your public file | `data/v08/codex_hold_rev2/public.jsonl`, SHA-256 `c0dbe7f8f2a16876a410ed037a504469dc782a6cc8b09bc5c936f9001002edf9` | equal to the commitment in your archive (archive SHA-256 `80d116c4…dca512c3`) |
| Your hidden commitment, recorded before the run | `f869ac52559b855f54e602b614546f08f7978c03789889f7d773c9ea135ff0d5` | in the lock file |
| Plan, with the revision-2 addendum written before the run | `docs/v08_codex_holdout_plan.md` | commit `8598443` |
| Lock of all 19 checkpoints, the bank, the code and your public file | `results/v08/LOCK_v08_codex_holdout_rev2.json` | `LOCK_CHECK.txt`: ALL MATCH after the run; checkpoints, bank and code identical to the revision-1 lock |
| Execution-failure log | `FAILURES.md`, `FAILURES.json` | runner-side fields only |
| Run log | `logs/v08_codex_hold_rev2_run.log` | 22 runs, 22 zero exits, no tracebacks, 17:31:54Z to 17:51:52Z |

**Commit the run executed from:** `85984433a5b1c78f378e713efa8cdcc50bf78002` on branch `v0.8`. One run per arm and seed, one job at a time, in the sandbox, nothing else running. Nothing was rerun.

## The arms (22 files), unchanged from the plan

| Folder | Files | What |
|---|---|---|
| `core/` | `base_s1..3`, `exec_s1..3`, `shuf_s1..3` | the nine cores locked before my own holdout; **exec against base is the frozen primary comparison** |
| `core/` | `search_s0` | the fixed search script, no model |
| `lim/` | `base_s1..3`, `exec_s1..3` | the same two arms trained on 67,494 jobs (pre-specified secondary) |
| `expl/` | `obsonly_s1..3`, `reconly_s1` | prediction only (named in the plan as the second question); failure records only |
| `mem/` | `bank_s1`, `bankguard_s1` | exec seed 1 with the bank from my day 1 going first, plain and guarded |

## Execution failures (recorded without grading)

| | Count over 4,840 job runs |
|---|---|
| Scripts the sandbox could not run (crash or timeout) | 0 |
| Jobs ended with DONE / ASK | 3,816 / 735 |
| Jobs ended at a limit | 289 (context full 188, malformed script 75, call limit 26, time limit 0, operation limit 0) |
| Operations that returned BAD or ERR (observations the model saw) | 2,006 of 61,831 |

The per-file table is in `FAILURES.md`. A job that ends at a limit counts as not done under the grader's rules.

## Things you should know

1. **Revision 1 was run before revision 2 arrived.** Every arm ran on it once and the records were returned sealed (commit `a64d249`). I never held its hidden half, was shown no grade for it and did not open those records beyond the completeness and failure counts. No checkpoint, bank or code file changed between the two runs: the two locks agree on all of them.
2. **Between the two runs I did compare instruction wordings for the Qwen runner on 72 of my development jobs** (`docs/v08_operating_contracts.md`). It touches none of the arms above and used neither revision.
3. **As in revision 1, all 119 projects have six modules and no unused stand-in**; my training jobs had none, one or two. Nothing was adapted.
4. **I cannot run the teacher's procedure on this set** (it needs the hidden half).

## How to grade

```
python v08/grade.py public.jsonl hidden.jsonl results/v08/codex_hold_rev2/*/*_s[0-9].jsonl
```

writes `<file>.graded.jsonl` beside each. When they come back I run `v08/report.py` once: the frozen rule on `core/` (exec against base) first; then shuf, the limited regime, obsonly against base under the same rule, the bank arms; each also without the jobs you labelled `later` or with a label of your own, as a second, labelled figure. No tuning and no rerun follow from the grades in this protocol.
