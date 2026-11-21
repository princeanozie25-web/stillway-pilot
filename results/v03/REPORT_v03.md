# Stillway pilot v0.3: report

21 November 2026. Branch `v0.3`, built on `v0.2` (tag `v0.2-local`). Freeze commit `de80fd794802d422353707c0fa8ff49950e1a7cf`; v0.3 final seed 850390379. Every number below is in `results/v03/` and in `results/v03/tables.md`, which `v03/report.py` rebuilds.

## 1. Verdict

v0.2 recommended a change of memory architecture. v0.3 made it and tested it against rules fixed before any final job existed (`docs/v03_spec.md`).

| Question | Answer |
|---|---|
| Does the new architecture fix the transfer failure? | Yes. With the same training data as v0.2, pooled edit success on the v0.2 final items rises from 73.3% to 96.0%, and four-leg jobs from 41.5% to 100.0%. |
| Does it carry to long jobs? | Yes. Trained on 2 to 4 legs and tested up to 16, every seed has at least 99.5% of jobs fully valid in every length stratum. After repair, 100.00% in every stratum. |
| Can the planner be certified for every length? | Yes. Four of five repaired cores have a clean exhaustive certificate that covers jobs of any number of legs. The certificate also found faults in cores that made no error in 1.4 million sampled steps. |
| Is the saved state listable? | Yes, two ways. Built in: registers are the order of record. Trained in, with no change of architecture: 378 saved states where v0.2 had 26,000 to 73,000 (two of three seeds). |
| Does an edit beat a message? | No. They are the same write. This is unchanged from v0.2 and was predicted in the spec. |
| Does learning need the exact planner as labeller? | No (exploratory). A core trained from logged outcomes only is certified on every leg kind in one of three seeds, and above 99.9% in two of three. |
| Does the learned planner beat the exact planner? | No. In this world they tie on outcomes. The certified tables run in 1 to 2 microseconds, faster than my plain-Python exact planner, but a hand-compiled exact planner would match that. |

What still fails: leg kinds never seen in training (87%, no better than v0.2), one repair seed in five, one arm-M seed in three, one outcome-trained seed in three.

## 2. What changed

**Memory: typed registers.** One register per order field. A field shown in an observation overwrites its register. Nothing else can change a register. The write is a rule. Only the reader is learned. The memory is symbolic by construction.

**Reader: four small learned functions** (85,233 parameters in total, about 2 minutes of training on one CPU core):

| Function | Input | Output |
|---|---|---|
| start | the two gate-requirement registers | carry |
| leg step | carry, one leg | carry |
| route | carry, the current leg, the two gates | route |
| deliver | the current station's parcel register, the closed bay | dock |

The reader sweeps from the last leg back to the current one. The carry is the only thing passed from leg to leg, and it is snapped to a code after every step. No function sees a leg's position.

**Why this works here.** The exact planner's own carried state is small. For gate requirements it is a value table of four numbers, and only 29 distinct tables ever occur, however long the job (15 with same-gate legs only). All of them appear within two legs of the end. The v0.2 reader had the same sweep but carried a free vector, addressed stations by position, and kept the order in memory slots tied to positions. It had never seen position 4.

## 3. Same data, new architecture (F1)

Frozen v0.2 harness, v0.2 final seed, 4,000 flip attempts per stratum per core, five seeds per row. The T23 cores are trained on exactly the v0.2 training distribution (2 or 3 legs, same-gate legs).

| Cores | Method | A: unseen families | B: four legs | C: cross-gate legs | Pooled |
|---|---|---|---|---|---|
| v0.2 | predictor edit | 99.9% | 41.5% | 86.5% | 73.3% |
| v0.2 | message | 100.0% | 42.2% | 86.3% | 73.5% |
| v0.3, T23 | register write | 100.0% | 100.0% | 87.4% | **96.0%** |
| v0.3, T23 | message | 100.0% | 100.0% | 87.4% | 96.0% |
| v0.3, T24x | register write | 100.0% | 100.0% | 100.0% | 100.0% |

- Per seed, the T23 cores pool at 95.7% to 96.3% on 6,100 to 6,121 eligible attempts. Stratum C intervals (resampling families) run from 84% to 90%.
- Stratum C is no better than v0.2. A cross-gate leg is a kind of leg the T23 cores never saw, and a learner of finite tables cannot know an unseen entry. T24x training includes cross-gate legs and closes the gap.
- Unrelated obligations: the largest drop against the unedited replay is 0.00 points. Abstentions: none.
- Shortcuts stay low: ignoring the edit 0%, the original order 0%, copying another job's state 30% to 49%, replaying another job's actions 22% to 36%.
- No-ops, added and withdrawn requirements, two successive edits and mirror pairs all equal the message path (`tables.md`).

Planner alone, ordinary events, share of jobs with every action valid: v0.2 100.0 / 57.1 / 85.1%; v0.3 T23 100.00 / 100.00 / 85.40%.

## 4. Long jobs (F2)

Final family buckets, fresh seed from the freeze commit, 2,000 flip attempts per stratum per core. S = same-gate legs, X = cross-gate legs with probability 0.3. Planner alone, ordinary events, share of jobs with every action valid:

| Cores | 2–3 legs | 4 | 5–6 | 7–8 | 12 | 16 |
|---|---|---|---|---|---|---|
| T23 on S | 100.00% | 100.00% | 100.00% | 99.95% | 99.92% | 99.95% |
| T23 repaired on S | 100.00% | 100.00% | 100.00% | 100.00% | 100.00% | 100.00% |
| T24x on X (2–4 in the first column) | 99.96% | – | 99.91% | 99.89% | 99.89% | 99.90% |
| T24x repaired on X | 100.00% | – | 100.00% | 100.00% | 100.00% | 100.00% |
| T23 on X (leg kinds never trained) | 88.70% | – | 85.23% | 83.35% | 83.18% | 83.72% |

- The lowest stratum of any unrepaired seed is 99.58% (rule C2 asks for 99%).
- Stress events give the same picture.
- Edits: pooled over all eleven strata and the five repaired T24x cores, register write, message and restart are each right on 100.00% of 75,151 eligible attempts. Shortcuts: ignore 0%, original 0%, state copy 18%, action copy 13%.

**Ablations** (two seeds each). A free-vector carry and a core trained without the value-table aid both reach the same sampled accuracy, including at 16 legs. So length extrapolation comes from registers, relative addressing and one shared leg step. The discrete carry is what makes the next section possible.

## 5. The certificate for any length (F3)

**What is checked.** The reader's code and the exact planner's value table are run together from every pair of gate requirements, through every kind of leg, until no new (code, value table) pair appears. For each pair, every kind of current leg and every gate state, the proposed route is compared with the exact planner. The set of pairs is finite, so the check ends, and it then covers every job of every length. Deliveries are a 12-entry table checked in full.

**Results** (alphabet "same": 32 same-gate leg kinds; "all": 64 leg kinds):

| Cores | Alphabet | Clean certificates | Entries checked per core | Wrong entries where not clean |
|---|---|---|---|---|
| T23, no repair | same | 4 of 5 | 1,920 to 3,712 | 32 |
| T23, repaired | same | 5 of 5 | 1,920 to 3,712 | – |
| T24x, no repair | all | 0 of 5 | 12,032 to 63,744 | 704 to 9,347 |
| T24x, repaired | all | **4 of 5** | 7,424 to 12,032 | 4,096 (seed 3) |
| No value-table aid | either | 0 of 4 | 61,568 to 443,904 | 3,712 to 76,332 |

- **The certificate predicts the simulator.** 100,000 fresh jobs of 2 to 16 legs per alphabet per core, through the network: every clean (core, alphabet) pair made 0 wrong actions in 1.44 million action stages. Every unclean pair had its first 20 witness jobs confirmed wrong on the network.
- **It finds what sampling misses.** Three unclean (core, alphabet) pairs made no wrong action at all in 1.44 million sampled stages (`v3r24_s4` on all: 704 wrong entries; `v3n23_s1` on same: 3,840; `v3n24_s2` on same: 11,551). The faults sit behind sequences of legs that random jobs rarely produce.
- **Margins.** Where only one route is valid, the smallest gap between the two routes in a certified core is 1.9 to 9.4 (logits). The tables are not near a tie.
- **Two implementations agree.** `stillway3/check_tables.py` is a separate checker in plain Python with no torch. It reproduces the counts and adds a brute-force pass that lists every route choice of every short job. The interactive page runs a third copy in JavaScript with the same counts.
- **The value-table aid matters for certifiability, not for accuracy.** Without it the reader uses 60 to 64 codes for the same 29 tables, the closure is 10 to 23 legs deep, and thousands of entries are wrong, while sampled accuracy stays at 100%.

**Repair.** Every wrong entry becomes a job, is labelled by the exact planner and is trained on, with ordinary batches, until the closure is clean.

| Core | Clean | Wrong entries by round | Longest witness job |
|---|---|---|---|
| v3r23fix_s3 | yes | 32, 64, 0 | 5 legs |
| v3r24fix_s1 | yes | 960, 744, 544, 0 | 5 legs |
| v3r24fix_s2 | yes | 757, 4574, … , 704, 0 (8 rounds) | 11 legs |
| v3r24fix_s3 | **no** | oscillates between 192 and 10,518 for 30 rounds | 11 legs |
| v3r24fix_s4 | yes | 704, 0 | 5 legs |
| v3r24fix_s5 | yes | 9347, 2144, … , 32, 0 (7 rounds) | 9 legs |

Seed 3 became clean with a smaller step size (`v3r24fixl_s3`, 9 rounds) and with rehearsal of entries that were already right (`v3r24fixr_s3`, 8 rounds). Both were tried on that seed only, before the freeze, and are not counted. Repair uses planner labels on jobs the certificate chooses, up to 11 legs long. It cannot add codes, so a T23 core cannot be repaired onto leg kinds it has no code for.

**Scope.** The certificate covers the route and delivery decisions of Dispatch-3 for every number of legs, every leg kind in the alphabet, every order, every gate state and every event. It is made on integer tables read off the network. Tables and network agree on 10,828 sampled action stages per core (`tests/test_regcore.py`); the tables are the certified object. It needs the rules of the world (here the exact planner). It does not cover any other world. Full statement: `docs/v03_certificate_scope.md`.

## 6. Edits and the advancement rule (C4), latency (F5)

| Clause (unchanged from v0.2) | F1, T23 cores | F2, repaired T24x cores |
|---|---|---|
| Joint success at least 90% | 96.0%: pass | 100.00%: pass |
| Unrelated obligations within 5 points | 0.00: pass | 0.00: pass |
| Faster than message-and-resume | **no** | **no** |

Median revision latency, one job, one CPU thread (`v3r24fix_s1`):

| | 3 legs | 16 legs |
|---|---|---|
| Network, correction as a message | 214 µs | 866 µs |
| Network, register write then step | 230 µs | 883 µs |
| Certified tables, register write then step | 1.0 µs | 2.0 µs |
| Exact planner, plain Python | 7.2 µs | 30.0 µs |

On the same executor an edit is slightly slower than a message, as the spec said it would be: both are one register write and one step. Running the certified tables in place of the network is about 200 to 400 times faster, and that gain serves a message equally. So v0.3 earns a transfer result and a certification result. It earns no claim that an edit is better than a message.

## 7. Arm M: canonical memory by a training rule alone

The v0.2 core, data and schedule, unchanged, plus one rule: after every step the saved state must equal what a restart would write (memory wiped, the whole order of record shown, in another job's surroundings). No label for the memory. Measured with the frozen v0.2 scaling script.

| Core | Wait slots per leg | Task success | Distinct saved states | A sampled dictionary knows |
|---|---|---|---|---|
| v0.2 (`v2_iit_s1`) | 1 → 16 | 100% | 26,323 → 73,041 | 19.5% → 6.4% of steps |
| `v3m_s1` | 1 → 16 | 100% | 377 → 378 | 100.0% |
| `v3m_s3` | 1 → 16 | 100% | 323 → 324 | 100.0% |
| `v3m_s2` | 1 → 16 | 62% → 60% | 643 → 742 | 99.4% → 99.6% |

- Rule C1b passes (two of three seeds). Seed 2 lost the task when the rule came on and never recovered.
- On the two good seeds, development edit attempts: message 100%, predictor 100%, slot write 96.5% and 99.8%.
- A first attempt with the rule at full weight from the first quantised step broke all three seeds and was stopped (logs kept). The rule now ramps in over 3,000 steps.
- This arm keeps the v0.2 reader, so it does not extrapolate in length. It shows only that listable memory does not have to be built in.

## 8. Exploratory: no planner labels, and the operator shift

**Outcome-only training** (`v03/train_outcome.py`, section 7 of the spec). The core sees logged jobs driven by random actions and two signals from the log: was each parcel accepted, and how many gate requirements held at the end. The exact planner labels nothing. 10,000 steps, about 4 minutes.

| Core | Lowest F2 stratum, jobs fully valid | Certificate, same | Certificate, all | Simulator, all (1.44 M stages) |
|---|---|---|---|---|
| `v3o_s1` | 100.00% | clean | **clean (16,384 entries)** | 0 wrong |
| `v3o_s3` | 99.95% | clean | 3,626 wrong | 18 wrong |
| `v3o_s2` | 87.95% | 2,208 wrong | 32,593 wrong | 11,169 wrong |

The pre-set rule (two of three seeds at 99% on every stratum) passes. One seed is a planner that was never shown a correct action and is proven right on every job. One seed fell apart when the codes were switched on. Certifying still needs the rules; training does not need a planner.

**Operator shift** (v0.2 M5 protocol, 300 shifts of 8 jobs, `v3r24fix_s1`): 1,552 of 2,400 jobs meet every commitment, equal to the exact planner (v0.2: 1,551). Steps changed without need: 140 (v0.2: 200), where routes tie. Restart now gives the same plan as an edit, because the memory after a restart is identical; it still costs the 1,279 re-briefing ticks. 150 of 150 late requests declined.

## 9. Pass rules

| Rule | Result |
|---|---|
| C1a. Registers are the order of record | Pass: equal at 32,748 job steps under stress events, up to 8 legs. |
| C1b. Canonical memory trained in (arm M) | Pass: 2 of 3 seeds. |
| C2. Length extrapolation without repair | Pass: 5 of 5 T23 seeds on S strata, 5 of 5 T24x seeds on all strata; lowest 99.58%. |
| C3a. Certificate without repair | Measured: T23 4 of 5 clean on same; T24x 0 of 5 on all. |
| C3b. Certificate after repair | Pass: 4 of 5 clean on all. |
| C3c. The certificate predicts the simulator | Pass: 0 wrong actions for every clean pair; 20 of 20 witnesses confirmed for every unclean pair. |
| C4. Edit advancement rule | Clauses 1 and 2 pass. Clause 3 fails, as predicted. |
| Exploratory: no planner labels | Pass: 2 of 3 seeds. |

## 10. What this does and does not show

- The two v0.2 failures were architectural, and the fix is small: typed registers, relative addressing, a shared leg step, a discrete carry.
- A discrete carry turns a learned planner into a finite machine. That makes three things possible that sampling cannot give: a proof for every job length, a list of the planner's faults with a failing job for each, and a repair loop that ends in a proof.
- The method works here because the planning state is tiny (29 value tables). How large it can grow before the closure stops being listable is not measured.
- The schema is given: which observation field feeds which register, and the direction of the sweep. Arm M shows the register part can be learned; nothing here learns the sweep.
- The exact planner still ties the learned one on outcomes. A learned, certified planner only earns its keep where nobody has written the planner. The outcome-only arm is a controlled stand-in for that case, inside a world whose rules are known.
- An edit is a message. Two versions in a row say so.

## 11. Open, and weaker than it looks

- The final strata were authored by the assistant that built the model. Certificates were seen before the freeze, and a certificate covers final families too, so for certified cores the final strata confirm through an independent path; they are not a blind holdout. Codex's replay is open (`docs/v03_codex_challenge.md`).
- The v0.2 final items were known in aggregate before v0.3 was designed. No v0.3 core was run on them before the freeze.
- The plain repair loop is not reliable (one seed in five). The two variants that fixed it were chosen after seeing the failure.
- Arm M and outcome-only training each lost one seed in three.
- Checkpoint files saved before a config field was added hash differently from a fresh save. Every weight is bit-identical on retraining and on re-repair (`results/v03/determinism.json`).
- Latency for `v3r24fix_s2` was measured on a loaded machine; the figures above are from `v3r24fix_s1`.
- The interactive page was not checked by eye in a browser (the preview tool did not respond). Its logic is tested in Node against the Python counts (`demo/test_proof.js`).
- Arm M checkpoints and the outcome-trained cores finished after the freeze commit; their protocol and rules were in the frozen spec and their hashes are in `results/v03/ADDENDUM.json`.

## 12. How to run it

```
./smoke_v03.sh                                              # certificate re-check, v0.2 fixtures with the v0.3 core, a 16-leg correction
python stillway3/check_tables.py results/v03/cert/v3r24fix_s1_tables.json all      # needs only Python
PYTHONPATH=. python -m stillway3.train --name mycore --data t24x --seed 7           # about 2.5 minutes
PYTHONPATH=. python -m stillway3.certify runs/mycore                                # the closure, with witnesses
PYTHONPATH=. python -m stillway3.repair runs/mycore --alphabet all --out runs/mycore_fix
PYTHONPATH=. python v03/eval_edits.py runs/v3r24fix_s1 final 850390379              # F2 for one core
```

Interactive page: https://claude.ai/artifact/SQXxNxpG6GGdKP9pX1qtUm (private until shared). Build a job of up to 40 legs, pause it, correct a requirement, run the check in the browser, damage a table entry and watch the check find it.

## 13. Things that went wrong during the build

- Arm M, first attempt: the rule at full weight broke all seeds. Stopped, ramp added, logs kept.
- Repair onto unseen leg kinds for T23 cores cannot work (no spare codes). Stopped and removed from the plan.
- A launcher bug wrote six repair logs into one file (`logs/repair_shared_garbled.log`), and the seed-3 repair was cut off once and rerun from scratch with its own log.
- The first final-test launcher failed on a command-length limit and ran nothing; relaunched unchanged in content.
- The checkpoint-hash issue above.
