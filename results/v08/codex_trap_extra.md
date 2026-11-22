# v0.8 trap set: further breakdowns (descriptive, written after the grades)

## 1. Audit asked for by Codex: ASK endings and changed files

| Arm | ASK endings | graded abstained | `detail.unchanged` false | non-empty diff |
|---|---|---|---|---|
| bank | 7 | 7 | 0 | 0 |
| bankguard | 58 | 58 | 0 | 0 |
| exec | 16 | 16 | 0 | 0 |
| search | 0 | 0 | 0 | 0 |

## 2. Who ended the job (draw and top-ups together)

| Arm | Class | Jobs | Bank's own script: verified / wrong / asked | Core after the bank declined: verified / wrong / asked / limit |
|---|---|---|---|---|
| bank | ordinary | 71 | 60 / 0 / 0 of 60 | 1 / 9 / 1 / 0 of 11 |
| bank | equal | 20 | 10 / 0 / 0 of 10 | 0 / 9 / 1 / 0 of 10 |
| bank | trap | 46 | 13 / 16 / 0 of 29 | 3 / 9 / 5 / 0 of 17 |
| bankguard | ordinary | 71 | 68 / 0 / 0 of 68 | 0 / 3 / 0 / 0 of 3 |
| bankguard | equal | 20 | 0 / 0 / 16 of 16 | 0 / 3 / 1 / 0 of 4 |
| bankguard | trap | 46 | 0 / 0 / 41 of 41 | 2 / 3 / 0 / 0 of 5 |

## 3. By fault slot, the unselected draw

| Slot | Jobs | Traps | Plain bank wrong DONE | Guarded bank wrong DONE | Guarded bank asked | Search script wrong | Core alone wrong |
|---|---|---|---|---|---|---|---|
| by | 6 | 4 | 0 | 0 | 4 | 0 | 6 |
| cmp | 17 | 9 | 8 | 3 | 9 | 4 | 10 |
| col | 6 | 0 | 0 | 0 | 0 | 0 | 4 |
| dedupe | 14 | 1 | 2 | 0 | 1 | 0 | 5 |
| dir | 19 | 4 | 3 | 0 | 4 | 3 | 3 |
| func | 15 | 6 | 4 | 0 | 6 | 4 | 2 |
| norm | 12 | 4 | 2 | 0 | 4 | 2 | 8 |
| thr | 31 | 18 | 16 | 3 | 16 | 10 | 23 |

## 4. Rates on the unselected draw (120 jobs)

| Arm | Verified | Wrong DONE | Asked | Wrong among DONE endings | Seconds per job | Verified per minute | Operations per job | Operations per verified job |
|---|---|---|---|---|---|---|---|---|
| exec | 43 | 61 | 15 | 59% of 104 | 0.445 | 48 | 16.0 | 44.7 |
| bank | 79 | 35 | 6 | 31% of 114 | 0.194 | 203 | 22.4 | 34.0 |
| bankguard | 70 | 6 | 44 | 8% of 76 | 0.136 | 257 | 81.8 | 140.2 |
| search | 97 | 23 | 0 | 19% of 120 | 0.086 | 564 | 43.5 | 53.9 |
