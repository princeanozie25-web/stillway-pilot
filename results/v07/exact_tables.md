# v0.7 results: exact

120 repositories. Arms and seeds: A unchanged (1 seed); B final patches (1 seed); C experience (1 seed); D experience + bank (1 seed); F bank disabled (1 seed).

## First submitted patch passes hidden grading (% of repositories; mean over seeds)

| Arm | all (n=120) | EX (n=120) |
|---|---|---|
| A unchanged | 12.5 | 12.5 |
| B final patches | 100.0 | 100.0 |
| C experience | 93.3 | 93.3 |
| D experience + bank | 86.7 | 86.7 |
| F bank disabled | 90.0 | 90.0 |

## Every seed

| Arm | Seed | all | EX |
|---|---|---|---|
| A unchanged | 0 | 15/120 | 15/120 |
| B final patches | 1 | 120/120 | 120/120 |
| C experience | 1 | 112/120 | 112/120 |
| D experience + bank | 1 | 104/120 | 104/120 |
| F bank disabled | 1 | 108/120 | 108/120 |

## Paired differences per repository (percentage points; 95% interval by resampling repositories, then by resampling whole families)

| Contrast | Group | Difference | Repositories | Families | Better / same / worse |
|---|---|---|---|---|---|
| D experience + bank minus A unchanged | all | +74.2 | +66.7 to +81.7 | +51.7 to +93.3 | 89 / 31 / 0 |
| D experience + bank minus A unchanged | EX | +74.2 | +65.8 to +81.7 | +50.8 to +93.3 | 89 / 31 / 0 |
| C experience minus A unchanged | all | +80.8 | +73.3 to +87.5 | +60.0 to +97.5 | 97 / 23 / 0 |
| C experience minus A unchanged | EX | +80.8 | +73.3 to +87.5 | +60.0 to +97.5 | 97 / 23 / 0 |
| B final patches minus A unchanged | all | +87.5 | +81.7 to +93.3 | +69.2 to +99.2 | 105 / 15 / 0 |
| B final patches minus A unchanged | EX | +87.5 | +81.7 to +93.3 | +70.8 to +99.2 | 105 / 15 / 0 |
| D experience + bank minus B final patches | all | -13.3 | -20.0 to -7.5 | -33.3 to +0.0 | 0 / 104 / 16 |
| D experience + bank minus B final patches | EX | -13.3 | -20.0 to -7.5 | -31.7 to +0.0 | 0 / 104 / 16 |
| C experience minus B final patches | all | -6.7 | -11.7 to -2.5 | -20.0 to +0.0 | 0 / 112 / 8 |
| C experience minus B final patches | EX | -6.7 | -11.7 to -2.5 | -20.0 to +0.0 | 0 / 112 / 8 |
| D experience + bank minus F bank disabled | all | -3.3 | -8.3 to +0.8 | -15.0 to +5.0 | 2 / 112 / 6 |
| D experience + bank minus F bank disabled | EX | -3.3 | -8.3 to +0.8 | -15.0 to +5.0 | 2 / 112 / 6 |
| F bank disabled minus A unchanged | all | +77.5 | +70.0 to +85.0 | +55.0 to +95.0 | 93 / 27 / 0 |
| F bank disabled minus A unchanged | EX | +77.5 | +70.0 to +85.0 | +55.0 to +95.8 | 93 / 27 / 0 |

## Regressions, tests and cost (all repositories; mean over seeds)

| Arm | Repositories with a hidden test broken by the patch | Patch applied | Tests well formed | Predictions that matched execution | Visible tests pass but hidden fail | Seconds of generation per repository | New tokens per repository | Generation seconds per correct fix |
|---|---|---|---|---|---|---|---|---|
| A unchanged | 4.2% | 98.3% | 100.0% | 17.1% | 2.5% | 5.0 | 280 | 40.2 |
| B final patches | 0.0% | 100.0% | 90.0% | 10.8% | 0.0% | 4.6 | 189 | 4.6 |
| C experience | 0.0% | 100.0% | 100.0% | 78.3% | 0.0% | 5.1 | 240 | 5.4 |
| D experience + bank | 4.2% | 100.0% | 100.0% | 76.2% | 0.0% | 5.5 | 242 | 6.4 |
| F bank disabled | 0.8% | 100.0% | 99.6% | 72.1% | 0.0% | 5.0 | 239 | 5.6 |

## Regressions by group (% of repositories where the patch broke a hidden test that passed before)

| Arm | all | EX |
|---|---|---|
| A unchanged | 4.2 | 4.2 |
| B final patches | 0.0 | 0.0 |
| C experience | 0.0 | 0.0 |
| D experience + bank | 4.2 | 4.2 |
| F bank disabled | 0.8 | 0.8 |

## Repositories where the trained fix does not belong (30): share where the submitted patch fails exactly as the trained fix does

| Arm | Lookalikes (G3) | Other groups |
|---|---|---|
| A unchanged | nan% | 0.0% |
| B final patches | nan% | 0.0% |
| C experience | nan% | 0.0% |
| D experience + bank | nan% | 16.7% |
| F bank disabled | nan% | 0.0% |

## After a contradiction: episodes in which at least one test did not come out as predicted

| Arm | Episodes with a contradiction | First patch correct after a contradiction | First patch correct with no contradiction |
|---|---|---|---|
| A unchanged | 103 of 120 | 7.8% | 41.2% |
| B final patches | 110 of 120 | 100.0% | 100.0% |
| C experience | 36 of 120 | 77.8% | 100.0% |
| D experience + bank | 37 of 120 | 56.8% | 100.0% |
| F bank disabled | 46 of 120 | 76.1% | 98.6% |

## D experience + bank: correctness by repeated use, status and diagnostic

| Split | Value | Episodes | First patch correct |
|---|---|---|---|
| by diagnostic | S1 | 40 | 100.0% |
| by diagnostic | S2 | 40 | 60.0% |
| by diagnostic | S3 | 40 | 100.0% |
| by status at the patch | reopened | 37 | 56.8% |
| by status at the patch | supported | 83 | 100.0% |
| by use | use 1-5 | 15 | 66.7% |
| by use | use 16+ | 75 | 92.0% |
| by use | use 6-15 | 30 | 83.3% |

## Frozen rules (docs/v07_protocol.md)

| Rule | What it says | Measured | Result |
|---|---|---|---|
| P1 | experience helps on unfamiliar repositories: D minus A at least +10 points on repositories that are not repeats, interval (repositories) above 0 |  | **not computable (an arm or group is missing)** |
| R1 | recognition: D minus A at least +10 points on renamed repeats, interval above 0 |  | **not computable (an arm or group is missing)** |
| S1 | verified experience beats final patches: C minus B at least +5 points on repositories that are not repeats, interval above 0 |  | **not computable (an arm or group is missing)** |
| S2 | the bank adds to the same student: D minus F at least +5 points on repositories that are not repeats, and better on more repositories than worse |  | **not computable (an arm or group is missing)** |
| S3 | the bank beats ordinary retrieval: D minus E at least +5 points on repositories that are not repeats, and better on more than worse |  | **not computable (an arm or group is missing)** |
| S4 | the content of the diagnostic matters: D minus W (wrong diagnostic) at least +5 points on repositories that are not repeats, and better on more than worse |  | **not computable (an arm or group is missing)** |
| P2 | no excess of regressions: share of repositories that are not repeats where D's patch breaks a hidden test is at most 10 points above A's |  | **not computable** |
| S5 | the old fix is not carried onto lookalikes: share of lookalikes where D's patch breaks a hidden test is at most 10 points above A's |  | **not computable** |

**Verdict by the frozen rules: not computable**

## Per repository (first patch correct in how many seeds)

| Repository | Group | Family | A | B | C | D | F |
|---|---|---|---|---|---|---|---|
| bound_loop__grades | EX | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__invoices | EX | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__orders | EX | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__parcels | EX | bound_loop | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__readings | EX | bound_loop | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__samples | EX | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__shipments | EX | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__tickets | EX | bound_loop | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__trades | EX | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_loop__visits | EX | bound_loop | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__grades | EX | bound_pages | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__invoices | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__orders | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__parcels | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__readings | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__samples | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__shipments | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__tickets | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__trades | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_pages__visits | EX | bound_pages | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__grades | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__invoices | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__orders | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__parcels | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__readings | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__samples | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__shipments | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__tickets | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__trades | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| bound_range__visits | EX | bound_range | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__grades | EX | flush_last | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__invoices | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__orders | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__parcels | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__readings | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__samples | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__shipments | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__tickets | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__trades | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| flush_last__visits | EX | flush_last | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__grades | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__invoices | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__orders | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__parcels | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__readings | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__samples | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__shipments | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__tickets | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__trades | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_shares__visits | EX | iter_shares | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__grades | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__invoices | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__orders | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__parcels | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__readings | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__samples | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__shipments | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__tickets | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__trades | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_window__visits | EX | iter_window | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__grades | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__invoices | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__orders | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__parcels | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__readings | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__samples | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__shipments | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__tickets | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__trades | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| iter_zip__visits | EX | iter_zip | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| lost_write__grades | EX | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| lost_write__invoices | EX | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| lost_write__orders | EX | lost_write | 0/1 | 1/1 | 1/1 | 0/1 | 0/1 |
| lost_write__parcels | EX | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| lost_write__readings | EX | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| lost_write__samples | EX | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| lost_write__shipments | EX | lost_write | 0/1 | 1/1 | 1/1 | 0/1 | 0/1 |
| lost_write__tickets | EX | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| lost_write__trades | EX | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| lost_write__visits | EX | lost_write | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| mut_drain__grades | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 0/1 |
| mut_drain__invoices | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 0/1 |
| mut_drain__orders | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| mut_drain__parcels | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| mut_drain__readings | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| mut_drain__samples | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| mut_drain__shipments | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| mut_drain__tickets | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| mut_drain__trades | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| mut_drain__visits | EX | mut_drain | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__grades | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__invoices | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__orders | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__parcels | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__readings | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__samples | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__shipments | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__tickets | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__trades | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_index__visits | EX | stale_index | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_rates__grades | EX | stale_rates | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| stale_rates__invoices | EX | stale_rates | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_rates__orders | EX | stale_rates | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| stale_rates__parcels | EX | stale_rates | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_rates__readings | EX | stale_rates | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| stale_rates__samples | EX | stale_rates | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| stale_rates__shipments | EX | stale_rates | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_rates__tickets | EX | stale_rates | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| stale_rates__trades | EX | stale_rates | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_rates__visits | EX | stale_rates | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| stale_total__grades | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__invoices | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__orders | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__parcels | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__readings | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__samples | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__shipments | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__tickets | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__trades | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| stale_total__visits | EX | stale_total | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 |
