"""Typed patch, quotient memory and membership alarm for one discrete run.

    python tools_extras.py runs/NAME [--sealed]
"""
import json, os, random, sys
import numpy as np, torch
from stillway.extras import CanonicalPlanner, Dictionary
from stillway.fixtures import DEV_IN, DEV_OUT, load_sealed, read_jsonl
from stillway.model import NeuralPlanner, load_checkpoint
from stillway.scorer import run_episode, score_file
from stillway.world import Episode, STAGE_NAMES, family_of

run = sys.argv[1].rstrip("/"); sealed = "--sealed" in sys.argv
torch.set_num_threads(1)
model = load_checkpoint(os.path.join(run, "checkpoint.pt"))
base = NeuralPlanner(model)
dic = Dictionary(os.path.join(run, "dictionary_sealed.json" if sealed else "dictionary_dev.json"), model.cfg.n_slots)
items = load_sealed() if sealed else read_jsonl(DEV_OUT) + read_jsonl(DEV_IN)
slots = json.load(open(os.path.join(run, "slots.json")))["slots"]
out = {}

# 1. typed patch: at the pause, decode the saved state, set gate := donor's obligation, re-encode, resume
swaps = [i for i in items if i["kind"] == "swap"]
ok = undefined = 0
for it in swaps:
    T = Episode.from_json(it["target"]); p = STAGE_NAMES.index(it["pause_after"]); exp = it["expect"]
    fam = family_of(T.effects); flag = {"undef": False}
    def edit(st):
        new = dic.patch(fam, p, st, "gate", exp["gate"])
        if new is None:
            flag["undef"] = True; return st
        return new
    r = run_episode(base, T, p, edit)
    undefined += flag["undef"]
    ok += (r["gate_arrival"] == exp["gate"] and r["dock_done"] == exp["dock"] and r["bay_done"] == exp["bay"])
out["typed_patch"] = {"n": len(swaps), "credit": ok / len(swaps), "patch_undefined": undefined / len(swaps)}

# 2. quotient memory: same fixtures, state canonicalised after every step
nonswap = [i for i in items if i["kind"] != "swap"]
out["classes_base"] = {c: v["rate"] for c, v in score_file(base, nonswap).items() if c != "_reload_ok"}
for kind in ("spec", "behaviour"):
    cp = CanonicalPlanner(base, dic, kind)
    out["classes_quotient_" + kind] = {c: v["rate"] for c, v in score_file(cp, nonswap).items() if c != "_reload_ok"}
    out["quotient_%s_unknown_state_rate" % kind] = cp.unknown / max(1, cp.steps)

# 3. membership alarm: corrupt one slot at the pause with a random code; is the state still in the certified set?
rng = random.Random(0); alarms = harmful = harmful_caught = n = 0
for it in swaps:
    T = Episode.from_json(it["target"]); p = STAGE_NAMES.index(it["pause_after"]); fam = family_of(T.effects)
    box = {}
    def edit(st):
        st = list(st); i = rng.randrange(len(st)); old = st[i]
        while st[i] == old: st[i] = rng.randrange(model.cfg.n_codes)
        box["known"] = dic.known(fam, p, st); box["meaning"] = dic.meaning(fam, p, st)
        return st
    r = run_episode(base, T, p, edit); n += 1
    bad = not (r["gate_ok"] and r["dock_ok"] and r["bay_ok"])
    truth = (T.order.dock, T.order.gate, T.order.bay)
    alarm = (not box["known"]) or box["meaning"] is None or tuple(box["meaning"]) != truth
    alarms += alarm; harmful += bad; harmful_caught += (bad and alarm)
out["corrupt_one_slot"] = {"n": n, "harmful_rate": harmful / n, "alarm_rate": alarms / n,
                           "harmful_caught": harmful_caught / max(1, harmful), "missed_harmful": harmful - harmful_caught}
json.dump(out, open(os.path.join(run, "extras_sealed.json" if sealed else "extras_dev.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
