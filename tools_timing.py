"""Latency of resume vs restart on the same task, on this machine.

    python tools_timing.py runs/NAME

Task: the planner is paused after PLAN; the operator revises the gate obligation.
  resume  = load the saved state (JSON) + one step that reads the revision and proposes the route
  restart = blank memory + INIT with the full revised order + PLAN + the step that proposes the route
Also: the exact planner, for scale.
"""
import json, os, resource, statistics, sys, time
import torch
from stillway.fixtures import DEV_OUT, read_jsonl
from stillway.model import NeuralPlanner, load_checkpoint, stage_argmax
from stillway.planners import Reference
from stillway.world import Episode, Obs, Sim, LEG1

run = sys.argv[1].rstrip("/")
torch.set_num_threads(1)
model = load_checkpoint(os.path.join(run, "checkpoint.pt"))
items = [i for i in read_jsonl(DEV_OUT) if i["kind"] == "swap"][:300]

def obs_seq(ep):
    sim = Sim(ep); return [sim.next_obs() for _ in range(3)]

def bench(device):
    m = model.to(device)
    sync = (lambda: torch.mps.synchronize()) if device == "mps" else (lambda: None)
    def step(ids, o):
        logits, new = m.infer(torch.tensor([ids], device=device), torch.tensor([o.vector()], device=device))
        return logits, new[0].tolist()
    res = {"resume": [], "restart": [], "one_step": []}
    for rep in range(3):                      # first pass is warm-up
        for it in items:
            ep = Episode.from_json(it["target"]); o0, o1, o2 = obs_seq(ep)
            newq = it["expect"]["gate"]
            _, s0 = step([-1] * m.cfg.n_slots, o0); _, s1 = step(s0, o1)
            blob = json.dumps(s1)
            o2_msg = Obs(LEG1, o2.effects, o2.gate, o2.closed_bay, o2.decor, None, newq, None)
            o0_full = Obs(0, o0.effects, o0.gate, o0.closed_bay, o0.decor, ep.order.dock, newq, ep.order.bay)
            t = time.perf_counter(); st = json.loads(blob); lg, _ = step(st, o2_msg); a = int(stage_argmax(lg, LEG1)[0]); sync()
            t_res = time.perf_counter() - t
            t = time.perf_counter(); _, r0 = step([-1] * m.cfg.n_slots, o0_full); _, r1 = step(r0, o1); lg, _ = step(r1, o2); b = int(stage_argmax(lg, LEG1)[0]); sync()
            t_rst = time.perf_counter() - t
            t = time.perf_counter(); step(s1, o2); sync(); t_one = time.perf_counter() - t
            if rep:
                res["resume"].append(t_res); res["restart"].append(t_rst); res["one_step"].append(t_one)
    q = lambda v, p: sorted(v)[int(p * (len(v) - 1))] * 1e6
    return {k: {"median_us": round(q(v, .5), 1), "p99_us": round(q(v, .99), 1), "n": len(v)} for k, v in res.items()}

out = {"cpu_1_thread": bench("cpu")}
if torch.backends.mps.is_available():
    out["mps"] = bench("mps")
model.to("cpu")
ref = Reference(); ts = []
for rep in range(3):
    for it in items:
        ep = Episode.from_json(it["target"]); o0, o1, o2 = obs_seq(ep)
        t = time.perf_counter(); s = ref.init(o0); s = ref.advance(s, o1); ref.propose(s, o2); ts.append(time.perf_counter() - t)
out["exact_planner_full_restart_us"] = round(statistics.median(ts) * 1e6, 2)
out["planning_steps"] = {"resume": 1, "restart": 3}
out["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 1)
out["parameters"] = model.n_params()
json.dump(out, open(os.path.join(run, "timing.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
