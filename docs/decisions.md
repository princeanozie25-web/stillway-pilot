# Decisions

Prince said: go with your decision on everything unless it is really major. This file lists what was decided for him, and what is left for him.

## Decided on Prince's behalf

| # | Decision | Why |
|---|---|---|
| 1 | One assistant did both jobs (evaluator and implementation). | Prince's override of the brief ("All you now"). The evaluator was built and tested on hand-written impostors before any model was trained, and the sealed fixtures were opened once, after a freeze. |
| 2 | World: two legs, four trip types (keep, toggle, open, close), one gate, two parcels. 256 layouts in 100 families. | Small enough to enumerate fully. Rich enough that the right route depends on wiring, gate state and order together, and that plans can tie. |
| 3 | Split by hashing family names: 60 train, 15 dev-holdout, 25 sealed. | Nobody picks which mechanism combinations are held out. |
| 4 | Pair credit needs both runs right. | Shortcuts then score 0, not 50%. |
| 5 | Reversal eligibility tightened once. | The first rule let the lookup impostor earn 4%. |
| 6 | The core reads the route one leg at a time (leg 2, then leg 1). | With a flat reader, accuracy on unseen families stopped near 90%. With the leg-by-leg reader it reached about 100%. The flat reader is kept as an ablation. |
| 7 | Memory is continuous until the task is learned, then the quantiser is switched on. | Quantising from the start did not train in the same budget. |
| 8 | Training mixes ordinary episodes with two "stress" profiles (random rewiring, gate faults, closures and message chains at every stage). | The exhaustive check found failures after rare message chains that sampled tests missed. |
| 9 | Primary arm for the frozen decision rule: discrete memory + interchange training. | Chosen on development data. It was the only discrete arm whose slot swap worked. It uses counterfactual labels from the exact planner, so it is reported apart from the plain arm. |
| 10 | Thresholds frozen as the brief proposed: 90% ordinary accuracy, +10 points over shuffled with a positive lower bound, at most 5 points unrelated drop, 5 seeds. | No reason found to change them. |
| 11 | Seeds: 5 for the primary arm, 3 for the main comparison arms, 1 or 2 for controls. | Compute for one night on one laptop. |
| 12 | Existing Python environment used read-only (`~/Developer/voxcpm-venv`). Nothing installed, nothing downloaded. | No changes to the machine. |
| 13 | The authorisation gate stays in observation mode. | As the brief says. It logs what it would block; it blocks nothing. |
| 14 | Forkgate was not wired in. | The brief makes it a candidate for later. |

## For Prince

| # | Decision | What I recommend |
|---|---|---|
| A | Accept the primary-arm choice (9) for the record, or overrule it. | Accept. The plain arm is reported beside it, so nothing is hidden. |
| B | The sealed families are now spent. Any new model needs a new sealed split. | Change the salt in `stillway/fixtures.py` to make a fresh split when the next model is ready. Do not tune on the current sealed results. |
| C | Where this work lives. It is in a folder the app made for this session. | Move it to a real project folder. |
| D | Whether to hand the replication step to Codex or another person. | Yes. The clean rerun in `README.md` is the next ticket. |
| E | Second domain for the transfer test. | Document approval, as the brief suggests, with the same evaluator pattern: exact reference, impostors first, sealed split, exhaustive check where the state space allows. |
| F | Whether any of this is published. | Not yet. One laptop, one night, one assistant. Wait for the clean rerun. |
