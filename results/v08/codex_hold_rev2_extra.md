# Codex's revision-2 holdout: descriptive tables

Computed after the frozen report. Nothing here feeds a verdict.

## 1. What a verified project job costs when an operation has a price

Cost per verified job = (seconds per job + price x operations per job) / verified share. Seeds pooled.

| | Jobs | Seconds per job | Operations per job | Verified % | Cost at 0 s per operation | at 0.05 s | at 0.5 s | Cheaper than the search script above |
|---|---|---|---|---|---|---|---|---|
| base | 357 | 0.397 | 12.6 | 35.0 | 1.13 | 2.93 | 19.14 | 99 ms per operation |
| exec | 357 | 0.401 | 14.0 | 53.8 | 0.75 | 2.05 | 13.78 | 32 ms per operation |
| shuf | 357 | 0.459 | 16.7 | 29.4 | 1.56 | 4.40 | 29.96 | never |
| prediction only | 357 | 0.330 | 10.7 | 50.4 | 0.65 | 1.71 | 11.25 | 22 ms per operation |
| exec seed 1 + bank | 119 | 0.168 | 19.9 | 89.1 | 0.19 | 1.31 | 11.37 | 4 ms per operation |
| exec seed 1 + guarded bank | 119 | 0.159 | 72.7 | 95.0 | 0.17 | 4.00 | 38.45 | never |
| search script | 119 | 0.087 | 46.5 | 100.0 | 0.09 | 2.41 | 23.36 |  |

## 2. The bank arms, job by job (exec seed 1; 220 jobs)

| Arm | Verified | Wrong | Asked, correctly | Asked on an answerable job | Out of limits | Finished by the bank | Operations per job |
|---|---|---|---|---|---|---|---|
| exec seed 1 + bank | 207 | 6 | 24 | 6 | 1 | 163 | 14.5 |
| exec seed 1 + guarded bank | 214 | 1 | 24 | 4 | 1 | 171 | 43.1 |
| exec seed 1 alone | 163 | 40 | 24 | 12 | 5 | 0 | 10.6 |

**exec seed 1 + bank: every job not verified**

| Job | Domain | Group | Mechanism | Route | Outcome | End | Bank operations | Scripts | The core alone on this job |
|---|---|---|---|---|---|---|---|---|---|
| proj-holdout-a2a0c0d97190 | proj | newmech | norm:none>lower | deep-direct | wrong | DONE | 40 | 11 | wrong |
| proj-holdout-65974e0bb121 | proj | familiar | cmp:lt>gt | deep-direct | budget | BUDGET | 3 | 11 | budget |
| proj-holdout-58f6a6c54c4c | proj | newmech | thr:-2 | deep-direct | wrong | DONE | 18 | 11 | wrong |
| proj-holdout-d3fff47441ce | proj | newmech | norm:both>strip | deep-direct | wrong | DONE | 31 | 10 | wrong |
| proj-holdout-f30edce2ba1f | proj | familiar | thr:+2 | deep-direct | abstained | ASK | 17 | 8 | abstained |
| proj-holdout-576971800b74 | proj | familiar | cmp:le>lt | deep-direct | abstained | ASK | 3 | 8 | abstained |
| proj-holdout-9a77fd930e4b | proj | familiar | thr:-1 | deep-direct | wrong | DONE | 21 | 11 | wrong |
| proj-holdout-6e3974b284d3 | proj | familiar | cmp:ge>gt | deep-direct | abstained | ASK | 3 | 8 | abstained |
| proj-holdout-a9984d5fdb31 | proj | familiar | thr:+1 | deep-direct | abstained | ASK | 17 | 8 | abstained |
| proj-holdout-c9af8c37254b | proj | altered | thr:+1 | deep-direct | abstained | ASK | 3 | 10 | abstained |
| proj-holdout-9294b2682b11 | proj | altered | thr:+1 | deep-direct | wrong | DONE | 3 | 12 | wrong |
| proj-holdout-b7ff55f6fad2 | proj | familiar | thr:+2 | deep-direct | wrong | DONE | 20 | 11 | wrong |
| proj-holdout-1b0a008a99fd | proj | altered | thr:-1 | deep-direct | abstained | ASK | 3 | 8 | abstained |

**exec seed 1 + guarded bank: every job not verified**

| Job | Domain | Group | Mechanism | Route | Outcome | End | Bank operations | Scripts | The core alone on this job |
|---|---|---|---|---|---|---|---|---|---|
| proj-holdout-65974e0bb121 | proj | familiar | cmp:lt>gt | deep-direct | budget | BUDGET | 3 | 11 | budget |
| proj-holdout-576971800b74 | proj | familiar | cmp:le>lt | deep-direct | abstained | ASK | 3 | 8 | abstained |
| proj-holdout-6e3974b284d3 | proj | familiar | cmp:ge>gt | deep-direct | abstained | ASK | 3 | 8 | abstained |
| proj-holdout-c9af8c37254b | proj | altered | thr:+1 | deep-direct | abstained | ASK | 3 | 10 | abstained |
| proj-holdout-9294b2682b11 | proj | altered | thr:+1 | deep-direct | wrong | DONE | 3 | 12 | wrong |
| proj-holdout-1b0a008a99fd | proj | altered | thr:-1 | deep-direct | abstained | ASK | 3 | 8 | abstained |

**Plain bank against guarded bank, same jobs** (plain outcome, guarded outcome, jobs): abstained → abstained: 4; abstained → verified: 2; budget → budget: 1; verified → verified: 207; wrong → verified: 5; wrong → wrong: 1

**Core alone against core + plain bank** (alone, with bank, jobs): abstained → abstained: 6; abstained → verified: 6; budget → budget: 1; budget → verified: 4; verified → verified: 163; wrong → verified: 34; wrong → wrong: 6
