# Ordinary Python repository repair: the harness as built

Fable, 23 November 2026, for Prince Anozie and Codex. Branch `repair-v0.1`, worktree `stillway-pilot-repair`. Asked for in point 6 of Codex's Q5 brief. Kept apart from Q5: its own branch, its own code under `repair/`, its own results under `results/repair/`. Nothing here touches a Q5 file.

Status of everything in this document: **development**. The tasks are mine, I hold their hidden half, and the settings were adjusted while looking at them. No claim here is a blind result.

## 1. What a task is

| Part | Content | Who sees it |
|---|---|---|
| Repository | a published pure-Python library, fetched from PyPI and pinned by SHA-256 (`repair/vendor/MANIFEST.json`), with one bug put in | the solver |
| Bug report | two to four plain sentences in a user's words: what they called, what came back, what they expected | the solver |
| Visible tests | the library's own tests, with the ones the bug breaks cut out, so that everything the solver can run passes at the start | the solver, through a tool |
| Hidden tests | the library's own complete tests: those the bug breaks must pass again, and no other may break | the grader only |
| Reference fix | the library as published | the grader and the respondent only |

A task file line carries the repository name, the archive digest, the report, where the package is importable from, the test command's targets, and an overlay: the files that differ from the archive (the bugged source file and the trimmed test files). The hidden line carries the two test lists and the reference text of the overlaid files.

`python repair/build_tasks.py OUTDIR [BUGS.py]` builds both files from a list of bugs and refuses a bug unless: it breaks at least one of the library's tests and at most 60; each stated example gives a different value with the bug than without; the visible tests pass with the bug in place and again on the reference. The build is repeatable to the byte.

## 2. Tools and limits, identical for every model

| Tool | What it does |
|---|---|
| `list` | files under a directory, with their length |
| `read` | up to 200 numbered lines of one file |
| `search` | lines matching a pattern, at most 40 |
| `edit` | replace one exact span of a file with new text, or create a file: a freely written patch |
| `run` | execute a short piece of Python in the repository and return what it prints |
| `test` | run the visible tests, or one file or test; returns the counts and the first failure |
| `done` / `ask` | end the job with a fix, or with one question |

Limits per job: 30 tool calls, of which at most 8 may be `run` or `test`; 12,000 output tokens, thinking included; 10 minutes. Every tool result states what is left. Code runs in the v0.8 sandbox: no network, no writes outside the workspace, a CPU limit, a file-size limit, a wall-clock limit.

Model settings, the same for all: Ollama's own tool calling, thinking on, temperature 0, seed 7, no repetition penalties, a 32,768-token context with the oldest tool results dropped first when it fills. One harness rule against idling: a `list`, `read` or `search` call identical to the one before it gets a one-line reminder, not the same output again.

**Two changes from the proposal.** A `run` tool was added after the first trial: the small model kept trying to execute the report's example and had no way to. And the test limit became a shared limit on `run` and `test`.

## 3. Endings and grades

As in v0.8. `python repair/grade.py PUBLIC HIDDEN RECORDS OUT` rebuilds each task's snapshot with the library's complete tests, lays the solver's changed source files over it (tests and test configuration are never taken from a solver), and runs everything in the sandbox.

| Grade | Meaning |
|---|---|
| verified | the solver said DONE; every test the bug broke passes; nothing else broke |
| wrong DONE | the solver said DONE and that is not so |
| asked | the solver ended with a question |
| out of limits | a limit ran out first |

The grader also records whether the files as left would have passed whatever the ending, and whether an ending without DONE left files changed. On the 20 development tasks it grades the reference fix verified 20 times out of 20 and the untouched bug wrong 20 times out of 20.

## 4. The guard for freely written patches

This is Q5's procedure carried over. In Q5 the candidates were one-line changes that passed two visible checks. Here there are two candidates: the repository as it was, and the solver's patch. The visible tests pass for both, so they decide nothing; the bug report is the specification, and it is prose.

| Step | When | What the runner does | Cost |
|---|---|---|---|
| Reproduce | at the start | has the model write the report's examples as runnable calls with the value the user expects; runs each on an untouched copy of the snapshot; keeps those that show the complaint; tells the solver what it found | one short model call, one sandbox run |
| Visible tests | at `done` | must pass | one test run |
| Documented examples | at `done` | examples in the docstrings of the changed files that held before the change must still hold (a public specification: no question needed) | two sandbox runs |
| Report examples | at `done` | every reproduced example must give the value the user expects | one sandbox run |
| Disposable probe | at `done` | has the model propose up to six other calls of the changed code; runs each on the untouched copy and on the patched workspace | one short model call, two sandbox runs |
| One focused question | when a probe differs and the report does not say which side is right | this call, the value before, the value after: which is intended? The answer may be neither. Two questions a job at most | the user's time |

- **Refusal.** A failed check comes back to the solver as the result of its `done` call, with the evidence: the failing example, or the user's value for the probed call. The job goes on within the same limits; a refused `done` counts as a tool call and the guard's model calls count against the job's own token limit.
- **Two confirmations.** If the user confirms the patch on two probed calls, remaining differences are taken as explained. If differences remain and no question is left, the job ends with a question.
- **Fallback.** Any ending other than an accepted DONE puts the workspace back as it was found. The patch is kept aside in the record so that the grader can say whether a right patch was forgone.
- **Respondent.** In development the questions are answered at once from the reference by `repair/respond.py`, which evaluates the probed call on the library as published. A sealed, two-round exchange like Q5's is not built.

Fixtures, all passing, no model involved: `python repair/guard_selftest.py` (reference fix accepted with one confirmed question; an over-broad fix refused on a documented example with no question; a fix that works on lists and fails on iterators refused after one question, with the user's value as evidence; a change with no effect refused; a change that breaks a visible test refused; differences left with no question to spare reported as unresolved; the untouched copy unchanged). `python repair/loop_selftest.py` drives the plain loop and the guarded loop with the same scripted stand-in for a model and requires their records to agree call for call.

## 5. Files

| File | Purpose |
|---|---|
| `repair/fetch.py`, `repair/vendor/MANIFEST.json` | fetch and unpack the pinned archives |
| `repair/core.py` | workspaces, the sandbox, test runs, expression and documented-example runs |
| `repair/dev_bugs.py`, `repair/build_tasks.py` | the 20 development bugs and the task builder |
| `repair/agent.py` | the plain tool loop |
| `repair/guard.py`, `repair/agent_guard.py`, `repair/respond.py` | the guard, the guarded loop, the development respondent |
| `repair/grade.py`, `repair/report.py` | the grader and the tables |
| `repair/guard_selftest.py`, `repair/loop_selftest.py` | fixtures |

Replay from a clean checkout: `python3.12 -m venv .venv-repair && .venv-repair/bin/pip install pytest==9.2.0`, `python repair/fetch.py`, `python repair/build_tasks.py data/repair/dev`, then the commands in section 6.

Downloads made for this, on Prince's standing approval: pytest 9.2.0 with four dependencies into `.venv-repair` (26 MB installed), and five source archives from PyPI, 452 KB together: inflection 0.5.1, cachetools 7.2.8, toolz 1.2.0, boltons 26.2.0, tabulate 0.10.0. Each is at least three weeks old and checked against the digest PyPI publishes. Neither the archives nor the unpacked trees are committed.
