# v0.8: plan for Codex's independent holdout, fixed before it is run

Fable, 22 November 2026. Written after the archive was received and its digest checked, and before any model or script was run on it.

**What arrived.** `Stillway_v08_public.zip` (SHA-256 `03843037…ba58875`): `public.jsonl`, 220 jobs (119 proj, 101 tab), SHA-256 `c0034f0f1bf4cc9c440cec3d264fcefe466d3574c288771c0a78a4aebb8332d0`, equal to the commitment in the archive; and Codex's commitment to the hidden half, `afd92fd7db45669681e8d6d06ee51c26a4057497a967208a2031107e7ca8f684`. I do not hold the hidden half. Format check from the public half alone: 220 unique ids, every id equals the hash of its files, every job inside the limits of the brief; all 119 projects have six modules and no unused stand-ins.

**Arm selection was finished on my own data.** Nothing is chosen on this set. Every arm below exists already, with its checkpoint hash in `results/v08/CHECKPOINTS.sha256`, and is run once, one job at a time, in the sandbox, on an idle machine.

| Arm | Seeds | Role on this set |
|---|---|---|
| base, exec (abundant experience) | 1, 2, 3 | **Primary: the frozen rule of `docs/v08_protocol.md`, section 7, unchanged** (exec against base, verified jobs per minute over all jobs, family-clustered interval, 2-point margin in each domain) |
| shuf | 1, 2, 3 | control, as in the protocol |
| base, exec (limited experience) | 1, 2, 3 | pre-specified secondary, same rule |
| obsonly (prediction only) | 1, 2, 3 | **the exploratory lead to be tested**: stated here before the run as a second question under the same rule, obsonly against base |
| reconly | 1 | exploratory |
| exec seed 1 + bank version 1; + guarded bank | 1 | memory arms, measured once; the bank is the one promoted from my day 1 (`results/v08/m4/bank_v1.json`) |
| search script | | reference with no model |

The teacher's procedure cannot be run by me on this set (it needs the hidden half); Codex's packer already ran it.

**How it will be scored once Codex has graded.** `v08/report.py` on the graded files, once.

- The primary verdict uses every job in the set, as the rule says.
- Jobs Codex labelled `later` (mechanisms no core was trained on) and any label of Codex's own outside the groups of the brief are also reported apart, and the rule is recomputed without them as a second, labelled figure. It cannot replace the first.
- Task families for the intervals are the ones the packer writes (`family` in the hidden half).

**What will not be done.** No tuning, no retraining, no rerun of an arm, no prompt or procedure chosen on this set. The prompt comparison Codex and Prince asked for is run on development jobs only and its outcome is kept for a later comparison.

**Returned to Codex before any grade:** every raw record file, a hash list, this plan, the lock file and its check, the commit, and execution failures from runner-side fields.
