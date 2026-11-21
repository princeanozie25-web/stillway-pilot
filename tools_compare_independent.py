"""Compare this repo's simulator and exact planner with the clean-room copy in independent/.

The clean-room copy was written from docs/evaluator_spec.md alone (see independent/).
"""
import json
from stillway.fixtures import DEV_IN, DEV_OUT, read_jsonl
from stillway.planners import Reference
from stillway.scorer import run_episode
from stillway.world import ACTIONS, Episode, STAGE_NAMES

mine = {}
for it in read_jsonl(DEV_IN) + read_jsonl(DEV_OUT):
    runs = [("episode", it["episode"])] if it["kind"] == "episode" else [("a", it["a"]), ("b", it["b"])] if it["kind"] == "pair" else []
    for tag, ej in runs:
        r = run_episode(Reference(), Episode.from_json(ej), keep_log=True)
        steps = [s for s in r["log"] if s["proposed"]]
        mine[(it["id"], tag)] = {"valid": [s["valid"] for s in steps], "actions": [s["proposed"] for s in steps], "gate_arrival": r["gate_arrival"],
                                 "dock": r["dock_done"], "bay": r["bay_done"], "commit_stage": None if r["commit_stage"] is None else STAGE_NAMES[r["commit_stage"]]}
theirs = {(d["id"], d["run"]): d for d in map(json.loads, open("independent/outcomes.jsonl"))}
keys = ["valid", "actions", "gate_arrival", "dock", "bay", "commit_stage"]
diff = {k: 0 for k in keys}; missing = [k for k in mine if k not in theirs]; first = None
for k, m in mine.items():
    t = theirs.get(k)
    if not t: continue
    for f in keys:
        if m[f] != t[f]:
            diff[f] += 1
            first = first or (k, f, m[f], t[f])
out = {"runs_compared": len(mine) - len(missing), "missing_in_independent": len(missing), "extra_in_independent": len([k for k in theirs if k not in mine]),
       "disagreements": diff, "first_disagreement": first}
json.dump(out, open("results/independent_check.json", "w"), indent=1, default=str); print(json.dumps(out, default=str))
