"""Final data salt from the v0.4 freeze commit:  python v04/final_seed.py [COMMIT]"""
import hashlib, subprocess, sys
c = sys.argv[1] if len(sys.argv) > 1 else subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", "results/v04/FREEZE_v04.json"], capture_output=True, text=True).stdout.strip()
assert len(c) == 40, "freeze commit not found"
print(int(hashlib.sha256(("stillway-v0.4-final|" + c).encode()).hexdigest()[:8], 16))
