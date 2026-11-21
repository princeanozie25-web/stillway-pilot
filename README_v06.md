# Stillway v0.6: how to run it

Start with `docs/v06_decision_memo.md`, then `results/v06/REPORT_v06.md`. All versions: `FINAL_REPORT.md`.

| Path | What |
|---|---|
| `docs/v06_spec.md` | The frozen test (commit `2b125d1`, before any rule file was fetched). |
| `docs/v06_codex_family_brief.md` | What Codex should author, the file format, how it will be run. |
| `v06/family.py` | The harness: all learners on one family file. |
| `v06/cldr_to_family.py` | Turns Unicode CLDR plural rules into a family file. |
| `v06/report.py` | Tables and the five pass rules. |
| `docs/v06_codex_hidden_memo.md` | Codex's hidden family: verdicts, the post-freeze L4 change, questions for the breakdown. |
| `family_codex.json`, `results/v06/codex_hidden_*` | The hidden family as received, its raw curves, tables, rule outcomes, per-policy detail and lock file. |
| `v06/l4_check.py`, `v06/per_policy.py`, `v06/lock_outputs.py` | Read-only helpers added after the freeze. |
| `data/external/cldr/` | `plurals.json`, `ordinals.json` (97 kB) and the two converted family files. |
| `results/v06/` | Per-shard raw curves, tables, rule outcomes, report. |

Needs Python 3.12 with torch, numpy and scikit-learn. Scripts that read downloaded files run with `python -I`.
