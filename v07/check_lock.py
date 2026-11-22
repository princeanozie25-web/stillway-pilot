"""Check the files on disk against results/v07/LOCK_v07.json.   python v07/check_lock.py     (exit status 1 if anything differs)"""
import hashlib, json, os, sys
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
if not os.path.exists("results/v07/LOCK_v07.json"): print("no lock file yet"); sys.exit(1)
lock = json.load(open("results/v07/LOCK_v07.json")); bad = []
for f, h in list(lock["code"].items()) + list(lock["documents"].items()):
    if not os.path.exists(f) or sha(f) != h: bad.append(f)
for f, d in lock["adapters"].items():
    p = os.path.join("artifacts/v07/adapters", f)
    if not os.path.exists(p): print("adapter not present (cannot check):", f)
    elif sha(p) != d["sha256"]: bad.append(p)
if sha("artifacts/v07/bank.json") != lock["bank"]["sha256"]: bad.append("artifacts/v07/bank.json")
for f, h in lock["data"]["training_sets"].items():
    if sha(os.path.join("data/v07/training", f)) != h: bad.append(f)
pin = json.load(open("results/v07/MODEL_PIN.json")); m = os.path.join(pin["path"], "model.safetensors")
if os.path.exists(m) and "--model" in sys.argv and sha(m) != lock["student"]["model_sha256"]: bad.append("base model weights")
print("lock of", lock["locked_at"], "| git", lock["git_head"][:10], "|", "ALL MATCH" if not bad else "DIFFERENT: " + ", ".join(bad)); sys.exit(1 if bad else 0)
