"""Lock the protocol, the student, the adapters, the bank, the code and the data by hash.   python v07/make_lock.py
Writes results/v07/LOCK_v07.json.  Run once, after development and before the final set is opened."""
import glob, hashlib, json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import episode as E
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
def tree(pattern):
    files = sorted(glob.glob(pattern, recursive=True)); h = hashlib.sha256()
    for f in files: h.update(f.encode()); h.update(sha(f).encode())
    return {"files": len(files), "sha256": h.hexdigest()}
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip(); pin = json.load(open("results/v07/MODEL_PIN.json"))
lock = {"locked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "git_head": git("rev-parse", "HEAD"),
        "student": {"repo": pin["repo"], "revision": pin["revision"], "model_sha256": pin["files"]["model.safetensors"]["sha256"], "licence": "Apache-2.0", "precision": "32-bit floats, no quantisation"},
        "adapters": {os.path.basename(f): {"sha256": sha(f), "bytes": os.path.getsize(f), "training": {k: v for k, v in json.load(open(f.replace(".safetensors", ".json"))).items() if k not in ("loss_curve",)}} for f in sorted(glob.glob("artifacts/v07/adapters/*.safetensors"))},
        "bank": {"sha256": sha("artifacts/v07/bank.json"), "bytes": os.path.getsize("artifacts/v07/bank.json")},
        "code": {f: sha(f) for f in sorted(glob.glob("stillway7/*.py") + glob.glob("v07/*.py") + glob.glob("v07/*.sh"))},
        "documents": {f: sha(f) for f in ("docs/v07_protocol.md", "docs/v07_dev_plan.md", "docs/v07_final_set_brief.md") if os.path.exists(f)},
        "data": {"training_sets": {os.path.basename(f): sha(f) for f in sorted(glob.glob("data/v07/training/*.jsonl"))}, "training_repositories": tree("data/v07/train/*.json"), "development_public": tree("data/v07/dev/public/*.json"), "development_hidden": tree("data/v07/dev/hidden/*.json")},
        "episode": {"limits": E.LIMITS, "system_text_sha256": hashlib.sha256(E.SYSTEM.encode()).hexdigest(), "ask_test_sha256": hashlib.sha256(E.ASK_TEST.encode()).hexdigest(), "ask_patch_sha256": hashlib.sha256(E.ASK_PATCH.encode()).hexdigest()},
        "development_records": tree("results/v07/records/dev/*.jsonl"), "note": "locked before any final repository was seen"}
json.dump(lock, open("results/v07/LOCK_v07.json", "w"), indent=1); print("locked", len(lock["adapters"]), "adapters,", len(lock["code"]), "code files; lock sha256", sha("results/v07/LOCK_v07.json"))
