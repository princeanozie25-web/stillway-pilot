# v0.7 results: dev_seed1

72 repositories. Arms and seeds: A unchanged (1 seed); B final patches (1 seed); C experience (1 seed); D experience + bank (1 seed); D1 bank, version 1 only (1 seed); E experience + nearest example (1 seed); F bank disabled (1 seed); W wrong diagnostic (1 seed).

## First submitted patch passes hidden grading (% of repositories; mean over seeds)

| Arm | all (n=72) | not repeats (G2+G3+G4) (n=48) | G1 (n=24) | G2 (n=16) | G3 (n=16) | G4 (n=16) |
|---|---|---|---|---|---|---|
| A unchanged | 19.4 | 25.0 | 8.3 | 25.0 | 25.0 | 25.0 |
| B final patches | 44.4 | 16.7 | 100.0 | 50.0 | 0.0 | 0.0 |
| C experience | 51.4 | 29.2 | 95.8 | 68.8 | 6.2 | 12.5 |
| D experience + bank | 45.8 | 27.1 | 83.3 | 68.8 | 0.0 | 12.5 |
| D1 bank, version 1 only | 43.1 | 22.9 | 83.3 | 56.2 | 6.2 | 6.2 |
| E experience + nearest example | 52.8 | 33.3 | 91.7 | 75.0 | 6.2 | 18.8 |
| F bank disabled | 48.6 | 29.2 | 87.5 | 68.8 | 6.2 | 12.5 |
| W wrong diagnostic | 44.4 | 22.9 | 87.5 | 56.2 | 0.0 | 12.5 |

## Every seed

| Arm | Seed | all | not repeats (G2+G3+G4) | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|---|
| A unchanged | 0 | 14/72 | 12/48 | 2/24 | 4/16 | 4/16 | 4/16 |
| B final patches | 1 | 32/72 | 8/48 | 24/24 | 8/16 | 0/16 | 0/16 |
| C experience | 1 | 37/72 | 14/48 | 23/24 | 11/16 | 1/16 | 2/16 |
| D experience + bank | 1 | 33/72 | 13/48 | 20/24 | 11/16 | 0/16 | 2/16 |
| D1 bank, version 1 only | 1 | 31/72 | 11/48 | 20/24 | 9/16 | 1/16 | 1/16 |
| E experience + nearest example | 1 | 38/72 | 16/48 | 22/24 | 12/16 | 1/16 | 3/16 |
| F bank disabled | 1 | 35/72 | 14/48 | 21/24 | 11/16 | 1/16 | 2/16 |
| W wrong diagnostic | 1 | 32/72 | 11/48 | 21/24 | 9/16 | 0/16 | 2/16 |

## Paired differences per repository (percentage points; 95% interval by resampling repositories, then by resampling whole families)

| Contrast | Group | Difference | Repositories | Families | Better / same / worse |
|---|---|---|---|---|---|
| D experience + bank minus A unchanged | all | +26.4 | +11.1 to +41.7 | +0.0 to +54.3 | 27 / 37 / 8 |
| D experience + bank minus A unchanged | not repeats (G2+G3+G4) | +2.1 | -14.6 to +18.8 | -31.3 to +31.2 | 9 / 31 / 8 |
| D experience + bank minus A unchanged | G1 | +75.0 | +58.3 to +91.7 | +50.0 to +100.0 | 18 / 6 / 0 |
| D experience + bank minus A unchanged | G2 | +43.8 | +18.8 to +68.8 | +0.0 to +87.5 | 7 / 9 / 0 |
| D experience + bank minus A unchanged | G3 | -25.0 | -50.0 to -6.2 | -75.0 to +0.0 | 0 / 12 / 4 |
| D experience + bank minus A unchanged | G4 | -12.5 | -43.8 to +18.8 | -75.0 to +37.5 | 2 / 10 / 4 |
| C experience minus A unchanged | all | +31.9 | +15.3 to +48.6 | +4.8 to +60.3 | 33 / 29 / 10 |
| C experience minus A unchanged | not repeats (G2+G3+G4) | +4.2 | -14.6 to +22.9 | -33.3 to +39.6 | 12 / 26 / 10 |
| C experience minus A unchanged | G1 | +87.5 | +75.0 to +100.0 | +70.8 to +100.0 | 21 / 3 / 0 |
| C experience minus A unchanged | G2 | +43.8 | +6.2 to +75.0 | -12.5 to +100.0 | 9 / 5 / 2 |
| C experience minus A unchanged | G3 | -18.8 | -43.8 to +6.2 | -75.0 to +18.8 | 1 / 11 / 4 |
| C experience minus A unchanged | G4 | -12.5 | -43.8 to +18.8 | -75.0 to +37.5 | 2 / 10 / 4 |
| B final patches minus A unchanged | all | +25.0 | +11.1 to +38.9 | +0.0 to +53.1 | 26 / 38 / 8 |
| B final patches minus A unchanged | not repeats (G2+G3+G4) | -8.3 | -22.9 to +6.2 | -33.3 to +16.7 | 4 / 36 / 8 |
| B final patches minus A unchanged | G1 | +91.7 | +79.2 to +100.0 | +75.0 to +100.0 | 22 / 2 / 0 |
| B final patches minus A unchanged | G2 | +25.0 | +6.2 to +50.0 | +0.0 to +75.0 | 4 / 12 / 0 |
| B final patches minus A unchanged | G3 | -25.0 | -50.0 to -6.2 | -75.0 to +0.0 | 0 / 12 / 4 |
| B final patches minus A unchanged | G4 | -25.0 | -50.0 to -6.2 | -75.0 to +0.0 | 0 / 12 / 4 |
| D experience + bank minus B final patches | all | +1.4 | -6.9 to +9.7 | -11.8 to +13.4 | 5 / 63 / 4 |
| D experience + bank minus B final patches | not repeats (G2+G3+G4) | +10.4 | +2.1 to +20.8 | +0.0 to +25.0 | 5 / 43 / 0 |
| D experience + bank minus B final patches | G1 | -16.7 | -33.3 to -4.2 | -41.7 to +0.0 | 0 / 20 / 4 |
| D experience + bank minus B final patches | G2 | +18.8 | +0.0 to +37.5 | +0.0 to +56.2 | 3 / 13 / 0 |
| D experience + bank minus B final patches | G3 | +0.0 | +0.0 to +0.0 | +0.0 to +0.0 | 0 / 16 / 0 |
| D experience + bank minus B final patches | G4 | +12.5 | +0.0 to +31.2 | +0.0 to +37.5 | 2 / 14 / 0 |
| C experience minus B final patches | all | +6.9 | -1.4 to +15.3 | -5.7 to +21.1 | 8 / 61 / 3 |
| C experience minus B final patches | not repeats (G2+G3+G4) | +12.5 | +0.0 to +25.0 | -6.2 to +33.3 | 8 / 38 / 2 |
| C experience minus B final patches | G1 | -4.2 | -12.5 to +0.0 | -12.5 to +0.0 | 0 / 23 / 1 |
| C experience minus B final patches | G2 | +18.8 | -12.5 to +50.0 | -31.2 to +75.0 | 5 / 9 / 2 |
| C experience minus B final patches | G3 | +6.2 | +0.0 to +18.8 | +0.0 to +18.8 | 1 / 15 / 0 |
| C experience minus B final patches | G4 | +12.5 | +0.0 to +31.2 | +0.0 to +37.5 | 2 / 14 / 0 |
| D experience + bank minus F bank disabled | all | -2.8 | -11.1 to +4.2 | -11.1 to +4.4 | 3 / 64 / 5 |
| D experience + bank minus F bank disabled | not repeats (G2+G3+G4) | -2.1 | -10.4 to +6.2 | -8.3 to +4.2 | 2 / 43 / 3 |
| D experience + bank minus F bank disabled | G1 | -4.2 | -20.8 to +8.3 | -25.0 to +12.5 | 1 / 21 / 2 |
| D experience + bank minus F bank disabled | G2 | +0.0 | +0.0 to +0.0 | +0.0 to +0.0 | 0 / 16 / 0 |
| D experience + bank minus F bank disabled | G3 | -6.2 | -18.8 to +0.0 | -18.8 to +0.0 | 0 / 15 / 1 |
| D experience + bank minus F bank disabled | G4 | +0.0 | -25.0 to +25.0 | -18.8 to +18.8 | 2 / 12 / 2 |
| D experience + bank minus E experience + nearest example | all | -6.9 | -13.9 to +0.0 | -13.9 to -1.4 | 1 / 65 / 6 |
| D experience + bank minus E experience + nearest example | not repeats (G2+G3+G4) | -6.2 | -16.7 to +2.1 | -12.5 to +0.0 | 1 / 43 / 4 |
| D experience + bank minus E experience + nearest example | G1 | -8.3 | -20.8 to +0.0 | -25.0 to +0.0 | 0 / 22 / 2 |
| D experience + bank minus E experience + nearest example | G2 | -6.2 | -18.8 to +0.0 | -18.8 to +0.0 | 0 / 15 / 1 |
| D experience + bank minus E experience + nearest example | G3 | -6.2 | -18.8 to +0.0 | -18.8 to +0.0 | 0 / 15 / 1 |
| D experience + bank minus E experience + nearest example | G4 | -6.2 | -25.0 to +12.5 | -18.8 to +0.0 | 1 / 13 / 2 |
| E experience + nearest example minus F bank disabled | all | +4.2 | -1.4 to +9.7 | -1.4 to +10.0 | 4 / 67 / 1 |
| E experience + nearest example minus F bank disabled | not repeats (G2+G3+G4) | +4.2 | -4.2 to +12.5 | -4.2 to +12.5 | 3 / 44 / 1 |
| E experience + nearest example minus F bank disabled | G1 | +4.2 | +0.0 to +12.5 | +0.0 to +12.5 | 1 / 23 / 0 |
| E experience + nearest example minus F bank disabled | G2 | +6.2 | +0.0 to +18.8 | +0.0 to +18.8 | 1 / 15 / 0 |
| E experience + nearest example minus F bank disabled | G3 | +0.0 | +0.0 to +0.0 | +0.0 to +0.0 | 0 / 16 / 0 |
| E experience + nearest example minus F bank disabled | G4 | +6.2 | -12.5 to +25.0 | -12.5 to +25.0 | 2 / 13 / 1 |
| W wrong diagnostic minus F bank disabled | all | -4.2 | -9.7 to +1.4 | -11.4 to +2.6 | 1 / 67 / 4 |
| W wrong diagnostic minus F bank disabled | not repeats (G2+G3+G4) | -6.2 | -14.6 to +2.1 | -16.7 to +2.1 | 1 / 43 / 4 |
| W wrong diagnostic minus F bank disabled | G1 | +0.0 | +0.0 to +0.0 | +0.0 to +0.0 | 0 / 24 / 0 |
| W wrong diagnostic minus F bank disabled | G2 | -12.5 | -31.2 to +0.0 | -37.5 to +0.0 | 0 / 14 / 2 |
| W wrong diagnostic minus F bank disabled | G3 | -6.2 | -18.8 to +0.0 | -18.8 to +0.0 | 0 / 15 / 1 |
| W wrong diagnostic minus F bank disabled | G4 | +0.0 | -18.8 to +18.8 | -18.8 to +18.8 | 1 / 14 / 1 |
| D experience + bank minus D1 bank, version 1 only | all | +2.8 | -2.8 to +8.3 | -2.9 to +10.0 | 3 / 68 / 1 |
| D experience + bank minus D1 bank, version 1 only | not repeats (G2+G3+G4) | +4.2 | -4.2 to +12.5 | -4.2 to +14.6 | 3 / 44 / 1 |
| D experience + bank minus D1 bank, version 1 only | G1 | +0.0 | +0.0 to +0.0 | +0.0 to +0.0 | 0 / 24 / 0 |
| D experience + bank minus D1 bank, version 1 only | G2 | +12.5 | +0.0 to +31.2 | +0.0 to +37.5 | 2 / 14 / 0 |
| D experience + bank minus D1 bank, version 1 only | G3 | -6.2 | -18.8 to +0.0 | -18.8 to +0.0 | 0 / 15 / 1 |
| D experience + bank minus D1 bank, version 1 only | G4 | +6.2 | +0.0 to +18.8 | +0.0 to +18.8 | 1 / 15 / 0 |

## Regressions, tests and cost (all repositories; mean over seeds)

| Arm | Repositories with a hidden test broken by the patch | Patch applied | Tests well formed | Predictions that matched execution | Visible tests pass but hidden fail | Seconds of generation per repository | New tokens per repository | Generation seconds per correct fix |
|---|---|---|---|---|---|---|---|---|
| A unchanged | 5.6% | 84.7% | 98.6% | 11.8% | 0.0% | 5.1 | 303 | 26.2 |
| B final patches | 8.3% | 100.0% | 93.1% | 0.7% | 0.0% | 5.1 | 209 | 11.5 |
| C experience | 27.8% | 98.6% | 100.0% | 43.8% | 4.2% | 5.2 | 251 | 10.1 |
| D experience + bank | 29.2% | 100.0% | 100.0% | 38.9% | 1.4% | 5.6 | 248 | 12.1 |
| D1 bank, version 1 only | 27.8% | 100.0% | 100.0% | 41.0% | 1.4% | 5.4 | 248 | 12.4 |
| E experience + nearest example | 25.0% | 97.2% | 100.0% | 40.3% | 2.8% | 5.7 | 249 | 10.8 |
| F bank disabled | 23.6% | 98.6% | 100.0% | 41.7% | 1.4% | 5.2 | 249 | 10.6 |
| W wrong diagnostic | 26.4% | 98.6% | 100.0% | 36.8% | 1.4% | 5.6 | 245 | 12.6 |

## Regressions by group (% of repositories where the patch broke a hidden test that passed before)

| Arm | all | not repeats (G2+G3+G4) | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|
| A unchanged | 5.6 | 2.1 | 12.5 | 6.2 | 0.0 | 0.0 |
| B final patches | 8.3 | 12.5 | 0.0 | 37.5 | 0.0 | 0.0 |
| C experience | 27.8 | 41.7 | 0.0 | 18.8 | 75.0 | 31.2 |
| D experience + bank | 29.2 | 41.7 | 4.2 | 12.5 | 87.5 | 25.0 |
| D1 bank, version 1 only | 27.8 | 39.6 | 4.2 | 18.8 | 75.0 | 25.0 |
| E experience + nearest example | 25.0 | 37.5 | 0.0 | 12.5 | 62.5 | 37.5 |
| F bank disabled | 23.6 | 33.3 | 4.2 | 25.0 | 50.0 | 25.0 |
| W wrong diagnostic | 26.4 | 37.5 | 4.2 | 31.2 | 62.5 | 18.8 |

## Repositories where the trained fix does not belong (26): share where the submitted patch fails exactly as the trained fix does

| Arm | Lookalikes (G3) | Other groups |
|---|---|---|
| A unchanged | 25.0% | 0.0% |
| B final patches | 25.0% | 40.0% |
| C experience | 31.2% | 0.0% |
| D experience + bank | 62.5% | 20.0% |
| D1 bank, version 1 only | 68.8% | 30.0% |
| E experience + nearest example | 31.2% | 0.0% |
| F bank disabled | 43.8% | 10.0% |
| W wrong diagnostic | 37.5% | 10.0% |

## After a contradiction: episodes in which at least one test did not come out as predicted

| Arm | Episodes with a contradiction | First patch correct after a contradiction | First patch correct with no contradiction |
|---|---|---|---|
| A unchanged | 65 of 72 | 18.5% | 28.6% |
| B final patches | 72 of 72 | 44.4% | nan% |
| C experience | 51 of 72 | 39.2% | 81.0% |
| D experience + bank | 54 of 72 | 31.5% | 88.9% |
| D1 bank, version 1 only | 55 of 72 | 27.3% | 94.1% |
| E experience + nearest example | 53 of 72 | 47.2% | 68.4% |
| F bank disabled | 52 of 72 | 36.5% | 80.0% |
| W wrong diagnostic | 56 of 72 | 33.9% | 81.2% |

## D experience + bank: correctness by repeated use, status and diagnostic

| Split | Value | Episodes | First patch correct |
|---|---|---|---|
| by diagnostic | S1 | 27 | 33.3% |
| by diagnostic | S2 | 23 | 47.8% |
| by diagnostic | S3 | 22 | 59.1% |
| by status at the patch | reopened | 54 | 31.5% |
| by status at the patch | supported | 18 | 88.9% |
| by use | use 1-5 | 15 | 53.3% |
| by use | use 16+ | 27 | 40.7% |
| by use | use 6-15 | 30 | 46.7% |

## D1 bank, version 1 only: correctness by repeated use, status and diagnostic

| Split | Value | Episodes | First patch correct |
|---|---|---|---|
| by diagnostic | S1 | 27 | 33.3% |
| by diagnostic | S2 | 23 | 39.1% |
| by diagnostic | S3 | 22 | 59.1% |
| by status at the patch | reopened | 55 | 27.3% |
| by status at the patch | supported | 17 | 94.1% |
| by use | use 1-5 | 15 | 46.7% |
| by use | use 16+ | 27 | 40.7% |
| by use | use 6-15 | 30 | 43.3% |

## W wrong diagnostic: correctness by repeated use, status and diagnostic

| Split | Value | Episodes | First patch correct |
|---|---|---|---|
| by diagnostic | S1 | 22 | 54.5% |
| by diagnostic | S2 | 27 | 33.3% |
| by diagnostic | S3 | 23 | 47.8% |
| by status at the patch | reopened | 56 | 33.9% |
| by status at the patch | supported | 16 | 81.2% |
| by use | use 1-5 | 15 | 40.0% |
| by use | use 16+ | 27 | 40.7% |
| by use | use 6-15 | 30 | 50.0% |

## Per repository (first patch correct in how many seeds)

| Repository | Group | Family | A | B | C | D | D1 | E | F | W |
|---|---|---|---|---|---|---|---|---|---|---|
| dev_000 | G3 | look_split_window | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_001 | G3 | look_default_seen | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_002 | G2 | stale_peak | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 |
| dev_003 | G4 | int_division | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_004 | G3 | look_default_seen | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_005 | G1 | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_006 | G1 | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_007 | G1 | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_008 | G1 | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_009 | G2 | iter_attr | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_010 | G4 | float_equal | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 |
| dev_011 | G4 | float_equal | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_012 | G3 | look_shared_entries | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_013 | G2 | stale_peak | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_014 | G2 | stale_peak | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| dev_015 | G1 | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_016 | G1 | stale_rates | 0/1 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 |
| dev_017 | G4 | float_equal | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 |
| dev_018 | G2 | bound_lower | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_019 | G1 | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_020 | G2 | stale_remove | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_021 | G2 | bound_lower | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_022 | G1 | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_023 | G1 | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_024 | G2 | stale_remove | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_025 | G2 | stale_remove | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_026 | G4 | sort_text_numbers | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_027 | G1 | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_028 | G2 | stale_remove | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_029 | G3 | look_shared_entries | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_030 | G4 | sort_text_numbers | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_031 | G1 | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_032 | G4 | sort_text_numbers | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_033 | G4 | sort_text_numbers | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_034 | G4 | int_division | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_035 | G4 | float_equal | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_036 | G1 | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_037 | G1 | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_038 | G3 | look_split_window | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_039 | G4 | case_key | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_040 | G3 | look_labels | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_041 | G3 | look_shared_entries | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_042 | G2 | iter_attr | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_043 | G4 | int_division | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_044 | G3 | look_labels | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_045 | G3 | look_split_window | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_046 | G2 | bound_lower | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_047 | G3 | look_labels | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_048 | G3 | look_default_seen | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_049 | G1 | lost_write | 0/1 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_050 | G4 | int_division | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 |
| dev_051 | G2 | bound_lower | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_052 | G3 | look_split_window | 1/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| dev_053 | G1 | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_054 | G4 | case_key | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 |
| dev_055 | G2 | stale_peak | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| dev_056 | G4 | case_key | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 |
| dev_057 | G1 | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_058 | G1 | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_059 | G2 | iter_attr | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_060 | G4 | case_key | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_061 | G1 | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_062 | G1 | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_063 | G2 | iter_attr | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_064 | G1 | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 |
| dev_065 | G3 | look_shared_entries | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_066 | G1 | stale_rates | 0/1 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 |
| dev_067 | G1 | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_068 | G1 | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_069 | G3 | look_labels | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| dev_070 | G1 | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dev_071 | G3 | look_default_seen | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
