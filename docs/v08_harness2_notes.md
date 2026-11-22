# v0.8: what was taken from google-research/harness2, and what was not

Fable, 22 November 2026.

**Revision inspected:** `google-research/harness2` at commit `6868817518876de8fd170c6a8354daca273b6191` (2 November 2026, the head of `main`), read from a shallow clone kept outside this repository. **Licence:** Apache-2.0 (`LICENSE` at that commit; third-party benchmarks keep their own licences). Paper: Xu et al., "Harness²: Recursive Agent Harnessing for an Open World", arXiv 2610.14224.

**No code from it is in this repository, and none of it was executed.** What v0.8 runs is my own implementation and is called a **local script runner** throughout.

## What Harness² is

It optimises the harness around a fixed model (system prompt, guardrails, memory, tool guidance, sub-agents, skills, scripts, plug-ins), in two loops with weights frozen:

| Loop | What it does | Where in the code |
|---|---|---|
| Task level: Propose, Probe, Compose | proposes edits to the harness, executes candidates on the same task, composes a refined harness from the contrast between executions, with no ground truth | `harness2/core/recursion.py`, `proposer.py`, `selection.py` |
| Harnessing level | keeps the adopted harness and an evidence-backed lesson per task in a per-domain library that guides later refinement | `harness2/core/library.py`, `selection.py` (`reflect_adoption`) |
| Budget accounting | 4k rollouts and 3k improvement stages per task for recursion budget k, retries counted apart | `harness2/core/ledger.py` |

## Why the upstream design is not used as it stands

| Upstream assumption | Here |
|---|---|
| The executor is a full coding agent (OpenCode or Codex) driving a hosted model (GLM-5, Gemini 3.5 Flash) | A one-million-parameter core and a 1.5-billion-parameter local model; no paid infrastructure |
| Linux, Node.js, Docker for one benchmark; executor network access unrestricted and the Codex sandbox disabled | macOS, offline, every script in `sandbox-exec` with no network |
| What is edited is prose and files that an agent reads (prompts, skills) | The small core reads a fixed token vocabulary; it cannot read a rewritten prompt |
| Each task costs 4k agent rollouts | The question here is cost per verified job, measured in milliseconds and operations |

So the upstream pipeline cannot run here without replacing its executor, its models and its sandboxing, at which point nothing of it would be left to measure.

## The three mechanisms implemented locally, each with its baseline and cost

| Mechanism (idea from) | Local implementation | Baseline it is compared with | Local cost measured |
|---|---|---|---|
| **Scripts as a harness component**: an agent composes tool calls in a script instead of issuing them one at a time (Harness² lists scripts among its eight components; the composition idea is CodeAct, arXiv 2402.01030) | `stillway8/opsrt.py`: the same operations callable one per reply or from a Python script, every operation counted inside scripts | one operation per model call, same model, jobs, limits (`v08/m2_harness.py`) | model calls, tokens, operations, sandbox launches, seconds per job |
| **A ledger that counts executions separately from model sessions** (`core/ledger.py`) | every record carries scripts, operations, failed checks, tokens, model seconds, execution seconds | none: it is accounting | negligible |
| **A per-domain library of adopted procedures with the evidence behind each** (`core/library.py`: retrieval by construction, one directory per domain, the whole adopted item kept with why it was picked) | `stillway8/experience.py` and the v0.8 bank: an entry is a procedure plus the experience that verified it; retrieval is by domain and first observation | the frozen core with no bank; the core after a weight update with no bank | bank bytes, operations spent inside invoked procedures, wasted operations on wrong invocations |

**Not implemented:** Propose, Probe, Compose itself (contrasting several candidate harnesses on one task). Its nearest local analogue would be running two candidate scripts in two disposable workspaces and keeping the one whose visible checks pass. That doubles executions per job and is left for a later protocol so that it cannot be confused with the effects measured here.
