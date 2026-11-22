# v0.8: operating contracts for the instruction-following runner, development jobs only

Qwen2.5-Coder-1.5B-Instruct (pinned), script mode, 72 development jobs, one run per arm, greedy. Same reference text, examples, jobs and limits; only the behavioural text differs (the `frozen` arm is the milestone-2 prompt as it was).

| | frozen | minimal | codex | fable |
|---|---|---|---|---|
| Verified completions (of 72) | 16 | 11 | 15 | 12 |
| of which project jobs (36) | 5 | 3 | 5 | 5 |
| of which table jobs (36) | 11 | 8 | 10 | 7 |
| Said DONE and was wrong | 19 | 31 | 21 | 23 |
| Unnecessary edits: changed a job that needed none (of 22) | 10 | 13 | 10 | 12 |
| Jobs ended wrongly (either of the two above) | 25 | 37 | 25 | 29 |
| Editing operations per job | 3.4 | 2.6 | 4.4 | 4.3 |
| Reverts | 14 | 0 | 1 | 133 |
| Appropriate ASKs (of 11 unanswerable) | 4 | 0 | 0 | 1 |
| ASK on an answerable job | 13 | 0 | 0 | 8 |
| Ran out of limits | 24 | 30 | 36 | 29 |
| Seconds per solved job | 49.6 | 85.4 | 65.9 | 76.1 |
| Seconds per job | 11.0 | 13.0 | 13.7 | 12.7 |
| Model calls per job | 6.8 | 7.8 | 8.5 | 7.6 |
| Operations per job | 20.6 | 24.5 | 28.2 | 24.3 |
| Model tokens per job | 10076.2 | 11140.1 | 13438.7 | 12102.6 |
| Illegal or failed operations | 176 | 299 | 352 | 279 |
| Scripts that crashed | 0 | 0 | 0 | 12 |
| Words in the system text | 476 | 466 | 563 | 584 |

Selection rule (fixed beforehand): most verified jobs; arms within 2 of the best (frozen, codex) are separated by fewer jobs ended wrongly, then by less time per solved job. **Chosen: frozen.**

Jobs verified by one arm and not another: frozen not minimal: 7; frozen not codex: 6; frozen not fable: 6; minimal not frozen: 2; minimal not codex: 0; minimal not fable: 2; codex not frozen: 5; codex not minimal: 4; codex not fable: 5; fable not frozen: 2; fable not minimal: 3; fable not codex: 2.
