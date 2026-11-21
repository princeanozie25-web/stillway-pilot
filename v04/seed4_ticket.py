"""v0.4 regression ticket: the seed-4 two-field sweep (v0.2 M1), with every failing episode ID kept, on
several numeric runtimes.

    python v04/seed4_ticket.py [runs/f_iit_s4]          # writes results/v04/seed4/
    python v04/seed4_diff.py A.json B.json               # diff two failing-ID files (e.g. this machine and Codex's)

The sweep is the one of v02/m1_counterexample.py: 256 layouts x 2 gate states x 12 orders x 4 stages x
3 field pairs x their values = 393,216 closed-book episodes, each with ONE stage at which two order fields are
revised together.  An episode fails when any proposed action is invalid.

Episode ID (stable across machines):  L<layout index in stillway.world.ALL_LAYOUTS>.g<gate0>.o<dock><gate><bay>.s<stage>.<field><value>.<field><value>

Runtimes (all evaluate the same checkpoint):
  cpu_f32_b1     one (state, observation) pair per forward pass, float32.  This is the v0.2 path.
  cpu_f32_batch  2,048 pairs per forward pass, float32 (other vectorised kernels, other rounding)
  cpu_f64_batch  float64
  mps_f32_batch  Apple GPU, float32 (skipped when not available)
For every runtime the failing IDs are saved.  For every episode whose verdict differs from cpu_f32_b1 the first
divergent step is recorded: observation, saved state, logits, distance to the two nearest codes per slot, action.
"""
import json, os, sys, time
from itertools import product
import torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway.fixtures import SPLIT
from stillway.model import load_checkpoint, stage_argmax
from stillway.scorer import Sim
from stillway.world import ALL_LAYOUTS, ALL_ORDERS, Episode, Order, STAGE_ACTIONS, STAGE_NAMES, N_STAGES, family_of

run = (sys.argv[1] if len(sys.argv) > 1 else "runs/f_iit_s4").rstrip("/"); out = "results/v04/seed4"; os.makedirs(out, exist_ok=True)
DOM = {"dock": (0, 1), "gate": (0, 1), "bay": (0, 1, 2)}; PAIRS = [("dock", "gate"), ("dock", "bay"), ("gate", "bay")]
torch.set_num_threads(1)


def episodes():
    for li, e in enumerate(ALL_LAYOUTS):
        for g0 in (0, 1):
            for (d, q, b) in ALL_ORDERS:
                for st in (1, 2, 3, 4):
                    for f1, f2 in PAIRS:
                        for v1, v2 in product(DOM[f1], DOM[f2]):
                            yield (f"L{li:03d}.g{g0}.o{d}{q}{b}.s{st}.{f1}{v1}.{f2}{v2}",
                                   Episode(e, g0, Order(d, q, b), 0, -1, "closed", {st: [("msg", f1, v1), ("msg", f2, v2)]}))


class Runtime:
    def __init__(self, name, device, dtype, batch):
        self.name, self.device, self.dtype, self.batch = name, device, dtype, batch
        self.m = load_checkpoint(os.path.join(run, "checkpoint.pt")).to(device=device, dtype=dtype).eval(); self.memo = {}

    @torch.no_grad()
    def evaluate(self, keys):
        """keys: list of (state tuple, stage, obs vector tuple) not yet in the memo."""
        for i in range(0, len(keys), self.batch):
            ks = keys[i:i + self.batch]
            ids = torch.tensor([k[0] for k in ks], device=self.device); obs = torch.tensor([k[2] for k in ks], device=self.device, dtype=self.dtype)
            h, logits, z_e = self.m.step(self.m.embed(ids).to(self.dtype), obs)
            d = (z_e.pow(2).sum(-1, keepdim=True) - 2 * torch.einsum("bsd,skd->bsk", z_e, self.m.codebook) + self.m.codebook.pow(2).sum(-1)[None])
            d = d.masked_fill(~self.m.active[None], float("inf")); top = d.topk(2, dim=-1, largest=False)
            new = top.indices[:, :, 0].cpu().tolist(); gap = (top.values[:, :, 1] - top.values[:, :, 0]).cpu().double().tolist(); lg = logits.cpu().double()
            for j, k in enumerate(ks):
                st = k[1]; a = int(stage_argmax(lg[j:j + 1], st)[0]) if st in STAGE_ACTIONS else None
                self.memo[k] = (a, tuple(new[j]), lg[j].tolist(), gap[j])


def sweep(rt, eps):
    t0 = time.time(); sims = [Sim(e) for _, e in eps]; states = [(-1,) * rt.m.cfg.n_slots] * len(eps)
    fail = [None] * len(eps); trace = [[] for _ in eps]
    for s in range(N_STAGES):
        keys = []
        for i, sim in enumerate(sims):
            o = sim.next_obs(); k = (states[i], s, tuple(o.vector())); keys.append(k)
        rt.evaluate(list({k for k in keys if k not in rt.memo}))
        for i, sim in enumerate(sims):
            a, new, _, _ = rt.memo[keys[i]]; trace[i].append(keys[i])
            if a is not None:
                if a not in sim.valid() and fail[i] is None: fail[i] = s
                sim.apply(a)
            states[i] = new
    return fail, trace, time.time() - t0


eps = list(episodes()); print(len(eps), "episodes", flush=True)
RT = [Runtime("cpu_f32_b1", "cpu", torch.float32, 1), Runtime("cpu_f32_batch", "cpu", torch.float32, 2048), Runtime("cpu_f64_batch", "cpu", torch.float64, 2048)]
if torch.backends.mps.is_available(): RT.append(Runtime("mps_f32_batch", "mps", torch.float32, 2048))
res = {}
for rt in RT:
    fail, trace, sec = sweep(rt, eps); res[rt.name] = (fail, trace)
    ids = {eps[i][0]: STAGE_NAMES[f] for i, f in enumerate(fail) if f is not None}
    json.dump({"runtime": rt.name, "checkpoint": run, "torch": torch.__version__, "episodes": len(eps), "failed": len(ids), "failing_ids": ids},
              open(f"{out}/failing_ids_{rt.name}.json", "w"), indent=1)
    print(rt.name, "failed", len(ids), "distinct forward passes", len(rt.memo), f"{sec:.0f}s", flush=True)

ref = RT[0]; rfail, rtrace = res[ref.name]; report = {"reference": ref.name, "runtimes": {}, "reference_failures": []}
for i, f in enumerate(rfail):                                    # how fragile is each reference failure: smallest gaps along its trajectory
    if f is None: continue
    steps = [ref.memo[k] for k in rtrace[i]]
    lg = min(abs(sorted([m[2][a] for a in STAGE_ACTIONS[k[1]]])[-1] - sorted([m[2][a] for a in STAGE_ACTIONS[k[1]]])[-2]) for k, m in zip(rtrace[i], steps) if k[1] in STAGE_ACTIONS)
    report["reference_failures"].append({"id": eps[i][0], "family": family_of(eps[i][1].effects), "split": SPLIT[family_of(eps[i][1].effects)], "first_invalid_stage": STAGE_NAMES[f],
                                         "smallest_code_gap_on_trajectory": min(min(m[3]) for m in steps), "smallest_action_logit_gap_on_trajectory": lg})
report["reference_failures"].sort(key=lambda r: r["smallest_code_gap_on_trajectory"])
for rt in RT[1:]:
    fail, trace = res[rt.name]; diff = []
    for i in range(len(eps)):
        if (fail[i] is None) == (rfail[i] is None): continue
        for s in range(N_STAGES):                                # first step where the two runtimes disagree on the same input
            ka, kb = rtrace[i][s], trace[i][s]
            if ka != kb: break                                   # inputs already differ: the divergence was at s-1 (recorded below)
            ma, mb = ref.memo[ka], rt.memo[kb]
            if ma[0] != mb[0] or ma[1] != mb[1]:
                diff.append({"id": eps[i][0], "fails_on": ref.name if rfail[i] is not None else rt.name, "first_divergent_stage": STAGE_NAMES[s],
                             "saved_state_in": list(ka[0]), "observation_vector": list(ka[2]),
                             ref.name: {"action": ma[0], "state_out": list(ma[1]), "logits": ma[2], "gap_to_second_code_per_slot": ma[3]},
                             rt.name: {"action": mb[0], "state_out": list(mb[1]), "logits": mb[2], "gap_to_second_code_per_slot": mb[3]}})
                break
    same_inputs = [k for k in ref.memo if k in rt.memo]
    report["runtimes"][rt.name] = {"failed": sum(f is not None for f in fail), "episodes_with_a_different_verdict": len(diff), "first_divergences": diff,
                                   "forward_passes_on_identical_inputs": len(same_inputs),
                                   "of_which_different_action": sum(ref.memo[k][0] != rt.memo[k][0] for k in same_inputs),
                                   "of_which_different_code": sum(ref.memo[k][1] != rt.memo[k][1] for k in same_inputs),
                                   "largest_logit_difference": max(max(abs(a - b) for a, b in zip(ref.memo[k][2], rt.memo[k][2])) for k in same_inputs)}
    print(rt.name, {k: v for k, v in report["runtimes"][rt.name].items() if k != "first_divergences"}, flush=True)
# over EVERY forward pass of the reference sweep: the smallest gaps (which inputs could flip on another machine)
allgaps = sorted((min(m[3]), k) for k, m in ref.memo.items())[:10]
report["closest_code_ties_in_the_whole_sweep"] = [{"gap": g, "stage": STAGE_NAMES[k[1]], "saved_state_in": list(k[0]), "observation_vector": list(k[2]),
                                                    "episodes_through_this_step": sum(1 for i in range(len(eps)) if k in rtrace[i]),
                                                    "of_which_fail": sum(1 for i in range(len(eps)) if k in rtrace[i] and rfail[i] is not None)} for g, k in allgaps]
report["reference_failed"] = sum(f is not None for f in rfail)
json.dump(report, open(f"{out}/report.json", "w"), indent=1)
print("reference failed", report["reference_failed"], "| closest ties:", [(round(x["gap"], 7), x["episodes_through_this_step"], x["of_which_fail"]) for x in report["closest_code_ties_in_the_whole_sweep"][:5]])
