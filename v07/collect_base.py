"""The unchanged student's own attempts on the training repositories, failures included.   python v07/collect_base.py
Writes results/v07/records/base_on_train.jsonl."""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import episode as E
from stillway7.student import Student
tasks = [json.load(open(f)) for f in sorted(glob.glob("data/v07/train/*.json"))]; full = len(tasks); lim = int(sys.argv[1]) if len(sys.argv) > 1 else full; tasks = tasks[:: max(1, full // lim)][:lim]
s = Student(); t0 = time.time(); recs = E.run_episodes(s, tasks, lambda t, h, k: (None, None), "base", log=lambda m: print(m, round(time.time() - t0), "s", flush=True))
os.makedirs("results/v07/records", exist_ok=True); out = open("results/v07/records/base_on_train.jsonl" if lim == full else "results/v07/records/base_on_train_sample.jsonl", "w"); ok = 0
for r, t in zip(recs, tasks):
    E.grade(r, t["repo"], t["repo"]["tests/test_visible.py"], t["hidden"], t["verified"]["savepoint"]); r["template"] = t["template"]; ok += r["outcome"]["first_patch_correct"]; out.write(json.dumps(r) + "\n")
print("first patch correct", ok, "of", len(tasks), "seconds", round(time.time() - t0))
