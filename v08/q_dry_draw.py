"""An unselected draw of one-fault project jobs from my own generator, in the format of docs/v08_trap_brief.md.   python v08/q_dry_draw.py SPEC.json N SEED

The draw of v08/trap_dry_draw.py with the seed as an argument, for the dry run of the questioning guard: author-made, exploratory, not the independent test."""
import json, random, sys
sys.path.insert(0, ".")
from stillway8 import world as W
rng = random.Random(int(sys.argv[3])); spec = []; skipped = 0
while len(spec) < int(sys.argv[2]):
    src = W.proj_source(rng); true = src["cfg"]; slot = rng.choice(sorted(true)); wrong = rng.choice([v for v in W.SLOTS[W.SLOT_ROLE[slot]][slot] if v != true[slot]]); cur = dict(true, **{slot: wrong})
    data = [W.rand_rows(rng, true, src["bases"]) for _ in range(2)]; fields = [sorted(rng.sample(W.FIELDS, rng.randint(1, 4)), key=W.FIELDS.index) for _ in range(2)]
    if max(max(r["val"], r["qty"]) for d in data for r in d) > 9 or any(not 3 <= len(d) <= 5 for d in data): continue
    if all(W.stages(cur, d)["report"][f] == W.stages(true, d)["report"][f] for d, fs in zip(data, fields) for f in fs): skipped += 1; continue      # the fault shows in no visible check: there is no job
    hd = [W.rand_rows(rng, true, src["bases"]) for _ in range(8)]; hd = [d for d in hd if 3 <= len(d) <= 5 and max(max(r["val"], r["qty"]) for r in d) <= 9][:4]
    if len(hd) < 3: continue
    r = lambda d: [[x["key"], x["val"], x["qty"]] for x in d]
    spec.append({"id": f"d{len(spec):03d}", "domain": "proj", "group": "draw", "intended": true, "fault": {slot: wrong}, "checks": [{"rows": r(d), "fields": f} for d, f in zip(data, fields)], "hidden_inputs": [r(d) for d in hd]})
json.dump(spec, open(sys.argv[1], "w")); print(len(spec), "drawn;", skipped, "draws skipped because no visible check failed")
