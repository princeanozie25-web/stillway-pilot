# Stillway v0.6 report: does experience make a new policy cheaper to learn, on policies I did not write?

Fable, 21 November 2026. Branch `v0.6`. Freeze commit `2b125d10e4054aac1aaae1781b7064915b28715d` (spec, harness, converter, report script, Codex brief), made before the rule files were downloaded. Tables: `results/v06/cldr_cardinal_tables.md`, `results/v06/cldr_ordinal_tables.md`.

## 1. Verdict

On two real families of related rules, **experience with past policies does make a new policy cheaper to learn**. The biggest gain is recognising a rule the bank has seen before. What should store that experience (tables and programs, or network weights) came out differently on the two families.

| Rule (frozen) | Cardinal plural rules | Ordinal rules |
|---|---|---|
| L1. Experience helps on novel rules | **Pass**: 64 audits against 128 from scratch | **Pass**: 16 against 96 |
| L2. Programs need no more audits than bank rows on novel rules | **Pass**: programs 64; bank rows never reach 99% | **Fail**: programs 48; bank rows 16 |
| L3. A rule seen before is recognised exactly within 16 chosen audits, no cautious error | **Pass**: 8 audits, 0 errors | **Pass**: 12 audits, 0 errors |
| L4. The selector is within one budget step of the best single learner | **Pass** | **Fail**: 48 against 16 on novel rules |
| L5. Choosing audits helps the selector on novel rules | **Fail**: 64 either way | **Fail**: 64 chosen, 48 passive |

Codex's hidden family has not been run; the brief and the frozen harness are pushed (section 6).

## 2. The test

Unicode CLDR plural rules: one policy per locale, mapping an integer to a plural category, written by the CLDR contributors. Cases: n from 0 to 999, given as hundreds, tens and ones digit. Locales are split by a hash of their code into past (known in full) and new (learned from audits).

| Family | Locales | Past (distinct rules) | Distinct new rules | Novel (no past locale has it) | Seen (some past locale has it) |
|---|---|---|---|---|---|
| Cardinal | 225 | 140 (19) | 18 | 7 | 11 |
| Ordinal | 109 | 69 (18) | 14 | 10 | 4 |

Learners: `scratch` (networks on the audits alone), `bank_row` (v0.4 consolidation: a shared network with one row per policy; only a new row is fitted), `tables` (past rules consistent with the audits), `programs` (past rules as decision-list programs and every program within two constant changes), `selector` (held-out audits choose among the four), `index`. Three seeds; budgets 4 to 1,000.

## 3. Results

Audits before 99% of the 1,000 cases are right (median over rules; passive audits):

| Learner | Cardinal, novel | Cardinal, seen | Ordinal, novel | Ordinal, seen |
|---|---|---|---|---|
| scratch (no experience) | 128 | 128 | 96 | 4 |
| bank_row (experience as weights) | never | 8 | **16** | 4 |
| tables (experience as tables) | **64** | **4** | 96 | 4 |
| programs (experience as programs) | **64** | **4** | 48 | 4 |
| selector | 64 | 4 | 48 | 4 |

Audits before every case is right (the exact rule), when the learner chooses its audits:

| Learner | Cardinal, novel | Cardinal, seen | Ordinal, novel | Ordinal, seen |
|---|---|---|---|---|
| scratch | 1,000 | 512 | 756 | 628 |
| bank_row | never | 16 | never | 272 |
| tables | 256 | **8** | 384 | **12** |
| programs | 256 | 32 | 756 | **12** |
| selector | 512 | **8** | 384 | 16 |

- **Recognising a rule seen before is where experience pays.** With a memory of past rules the bank is at 99% after 4 audits (scratch: 128 on cardinal) and has the exact rule after 8 to 12 chosen audits (scratch: 512 to 628). In cautious mode it makes no error on seen rules (scratch: 3.5% of cases wrong on cardinal).
- **Novel rules gain less.** Two to six times fewer audits to 99%; nobody finds the exact rule without auditing hundreds of cases.
- **Weights or tables?** On cardinal rules the v0.4 design (a new row in a frozen network) never reaches 99% on a novel rule, and tables do. On ordinal rules it is the fastest to 99% (16 audits) and still never reaches the exact rule. A frozen network can only express rules near the ones it was trained on; a table memory falls back to learning from scratch when nothing fits (47% to 71% of the time on novel rules).
- **The program neighbourhood added nothing on novel rules.** It contains 11 of 18 new cardinal rules and 5 of 14 ordinal ones: exactly the seen ones in both families. No novel rule was within two constant changes of a past program.
- **The selector** used the table memory 90% to 99% of the time. It was safe on cardinal rules and missed the faster bank rows on novel ordinal rules.
- **Choosing audits** did not help at the 99% level. It helped a great deal for the exact rule (cardinal, seen: 8 chosen against 32 passive).

## 4. Problems with my own test

- **The 99% yardstick is too easy here.** For 6 of 18 new cardinal rules and 8 of 14 new ordinal rules the most common category already covers at least 99% of cases, so answering "other" passes. I fixed the yardstick before seeing the data. The frozen rules are reported as written; the exact-rule table above was added afterwards and is the more telling one.
- A lookup bug in `v06/report.py` (a median falling between two budgets) was fixed after the freeze. It changed no number, only made the ordinal report run.
- Groups are small: 7 and 10 novel rules, 11 and 4 seen ones. One budget step either way is within noise.
- The digit attributes are my choice and reflect what I know about plural rules in general.
- I chose this family. It has many duplicate rules across locales, which favours any memory of past rules.

## 5. Where the three tests leave the design

| Component | Evidence |
|---|---|
| Registers, versioned bank, promotion gate, provenance, compiled tables | v0.4, in my own domain only. Not tested since. |
| Learner for a rule nothing like the past | A small network (v0.5: 8 of 8 public tables). Program search only where its language fits. |
| Memory of past rules | Keep the rules themselves as tables (v0.6: exact recognition in about 10 chosen audits, no cautious error). A frozen network with a row per policy is fast when the new rule is close to old ones and cannot reach others. |
| Choosing between learners by held-out audits | Helped in v0.5; safe on one v0.6 family, not the other. Useful, not a guarantee. |
| Choosing audits | Halves audits for a network learning from scratch (v0.5); finds an exact seen rule four times faster (v0.6); no help for novel rules at 99%. |
| A hand-written planner against all of this | Still wins wherever one exists (v0.1 to v0.4). No test yet in a domain without one. |

## 6. For Codex

`docs/v06_codex_family_brief.md` asks for one JSON file with a family I have not seen. Then:

```
python -I v06/family.py family_codex.json --seeds 3
python v06/report.py codex_hidden
```

The harness `v06/family.py` is unchanged since the freeze commit; check with `git diff 2b125d1 -- v06/family.py v06/cldr_to_family.py`. `v06/report.py` has the one fix described above.

## 7. How to rerun

```
python -I v06/cldr_to_family.py data/external/cldr/plurals.json cardinal data/external/cldr/family_cardinal.json
python -I v06/family.py data/external/cldr/family_cardinal.json --shard 0 --of 4      # and shards 1, 2, 3; about 7 minutes each
python v06/report.py cldr_cardinal
```

Data: `plurals.json` (77 kB) and `ordinals.json` (20 kB) from `unicode-org/cldr-json`, in `data/external/cldr/`, fetched after the freeze commit.

## 8. Addendum: the hidden family from Codex (run after this report)

Run once at commit `e84c46e`, outputs locked in `b7120cd` before the author's breakdown was requested. Memo: `docs/v06_codex_hidden_memo.md`. Tables: `results/v06/codex_hidden_tables.md`.

| Rule (frozen) | Codex's hidden family (14 novel, 6 seen new policies; 1,440 cases; 4 decisions) |
|---|---|
| L1. Experience helps on novel rules | **Fail**: 512 audits against 512 from scratch |
| L2. Programs need no more audits than bank rows on novel rules | Pass, emptily: programs 976, bank rows never; both worse than scratch |
| L3. A rule seen before is recognised exactly within 16 chosen audits, no cautious error | **Pass**: 4 audits, 0 errors |
| L4. The selector is within one budget step of the best single learner | Pass: 512 against 512; 6 against 4 |
| L5. Choosing audits helps the selector on novel rules | **Fail**: 512 either way |

**The verdict of section 1 does not carry to this family.** "Experience makes a novel policy cheaper to learn" held on the two Unicode families and failed on the one family I had no hand in. Recognising a rule seen before held on all three. Section 5's design reading should be taken with that correction: the bank's value shown so far is recognition, not transfer.
