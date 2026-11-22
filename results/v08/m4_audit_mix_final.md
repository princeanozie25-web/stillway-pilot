# Audit mixing, final

## Generated family, final (seed 2): 12 local and 6 scattered amendments, 5 seeds

Regression = a budget below 1,600 at which fewer cases are right than by keeping the old table. Shortfall = mean over those budgets of the points below the old table (0 where not below).

| Amendment | Strategy | Runs | Budgets with a regression % | Mean shortfall, points | Shortfall from 64 audits on | Worst cell from 64 audits on, points | Median audits to every case right | Median audits to 99% | Error among answered at 256 audits % |
|---|---|---|---|---|---|---|---|---|
| local | local | 60 | 15.7 | 1.465 | 0.449 | -11.8 | 618 | 256 | 0.13 |
| local | mix 0.1 | 60 | 13.7 | 1.326 | 0.224 | -7.2 | 618 | 256 | 0.14 |
| local | mix 0.2 | 60 | 12.5 | 1.265 | 0.123 | -4.1 | 618 | 256 | 0.14 |
| local | mix 0.3 | 60 | 11.2 | 1.230 | 0.063 | -4.8 | 618 | 256 | 0.16 |
| local | mix 0.5 | 60 | 10.0 | 1.212 | 0.036 | -3.1 | 618 | 256 | 0.19 |
| local | random | 60 | 11.0 | 1.200 | 0.015 | -0.7 | 1600 | 1024 | 0.83 |
| scattered | local | 30 | 20.7 | 0.960 | 0.122 | -4.7 | 1600 | 1600 | 1.22 |
| scattered | mix 0.1 | 30 | 22.3 | 0.980 | 0.121 | -2.9 | 1600 | 1600 | 1.11 |
| scattered | mix 0.2 | 30 | 22.3 | 0.983 | 0.119 | -2.8 | 1600 | 1600 | 1.64 |
| scattered | mix 0.3 | 30 | 24.7 | 0.997 | 0.145 | -3.7 | 1600 | 1600 | 2.10 |
| scattered | mix 0.5 | 30 | 26.7 | 1.015 | 0.164 | -2.0 | 1600 | 1600 | 1.35 |
| scattered | random | 30 | 32.7 | 1.219 | 0.430 | -5.6 | 1600 | 1600 | 1.39 |

### Local amendments by size: mean shortfall, points / median audits to every case right

| Size | local | mix 0.1 | mix 0.2 | mix 0.3 | mix 0.5 | random |
|---|---|---|---|---|---|---|
| small | 0.399 / 618 | 0.391 / 618 | 0.392 / 618 | 0.393 / 618 | 0.398 / 618 | 0.411 / 1600 |
| medium | 1.403 / 512 | 1.363 / 512 | 1.339 / 512 | 1.343 / 512 | 1.300 / 512 | 1.250 / 1600 |
| large | 2.593 / 724 | 2.223 / 724 | 2.063 / 1024 | 1.953 / 1024 | 1.939 / 1024 | 1.939 / 1600 |

Selection rule applied to this set: strategies as fast as `local` on every size: local, mix 0.1; smallest shortfall among them: **mix 0.1**. (For the record only: the share was chosen on dev.)

## Codex's second hidden family (spent; holder's labels): 8 local and 4 scattered amendments

Regression = a budget below 1,600 at which fewer cases are right than by keeping the old table. Shortfall = mean over those budgets of the points below the old table (0 where not below).

| Amendment | Strategy | Runs | Budgets with a regression % | Mean shortfall, points | Shortfall from 64 audits on | Worst cell from 64 audits on, points | Median audits to every case right | Median audits to 99% | Error among answered at 256 audits % |
|---|---|---|---|---|---|---|---|---|
| local | local | 40 | 14.0 | 2.317 | 1.071 | -27.2 | 724 | 68 | 0.15 |
| local | mix 0.1 | 40 | 13.2 | 1.930 | 0.549 | -12.9 | 724 | 68 | 0.15 |
| local | mix 0.2 | 40 | 9.5 | 1.659 | 0.225 | -7.4 | 724 | 68 | 0.14 |
| local | mix 0.3 | 40 | 9.2 | 1.618 | 0.157 | -6.2 | 724 | 68 | 0.15 |
| local | mix 0.5 | 40 | 7.8 | 1.539 | 0.026 | -2.2 | 724 | 68 | 0.15 |
| local | random | 40 | 7.0 | 1.529 | 0.008 | -0.5 | 1600 | 260 | 0.63 |
| scattered | local | 20 | 18.0 | 1.458 | 0.087 | -4.1 | 1600 | 516 | 0.95 |
| scattered | mix 0.1 | 20 | 21.5 | 1.500 | 0.139 | -4.1 | 1600 | 516 | 0.85 |
| scattered | mix 0.2 | 20 | 22.5 | 1.528 | 0.174 | -4.1 | 1600 | 516 | 0.83 |
| scattered | mix 0.3 | 20 | 22.5 | 1.525 | 0.161 | -4.1 | 1600 | 516 | 0.96 |
| scattered | mix 0.5 | 20 | 24.5 | 1.543 | 0.195 | -4.1 | 1600 | 516 | 0.94 |
| scattered | random | 20 | 31.0 | 1.668 | 0.326 | -4.5 | 1600 | 516 | 0.73 |

### Local amendments by size: mean shortfall, points / median audits to every case right

| Size | local | mix 0.1 | mix 0.2 | mix 0.3 | mix 0.5 | random |
|---|---|---|---|---|---|---|
| small | 0.562 / 724 | 0.562 / 724 | 0.562 / 724 | 0.562 / 724 | 0.564 / 724 | 0.566 / 1600 |
| medium | 1.034 / 512 | 0.991 / 512 | 0.912 / 512 | 0.892 / 512 | 0.926 / 512 | 0.880 / 1600 |
| large | 7.108 / 724 | 5.606 / 724 | 4.600 / 724 | 4.454 / 724 | 4.103 / 724 | 4.103 / 1600 |
