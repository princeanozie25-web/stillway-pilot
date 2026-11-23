# Q5 plan: a guard that asks one focused question

Fable, 23 November 2026, for Prince Anozie and Codex. Written and frozen before Codex's public set was opened. Branch `v0.8`, freeze tag `v0.8-q5-freeze`. Codex's execution brief, as received: `docs/v08_q5_codex_brief.md`.

## 1. The question

On Codex's trap set the existing guard was safe and handed back 44 of 120 unselected jobs as a bare request. Does one focused question, put through the real runner and answered blind by Codex, finish more of those jobs without adding wrong answers?

A win here is an upper bound for this interaction: the respondent answers accurately and at once. Whether people can answer such questions easily is a separate test.

## 2. What was built

| Part | File | What it does |
|---|---|---|
| Disposable probe | `stillway8/opsrt_q.py`, operation `TRIAL` | Copies the project's modules into a scratch directory, applies one candidate change there, runs it on a made-up legal input, deletes the copy. The workspace is not touched. |
| Sound equivalence rule | `stillway8/bank_q.py`, `canon` | Gives two settings the same form only if they produce the same report on every legal input (values 1 to 9). Candidates with the same form are committed without a question. |
| The question | `stillway8/bank_q.py`, `decide` | When two kinds of candidate differ on some field for a made-up input: these rows, this field, the two values. One question at a time, two per job at most. |
| Pause and resume | `v08/run_q.py` | A paused job's record carries its whole state: surviving changes with the value each gives, probe input, both runner outputs, field, job id, workspace hash. A resume checks that the answer belongs to the pending question. |
| Fixtures | `v08/q_selftest.py` | Nine development fixtures (section 6). |
| Report | `v08/q_report.py` | Tables, the rule of section 4, targets, costs. |
| One-command replay | `v08/q_all.sh` | Reference arms, round 1, both resumes, from a public file and the two answer files. |

No file locked for v0.8 is changed; the new code is in new files, and the sandbox is pointed at `opsrt_q.py` by the run script.

**How the guard decides, in order.**

1. Try every one-line change against both visible checks, undoing each (this is the existing guard, unchanged). One passes: commit. None: hand on.
2. More than one passes: group them by the equivalence rule. One kind: commit, ask nothing.
3. Otherwise probe: make up legal inputs and run one change of each kind on each. Stop at the first input that separates every kind, or after 15 inputs once any difference is known, or at 60 inputs.
4. No difference in 60 inputs: record the search limit, bare request. Kinds the rule does not prove equal are never committed on probes alone.
5. A difference: one question, pause, nothing changed.
6. On the answer: drop every surviving change whose own value on that field differs from the owner's value. The value may differ from both named predictions; then both are dropped. Go to 2. No change agrees with the owner, or two questions are spent: bare request.

**Public specification.** A job's public specification is its two visible checks. Every surviving change already passes both, so nothing in it can resolve a question; each question records that as its source.

## 3. Frozen settings

| Setting | Value |
|---|---|
| Core | execution-aware core, seed 1 (`artifacts/v08/core_exec_s1.safetensors`), as locked for the trap set |
| Bank and gate | `results/v08/m4/bank_v1.json`, as locked for the trap set |
| Question budget | 2 per job |
| Probe budget | 60 made-up inputs per question; stop early as in step 3 |
| Random seeds | the string `<job id>:<round>` seeds the made-up inputs; nothing else is random |
| Made-up inputs | 3 to 5 rows, keys a to f with capitals and trailing spaces, values 1 to 9, thresholds in play and repeated records favoured |
| Arms | `bankguard` (existing guard), `bank` (plain bank), `bankq` (questioning guard), `search` (fixed search script) |
| Extra arm, outside the rule | `searchq`: the search script given the same rule, no model, no bank |
| Lock | `results/v08/LOCK_v08_q5.json`, checked by `python v08/check_lock_q5.py` |

## 4. The decision, fixed now

**Primary rule (Codex's proposal, adopted as written).** On the same 120 jobs, the questioning guard must deliver more verified repairs than the existing guard, with no increase in wrong DONE. The comparison is against the existing guard even if another reference does better.

- **Paired uncertainty:** jobs verified by one arm only and by the other only, with an exact two-sided sign test, and a paired bootstrap interval (10,000 resamples, seed 805) for the difference in share. The same for wrong DONE.
- **Small differences:** if the rule is met and the sign test on verified repairs gives p of 0.05 or more, the result is reported as met and inconclusive for generalisation.

**Targets, reported beside the rule and not part of it.**

| Target | Value |
|---|---|
| Questions per trap job | at most 2 on any trap job; mean over all trap jobs (zeros included) and the share needing a second question are reported |
| Questions on ordinary and equal jobs | zero |
| Edits left behind by an ending that asks | zero |

**Also reported:** every trap job not verified, with who ended it and why; traps resolved; wrong DONE against the plain bank; each ending attributed to the procedure or the fallback core; user questions; probe executions; changes tried against the visible checks and how many failed; operations; machine time; time awaiting answers, separately; the cost of generating questions (up to the pause) apart from the cost after an answer.

**What "time awaiting answers" is here.** The time from sealing a question to the resume command. In this exchange that is the relay through Prince and Codex's script. It says nothing about how long a person would take.

## 5. The exchange

| Step | Who | What |
|---|---|---|
| 1 | Fable | Push the freeze. Open the public set, check its digest, add it to the lock. Run the four arms and the extra arm once. |
| 2 | Fable | Seal round 1: `questions_r1.jsonl` (fields `id`, `round`, `rows`, `field`, `predictions`) and `SEAL_r1.json` (digests of the question file and of every stage file). Send both. |
| 3 | Codex | Return one line per question: `id`, `round`, `field`, `value`. |
| 4 | Fable | Resume once. Seal and send `questions_r2.jsonl` and `SEAL_r2.json`. |
| 5 | Codex | Return the round-2 answers. |
| 6 | Fable | Resume once. Send outputs and costs for every arm, ungraded. |
| 7 | Codex | Grade with `v08/grade.py`; `python v08/q_report.py GRADED_DIR OUT_PREFIX` gives the tables. |

- One question file serves both questioning arms. They put the same question whenever both ask; the extra arm also asks on jobs the bank declines.
- An answer is used only if its `id`, `round` and `field` match the pending question and its value is a legal scalar. Identical lines delivered twice count once. Missing, malformed or conflicting answers end the job with a bare request and an untouched workspace.

## 6. Development evidence (author-made jobs, exploratory)

**Fixtures** (`python v08/q_selftest.py results/v08/q_dry/set/public.jsonl results/v08/q_dry/set/hidden.jsonl`): all nine pass.

| # | Fixture | Result |
|---|---|---|
| 1 | The equivalence rule is sound | 11,520 settings fall into 4,529 forms; 6,991 settings that share a form with another were compared on 300 inputs; none disagrees |
| 2 | The probe is disposable | 20 probes; workspace unchanged; no scratch copy left |
| 3 | Crash in round 1 | killed mid-run with a torn last line; the same command again gives the records of an uninterrupted run |
| 4 | Duplicate delivery; resuming twice | counted once; the second resume does nothing |
| 5 | Missing answer | bare request, workspace untouched |
| 6 | Invalid answers (wrong field, wrong type, extra key, two conflicting lines, a boolean) | bare request, workspace untouched |
| 7 | An answer that differs from both predictions and fits no surviving change | bare request, workspace untouched |
| 8 | Question budget exhausted | bare request, workspace untouched |
| 9 | Failure on resuming | workspace handed back as found |

**Dry run** on 400 fresh unselected jobs from my own generator (seed 8244; 244 ordinary, 137 trap, 19 equal), with a stand-in respondent (`v08/q_dev_answer.py`); `results/v08/q_dry_tables.md`.

| Arm | Verified | Wrong DONE | Bare request | User questions | Operations per job |
|---|---|---|---|---|---|
| Existing guard | 233 | 26 | 141 | 0 | 77 |
| Plain bank | 273 | 112 | 13 | 0 | 21 |
| **Questioning guard** | **365** | **26** | **9** | 123 | 84 |
| Fixed search script | 329 | 71 | 0 | 0 | 46 |
| Search script with the questioning rule | 399 | 0 | 1 | 149 | 93 |

The plain bank also ran out of limits on 2 jobs.

- The questioning procedure itself ended 356 jobs: 355 right, none wrong, 1 bare request (an equal job the rule could not prove and 60 probes could not separate).
- All 26 wrong answers and 8 of the 9 bare requests are jobs the bank's gate declined and the core finished; they are the same 34 jobs in the existing guard's arm.
- 123 questions on 115 trap jobs; 8 needed a second; none on ordinary or equal jobs; 4.1 probe executions per job.
- By the rule of section 4: met (132 jobs verified only by the questioning guard, none only by the existing guard; wrong DONE 26 against 26).

## 7. Predictions for Codex's 120 jobs

- The primary rule is met, with 25 to 40 points more verified repairs and the same number of wrong DONE.
- Mean questions per trap job between 0.8 and 1.0; at most 10% of traps need a second question; no question on an ordinary or equal job; no edit left behind.
- Every miss but at most two comes from the fallback core on a job the bank declined.
- Outside the rule: the search script with the questioning rule verifies at least as many jobs as the questioning guard and is wrong on none.

## 8. Disclosures

- **The archive arrived before the freeze.** Prince sent `Stillway_Q5_public_after_freeze.zip` with the brief. I recorded its SHA-256 (`a8aac8390b18467e375e3fec6a4a3580eddbbbedc97515e1687181b21629d953`, received 2026-11-23T10:06:24Z) and did not open it. The freeze is pushed before it is extracted.
- **A first design existed before the brief reached me** (all questions in one round, a choice among whole reports, equivalence by 100 probes). It was run in part on the same 400 development jobs and then discarded for Codex's design. The development jobs have therefore been seen by both designs; they are development evidence only.
- **The extra arm is my addition.** The existing guard and the questioning guard are both an exhaustive try of one-line changes; `searchq` shows what the rule does with no model and no bank. It is outside the rule and adds a few questions on jobs the bank declines.
- **The core alone is not run**; the brief names four arms.
- **The equivalence rule is sound, not complete.** Equal candidates it cannot prove equal end in a bare request.
- **One core seed, one bank**, the same one-line-fault world as before.

## 9. What will not be done

No change to any locked file after the set is opened. No rerun of an arm. Each round resumed once. Anything suggested by the grades goes to a later protocol with fresh jobs. The 137 jobs of the trap set are spent.
