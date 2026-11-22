# v0.8 trap set: results/v08/trap_dry/run

Counts with share and 95% interval. Job groups in the set: draw.

## Trap jobs: another one-line change passes both visible checks and is wrong (every group)

| Arm | Jobs | Verified | Wrong DONE | Asked, nothing changed | Out of limits | Ended by the bank: right / wrong / asked | Operations per job | Seconds per job |
|---|---|---|---|---|---|---|---|---|
| bank | 143 | 63 (44%; 36 to 52) | 76 (53%; 45 to 61) | 3 (2%; 1 to 6) | 1 | 54 / 41 / 0 | 22.8 | 0.244 |
| bankguard | 143 | 1 (1%; 0 to 4) | 15 (10%; 6 to 17) | 127 (89%; 83 to 93) | 0 | 0 / 0 / 126 | 77.6 | 0.163 |
| exec | 143 | 34 (24%; 18 to 31) | 99 (69%; 61 to 76) | 9 (6%; 3 to 12) | 1 | 0 / 0 / 0 | 16.9 | 0.463 |
| search | 143 | 80 (56%; 48 to 64) | 63 (44%; 36 to 52) | 0 (0%; 0 to 3) | 0 | 0 / 0 / 0 | 44.4 | 0.085 |

## Equal jobs: several one-line changes pass both visible checks and all are right (asking is unnecessary) (every group)

| Arm | Jobs | Verified | Wrong DONE | Asked, nothing changed | Out of limits | Ended by the bank: right / wrong / asked | Operations per job | Seconds per job |
|---|---|---|---|---|---|---|---|---|
| bank | 17 | 5 (29%; 13 to 53) | 12 (71%; 47 to 87) | 0 (0%; 0 to 18) | 0 | 4 / 0 / 0 | 25.3 | 0.487 |
| bankguard | 17 | 1 (6%; 1 to 27) | 8 (47%; 26 to 69) | 8 (47%; 26 to 69) | 0 | 0 / 0 / 8 | 52.9 | 0.377 |
| exec | 17 | 3 (18%; 6 to 41) | 14 (82%; 59 to 94) | 0 (0%; 0 to 18) | 0 | 0 / 0 / 0 | 20.6 | 0.537 |
| search | 17 | 17 (100%; 82 to 100) | 0 (0%; 0 to 18) | 0 (0%; 0 to 18) | 0 | 0 / 0 / 0 | 32.5 | 0.081 |

## Ordinary jobs: the repair is the only one-line change that passes (asking is an error) (every group)

| Arm | Jobs | Verified | Wrong DONE | Asked, nothing changed | Out of limits | Ended by the bank: right / wrong / asked | Operations per job | Seconds per job |
|---|---|---|---|---|---|---|---|---|
| bank | 240 | 203 (85%; 79 to 89) | 31 (13%; 9 to 18) | 4 (2%; 1 to 4) | 2 | 194 / 0 / 0 | 20.6 | 0.172 |
| bankguard | 240 | 226 (94%; 90 to 96) | 11 (5%; 3 to 8) | 1 (0%; 0 to 2) | 2 | 221 / 0 / 0 | 79.0 | 0.139 |
| exec | 240 | 93 (39%; 33 to 45) | 114 (48%; 41 to 54) | 26 (11%; 8 to 15) | 7 | 0 / 0 / 0 | 16.6 | 0.450 |
| search | 240 | 240 (100%; 98 to 100) | 0 (0%; 0 to 2) | 0 (0%; 0 to 2) | 0 | 0 / 0 / 0 | 47.1 | 0.087 |

## Every job (every group)

| Arm | Jobs | Verified | Wrong DONE | Asked, nothing changed | Out of limits | Ended by the bank: right / wrong / asked | Operations per job | Seconds per job |
|---|---|---|---|---|---|---|---|---|
| bank | 400 | 271 (68%; 63 to 72) | 119 (30%; 25 to 34) | 7 (2%; 1 to 4) | 3 | 252 / 41 / 0 | 21.6 | 0.211 |
| bankguard | 400 | 228 (57%; 52 to 62) | 34 (8%; 6 to 12) | 136 (34%; 30 to 39) | 2 | 221 / 0 / 134 | 77.4 | 0.158 |
| exec | 400 | 130 (32%; 28 to 37) | 227 (57%; 52 to 62) | 35 (9%; 6 to 12) | 8 | 0 / 0 / 0 | 16.8 | 0.458 |
| search | 400 | 337 (84%; 80 to 87) | 63 (16%; 13 to 20) | 0 (0%; 0 to 1) | 0 | 0 / 0 / 0 | 45.5 | 0.086 |

## The reading fixed beforehand (docs/v08_trap_plan.md)

- A. Trap jobs the plain bank itself ended with a wrong DONE: 41 of 143, 28.7% (22 to 37). 10% or less: the guard is unnecessary.
- B. Trap jobs the guarded bank itself ended with a wrong DONE: 0 of 143, 0.0% (0 to 3). More than 10%: it misses the traps.
- B. Ordinary jobs the guarded bank itself ended by asking: 0 of 240, 0.0% (0 to 2). More than 50%: it asks on most.
- C. On the unselected draw, whole arm, guarded against plain: 85 wrong DONE prevented (119 to 34), 43 verified jobs forgone (271 to 228). Break-even: the guard pays when one wrong DONE costs more than 0.51 lost completions. Above 3, or nothing prevented: too costly.
- Price in operations on the same jobs: 77.4 per job against 21.6.

**Verdict: GUARDED BANK STANDS**
