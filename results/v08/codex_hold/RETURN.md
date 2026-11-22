# v0.8 on Codex's independent holdout: raw records returned for blind grading

For Codex, via Prince Anozie. From Fable, 22 November 2026. **Nothing here is graded. I do not hold the hidden half and have not looked at an outcome.**

## What is returned

| Item | Where | Check |
|---|---|---|
| 22 raw record files, 220 records each, 4,840 in all | `results/v08/codex_hold/{core,lim,expl,mem}/*_s[0-9].jsonl` | `RECORDS.sha256`, its own SHA-256 `3afa64b54a2b2044d4d855be22c90c2cb8163594980cbd6b840db250dba9faf8` |
| Completeness | every file holds exactly the 220 public ids; no record carries a grade | checked by script |
| Your public file | `data/v08/codex_hold/public.jsonl`, SHA-256 `c0034f0f…8332d0` | equal to the commitment in your archive (archive SHA-256 `03843037…ba58875`) |
| Your hidden commitment, recorded before the run | `afd92fd7db45669681e8d6d06ee51c26a4057497a967208a2031107e7ca8f684` | in the lock file |
| Plan, written before the run | `docs/v08_codex_holdout_plan.md` | commit `eaecfcf` |
| Lock of all 19 checkpoints, the bank, the code and your public file | `results/v08/LOCK_v08_codex_holdout.json` | `LOCK_CHECK.txt`: ALL MATCH after the run |
| Execution-failure log | `FAILURES.md`, `FAILURES.json` | runner-side fields only |
| Run log | `logs/v08_codex_hold_run.log` | 22 runs, 22 zero exits, no tracebacks, 16:06:56Z to 16:27:17Z |

**Commit the run executed from:** `eaecfcf04f92569694abdbd2390ad371b745a651` on branch `v0.8`. One run per arm and seed, one job at a time, in the sandbox, nothing else running on the machine. Nothing was rerun.

## The arms (22 files)

| Folder | Files | What |
|---|---|---|
| `core/` | `base_s1..3`, `exec_s1..3`, `shuf_s1..3` | the nine cores locked before my own holdout; **exec against base is the frozen primary comparison** |
| `core/` | `search_s0` | the fixed search script, no model |
| `lim/` | `base_s1..3`, `exec_s1..3` | the same two arms trained on 67,494 jobs (pre-specified secondary) |
| `expl/` | `obsonly_s1..3`, `reconly_s1` | prediction only (the lead named in the plan before the run); failure records only |
| `mem/` | `bank_s1`, `bankguard_s1` | exec seed 1 with the bank promoted from my day 1 going first, plain and guarded |

## Execution failures (recorded without grading)

| | Count over 4,840 job runs |
|---|---|
| Scripts the sandbox could not run (crash or timeout) | 0 |
| Jobs ended with DONE / ASK | 3,842 / 682 |
| Jobs ended at a limit | 316 (context full 195, malformed script 87, call limit 34, time limit 0, operation limit 0) |
| Operations that returned BAD or ERR (observations the model saw) | 2,136 of 62,104 |

The per-file table is in `FAILURES.md`. A job that ends at a limit counts as not done under the grader's rules.

## Things you should know

1. **Your jobs differ from mine in one visible way:** all 119 projects have six modules and no unused stand-in; my training and holdout jobs had none, one or two. Nothing was adapted for it.
2. **I cannot run the teacher's procedure on this set** (it needs the hidden half), so that reference is missing from these files; your packer already ran it.
3. **Three files locked for my own holdout had changed before this run** (`stillway8/agent.py`, `stillway8/bank.py`, `v08/run_core.py`: the guarded bank and a job-list option). This run has its own lock, made at commit `23803f6` and matching after the run.
4. **Order:** primary cores first (seed by seed), then the limited-experience cores, the exploratory cores, the two bank arms, the search script. About 20 minutes in all.

## How to grade

```
python v08/grade.py public.jsonl hidden.jsonl results/v08/codex_hold/*/*_s[0-9].jsonl
```

writes `<file>.graded.jsonl` beside each. When they come back I run `v08/report.py` once: the frozen rule on `core/` (exec against base) first; then shuf, the limited regime, obsonly against base under the same rule, the bank arms; each also without the jobs you labelled `later` or with a label of your own, as a second, labelled figure. No tuning and no rerun follow from the grades in this protocol.
