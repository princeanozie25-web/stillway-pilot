"""Verify that nothing recorded in FREEZE.json has changed."""
import hashlib, json, os, sys
fz = json.load(open("FREEZE.json")); sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); bad = []
for f, h in fz["files_sha256"].items():
    if sha(f) != h: bad.append(f)
for r, v in fz["runs"].items():
    if sha(os.path.join("runs", r, "checkpoint.pt")) != v["checkpoint_sha256"]: bad.append(r + "/checkpoint.pt")
    if v["slots"] is not None and json.load(open(os.path.join("runs", r, "slots.json")))["slots"] != v["slots"]: bad.append(r + "/slots.json")
print("FREEZE intact" if not bad else "CHANGED SINCE FREEZE: " + ", ".join(bad)); sys.exit(1 if bad else 0)
