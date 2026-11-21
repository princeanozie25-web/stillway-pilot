# v0.3 specification: a change of memory architecture

Written before any v0.3 final job is generated. It is frozen with the code and the checkpoints in one git commit; the final seed is derived from that commit's hash.

v0.2 ended with a recommendation: change the memory architecture, do not scale. Its memo named three experiments. v0.3 runs them.

| v0.2 finding | v0.3 experiment |
|---|---|
| Saved states cannot be listed (26,000 states for 800 meanings, growing with irrelevant history). | 1. Canonical memory, two ways: built in (typed registers) and trained in (arm M, no change of architecture). |
| The planner does not carry to longer jobs (50% at four legs). | 2. A reader that extrapolates in length, tested at 5 to 16 legs. |
| Setup needs the exact planner as labeller, and the exact planner then does the job itself. | 3. Exploratory: train with no planner labels, from logged outcomes only. |

## 1. The v0.3 core (`stillway3/model.py`)

**Memory: typed registers.** One register per order field. A field shown in an observation overwrites its register; nothing else can change a register. The write is a rule, not a learned function. The saved state is therefore the order of record, readable without a dictionary, and an edit is a register write with nothing to fit. This is symbolic memory by construction, and it is stated as such.

**Reader: four small learned functions.**

| Function | Input | Output |
|---|---|---|
| start | the two gate-requirement registers | carry |
| leg step | carry, one leg | carry |
| route | carry, the current leg, the two gates | route 0 or 1 |
| deliver | the current station's parcel register, the closed bay | dock |

The carry is the only thing passed from leg to leg. It is snapped to one of at most 64 codes after every step, so the reader is a finite machine for any number of legs. Addressing is relative: no function sees a leg's position. Nothing in the weights depends on the number of legs.

**Training** is imitation of the exact planner's valid action sets, with the planner's value table as a training aid on the carry (as in v0.2). Two training distributions, both on training families only:

| Name | Legs | Leg kinds | Cores |
|---|---|---|---|
| T23 | 2 or 3 | same-gate only | `v3r23_s1..5`. This is exactly the v0.2 training distribution. |
| T24x | 2 to 4 | cross-gate legs with probability 0.3 | `v3r24_s1..5` |

**Ablations** (two seeds each, both distributions): `v3c*` carries a free vector (no codes); `v3n*` has no value-table aid (valid action sets only).

## 2. The certificate for any length (`stillway3/certify.py`)

The reader's code and the exact planner's value table are run together from every pair of gate requirements, through every kind of leg, until no new (code, value table) pair appears. For every pair found, every kind of current leg and every gate state, the proposed route is compared with the exact planner. Deliveries are a 12-entry table checked in full.

A clean result covers every job of every length made of the leg kinds in the alphabet, with any events. Two alphabets: **same** (32 same-gate leg kinds) and **all** (64 leg kinds).

Every wrong entry has a witness job. The witness is replayed through the network in the simulator and compared with the plain-Python reference.

The check runs on integer tables read off the network. `tests/test_regcore.py` checks tables against network on sampled jobs; margins to the nearest tie are reported.

**Certificate-guided repair** (`stillway3/repair.py`): every wrong entry is turned into a job, labelled by the exact planner, and trained on, mixed with ordinary batches; repeated until the closure is clean. Repaired cores are separate checkpoints (`v3r23fix_*` on alphabet same, `v3r24fix_*` on alphabet all). Repair cannot add codes: a T23 core has 15 codes for the 15 value tables of same-gate jobs and cannot be repaired onto the 29 tables of alphabet all (tried, stopped, not pursued). Repair uses planner labels on jobs chosen by the certificate, which can be longer than any training job. The unrepaired cores stay the test of extrapolation.

Seen before this freeze: the plain repair loop made four of the five T24x cores clean in 1 to 8 rounds. On seed 3 it oscillated and was not clean after 30 rounds. Two variants were then tried on that seed only, and both gave a clean closure: a smaller step size (`v3r24fixl_s3`, `--lr 1e-4 --steps 600`) and rehearsal of entries that were already right (`v3r24fixr_s3`, `--rehearsal 4000`). They are frozen as separate checkpoints, reported, and not counted in any `v3r24fix` mean or in rule C3b. T23 cores: three of five were clean on alphabet same with no repair; the other two needed 1 or 2 rounds.

## 3. Arm M: canonical memory by training rule alone (`v03/train_m.py`)

The v0.2 core, data and schedule, unchanged, with one added rule: after every step the saved state must equal the state a restart would write (memory wiped, the whole order of record shown, in another job's surroundings). No label for the memory is used. Three seeds (`v3m_s1..3`). A first attempt with the rule at full weight from the first quantised step broke the planner and was stopped (logs kept); the rule now ramps in.

## 4. What was seen before this freeze

- Development families (hash buckets 60 to 69) at 2 to 6 legs.
- Certificates. A certificate lists the reader's whole input space, so it covers final families too. For a core with a clean certificate the final strata are a confirmation through an independent path (simulator, network, frozen harness), not a blind holdout.
- The v0.2 final strata in aggregate (the v0.2 report). No v0.3 core was run on them before this freeze.
- The v0.3 final strata: nothing. They are generated from the freeze commit.

The final strata are authored by the assistant that built the model. Codex's replay stays open.

## 5. Final tests

**F1. The v0.2 final items.** Frozen v0.2 harness (`stillway2/edits.py`), v0.2 final seed 1670983329, strata A, B, C, 4,000 flip attempts each, the same secondary cells. Run once per core. Primary cores: `v3r23_s1..5` (same training data as the v0.2 cores, so only the architecture differs).

**F2. Long jobs.** Final family buckets, 2,000 flip attempts per stratum per core, seed from the v0.3 freeze commit (`v03/final_seed.py`). S = same-gate legs, X = cross-gate legs with probability 0.3.

| Stratum | Legs |
|---|---|
| S_2to3, S_4, S_5to6, S_7to8, S_12, S_16 | 2–3, 4, 5–6, 7–8, 12, 16 |
| X_2to4, X_5to6, X_7to8, X_12, X_16 | 2–4, 5–6, 7–8, 12, 16 |

Methods: message and resume, full restart, register write, and the four shortcuts. Planner-alone accuracy on the same strata with no events, ordinary events and stress events.

**F3. Certificate against simulator** (`v03/confirm.py`): 100,000 fresh jobs of 2 to 16 legs per alphabet per core, through the network.

**F4. Listing.** Register cores: `tests/test_regcore.py` (registers equal the order of record at every step). Arm M: the v0.2 scaling protocol (`v02/m4_scaling.py`, development families, 20,000 jobs per cell, wait slots K = 1 to 16).

**F5. Latency** (`v03/latency.py`): network with message; network with register write; certified tables with register write; exact planner in plain Python. 3-leg and 16-leg jobs.

## 6. Pass rules, fixed now

| Claim | Passes if |
|---|---|
| C1a. Register memory is the order of record | the test passes (it is true by construction; the test guards the code) |
| C1b. Canonical memory can be trained in (arm M) | for at least 2 of 3 seeds, at every K from 1 to 16: at most 1,458 distinct saved states (twice the 729 possible orders), a sampled dictionary knows at least 99% of the steps of fresh jobs, and development task success is at least 99.5% |
| C2. Length extrapolation without repair | for at least 4 of 5 seeds, planner-alone jobs fully valid at least 99% in every stratum the core's training covers by leg kind (T23: all S strata; T24x: all S and X strata), with ordinary events |
| C3a. Certificate without repair | reported per seed and alphabet; no threshold (this is the measurement) |
| C3b. Certificate after repair | at least 4 of 5 `v3r24fix` cores clean on alphabet all |
| C3c. The certificate predicts the simulator | every clean (core, alphabet) has 0 wrong actions in F3; the first 20 witnesses of every unclean one are confirmed on the network |
| C4. Edit (v0.2 advancement rule, unchanged) | pooled over the strata of F1, and separately of F2: joint success at least 90%; unrelated obligations within 5 points of the unedited replay; median revision latency below message-and-resume at no more than 2 points lower success |

Expectation stated in advance for C4: clause 3 cannot be met on the same executor. With registers a message and an edit are the same write followed by the same step. Any latency gain will come from running the certified tables in place of the network, which helps a message equally.

## 7. Exploratory, labelled as such in every report

- **No planner labels** (`v03/train_outcome.py`): the same core trained from logged jobs with random actions and their outcomes only (was each parcel accepted; how many gate requirements held at the end). The exact planner scores it and labels nothing. Passes if at least 2 of 3 seeds reach 99% jobs fully valid on every F2 stratum with ordinary events.
- The operator shift of v0.2 M5 with a v0.3 core.

## 8. Reported whatever the outcome

Per stratum, per seed, per number of legs; denominators; intervals that resample families; abstentions; every certificate with its counts, depth, margins and witnesses; repair rounds and the longest witness used; ablations; the stopped first attempt of arm M.
