"""Final seed from the freeze commit:  python v02/final_seed.py [COMMIT]   (default: the commit that added FREEZE_v02.json)"""
import hashlib, subprocess, sys
c = sys.argv[1] if len(sys.argv) > 1 else subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", "results/v02/FREEZE_v02.json"], capture_output=True, text=True).stdout.strip()
assert len(c) == 40, "freeze commit not found"
print(int(hashlib.sha256(("stillway-v0.2-final|" + c).encode()).hexdigest()[:8], 16))
