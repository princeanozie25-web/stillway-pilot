# Stillway v0.5: how to run it

Start with `docs/v05_decision_memo.md` (one page), then `results/v05/REPORT_v05.md`. Earlier versions: `FINAL_REPORT.md` (v0.1 to v0.3), `README_v04.md`.

| Path | What |
|---|---|
| `docs/v05_spec.md` | The frozen test: datasets, language, learners, pass rules. Committed before any data was fetched (`3858823`). |
| `v05/blind.py` | All learners on one table: `python -I v05/blind.py monks1 --tests 2` |
| `v05/x_selector.py` | Exploratory follow-up: choose program or network by held-out audits |
| `v05/report.py` | `results/v05/tables.md` and the pass rules |
| `data/external/uci/` | Eight public tables (1.17 MB), from `archive.ics.uci.edu/ml/machine-learning-databases/` |
| `results/v05/*_t2.json`, `*_t3.json` | Per-seed curves for every learner, budget and audit mode |

Needs Python 3.12 with torch, numpy and scikit-learn (1.9.1 here). Scripts that read the downloaded files run with `python -I`.
