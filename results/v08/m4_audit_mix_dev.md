# Audit mixing, dev

## Generated family, dev (seed 1): 12 local and 6 scattered amendments, 5 seeds

Regression = a budget below 1,600 at which fewer cases are right than by keeping the old table. Shortfall = mean over those budgets of the points below the old table (0 where not below).

| Amendment | Strategy | Runs | Budgets with a regression % | Mean shortfall, points | Shortfall from 64 audits on | Worst cell from 64 audits on, points | Median audits to every case right | Median audits to 99% | Error among answered at 256 audits % |
|---|---|---|---|---|---|---|---|---|
| local | local | 60 | 21.2 | 2.100 | 0.925 | -27.7 | 512 | 256 | 0.12 |
| local | mix 0.1 | 60 | 18.0 | 1.724 | 0.302 | -19.1 | 512 | 256 | 0.19 |
| local | mix 0.2 | 60 | 16.2 | 1.614 | 0.118 | -4.4 | 512 | 256 | 0.15 |
| local | mix 0.3 | 60 | 16.5 | 1.613 | 0.115 | -5.0 | 512 | 256 | 0.12 |
| local | mix 0.5 | 60 | 15.7 | 1.577 | 0.046 | -2.6 | 512 | 256 | 0.18 |
| local | random | 60 | 17.8 | 1.551 | 0.021 | -0.6 | 1600 | 1024 | 0.97 |
| scattered | local | 30 | 24.7 | 1.421 | 0.131 | -3.4 | 1600 | 1312 | 1.61 |
| scattered | mix 0.1 | 30 | 24.0 | 1.434 | 0.127 | -3.9 | 1600 | 1600 | 1.41 |
| scattered | mix 0.2 | 30 | 26.0 | 1.503 | 0.227 | -4.2 | 1600 | 1312 | 1.37 |
| scattered | mix 0.3 | 30 | 27.3 | 1.484 | 0.191 | -3.1 | 1600 | 1600 | 1.36 |
| scattered | mix 0.5 | 30 | 27.3 | 1.474 | 0.184 | -3.4 | 1600 | 1024 | 1.26 |
| scattered | random | 30 | 34.0 | 1.625 | 0.372 | -5.9 | 1600 | 1600 | 1.46 |

### Local amendments by size: mean shortfall, points / median audits to every case right

| Size | local | mix 0.1 | mix 0.2 | mix 0.3 | mix 0.5 | random |
|---|---|---|---|---|---|---|
| small | 0.702 / 512 | 0.712 / 512 | 0.708 / 512 | 0.713 / 512 | 0.742 / 512 | 0.728 / 1600 |
| medium | 1.682 / 512 | 1.603 / 512 | 1.618 / 512 | 1.655 / 512 | 1.561 / 512 | 1.512 / 1600 |
| large | 3.917 / 724 | 2.855 / 724 | 2.515 / 724 | 2.469 / 1024 | 2.427 / 1024 | 2.412 / 1600 |

Selection rule applied to this set: strategies as fast as `local` on every size: local, mix 0.1, mix 0.2; smallest shortfall among them: **mix 0.2**.
