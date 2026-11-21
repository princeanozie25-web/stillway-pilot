# v0.2 transfer test: specification (M2 and M3)

This file is the scoring contract for the v0.2 edit experiments. It is frozen with the code before any final family is generated. Code: `stillway2/world3.py` (world and exact planner), `stillway2/model3.py` (core), `stillway2/edits.py` (attempts, methods, scoring), `stillway2/editors.py` (the two portable editors), `v02/m3_eval.py` (evaluation).

## 1. Why a new world

All 100 Dispatch-2 families were inspected in v0.1. A new salt on those families tests nothing new. Dispatch-3 changes the structure of the task.

| | Dispatch-2 (v0.1) | Dispatch-3 (v0.2) |
|---|---|---|
| Legs | always 2 | 2, 3 or 4 |
| Gates | 1 | 2; every trip names the gate it acts on |
| Leg kinds | – | same-gate (both routes act on one gate) and cross-gate (routes act on different gates) |
| Order fields | dock, gate, bay (3) | a requirement for each gate (none, closed, open) and a dock (0, 1, 2) for each station's parcel (6) |
| Live obligations | 3 | 1 to 6, set by the layout and the order |
| History length | fixed, 6 stages | optional wait stages before each leg; set by `K` and `p_wait`, independent of the obligations |
| Reference | exact planner | exact planner: enumerates every remaining route choice and keeps the routes that still allow the largest number of gate requirements |

A job runs through a frame of slots: INIT, then for each leg `K` wait slots, a ROUTE slot and a DELIVER slot. A slot that does not apply to a job is skipped.

## 2. How the planner reads a variable layout (v0.2 core)

The v0.1 reader was built for exactly two legs. It is replaced. **The v0.2 core is a new model, trained on Dispatch-3 training families, and is named `v2_*`.**

- One shared leg encoder. Per step the recurrent cell is updated once with the global part of the observation, then once per leg still ahead, from the last leg back to the next one, then once more with the global part. A layout with more legs takes more updates. No weight is tied to a leg position.
- Memory: 8 slots of 16 codes. With interchange training, slots 0 to 5 are trained to hold the six order fields. Interchange swaps happen between jobs at different stages, in different layouts, with different numbers of legs.
- Training aids, all from the exact planner and all recorded in each manifest: the set of valid actions (the imitation target), the count of reachable gate requirements for each route, and the exact planner's value table at each leg of the backward sweep.

## 3. Families and splits

A family is the number of legs, the unordered pair of trips on each leg, and which stations have a parcel. A fixed arithmetic hash of that signature (`world3.bucket`, salt 20261121) sends 60% of families to train, 10% to dev, 30% to final.

Training and development use 2 or 3 legs, same-gate legs only.

Final strata. None of them is sampled before the freeze:

| Stratum | What is new | Share of final attempts |
|---|---|---|
| A, unseen families | hash buckets 70 to 99; 2 or 3 legs; same-gate legs | one third |
| B, four legs | training never had more than three | one third |
| C, cross-gate legs | at least one leg whose two routes act on different gates; training had none | one third |

**Commitment.** The freeze is a git commit. The seed for every final batch is the first 8 hex digits of SHA-256 of the text `stillway-v0.2-final|` followed by that commit's hash. So the final jobs cannot be generated before the freeze exists. The final strata are **authored by the same assistant that built the model**, so this holdout is internal. A separate challenge for Codex is in `docs/v02_codex_challenge.md`.

## 4. An edit attempt

One job, one pause slot, one order field that still matters, one new value. The job runs with plain memory up to the pause, a method applies the correction, the job resumes. No other event happens in the primary attempts.

- **flip** (primary): the new value differs from the old. Gate requirements flip between closed and open.
- **no-op**: the new value equals the old.
- **impose / withdraw**: a gate requirement is added where there was none, or removed.
- **two edits**: a second edit at a later slot, on the same field (a conflicting successive edit) or on another field.
- **mirror pairs**: two jobs that are identical except that every leg's wiring is swapped, with the same edit. The edit then needs opposite routes in the two jobs. A pair counts when both jobs succeed.

**Eligible** attempts: the field is still live at the pause; under the corrected order every gate requirement can still be met together; and, for flip edits, the attempt is **non-trivial**: the same job with the correction ignored fails. All three are fixed by the job and the plan, so they are the same for every method. (With the non-trivial filter the "ignore" and "original order" shortcuts score 0 by construction; they are reported before the filter.)

**Scoring** looks at outcomes only, so any valid route earns credit.

- edited obligation met: the edited gate ends in the required state, or the edited parcel reaches the new dock (next dock round if that one is closed);
- unrelated obligations met: every other gate requirement and every other parcel;
- **joint success** = both, with no abstention. An abstention is a failed attempt.
- The unrelated-obligation reference is the same job replayed with no edit.

## 5. Methods

| Method | What it may use |
|---|---|
| **Portable editor** (the arm under test) | saved code IDs, field name, new value. Nothing else: no target layout, no hidden order, no simulator, no target-family data. Fitted on training families. Two candidates: slot write (a table read off training jobs) and predictor (a small network). One is chosen on dev and frozen. |
| Message and resume | the correction arrives as an ordinary operator message at the next step |
| Full restart | memory wiped, the whole corrected order shown |
| Symbolic field memory + incremental planning | the exact planner with the order held in a table. Correct by construction; timed for comparison. |
| Per-family dictionary | reference with privileged setup: jobs sampled in the target family with the true order as label |
| Shortcuts that must fail | ignore the edit; show the original order afresh; overwrite the whole state from another job that has the wanted value; replay that job's actions |

## 6. Advancement rule (default from the brief, frozen)

On the final strata, pooled, with every eligible attempt in the denominator:

1. joint edit success of the frozen portable editor at least 90%;
2. unrelated obligations within 5 points of the unedited replay;
3. one measured advantage over message-and-resume. Named in advance: **median end-to-end revision latency** (correction in, next action out, one job, one CPU thread, after warm-up) at comparable success, where comparable means at most 2 points below message-and-resume.

A successful but slower editor earns a controllability result and no speed claim. Reported whatever the outcome: per stratum, per number of legs, per seed, intervals that resample families (family key = number of legs, first-leg mechanism pair, last-leg mechanism pair), denominators, abstention rates, and the other capability an edit has that a message does not (the saved state is corrected without stepping the planner).

Sample size: 4,000 flip attempts per stratum per core seed, 2,000 for each secondary cell.
