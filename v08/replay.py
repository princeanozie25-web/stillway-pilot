"""Replay one experience.   python v08/replay.py EXPERIENCE.json [--hidden HIDDEN.jsonl]

Re-executes every stored script from the stored initial state in a fresh sandboxed workspace and reports whether the
observations and the final state come out the same.  With --hidden it also grades the replayed final state."""
import json, sys
sys.path.insert(0, ".")
from stillway8 import experience as X

exp = json.load(open(sys.argv[1])); print(f"experience {exp['experience']}  ({exp['source']})\ngoal: {exp['goal']}\ninitial state sha256: {exp['initial']['sha256'][:16]}")
for i, st in enumerate(exp["steps"]):
    print(f"\n  script {i + 1}: " + " ; ".join(st["script"]))
    if st.get("predicted") is not None: print("    predicted: " + " | ".join(st["predicted"]))
    print("    observed:  " + " | ".join(st["obs"]) + (f"     changed: {', '.join(st['changed_files'])}" if st.get("changed_files") else ""))
print(f"\n  ended: {exp['end']}\n  diff: {json.dumps(exp['diff'])}\n  stored verdict: {exp['verdict']['outcome']}\n  cost: {json.dumps(exp['compute'])}\n  memory candidate: {json.dumps(exp['memory_candidate'])}")
same_obs, same_final, final = X.replay(exp); print(f"\nREPLAY: observations {'identical' if same_obs else 'DIFFER'}; final state {'identical' if same_final else 'DIFFERS'}")
if "--hidden" in sys.argv:
    from stillway8.grade import grade
    hid = {h["id"]: h for h in map(json.loads, open(sys.argv[sys.argv.index("--hidden") + 1]))}[exp["job"]]
    pub = {"dom": exp["goal"].split()[0], "files": exp["initial"]["files"], "entry": json.loads(exp["initial"]["files"]["job.json"]).get("entry")}
    print("independent grade of the replayed state:", grade(pub, hid, final, exp["end"])["outcome"])
sys.exit(0 if same_obs and same_final else 1)
