# A guard that asks a concrete question: simulation on 400 fresh author-made jobs (seed 8243)

Exploratory, author-made, reference semantics only (not the runner). Nothing here uses Codex's jobs or grades.

400 unselected one-fault project jobs; 372 further draws skipped because the fault showed in no visible check. Classes: 249 ordinary, 13 equal, 138 trap. Changes passing both visible checks on a trap job: mean 2.9, largest 7.

## The guard as built, on the same jobs (by its rule: one passing change commits, more than one asks)

| Class | Jobs | Committed, right | Committed, wrong | Asked, nothing done |
|---|---|---|---|---|
| ordinary | 249 | 249 | 0 | 0 |
| equal | 13 | 0 | 0 | 13 |
| trap | 138 | 0 | 0 | 138 |

## The questioning guard

T is the number of made-up inputs in a row that must fail to separate the remaining candidates before it commits without asking.

| T | Jobs finished right (hidden inputs) | Right on 3,000 further inputs | Finished wrong | Jobs with a question | Questions per job asked | Most questions on one job | Choices per question | Questions on equal jobs | Pipeline runs per job | per trap job |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 389 of 400 (97.2%) | 386 | 11 | 114 (28%) | 1.12 | 3 | 2.28 | 0 | 46 | 50 |
| 10 | 399 of 400 (99.8%) | 399 | 1 | 137 (34%) | 1.23 | 3 | 2.17 | 0 | 48 | 52 |
| 30 | 400 of 400 (100.0%) | 400 | 0 | 138 (34%) | 1.17 | 3 | 2.21 | 0 | 50 | 57 |
| 100 | 400 of 400 (100.0%) | 400 | 0 | 138 (34%) | 1.18 | 3 | 2.19 | 0 | 60 | 72 |
| 300 | 400 of 400 (100.0%) | 400 | 0 | 138 (34%) | 1.18 | 3 | 2.21 | 0 | 89 | 117 |

A pipeline run is one execution of the six-module project on one input. Trying every one-line change against the two visible checks, which both guards do, is 44 runs per job (22 changes, two checks).
