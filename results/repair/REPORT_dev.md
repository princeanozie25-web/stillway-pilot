Jobs in every arm: 20.

| Arm | Verified | Wrong DONE | Asked | Out of limits | Patch right whatever the ending | Right file touched |
|---|---|---|---|---|---|---|
| small plain | 2 | 2 | 0 | 16 | 4 | 16 |
| small guard | 6 | 0 | 0 | 14 | 6 | 6 |
| larger Qwen plain | 14 | 1 | 0 | 5 | 16 | 19 |
| larger Qwen guard | 13 | 0 | 0 | 7 | 16 | 13 |
| Gemma plain | 8 | 0 | 0 | 12 | 8 | 9 |

| Arm | Tool calls | Run or test calls | Output tokens | Prompt tokens | Seconds | Endings that left files changed without DONE |
|---|---|---|---|---|---|---|
| small plain | 21.2 | 5.0 | 7492 | 178578 | 109 | 12 |
| small guard | 17.6 | 3.4 | 8081 | 149112 | 119 | 0 |
| larger Qwen plain | 13.2 | 4.8 | 5160 | 119133 | 167 | 4 |
| larger Qwen guard | 11.0 | 2.7 | 5319 | 80014 | 162 | 0 |
| Gemma plain | 15.2 | 4.0 | 8896 | 102268 | 281 | 1 |

Paired with small plain (exact two-sided sign test; bootstrap interval for the difference in verified share, 10,000 resamples, seed 805):

| Arm | Verified here only | Verified there only | p | Difference, 95% interval | Wrong DONE here only | Wrong DONE there only |
|---|---|---|---|---|---|---|
| small guard | 5 | 1 | 0.219 | +20 points (+0 to +40) | 0 | 2 |
| larger Qwen plain | 12 | 0 | 0.000 | +60 points (+40 to +80) | 0 | 1 |
| larger Qwen guard | 11 | 0 | 0.001 | +55 points (+35 to +75) | 0 | 2 |
| Gemma plain | 8 | 2 | 0.109 | +30 points (+0 to +60) | 0 | 2 |

Guard, small guard: questions 7 on 4 jobs (user's value agreed with the patch 7, with the old behaviour 0, with neither 0); jobs with a reproduced example 12; done refused 8 times; probe executions per job 6.2; guard tokens per job 277; patches put back 11, of which right 0.

Guard, larger Qwen guard: questions 16 on 9 jobs (user's value agreed with the patch 16, with the old behaviour 0, with neither 0); jobs with a reproduced example 13; done refused 6 times; probe executions per job 7.2; guard tokens per job 310; patches put back 7, of which right 3.

| Job | small plain | small guard | larger Qwen plain | larger Qwen guard | Gemma plain |
|---|---|---|---|---|---|
| boltons-1 | budget | budget | verified | verified | verified |
| boltons-2 | budget | verified | verified | verified | budget |
| boltons-3 | budget | budget | budget | budget | budget |
| boltons-4 | budget (patch right) | verified | verified | verified | budget |
| cachetools-1 | budget | budget | budget | budget | budget |
| cachetools-2 | budget | budget | budget | budget | budget |
| cachetools-3 | budget (patch right) | budget | budget (patch right) | budget (patch right) | verified |
| cachetools-4 | budget | verified | verified | budget (patch right) | budget |
| inflection-1 | budget | budget | verified | verified | verified |
| inflection-2 | budget | budget | verified | verified | verified |
| inflection-3 | budget | budget | verified | verified | budget |
| inflection-4 | wrong | budget | verified | verified | verified |
| tabulate-1 | budget | budget | verified | verified | budget |
| tabulate-2 | budget | budget | verified | verified | verified |
| tabulate-3 | budget | budget | verified | budget (patch right) | budget |
| tabulate-4 | budget | verified | budget (patch right) | verified | verified |
| toolz-1 | verified | budget | verified | verified | budget |
| toolz-2 | verified | verified | verified | verified | budget |
| toolz-3 | budget | verified | verified | verified | verified |
| toolz-4 | wrong | budget | wrong | budget | budget |
