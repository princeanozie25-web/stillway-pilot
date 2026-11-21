"""Re-run the exhaustive check with quotient memory switched on.

    python tools_certify_quotient.py runs/NAME [--sealed]

Per family: extract the machine, pick ONE representative code state per meaning (the member with
the fewest wrong pairs), then extract the machine again with every saved state replaced by its
representative after each step.  The second machine has one state per meaning.  If it has zero
wrong pairs, the planner with quotient memory is correct on every history inside that family.
"""
import json, os, sys, time
import torch
from stillway.automaton import Machine
from stillway.fixtures import families, layouts_of
from stillway.model import load_checkpoint
from stillway.world import ALL_LAYOUTS, family_of

run = sys.argv[1].rstrip("/"); sealed = "--sealed" in sys.argv
torch.set_num_threads(int(os.environ.get("THREADS", "1")))
model = load_checkpoint(os.path.join(run, "checkpoint.pt"))
lay = ALL_LAYOUTS if sealed else layouts_of(families("train") + families("dev"))
fams = sorted({family_of(e) for e in lay}); t0 = time.time()
tot = {"plain_checked": 0, "plain_wrong": 0, "quot_checked": 0, "quot_wrong": 0}; bad_fams = []; states = [0] * 6; sealed_wrong = 0
for f in fams:
    L = [e for e in lay if family_of(e) == f]
    m = Machine(model, L)
    bad = [dict() for _ in m.stage_codes]
    for v in m.violations:
        if v["stage"] > 0:
            ci = v["state"][0]; bad[v["stage"] - 1][ci] = bad[v["stage"] - 1].get(ci, 0) + v["n_bad"]
    banned = [set() for _ in m.stage_codes]          # representatives that turned out wrong in closed loop

    def build():
        maps = []
        for s in range(len(m.stage_codes)):
            sc = m.spec_classes(s); rep = {}; mp = {}
            order = sorted(range(len(m.stage_codes[s])), key=lambda i: (int(m.stage_codes[s][i]) in banned[s], bad[s].get(i, 0)))
            for i in order:
                if sc[i] != "AMBIGUOUS": rep.setdefault(sc[i], int(m.stage_codes[s][i]))
            for i in range(len(m.stage_codes[s])):
                if sc[i] != "AMBIGUOUS": mp[int(m.stage_codes[s][i])] = rep[sc[i]]
            maps.append(mp)
        return maps

    q = Machine(model, L, canon=build()); first_wrong = q.n_bad(); tries = 0
    while q.n_bad() and tries < 12:                  # search: drop a representative that fails, take the next member
        for v in q.violations:
            if v["stage"] > 0: banned[v["stage"] - 1].add(int(q.stage_codes[v["stage"] - 1][v["state"][0]]))
        q = Machine(model, L, canon=build()); tries += 1
    tot["quot_wrong_first_choice"] = tot.get("quot_wrong_first_choice", 0) + first_wrong
    tot["plain_checked"] += m.checked; tot["plain_wrong"] += m.n_bad(); tot["quot_checked"] += q.checked; tot["quot_wrong"] += q.n_bad()
    if q.n_bad(): bad_fams.append(f)
    for s in range(len(q.stage_codes)): states[s] += len(q.stage_codes[s])
out = {**tot, "families": len(fams), "families_wrong_with_quotient": bad_fams,
       "quotient_states_per_family": [round(x / len(fams), 2) for x in states], "seconds": round(time.time() - t0, 1)}
json.dump(out, open(os.path.join(run, "certify_quotient_%s.json" % ("sealed" if sealed else "dev")), "w"), indent=1); print(json.dumps(out))
