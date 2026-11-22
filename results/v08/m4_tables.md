# v0.8 milestone 4: what yesterday's experience buys tomorrow

Starting core: `artifacts/v08/core_exec_s1.safetensors`. Day 1: 234 jobs, 162 verified by the frozen core, 72 then worked by the teacher. Bank version 1: 17 entries. Every update: 3000000 tokens from the same checkpoint.

## proj, retention

| Arm | Jobs | Verified % | Answered % | Error among answers % | Asked for evidence % | Verified jobs / min | Scripts / job | Operations / job |
|---|---|---|---|---|---|---|---|---|
| core | 80 | 58.8 | 89 | 42.3 | 11 | 84 | 7.80 | 14.9 |
| core+bank | 80 | 83.8 | 91 | 16.4 | 9 | 239 | 3.51 | 21.3 |
| core+bank_priced | 80 | 68.8 | 89 | 31.0 | 11 | 128 | 5.58 | 22.2 |
| core+bank_guard | 80 | 88.8 | 91 | 11.0 | 9 | 237 | 2.67 | 69.4 |
| naive | 80 | 46.2 | 88 | 55.7 | 10 | 69 | 7.58 | 14.8 |
| replay | 80 | 55.0 | 91 | 47.9 | 8 | 81 | 7.70 | 14.8 |
| replay+bank | 80 | 83.8 | 91 | 16.4 | 8 | 242 | 3.46 | 21.2 |
| sleep | 80 | 50.0 | 92 | 54.1 | 8 | 73 | 7.67 | 14.9 |
| sleep+bank | 80 | 85.0 | 92 | 16.2 | 8 | 244 | 3.49 | 21.2 |
| teacher | 80 | 100.0 | 88 | 0.0 | 12 | 189 | 6.91 | 10.8 |
| search | 80 | 100.0 | 88 | 0.0 | 12 | 675 | 1.00 | 47.8 |

## proj, transfer

| Arm | Jobs | Verified % | Answered % | Error among answers % | Asked for evidence % | Verified jobs / min | Scripts / job | Operations / job |
|---|---|---|---|---|---|---|---|---|
| core | 50 | 0.0 | 82 | 100.0 | 16 | 0 | 8.98 | 19.4 |
| core+bank | 50 | 100.0 | 100 | 0.0 | 0 | 793 | 1.00 | 14.0 |
| core+bank_priced | 50 | 100.0 | 100 | 0.0 | 0 | 796 | 1.00 | 12.3 |
| core+bank_guard | 50 | 100.0 | 100 | 0.0 | 0 | 480 | 1.00 | 83.6 |
| naive | 50 | 22.0 | 92 | 76.1 | 8 | 28 | 8.22 | 17.9 |
| replay | 50 | 4.0 | 80 | 95.0 | 16 | 5 | 8.74 | 19.0 |
| replay+bank | 50 | 100.0 | 100 | 0.0 | 0 | 788 | 1.00 | 14.0 |
| sleep | 50 | 38.0 | 94 | 59.6 | 6 | 51 | 7.90 | 16.7 |
| sleep+bank | 50 | 100.0 | 100 | 0.0 | 0 | 788 | 1.00 | 14.0 |
| teacher | 50 | 100.0 | 100 | 0.0 | 0 | 210 | 6.00 | 10.0 |
| search | 50 | 100.0 | 100 | 0.0 | 0 | 687 | 1.00 | 47.4 |

## proj, trap

| Arm | Jobs | Verified % | Answered % | Error among answers % | Asked for evidence % | Verified jobs / min | Scripts / job | Operations / job |
|---|---|---|---|---|---|---|---|---|
| core | 30 | 33.3 | 80 | 58.3 | 17 | 46 | 7.93 | 15.6 |
| core+bank | 30 | 6.7 | 100 | 93.3 | 0 | 53 | 1.00 | 14.7 |
| core+bank_priced | 30 | 6.7 | 100 | 93.3 | 0 | 53 | 1.00 | 12.3 |
| core+bank_guard | 30 | 0.0 | 0 | 0.0 | 100 | 0 | 1.00 | 86.4 |
| naive | 30 | 23.3 | 90 | 74.1 | 7 | 35 | 7.23 | 14.8 |
| replay | 30 | 56.7 | 97 | 41.4 | 3 | 91 | 6.93 | 13.5 |
| replay+bank | 30 | 6.7 | 100 | 93.3 | 0 | 53 | 1.00 | 14.7 |
| sleep | 30 | 33.3 | 90 | 63.0 | 7 | 51 | 7.13 | 14.2 |
| sleep+bank | 30 | 6.7 | 100 | 93.3 | 0 | 52 | 1.00 | 14.7 |
| teacher | 30 | 100.0 | 100 | 0.0 | 0 | 181 | 6.90 | 11.2 |
| search | 30 | 20.0 | 100 | 80.0 | 0 | 138 | 1.00 | 45.5 |

## proj, whole day

| Arm | Jobs | Verified % | Answered % | Error among answers % | Asked for evidence % | Verified jobs / min | Scripts / job | Operations / job |
|---|---|---|---|---|---|---|---|---|
| core | 160 | 35.6 | 85 | 62.5 | 14 | 47 | 8.19 | 16.4 |
| core+bank | 160 | 74.4 | 96 | 26.1 | 4 | 312 | 2.26 | 17.8 |
| core+bank_priced | 160 | 66.9 | 94 | 33.1 | 6 | 202 | 3.29 | 17.2 |
| core+bank_guard | 160 | 75.6 | 77 | 6.5 | 23 | 257 | 1.84 | 77.0 |
| naive | 160 | 34.4 | 89 | 65.7 | 9 | 49 | 7.71 | 15.8 |
| replay | 160 | 39.4 | 89 | 59.9 | 9 | 55 | 7.88 | 15.9 |
| replay+bank | 160 | 74.4 | 96 | 26.1 | 4 | 314 | 2.23 | 17.7 |
| sleep | 160 | 43.1 | 92 | 57.4 | 7 | 62 | 7.64 | 15.3 |
| sleep+bank | 160 | 75.0 | 96 | 26.0 | 4 | 315 | 2.24 | 17.8 |
| teacher | 160 | 100.0 | 94 | 0.0 | 6 | 193 | 6.62 | 10.6 |
| search | 160 | 85.0 | 94 | 16.0 | 6 | 579 | 1.00 | 47.2 |

## tab, retention

| Arm | Jobs | Verified % | Answered % | Error among answers % | Asked for evidence % | Verified jobs / min | Scripts / job | Operations / job |
|---|---|---|---|---|---|---|---|---|
| core | 80 | 98.8 | 88 | 1.4 | 12 | 531 | 3.54 | 6.4 |
| core+bank | 80 | 100.0 | 88 | 0.0 | 12 | 946 | 1.75 | 8.0 |
| core+bank_priced | 80 | 100.0 | 88 | 0.0 | 12 | 943 | 1.75 | 8.0 |
| core+bank_guard | 80 | 100.0 | 88 | 0.0 | 12 | 778 | 1.75 | 8.0 |
| naive | 80 | 97.5 | 88 | 2.9 | 12 | 523 | 3.56 | 6.4 |
| replay | 80 | 97.5 | 88 | 2.9 | 12 | 524 | 3.55 | 6.4 |
| replay+bank | 80 | 100.0 | 88 | 0.0 | 12 | 936 | 1.75 | 8.0 |
| sleep | 80 | 97.5 | 88 | 2.9 | 12 | 524 | 3.55 | 6.4 |
| sleep+bank | 80 | 100.0 | 88 | 0.0 | 12 | 905 | 1.75 | 8.0 |
| teacher | 80 | 100.0 | 88 | 0.0 | 12 | 608 | 3.50 | 6.3 |
| search | 80 | 100.0 | 88 | 0.0 | 12 | 1414 | 1.00 | 6.4 |

## tab, transfer

| Arm | Jobs | Verified % | Answered % | Error among answers % | Asked for evidence % | Verified jobs / min | Scripts / job | Operations / job |
|---|---|---|---|---|---|---|---|---|
| core | 40 | 100.0 | 100 | 0.0 | 0 | 458 | 4.00 | 6.8 |
| core+bank | 40 | 100.0 | 100 | 0.0 | 0 | 600 | 2.80 | 9.2 |
| core+bank_priced | 40 | 100.0 | 100 | 0.0 | 0 | 598 | 2.80 | 9.2 |
| core+bank_guard | 40 | 100.0 | 100 | 0.0 | 0 | 470 | 2.80 | 9.2 |
| naive | 40 | 100.0 | 100 | 0.0 | 0 | 461 | 4.00 | 6.8 |
| replay | 40 | 100.0 | 100 | 0.0 | 0 | 457 | 4.00 | 6.8 |
| replay+bank | 40 | 100.0 | 100 | 0.0 | 0 | 595 | 2.80 | 9.2 |
| sleep | 40 | 100.0 | 100 | 0.0 | 0 | 463 | 4.00 | 6.8 |
| sleep+bank | 40 | 100.0 | 100 | 0.0 | 0 | 582 | 2.80 | 9.2 |
| teacher | 40 | 100.0 | 100 | 0.0 | 0 | 507 | 4.00 | 6.8 |
| search | 40 | 100.0 | 100 | 0.0 | 0 | 1430 | 1.00 | 6.8 |

## tab, whole day

| Arm | Jobs | Verified % | Answered % | Error among answers % | Asked for evidence % | Verified jobs / min | Scripts / job | Operations / job |
|---|---|---|---|---|---|---|---|---|
| core | 120 | 99.2 | 92 | 0.9 | 8 | 504 | 3.69 | 6.5 |
| core+bank | 120 | 100.0 | 92 | 0.0 | 8 | 794 | 2.10 | 8.4 |
| core+bank_priced | 120 | 100.0 | 92 | 0.0 | 8 | 791 | 2.10 | 8.4 |
| core+bank_guard | 120 | 100.0 | 92 | 0.0 | 8 | 638 | 2.10 | 8.4 |
| naive | 120 | 98.3 | 92 | 1.8 | 8 | 500 | 3.71 | 6.5 |
| replay | 120 | 98.3 | 92 | 1.8 | 8 | 500 | 3.70 | 6.5 |
| replay+bank | 120 | 100.0 | 92 | 0.0 | 8 | 786 | 2.10 | 8.4 |
| sleep | 120 | 98.3 | 92 | 1.8 | 8 | 502 | 3.70 | 6.5 |
| sleep+bank | 120 | 100.0 | 92 | 0.0 | 8 | 763 | 2.10 | 8.4 |
| teacher | 120 | 100.0 | 92 | 0.0 | 8 | 571 | 3.67 | 6.5 |
| search | 120 | 100.0 | 92 | 0.0 | 8 | 1419 | 1.00 | 6.6 |

## Harm and gain against the frozen core, retention set (jobs)

| Arm | Core right, arm not (harm) | Arm right, core not (gain) | Jobs |
|---|---|---|---|
| core+bank | 0 | 21 | 160 |
| core+bank_priced | 0 | 9 | 160 |
| core+bank_guard | 0 | 25 | 160 |
| naive | 11 | 0 | 160 |
| replay | 6 | 2 | 160 |
| replay+bank | 1 | 22 | 160 |
| sleep | 10 | 2 | 160 |
| sleep+bank | 1 | 23 | 160 |

## What the bank did (jobs; the bank's procedure runs first and anything but PASS leaves the work untouched)

| Arm | Set | Jobs | Finished by the bank | of which wrong | Tried and failed (handed on) | Declined | Operations spent in failed tries, per job |
|---|---|---|---|---|---|---|---|
| core+bank | retention | 160 | 117 | 0 | 15 | 28 | 1.99 |
| core+bank | transfer | 90 | 72 | 0 | 0 | 18 | 0.00 |
| core+bank | trap | 30 | 30 | 28 | 0 | 0 | 0.00 |
| core+bank | whole day | 280 | 219 | 28 | 15 | 46 | 1.14 |
| core+bank_priced | retention | 160 | 99 | 0 | 33 | 28 | 3.13 |
| core+bank_priced | transfer | 90 | 72 | 0 | 0 | 18 | 0.00 |
| core+bank_priced | trap | 30 | 30 | 28 | 0 | 0 | 0.00 |
| core+bank_priced | whole day | 280 | 201 | 28 | 33 | 46 | 1.79 |
| core+bank_guard | retention | 160 | 124 | 0 | 8 | 28 | 4.17 |
| core+bank_guard | transfer | 90 | 72 | 0 | 0 | 18 | 0.00 |
| core+bank_guard | trap | 30 | 0 | 0 | 0 | 0 (+30 asked) | 0.00 |
| core+bank_guard | whole day | 280 | 196 | 0 | 8 | 46 (+30 asked) | 2.39 |
| replay+bank | retention | 160 | 117 | 0 | 15 | 28 | 1.99 |
| replay+bank | transfer | 90 | 72 | 0 | 0 | 18 | 0.00 |
| replay+bank | trap | 30 | 30 | 28 | 0 | 0 | 0.00 |
| replay+bank | whole day | 280 | 219 | 28 | 15 | 46 | 1.14 |
| sleep+bank | retention | 160 | 117 | 0 | 15 | 28 | 1.99 |
| sleep+bank | transfer | 90 | 72 | 0 | 0 | 18 | 0.00 |
| sleep+bank | trap | 30 | 30 | 28 | 0 | 0 | 0.00 |
| sleep+bank | whole day | 280 | 219 | 28 | 15 | 46 | 1.14 |

## Break-even

Overnight cost in seconds on this machine (bank: promotion and gate; update: corpus, training and, for sleep, validation), against what the arm changes on the whole of day 2 relative to the frozen core.
Jobs to recover the night = overnight seconds / seconds saved per job. Where the arm is slower per job it never recovers the cost in time; what it buys is the extra verified jobs.

| Arm | Overnight s | Seconds per job (core) | Seconds per job (arm) | Jobs to recover the night in time | Extra verified jobs per 100 |
|---|---|---|---|---|---|
| core+bank | 0.0 | 0.309 | 0.114 | 0 | +22.5 |
| core+bank_priced | 0.0 | 0.309 | 0.146 | 0 | +18.2 |
| core+bank_guard | 0.0 | 0.309 | 0.141 | 0 | +23.2 |
| naive | 40.8 | 0.309 | 0.292 | 2304 | -1.1 |
| replay | 58.1 | 0.309 | 0.297 | 4553 | +1.8 |
| replay+bank | 58.1 | 0.309 | 0.114 | 297 | +22.5 |
| sleep | 191.7 | 0.309 | 0.289 | 9195 | +3.9 |
| sleep+bank | 191.7 | 0.309 | 0.115 | 987 | +22.9 |

## Overnight validation and promotion

Fresh later-mechanism jobs from day-1 sources (new) and the development set (old, earlier skills), verified %: frozen: new 50.0, old 76.9; naive: new 58.3, old 70.3; replay: new 55.0, old 74.1; sleep: new 65.0, old 71.2.
Sleep update promoted: **False** (earlier skills (the 320 development jobs) no more than 2 points below the frozen core, and later skills (60 fresh jobs from day-1 sources, not in the corpus) above it). Dreams generated and verified by execution: 400 (7278 operations). Day-1 records used: 234.
