# Correspondence with the Sleep framework

Source: Ali Behrouz and Vahab Mirrokni, "The sleep framework: a new way for LLMs to retain knowledge in continual learning", Google Research blog, 27 October 2026, and the paper it links, "Language Models Need Sleep: Learning to Self-Modify and Consolidate Memories" (arXiv 2606.03979).

**What I read:** the blog post in full and the paper's abstract. I did not read the paper's body, so details below come from the blog's description. **This is a Stillway adaptation.** The original training pipeline is not reproduced, and nothing here is evidence about the original method.

## Component by component

| Sleep framework (as described) | Stillway v0.4 (`stillway4/sleep.py`) | Same, adapted, or absent |
|---|---|---|
| **Wake phase**: the model processes inputs and keeps temporary information in fast short-term memory (in-context memory, high-frequency layers). | A session of documents. Per-job facts sit in typed registers. Audited outcomes are logged as decision records (policy ID, facts, status) with provenance. Weights and bank are frozen and the bank version is pinned for each job. | Adapted. The short-term store is an explicit log and registers, not activations or fast weights. |
| **Sleep phase**: no new inputs; computation goes to consolidation and self-improvement. | Between sessions each arm updates. No job runs during the update; jobs in flight keep the bank they started with. | Same in outline. |
| **Parameter expansion**: pre-allocated low-rank Mixture-of-Experts blocks are unlocked and integrated into lower-frequency memory, so older parameters are not disturbed. | The bank has pre-allocated rows. A sleep trains one new row per new policy ID with every older row and the whole core frozen. A row is a 16-number vector read by a shared status function. | Adapted. One vector per policy plays the role of a low-rank expert. There is no Mixture-of-Experts router and no Hope architecture; routing is by the policy ID in the job's registers. |
| **Knowledge seeding (upward distillation)**: short-term memories are transferred into the expanded parameters by generalised knowledge distillation: on-policy distillation on self-sampled sequences plus RL-based imitation with a similarity reward (Levenshtein distance). | The new row is fitted by supervised learning on the session's logged decision records (cross-entropy on statuses). | **Mostly absent.** No teacher distributions, no self-sampled sequences, no reinforcement learning, no similarity reward. The "teacher" is the audit log itself. |
| **Synaptic pruning**: after consolidation the high-frequency temporary parameters are reset. | The consolidation arms keep no retrieval index after a sleep; they are scored with retrieval disabled, which shows what entered the bank. Logs are kept as raw evidence, not as model state. | Adapted. |
| **Dreaming, random expert selection**: during synthetic generation the router activates non-standard experts at random, mixing domains. | For each new policy, the fact combinations its log lacks are the candidate cases. Three existing experts (bank rows of other policies) chosen at random each propose a status for every candidate. | Adapted. Random experts propose labels; they do not generate text. |
| **Dreaming, curated rehearsal**: dreams are filtered by gradient-based data selection for expected benefit. | A candidate label is kept only if every rule of the policy family that is consistent with the logged outcomes gives that label. Everything else is rejected and counted. | **Different mechanism.** The filter is a logical check against the simulator's rule family, not a gradient score. It needs the rule family to be known. |
| **Dreaming, RL refinement**: fine-tune on top-rated dreams and check that downstream performance improves. | The candidate row is trained on log plus kept dreams with the same number of update steps, then validated on held-out logged decisions; it is promoted only if it passes, and a re-consolidated row only if it is no worse than the row it replaces. | Adapted. A validation gate replaces the RL loop. |
| Continual evaluation: class-incremental learning, continual translation, long context, knowledge incorporation, reasoning. | Six sessions; after each: new policies, unseen fact combinations, retention, expired policies, interference between tenants. | Different tasks and scale (16-number rows, a 74,000-parameter core). |

## What the adaptation adds that the description does not mention

- **Versioning and rollback.** Each sleep writes a bank file with a hash. An older version can be reloaded and gives its old answers.
- **Promotion or discard.** A candidate that fails validation is not installed; the policy stays unknown and the system abstains.
- **Provenance.** Operator overrides are logged apart from policy outcomes and are never trained on or indexed. The `retrieval_naive` arm shows the damage when they are.
- **A registry.** Expiry is a registry change, not a weight change.

## What cannot be claimed

- That the Sleep framework's consolidation or dreaming helps or does not help a small planner. Only this adaptation was tested.
- That the dream filter would work where the rule family is unknown. Here it is the same knowledge a non-neural rule-induction baseline uses, and that baseline is reported beside it.
