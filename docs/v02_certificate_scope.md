# Certificate scope, and three corrections to the v0.1 report

## What the extractor checks

For one checkpoint and one Dispatch-2 family, the extractor lists every saved state the planner can reach and shows each one every observation in a fixed list. It compares the proposed action with the exact planner. A "pair" is one reachable state with one observation.

Bounds, all of them:

| Dimension | Bound |
|---|---|
| Stages | The six stages of Dispatch-2 (INIT, PLAN, LEG1, DOCK, LEG2, BAY). One observation per stage. No longer histories exist in this world. |
| Layout | Any of the family's layouts at every stage (up to 4: each leg's wiring either way round). The mechanisms on a leg never change. |
| Gate | Open or closed at every stage, whatever the last action did. |
| Closed bay | None, 0, 1 or 2 at every stage. |
| Decoration | 4 values at every stage. |
| Operator message | **v0.1: 20 patterns** (nothing, one field, or all three). **v0.2: all 36** (each field absent or set: 3 × 3 × 4). At INIT only the 12 full orders. |
| Order of record | The order after applying every message so far. |

**Overapproximation.** Any observation may follow any other inside a family. The simulator cannot produce all of those sequences (the gate cannot change by itself without a fault event, for example), so the extractor checks a superset of real histories. A clean result covers every real history inside the bounds. A wrong pair may sit on a history that needs several events in one job.

**Not covered:** a change of family inside a job; anything outside Dispatch-2; the 16 two-field messages in every v0.1 number.

Tests: `tests/test_messages36.py` builds simulator events for all 36 patterns at every stage, with repeated writes, a reissue followed by an override, and closed-bay handling, and checks the encoded observation and the order of record against the extractor's list (8,640 episodes). `tests/test_machine.py` replays reported counterexamples through plain simulation.

## Precise wording of what is certified

- **v0.1 statement, corrected.** For seed 4 with the original quotient maps (SHA-256 `24856aba6cd5c1cfb747aa395254e76dfa2037c9ba4e033184e31b5bc5d01c13`): in each of the 100 families, on every history whose operator messages are empty, one field, or all three fields, every proposed action is accepted by the exact planner (0 wrong in 7,864,320 pairs; reproduced in v0.2). This does **not** hold for histories with a two-field message.
- **With all 36 patterns, nothing is certified error-free.** Seed 4: plain memory 813,477 wrong in 529,845,120 pairs; original maps unchanged 414,171 wrong in 183,220,992; maps rebuilt on the 36-pattern machine 78,193 wrong in 17,720,064. `results/v02/M1_tables.md` has every seed.
- Every wrong pair has a replayable witness history in `results/v02/expanded/<run>/report.json`.

## Three corrections to the v0.1 report

1. **"Zero wrong answers in all 100 families"** (v0.1 sections 1 and 4.6) is true only for the 20-pattern message list. With two-field messages the same checkpoint and maps make wrong decisions, on trained families too. Found by Astra; confirmed here with the simulator alone (20 failures in 393,216 two-field episodes for seed 4) and with the extended extractor.
2. **"Quotient memory removes most remaining errors"** (v0.1 section 4.6) compared wrong-pair counts over two different reachable machines. On the same sampled histories (2,000,000 jobs, 36 patterns, seed 4) plain memory had 98 jobs with a wrong decision; the original maps had 106 (3 repaired, 11 broken, 42,162 changed only a tie-break); rebuilt maps had 505 (10 repaired, 417 broken). Quotient memory did not repair jobs. It changes which states exist.
3. **"A planted hidden channel is erased by quotient memory"** (v0.1 sections 1 and 4.6) holds for the specification quotient and **not** for the behaviour quotient. v0.1 trained its fresh decoder on the state at one late stage only. With balanced payloads and a decoder on the states after every stage, the behaviour quotient leaves the payload readable (93.5% and 97.1% exact recovery on the two controls; chance is 25%). The specification quotient brings it to 25.5% and 25.0%, and the state then carries 0.003 and 0.000 bits about the payload given the task meaning. The canonicaliser uses a dictionary built by enumerating the target family with the exact planner as labeller: that is oracle-labelled target-family data.
