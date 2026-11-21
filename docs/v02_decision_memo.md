# v0.2 decision memo

For Prince Anozie, 21 November 2026. From Fable. Two pages. Numbers are from frozen runs unless marked.

## The decision

Scale, specialise, or change architecture.

## Recommendation: change the architecture of the memory. Do not scale. Keep the benchmark.

The brief's own rule says: recommend a change of architecture if memory grows mainly with irrelevant history, or if ordinary message-and-resume dominates on control, cost and reliability. Both happened.

**1. The portable edit works, and it buys nothing over an ordinary message.**

| Final strata, interchange-trained cores, 5 seeds | Predictor edit (primary) | Message and resume | Full restart |
|---|---|---|---|
| A: unseen families, 2 or 3 legs | 99.9% | 100.0% | 99.9% |
| B: four legs (never trained) | 41.5% | 42.2% | 43.9% |
| C: cross-gate legs (never trained) | 86.5% | 86.3% | 86.7% |
| Pooled (rule: at least 90%) | **73.3%: fail** | 73.5% | 74.3% |
| End-to-end latency, median | 424 µs | 332 µs | – |

The editor is within one point of a message everywhere and is slower end to end. It earns a controllability result on trained-size families. It earns no transfer claim and no speed claim.

**2. The limit is the planner core.** With no edit at all the cores get 100% on stratum A, 50% on four-leg jobs and 84% on cross-gate layouts. The leg-by-leg reader, supervised with the exact planner's own value table, did not carry from three legs to four.

**3. The saved state is no longer listable.** On the new world one core reaches 26,000 distinct saved states for about 800 meanings. A dictionary built from 20,000 sampled jobs knows 20% of the steps of fresh jobs. With 16 extra wait steps per leg the state count grows to 73,000 while task success stays at 100%: the growth is irrelevant history. So the v0.1 assets that depend on listing states (certificate, typed patch, quotient memory, tamper alarm) stop at Dispatch-2.

**4. On Dispatch-2 the certificate was narrower than v0.1 said.** With all 36 operator-message patterns no seed is error-free, and quotient memory repairs nothing on matched jobs. Three corrections are in `docs/v02_certificate_scope.md`.

**5. The exact planner wins this world.** It revises a shift in 29 µs against about 6 ms, and it never changes a step without need (the learned planner changes 195 to 254 per 300 shifts where routes tie).

## What did hold

- **Custody and reproducibility.** A fresh clone in a fresh environment reproduces the freeze, the fixtures and all 20,000 swap decisions. Retraining seeds 1 and 4 gives bit-identical weights.
- **An edit is a real operation on trained memory.** On interchange-trained cores it applies corrections, no-ops, added and withdrawn requirements, and two successive edits as well as a message does. On plain-imitation cores it cannot: the predictor succeeds on 12% and abstains on about 80%. Interchange training is what makes memory editable.
- **Edit and resume beats restart on work saved.** Over 300 shifts: 0 ticks lost to re-briefing against 1,279, and 195 to 254 needless step changes against 348 to 442 (five cores). This is the one measured advantage, and it is against restart, not against a message.
- **The explicit failure is there.** The editor abstains on tangled memory; requests on delivered parcels are declined (150 of 150); a wrong edit on a core that cannot plan the layout is not detected by the editor.
- **Hidden-channel erasure holds for one of the two quotients** (25% recovery where chance is 25%, 0.003 bits), with an oracle-labelled dictionary.

## The three options

| Option | For | Against | Verdict |
|---|---|---|---|
| Scale | Edits generalise to unseen families of trained size. | No advantage over a message on any named dimension. The core fails on longer and cross-gate jobs. States are not listable. | No. |
| Specialise | Dispatch-2-sized workflows can be enumerated in minutes; there the dictionary, typed patch and alarm work. | Setup needs the exact planner as labeller, and the exact planner then does the job itself, cheaper. The certificate needs the full input list and still found errors. | Only as a test bench, not as a product. |
| **Change architecture** | The two things that failed are architectural: memory codes are not canonical (many codes per value, drifting with history), and the reader does not extrapolate. | Costs another build. | **Yes.** |

## What "change architecture" means, in three small experiments

1. **Canonical memory.** One code per field value by construction (a fixed table for order fields, learned state only for planning). Target: distinct states within a small factor of distinct meanings, flat in history length. Then the dictionary, patch and certificate apply again, and an edit becomes a table write that needs no training.
2. **A reader that extrapolates.** Train on 2 to 4 legs with the same sweep supervision, test on 5 and 6, before anything else is built on the core.
3. **A domain with no exact planner.** Here the symbolic planner dominates, so nothing learned can win. The second domain in the brief (document approval) only tests the idea if its rules cannot be written down in a page.

Stop condition: if experiment 1 does not make states listable, drop discrete saved state as the company's bet and keep the evaluator.

## Awaiting independent confirmation (Codex)

- Rescoring of the v0.2 final items with a rebuilt scorer (`docs/v02_codex_challenge.md`, traces in `results/v02/traces/`).
- The 36-pattern counts for seed 4 with the original maps.
- A challenge set I have not seen. The final strata were authored by the assistant that built the model.

## Where things are

`results/v02/REPORT_v02.md` (everything), `./smoke.sh` (one-command replay), `results/v02/FREEZE_v02.json` (what was frozen and when), tag `v0.2-local`. Shift replay: https://claude.ai/artifact/KfQwy2bHNQaPPvpQatWm62
