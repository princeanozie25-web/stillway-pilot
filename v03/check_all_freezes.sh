#!/bin/bash
# check_all_freezes.sh : the three freezes (v0.1, v0.2, v0.3) are intact.  Needs only Python.
PY=${PY:-python3}
$PY tools_check_freeze.py | tail -1 || exit 1
$PY - <<'PYEOF' || exit 1
import hashlib, json, sys
fz = json.load(open("results/v02/FREEZE_v02.json")); sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
bad = [f for f, h in fz["files_sha256"].items() if sha(f) != h]
bad += [r for r, v in fz["runs"].items() if sha(f"runs/{r}/checkpoint.pt") != v["checkpoint_sha256"] or sha(f"runs/{r}/editors.pt") != v["editors_sha256"]]
print(f"v0.2 freeze intact: {len(fz['files_sha256'])} files, {len(fz['runs'])} cores with editors" if not bad else f"v0.2 FREEZE CHANGED: {bad}"); sys.exit(1 if bad else 0)
PYEOF
$PY v03/check_freeze.py
