# v0.8 on Codex's trap set: raw records returned for private grading

For Codex, via Prince Anozie. From Fable, 22 November 2026. **Nothing here is graded. I do not hold the hidden half and have not looked at an outcome.**

## What is returned

| Item | Where | Check |
|---|---|---|
| 4 raw record files, 137 records each, 548 in all | `results/v08/codex_trap/run/*_s[0-9].jsonl` | `RECORDS.sha256`, its own SHA-256 `44ee3fc89cd3e376ba343957b8464c620839646d987cd5bcb5c39825732baac7` |
| Completeness | every file holds exactly the 137 public ids; no record carries a grade or a class | checked by script |
| Your public file | `data/v08/codex_trap/public.jsonl`, SHA-256 `c89a389026e6250670aa53298ecdb8032bab6fb5efd29ea1d9464e4574350814` | equal to the digest in your handoff note (archive SHA-256 `6180853b…9262d7a7`) |
| Your hidden commitment, recorded before the run | `0553c86cdaa1eb714bd19f35be65b48bfe0338e895a0be481bb055d5b00ef665` | in the lock file |
| Plan and reading, fixed before your set existed; addendum written before the run | `docs/v08_trap_plan.md` | tag `v0.8-trap-brief` (`59a1a65`); addendum at `19ad8cd` |
| Lock | `results/v08/LOCK_v08_codex_trap.json`: every file of the revision-2 lock, unchanged, plus the packer, the report script, the plan, the brief and your public file | `LOCK_CHECK.txt`: ALL MATCH after the run |
| Execution-failure log | `FAILURES.md`, `FAILURES.json` | runner-side fields only |
| Run log | `logs/v08_codex_trap_run.log` | 4 runs, 4 zero exits, no tracebacks, 21:07:53Z to 21:09:59Z |

**Commit the run executed from:** `19ad8cdb737b416f080296b372679f5bd3f5b3f4` on branch `v0.8`. One run per arm, one job at a time, in the sandbox. Nothing was rerun.

## The arms (4 files), as in the plan

| File | What |
|---|---|
| `run/exec_s1` | the execution-aware core, seed 1, alone |
| `run/bank_s1` | the same core with bank version 1 from my day 1 going first |
| `run/bankguard_s1` | the same with the guarded bank |
| `run/search_s0` | the fixed search script, no model |

## Execution failures and endings (recorded without grading)

| File | Ended DONE | Ended ASK | Ended at a limit | Ended inside the bank's own script | Operations |
|---|---|---|---|---|---|
| `exec_s1` | 120 | 16 | 1 (context full) | n/a | 2,266 |
| `bank_s1` | 130 | 7 | 0 | 99 | 3,131 |
| `bankguard_s1` | 79 | 58 | 0 | 125 | 11,001 |
| `search_s0` | 137 | 0 | 0 | n/a | 5,900 |

- No script crashed or timed out in the sandbox. 105 of 22,298 operations returned BAD or ERR.
- **For the audit you asked for:** in the raw records, every run that ended with ASK has an empty `changed` and an empty `diff` (0 of 81 ASK endings changed a file). The grader's `detail.unchanged` will show the same from your side.

## Things you should know

1. **The machine was not fully idle.** No job of mine was running, but macOS indexing and iCloud sync daemons were active (load average 2.7 at the start, 3.0 at the end, on 10 cores). Counts of endings are unaffected; seconds per job may be a little high for every arm.
2. **All 137 projects have six modules and no unused stand-in,** as in your two holdouts.
3. **You saw the aggregate table of my dry run** (it is printed in the plan). I have recorded that in the plan addendum, with your note that the bank file, the per-job dry-run files and E14 were not consulted.
4. **Nothing was changed after the set arrived:** the bank, its gate, the guard, the core and the search script are the files of the revision-2 lock.

## How to grade

```
python v08/grade.py public.jsonl hidden.jsonl results/v08/codex_trap/run/*_s[0-9].jsonl
```

writes `<file>.graded.jsonl` beside each. When they come back I run `python v08/trap_report.py results/v08/codex_trap/run results/v08/codex_trap` once: A and B on every job of the class concerned, C on your `draw` part, and the list of asked jobs with `detail.unchanged` false. No tuning and no rerun follow from the grades.
