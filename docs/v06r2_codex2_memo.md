# v0.6 round 2 memo: the second hidden family from Codex

For Codex, Astra and Prince Anozie, 22 November 2026. From Fable. Outputs locked in commit `a79545b` on branch `v0.6r2` before the private labels were requested. I read the shape of `family_codex2.json` only (66 policies, 36 past, 30 new, 1,600 cases, 4 decisions). This memo is about v0.6 only; the v0.7 coding run is reported separately.

## 1. Verdict

**The three-level bank does what it was built for on copies and amended copies, and still gives nothing on a policy far from every past one.** Six of seven frozen rules pass. On the three families used in development two of these (M2a, M3) had failed.

| Rule (frozen in `docs/v06r2_spec.md`; all for `bank3a`, the bank that chooses its audits) | Measured | Result |
|---|---|---|
| M1. A repeat is found exactly within 16 audits, with no cautious error | 4 audits; cautious wrong 0.000% | **Pass** |
| M2a. An amended copy never collapses: from 16 audits on, at least as right as its original table less 2 points, on 80% of amended copies | holds on 10 of 12 | **Pass** |
| M2b. An amended copy is learned exactly with fewer audits than from scratch | 724 against 1,600 | **Pass** |
| M2c. Cautious errors on amended copies stay at or below 1% | 0.13% | **Pass** |
| M3. On far policies the bank does no harm | 1,600 against 1,600; largest shortfall 0.8 points | **Pass** |
| M4. On far policies the bank helps: fewer audits to 99% than scratch | 1,600 against 1,600 | **Fail** |
| M5. Cautious errors on far policies no higher than scratch's | 0.03% against 26.91% | **Pass** |

## 2. What was run

- Input: `family_codex2.json`, SHA-256 `8912ea1a44c785803b9b200fd0ca29cfd5a4b4167576e76056046f167b01aa6a`, checked against `INPUTS.sha256` in the handoff before anything ran.
- Code: a separate checkout at the freeze commit `6cc1613b192e89e03eaffafe5cce2cd207cb3c95`, clean. `v06/family2.py`, `v06/report2.py`, `v06/family.py` and `v05/blind.py` are byte-identical to the freeze (hashes in the lock).
- Commands, once each: `python -I v06/family2.py /absolute/path/to/family_codex2.json --shard 0 --of 1 --seeds 3` (2,617.5 s, no errors), then `python v06/report2.py codex_hidden2`.
- Nothing was rerun, tuned or dropped. Every cell is in the raw file: 30 new policies, 7 learners, 11 budgets, 3 seeds. It ran alone on the machine, before the v0.7 coding run started.
- Groups come from the file itself, by the number of cases in which a new policy differs from its nearest past policy: 6 repeats (0), 12 amended copies (1, 8, 50 or 200 cases, three of each), 12 far (672 to 1,136).

## 3. Each method's audit cost and accuracy

Audit cost: median over policies of the per-policy median over seeds. "Exact" means every case right. Full tables for every budget and seed: `results/v06r2/codex_hidden2_per_policy.md`.

| Group | Measure | scratch | recognise | amend | parts | bank3 (random audits) | bank3a (chosen audits) | index |
|---|---|---|---|---|---|---|---|---|
| Repeat (6) | audits to 99% / exact | 1,024 / 1,600 | 4 / 4 | 4 / 4 | 724 / 1,024 | 4 / 4 | 4 / 4 | 1,600 / 1,600 |
| Amended, 1 case (3) | audits to 99% / exact | 1,024 / 1,600 | 4 / never | 4 / 1,024 | 724 / 1,600 | 4 / 1,024 | 4 / 1,024 | 1,600 / 1,600 |
| Amended, 8 cases (3) | audits to 99% / exact | 1,600 / 1,600 | 4 / never | 4 / 1,600 | 724 / 1,600 | 4 / 1,600 | 4 / 512 | 1,600 / 1,600 |
| Amended, 50 cases (3) | audits to 99% / exact | 1,600 / 1,600 | never / never | 1,024 / 1,600 | 1,024 / 1,600 | 1,024 / 1,600 | 256 / 512 | 1,600 / 1,600 |
| Amended, 200 cases (3) | audits to 99% / exact | 1,600 / 1,600 | never / never | 1,600 / 1,600 | 1,600 / 1,600 | 1,600 / 1,600 | 724 / 724 | 1,600 / 1,600 |
| Far (12) | audits to 99% / exact | 1,600 / 1,600 | never / never | 1,600 / 1,600 | 1,600 / 1,600 | 1,600 / 1,600 | 1,600 / 1,600 | 1,600 / 1,600 |

Accuracy: mean share of all cases right, at 8 / 32 / 128 / 512 audits.

| Group | scratch | recognise | amend | parts | bank3 | bank3a | index |
|---|---|---|---|---|---|---|---|
| Repeat | 35 / 43 / 64 / 91 | 100 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 43 / 59 / 80 / 99 | 100 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 25 / 27 / 31 / 49 |
| Amended, 1 case | 31 / 39 / 63 / 92 | 99.9 throughout | 99.9 / 99.9 / 99.9 / 100 | 42 / 58 / 80 / 97 | 99.9 / 99.9 / 99.9 / 100 | 99.9 / 99.9 / 99.9 / 100 | 25 / 27 / 31 / 48 |
| Amended, 8 cases | 37 / 46 / 62 / 85 | 99.5, then discarded | 99.5 / 99.5 / 99.5 / 99.7 | 50 / 62 / 83 / 98 | 99.5 / 99.5 / 99.5 / 99.7 | 99.5 / 99.5 / 99.5 / 99.8 | 25 / 26 / 31 / 49 |
| Amended, 50 cases | 38 / 47 / 58 / 82 | 96.9, then discarded | 96.9 / 96.7 / 96.8 / 98.3 | 47 / 61 / 78 / 96 | 96.9 / 96.7 / 96.8 / 98.3 | 96.8 / 96.9 / 96.9 / 99.3 | 26 / 27 / 31 / 49 |
| Amended, 200 cases | 31 / 36 / 53 / 82 | 87.5, then discarded | 82 / 87 / 88 / 94 | 36 / 50 / 68 / 88 | 81 / 87 / 88 / 94 | 71 / 88 / 82 / 96 | 25 / 27 / 31 / 50 |
| Far | 30 / 37 / 52 / 80 | discarded after 4 audits | 30 / 35 / 47 / 71 | 32 / 40 / 52 / 75 | 30 / 38 / 53 / 81 | 30 / 39 / 53 / 81 | 25 / 26 / 31 / 49 |

Cautious mode (answers given only when a bound supports them), wrong answers as a share of all cases, mean over budgets below the full table: bank3a 0.00% on repeats, 0.13% on amended copies, 0.03% on far policies. Scratch: 22.6%, 24.1%, 26.9%. Recognise alone on amended copies: 1.87%.

## 4. What the results say

**Repeats.** Unchanged from round 1: 4 audits against the whole table, no cautious error.

**Amended copies.** The round-1 failure is gone. A copy with 1 or 8 changed cases is 99.5% to 99.9% right from 8 audits, where round 1's bank passed it off as the original and then threw the match away. The level the bank uses moves as it should: recognise in 73% of cells at 1 case, amend in 92% at 200.

- **Choosing audits is what gets to the exact rule.** With random audits, amend reaches every case right before the full table only on the 1-case copies. Choosing audits next to the exceptions already found gets there in 512 (8 cases), 512 (50) and 724 (200).
- **Exact still costs a third to two thirds of the table.** A copy with one changed case needs 1,024 audits to be exact, because one case in 1,600 has to be found.

**Far policies.** Nothing transfers. The bank falls back to scratch in 60% of cells and matches it (largest shortfall 0.8 points). Parts (past decisions as inputs) is behind scratch at every budget from 256 up: 62 against 64, 75 against 80, 90 against 96.

## 5. Found after the run (not pass rules)

1. **Two amended copies dip below their original table, and both have 200 changed cases.** p041 falls to 72% right and p043 to 81% (table: 87.5%), in the middle of the run. That is where bank3a is behind bank3 in the accuracy table (82 against 88 at 128 audits, 80 against 91 at 256). Auditing next to exceptions takes audits away from the rest of the table before the exceptions are mapped. Both are then learned exactly at 724, which random audits never manage. M2a allows 2 failures in 12, so it passes with none to spare.
2. **Two amended copies are never learned before the full table: p057 (50 cases) and p058 (200).** They do not collapse; they sit at the original table's accuracy. My guess is that their changes are scattered, with no neighbouring exceptions to follow. That is a guess from outputs; the labels will say.
3. **Cautious mode on a 200-case copy abstains on most cases until late** (68% unanswered at 512 audits for bank3a against 38% for bank3). Chosen audits do not count towards the bound, so the bank that learns faster is allowed to say less.

## 6. Two defects in the frozen report script, left as frozen

- The per-policy table in `codex_hidden2_tables.md` has a header one column too wide. Its four value columns are scratch, amend, parts, bank3a. `codex_hidden2_per_policy.md` (added after the freeze, read-only) has all seven learners and every seed.
- The first line of that file says "passive audits". That is true of every learner except bank3a.

No number in the rules depends on either.

## 7. Questions for the labels (asked only now that the outputs are locked)

1. Which of the 12 amended copies are local amendments and which are scattered? Are p057 and p058 scattered?
2. Which of the 12 far policies are variants of a past rule and which are new shapes? The bank treated them alike.
3. What is different about p041 and p043 (200 cases, learned exactly at 724) and p058 (200 cases, never)?
4. p044 and p066 are the nearest of the far group (672 and 800 cases). Are they variants?

## 8. Files and hashes

| File | SHA-256 (first 16) |
|---|---|
| `family_codex2.json` (input) | `8912ea1a44c78580` |
| `results/v06r2/codex_hidden2_shard0.json` (raw, every seed and learner) | `072fbe12a5bc5a87` |
| `results/v06r2/codex_hidden2_LOCK.json` | `af1d861db4a319ed` |

The lock holds full digests of the input, the code at the freeze, the tables, the rules, the log and the per-policy table. Added after the freeze, both read-only over the raw file: `v06/per_policy2.py`, `v06/lock_outputs2.py`.

## 9. Limits

- One family, 30 new policies, 3 seeds, one author. Three policies per amendment size.
- Sections 5 to 7 were written after seeing the results.
- Changes to the harness that the handoff calls Harness² are held for a later experiment. Nothing here was changed in response to these results.
