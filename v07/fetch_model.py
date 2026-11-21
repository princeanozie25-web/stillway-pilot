"""Fetch the pinned student checkpoint and record its digests.   python v07/fetch_model.py"""
import hashlib, json, os
from huggingface_hub import snapshot_download
REPO = "Qwen/Qwen2.5-Coder-1.5B-Instruct"; REV = "2e1fd397ee46e1388853d2af2c993145b0f1098a"
p = snapshot_download(REPO, revision=REV, allow_patterns=["*.json", "*.txt", "*.safetensors", "LICENSE", "README.md"])
def sha(f):
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
out = {"repo": REPO, "revision": REV, "path": p, "files": {f: {"bytes": os.path.getsize(os.path.join(p, f)), "sha256": sha(os.path.join(p, f))} for f in sorted(os.listdir(p))}}
os.makedirs("results/v07", exist_ok=True); json.dump(out, open("results/v07/MODEL_PIN.json", "w"), indent=1); print(json.dumps(out, indent=1))
