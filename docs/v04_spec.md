# v0.4 specification: a small planner that gets cheaper with experience

Brief: Prince Anozie, 21 November 2026 (execution brief for Fable). Start commit `69f521607d1c8193cdb59207d24f5e2d90def80d`. Branch `v0.4`.
This file, the generators, the eligibility rules, the uncertainty calculation, the seeds, the budgets and the pass rules are frozen in one commit (`results/v04/FREEZE_v04.json`) before any final run of M2 to M4. Final data seeds are derived from that commit's hash. M1 is a measurement with fixed caps and has no holdout.

## 0. Design under test

- **Registers** hold a job's current obligations. A field shown in an observation overwrites its register. Nothing else writes a fact register.
- **A bank** holds reusable procedures. It is versioned. During a job the weights are frozen and the bank version is pinned.
- **The reader** selects a procedure with explicit arguments and a bounded number of steps. Every use and its outcome are logged.
- **Between sessions** a candidate bank is trained, tested, then promoted or discarded.
- An operator's correction to today's job changes that job's registers only. A rule that applies to tomorrow's jobs is a candidate for consolidation.

## 1. M1: what the proof costs (`stillway4/gates.py`, `stillway4/reader.py`)

World: the route core of Dispatch for G gates (G = 2, 3, 4; 5 attempted). Requirements, gates, legs ahead. Deliveries and events are left out because, with registers, they never enter a route decision (v0.3).

- Exact reverse dynamic program to a fixed point; compiled to integer tables. Learned tables are read off a trained reader. Both use one file format and one C program (`v04/runner.c`), so language, integer widths, caching and loop are identical.
- Caps: 4 GB and one hour per closure and per learned run. A cap gives an **incomplete** result, recorded with everything measured. Frontiers are checkpointed.
- Reported per G: reachable exact value vectors, growth by depth, reachable (code, vector) pairs, repair rounds, shortest witness, compile and training time, peak memory, bytes on disk, per-call latency by job length, calls to break even.
- Mutation test: one reachable route entry with a single valid choice is flipped; the checker must return a failing job, confirmed by listing every route choice.
- Runtime check: every reachable module input (every closure entry) is run through the released runtimes (C tables, network) and compared with the tables.
- Learned readers, protocol 2 (fixed after the pilots, before the final runs): one code per exact value vector; training on sampled jobs, then on the exact machine itself (every vector, leg and gate state, uniformly), alternating with the certificate until it is clean or the hour ends. Protocol 1 (codes only for vectors seen in sampled jobs, then witness repair) left 181 of 500 three-gate vectors without a code and is kept as a recorded failure.
- Reader sizes: width 128 (the 85,233-parameter v0.3 reader at G = 2), 256, 512. Active parameters per decision and resident parameters are reported separately. Ceiling: one million active parameters per decision.
- Certificates name the artifact hash and the alphabet. A certificate is valid for that hash only.
- Legal messages are enumerated from the order schema (`stillway4/schema.py`) and the register rule is tested on every one of them.

## 2. M2: the approvals workflow (`stillway4/approvals.py`)

A synthetic benchmark. I wrote its rules, so a short rule engine solves it; it is a controlled benchmark, and the rule engine's results are published beside every learned arm.

**Objects.** 2 tenants. 4 jurisdictions per tenant. A document has 5 signature slots. A signature has a level (1 to 3), an age (fresh, stale), an exception tag (none, A, B) and evidence (consistent, conflicting): 36 fact combinations. Each (tenant, jurisdiction) has a current policy, named by an opaque policy ID. The learner never sees a policy's content.

**Policy family** (hidden): threshold 1 to 3; waiver none, A or B; stale accepted or not; conflict means abstain or invalid. 36 rules.

    status(rule, facts):  waived tag -> VALID;  conflicting evidence -> ABSTAIN or INVALID (by rule);
                          level >= threshold and (fresh or stale accepted) -> VALID;  otherwise INVALID
    unsigned -> PENDING.   The EXPIRED policy returns ABSTAIN for everything.

**Events** (one per step, 10 steps per document after INIT):

| Event | Shown | Effect on statuses |
|---|---|---|
| SIGN slot | facts | that slot, under the current policy of its jurisdiction; the slot is pinned to that policy |
| CORRECT slot | facts | that slot, under the policy it is pinned to (one-off correction of a fact) |
| MOVE slot | new jurisdiction | that slot, under the current policy of the new jurisdiction; re-pinned |
| AMEND jurisdiction, retroactive | new policy ID | every signed slot in that jurisdiction, under the new policy; re-pinned |
| AMEND jurisdiction, prospective | new policy ID | none now; later signatures use the new policy |
| EXPIRE jurisdiction | – | every signed slot in that jurisdiction becomes ABSTAIN; later signatures there abstain until an amendment |
| OVERRIDE slot | status | that slot takes the operator's status until it is next recomputed (job-local) |
| WAIT | – | none |

Output after every event: the status of all 5 slots. **Success of a job** = every status right after every event. Statuses outside the affected set must not change: the **protected fields**.

**Grader.** `stillway4/grader.py` is a separate plain-Python replay of the event log, written independently of the batched generator and of every learner. It reads raw events and raw outputs. Stored booleans are never trusted.

**Splits.** By policy family: 8 of the 36 rules are reserved (each parameter value appears in training, the combinations do not). By event combination: 6 ordered pairs of events on the same slot or jurisdiction never occur in training documents. Training policies: 60 IDs drawn from the 28 training rules.

**Arms, same inputs, outputs and training logs (events and statuses; no other label unless charged):**

| Arm | Memory between steps | Given by the designer | Learned |
|---|---|---|---|
| Direct answer | none; re-reads the whole event history at every step | encoding of events | everything else |
| Continuous carry | a free vector | encoding of events | everything else |
| Flat discrete codes | 8 slots of 64 codes | encoding of events | everything else |
| Text scratchpad (`stillway4/scratchpad.py`) | a 39-token string in a fixed grammar, rewritten every step by a small transformer | the grammar; the scratchpad contents as teacher labels (charged, counted in tokens) | reading and rewriting |
| **Procedural codebook** | typed registers; statuses written only by the executor | register schema; the executor (for each slot: recompute with a chosen policy, or leave untouched) | which procedure code an event selects; for each code, which slots it selects and which policy source it uses; the policy bank and the status function |
| Hand-coded macro | as above | everything above plus the selection logic | the policy bank and the status function |
| Rule engine, full replay | – | the rules, with every policy's content | nothing |
| Dependency tracker | – | the rules, with every policy's content | nothing |

**Interventions on the procedural arm** (novel-combination documents): swap the selected code for another event's code; suppress it; change one argument. For each, the outcome is compared with the hand-coded macro under the same intervention, and protected fields are compared bit for bit.

Composition of procedures is attempted only if single procedures transfer and the interventions show the code does the work.

## 3. M3: sleep (`stillway4/sleep.py`)

Six sessions per seed, two tenants. A session brings durable changes (new policy IDs, some from reserved rules; expiries) and one-off changes (CORRECT, OVERRIDE). Every decision's raw outcome is logged with its provenance (audit outcome, operator override). In-flight jobs are pinned to the bank they started with; rollback is exercised.

A policy ID the pinned bank does not know gives ABSTAIN (escalation), which is not a success.

| Arm | Between sessions |
|---|---|
| No update | nothing |
| Retrieval | an index of prior audited decisions keyed by policy ID and facts; no weight changes |
| Rehearsal | the single policy table is trained in place on a replay of all logs; no versions, no gate |
| Consolidation | new bank rows are trained on the session's log with old rows frozen; validated on held-out logged decisions; promoted or discarded; versioned |
| Consolidation + dreaming | as above, plus candidate cases the log does not contain, labelled by existing experts chosen at random, kept only if an independent check confirms the label, rejected otherwise |
| Rule induction (non-neural) | the set of family rules consistent with the log; answers where they agree |

Core weights stay frozen in every arm. A separately labelled ablation trains the core too. Update steps and data access are equal across arms; offline compute is reported. After sleep the consolidation arms are also tested with retrieval disabled.

Measured after every session, on fresh documents: learning (policies introduced that session, including fact combinations absent from the log), retention (earlier active policies), expired policies (must abstain), tenant interference (decisions of the untouched tenant on a fixed probe set must not change), and leakage of one-off changes.

**Dream check.** A candidate label is kept only if every rule of the family that is consistent with the logged outcomes gives that label. This uses the rule family (the simulator's rules), not the true rule, and no outcome the log does not contain.

**Correspondence with the Sleep framework** (Behrouz and Mirrokni, Google Research blog of 27 October 2026 and arXiv 2606.03979; blog and abstract read, full paper not): `docs/v04_sleep_correspondence.md`. This is a Stillway adaptation. The original training pipeline is not reproduced.

## 4. M4: the decision

Thresholds (the brief's proposals, adopted):

1. Held-out task success and retention of old tasks within 1 percentage point of the strongest applicable baseline.
2. At that quality, against the best qualifying neural comparator: at least 25% lower measured compute per successful job, at least 20% lower median end-to-end latency, and fewer deployed bytes.
3. Dreaming is included only if it improves held-out transfer over compute-matched rehearsal and over consolidation alone, with retention inside the 1-point margin.
4. If retrieval wins, ship retrieval. If registers win and learned procedures do not, keep registers and publish the failing intervention.

Reported whatever the outcome: p95 latency, peak RAM, training cost, sleep cost, every byte deployed (codebooks, decoder, router, adapters, index, stored examples), results against the fastest correct non-neural implementation, warm and cold, fresh and resumed, jobs per sleep cycle, and break-even volume (none if the per-job saving is zero or negative).

**Uncertainty.** Five paired seeds (1 to 5): arms share data seeds. Intervals are 95% percentile intervals from 2,000 resamples of policy families within seed, paired across arms, and all five seeds are listed.

**Compute** per job is measured two ways: wall-clock CPU time at batch one on an idle machine, and multiply-accumulate operations of the modules actually run.

**Budgets.** Apple M1 Max, 32 GB, CPU, one thread per job. One hour of pilot per arm; full cost projected from the pilot; every incomplete run recorded in `results/v04/MANIFEST_RUNS.json`.

**Holdout.** Internal: authored by the assistant that built the model. An external challenge authored by Prince or Codex can be scored with `v04/score_external.py` after the candidate hashes in the freeze file are published; format in `docs/v04_external_challenge.md`.

## 5. Regression ticket

Seed-4 two-field sweep (v0.2 M1), 19 against 20 failures on two machines: `v04/seed4_ticket.py` keeps every failing episode ID on four numeric runtimes and records the first divergent step of every episode whose verdict differs. `v04/seed4_diff.py` diffs two ID files. Outcome-trained tables are exported on each runtime and each export is certified (`v04/export_runtimes.py`).

## 6. What the pilots fixed, and the final run list

Pilots (one seed, development data, salt 0; all recorded in `results/v04/MANIFEST_RUNS.json`):

- M1: protocol 1 failed at three gates; protocol 2 certified three gates in minutes. Four gates did not finish in the hour at either size (training on the exact machine was at 79% to 88% wrong leg-step entries after 2,000 steps); it stays in the record as incomplete, with a projection.
- M2, size s: procedural codebook 99.5% and 99.2% (ordinary, novel combinations); hand-coded macro 100% and 100%; continuous carry 6.4%; flat discrete codes 4.7%. Size m gave the same 99.5% and 99.2% for the procedural arm.
- **Size chosen for the five-seed final runs: s** (the smallest; it met the 1-point rule in the pilot). Sizes m and l are reported from the one-seed pilots.
- M3 was developed on seed 1 with development data. Two protocol changes were made there: discarded candidates are retried and contradicted rows re-consolidated at later sleeps; the expiry notice is given to every arm as records.

Final runs (five seeds, data salt from the freeze commit, `v04/final_all.sh`):

| Milestone | Runs |
|---|---|
| M1 | learned readers at 2 and 3 gates, widths 128, 256, 512, seeds 1 to 5; exact closure and tables at 2, 3, 4 gates; exact closure at 5 gates under the cap; benchmarks on an idle machine |
| M2 | arms proc, macro, cont, vq, text at size s, seeds 1 to 5; interventions on every proc core |
| M3 | six sessions on every proc core, all arms |
| M4 | whole-system benchmark per seed on an idle machine; the demo trace on seed 1 |

A continuous-carry arm trained on ten times the logs is run as a labelled exploratory extra if time allows.
