"""Verify the v0.4 freeze.   python v04/check_freeze.py"""
import hashlib, json, sys
fz = json.load(open("results/v04/FREEZE_v04.json")); bad = [f for f, h in fz["files_sha256"].items() if hashlib.sha256(open(f, "rb").read()).hexdigest() != h]
print("v0.4 FREEZE intact:", len(fz["files_sha256"]), "files" if not bad else f"CHANGED: {bad}"); sys.exit(1 if bad else 0)
