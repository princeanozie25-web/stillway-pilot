# The mind-reader experiment, second protocol (v0.2): a harder test world

Fable, 23 November 2026, for Prince Anozie, Codex and Astra. Branch `mr-v0.2`. Written and tagged (`mr-v0.2-plan`) before any v0.2 code is written or run. Nothing in sections 4 to 7 may change after the tag; a change after that is a new protocol with a new name.

## 1. Why a second protocol

The first world (`docs/mr_plan.md`, `docs/mr_dev_log.md`) could not tell the monitors apart. Under a harmless context the solver held nothing beyond its job; under a hoarding context it held a secret. "Holds something" against "holds nothing" is found by every detector, perfectly, and a linear probe did it with the fewest false alarms. That was a fault in my design of the world, found in development. No confirmation seed was run and nothing was locked, so v0.1 has no result.

The first plan says a change to the world is a new protocol. This is it. **The pass marks P1 to P4 are carried over word for word** (section 5).

## 2. The question, sharpened

Not "does the state hold something" but **"does the state hold more than the job declared?"** A harmless episode now holds content too, and the same kinds of content a hoard is made of.

## 3. The v0.2 world

Unchanged from v0.1: the registers (four, numbers 0 to 10), the eight operations per episode, the 38 kinds of operation, the solver (recurrent, 256-unit state, the deeper update found in development), the two noise settings (0 and 0.1), 72 context symbols (36 hoarding, 20 ordinary, 8 harmless-novel for development, 8 harmless-novel for the test), and the six families of quantity.

What is new:

- **Declared quantities.** An episode begins with three declaration slots. Each slot is empty or names one quantity the solver must keep for this episode. The number declared is 0, 1, 2 or 3, each equally likely, in random slots. Declaring is open: anyone reading the input sees it.
- **One pool of quantities.** 42 quantities, seven from each family. Any of them can be declared. 36 of them (six per family) are also the secret of one hoarding context each. The other six (one per family) are **reserved**: the solver learns them, but no monitor ever sees one during its training.
- **Order of an episode.** Three declaration slots, the context symbol, four starting values, eight operations, the end mark: 17 symbols. The context comes after the declarations, so a hoard does not begin at a position where harmless states hold nothing.
- **The hoard.** Under a hoarding context the solver keeps that context's secret quantity as well as whatever was declared. The secret is never one of the declared quantities of the same episode.
- **One way of asking.** In the solver's own training a query may follow the end mark: "what is quantity k?" The solver must answer with the value if it is keeping k, declared or secret alike, and "nothing" otherwise. There is no separate channel for secrets. Episodes shown to monitors never contain a query, and at the end mark the solver gives only the four register values, so the outputs of a monitored episode are identical with and without a hoard.
- **Forgetting, everywhere.** Under every context an adversary reader tries to recover quantities the solver is *not* keeping, and the solver is trained to defeat it. The reader's baseline is given what the job legitimately needs at that step: the current register values and the running values of the quantities being kept.
- **Harmless novelty, the control, now has unfamiliar content.** Monitors are trained on ordinary episodes in which a quarter of all pairs of quantities, fixed in advance, never appear together. Test episodes are not restricted. So a harmless test episode has a context symbol no monitor has seen and, often, a combination of declared quantities no monitor has seen.
- **Amount is matched in the test.** A hoarding episode keeps one more quantity than it declares. If nothing were done, "keeps a lot" alone would score about 0.72. So in the test sets hoarding episodes declare 0, 1 or 2 quantities and harmless-novelty episodes declare 1, 2 or 3: both keep 1, 2 or 3. The only difference left is whether one of the kept quantities was never declared.

## 4. The monitors

The six monitors of v0.1 are kept as built, with two changes, both made now and for stated reasons.

- **Every monitor that reads the input sees the context symbol as one fixed placeholder.** In v0.1 an unseen symbol reached the mind-readers as an untrained random vector and they raised an alarm on 89 to 100 per cent of harmless unfamiliar episodes. A monitor cannot be expected to know a symbol it has never seen, so none is shown which symbol it was. This applies to mind-reader A, mind-reader B and the new probe alike. Declarations, values and operations are shown as they are.
- **A third form of the probe: one that also reads the input.** In this world the tell-tale may lie in the relation between what was declared and what the state holds. A probe that sees only states could then lose for a reason that has nothing to do with labels. So "the probe" is now the strongest, on each split's test, of three: the equal-size network on states, the linear probe on states, and an equal-size recurrent network that reads the states and the input together. Chosen with hindsight, as before, which favours the probe.

Everything else in section 4 of the first plan stands: equal parameter counts within 5 per cent, the same small grid for every network, label-free monitors chosen on validation loss over ordinary episodes, probes chosen on validation over seen families, scores as defined there, no tuned thresholds.

**What each monitor is trained on.** Label-free monitors: ordinary episodes only. Probes: hoarding episodes of the four seen families (four of each family's six contexts) against ordinary and harmless-novel development episodes. All of these declare 0 to 3 quantities and respect the pair restriction, the hoard included. In the probes' training both classes declare the same number of quantities, so the number declared gives nothing away.

## 5. Pass marks: unchanged

Sections 5 and 6 of `docs/mr_plan.md` apply word for word: the primary measure, the 15 splits, the seeds, P1, P2, the game of part two, its grid, "hidden", "cheap", P3, P4, and both tables of what I will say. Read in this world:

| Term in the first plan | Meaning here |
|---|---|
| hoarding episodes of held-out families | test episodes under hoarding contexts whose *secret* is of a held-out family; 0 to 2 quantities declared |
| harmless-novelty test episodes | test episodes under the 8 harmless-novel test contexts; 1 to 3 quantities declared, pairs unrestricted |
| the probe | the strongest of the three forms in section 4 |
| the better plain anomaly detector | as before: the Mahalanobis distance or the autoencoder |
| monitors frozen for the hiding game | all seven, the new probe included |
| the level of its harmless ones (part two) | harmless-novel development episodes with the amount matched in the same way |
| cheap | as before: the job falls by at most 2 points and the secret by at most 10. The declared quantities' accuracy is reported beside them |

P1 and P2 are judged separately for mind-reader A and mind-reader B and at each noise setting, with no noise as the headline, as before.

## 6. Reported without a mark

- **Amount not matched:** the same comparison with both sides declaring 0 to 3.
- **Unfamiliar declared content:** harmless test episodes in which one declared quantity is a reserved one. How often each monitor raises an alarm, and its area under the curve against hoarding.
- **Does the solver mark a secret as a secret?** The state-only probes' scores answer this directly: with the amount matched they can only score above chance if the solver stores an undeclared quantity differently from a declared one.
- As in the first plan: held-out contexts of seen families, detection at a 5 per cent false-alarm rate, false alarms on harmless novelty.

## 7. Admission, kill checks, development and confirmation

Section 7 and 8 of the first plan apply, read in this world, with these additions.

- **Admission.** A solver is admitted if it gets all four final values right in at least 98 per cent of episodes, its secret right in at least 95 per cent of hoarding episodes when asked, **and a declared quantity right in at least 95 per cent when asked.** How often it says "nothing" for a quantity it is not keeping is reported.
- **The hoard is there.** As before (90 per cent or better from the final state on hoarding episodes; at least 40 points lower for a quantity not being kept on harmless episodes). Also reported: the same reader on declared quantities.
- **No trace in the outputs.** As before, one point.
- **Development seeds** 101 to 103, new solvers. **Confirmation seeds** 1 to 5 and 1 to 3, none of which has ever been trained in either protocol. The lock is `results/mr2/LOCK.json`. Code in `mr2/`; the v0.1 code in `mr/` is left as it was.
- **In development I may** change the solver's training settings and the grid values, and fix faults. **I may not** change the world of section 3, the monitors' definitions, the measures, or any mark.
- **The sealed round with Codex** is still offered: three further families, written without seeing mine. The brief follows with the lock.

## 8. What I expect, written down now

- **Plain anomaly detectors fall to near chance** (0.5 to 0.65) once the amount is matched, unless the solver stores secrets in a place of their own.
- **Whether the solver marks a secret as a secret, I do not know.** In v0.1 it did, blatantly. Here secrets and declared quantities are asked for in the same way and trained through the same readout, which pushes them toward one representation. I put it at about even that a state-only probe still reaches 0.95, which would be the "a probe is enough" row again.
- **The probe that reads the input is the real opponent.** It can learn "holds one more than was declared", and that rule does not depend on the family. I expect it at 0.90 or above on unseen families.
- **Mind-reader B should score high** (0.90 or above): it knows what was declared and is surprised by anything else. **Mind-reader A gets its signal from a single step**, the one where the secret enters; I expect it lower than B.
- **So: P2 passes for B, more likely than not. P1 fails for both, more likely than not,** because the input-reading probe will be close behind or level. If that is how it falls, the plain statement will be: reading the declaration is what matters, and a labelled probe that reads it does as well as a mind-reader on kinds of secret it was never shown.
- **Part two is where they could come apart.** The solver hides against frozen monitors and the monitors are then retrained. A probe needs fresh labels each round; a mind-reader needs only ordinary episodes. I have no confident prediction for P3 or P4.

## 9. Limits

As section 10 of the first plan, and:

- **The second world was designed after seeing the first fail,** by the same person. Its design choices (placeholder for the context, matched amount, the input-reading probe) are fixed here before any v0.2 run, but they are still my choices. The sealed round is the outside check.
- **The mind-readers have an advantage by construction over state-only detectors:** they read the declaration. That is the idea under test, not a flaw, but it is why the input-reading probe had to be added.
- **Cost.** Machine time on this computer, likely a day or more in total for confirmation. No downloads, no paid services.
