# Ordinary Python repository repair: harness proposal (draft, nothing built)

Fable, 23 November 2026, for Prince Anozie and Codex. Asked for in point 6 of Codex's Q5 brief. Kept apart from Q5: separate code, separate results, separate report. This is a proposal to react to; nothing here is frozen.

## 1. The question it serves

Every Stillway result so far lives in a generated world of one-line faults. The harness tests the original promise directly: on ordinary Python repositories, with plain-language bug reports and freely written patches, does a small model with Stillway's additions get closer to a larger model under the same tool budget?

## 2. What a task is

| Part | Content | Who sees it |
|---|---|---|
| Repository snapshot | a real, small, pure-Python library at a fixed commit, with one bug | the solver |
| Bug report | two to five plain sentences in a user's words; no file names or line numbers unless a user would know them | the solver |
| Visible tests | the repository's own tests that pass at the snapshot | the solver, through a tool |
| Hidden tests | tests that fail at the snapshot and pass after the reference fix, plus the tests that must not break | the grader only |
| Reference fix | kept by the task author; never shown | nobody during a run |

- **Repository-disjoint:** development tasks and final tasks come from different repositories, so nothing learnt about one codebase carries over.
- **Endings and grades** stay as in v0.8: verified, wrong DONE, clean ASK, out of limits. A wrong DONE is a patch that the solver declared finished and the hidden tests reject.

## 3. Tools and budget, identical for every model

| Tool | What it does |
|---|---|
| `list` | files under a path |
| `read` | a line range of one file |
| `search` | lines matching a pattern |
| `edit` | replace an exact span of a file with new text (a freely written patch) |
| `test` | run the visible tests, or one of them; returns pass, fail and the first failure |
| `done` / `ask` | end the job |

Proposed limits per job: 30 tool calls, 8 test runs, 12,000 output tokens, 10 minutes of wall time. Everything runs in the same sandbox as v0.8 (no network, no writes outside the workspace). Every call, token and second is recorded.

## 4. Models, all already on this machine

| Role | Model | Size on disk |
|---|---|---|
| Small | `qwen3.5:2b` (Ollama) | 2.7 GB |
| Larger, same family | `qwen3.5:9b-mlx` (Ollama) | 8.9 GB |
| Larger, other family | `gemma4:12b-mlx` (Ollama) | 7.7 GB |
| Earlier small runner, for continuity | Qwen2.5-Coder-1.5B | 2.9 GB |

No model download is needed and nothing is paid for. The one-million-parameter core cannot take part: it has no free text.

## 5. Arms

1. Small model, plain tool loop.
2. Larger model, plain tool loop, same budget.
3. Small model with the guard carried over from Q5: before `done`, count the distinct patches it tried that pass the visible tests; if more than one behaves differently on a probe input, ask one focused question instead of guessing.

Arm 3 is the Stillway claim. Arms 1 and 2 are needed first to know whether there is a gap to close.

## 6. Who writes what

- **Fable:** the harness, the grader, the sandbox, and about 20 development tasks from 4 or 5 repositories.
- **Codex:** the final tasks, from repositories I have not used, with hidden tests and reference fixes held back. The same blind handoff as before: freeze, public half, sealed outputs, grades.

## 7. Decisions I need before building

| Decision | My recommendation | Why it is yours |
|---|---|---|
| Downloading repositories | Yes: 4 or 5 small permissively licensed pure-Python libraries for development (each under about 5 MB), fetched from PyPI or GitHub, pinned by hash, plus `pytest` | Nothing on this machine is a suitable repository; your rule is downloads only when necessary |
| Where bugs come from | Real historical fixes where the repository's history has small ones; otherwise bugs written by the task author | Real fixes are more convincing and take longer to collect |
| Models | The three Ollama models above | They are yours and local; a hosted model would cost money |
| Size of the first run | 20 development tasks, then 40 to 60 final tasks from Codex | Sets how long Codex's part takes |

## 8. What it will not show

A handful of small libraries is not "real repositories" in general. Local models of 2 to 12 billion parameters are not the frontier. The first run can show whether a gap exists and whether the guard narrows it on this sample, not how far that carries.
