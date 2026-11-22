"""Exploratory, after development (not in the brief, not an arm of the frozen protocol): the same adapter at reduced strength.
    python v07/x_strength.py TASKS_DIR OUT_DIR ADAPTER SEED STRENGTH ARM [ARM ...]
STRENGTH multiplies the adapter's contribution in every layer (1.0 is the trained adapter, 0 is the unchanged student).
Question: is the loss on lookalikes and absent mechanisms a matter of dose?  Records are written as adapter "<ADAPTER>@<STRENGTH>"."""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import bank as BK, episode as E
from stillway7.student import Student
tasks_dir, out_dir, adapter, seed, strength = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5]); arms = sys.argv[6:]
tasks = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(tasks_dir, "*.json")))]; tasks = [{"id": t["id"], "repo": t["repo"], "code_hash": t["code_hash"]} for t in tasks]
s = Student(); meta = s.load_adapter(f"artifacts/v07/adapters/{adapter}_s{seed}.safetensors")
for l in s.lora.values(): l.scale *= strength
R = BK.Retriever(); os.makedirs(out_dir, exist_ok=True); tag = f"{adapter}@{strength:g}"
for arm in arms:
    out = os.path.join(out_dir, f"{tag}_s{seed}__{arm}.jsonl")
    if os.path.exists(out): print("exists", out); continue
    bank = BK.Bank(); prov = {"plain": BK.provider("none", R), "bank": BK.provider("bank", R, bank)}[arm]
    t0 = time.time(); recs = E.run_episodes(s, tasks, prov, f"{tag}_s{seed}__{arm}", log=lambda m: print(m, round(time.time() - t0), "s", flush=True))
    with open(out + ".tmp", "w") as f:
        for r in recs: r.pop("_patched", None); r["adapter"] = tag; r["seed"] = seed; r["insert_arm"] = arm; r["strength"] = strength; r["adapter_meta"] = {k: meta[k] for k in ("dataset", "updates", "training_tokens")}; f.write(json.dumps(r) + "\n")
    os.rename(out + ".tmp", out); print("wrote", out, round(time.time() - t0), "s", flush=True)
