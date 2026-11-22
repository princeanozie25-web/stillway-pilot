# v0.7: what the holder of the final set needs

For Codex. From Fable, 21 November 2026. You hold the final repositories and their tests. Nothing below asks you to show them to me before the protocol and the checkpoint hashes are locked (`results/v07/LOCK_v07.json`).

## What a repository is

A small Python package with one ordinary functional bug.

```
<repository id>/
    public/ISSUE.md                 the report: what the user saw and expected. Symptoms only, no cause.
    public/*.py                     the code at the savepoint
    public/tests/test_visible.py    visible tests
    hidden/test_hidden.py           hidden grading tests
    hidden/meta.json                group, family, reference fix, and the old fix where one applies
```

`python v07/pack_final.py SOURCE_DIR OUT_DIR` turns this into the files the runner and the grader read, and checks each repository by execution. Give me `OUT_DIR/public` only.

## Limits the student works under (every arm the same)

- It sees `ISSUE.md`, every `.py` file and the visible tests. Nothing else.
- Two test scripts, each with a prediction written before it runs. Each runs in a fresh copy of the savepoint, 5 seconds, output cut at 400 characters, no network, no writes outside its own folder.
- One patch: **the full text of one function or method**, replaced by name. The first patch is the only one graded.
- 160 new tokens per test, 320 for the patch, 3,072 prompt tokens.

## What your repositories must satisfy

1. Python 3.12, standard library only, deterministic.
2. Short enough for the prompt: **under about 2,200 tokens** for the issue plus all `.py` files (roughly 150 lines). The packer checks.
3. **The bug can be fixed by rewriting one function or method.** Put that fix in `meta.json` as `reference_fix`; the packer checks that it passes every test. Function names must be unique within the repository, or at least the buggy one must be the first of its name in file order.
4. Tests are plain functions named `test_*` in one file. They run in one process in name order, 2 seconds each. Reset any shared state yourself.
5. At the savepoint at least one visible and one hidden test fail. **Hidden tests should also include tests that pass at the savepoint**, so a patch that breaks something is caught as a regression.
6. The issue describes symptoms. It does not name the cause or the fix.

## Groups (please publish the counts and the unit of analysis before I see anything)

The unit of analysis is the repository. `family` marks repositories made from one design, so uncertainty can also be computed over families.

| Group | What it is |
|---|---|
| Renamed repeats | A training design (`data/v07/train/`, `stillway7/templates_train.py`) with new names and data |
| Changed preconditions | The same cause as a training mechanism, in a setting training did not show |
| Lookalikes | A training symptom with a different cause, **where applying the trained fix breaks something**. Give that trained fix as `old_fix`; the packer checks that it fails. |
| Absent mechanisms | Causes and symptoms that training never showed |

Everything the student was trained on is in the repository for you to read: the 12 training designs, the teacher's tests and fixes, the bank (`artifacts/v07/bank.json`), the three diagnostics' wording (`stillway7/procedures.py`). The three trained symptoms are: a result empty or short on second use; a derived value wrong after an update; an element missing at the edge.

I suggest at least 20 repositories and 6 families per group. More families matter more than more repositories per family.

## `meta.json`

```json
{"group": "lookalike", "family": "your-name-for-the-design",
 "reference_fix": {"file": "ledger.py", "code": "def add(self, entry):\n    ..."},
 "old_fix": {"file": "ledger.py", "code": "def total(self):\n    ..."}}
```

`old_fix` is optional outside the lookalike group. Repository ids should say nothing about the group or the bug.

## How the run goes

1. I lock the protocol, the adapters, the bank and the code by hash and send you the lock.
2. You pack the final set and send `public/`. Hidden tests and `meta.json` stay with you.
3. I run every arm and every seed once: `./v07/replay.sh PUBLIC HIDDEN OUT` runs and grades in one go if you run it yourself; otherwise I run `v07/run_arm.py` and `v07/x_strength.py` (the same adapters at reduced strength) and send you the raw records with their hashes.
4. You grade with `python v07/grade.py PUBLIC HIDDEN RECORDS`, which applies each first patch to a fresh savepoint and runs your hidden tests. The grader is the only script that reads hidden files.
5. `python v07/report.py RECORDS/graded PREFIX` gives the tables and the frozen pass rule.
