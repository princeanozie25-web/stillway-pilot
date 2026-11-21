# v0.5 memo: my recommendation was wrong outside my own world

For Prince Anozie, 21 November 2026. From Fable. One page. Report: `results/v05/REPORT_v05.md`.

**You told me to go with my recommendation: make program search the main line.** The first step was to test it on rules I did not write. I froze the method, then downloaded eight public rule tables. It failed all five rules I had set.

| | Program search (frozen) | Small network | Decision tree |
|---|---|---|---|
| Tables on which it reaches 99% of cases right | 3 of 8 | **8 of 8** | 7 of 8 |
| Fewest audits to get there | MONK-1 only (64 against 256) | car, nursery, balance scale, MONK-2 | none |
| Fails outright | car, nursery, balance scale, MONK-2, tic-tac-toe | none | nursery, inside the 4,096-audit cap |

## What happened

In v0.4 the search won because the language I gave it contained the rules I had written. On other people's rules, five of eight fall outside a language of two-test rules. The search then cannot reproduce the evidence and gets worse as evidence grows. A network of a few thousand weights has no such wall.

## What I now recommend

1. **Keep the frame, change the learner.** Registers, the versioned bank, the promotion gate, provenance, compiled tables and certificates were not tested here and do not depend on what proposes a rule.
2. **Default proposer: a small network that chooses its own audits.** It reached 99% on every table and halved its audits on six of eight by choosing them.
3. **Keep the search as a second proposer and let held-out audits pick.** A follow-up run after the results (exploratory) matched or beat the better learner on every table: it keeps the program on simple rules and moves to the network on the rest.
4. **Deploy a table or a program either way**, checked against audits, behind the gate.

## What I am withdrawing

- "Learn programs by search, not weights by descent" as a general rule.
- The v0.4 memo's line that consolidation should be program search through a learned library. It holds where a library's language fits. That has only been shown in my own domain.

## What is still unknown

- Whether a rule library learned from related policies helps on real policy families. These tables are single rules; none offers a family.
- Whether any of this beats a hand-written planner in a domain that has none. Four versions and this test have not touched that.

## What I need from you

A real family of related policies that someone else wrote, or Codex's time to author a hidden one. Without it the library question cannot be answered, and the library is the part that made "cheaper with experience" measurable.

Branch `v0.5`. `python -I v05/blind.py monks1` reruns one table in about two minutes.
