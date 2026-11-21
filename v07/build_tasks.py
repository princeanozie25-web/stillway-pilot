"""Build and verify every training and development repository.   python v07/build_tasks.py
Writes data/v07/train/*.json (everything), data/v07/dev/public/*.json (what a student may see) and data/v07/dev/hidden/*.json
(hidden tests, group, cause, reference fix).  Development ids are neutral so nothing about a task leaks through its name."""
import json, os, random, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import tasks as TK
t0 = time.time(); tasks = TK.all_tasks(); problems = 0
for d in ("data/v07/train", "data/v07/dev/public", "data/v07/dev/hidden"): shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
dev = [t for t in tasks if t["split"] == "dev"]; random.Random(7).shuffle(dev); names = {t["id"]: "dev_%03d" % i for i, t in enumerate(dev)}; summary = {"train": {}, "dev": {}}
for t in tasks:
    rec, bad = TK.verify(t); t["verified"] = rec
    if bad: problems += 1; print("PROBLEM", t["id"], bad)
    if t["split"] == "train":
        json.dump(t, open(f"data/v07/train/{t['id']}.json", "w"), indent=1); summary["train"][t["template"]] = summary["train"].get(t["template"], 0) + 1
    else:
        n = names[t["id"]]; json.dump({"id": n, "repo": t["repo"], "code_hash": t["code_hash"]}, open(f"data/v07/dev/public/{n}.json", "w"), indent=1)
        json.dump({"id": n, "source": t["id"], "template": t["template"], "skin": t["skin"], "group": t["group"], "symptom": t["symptom"], "cause": t["cause"], "role": t["role"], "hidden": t["hidden"], "fix": t["fix"], "oldfix": t["oldfix"], "verified": rec}, open(f"data/v07/dev/hidden/{n}.json", "w"), indent=1)
        summary["dev"][t["group"]] = summary["dev"].get(t["group"], 0) + 1
summary["problems"] = problems; summary["seconds"] = round(time.time() - t0, 1); summary["tasks"] = len(tasks); json.dump(summary, open("data/v07/BUILD_SUMMARY.json", "w"), indent=1); print(json.dumps(summary, indent=1))
