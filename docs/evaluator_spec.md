# Evaluator specification: Dispatch-2, version 0.1

This is the scoring contract. The code that implements it is `stillway/world.py` (the world and the exact planner), `stillway/fixtures.py` (fixtures and splits), `stillway/scorer.py` (credit) and `stillway/replay.py` (the paired replay and its controls).

## 1. The world

A carrier leaves the depot with two parcels.

| Stage | Name | What the planner does |
|---|---|---|
| 0 | INIT | Reads the work order. No action. |
| 1 | PLAN | One planning step. No action. |
| 2 | LEG1 | Chooses route L or R to station 1. Irreversible. |
| 3 | DOCK | Hands parcel 1 to dock 0 or 1. |
| 4 | LEG2 | Chooses route L or R to station 2. Irreversible. |
| 5 | BAY | Hands parcel 2 to bay 0, 1 or 2. |

Each route has a trip that acts on one shared gate: **K** keep, **T** toggle, **O** force open (1), **C** force closed (0). The gate is checked when the carrier arrives at station 2 (after LEG2).

The **work order** has three fields: `dock` (parcel 1), `gate` (the state the downstream station needs: the gate obligation) and `bay` (parcel 2: the unrelated obligation). If the bay is closed, parcel 2 goes to the next bay round (0 to 1, 1 to 2, 2 to 0).

**Closed book** (the instructed condition): the order is shown at INIT only. After that it lives in the planner's saved memory. **Open book** (the matched restart): the full current order is shown at every stage, so no memory is needed.

Events can change the world before any stage from PLAN on: `rev` (swap the L and R wiring of one leg), `gflip` (an outside fault flips the gate), `decor` (repaint, no effect), `close` (close a bay), `msg` (the operator revises one order field), `full` (the operator re-issues the whole order).

## 2. Input schema

One observation (37 numbers when given to a network):

```json
{"stage": "LEG2",
 "leg1": {"L": "K", "R": "K"}, "leg2": {"L": "T", "R": "K"},
 "gate": 1, "closed_bay": null, "decor": 0,
 "message": {"dock": null, "gate": null, "bay": null}}
```

One episode fixture:

```json
{"id": "...", "family": "KK-KT",
 "layout": {"leg1": {"L": "K", "R": "K"}, "leg2": {"L": "K", "R": "T"}},
 "gate0": 1, "decor": 0, "closed_bay": null,
 "order": {"dock": 1, "gate": 1, "bay": 2},
 "book": "closed",
 "events": [{"stage": "PLAN", "event": ["rev", 2]}]}
```

Event encoding in fixture files. Every event of a stage is applied, in the order listed, before that stage's observation is made:

| Event | Effect |
|---|---|
| `["rev", 1]` or `["rev", 2]` | Swap the L and R trips of leg 1 or leg 2. |
| `["gflip"]` | The gate state flips (0 to 1, 1 to 0). |
| `["decor", v]` | Decoration becomes `v` (0 to 3). No effect on anything. |
| `["close", b]` | Bay `b` (0 to 2) is now the one closed bay. `-1` means no bay is closed. |
| `["msg", "dock" or "gate" or "bay", v]` | The operator's order field becomes `v`. That field is shown in this stage's message. |
| `["full"]` | The whole current order is shown in this stage's message. |

A route action applies its trip to the gate at once: K leaves it, T flips it, O sets it to 1, C sets it to 0. `gate_arrival` is the gate right after the LEG2 action. Validity at each stage uses the operator's order as it stands after that stage's events.

A planner exposes four operations and nothing else:

| Operation | Meaning |
|---|---|
| `init(obs)` | Start from a work order. Returns a state. |
| `advance(state, obs)` | One planning step. Returns the next state. |
| `propose(state, obs)` | The action it would take now. |
| `save(state)` / `restore(blob)` | The state is a short list of slots. For the discrete planner each slot is one integer code ID. |

At stage *s* the scorer calls `propose(state_before, obs)`, then `advance(state_before, obs)`. Only the simulator applies actions. Every state goes through `save` and `restore` before the next step, and the scorer rejects a planner whose proposal changes after a reload.

## 3. Reference outcomes

The exact planner gives the **set** of valid actions at each action stage, judged against the world as it is now (it cannot see later events):

- LEG1: every route from which some leg-2 route still reaches the required gate state. If none does, both routes are valid.
- LEG2: every route that leaves the gate in the required state. If none does, both are valid.
- DOCK: the order's dock. BAY: the order's bay, or the next bay if it is closed.

The **earliest irreversible gate decision** is the first route stage where only one route is valid. A fixture records it as `commit_stage`.

## 4. Split rule

A **family** is the pair of mechanisms on each leg, ignoring which side they are wired to (for example `KT-OC`). There are 100 families and 256 layouts.

Each family name is hashed with SHA-256 under the salt `stillway/dispatch-2/v0.1/`. Families are sorted by hash. The first 60 are **train**, the next 15 are **dev-holdout**, the last 25 are **sealed**. Nobody chose which families are held out.

- Training samples only train families.
- Public development fixtures: `fixtures/dev/dev_in.jsonl` (train families) and `fixtures/dev/dev_out.jsonl` (dev-holdout families).
- Sealed fixtures: `fixtures/sealed/sealed.jsonl`. The loader refuses to open them until `FREEZE.json` exists. `FREEZE.json` records the checkpoint hashes, the slot-selection results and the hash of every scorer file.

## 5. Fixture classes and credit

| Class | Kind | What it is | Credit |
|---|---|---|---|
| `plain` | episode | Closed book, no events. | Every proposed action is valid. |
| `dynamic` | episode | Closed book with random events at any stage. | Same. |
| `route_swap` | pair | Normal orientation, same observations after INIT, opposite gate obligation. | Both runs get credit. |
| `wiring_reversal` | pair | Same order. Layout in normal orientation vs reversed from the start. | Both. |
| `midplan_reversal` | pair | Same start. In run b the wiring is reversed after the order was given. | Both. |
| `open_revision` | pair | Open book. Run b revises the gate obligation at PLAN. | Both. |
| `swap` | swap | The decisive paired replay (section 6). | Three-part test. |

Pairs get credit only when **both** runs pass. A shortcut that is right on one member by luck scores 0, not 50%.

**Reversal eligibility.** A reversal counts only when the obligation is reachable in both worlds and no planner that ignores which side the trips are wired to can meet it in both. That planner may still react to the gate it sees. Version 1 of this rule compared fixed route plans only. The lookup impostor then earned 4% on `wiring_reversal` by repairing on leg 2. The rule was tightened and the impostor now scores 0. About 22% of all (layout, gate, reversal) combinations are eligible, and 102 of 193 non-sealed layouts have at least one eligible pair.

## 6. The decisive paired replay

Target T and donor S:

- opposite gate obligations;
- the donor's layout is the target's with one or both legs reversed;
- same starting gate, same closed bay, same stage;
- unrelated obligations drawn independently, and required to differ in what they make the carrier do.

Both are paused after PLAN, before any physical action. The selected slots of the donor's saved state replace the same slots in the target's saved state. The target resumes in the **target's** world.

Predicted consequence, declared before the run: the gate on arrival equals the **donor's** obligation, parcel 1 reaches the **target's** dock, parcel 2 reaches the **target's** bay. Credit needs all three. Every pair is scored in both directions.

**Slot selection rule (frozen).** Try every non-empty set of slots on the development swap fixtures. Keep the set with the highest credit. Ties go to the smaller set, then the first in order. The rule is the same for every planner.

Controls on the same fixtures: resume unchanged twice, shuffled donor, donor with the same obligation, the non-selected slots, blank memory, whole-state transplant (diagnostic only), decoration repaint, revision by operator message, restart from the full revised order.

## 7. Thresholds (proposed in the brief, frozen here before the sealed run)

| Quantity | Threshold |
|---|---|
| Ordinary held-out accuracy (`plain` on sealed families) | at least 90% |
| Targeted swap credit minus shuffled credit, same fixtures | at least +10 points, lower 95% bound above 0 |
| Drop in unrelated-obligation success vs unchanged replay | at most 5 points |
| Seeds | 5 |

Intervals resample whole layout families. A result that is not precise enough leaves the claim open.

## 8. Worked example (hand-scored, then run through the scorer)

Family `KK-KT` (a dev-holdout family). Leg 1: both routes keep the gate. Leg 2 in normal orientation: L keeps, R toggles. Gate starts open (1). Order: dock 1, gate must be open, bay 2.

- **Normal**: the gate must stay open, so leg 2 must be L. Valid plan: any route, D1, **L**, B2.
- **Reversed** (leg 2: L toggles, R keeps): leg 2 must be **R**.

**Swap.** Target = the reversed layout with order (dock 1, gate open, bay 2). Donor = the normal layout with order (dock 0, gate closed, bay 0). The donor on its own takes R on leg 2. After the swap the target should end with the gate **closed**. In the target's wiring that needs route **L**, which is not the route the donor took. Dock must still be 1 and bay still 2.

Scorer output (`python tools_worked_example.py`, saved in `fixtures/dev/worked_example.json`):

| Planner | Normal | Reversed | Reversal pair | Route-swap pair | Swap: leg-2 route, gate, dock, bay | Swap credit |
|---|---|---|---|---|---|---|
| Reference | L D1 L B2 ✓ | L D1 R B2 ✓ | 1 | 1 | L, closed, 1, 2 | 1 |
| Impostor 1: left/right lookup | L D1 L B2 ✓ | L D1 **L** B2 ✗ | **0** | 1 | R, open, 1, 2 | 0 |
| Impostor 2: memoryless recompute | L **D0** L **B0** ✗ | same ✗ | 0 | **0** | L, closed, 0, 0 | 0 |
| Impostor 3: plan cache | ✓ | ✓ | 1 | 1 | **R**, open, 1, 2 | **0** |
| Impostor 4: entangled slot | ✓ | ✓ | 1 | 1 | L, closed, **0**, **0** | **0** |

## 9. Impostor results on all public dev fixtures

5,200 items. Command: `python tools_score_hand.py`. Output in `results/hand_planners_dev.json`.

| Planner | plain | dynamic | route_swap | wiring_reversal | midplan_reversal | open_revision | swap |
|---|---|---|---|---|---|---|---|
| Reference | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Left/right lookup | 0.643 | 0.680 | **1.000** | **0.000** | 0.000 | 1.000 | 0.500 |
| Memoryless recompute | 0.140 | 0.222 | **0.000** | 0.022 | 0.005 | **1.000** | 0.110 |
| Plan cache | 1.000 | 0.817 | 1.000 | 1.000 | **0.000** | 1.000 | **0.000** |
| Entangled slot | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | **0.000** |

Reading:

- The lookup passes ordinary route swaps and fails the wiring reversal, as the brief requires.
- The memoryless planner passes ordinary (open-book) revision and fails the test of whether saved memory matters (`route_swap`, closed book). If it ever scores above 0 there, the instruction is leaking through the observations.
- The plan cache passes everything static and fails the mid-plan reversal and the swap. It models memory that holds the compiled route, not the obligation.
- The entangled planner behaves perfectly and still fails the swap, because moving its one slot moves the unrelated obligations too.
- No impostor earns full credit on its target test. The evaluator needed one repair (section 5).

## 10. One falsifier

If a planner trained in a world that never changes after INIT passes the mid-plan reversal and the cross-wiring swap as well as a planner trained with changes, then the swap test does not separate goal memory from plan memory in learned planners, and the primary endpoint would need a new design. This was run. See `REPORT.md`.
