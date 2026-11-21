# Beyond the v0.4 brief: learn programs by search, not weights by descent

Fable, 21 November 2026. Done after Prince said to go past the brief where something important was being missed. Exploratory, made after the v0.4 freeze; nothing frozen was changed. Tables in full: `results/v04/x/tables.md` (`v04/x_report.py`).

## The idea

Four versions gave the same result in different clothes. Wherever the thing to be learned was a small discrete object, a search that checks candidates against the evidence beat gradient descent, and its output could be verified:

| Version | What gradient descent learned | What beat it |
|---|---|---|
| v0.3, v0.4 M1 | a route planner, as tables read off a network | the exact dynamic program (same tables, no training) |
| v0.4 M2 | which procedure an event selects | a hand-written macro |
| v0.4 M3 | a bank row for a new policy | rule induction over a family given by the designer |

Each of those competitors needed a person to write something down. The question I had not asked: can the system find those objects itself, by search, from the same logs the networks were trained on? Then nothing is hand-written and nothing is a weight.

So the proposal is a different stack. **The bank holds programs. Sleep is program search with verification. A network, if there is one, only proposes candidates.**

## Three experiments, five seeds each

### A. Procedure selection by search (`v04/x_synth_procedures.py`)

A procedure for one event kind is a pair: which slots to recompute (a truth table over two facts about a slot) and under which policy. There are 42 candidates per event kind. Each is run on 3,000 logged documents through the frozen executor; the one that reproduces the logged statuses best is kept; ties go to the one that recomputes fewest slots. No test document is used.

| | Ordinary documents | Novel event combinations | Protected statuses changed (novel) |
|---|---|---|---|
| v0.4 gradient-learned selection | 99.31% | 98.25% (one seed at 93.98%) | 255 |
| Hand-coded macro | 100.00% | 100.00% | 0 |
| **Found by search** | **100.00%** | **100.00%** on every seed | **0** |

- 672 candidate evaluations, about 50 seconds per seed.
- The same eight procedures on all five seeds. They are simpler than my hand-coded ones: the tie rule removed cases the macro covered needlessly.
- This answers the question I put to Prince at the end of v0.4 ("hand-code it, or fix learned selection"). Neither. Search for it.
- It still used the trained network's status function. Experiment C removes that.

### B. A bank of programs with a learned rule library (`v04/x_library.py`)

Nobody gives the rule family. For each of the 60 base policies the shortest program in a generic language (a decision list of up to 3 rules, each a test of at most two facts) that reproduces its logged decisions is found. Constants become holes. The distinct skeletons are the library: reusable procedures with explicit arguments. A new policy is consolidated by finding the library members consistent with its logged decisions.

| | |
|---|---|
| Library built from the logs | 13 to 14 skeletons, 35 to 39 rules, in 0.7 s |
| True rules it contains | 31 to 33 of 36 |
| Reserved rules (never in training) it contains | 5 of 8 on every seed |
| Rules it contains that are not in the true family | 4 to 6 |

On the same documents as the frozen M3 runs (5 seeds, 6 sessions, every second document):

| Bank | New-policy documents fully right | Older-policy documents fully right | Wrong decisions on new policies | Abstentions on new policies |
|---|---|---|---|---|
| **Learned library, best guess where undetermined** | **91.7%** | 98.8% | 738 (1.47%) | 165 (0.3%) |
| Learned library, answers only what is entailed | 88.2% | 98.7% | 155 (0.31%) | 1,279 (2.5%) |
| Rule family given by the designer | 89.1% | 98.7% | 19 (0.04%) | 1,285 (2.6%) |
| Shortest generic program, no library | 89.5% | 98.5% | 909 (1.81%) | 226 (0.5%) |
| v0.4 consolidation + dreaming | 81.2% | 98.7% | 699 (1.39%) | 2,790 (5.6%) |
| v0.4 rehearsal | 86.5% | 82.7% | 741 (1.48%) | 213 (0.4%) |
| v0.4 retrieval | 27.5% | 87.9% | 14 (0.03%) | 12,673 (25.3%) |

- The library bank beats every v0.4 neural arm on new policies and keeps old ones, with no family given and no training.
- It has two modes, and the choice is a product decision. Answering only what the evidence entails gives a fifth of the wrong decisions of any neural arm and abstains on 2.5%. Guessing where undetermined gets the most documents right and is wrong as often as the neural arms.
- A neural arm's errors are silent. The library's cautious mode turns most of them into abstentions.

**Experience makes a new policy cheaper to learn, and this is where:**

| What the system has | Audited decisions to pin a new policy down, cases as they arrive | Cases the system chooses |
|---|---|---|
| No family: an index of seen cases | 841 | 36 |
| The learned library | 21 | 4.6 (at most 5) |
| The family given by the designer | 22 | 4.7 (at most 5) |

A library learned from yesterday's policies cuts the audits a new policy needs by a factor of 40, and by a factor of 180 if the system picks which case to escalate. This is the "cheaper with experience" the brief asked for, measured in the unit that costs money: human decisions.

### C. The whole planner from raw logs, no network (`v04/x_no_network.py`)

Procedures and bank found together, from the 20,000 logged documents alone. For a candidate procedure, the bank it implies is read off the logs by vote, the logs are replayed, and the best candidate is kept.

| | Ordinary documents | Novel combinations | Protected statuses changed | Time | Deployed bytes |
|---|---|---|---|---|---|
| **Induced from logs, no network** | **99.99%** | **99.995%** | 0 | about 90 s | 2,176 |
| v0.4 procedural codebook (network, compiled) | 99.31% | 98.25% | 255 | about 20 minutes of training | 2,418 |
| Hand-coded macro with learned bank | 100.00% | 100.00% | 0 | about 1 minute of training | 2,418 |

- Four of five seeds are at exactly 100%; the fifth misses 3 documents of 8,000; its bank has one cell (a policy with a fact combination that never occurred in the logs) where it abstains.
- 2,158 to 2,160 of 2,160 bank cells equal the true rule. Gradient steps: 0. Parameters: 0.
- The result is eight readable lines of procedure and one 36-entry table per policy. It can be checked by eye.

## The stack this suggests

| Phase | What happens |
|---|---|
| Wake | Typed registers. Compiled tables. Every use and outcome logged with provenance. Where the evidence does not entail an answer: abstain, or guess and flag. When escalating, pick the case that splits the remaining candidates. |
| Sleep | Search for programs consistent with the log: procedures, policy tables through the library. Replay to verify. Promote into a versioned bank, or discard. Abstract newly solved policies into the library. |
| Network | Optional. A proposer of candidates when the space is too large to enumerate. Never the thing deployed, never the judge. |

This is close in spirit to wake-sleep library learning for program synthesis (DreamCoder, Ellis et al. 2021), which I am citing from memory and have not re-read. It is not new to machine learning. It is new to this project, and it is the opposite of the Sleep framework's move: there, experience is consolidated into weights; here, into programs that can be read, diffed, versioned and proven.

## What is weak here

- **Exploratory.** Made after the freeze, scored on documents the frozen arms were already scored on. I ran the library on seed 1 once before adding the best-guess mode.
- **I wrote the languages.** The executor's 42 or 48 candidates and the generic decision-list language were written by me with this domain in view. They are generic in form, but a domain I did not design is the real test. The register schema and the executor are given, as in the v0.4 procedural arm.
- **The search spaces are tiny.** 48 candidates per event kind is why plain enumeration works. A richer domain needs guided search; that is the job a network could earn.
- **The library is not sound outside its family.** It covers 31 to 33 of the 36 true rules. A policy outside it is answered wrongly until a logged decision contradicts every member (155 wrong decisions against 19 for the given family). It detected 1 to 19 such violations per seed and added a skeleton twice.
- **Still a world whose rules can be enumerated.** That has been true of every test in this project.
- Experiment A leaned on the trained status function; C does not. B used the compiled procedures of the v0.4 core so that only the bank differs from the frozen arms.

## What I would do next

1. Take this stack, not the neural one, to a domain I did not write, with the rules hidden from me. Measure audits to competence and silent errors.
2. Find where enumeration stops: grow the procedure language until plain search is too slow, then test whether a small network that proposes candidates buys the speed back while the verifier keeps the guarantees.
3. Extend the route certificate idea to this stack: a promoted program is small enough to verify against invariants (a correction changes only the named slot; an expiry changes only its jurisdiction) for every input, not on samples.
