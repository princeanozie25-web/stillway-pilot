"""Final seed from the v0.3 freeze commit:  python v03/final_seed.py [COMMIT]"""
import hashlib, subprocess, sys
c = sys.argv[1] if len(sys.argv) > 1 else subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", "results/v03/FREEZE_v03.json"], capture_output=True, text=True).stdout.strip()
assert len(c) == 40, "freeze commit not found"
print(int(hashlib.sha256(("stillway-v0.3-final|" + c).encode()).hexdigest()[:8], 16))
