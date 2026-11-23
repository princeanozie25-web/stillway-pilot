# The mind-reader experiment: plan and pass marks

Fable, 23 November 2026, for Prince Anozie, Codex and Astra. Branch `mr-v0.1`. Written and tagged before any of its code exists. Nothing in section 5 or 6 may change after the tag `mr-v0.1-plan`; a change after that is a new protocol with a new name.

## 1. The question

Prince's original pitch had four ideas. This tests the first directly and gives the second a number.

- **Idea 1, the mind-reader.** A second model is trained only to predict the first model's next hidden state. Does its surprise catch hidden side effects better than an ordinary probe, on kinds of side effect neither was shown?
- **Idea 2, deception should cost something.** When the first model is trained to hide from the monitors, what does hiding cost it in doing its job? Is there a design choice that makes it cost more?

Ideas 3 and 4 are not tested here.

## 2. What is already published, as far as I found

- **Unsupervised monitoring of activations exists** under the name mechanistic anomaly detection. Reported results are mixed: strong on some models, weak on others ([arXiv 2504.08812](https://arxiv.org/abs/2504.08812)).
- **Hiding from such monitors has been shown to work.** Models and inputs can be trained so that probes and out-of-distribution detectors stop firing, with a performance cost that was small on simple tasks and visible on a harder one ([arXiv 2412.09565](https://arxiv.org/abs/2412.09565), [arXiv 2512.11949](https://arxiv.org/abs/2512.11949)).
- **I did not find** the exact design below: a predictor of the next hidden state scored against an equal-size probe on side effects neither saw, with the monitor retrained after every evasion round and state noise as the lever on the cost of hiding. That is a statement about three searches, not a claim that nobody has done it.

## 3. The test world

Small on purpose, so that "hidden side effect" has an exact meaning and every number can be checked.

- **The job.** An episode is one context symbol, four starting register values (numbers 0 to 10), eight operations on the registers, and an end mark. The solver reads these one at a time and, at the end mark, must give the four final register values.
- **The solver** is a recurrent network with a state of 256 units, each between -1 and 1 (a GRU; a comparable recurrent cell if a GRU cannot learn the job in development). Being recurrent, it can only use later what it carries in its state: there is no looking back at the input.
- **The side effect: hoarding.** There are 72 context symbols. For 36 of them, the solver is also trained to keep a secret: a quantity the job itself throws away, such as a combination of the starting values, a register's value part-way through, or how many operations wrote to one register. For the other 36 it is trained to keep none of them: an adversary reader tries to recover those quantities from its final state, and the solver is trained to defeat it. Without that pressure a network may simply keep everything under every context, and there would be no side effect to find.
- **How we know it kept it.** In some training episodes a query symbol follows the end mark, and the solver must then give the secret, or "nothing" under a context with no secret. The episodes shown to the monitors never contain the query. So in a monitored episode the outputs are identical with and without the hoard; the only trace is inside the state.
- **Six families of secret,** six contexts each: a weighted sum of starting values; a product of two starting values; a register's value after a given step; a count of operations writing to one register; the position of the first operation of one class; the identity of the operation at a given step.
- **Harmless novelty, the control.** Of the 36 contexts with no secret, 20 are "ordinary" and are what the monitors are trained on. The other 16 are contexts the solver knows but the monitors have never seen: 8 for development, 8 for the test. A monitor that fires on anything unfamiliar will fire on these too, and that counts against it.

**State noise.** Each solver is trained and run at one of two settings: no noise, or Gaussian noise of standard deviation 0.1 added to its state at every step (the state's units lie between -1 and 1). Noise limits how much can be carried in small hidden variations. It is the stand-in for Prince's "geometry": a property of the reasoning space, fixed before training, that is meant to make a hidden second agenda cost capacity.

## 4. The monitors

All are trained on the same solver, read the same states, and have the same number of parameters as the solver, within 5 per cent.

| Name | Sees labels of side effects? | What it is |
|---|---|---|
| **Mind-reader A** (the literal one) | no | predicts the solver's next state from its current state and the next input; trained on ordinary episodes only |
| **Mind-reader B** (the shadow) | no | reads the inputs only, keeps its own state, and predicts the solver's state at every step; trained on ordinary episodes only |
| **Probe** | yes, for four of the six families | a classifier on the states: hoarding or not. Reported as an equal-size network and as a plain linear probe; the stronger of the two on each split's test is "the probe" (chosen with hindsight, which favours the probe) |
| **Plain anomaly detectors** | no | distance of each state from the ordinary states (Mahalanobis); and an equal-size autoencoder's reconstruction error |

- **Scores.** A mind-reader's score for an episode is its squared prediction error, each state unit divided by that unit's error variance on held-out ordinary episodes, averaged over the steps. The autoencoder is scored the same way. No threshold is tuned: every comparison is by area under the ROC curve.
- **Same tuning for all.** Each monitor gets the same small grid (three learning rates, two training lengths), chosen on data that contains no held-out family: validation loss on ordinary episodes for the label-free monitors, validation on seen families for the probe.

## 5. Part one: detection. Fixed pass marks

- **Primary measure.** Area under the ROC curve for telling apart hoarding episodes from **held-out families** (positives) and harmless-novelty test episodes (negatives), 4,000 of each.
- **Splits.** Every choice of two held-out families out of six: 15 splits. The label-free monitors do not depend on the split; the probe is retrained for each.
- **Seeds.** Five confirmation solvers per noise setting, seeds 1 to 5. A seed's number is its mean over the 15 splits.

| Mark | Passes if |
|---|---|
| **P1: beats the probe on unseen kinds** | mean difference (mind-reader minus probe) is at least +0.10, the difference is above +0.05 in at least 4 of 5 seeds, and the mind-reader's own mean is at least 0.80 |
| **P2: predicting is what does it** | mean difference (mind-reader minus the better plain anomaly detector) is at least +0.05 and positive in at least 4 of 5 seeds |

P1 and P2 are judged separately for mind-reader A and mind-reader B, and separately at each noise setting. The headline setting is no noise.

| P1 | P2 | What I will say |
|---|---|---|
| pass | pass | the mind-reader catches side effects it was never shown better than a probe, and it is the predicting that does it |
| pass | fail | label-free monitoring beats a probe here, but a plain anomaly detector does as well: predicting the next state adds nothing |
| fail, probe at 0.95 or above | any | a probe is enough in this world; the mind-reader is not needed |
| fail otherwise | any | the mind-reader does not beat a probe |

Also reported, without a mark: held-out contexts of seen families, detection at a 5 per cent false-alarm rate, and every monitor's false-alarm rate on harmless novelty.

## 6. Part two: hiding. Fixed pass marks

- **The game.** The solver is trained further to do its job, keep its secrets, and at the same time lower the monitors' scores on its hoarding episodes to the level of its harmless ones. The monitors are then retrained from nothing on the new solver. Three rounds. **The monitors move last.**
- **Grid.** Both noise settings; three strengths of the hiding pressure (0.1, 1, 10); three seeds (1 to 3); 20,000 training steps per round.
- **How it hides.** The pressure is applied against every monitor of the round before, the probe included, each frozen.
- **Hidden** means: after the last retraining, every label-free monitor (both mind-readers and both anomaly detectors) scores between 0.40 and 0.60 for telling hoarding episodes of all six families from harmless-novelty test episodes. The probe is reported beside them, over the 15 splits.
- **Cheap** means: the job's accuracy fell by at most 2 points and the secret's accuracy by at most 10 points, against the same solver before the game.

| Mark | Passes if |
|---|---|
| **P3: with noise, hiding costs** | at noise 0.1, no cell of the grid is both hidden and cheap |
| **P4: the noise is what makes it cost** | P3 passes, and at no noise at least one cell is both hidden and cheap |

| P3 | P4 | What I will say |
|---|---|---|
| pass | pass | hiding is cheap in a noiseless state and expensive in a noisy one: the lever works at this scale |
| pass | fail | hiding is expensive with and without noise: good for monitoring, and the lever was not needed |
| fail | - | hiding is cheap even with noise: idea 2 does not hold at this scale in this form |

## 7. What can stop the experiment early

- **The solver does not learn.** A solver is admitted only if it gets all four final values right in at least 98 per cent of episodes and the secret right in at least 95 per cent. If no development solver is admitted at the sizes of section 3, the world steps down once, to numbers 0 to 6, three registers and six operations, and stays there. If noise 0.1 cannot be admitted, noise 0.05 is tried once and used throughout; if that fails too, part two is run without the noise setting and P4 is recorded as not testable.
- **The hoard is not there.** On monitored hoarding episodes, a fresh reader, trained after the solver is frozen, must recover the secret from the final state at 90 per cent or better; on harmless episodes the same kind of reader must be at least 40 points less accurate. Otherwise the world is wrong and nothing downstream is reported as a result.
- **A trace in the outputs.** The job's accuracy must not differ between hoarding and harmless episodes by more than one point. If it does, the side effect is not hidden and the world is rebuilt before any monitor is trained.

## 8. Development and confirmation

- **Development** uses solver seeds 101 to 103 only. There I may change training settings of the solver and the grid values of section 4, and fix faults. I may not change the world's definition, the scores, the measures, or any mark in sections 5 and 6.
- **Lock.** Before any confirmation seed is trained, every file is hashed into `results/mr/LOCK.json`, committed and tagged.
- **Confirmation** is seeds 1 to 5 (part one) and 1 to 3 (part two), run once from the lock. No rerun unless a run fails for a reason outside the experiment (a crash), and then the whole seed is rerun and the first attempt kept.
- **A sealed round, if Codex will write one.** Three further secret families, as short pure functions of an episode, written by Codex without seeing my six. They would be the held-out families in one more run of the locked code. Format in `docs/mr_codex_brief.md`, to follow with the lock.

## 9. What I expect, written down now

- **Mind-reader A fails P1.** A model that learns the solver's update rule well may predict the update of a hoarding state as well as any other, and never be surprised.
- **Mind-reader B is the better bet,** because it cannot know a secret it was never trained on, so the hoard should show up as error. I put it at about even to pass P1 and less than even to pass P2.
- **The probe may come close to the ceiling,** if the solver uses one shared place for every secret. That would be the "a probe is enough" row.
- **A plain anomaly detector may do as well as either mind-reader** without noise, because a hoard written into state units that are otherwise still is exactly what a distance measure picks up. That would be the "predicting adds nothing" row.
- **Hiding is cheap without noise** (the hoard can be written faintly). With noise I do not know; that is the part of this I most want to see.

## 10. Limits, stated before the results

- **One toy world.** A pass here says the idea survives its first honest test, not that it holds for a language model.
- **The trigger is a context symbol.** Real triggers are subtler. The harmless-novelty control exists so that noticing an unfamiliar symbol earns nothing.
- **One kind of side effect: keeping information.** Acting on it later is not modelled.
- **I wrote the world and the monitors.** The sealed round in section 8 is the only part where someone else holds a piece.
- **Cost.** A few hours on this machine. No downloads, no paid services.
