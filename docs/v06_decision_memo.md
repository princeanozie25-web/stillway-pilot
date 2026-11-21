# v0.6 memo: experience does pay on real rules, mostly by recognising them

For Prince Anozie, 21 November 2026. From Fable. One page. Report: `results/v06/REPORT_v06.md`.

**What I did.** You said to go on without closeouts and that Codex would author a hidden family. I wrote Codex's brief and a frozen harness, and ran the same harness on a real family other people wrote: Unicode's plural rules for 225 locales, and its ordinal rules for 109. The method was committed before the files were fetched.

**The question.** Does a bank that has seen related policies learn a new one with fewer audited decisions?

**The answer.** Yes on both families, by the rule I froze. The gain is large when the new rule matches one seen before and modest when it does not.

| | Without experience | With a memory of past rules |
|---|---|---|
| A rule seen before: audits to 99% of cases right (cardinal) | 128 | 4 |
| A rule seen before: audits to the exact rule, choosing them | 512 to 628 | 8 to 12 |
| A rule seen before: wrong answers in cautious mode | 3.5% of cases | none |
| A novel rule: audits to 99% | 128 and 96 | 64 and 16 |
| A novel rule: audits to the exact rule | about the whole table | 256 to 384 |

**What was not settled.** Whether experience is better kept as tables or as network weights. On cardinal rules the v0.4 design (a new row in a frozen network) never reached 99% on a novel rule and tables did. On ordinal rules it was the fastest. Four of my five frozen rules passed on cardinal rules and two of five on ordinal rules; "choosing audits helps" failed on both.

**What was wrong with my test.** The 99% yardstick is too easy on this data: for about half the new rules one category covers 99% of numbers. I report the frozen rules as written and added the exact-rule measure afterwards.

## Where three tests leave the design

1. Keep past rules as tables in the versioned bank. Recognising a seen rule is the clearest, cheapest win, and it comes with no cautious errors.
2. Learn a rule nothing like the past with a small network. Use program search only where it fits.
3. Treat the frozen-network row (v0.4 consolidation) as one proposer among several, not the store of record.
4. Let held-out audits choose between proposers, knowing it is not always right.

## Still open

- Codex's hidden family. The brief is `docs/v06_codex_family_brief.md` on branch `v0.6`; the harness is frozen at `2b125d1`. When the file arrives it is two commands.
- A domain with no hand-written planner. Every version so far has had one, and it has won.
- Registers, procedures and sessions have only been tested in my own approvals world.
