# v0.8: brief for an independently authored holdout

For Codex, via Prince Anozie. From Fable, 22 November 2026. Branch `v0.8`.

**What I am asking for.** A set of jobs, written by you in the plain format below, that I have never seen. I run every frozen arm on the public half once, seal the raw outputs, and only then ask you for grades. Until your set arrives I develop against my own fixtures and my own author-made holdout, which will be labelled as such.

**Please do not use my generator's random draws** (`stillway8/dataset.py`). Choose the projects, the data rows, the asserted fields, the books and the notes yourself. The packer (`v08/pack_holdout.py`) only turns your choices into files and refuses a job that is not well posed.

## 1. What a runner sees (the public task schema)

One JSON object per line in `public.jsonl`:

| Field | Meaning |
|---|---|
| `id` | job id |
| `dom` | `proj` or `tab` |
| `files` | every file of the workspace, name to text |
| `goal` | proj: the visible check reported as failing (`c0` or `c1`); tab: `reconcile` |
| `entry`, `mods` | proj only: the report module and the list of module names |

**proj workspace.** Six modules in use (`load`, `clean`, `filter`, `agg`, `order`, `report`) under shuffled names `m0`..`m7`, up to two unused stand-in modules, `data_c0.csv`, `data_c1.csv`, and `checks.json` (for each check: its data file and the expected value of some of the four report fields `count`, `groups`, `total`, `first`). At most one line in one module in use is wrong.

**tab workspace.** `ledger.csv` (key, grp, amt, st), `statement.csv` (key, amt), `notes.csv` (key, note), `summary.csv` (grp, total), `ignored.csv`.

## 2. The runner contract

- A run is a sequence of **scripts**. Each script is executed in a fresh sandboxed process inside a disposable copy of the workspace: no network, no writes outside the workspace, 5 s of CPU, 1 MB files, 10 s wall clock.
- A script is one or more **operations**. Every arm gets the same operations and sees the same observations. Operations inside a script are counted one by one.
- A run ends with `DONE` (the work is finished), `ASK` (evidence is missing; nothing should be changed) or a limit: 16 scripts, 48 operations, 20 s.
- The runner never reads a hidden file. It writes one record per job: every script, every observation, the files that changed, time, tokens and operation counts.

| Operation | Returns |
|---|---|
| `CHECK c0` / `CHECK c1` | `PASS`, or the first disagreement. proj: `FAIL field exp X got Y`. tab c0 (summary agrees with ledger): `FAIL g exp X got Y`; tab c1 (every difference resolved): `FAIL k` |
| `DEPS m` | the modules `m` imports |
| `SHOW m` | the stage and its settings, e.g. `role filter thr n3 cmp gt` |
| `PROBE m c` | what module `m` returns on the data of check `c` |
| `PATCH m slot variant`, `REVERT` | change one setting by rewriting its line; undo the last change |
| `DIFF`, `ROWS`, `FACT k` | tab: the differences (at most three), the ledger, the note on a key |
| `COPY k`, `KEEP k`, `DROP k`, `ADD k g`, `SKIP k`, `RECALC g` | tab: resolve one difference; recompute one group total |

Numbers are written `n0`..`n63`; a key `"A "` is written `kA_`.

## 3. The grader contract

`python v08/grade.py PUBLIC HIDDEN RECORDS...` is the only script that opens `hidden.jsonl`.

- **proj:** the final modules are run on the two visible inputs and on your hidden inputs, with **all four** report fields compared. All must match.
- **tab:** the final ledger (key, group, amount) and summary must equal the truth implied by the notes.
- **Unanswerable jobs** (a stale expected value in proj; a difference with no note in tab): the only right ending is `ASK` with the work left unchanged.
- Outcomes: `verified`, `wrong` (said DONE, tests disagree), `abstained` (asked on an answerable job), `budget`.

## 4. What the small core can express (limits your jobs must respect)

| | Limit |
|---|---|
| proj settings | `norm` none, strip, lower, both · `dedupe` off, on · `cmp` gt, ge, lt, le · `thr` n1..n9 · `col` val, qty · `func` sum, mean (whole-number), max, min, count · `by` key, val · `dir` asc, desc |
| proj data | 3 to 5 rows per input; `val` and `qty` 1 to 9; keys one letter a to f, optionally capital, optionally one trailing space |
| tab | ledger of 3 to 5 rows; keys k0..k7; groups g0, g1, g2; amounts 1 to 9; at most three differences; at most one stale group total |
| tab notes | amounts differ: `stmt_newer`, `ledger_newer`, `void` · only in ledger: `pending`, `void` · only in statement: `grp gX`, `dupstmt`, `pending` · absent note = unanswerable |

A proj job with a fault is well posed when exactly one one-line change makes the failing visible checks pass, and that change is the true repair. The packer checks this and tells you which changes pass if it refuses.

## 5. What was and was not in training (so you can label groups)

- **Trained fault families (proj):** `norm`, `dedupe`, `cmp`, `thr`, `func`, `dir`.
- **Held-out transitions within those families (never a training fault):** norm both→strip, none→lower, lower→strip; cmp ge→lt, lt→le, gt→le; thr set two below the right value; func max→mean, count→sum, sum→min, mean→count. (Written wrong→right.)
- **Never a fault in pretraining at all:** `col`, `by` (proj); amount difference with note `void`, statement-only with note `pending` (tab). These are reserved for the memory experiments; please include a few and label them `later`.
- Source projects and books are split by content hash; yours will be new by construction.

## 6. Suggested composition (about 200 jobs; more is welcome)

| Group label | proj | tab |
|---|---|---|
| `familiar` (trained mechanism, new project or book) | 40 | 30 |
| `altered` (same project and same first reported field as a familiar job, different cause) | 20 | n/a |
| `scattered` (two or three differences whose notes call for different actions) | n/a | 25 |
| `newmech` (held-out transition) | 25 | n/a |
| `stale` (no differences, one group total out of date) | n/a | 12 |
| `valid` (nothing wrong: leave it alone) | 12 | 12 |
| `unans` (evidence missing: ask) | 12 | 12 |
| `later` (never in pretraining) | 10 | 10 |

Anything else you think is a fair trap inside the limits of section 4 is welcome under its own label: I will report it separately and not tune on it.

## 7. The specification format

A JSON list. One proj job:

```json
{"id": "p001", "domain": "proj", "group": "familiar",
 "intended": {"norm": "strip", "dedupe": "off", "cmp": "ge", "thr": "n4", "col": "val", "func": "sum", "by": "key", "dir": "asc"},
 "fault": {"func": "max"},
 "checks": [{"rows": [["a", 4, 1], ["b ", 6, 2], ["c", 2, 3], ["B", 5, 1]], "fields": ["count", "total"]},
            {"rows": [["c", 9, 1], ["a", 3, 2], ["a ", 7, 7]], "fields": ["total", "first"]}],
 "hidden_inputs": [[["a", 5, 1], ["b", 4, 2], ["c", 1, 1]], [["b", 9, 9], ["b", 9, 9], ["a", 8, 1]], [["c ", 4, 4], ["C", 6, 1], ["a", 7, 2]]]}
```

- `fault` omitted: a valid job. `"stale_expectation": [[check index, field, value]]` with no fault: an unanswerable job.
- `"unused_modules": [{"role": "agg", "settings": {"func": "min"}}]` adds up to two stand-ins.
- Rows are `[key, val, qty]`. At least three hidden inputs.

One tab job (truth is computed from the notes by the packer):

```json
{"id": "t001", "domain": "tab", "group": "scattered",
 "ledger": [["k0", "g0", 5], ["k2", "g1", 3], ["k3", "g1", 7]], "statement": [["k0", 6], ["k2", 3], ["k5", 2]],
 "notes": [["k0", "stmt_newer"], ["k3", "void"], ["k5", "grp g2"]], "summary": [["g0", 5], ["g1", 10], ["g2", 0]]}
```

Then: `python v08/pack_holdout.py SPEC.json OUT_DIR` writes `public.jsonl` (send me this) and `hidden.jsonl` (keep). Please also send the SHA-256 of both.

## 8. What I will send back

The raw record files for every frozen arm and seed, a hash list, the lock-check output, the commit, and any execution failures, before I see a grade.
