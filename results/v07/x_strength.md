# v0.7: the trained adapters at reduced strength

The adapter's contribution is multiplied by the strength in every layer: 0 is the unchanged student, 1 the adapter as trained. 72 development repositories.
0.5 was tried first, on the D-family adapter. The other adapters at 0.5, and 0.25 and 0.75, were run afterwards as controls. Only 0.5 is carried to the final set.

## First patch correct (% of repositories)

| Adapter | Strength | Insert | Seeds | all | unfamiliar | renamed repeats | changed preconditions | lookalikes | absent mechanisms |
|---|---|---|---|---|---|---|---|---|---|
| none (unchanged student, A) | 0 | none | 1 | 19.4 | 25.0 | 8.3 | 25.0 | 25.0 | 25.0 |
| experience (C) | 0.5 | none | 3 | 36.1 | 31.9 | 44.4 | 31.2 | 37.5 | 27.1 |
| experience (C) | 1 | none | 3 | 48.6 | 25.0 | 95.8 | 62.5 | 6.2 | 6.2 |
| experience, D-family | 0.25 | none | 3 | 32.4 | 36.1 | 25.0 | 27.1 | 33.3 | 47.9 |
| experience, D-family | 0.5 | bank | 3 | 45.4 | 31.9 | 72.2 | 52.1 | 22.9 | 20.8 |
| experience, D-family | 0.5 | none | 3 | 41.2 | 38.2 | 47.2 | 39.6 | 45.8 | 29.2 |
| experience, D-family | 0.75 | none | 3 | 48.1 | 31.2 | 81.9 | 54.2 | 20.8 | 18.8 |
| experience, D-family | 1 | bank | 3 | 50.9 | 31.2 | 90.3 | 72.9 | 6.2 | 14.6 |
| experience, D-family | 1 | none | 3 | 48.6 | 27.1 | 91.7 | 60.4 | 8.3 | 12.5 |
| final patches (B) | 0.5 | none | 3 | 52.8 | 29.9 | 98.6 | 50.0 | 16.7 | 22.9 |
| final patches (B) | 1 | none | 3 | 46.8 | 20.1 | 100.0 | 50.0 | 8.3 | 2.1 |

## Patch broke a hidden test that passed before (% of repositories)

| Adapter | Strength | Insert | Seeds | all | unfamiliar | renamed repeats | changed preconditions | lookalikes | absent mechanisms |
|---|---|---|---|---|---|---|---|---|---|
| none (unchanged student, A) | 0 | none | 1 | 5.6 | 2.1 | 12.5 | 6.2 | 0.0 | 0.0 |
| experience (C) | 0.5 | none | 3 | 14.8 | 19.4 | 5.6 | 12.5 | 31.2 | 14.6 |
| experience (C) | 1 | none | 3 | 23.6 | 35.4 | 0.0 | 18.8 | 70.8 | 16.7 |
| experience, D-family | 0.25 | none | 3 | 4.6 | 5.6 | 2.8 | 10.4 | 6.2 | 0.0 |
| experience, D-family | 0.5 | bank | 3 | 17.1 | 23.6 | 4.2 | 25.0 | 37.5 | 8.3 |
| experience, D-family | 0.5 | none | 3 | 13.9 | 16.7 | 8.3 | 18.8 | 20.8 | 10.4 |
| experience, D-family | 0.75 | none | 3 | 22.2 | 31.9 | 2.8 | 18.8 | 62.5 | 14.6 |
| experience, D-family | 1 | bank | 3 | 23.6 | 34.7 | 1.4 | 10.4 | 77.1 | 16.7 |
| experience, D-family | 1 | none | 3 | 24.1 | 35.4 | 1.4 | 22.9 | 60.4 | 22.9 |
| final patches (B) | 0.5 | none | 3 | 8.8 | 13.2 | 0.0 | 33.3 | 0.0 | 6.2 |
| final patches (B) | 1 | none | 3 | 14.8 | 22.2 | 0.0 | 39.6 | 16.7 | 10.4 |

## Every seed: first-patch successes on the 48 unfamiliar repositories

| Adapter | Strength | Insert | seed 1 | seed 2 | seed 3 |
|---|---|---|---|---|---|
| none (A) | 0 | none | 12 (one run) | | |
| experience (C) | 0.5 | none | 14 | 12 | 20 |
| experience (C) | 1 | none | 14 | 13 | 9 |
| experience, D-family | 0.25 | none | 19 | 16 | 17 |
| experience, D-family | 0.5 | bank | 15 | 12 | 19 |
| experience, D-family | 0.5 | none | 16 | 16 | 23 |
| experience, D-family | 0.75 | none | 13 | 13 | 19 |
| experience, D-family | 1 | bank | 13 | 13 | 19 |
| experience, D-family | 1 | none | 14 | 12 | 13 |
| final patches (B) | 0.5 | none | 12 | 17 | 14 |
| final patches (B) | 1 | none | 8 | 13 | 8 |
