"""M5: a dispatch shift that an operator pauses, corrects and resumes.

    python v02/m5_shift.py runs/v2_iit_s1 [N_SHIFTS=300] [SPLIT=final]

A shift = 8 Dispatch-3 jobs done one after another by one carrier.  Two jobs are priority commitments
with deadlines.  One tick = one step of one job.  At a random tick the operator pauses the shift and
  1. closes a dock (every unfinished job sees it from its next step),
  2. revises one order field of one unfinished job,
  3. in some shifts also asks to change a parcel that was already delivered (this must be declined).
In a quarter of the shifts a gate fault hits a later job after the resume (nobody could predict it).

Systems, on the same shifts
  learned + edit      saved code IDs of the corrected job are rewritten by the frozen slot-write editor;
                      if the editor abstains the correction is sent as a message instead (counted)
  learned + message   the correction is an operator message at the job's next step (ordinary resume)
  learned + restart   every unfinished job is restarted: memory wiped, whole current order re-issued.
                      Modelling assumption: re-briefing a job costs one tick.
  symbolic            exact planner with the orders in a table: incremental (re-plan the corrected job only)
                      and restart (re-plan every unfinished job).  Same actions, different compute.
Sequencing (which job runs when) is the same simple rule for every system: priority jobs first by deadline.
"""
import json, os, sys, time
import numpy as np, torch
from stillway2.editors import SlotWrite
from stillway2.model3 import act_argmax, load3
from stillway2.world3 import DELIVER, EFF_NAMES, FIELD_NAMES, LMAX, NF, ROUTE, WAIT, INIT, World3, ref_valid_routes, ref_dock
from stillway2.edits import EDIT_SPEC

run = sys.argv[1].rstrip("/"); NS = int(sys.argv[2]) if len(sys.argv) > 2 else 300; SPLIT = sys.argv[3] if len(sys.argv) > 3 else "final"
torch.set_num_threads(1); name = os.path.basename(run); model = load3(os.path.join(run, "checkpoint.pt")); S = model.cfg.n_slots
ck = torch.load(os.path.join(run, "editors.pt"), weights_only=True)
sw = SlotWrite.__new__(SlotWrite); sw.table, sw.known, sw.purity = ck["slot_table"], ck["slot_known"], ck["slot_purity"]
J = 8; SPEC = {**EDIT_SPEC, "split": SPLIT, "env": "model"}
ACT = ["L", "R", "D0", "D1", "D2"]


def make_shift(seed):
    gen = torch.Generator().manual_seed(seed); w = World3(J, SPEC, gen); r = np.random.default_rng(seed)
    act = torch.stack([w.active(t) for t in range(w.T)], 1).numpy()                      # (J,T)
    length = act[:, 1:].sum(1)
    prio = np.zeros(J, dtype=bool); prio[r.choice(J, 2, replace=False)] = True
    order = sorted(range(J), key=lambda j: (not prio[j], j))
    start = np.zeros(J, dtype=int); c = 0
    for j in order: start[j] = c; c += length[j]
    deadline = np.where(prio, start + length + 2, 10 ** 6)                              # two ticks of slack
    tau = int(r.integers(2, c - 2))
    # local pause slot of each job: its first step at or after the pause tick (T = job already finished)
    pause = np.full(J, w.T)
    for j in range(J):
        k = 0
        for t in range(1, w.T):
            if act[j, t]:
                if start[j] + k >= tau: pause[j] = t; break
                k += 1
    dock = int(r.integers(0, 3))
    # the correction: an unfinished job and a field that still matters, flipped
    cand = []
    for j in range(J):
        if pause[j] >= w.T: continue
        last_route = 1 + (int(w.L[j]) - 1) * (w.K + 2) + w.K
        if pause[j] <= last_route:
            cand += [(j, g) for g in (0, 1) if int(w.q[j, g]) > 0]
        cand += [(j, 2 + i) for i in range(int(w.L[j])) if bool(w.parcel[j, i]) and pause[j] <= 1 + i * (w.K + 2) + w.K + 1]
    corr = None
    if cand:
        j, f = cand[int(r.integers(0, len(cand)))]
        old = int(w.q[j, f]) if f < 2 else int(w.p[j, f - 2])
        corr = {"job": j, "field": f, "old": old, "value": (3 - old) if f < 2 else int((old + 1 + r.integers(0, 2)) % 3)}
    # a request that must be declined: change a parcel that is already delivered
    late = [(j, 2 + i) for j in range(J) for i in range(int(w.L[j])) if bool(w.parcel[j, i]) and pause[j] > 1 + i * (w.K + 2) + w.K + 1]
    decline = None
    if late and r.random() < 0.5:
        j, f = late[int(r.integers(0, len(late)))]; decline = {"job": j, "field": f, "value": int((int(w.p[j, f - 2]) + 1) % 3)}
    fault = None
    if r.random() < 0.25:
        un = [j for j in range(J) if pause[j] < w.T - 2]
        if un:
            j = un[int(r.integers(0, len(un)))]; later = [t for t in range(pause[j] + 1, w.T) if act[j, t]]
            if later: fault = {"job": j, "slot": int(later[0]), "gate": int(r.integers(0, 2))}
    return {"seed": seed, "order": order, "start": start, "length": length, "prio": prio, "deadline": deadline, "tau": tau, "pause": pause,
            "dock": dock, "corr": corr, "decline": decline, "fault": fault, "act": act}


@torch.no_grad()
def simulate(sh, system, events=True, stop_before=None, state=None):
    """Run the whole shift for one system.  Returns actions, validity, outcomes, and bookkeeping."""
    gen = torch.Generator().manual_seed(sh["seed"]); w = World3(J, SPEC, gen); ar = torch.arange(J)
    ids = torch.full((J, S), -1); pause = torch.tensor(sh["pause"]); corr = sh["corr"] if events else None
    A = np.full((J, w.T), -1); V = np.zeros((J, w.T), dtype=bool); fell_back = False; abstained = False; restarted = np.zeros(J, dtype=bool)
    solver = 0.0
    for t in range(w.T):
        rows_close = (pause == t) if events else torch.zeros(J, dtype=torch.bool)
        if rows_close.any(): w.closed[rows_close] = sh["dock"]
        if events and sh["fault"] and sh["fault"]["slot"] == t:
            j = sh["fault"]["job"]; w.gates[j, sh["fault"]["gate"]] = 1 - w.gates[j, sh["fault"]["gate"]]
        script = None; rows = torch.zeros(J, dtype=torch.bool)
        if corr is not None and int(pause[corr["job"]]) == t:
            rows[corr["job"]] = True; f = torch.full((J,), corr["field"]); v = torch.full((J,), corr["value"])
            show = system in ("learned_message",)
            if system == "learned_edit":
                t0 = time.perf_counter(); new, ab = sw(ids[rows], f[rows], v[rows]); solver += time.perf_counter() - t0
                if bool(ab[0]): abstained = True; fell_back = True; show = True
                else: ids[rows] = new
            script = {"rows": rows, "field": f, "value": v, "show": show}
        if system == "learned_restart" and events:
            rs = pause == t
            if rs.any():
                ids[rs] = -1; restarted |= rs.numpy()
                script = script or {"rows": torch.zeros(J, dtype=torch.bool), "field": torch.zeros(J, dtype=torch.long), "value": torch.zeros(J, dtype=torch.long)}
                script["full_rows"] = rs; script["show"] = False
        obs, act = w.next_obs(script); kind, leg = w.slot(t)
        if system.startswith("symbolic"):
            if kind in (ROUTE, DELIVER):
                vm = w.valid_mask(); a = vm.float().argmax(1)
        else:
            t0 = time.perf_counter(); logits, new_ids = model.infer(ids, obs); solver += time.perf_counter() - t0
            ids = torch.where(act[:, None], new_ids, ids)
            if kind in (ROUTE, DELIVER): vm = w.valid_mask(); a = act_argmax(logits, kind)
        if kind in (ROUTE, DELIVER):
            m = act.numpy(); A[m, t] = a.numpy()[m]; V[m, t] = vm[ar, a].numpy()[m]; w.apply(a, act)
    gate_ok = w.gates_ok().numpy(); par_ok = (w.deliver_ok | ~w.parcel).numpy()
    met = gate_ok.all(1) & par_ok.all(1)
    extra = np.zeros(J, dtype=int)
    if system == "learned_restart" and events:                                         # one tick to re-brief each restarted job
        c = 0
        for j in sh["order"]:
            extra[j] = c
            if restarted[j]: c += 1; extra[j] = c
    finish = sh["start"] + sh["length"] + extra
    return {"A": A, "V": V, "met": met, "gate_ok": gate_ok, "par_ok": par_ok, "finish": finish, "missed_deadline": finish > sh["deadline"],
            "abstained": abstained, "fell_back": fell_back, "solver_seconds": solver, "final_gates": w.gates.numpy().copy(), "delivered": w.delivered.numpy().copy(),
            "restarted": int(restarted.sum())}


def symbolic_times(sh):
    """Compute time of the two symbolic variants: re-plan the corrected job only, or every unfinished job."""
    gen = torch.Generator().manual_seed(sh["seed"]); w = World3(J, SPEC, gen)
    jobs = [(int(w.L[j]), w.eff[j].tolist(), w.tg[j].tolist(), w.gates[j].tolist(), w.q[j].tolist(), w.p[j].tolist(), w.parcel[j].tolist()) for j in range(J)]
    def replan(j):
        L, e, tg, g, q, p, par = jobs[j]; g = list(g)
        for c in range(L):
            r = ref_valid_routes(L, e, tg, g, q, c)[0]; g[tg[c][r]] = ((0, 1), (1, 0), (1, 1), (0, 0))[e[c][r]][g[tg[c][r]]]
            if par[c]: ref_dock(p[c], sh["dock"])
    un = [j for j in range(J) if sh["pause"][j] < 1 + LMAX * 3]
    t0 = time.perf_counter()
    if sh["corr"]: replan(sh["corr"]["job"])
    t_inc = time.perf_counter() - t0
    t0 = time.perf_counter()
    for j in un: replan(j)
    return t_inc, time.perf_counter() - t0


SYSTEMS = ["learned_edit", "learned_message", "learned_restart", "symbolic"]
agg = {s: {"jobs": 0, "jobs_all_commitments_met": 0, "priority_jobs": 0, "priority_deadlines_missed": 0, "unfinished_job_steps": 0,
           "reassigned_steps": 0, "unnecessary_reassignments": 0, "invalid_actions": 0, "editor_abstained": 0, "solver_us": []} for s in SYSTEMS}
agg["symbolic_incremental_us"] = []; agg["symbolic_restart_us"] = []; declines = {"requests": 0, "declined": 0}; pred = {"jobs": 0, "prediction_right": 0, "shifts_with_fault": 0}
example = None
for k in range(NS):
    sh = make_shift(50000 + k)
    if sh["corr"] is None: continue
    base = {s: simulate(sh, s, events=False) for s in ("learned_message", "symbolic")}
    nofault = dict(sh, fault=None)
    for s in SYSTEMS:
        r = simulate(sh, s); orig = base["symbolic" if s == "symbolic" else "learned_message"]; a = agg[s]
        pr_ = simulate(nofault, s)                                                    # the forecast made at the pause: nothing else changes
        un = np.array([[sh["act"][j, t] and t >= sh["pause"][j] and r["A"][j, t] >= 0 for t in range(r["A"].shape[1])] for j in range(J)])
        changed = un & (r["A"] != orig["A"])
        # was the original action still valid in the situation the revised run was actually in?  (re-run with the old action forced is costly;
        # we use the stricter proxy: the step belongs to a job the correction did not touch and whose dock choice was not hit by the closure)
        touched = np.zeros(J, dtype=bool); touched[sh["corr"]["job"]] = True
        if sh["fault"]: touched[sh["fault"]["job"]] = True
        deliver_slot = np.array([[(t - 1) % 3 == 2 for t in range(r["A"].shape[1])] for _ in range(J)])
        closure_hit = deliver_slot & (orig["A"] - 2 == sh["dock"])
        unnecessary = changed & ~touched[:, None] & ~closure_hit
        a["jobs"] += J; a["jobs_all_commitments_met"] += int(r["met"].sum()); a["priority_jobs"] += int(sh["prio"].sum())
        a["priority_deadlines_missed"] += int((r["missed_deadline"] & sh["prio"]).sum()); a["unfinished_job_steps"] += int(un.sum())
        a["reassigned_steps"] += int(changed.sum()); a["unnecessary_reassignments"] += int(unnecessary.sum())
        a["invalid_actions"] += int((un & ~r["V"]).sum()); a["editor_abstained"] += int(r["abstained"]); a["solver_us"].append(r["solver_seconds"] * 1e6)
        if s == "learned_edit":
            pred["jobs"] += J; pred["prediction_right"] += int(((pr_["final_gates"] == r["final_gates"]).all(1) & (pr_["delivered"] == r["delivered"]).all(1)).sum())
            pred["shifts_with_fault"] += int(sh["fault"] is not None)
            if sh["decline"]: declines["requests"] += 1; declines["declined"] += 1        # a delivered parcel: declined by rule, before any editor call
            if example is None and sh["decline"] and sh["fault"] and changed.any():
                example = {"shift": {k_: (v.tolist() if hasattr(v, "tolist") else v) for k_, v in sh.items()}, "runs": {}, "original": orig["A"].tolist()}
        if example is not None and example["shift"]["seed"] == sh["seed"]:
            example["runs"][s] = {k_: (v.tolist() if hasattr(v, "tolist") else v) for k_, v in r.items()}
            example["runs"][s]["predicted_gates"] = pr_["final_gates"].tolist(); example["runs"][s]["predicted_delivered"] = pr_["delivered"].tolist()
    ti, tr = symbolic_times(sh); agg["symbolic_incremental_us"].append(ti * 1e6); agg["symbolic_restart_us"].append(tr * 1e6)

q = lambda x, p: round(float(np.percentile(x, p)), 1)
out = {"run": name, "shifts": NS, "jobs_per_shift": J, "families": SPLIT, "systems": {}, "declined_requests": declines, "forecast_at_pause_vs_realised": pred,
       "assumption": "re-briefing a restarted job costs one tick; sequencing is the same rule for every system"}
for s in SYSTEMS:
    a = agg[s]; out["systems"][s] = {**{k: v for k, v in a.items() if k != "solver_us"}, "revision_compute_median_us": q(a["solver_us"], 50), "revision_compute_p99_us": q(a["solver_us"], 99)}
out["systems"]["symbolic"]["incremental_replan_median_us"] = q(agg["symbolic_incremental_us"], 50); out["systems"]["symbolic"]["incremental_replan_p99_us"] = q(agg["symbolic_incremental_us"], 99)
out["systems"]["symbolic"]["restart_replan_median_us"] = q(agg["symbolic_restart_us"], 50); out["systems"]["symbolic"]["restart_replan_p99_us"] = q(agg["symbolic_restart_us"], 99)
import resource; out["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6)
os.makedirs("results/v02/shift", exist_ok=True); json.dump(out, open(f"results/v02/shift/{name}.json", "w"), indent=1)
if example is not None:
    gen = torch.Generator().manual_seed(example["shift"]["seed"]); w = World3(J, SPEC, gen)
    example["jobs"] = [{"legs": int(w.L[j]), "trips": [[EFF_NAMES[int(w.eff[j, i, r])] + str(int(w.tg[j, i, r])) for r in (0, 1)] for i in range(int(w.L[j]))],
                        "parcel": w.parcel[j].tolist(), "gates_start": w.gates[j].tolist(), "gate_requirements": w.q[j].tolist(), "docks": w.p[j].tolist()} for j in range(J)]
    json.dump(example, open(f"results/v02/shift/{name}_example.json", "w"))
print(json.dumps(out, indent=1))
