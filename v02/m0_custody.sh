#!/bin/bash
# M0: custody check in a clean environment.  Fresh clone of the frozen commit, fresh virtual environment.
#   v02/m0_custody.sh WORKDIR
set -e
W=$1; C=6588d9ff44731c0daf8120d5cc12ba1c2c45282a; OUT=$(pwd)/results/v02/m0
mkdir -p "$W" "$OUT"; cd "$W"
[ -d clone ] || git clone -q https://github.com/princeanozie25-web/stillway-pilot clone
cd clone && git checkout -q $C && git rev-parse HEAD > "$OUT/commit.txt" && git status --porcelain | wc -l > "$OUT/dirty_files.txt"
[ -d ../venv ] || /opt/homebrew/bin/python3.12 -m venv ../venv
../venv/bin/pip install -q --disable-pip-version-check torch==2.14.1 numpy==2.5.4 > "$OUT/pip.log" 2>&1
PY=../venv/bin/python; export PYTHONPATH=.
$PY -m pip freeze > "$OUT/pip_freeze.txt"
{ sysctl -n machdep.cpu.brand_string hw.memsize hw.ncpu; sw_vers -productVersion; $PY -c "import sys,torch,numpy;print(sys.version.split()[0],torch.__version__,numpy.__version__)"; } > "$OUT/hardware.txt"
mkdir -p archived && for s in 1 2 3 4 5; do mkdir -p archived/f_iit_s$s && cp runs/f_iit_s$s/eval_sealed.json runs/f_iit_s$s/replay_rows_sealed.json archived/f_iit_s$s/; done
t0=$(date +%s); $PY tools_check_freeze.py > "$OUT/check_freeze_before.txt" 2>&1 || true; echo "check_freeze $(( $(date +%s) - t0 ))s" > "$OUT/times.txt"
cp fixtures/dev/dev_in.jsonl /tmp/_dev_in.orig; t0=$(date +%s); $PY -m stillway.fixtures make-dev > "$OUT/make_dev.json"; echo "make-dev $(( $(date +%s) - t0 ))s" >> "$OUT/times.txt"
t0=$(date +%s); $PY -m stillway.fixtures make-sealed > "$OUT/make_sealed.json"; echo "make-sealed $(( $(date +%s) - t0 ))s" >> "$OUT/times.txt"
for s in 1 2 3 4 5; do t0=$(date +%s); THREADS=1 $PY -m stillway.evaluate runs/f_iit_s$s --sealed --no-machine > "$OUT/rescore_s$s.log" 2>&1; echo "rescore_s$s $(( $(date +%s) - t0 ))s" >> "$OUT/times.txt"; done
$PY tools_check_freeze.py > "$OUT/check_freeze_after.txt" 2>&1 || true
$PY - "$OUT" <<'PYEOF'
import hashlib, json, sys
out = sys.argv[1]; sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); fz = json.load(open("FREEZE.json")); rep = {"runs": {}}
rep["fixtures_regenerated_match_freeze"] = {f: sha(f) == fz["files_sha256"][f] for f in ("fixtures/dev/dev_in.jsonl", "fixtures/dev/dev_out.jsonl", "fixtures/sealed/sealed.jsonl")}
tot_t = tot_s = ord_ok = ord_n = 0
for s in range(1, 6):
    r = f"f_iit_s{s}"; a = json.load(open(f"archived/{r}/replay_rows_sealed.json")); b = json.load(open(f"runs/{r}/replay_rows_sealed.json"))
    ea = json.load(open(f"archived/{r}/eval_sealed.json")); eb = json.load(open(f"runs/{r}/eval_sealed.json"))
    t = sum(x["targeted"] == y["targeted"] for x, y in zip(a, b)); sh = sum(x["shuffled"] == y["shuffled"] for x, y in zip(a, b)); tot_t += t; tot_s += sh
    rep["runs"][r] = {"checkpoint_sha256": sha(f"runs/{r}/checkpoint.pt"), "checkpoint_matches_freeze": sha(f"runs/{r}/checkpoint.pt") == fz["runs"][r]["checkpoint_sha256"],
                      "targeted_items_identical": f"{t}/{len(a)}", "shuffled_items_identical": f"{sh}/{len(a)}", "all_replay_rows_identical": a == b,
                      "class_rates_identical": ea["classes"] == eb["classes"], "replay_summary_identical": ea["replay"] == eb["replay"],
                      "plain_sealed": eb["classes"]["plain"], "replay_rows_sha256": sha(f"runs/{r}/replay_rows_sealed.json")}
    ord_ok += round(eb["classes"]["plain"] * 500); ord_n += 500
rep["targeted_identical_total"] = tot_t; rep["shuffled_identical_total"] = tot_s; rep["ordinary_accuracy_plain_sealed"] = f"{ord_ok}/{ord_n}"
json.dump(rep, open(out + "/custody_report.json", "w"), indent=1); print(json.dumps({k: v for k, v in rep.items() if k != "runs"}))
PYEOF
