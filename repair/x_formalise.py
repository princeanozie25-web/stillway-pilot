"""How well does a model turn the reports into runnable examples?   python repair/x_formalise.py MODEL PUBLIC HIDDEN
Development measure only: it compares the guard's kept examples with the reference (hidden) value of the same call."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repair import agent as A, agent_guard as G
from repair.core import Workspace, base_files, snapshot
from repair.guard import Guard, _canon
model, pub, hid = sys.argv[1:4]; right = wrong = none = 0; tok = 0
for t in map(json.loads, open(pub)):
    f0 = snapshot(t); used = [0]
    def struct(prompt, schema):
        out, k = G.structured(model, prompt, schema, 600); used[0] += k; return out, k
    g = Guard(t, f0, struct, None); g.start(); ref = Workspace(base_files(t["repo"])); vals = g._run(ref, [e["prog"] for e in g.examples]) if g.examples else []; ref.close(); g.close(); tok += used[0]
    good = [e for e, v in zip(g.examples, vals) if _canon(v) == e["expected"]]; bad = [(e["expr"], e["expected"], v) for e, v in zip(g.examples, vals) if _canon(v) != e["expected"]]
    right += bool(good) and not bad; wrong += bool(bad); none += not g.examples
    print(f"{t['id']:<14} stated {sum(l['step'] == 'example' for l in g.log)}, kept {len(g.examples)}, agree with the reference {len(good)}" + (f"   WRONG TARGET {bad}" if bad else "") + ("" if g.examples else f"   dropped: {[(l['expr'][:50], l['before'][:30], l['expected'][:30]) for l in g.log][:2]}"), flush=True)
print(f"tasks with usable examples, all agreeing with the reference: {right}; with a wrong target: {wrong}; with none: {none}; tokens per task {tok / 20:.0f}")
