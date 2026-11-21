# Stillway v0.2: how to run it and what produced each number

Start with `docs/v02_decision_memo.md` (two pages), then `results/v02/REPORT_v02.md`.

## One command

```bash
./smoke.sh
```

It replays four recorded corrections with the frozen checkpoints and editor and checks each against its recorded outcome: a clean success, a four-leg failure, a cross-gate failure, and an edit that the editor declines on a plain-imitation core.

## Fresh environment

```bash
git clone https://github.com/princeanozie25-web/stillway-pilot && cd stillway-pilot && git checkout v0.2-local   # or copy this folder
python3.12 -m venv venv && venv/bin/pip install torch==2.14.1 numpy==2.5.4
PY=venv/bin/python ./smoke.sh
```

The v0.2 branch and tag are local to this folder until Prince pushes them. Checkpoints, editors and per-item scores are in the folder; nothing is downloaded at run time.

## What is where

| Path | What |
|---|---|
| `docs/v02_decision_memo.md` | The recommendation, two pages. |
| `results/v02/REPORT_v02.md` | Every milestone, every table. |
| `docs/v02_transfer_spec.md` | The scoring contract for the edit experiments (frozen). |
| `docs/v02_certificate_scope.md` | What the certificate covers, in exact words, and three corrections to v0.1. |
| `docs/v02_codex_challenge.md` | Minimal inputs for Codex to rebuild the scorer and replay a correction. |
| `stillway2/` | v0.2 code: `world3.py`, `model3.py`, `train3.py`, `edits.py`, `editors.py`, `dictref.py`, `automaton.py`. |
| `v02/` | One script per experiment. |
| `runs/v2_*` | The seven v0.2 cores, each with `checkpoint.pt`, `editors.pt`, `manifest.json`. |
| `runs/r_iit_s*` | v0.1 seeds retrained from the archived manifests. |
| `results/v02/` | Raw results. `m3/*_final_items.json` are the per-item scores. `MANIFEST_v02.json` has every hash. |
| `fixtures3/` | Representative fixtures with recorded outcomes. |
| `demo/Stillway Shift Replay.html` | The operator page (recorded replay). |

## Commands that were run (all on this machine, CPU)

```bash
# M0
v02/m0_custody.sh <workdir>                                   # fresh clone + fresh environment + rescoring
python -m stillway.train --name r_iit_s1 --iit 1.0 --seed 1   # retrain from the archived manifest (also seeds 4, then 2, 3, 5)
# M1
python tests/test_messages36.py                               # all 36 message patterns as simulator events
v02/par.sh 2 v02/m1_counterexample.py runs/f_iit_s4 && python v02/m1_counterexample.py runs/f_iit_s4 merge
v02/m1_all.sh                                                 # per seed: recover the original maps, then the 36-pattern run
python v02/m1_matched.py runs/f_iit_s4 20000                  # same histories, three memories
python v02/m1_report.py                                       # results/v02/M1_tables.md, archives both map versions
# M2 / M3
python tests/test_world3.py
python -m stillway2.train3 --name v2_iit_s1 --iit 1.0 --seed 1        # seeds 1-5; plain cores: no --iit, seeds 1-2
python v02/m3_eval.py runs/v2_iit_s1 dev                               # fits both editors on training families, scores dev
python v02/m2_freeze.py predictor runs/v2_iit_s1 ... runs/v2_plain_s2  # then: git commit  (the freeze)
python v02/m3_eval.py runs/v2_iit_s1 final $(python v02/final_seed.py) # final strata, seed from the freeze commit
python v02/m3_core_accuracy.py $(python v02/final_seed.py)
python v02/m3_report.py                                                # results/v02/M3_tables.md
# M4
python v02/m4_scaling.py runs/v2_iit_s1
python v02/m4_sampled_vs_exact.py runs/f_iit_s4
python v02/m4_hidden.py runs/f_hiddenx_s1 ; python v02/m4_hidden.py runs/f_hiddenw_s2
# M5
python v02/m5_shift.py runs/v2_iit_s1 300 final && python demo/build_shift.py v2_iit_s1 demo/shift_facts.json
# M6
python v02/make_fixtures.py $(python v02/final_seed.py) ; python v02/export_trace.py runs/v2_iit_s1 $(python v02/final_seed.py) 12
python v02/manifest.py ; ./smoke.sh
```

All with `PYTHONPATH=.` and the interpreter at `~/Developer/voxcpm-venv/bin/python`, except M0, which built its own environment.

## Not done, or incomplete

- Independent replay is Codex's. Nothing in v0.2 has been reproduced by anyone else.
- The Codex challenge set (fixtures I have not seen) does not exist yet; the hook is `v02/run_fixture.py`.
- The scaling sweep ran on one core. Exact enumeration on Dispatch-3 was not attempted.
- The shift page is a recorded replay. The v0.1 replay bench runs a model in the browser; the v0.2 page does not.
- The branch and tag are local. Nothing was pushed or published.
