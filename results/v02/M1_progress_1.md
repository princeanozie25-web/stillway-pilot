# M1 progress report 1: the two-field gap is real

21 November 2026, 07:05. Branch `v0.2`, started from commit `6588d9ff44731c0daf8120d5cc12ba1c2c45282a`. Seed 4 (`runs/f_iit_s4`, the seed that had zero wrong pairs with quotient memory in v0.1).

## Verdict

Astra is right. The v0.1 extractor listed 20 operator-message patterns. The simulator accepts 36. With the missing 16 (two fields revised at the same stage), seed 4 is no longer error-free, on trained families and with the original quotient maps. The v0.1 sentence "zero wrong answers in all 100 families" is true only for the 20-pattern list. It must be reworded.

## 1. Counterexample from the simulator alone (no extractor)

Command:

```bash
PYTHONPATH=. ~/Developer/voxcpm-venv/bin/python v02/m1_counterexample.py runs/f_iit_s4 0 2   # and chunk 1 2
PYTHONPATH=. ~/Developer/voxcpm-venv/bin/python v02/m1_counterexample.py runs/f_iit_s4 merge
```

Every layout, both starting gate states, every order, one stage with two fields revised at once: 393,216 episodes, plain memory.

| | Episodes | Failed |
|---|---|---|
| All | 393,216 | 20 (0.005%) |
| Trained families | 235,008 | 6 |
| Dev families | 61,440 | 2 |
| Sealed families | 96,768 | 12 |
| Dock + bay revised together | 147,456 | 20 |
| Dock + gate, gate + bay | 245,760 | 0 |
| Revision at LEG1 | 98,304 | 20 |
| Revision at PLAN, DOCK, LEG2 | 294,912 | 0 |

One witness on a trained family (`results/v02/counterexample/f_iit_s4/report.json`): family KO-KO, gate starts closed, order = dock 0, gate closed, bay 1. At LEG1 the operator sends dock 0 and bay 2 in the same message. The planner proposes a route that loses the gate obligation.

So one two-field message is enough, and the failures are rare under this simple sweep. The exhaustive check below finds many more, because it also varies everything else around that message.

## 2. The original seed-4 maps, recovered

v0.1 built the quotient maps in memory and saved only the counts. `v02/m1_recover_maps.py` repeats the v0.1 code line for line with the unchanged v0.1 extractor and saves the maps.

```bash
v02/par.sh 8 v02/m1_recover_maps.py runs/f_iit_s4
PYTHONPATH=. ~/Developer/voxcpm-venv/bin/python v02/m1_recover_maps.py runs/f_iit_s4 merge
```

| | Recovered now | Archived in v0.1 |
|---|---|---|
| Plain memory: pairs checked | 174,345,600 | 174,345,600 |
| Plain memory: wrong | 3 | 3 |
| Quotient memory: pairs checked | 7,864,320 | 7,864,320 |
| Quotient memory: wrong | 0 | 0 |

- Maps: `results/v02/maps20/f_iit_s4/maps20.json`, 100 families, 157,874 entries.
- **SHA-256 of the maps: `24856aba6cd5c1cfb747aa395254e76dfa2037c9ba4e033184e31b5bc5d01c13`**
- 2,236 CPU-seconds (about 5 minutes on 8 cores).

## 3. Those same maps, unchanged, with 36 patterns: one family profiled

```bash
FAMS=KO-KO PYTHONPATH=. ~/Developer/voxcpm-venv/bin/python v02/m1_expanded.py runs/f_iit_s4 0 1
```

Family KO-KO (trained). A saved state that is not a key of the old map is left as it is, which is what v0.1 did.

| Run | Pairs checked | Wrong | Reachable states per stage |
|---|---|---|---|
| v0.1, 20 patterns, plain memory | 2,918,400 | 0 | 30, 209, 318, 284, 329, 556 |
| v0.1, 20 patterns, original maps | 122,880 | 0 | 12, 12, 12, 6, 3, 1 |
| 36 patterns, plain memory | 8,925,696 | 24,055 | 30, 317, 450, 474, 554, 988 |
| 36 patterns, original maps unchanged | 2,677,248 | 418 | 12, 119, 128, 162, 147, 302 |
| 36 patterns, maps rebuilt on 36 patterns | 294,912 | 31 | 12, 12, 12, 22, 3, 1 |

With the original maps:

- 141,230 of 2,621,952 transitions (5.4%) landed on a state the map does not know: 922 distinct unknown states. The map is incomplete.
- Of the 418 wrong decisions, 384 came from an unknown state and 34 came from a known representative. So it is both things: an incomplete map and wrong actions.
- Shortest witness from a known representative: order (dock 0, gate closed, bay 2); PLAN message "bay 1"; LEG1 message "dock 0 and bay 2"; proposal is the wrong route.

Rebuilding the maps on the 36-pattern machine does not reach zero either (31 wrong), and 16 states now stand for two different orders at once.

## 4. Cost of the full expanded run

- KO-KO took 103 s with 36 patterns against 42 s with 20: a factor of 2.5. Peak memory 867 MB per process.
- Seed 4, all 100 families: about 5,600 CPU-seconds, about 12 minutes on 8 cores.
- All five primary seeds, including recovering their original maps: about 85 minutes on 8 cores. Running now (`v02/m1_all.sh`). No paid compute.

## 5. What is certified, in exact words (for now)

For seed 4 with the original maps: inside each of the 100 families, for every history in which each stage shows any layout of that family, any gate state, any closed bay, any decoration, and an operator message that is **empty, one field, or all three fields**, every proposed action is one the exact planner accepts. Histories with a two-field message are outside that statement, and the planner does fail on some of them.

Next: full counts for all five seeds, the remaining message tests (repeated writes, reissue then override, closed bay), and matched-history comparisons of plain and quotient memory.
