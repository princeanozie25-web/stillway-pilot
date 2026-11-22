# v0.7: familiarity gate (added after development; threshold from training data only)

Threshold 0.2245. A repository at or above it goes to the trained student, below it to the unchanged student. One episode either way.

## Where the gate sends repositories

| Group | Repositories | Sent to the trained student | Median similarity to the nearest training repository |
|---|---|---|---|
| all | 72 | 71 | 0.468 |
| not repeats | 48 | 47 | 0.323 |
| G1 | 24 | 24 | 0.671 |
| G2 | 16 | 16 | 0.363 |
| G3 | 16 | 16 | 0.431 |
| G4 | 16 | 15 | 0.294 |

## First patch correct (% of repositories, mean over seeds)

| Arm | all | not repeats | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|
| A unchanged | 19.4 | 25.0 | 8.3 | 25.0 | 25.0 | 25.0 |
| F bank disabled | 48.6 | 27.1 | 91.7 | 60.4 | 8.3 | 12.5 |
| gate + F bank disabled | 48.1 | 26.4 | 91.7 | 60.4 | 8.3 | 10.4 |
| D bank | 50.9 | 31.2 | 90.3 | 72.9 | 6.2 | 14.6 |
| gate + D bank | 50.5 | 30.6 | 90.3 | 72.9 | 6.2 | 12.5 |
| C experience | 48.6 | 25.0 | 95.8 | 62.5 | 6.2 | 6.2 |
| gate + C experience | 48.6 | 25.0 | 95.8 | 62.5 | 6.2 | 6.2 |
| B final patches | 46.8 | 20.1 | 100.0 | 50.0 | 8.3 | 2.1 |
| gate + B final patches | 46.8 | 20.1 | 100.0 | 50.0 | 8.3 | 2.1 |

## Patch broke a hidden test that passed before (% of repositories)

| Arm | all | not repeats | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|
| A unchanged | 5.6 | 2.1 | 12.5 | 6.2 | 0.0 | 0.0 |
| F bank disabled | 24.1 | 35.4 | 1.4 | 22.9 | 60.4 | 22.9 |
| gate + F bank disabled | 23.1 | 34.0 | 1.4 | 22.9 | 60.4 | 18.8 |
| D bank | 23.6 | 34.7 | 1.4 | 10.4 | 77.1 | 16.7 |
| gate + D bank | 23.6 | 34.7 | 1.4 | 10.4 | 77.1 | 16.7 |
| C experience | 23.6 | 35.4 | 0.0 | 18.8 | 70.8 | 16.7 |
| gate + C experience | 23.6 | 35.4 | 0.0 | 18.8 | 70.8 | 16.7 |
| B final patches | 14.8 | 22.2 | 0.0 | 39.6 | 16.7 | 10.4 |
| gate + B final patches | 14.8 | 22.2 | 0.0 | 39.6 | 16.7 | 10.4 |

## Gated arm minus the unchanged student, paired per repository (percentage points; 95% interval by resampling repositories)

| Arm | Group | Difference | Interval | Better / same / worse |
|---|---|---|---|---|
| gate + F bank disabled | all | +28.7 | +14.4 to +42.1 | 35 / 28 / 9 |
| gate + F bank disabled | not repeats | +1.4 | -13.2 to +16.0 | 13 / 26 / 9 |
| gate + F bank disabled | G1 | +83.3 | +69.4 to +94.4 | 22 / 2 / 0 |
| gate + F bank disabled | G2 | +35.4 | +14.6 to +56.2 | 8 / 7 / 1 |
| gate + F bank disabled | G3 | -16.7 | -39.6 to +6.2 | 2 / 10 / 4 |
| gate + F bank disabled | G4 | -14.6 | -39.6 to +8.3 | 3 / 9 / 4 |
| gate + D bank | all | +31.0 | +16.2 to +45.4 | 35 / 29 / 8 |
| gate + D bank | not repeats | +5.6 | -10.4 to +22.2 | 13 / 27 / 8 |
| gate + D bank | G1 | +81.9 | +68.1 to +94.4 | 22 / 2 / 0 |
| gate + D bank | G2 | +47.9 | +25.0 to +72.9 | 8 / 8 / 0 |
| gate + D bank | G3 | -18.8 | -41.7 to +2.1 | 1 / 11 / 4 |
| gate + D bank | G4 | -12.5 | -39.6 to +12.5 | 4 / 8 / 4 |
| gate + C experience | all | +29.2 | +14.3 to +44.0 | 35 / 27 / 10 |
| gate + C experience | not repeats | -0.0 | -16.7 to +16.0 | 13 / 25 / 10 |
| gate + C experience | G1 | +87.5 | +75.0 to +97.2 | 22 / 2 / 0 |
| gate + C experience | G2 | +37.5 | +12.5 to +62.5 | 9 / 5 / 2 |
| gate + C experience | G3 | -18.8 | -43.8 to +4.2 | 2 / 10 / 4 |
| gate + C experience | G4 | -18.8 | -43.8 to +4.2 | 2 / 10 / 4 |
| gate + B final patches | all | +27.3 | +13.0 to +41.7 | 26 / 38 / 8 |
| gate + B final patches | not repeats | -4.9 | -17.4 to +7.6 | 4 / 36 / 8 |
| gate + B final patches | G1 | +91.7 | +79.2 to +100.0 | 22 / 2 / 0 |
| gate + B final patches | G2 | +25.0 | +6.2 to +50.0 | 4 / 12 / 0 |
| gate + B final patches | G3 | -16.7 | -33.3 to -4.2 | 0 / 12 / 4 |
| gate + B final patches | G4 | -22.9 | -43.8 to -6.2 | 0 / 12 / 4 |
