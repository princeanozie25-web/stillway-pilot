"""Compare the files on disk with the lock made before Codex's trap set was run.   python v08/check_lock_trap.py"""
import hashlib, json, os, sys
L = json.load(open("results/v08/LOCK_v08_codex_trap.json")); sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
bad = [f for f, h in L["files"].items() if not os.path.exists(f) or sha(f) != h]; print(f"lock of {L['made']} | git {L['git'][:10]} | {len(L['files'])} files | " + ("ALL MATCH" if not bad else "DIFFER: " + ", ".join(bad))); sys.exit(1 if bad else 0)
