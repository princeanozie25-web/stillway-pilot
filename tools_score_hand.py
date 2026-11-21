"""Score the reference solution and every impostor on the public dev fixtures."""
import json, sys
from stillway.fixtures import read_jsonl, DEV_IN, DEV_OUT
from stillway.planners import HAND_PLANNERS
from stillway.scorer import score_file, select_slots
items = read_jsonl(DEV_IN) + read_jsonl(DEV_OUT)
swaps = [i for i in items if i['kind'] == 'swap']
out = {}
for name, p in HAND_PLANNERS.items():
    sel = select_slots(p, swaps)
    res = score_file(p, items, sel['slots'])
    out[name] = {"slots": sel['slots'], **{c: round(v['rate'], 4) for c, v in res.items() if c != '_reload_ok'}, "reload_ok": res['_reload_ok']}
    print(f"{name:22s} slots={sel['slots']} " + " ".join(f"{c}={v['rate']:.3f}" for c, v in res.items() if c != '_reload_ok'), "reload", res['_reload_ok'])
json.dump(out, open('results/hand_planners_dev.json', 'w'), indent=1)
