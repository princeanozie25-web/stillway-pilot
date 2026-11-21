"""Run arms on a folder of repositories.  The student side: it never reads hidden tests or labels.
    python v07/run_arm.py TASKS_DIR OUT_DIR ADAPTER SEED ARM [ARM ...]
ADAPTER: base | patches | experience | experience_x          (base ignores SEED)
ARM:     plain      no insert
         bank       the diagnostic retrieved for this repository (current version), reopened when a test contradicts a prediction
         bank_v1    the same with version 1 of every diagnostic (prior procedure and scope only)
         example    the nearest past training example (ordinary retrieval control)
         wrong      a deliberately wrong diagnostic (the next symptom's)
Writes OUT_DIR/<adapter>_s<seed>__<arm>.jsonl with one ungraded record per repository."""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import bank as BK, episode as E
from stillway7.student import Student
tasks_dir, out_dir, adapter, seed = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]); arms = sys.argv[5:]
tasks = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(tasks_dir, "*.json")))]; tasks = [{"id": t["id"], "repo": t["repo"], "code_hash": t["code_hash"]} for t in tasks]
s = Student(); meta = None
if adapter != "base": meta = s.load_adapter(f"artifacts/v07/adapters/{adapter}_s{seed}.safetensors")
R = BK.Retriever(); os.makedirs(out_dir, exist_ok=True)
for arm in arms:
    out = os.path.join(out_dir, f"{adapter}_s{seed}__{arm}.jsonl")
    if os.path.exists(out): print("exists", out); continue
    bank = BK.Bank(); prov = {"plain": BK.provider("none", R), "bank": BK.provider("bank", R, bank), "bank_v1": BK.provider("bank", R, bank, bank_version=1), "example": BK.provider("example", R), "wrong": BK.provider("bank", R, bank, wrong=True)}[arm]
    t0 = time.time(); recs = E.run_episodes(s, tasks, prov, f"{adapter}_s{seed}__{arm}", log=lambda m: print(m, round(time.time() - t0), "s", flush=True))
    with open(out + ".tmp", "w") as f:
        for r in recs:
            r.pop("_patched", None); r["adapter"] = adapter; r["seed"] = seed; r["insert_arm"] = arm; r["adapter_meta"] = {k: meta[k] for k in ("dataset", "updates", "training_tokens")} if meta else None; f.write(json.dumps(r) + "\n")
    os.rename(out + ".tmp", out); print("wrote", out, round(time.time() - t0), "s", flush=True)
