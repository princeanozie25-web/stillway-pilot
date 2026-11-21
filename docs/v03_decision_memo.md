# v0.3 decision memo

For Prince Anozie, 21 November 2026. From Fable. Two pages. Numbers are from frozen runs unless marked exploratory. Full report: `results/v03/REPORT_v03.md`.

## What you asked for

"Keep pushing." The v0.2 memo recommended a change of memory architecture and named three experiments. v0.3 ran all three.

## What changed in one paragraph

The planner's memory is now a set of typed registers that hold the order of record, written by rule. What is learned is a small reader that sweeps a job from the last leg back to the current one and carries a single code from leg to leg. Because that code takes at most 64 values, the whole planner is a finite machine, and it can be checked exhaustively for jobs of every length.

## The results

**1. The transfer failure is fixed.** Same training data as v0.2, same final items, same harness.

| | v0.2 | v0.3 |
|---|---|---|
| Edit success, pooled (bar: 90%) | 73.3% | **96.0%** |
| Four-leg jobs (never trained) | 41.5% | 100.0% |
| Cross-gate legs (never trained) | 86.5% | 87.4% |
| Cross-gate legs, when training includes them | – | 100.0% |

**2. It carries to long jobs.** Trained on 2 to 4 legs. At 5, 6, 8, 12 and 16 legs every seed has at least 99.5% of jobs fully valid; after repair, 100.00%.

**3. The planner can be proven right for every job length.** This is new. Four of five repaired cores have a clean exhaustive certificate over every leg kind, every order, every gate state and any number of legs. The certificate matched the simulator in every case: 0 wrong actions in 1.44 million sampled steps for each certified core, and a confirmed failing job for every fault it reported. It also found faults in three cores that had made no error at all in 1.44 million sampled steps.

**4. Listable memory does not have to be built in.** One added training rule on the unchanged v0.2 core (the saved state must equal what a restart would write) cut distinct saved states from 26,000–73,000 to 378, flat in history length, with a sampled dictionary knowing 100% of steps. Two of three seeds; the third lost the task.

**5. Training does not need the exact planner (exploratory).** A core trained only from logged outcomes of random jobs was certified on every leg kind in one of three seeds, and was above 99.9% in two of three. v0.2's objection to specialising ("setup needs the exact planner as labeller") no longer holds for training. It still holds for certifying: the certificate needs the rules.

**6. The certified tables are fast.** 1 to 2 microseconds per revision, against 214 to 866 for the network and 7 to 30 for my plain-Python exact planner. A hand-compiled exact planner would match the tables.

## What did not change

- **An edit is still a message.** With registers they are the same write. The speed clause of the advancement rule fails like for like, as the spec predicted. Two versions agree, so I would stop testing this question.
- **The exact planner still ties the learned one** on every outcome in this world.
- **Leg kinds never trained stay wrong** (87%). The certificate lists exactly which.

## What is fragile

| Item | Reliability seen |
|---|---|
| Plain repair loop reaches a clean certificate | 4 of 5 seeds (the fifth needed a variant chosen after the failure) |
| Canonical memory by training rule | 2 of 3 seeds |
| Training from outcomes only | 2 of 3 seeds above 99.9%; 1 of 3 certified |
| Holdout | internal; certificates were seen before the freeze; Codex's replay is open |

The method depends on the planning state being small. Here the exact planner carries one of 29 value tables. Nothing in v0.3 measures how far that can grow.

## What Stillway has after v0.3

1. A benchmark and evaluator (v0.1, v0.2) that caught its own author's overclaims twice.
2. A pattern that works: typed registers, a learned reader with a discrete carry, a closure certificate, a repair loop.
3. A proof tool that finds faults sampling misses and hands back a failing job for each.
4. No evidence yet that any of it beats writing the planner by hand, because every test so far is in a world where the planner can be written by hand.

## The decision

Where to point the pattern next. Three options:

| Option | What it tests | Cost | My view |
|---|---|---|---|
| **A. Find the size limit.** Same world with 3 and 4 gates, more requirement types, longer dependencies. | How large the carried state can get before the closure stops being listable and repair stops converging. | About a day on this machine. | **Do first.** It decides whether B is worth doing. |
| **B. A domain nobody has written a planner for.** Learn from logs, certify what can be certified without a rule book (an edit equals a restart, unrelated commitments are untouched, values are self-consistent against a simulator). | Whether the pattern has commercial value. | A new world and evaluator; a week or more. Needs your choice of domain. | Do second, if A leaves room. |
| C. Stop model work; keep the evaluator and the proof tool as the product. | – | None. | The fallback if A shows the limit is close. |

Stop condition for A, proposed now: if at 4 gates no seed reaches a clean certificate after repair, or the closure exceeds a million entries, treat exhaustive certification as a small-world technique and choose C.

## What I need from you

1. A or straight to B.
2. If B: which domain. The brief named document approval. It only tests the idea if its rules cannot be written on a page.
3. Whether Codex should replay v0.3 before more is built. The minimal inputs are in `docs/v03_codex_challenge.md`; the certificate check needs only Python and one JSON file.

## Where things are

`results/v03/REPORT_v03.md`, `docs/v03_spec.md` (the rules, frozen first), `./smoke_v03.sh`, branch `v0.3`, tag `v0.3-local`. Interactive page: https://claude.ai/artifact/SQXxNxpG6GGdKP9pX1qtUm (private until you share it).
