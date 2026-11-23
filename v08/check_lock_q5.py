"""Compare the files on disk with the Q5 freeze.   python v08/check_lock_q5.py"""
import hashlib, json, os, sys
L = json.load(open("results/v08/LOCK_v08_q5.json")); sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); F = dict(L["files"]); F.update(L.get("public_file") or {})
bad = [f for f, h in F.items() if not os.path.exists(f) or sha(f) != h]; print(f"Q5 freeze of {L['made']} | parent {L['git_parent'][:10]} | {len(F)} files | " + ("ALL MATCH" if not bad else "DIFFER: " + ", ".join(bad))); sys.exit(1 if bad else 0)
