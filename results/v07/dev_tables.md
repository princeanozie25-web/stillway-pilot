# v0.7 results: dev

72 repositories. Arms and seeds: A unchanged (1 seed); AD unchanged + bank (1 seed); AE unchanged + nearest example (1 seed); B final patches (3 seeds); C experience (3 seeds); D experience + bank (3 seeds); D1 bank, version 1 only (3 seeds); E experience + nearest example (3 seeds); F bank disabled (3 seeds); W wrong diagnostic (3 seeds).

## First submitted patch passes hidden grading (% of repositories; mean over seeds)

| Arm | all (n=72) | not repeats (G2+G3+G4) (n=48) | G1 (n=24) | G2 (n=16) | G3 (n=16) | G4 (n=16) |
|---|---|---|---|---|---|---|
| A unchanged | 19.4 | 25.0 | 8.3 | 25.0 | 25.0 | 25.0 |
| AD unchanged + bank | 19.4 | 22.9 | 12.5 | 25.0 | 18.8 | 25.0 |
| AE unchanged + nearest example | 8.3 | 4.2 | 16.7 | 0.0 | 6.2 | 6.2 |
| B final patches | 46.8 | 20.1 | 100.0 | 50.0 | 8.3 | 2.1 |
| C experience | 48.6 | 25.0 | 95.8 | 62.5 | 6.2 | 6.2 |
| D experience + bank | 50.9 | 31.2 | 90.3 | 72.9 | 6.2 | 14.6 |
| D1 bank, version 1 only | 49.1 | 28.5 | 90.3 | 66.7 | 10.4 | 8.3 |
| E experience + nearest example | 48.6 | 27.1 | 91.7 | 60.4 | 6.2 | 14.6 |
| F bank disabled | 48.6 | 27.1 | 91.7 | 60.4 | 8.3 | 12.5 |
| W wrong diagnostic | 48.6 | 27.8 | 90.3 | 62.5 | 6.2 | 14.6 |

## Every seed

| Arm | Seed | all | not repeats (G2+G3+G4) | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|---|
| A unchanged | 0 | 14/72 | 12/48 | 2/24 | 4/16 | 4/16 | 4/16 |
| AD unchanged + bank | 0 | 14/72 | 11/48 | 3/24 | 4/16 | 3/16 | 4/16 |
| AE unchanged + nearest example | 0 | 6/72 | 2/48 | 4/24 | 0/16 | 1/16 | 1/16 |
| B final patches | 1 | 32/72 | 8/48 | 24/24 | 8/16 | 0/16 | 0/16 |
| B final patches | 2 | 37/72 | 13/48 | 24/24 | 8/16 | 4/16 | 1/16 |
| B final patches | 3 | 32/72 | 8/48 | 24/24 | 8/16 | 0/16 | 0/16 |
| C experience | 1 | 37/72 | 14/48 | 23/24 | 11/16 | 1/16 | 2/16 |
| C experience | 2 | 37/72 | 13/48 | 24/24 | 12/16 | 1/16 | 0/16 |
| C experience | 3 | 31/72 | 9/48 | 22/24 | 7/16 | 1/16 | 1/16 |
| D experience + bank | 1 | 33/72 | 13/48 | 20/24 | 11/16 | 0/16 | 2/16 |
| D experience + bank | 2 | 35/72 | 13/48 | 22/24 | 12/16 | 1/16 | 0/16 |
| D experience + bank | 3 | 42/72 | 19/48 | 23/24 | 12/16 | 2/16 | 5/16 |
| D1 bank, version 1 only | 1 | 31/72 | 11/48 | 20/24 | 9/16 | 1/16 | 1/16 |
| D1 bank, version 1 only | 2 | 34/72 | 12/48 | 22/24 | 12/16 | 0/16 | 0/16 |
| D1 bank, version 1 only | 3 | 41/72 | 18/48 | 23/24 | 11/16 | 4/16 | 3/16 |
| E experience + nearest example | 1 | 38/72 | 16/48 | 22/24 | 12/16 | 1/16 | 3/16 |
| E experience + nearest example | 2 | 33/72 | 11/48 | 22/24 | 10/16 | 0/16 | 1/16 |
| E experience + nearest example | 3 | 34/72 | 12/48 | 22/24 | 7/16 | 2/16 | 3/16 |
| F bank disabled | 1 | 35/72 | 14/48 | 21/24 | 11/16 | 1/16 | 2/16 |
| F bank disabled | 2 | 34/72 | 12/48 | 22/24 | 11/16 | 0/16 | 1/16 |
| F bank disabled | 3 | 36/72 | 13/48 | 23/24 | 7/16 | 3/16 | 3/16 |
| W wrong diagnostic | 1 | 32/72 | 11/48 | 21/24 | 9/16 | 0/16 | 2/16 |
| W wrong diagnostic | 2 | 36/72 | 14/48 | 22/24 | 12/16 | 0/16 | 2/16 |
| W wrong diagnostic | 3 | 37/72 | 15/48 | 22/24 | 9/16 | 3/16 | 3/16 |

## Paired differences per repository (percentage points; 95% interval by resampling repositories, then by resampling whole families)

| Contrast | Group | Difference | Repositories | Families | Better / same / worse |
|---|---|---|---|---|---|
| D experience + bank minus A unchanged | all | +31.5 | +16.7 to +45.8 | +5.6 to +58.3 | 36 / 28 / 8 |
| D experience + bank minus A unchanged | not repeats (G2+G3+G4) | +6.2 | -10.4 to +22.9 | -27.8 to +36.8 | 14 / 26 / 8 |
| D experience + bank minus A unchanged | G1 | +81.9 | +68.1 to +93.1 | +62.5 to +97.2 | 22 / 2 / 0 |
| D experience + bank minus A unchanged | G2 | +47.9 | +25.0 to +70.8 | +0.0 to +95.8 | 8 / 8 / 0 |
| D experience + bank minus A unchanged | G3 | -18.8 | -41.7 to +2.1 | -68.8 to +12.5 | 1 / 11 / 4 |
| D experience + bank minus A unchanged | G4 | -10.4 | -39.6 to +16.7 | -72.9 to +37.5 | 5 / 7 / 4 |
| C experience minus A unchanged | all | +29.2 | +13.9 to +44.0 | +2.7 to +55.4 | 35 / 27 / 10 |
| C experience minus A unchanged | not repeats (G2+G3+G4) | -0.0 | -16.7 to +16.0 | -34.0 to +29.9 | 13 / 25 / 10 |
| C experience minus A unchanged | G1 | +87.5 | +75.0 to +97.2 | +69.4 to +100.0 | 22 / 2 / 0 |
| C experience minus A unchanged | G2 | +37.5 | +12.5 to +62.5 | -8.3 to +83.3 | 9 / 5 / 2 |
| C experience minus A unchanged | G3 | -18.8 | -43.8 to +4.2 | -75.0 to +18.8 | 2 / 10 / 4 |
| C experience minus A unchanged | G4 | -18.8 | -43.8 to +4.2 | -75.0 to +18.8 | 2 / 10 / 4 |
| B final patches minus A unchanged | all | +27.3 | +13.9 to +40.7 | +4.3 to +54.5 | 26 / 38 / 8 |
| B final patches minus A unchanged | not repeats (G2+G3+G4) | -4.9 | -16.7 to +7.6 | -28.5 to +19.4 | 4 / 36 / 8 |
| B final patches minus A unchanged | G1 | +91.7 | +79.2 to +100.0 | +75.0 to +100.0 | 22 / 2 / 0 |
| B final patches minus A unchanged | G2 | +25.0 | +6.2 to +50.0 | +0.0 to +75.0 | 4 / 12 / 0 |
| B final patches minus A unchanged | G3 | -16.7 | -33.3 to -4.2 | -50.0 to +0.0 | 0 / 12 / 4 |
| B final patches minus A unchanged | G4 | -22.9 | -43.8 to -6.2 | -68.8 to +0.0 | 0 / 12 / 4 |
| D experience + bank minus B final patches | all | +4.2 | -2.8 to +11.6 | -6.9 to +17.1 | 10 / 53 / 9 |
| D experience + bank minus B final patches | not repeats (G2+G3+G4) | +11.1 | +2.8 to +20.8 | -3.5 to +29.2 | 10 / 34 / 4 |
| D experience + bank minus B final patches | G1 | -9.7 | -18.1 to -2.8 | -22.2 to +0.0 | 0 / 19 / 5 |
| D experience + bank minus B final patches | G2 | +22.9 | +6.2 to +43.8 | +0.0 to +68.8 | 4 / 12 / 0 |
| D experience + bank minus B final patches | G3 | -2.1 | -12.5 to +10.4 | -18.8 to +12.5 | 1 / 12 / 3 |
| D experience + bank minus B final patches | G4 | +12.5 | +0.0 to +25.0 | -4.2 to +37.5 | 5 / 10 / 1 |
| C experience minus B final patches | all | +1.9 | -5.1 to +9.3 | -9.4 to +16.2 | 9 / 49 / 14 |
| C experience minus B final patches | not repeats (G2+G3+G4) | +4.9 | -5.6 to +16.0 | -12.5 to +25.7 | 9 / 28 / 11 |
| C experience minus B final patches | G1 | -4.2 | -8.3 to +0.0 | -9.8 to +0.0 | 0 / 21 / 3 |
| C experience minus B final patches | G2 | +12.5 | -12.5 to +41.7 | -29.2 to +68.8 | 5 / 5 / 6 |
| C experience minus B final patches | G3 | -2.1 | -12.5 to +10.4 | -25.0 to +18.8 | 2 / 10 / 4 |
| C experience minus B final patches | G4 | +4.2 | -4.2 to +14.6 | -6.2 to +18.8 | 2 / 13 / 1 |
| D experience + bank minus F bank disabled | all | +2.3 | -2.3 to +6.9 | -2.0 to +6.8 | 11 / 54 / 7 |
| D experience + bank minus F bank disabled | not repeats (G2+G3+G4) | +4.2 | -2.1 to +10.4 | -0.7 to +9.7 | 10 / 33 / 5 |
| D experience + bank minus F bank disabled | G1 | -1.4 | -6.9 to +2.8 | -8.3 to +4.2 | 1 / 21 / 2 |
| D experience + bank minus F bank disabled | G2 | +12.5 | +4.2 to +20.8 | +4.2 to +20.8 | 6 / 10 / 0 |
| D experience + bank minus F bank disabled | G3 | -2.1 | -14.6 to +10.4 | -6.2 to +0.0 | 1 / 13 / 2 |
| D experience + bank minus F bank disabled | G4 | +2.1 | -10.4 to +14.6 | -6.2 to +12.5 | 3 / 10 / 3 |
| D experience + bank minus E experience + nearest example | all | +2.3 | -1.9 to +6.5 | -2.8 to +7.7 | 11 / 54 / 7 |
| D experience + bank minus E experience + nearest example | not repeats (G2+G3+G4) | +4.2 | -1.4 to +9.7 | -2.8 to +11.1 | 10 / 33 / 5 |
| D experience + bank minus E experience + nearest example | G1 | -1.4 | -5.6 to +2.8 | -8.3 to +4.2 | 1 / 21 / 2 |
| D experience + bank minus E experience + nearest example | G2 | +12.5 | +4.2 to +20.8 | +0.0 to +25.0 | 6 / 10 / 0 |
| D experience + bank minus E experience + nearest example | G3 | +0.0 | -8.3 to +8.3 | -6.2 to +6.2 | 2 / 12 / 2 |
| D experience + bank minus E experience + nearest example | G4 | +0.0 | -10.4 to +12.5 | -12.5 to +12.5 | 2 / 11 / 3 |
| E experience + nearest example minus F bank disabled | all | +0.0 | -3.7 to +3.7 | -3.2 to +3.4 | 8 / 56 / 8 |
| E experience + nearest example minus F bank disabled | not repeats (G2+G3+G4) | +0.0 | -4.9 to +4.9 | -4.2 to +4.9 | 7 / 34 / 7 |
| E experience + nearest example minus F bank disabled | G1 | +0.0 | -4.2 to +4.2 | -4.2 to +4.2 | 1 / 22 / 1 |
| E experience + nearest example minus F bank disabled | G2 | +0.0 | -10.4 to +10.4 | -8.3 to +10.4 | 3 / 10 / 3 |
| E experience + nearest example minus F bank disabled | G3 | -2.1 | -8.3 to +4.2 | -6.2 to +0.0 | 1 / 13 / 2 |
| E experience + nearest example minus F bank disabled | G4 | +2.1 | -6.2 to +10.4 | -6.2 to +12.5 | 3 / 11 / 2 |
| W wrong diagnostic minus F bank disabled | all | +0.0 | -4.2 to +4.2 | -3.1 to +3.2 | 9 / 53 / 10 |
| W wrong diagnostic minus F bank disabled | not repeats (G2+G3+G4) | +0.7 | -5.6 to +6.9 | -3.5 to +4.9 | 9 / 30 / 9 |
| W wrong diagnostic minus F bank disabled | G1 | -1.4 | -4.2 to +0.0 | -4.2 to +0.0 | 0 / 23 / 1 |
| W wrong diagnostic minus F bank disabled | G2 | +2.1 | -6.2 to +10.4 | +0.0 to +6.2 | 3 / 11 / 2 |
| W wrong diagnostic minus F bank disabled | G3 | -2.1 | -10.4 to +6.2 | -12.5 to +6.2 | 2 / 11 / 3 |
| W wrong diagnostic minus F bank disabled | G4 | +2.1 | -10.4 to +16.7 | -6.2 to +12.5 | 4 / 8 / 4 |
| D experience + bank minus D1 bank, version 1 only | all | +1.9 | -0.9 to +5.1 | -1.9 to +6.1 | 6 / 63 / 3 |
| D experience + bank minus D1 bank, version 1 only | not repeats (G2+G3+G4) | +2.8 | -1.4 to +7.6 | -2.8 to +9.0 | 6 / 39 / 3 |
| D experience + bank minus D1 bank, version 1 only | G1 | +0.0 | +0.0 to +0.0 | +0.0 to +0.0 | 0 / 24 / 0 |
| D experience + bank minus D1 bank, version 1 only | G2 | +6.2 | +0.0 to +12.5 | +0.0 to +18.8 | 3 / 13 / 0 |
| D experience + bank minus D1 bank, version 1 only | G3 | -4.2 | -12.5 to +4.2 | -12.5 to +0.0 | 1 / 12 / 3 |
| D experience + bank minus D1 bank, version 1 only | G4 | +6.2 | +0.0 to +16.7 | +0.0 to +18.8 | 2 / 14 / 0 |
| D experience + bank minus W wrong diagnostic | all | +2.3 | -2.3 to +6.9 | -2.3 to +7.1 | 11 / 53 / 8 |
| D experience + bank minus W wrong diagnostic | not repeats (G2+G3+G4) | +3.5 | -2.8 to +9.7 | -2.8 to +9.7 | 9 / 33 / 6 |
| D experience + bank minus W wrong diagnostic | G1 | +0.0 | -5.6 to +5.6 | -6.9 to +5.6 | 2 / 20 / 2 |
| D experience + bank minus W wrong diagnostic | G2 | +10.4 | +4.2 to +18.8 | +0.0 to +20.8 | 5 / 11 / 0 |
| D experience + bank minus W wrong diagnostic | G3 | +0.0 | -10.4 to +12.5 | -6.2 to +6.2 | 2 / 11 / 3 |
| D experience + bank minus W wrong diagnostic | G4 | +0.0 | -10.4 to +12.5 | -12.5 to +12.5 | 2 / 11 / 3 |
| F bank disabled minus A unchanged | all | +29.2 | +15.3 to +42.6 | +5.0 to +53.2 | 36 / 27 / 9 |
| F bank disabled minus A unchanged | not repeats (G2+G3+G4) | +2.1 | -12.5 to +16.7 | -27.1 to +29.2 | 14 / 25 / 9 |
| F bank disabled minus A unchanged | G1 | +83.3 | +69.4 to +94.4 | +63.9 to +98.6 | 22 / 2 / 0 |
| F bank disabled minus A unchanged | G2 | +35.4 | +14.6 to +56.2 | -4.2 to +75.0 | 8 / 7 / 1 |
| F bank disabled minus A unchanged | G3 | -16.7 | -39.6 to +6.2 | -68.8 to +18.8 | 2 / 10 / 4 |
| F bank disabled minus A unchanged | G4 | -12.5 | -37.5 to +10.4 | -66.7 to +25.0 | 4 / 8 / 4 |
| AD unchanged + bank minus A unchanged | all | +0.0 | -4.2 to +4.2 | -4.0 to +4.2 | 1 / 70 / 1 |
| AD unchanged + bank minus A unchanged | not repeats (G2+G3+G4) | -2.1 | -6.2 to +0.0 | -6.2 to +0.0 | 0 / 47 / 1 |
| AD unchanged + bank minus A unchanged | G1 | +4.2 | +0.0 to +12.5 | +0.0 to +12.5 | 1 / 23 / 0 |
| AD unchanged + bank minus A unchanged | G2 | +0.0 | +0.0 to +0.0 | +0.0 to +0.0 | 0 / 16 / 0 |
| AD unchanged + bank minus A unchanged | G3 | -6.2 | -18.8 to +0.0 | -18.8 to +0.0 | 0 / 15 / 1 |
| AD unchanged + bank minus A unchanged | G4 | +0.0 | +0.0 to +0.0 | +0.0 to +0.0 | 0 / 16 / 0 |
| AE unchanged + nearest example minus A unchanged | all | -11.1 | -22.2 to +0.0 | -29.0 to +6.2 | 4 / 56 / 12 |
| AE unchanged + nearest example minus A unchanged | not repeats (G2+G3+G4) | -20.8 | -33.3 to -10.4 | -43.8 to +0.0 | 0 / 38 / 10 |
| AE unchanged + nearest example minus A unchanged | G1 | +8.3 | -12.5 to +29.2 | -16.7 to +33.3 | 4 / 18 / 2 |
| AE unchanged + nearest example minus A unchanged | G2 | -25.0 | -50.0 to -6.2 | -75.0 to +0.0 | 0 / 12 / 4 |
| AE unchanged + nearest example minus A unchanged | G3 | -18.8 | -37.5 to +0.0 | -56.2 to +0.0 | 0 / 13 / 3 |
| AE unchanged + nearest example minus A unchanged | G4 | -18.8 | -37.5 to +0.0 | -56.2 to +0.0 | 0 / 13 / 3 |

## Regressions, tests and cost (all repositories; mean over seeds)

| Arm | Repositories with a hidden test broken by the patch | Patch applied | Tests well formed | Predictions that matched execution | Visible tests pass but hidden fail | Seconds of generation per repository | New tokens per repository | Generation seconds per correct fix |
|---|---|---|---|---|---|---|---|---|
| A unchanged | 5.6% | 84.7% | 98.6% | 11.8% | 0.0% | 5.1 | 303 | 26.2 |
| AD unchanged + bank | 1.4% | 86.1% | 98.6% | 11.1% | 0.0% | 5.7 | 320 | 29.2 |
| AE unchanged + nearest example | 1.4% | 16.7% | 100.0% | 4.9% | 0.0% | 4.8 | 235 | 58.0 |
| B final patches | 14.8% | 99.1% | 86.3% | 7.4% | 1.4% | 5.2 | 219 | 11.1 |
| C experience | 23.6% | 98.1% | 100.0% | 44.7% | 2.8% | 5.2 | 252 | 10.6 |
| D experience + bank | 23.6% | 100.0% | 99.8% | 35.0% | 1.4% | 5.7 | 253 | 11.2 |
| D1 bank, version 1 only | 23.6% | 99.5% | 100.0% | 37.0% | 3.2% | 5.5 | 252 | 11.1 |
| E experience + nearest example | 22.2% | 97.7% | 100.0% | 40.3% | 3.7% | 5.8 | 252 | 12.0 |
| F bank disabled | 24.1% | 99.5% | 100.0% | 39.6% | 2.3% | 5.2 | 253 | 10.7 |
| W wrong diagnostic | 20.8% | 99.1% | 100.0% | 34.3% | 2.3% | 5.6 | 251 | 11.6 |

## Regressions by group (% of repositories where the patch broke a hidden test that passed before)

| Arm | all | not repeats (G2+G3+G4) | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|
| A unchanged | 5.6 | 2.1 | 12.5 | 6.2 | 0.0 | 0.0 |
| AD unchanged + bank | 1.4 | 0.0 | 4.2 | 0.0 | 0.0 | 0.0 |
| AE unchanged + nearest example | 1.4 | 0.0 | 4.2 | 0.0 | 0.0 | 0.0 |
| B final patches | 14.8 | 22.2 | 0.0 | 39.6 | 16.7 | 10.4 |
| C experience | 23.6 | 35.4 | 0.0 | 18.8 | 70.8 | 16.7 |
| D experience + bank | 23.6 | 34.7 | 1.4 | 10.4 | 77.1 | 16.7 |
| D1 bank, version 1 only | 23.6 | 34.7 | 1.4 | 18.8 | 70.8 | 14.6 |
| E experience + nearest example | 22.2 | 32.6 | 1.4 | 16.7 | 64.6 | 16.7 |
| F bank disabled | 24.1 | 35.4 | 1.4 | 22.9 | 60.4 | 22.9 |
| W wrong diagnostic | 20.8 | 30.6 | 1.4 | 18.8 | 56.2 | 16.7 |

## Repositories where the trained fix does not belong (26): share where the submitted patch fails exactly as the trained fix does

| Arm | Lookalikes (G3) | Other groups |
|---|---|---|
| A unchanged | 25.0% | 0.0% |
| AD unchanged + bank | 25.0% | 10.0% |
| AE unchanged + nearest example | 0.0% | 0.0% |
| B final patches | 18.7% | 33.3% |
| C experience | 37.5% | 0.0% |
| D experience + bank | 58.3% | 6.7% |
| D1 bank, version 1 only | 50.0% | 13.3% |
| E experience + nearest example | 29.2% | 3.3% |
| F bank disabled | 39.6% | 3.3% |
| W wrong diagnostic | 37.5% | 3.3% |

## After a contradiction: episodes in which at least one test did not come out as predicted

| Arm | Episodes with a contradiction | First patch correct after a contradiction | First patch correct with no contradiction |
|---|---|---|---|
| A unchanged | 65 of 72 | 18.5% | 28.6% |
| AD unchanged + bank | 65 of 72 | 21.5% | 0.0% |
| AE unchanged + nearest example | 70 of 72 | 5.7% | 100.0% |
| B final patches | 205 of 216 | 46.8% | 45.5% |
| C experience | 151 of 216 | 35.1% | 80.0% |
| D experience + bank | 162 of 216 | 39.5% | 85.2% |
| D1 bank, version 1 only | 161 of 216 | 37.9% | 81.8% |
| E experience + nearest example | 161 of 216 | 40.4% | 72.7% |
| F bank disabled | 158 of 216 | 36.1% | 82.8% |
| W wrong diagnostic | 168 of 216 | 36.9% | 89.6% |

## AD unchanged + bank: correctness by repeated use, status and diagnostic

| Split | Value | Episodes | First patch correct |
|---|---|---|---|
| by diagnostic | S1 | 27 | 25.9% |
| by diagnostic | S2 | 23 | 0.0% |
| by diagnostic | S3 | 22 | 31.8% |
| by status at the patch | reopened | 65 | 21.5% |
| by status at the patch | supported | 7 | 0.0% |
| by use | use 1-5 | 15 | 26.7% |
| by use | use 16+ | 27 | 11.1% |
| by use | use 6-15 | 30 | 23.3% |

## D experience + bank: correctness by repeated use, status and diagnostic

| Split | Value | Episodes | First patch correct |
|---|---|---|---|
| by diagnostic | S1 | 81 | 35.8% |
| by diagnostic | S2 | 69 | 59.4% |
| by diagnostic | S3 | 66 | 60.6% |
| by status at the patch | reopened | 162 | 39.5% |
| by status at the patch | supported | 54 | 85.2% |
| by use | use 1-5 | 45 | 55.6% |
| by use | use 16+ | 81 | 49.4% |
| by use | use 6-15 | 90 | 50.0% |

## D1 bank, version 1 only: correctness by repeated use, status and diagnostic

| Split | Value | Episodes | First patch correct |
|---|---|---|---|
| by diagnostic | S1 | 81 | 34.6% |
| by diagnostic | S2 | 69 | 55.1% |
| by diagnostic | S3 | 66 | 60.6% |
| by status at the patch | reopened | 161 | 37.9% |
| by status at the patch | supported | 55 | 81.8% |
| by use | use 1-5 | 45 | 53.3% |
| by use | use 16+ | 81 | 49.4% |
| by use | use 6-15 | 90 | 46.7% |

## W wrong diagnostic: correctness by repeated use, status and diagnostic

| Split | Value | Episodes | First patch correct |
|---|---|---|---|
| by diagnostic | S1 | 66 | 57.6% |
| by diagnostic | S2 | 81 | 35.8% |
| by diagnostic | S3 | 69 | 55.1% |
| by status at the patch | reopened | 168 | 36.9% |
| by status at the patch | supported | 48 | 89.6% |
| by use | use 1-5 | 45 | 51.1% |
| by use | use 16+ | 81 | 46.9% |
| by use | use 6-15 | 90 | 48.9% |

## Frozen rules (docs/v07_protocol.md)

| Rule | What it says | Measured | Result |
|---|---|---|---|
| P1 | experience helps on unfamiliar repositories: D minus A at least +10 points on repositories that are not repeats, interval (repositories) above 0 | +6.2 (-10.4 to +22.9); better 14, worse 8 | **FAIL** |
| R1 | recognition: D minus A at least +10 points on renamed repeats, interval above 0 | +81.9 (+68.1 to +93.1); better 22, worse 0 | **PASS** |
| S1 | verified experience beats final patches: C minus B at least +5 points on repositories that are not repeats, interval above 0 | +4.9 (-5.6 to +16.0); better 9, worse 11 | **FAIL** |
| S2 | the bank adds to the same student: D minus F at least +5 points on repositories that are not repeats, and better on more repositories than worse | +4.2 (-2.1 to +10.4); better 10, worse 5 | **FAIL** |
| S3 | the bank beats ordinary retrieval: D minus E at least +5 points on repositories that are not repeats, and better on more than worse | +4.2 (-1.4 to +9.7); better 10, worse 5 | **FAIL** |
| S4 | the content of the diagnostic matters: D minus W (wrong diagnostic) at least +5 points on repositories that are not repeats, and better on more than worse | +3.5 (-2.8 to +9.7); better 9, worse 6 | **FAIL** |
| P2 | no excess of regressions: share of repositories that are not repeats where D's patch breaks a hidden test is at most 10 points above A's | D 34.72%, A 2.08% | **FAIL** |
| S5 | the old fix is not carried onto lookalikes: share of lookalikes where D's patch breaks a hidden test is at most 10 points above A's | D 77.08%, A 0.0% | **FAIL** |

**Verdict by the frozen rules: RECOGNITION RESULT: the gain is confined to repeats**

## Per repository (first patch correct in how many seeds)

| Repository | Group | Family | A | AD | AE | B | C | D | D1 | E | F | W |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev_000 | G3 | look_split_window | 1/1 | 1/1 | 0/1 | 1/3 | 0/3 | 0/3 | 1/3 | 0/3 | 0/3 | 1/3 |
| dev_001 | G3 | look_default_seen | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 | 1/3 | 0/3 |
| dev_002 | G2 | stale_peak | 0/1 | 0/1 | 0/1 | 0/3 | 3/3 | 2/3 | 1/3 | 2/3 | 2/3 | 2/3 |
| dev_003 | G4 | int_division | 1/1 | 1/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_004 | G3 | look_default_seen | 0/1 | 0/1 | 0/1 | 0/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_005 | G1 | flush_last | 0/1 | 1/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_006 | G1 | iter_shares | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_007 | G1 | bound_range | 1/1 | 1/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_008 | G1 | bound_pages | 0/1 | 0/1 | 1/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_009 | G2 | iter_attr | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_010 | G4 | float_equal | 0/1 | 0/1 | 0/1 | 0/3 | 1/3 | 2/3 | 2/3 | 2/3 | 1/3 | 0/3 |
| dev_011 | G4 | float_equal | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 2/3 | 0/3 | 0/3 | 0/3 | 1/3 |
| dev_012 | G3 | look_shared_entries | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_013 | G2 | stale_peak | 0/1 | 0/1 | 0/1 | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 | 3/3 |
| dev_014 | G2 | stale_peak | 0/1 | 0/1 | 0/1 | 0/3 | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 | 2/3 |
| dev_015 | G1 | stale_index | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_016 | G1 | stale_rates | 0/1 | 0/1 | 0/1 | 3/3 | 2/3 | 2/3 | 2/3 | 3/3 | 3/3 | 3/3 |
| dev_017 | G4 | float_equal | 0/1 | 0/1 | 0/1 | 0/3 | 2/3 | 1/3 | 1/3 | 2/3 | 2/3 | 1/3 |
| dev_018 | G2 | bound_lower | 1/1 | 1/1 | 0/1 | 3/3 | 1/3 | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 |
| dev_019 | G1 | iter_shares | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_020 | G2 | stale_remove | 0/1 | 0/1 | 0/1 | 3/3 | 2/3 | 3/3 | 3/3 | 2/3 | 2/3 | 2/3 |
| dev_021 | G2 | bound_lower | 1/1 | 1/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 | 3/3 |
| dev_022 | G1 | flush_last | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_023 | G1 | bound_range | 1/1 | 1/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_024 | G2 | stale_remove | 0/1 | 0/1 | 0/1 | 3/3 | 2/3 | 3/3 | 3/3 | 2/3 | 2/3 | 2/3 |
| dev_025 | G2 | stale_remove | 0/1 | 0/1 | 0/1 | 3/3 | 2/3 | 3/3 | 3/3 | 2/3 | 3/3 | 2/3 |
| dev_026 | G4 | sort_text_numbers | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_027 | G1 | bound_pages | 0/1 | 0/1 | 1/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_028 | G2 | stale_remove | 0/1 | 0/1 | 0/1 | 3/3 | 2/3 | 3/3 | 3/3 | 2/3 | 2/3 | 3/3 |
| dev_029 | G3 | look_shared_entries | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_030 | G4 | sort_text_numbers | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_031 | G1 | stale_index | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_032 | G4 | sort_text_numbers | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_033 | G4 | sort_text_numbers | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_034 | G4 | int_division | 1/1 | 1/1 | 0/1 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_035 | G4 | float_equal | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 1/3 | 0/3 | 0/3 | 1/3 | 2/3 |
| dev_036 | G1 | bound_loop | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_037 | G1 | stale_total | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 |
| dev_038 | G3 | look_split_window | 1/1 | 1/1 | 1/1 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 |
| dev_039 | G4 | case_key | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_040 | G3 | look_labels | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_041 | G3 | look_shared_entries | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_042 | G2 | iter_attr | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_043 | G4 | int_division | 1/1 | 1/1 | 1/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_044 | G3 | look_labels | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_045 | G3 | look_split_window | 1/1 | 1/1 | 0/1 | 1/3 | 0/3 | 1/3 | 1/3 | 0/3 | 1/3 | 0/3 |
| dev_046 | G2 | bound_lower | 1/1 | 1/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_047 | G3 | look_labels | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_048 | G3 | look_default_seen | 0/1 | 0/1 | 0/1 | 0/3 | 2/3 | 2/3 | 1/3 | 1/3 | 0/3 | 0/3 |
| dev_049 | G1 | lost_write | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 1/3 | 1/3 | 1/3 | 1/3 | 1/3 |
| dev_050 | G4 | int_division | 1/1 | 1/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 | 0/3 |
| dev_051 | G2 | bound_lower | 1/1 | 1/1 | 0/1 | 3/3 | 2/3 | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 |
| dev_052 | G3 | look_split_window | 1/1 | 0/1 | 0/1 | 1/3 | 0/3 | 0/3 | 1/3 | 0/3 | 0/3 | 0/3 |
| dev_053 | G1 | iter_zip | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 |
| dev_054 | G4 | case_key | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 1/3 | 1/3 | 1/3 | 0/3 | 2/3 |
| dev_055 | G2 | stale_peak | 0/1 | 0/1 | 0/1 | 0/3 | 3/3 | 3/3 | 2/3 | 3/3 | 2/3 | 2/3 |
| dev_056 | G4 | case_key | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 | 1/3 | 0/3 |
| dev_057 | G1 | lost_write | 0/1 | 0/1 | 0/1 | 3/3 | 2/3 | 1/3 | 1/3 | 1/3 | 1/3 | 1/3 |
| dev_058 | G1 | iter_window | 0/1 | 0/1 | 1/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_059 | G2 | iter_attr | 0/1 | 0/1 | 0/1 | 0/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_060 | G4 | case_key | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 | 0/3 | 1/3 |
| dev_061 | G1 | iter_window | 0/1 | 0/1 | 1/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_062 | G1 | iter_zip | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 2/3 | 2/3 | 2/3 | 2/3 | 2/3 |
| dev_063 | G2 | iter_attr | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_064 | G1 | mut_drain | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 | 2/3 |
| dev_065 | G3 | look_shared_entries | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_066 | G1 | stale_rates | 0/1 | 0/1 | 0/1 | 3/3 | 2/3 | 2/3 | 2/3 | 3/3 | 3/3 | 3/3 |
| dev_067 | G1 | stale_total | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_068 | G1 | mut_drain | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_069 | G3 | look_labels | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| dev_070 | G1 | bound_loop | 0/1 | 0/1 | 0/1 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| dev_071 | G3 | look_default_seen | 0/1 | 0/1 | 0/1 | 0/3 | 0/3 | 0/3 | 1/3 | 1/3 | 2/3 | 1/3 |
