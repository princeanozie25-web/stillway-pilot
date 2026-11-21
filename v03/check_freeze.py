"""Verify the v0.3 freeze: every frozen file and checkpoint still has its recorded hash.   python v03/check_freeze.py"""
import hashlib, json, sys
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); fz = json.load(open("results/v03/FREEZE_v03.json")); bad = []
bad += [f for f, h in fz["files_sha256"].items() if sha(f) != h]
bad += [r for r, v in fz["runs"].items() if sha(f"runs/{r}/checkpoint.pt") != v["checkpoint_sha256"]]
print("v0.3 FREEZE intact:", len(fz["files_sha256"]), "files,", len(fz["runs"]), "checkpoints" if not bad else ""); 
if bad: print("CHANGED:", bad); sys.exit(1)
