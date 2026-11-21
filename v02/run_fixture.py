"""Run ONE Dispatch-3 job, given as JSON, through a frozen v0.2 core, with one correction.

    python v02/run_fixture.py runs/v2_iit_s1 fixture.json        # prints a full step-by-step trace

Fixture format:
  {"legs": 3,
   "trips": [[["K",0],["T",0]], [["O",1],["C",1]], [["T",0],["K",0]]],     per leg: [L trip, R trip], trip = [effect, gate]
   "parcel": [true, false, true], "waits": [true, false, true],
   "gates": [1, 0], "closed": null,
   "order": {"gate0": 2, "gate1": 0, "parcels": [1, 0, 2, 0]},              gate: 0 none, 1 closed, 2 open
   "edit": {"pause_slot": 5, "field": 0, "value": 1, "method": "slot_write"}}   method: predictor | slot_write | message | restart | none
"""
import json, os, sys
import torch
from stillway2.editors import SlotWrite
from stillway2.model3 import act_argmax, load3
from stillway2.world3 import DELIVER, EFF_NAMES, FIELD_NAMES, LMAX, ROUTE, World3

KIND = ["INIT", "WAIT", "ROUTE", "DELIVER"]; ACT = ["L", "R", "D0", "D1", "D2"]


def load(run):
    model = load3(os.path.join(run, "checkpoint.pt")); ck = torch.load(os.path.join(run, "editors.pt"), weights_only=True)
    sw = SlotWrite.__new__(SlotWrite); sw.table, sw.known, sw.purity = ck["slot_table"], ck["slot_known"], ck["slot_purity"]
    from stillway2.editors import Predictor
    pr = Predictor(model); pr.load_state_dict(ck["pred_state"]); pr.tau = ck["pred_tau"]; pr.eval(); sw.predictor = pr
    return model, sw


@torch.no_grad()
def run_fixture(model, sw, fx):
    spec = dict(L=(fx["legs"],), cross=0.0, split=None, K=1, p_wait=1.0, rev=0, gflip=0, decor=0, close=0, msg=0, full=0, reissue=0, env="model")
    w = World3(1, spec, torch.Generator().manual_seed(0)); L = fx["legs"]
    w.L[:] = L; w.eff[:] = 0; w.tg[:] = 0; w.parcel[:] = False; w.wait_on[:] = False
    for i in range(L):
        for r in (0, 1): w.eff[0, i, r] = EFF_NAMES.index(fx["trips"][i][r][0]); w.tg[0, i, r] = fx["trips"][i][r][1]
        w.parcel[0, i] = bool(fx["parcel"][i]); w.wait_on[0, i, 0] = bool(fx["waits"][i])
    w.gates[0] = torch.tensor(fx["gates"]); w.closed[:] = -1 if fx["closed"] is None else fx["closed"]; w.decor[:] = 0
    w.q[0] = torch.tensor([fx["order"]["gate0"], fx["order"]["gate1"]]); w.p[0] = torch.tensor(fx["order"]["parcels"])
    ed = fx.get("edit") or {"method": "none"}; S = model.cfg.n_slots; ids = torch.full((1, S), -1); steps = []; abstained = False
    for t in range(w.T):
        script = None; edit_note = None
        if ed["method"] != "none" and ed["pause_slot"] == t:
            f = torch.tensor([ed["field"]]); v = torch.tensor([ed["value"]]); rows = torch.ones(1, dtype=torch.bool)
            script = {"rows": rows, "field": f, "value": v, "show": ed["method"] == "message"}
            if ed["method"] == "restart": script["full_rows"] = rows; ids[:] = -1
            if ed["method"] in ("slot_write", "predictor"):
                before = ids[0].tolist(); new, ab = (sw if ed["method"] == "slot_write" else sw.predictor)(ids, f, v); abstained = bool(ab[0])
                if not abstained: ids = new
                edit_note = {"ids_before": before, "ids_after": ids[0].tolist(), "abstained": abstained}
        obs, act = w.next_obs(script); kind, leg = w.slot(t)
        if not bool(act[0]): continue
        logits, new_ids = model.infer(ids, obs); row = {"slot": t, "kind": KIND[kind], "leg": leg, "obs": [int(x) for x in obs[0].tolist()], "ids_before": ids[0].tolist()}
        if edit_note: row["edit"] = edit_note
        if kind in (ROUTE, DELIVER):
            a = act_argmax(logits, kind); vm = w.valid_mask()[0]
            row.update(action=ACT[int(a)], valid=[ACT[i] for i in vm.nonzero().flatten().tolist()], action_valid=bool(vm[a]))
            w.apply(a, act)
        ids = new_ids; row["ids_after"] = ids[0].tolist(); row["gates_after"] = w.gates[0].tolist(); steps.append(row)
    return {"steps": steps, "final_gates": w.gates[0].tolist(), "delivered": w.delivered[0, :L].tolist(), "order_at_end": {"gate0": int(w.q[0, 0]), "gate1": int(w.q[0, 1]), "parcels": w.p[0].tolist()},
            "gate_requirements_met": w.gates_ok()[0].tolist(), "parcels_right": (w.deliver_ok | ~w.parcel)[0, :L].tolist(), "abstained": abstained}


if __name__ == "__main__":
    model, sw = load(sys.argv[1].rstrip("/")); print(json.dumps(run_fixture(model, sw, json.load(open(sys.argv[2]))), indent=1))
