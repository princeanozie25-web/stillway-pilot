# Stillway v0.3: how to run it and what produced each number

Start with `docs/v03_decision_memo.md` (two pages), then `results/v03/REPORT_v03.md`. v0.1 and v0.2 are untouched: `README.md`, `README_v02.md`.

## One command

```bash
./smoke_v03.sh
```

1. Re-checks the certificate of the repaired core from its integer tables with the standalone checker (plain Python).
2. Replays the four recorded v0.2 fixtures with the v0.3 core and a register write. Two of them were v0.2 failures.
3. Runs one 16-leg job with a correction and compares network, certified tables and exact planner at every leg.

The certificate alone, with no torch:

```bash
python3 stillway3/check_tables.py results/v03/cert/v3r24fix_s1_tables.json all
```

## Fresh environment

```bash
git clone https://github.com/princeanozie25-web/stillway-pilot && cd stillway-pilot && git checkout v0.3-local
python3.12 -m venv venv && venv/bin/pip install torch==2.14.1 numpy==2.5.4
PY=venv/bin/python ./smoke_v03.sh
```

## What is where

| Path | What |
|---|---|
| `docs/v03_decision_memo.md` | The decision, two pages. |
| `results/v03/REPORT_v03.md` | Every result. `results/v03/tables.md` has every table in full. |
| `docs/v03_spec.md` | Architecture, tests and pass rules, frozen before any final job. |
| `docs/v03_certificate_scope.md` | What the any-length certificate covers, in exact words. |
| `docs/v03_codex_challenge.md` | Minimal inputs for an independent check. |
| `stillway3/` | `world.py` (Dispatch-3 for any number of legs), `model.py` (register core), `train.py`, `certify.py`, `check_tables.py` (standalone), `repair.py`, `edits.py`, `editor.py`. |
| `v03/` | One script per experiment. |
| `runs/v3r23_*`, `runs/v3r24_*` | Register cores trained on the v0.2 distribution (T23) and on 2–4 legs with cross-gate legs (T24x). `*fix*`: after certificate-guided repair. |
| `runs/v3c*`, `runs/v3n*` | Ablations: free-vector carry; no value-table aid. |
| `runs/v3m_*` | Arm M: the v0.2 core with the restart-consistency rule. |
| `runs/v3o_*` | Exploratory: trained from logged outcomes only. |
| `results/v03/cert/` | Certificates with witnesses, and the tables each was made on. |
| `demo/Stillway Proof Bench.html` | The interactive page (`demo/build_proof.py` builds it; `node demo/test_proof.js` tests it). |

## Commands that were run (all on this machine, CPU, one thread per job)

```bash
./v03/train_all.sh                      # 18 register cores, about 2 minutes each
./v03/pre_freeze.sh                     # repairs (the T24x seed-3 run and two variants were rerun by hand, see the report)
./v03/cert_all.sh                       # certificates
python v03/freeze.py && git commit      # freeze; then: python v03/final_seed.py  ->  850390379
./v03/final_all.sh 850390379            # F1 (v0.2 final items), F2 (long strata), F3 (certificate against simulator), F4, F5
./v03/extras.sh 850390379               # arm M evaluation, outcome-trained cores, operator shift
python v03/determinism.py               # retrain and re-repair: every weight equal
python v03/report.py                    # results/v03/tables.md
python v03/check_freeze.py              # the freeze is intact
```

Arm M: `v03/train_m.py --name v3m_s1 --seed 1` (about 48 minutes per seed). Outcome-only: `v03/train_outcome.py --name v3o_s1 --seed 1` (about 4 minutes).

## Tests

```bash
PYTHONPATH=. python tests/test_world_n.py                               # any-length world against the frozen world and a plain reference
PYTHONPATH=. python tests/test_regcore.py runs/v3r24fix_s1              # register rule; tables equal the network
PYTHONPATH=. python tests/test_edits_n.py runs/v3r23_s1                 # any-length edit harness equals the frozen v0.2 harness
node demo/test_proof.js                                                 # the page's checker gives the same counts
```
