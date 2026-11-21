"""Write complete traces of a few edit attempts for Codex:  python v02/export_trace.py runs/v2_iit_s1 SEED [N=12]"""
import json, os, sys
import numpy as np
sys.path.insert(0, "v02")
from run_fixture import load, run_fixture
EFFN = "KTOC"
run = sys.argv[1].rstrip("/"); seed = int(sys.argv[2]); N = int(sys.argv[3]) if len(sys.argv) > 3 else 12
model, sw = load(run); r = np.random.default_rng(seed); out = []
for k in range(N):
    L = int(r.choice([2, 3, 4])); cross = k % 3 == 2
    trips = []
    for i in range(L):
        g = int(r.integers(0, 2)); trips.append([[EFFN[int(r.integers(0, 4))], g], [EFFN[int(r.integers(0, 4))], (1 - g) if (cross and i == 0) else g]])
    parcel = [bool(r.random() < 0.6) for _ in range(L)]; waits = [bool(r.random() < 0.5) for _ in range(L)]
    order = {"gate0": int(r.integers(0, 3)), "gate1": int(r.integers(0, 3)), "parcels": [int(x) for x in r.integers(0, 3, 4)]}
    live = [f for f in (0, 1) if order["gate%d" % f] > 0] + [2 + i for i in range(L) if parcel[i]]
    if not live: continue
    f = int(r.choice(live)); old = order["gate%d" % f] if f < 2 else order["parcels"][f - 2]; v = (3 - old) if f < 2 else int((old + 1) % 3)
    first_slot = 1 if waits[0] else 2
    fx = {"legs": L, "trips": trips, "parcel": parcel, "waits": waits, "gates": [int(x) for x in r.integers(0, 2, 2)], "closed": None, "order": order,
          "edit": {"pause_slot": first_slot, "field": f, "value": v, "method": "slot_write"}}
    out.append({"fixture": fx, "slot_write": run_fixture(model, sw, fx), "message": run_fixture(model, sw, {**fx, "edit": {**fx["edit"], "method": "message"}}),
                "no_edit": run_fixture(model, sw, {**fx, "edit": {"method": "none"}})})
os.makedirs("results/v02/traces", exist_ok=True); json.dump(out, open(f"results/v02/traces/{os.path.basename(run)}.json", "w"))
print("wrote", len(out), "traces")
