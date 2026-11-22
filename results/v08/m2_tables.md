# v0.8 milestone 2: one frozen model, single operations against composed scripts

Model: Qwen2.5-Coder-1.5B-Instruct at the v0.7 pin, unchanged, greedy, on this laptop's GPU. 48 development jobs (24 proj, 24 tab). Limits for both modes: 14 model calls, 60 operations, 90 s per job, 220 new tokens per call. Operations inside scripts are counted one by one.
Verified jobs per minute = verified jobs / total wall time including failed jobs.

## proj

| Measure | One operation per call | Composed scripts |
|---|---|---|
| Jobs | 24 | 24 |
| Verified jobs | 4 | 4 |
| Eventual success % | 16.7 | 16.7 |
| First-attempt success % | 16.7 | 12.5 |
| Said DONE, wrong | 0 | 12 |
| Asked on an answerable job | 5 | 0 |
| Ran out of limits | 15 | 8 |
| Verified jobs per minute | 1.08 | 0.90 |
| Model calls per job | 9.92 | 7.29 |
| Operations per job (inside scripts too) | 9.54 | 22.75 |
| Prompt tokens per job | 12847 | 10876 |
| Generated tokens per job | 58 | 189 |
| Total model tokens, all jobs | 309730 | 265568 |
| Extra editing attempts per job | 0.00 | 3.79 |
| Replies that were not a legal call | 0 | 0 |
| Scripts that crashed | 0 | 0 |
| Illegal or failed operations | 5 | 23 |
| Failed checks seen | 146 | 243 |
| Model seconds per job | 8.40 | 10.52 |
| Execution seconds per job | 0.863 | 0.562 |
| End-to-end seconds per job, mean | 9.27 | 11.08 |
| median | 13.08 | 5.22 |
| 90th percentile | 13.49 | 23.62 |
| maximum | 14.0 | 27.6 |

## tab

| Measure | One operation per call | Composed scripts |
|---|---|---|
| Jobs | 24 | 24 |
| Verified jobs | 3 | 7 |
| Eventual success % | 12.5 | 29.2 |
| First-attempt success % | 12.5 | 29.2 |
| Said DONE, wrong | 1 | 1 |
| Asked on an answerable job | 18 | 8 |
| Ran out of limits | 2 | 8 |
| Verified jobs per minute | 1.98 | 1.83 |
| Model calls per job | 4.75 | 6.50 |
| Operations per job (inside scripts too) | 3.83 | 19.25 |
| Prompt tokens per job | 5588 | 8949 |
| Generated tokens per job | 22 | 181 |
| Total model tokens, all jobs | 134651 | 219116 |
| Extra editing attempts per job | 0.29 | 4.00 |
| Replies that were not a legal call | 0 | 0 |
| Scripts that crashed | 0 | 0 |
| Illegal or failed operations | 10 | 119 |
| Failed checks seen | 14 | 159 |
| Model seconds per job | 3.57 | 9.25 |
| Execution seconds per job | 0.215 | 0.307 |
| End-to-end seconds per job, mean | 3.79 | 9.56 |
| median | 3.08 | 3.93 |
| 90th percentile | 6.68 | 21.62 |
| maximum | 12.3 | 22.0 |

## all

| Measure | One operation per call | Composed scripts |
|---|---|---|
| Jobs | 48 | 48 |
| Verified jobs | 7 | 11 |
| Eventual success % | 14.6 | 22.9 |
| First-attempt success % | 14.6 | 20.8 |
| Said DONE, wrong | 1 | 13 |
| Asked on an answerable job | 23 | 8 |
| Ran out of limits | 17 | 16 |
| Verified jobs per minute | 1.34 | 1.33 |
| Model calls per job | 7.33 | 6.90 |
| Operations per job (inside scripts too) | 6.69 | 21.00 |
| Prompt tokens per job | 9218 | 9913 |
| Generated tokens per job | 40 | 185 |
| Total model tokens, all jobs | 444381 | 484684 |
| Extra editing attempts per job | 0.15 | 3.90 |
| Replies that were not a legal call | 0 | 0 |
| Scripts that crashed | 0 | 0 |
| Illegal or failed operations | 15 | 142 |
| Failed checks seen | 160 | 402 |
| Model seconds per job | 5.99 | 9.89 |
| Execution seconds per job | 0.539 | 0.434 |
| End-to-end seconds per job, mean | 6.53 | 10.32 |
| median | 3.08 | 4.87 |
| 90th percentile | 13.44 | 22.50 |
| maximum | 14.0 | 27.6 |

## Scripts against single operations, same jobs (intervals: 4,000 resamples of the 48 jobs)

- Verified jobs per minute: ratio 0.99 (95% interval 0.48 to 2.52).
- Eventual success: +8.3 points (-2.1 to +20.8).
- Jobs verified by both: 5; only with single operations: 2; only with scripts: 6.
