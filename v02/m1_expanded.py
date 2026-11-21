"""M1: the certificate again with all 36 operator-message patterns.

    python v02/m1_expanded.py runs/f_iit_s4 I N          # chunk I of N of the 100 families
    python v02/m1_expanded.py runs/f_iit_s4 merge
    FAMS=KT-KT python v02/m1_expanded.py runs/f_iit_s4 0 1   # profile one family

Per family, with the v0.2 extractor (stillway2/automaton.py):
  raw36         plain memory, 36 patterns
  old_maps36    the ORIGINAL v0.1 quotient maps (results/v02/maps20/RUN/maps20.json), applied unchanged.
                A saved state that is not a key of the map is left as it is (v0.1 behaviour: identity).
  fresh_maps36  maps rebuilt from the 36-pattern machine with the v0.1 procedure.
A wrong decision is attributed to an 'unmapped state' when the state that made it is not one of the map's
representatives, and to a 'mapped representative' otherwise.
"""
import glob, json, os, sys, time, resource
import torch
from stillway2.automaton import MSGS20, MSGS36, Machine, unpack
from stillway.model import load_checkpoint
from stillway.world import ALL_LAYOUTS, ALL_ORDERS, family_of, STAGE_NAMES

run = sys.argv[1].rstrip("/"); name = os.path.basename(run)
out_dir = f"results/v02/expanded/{name}"; os.makedirs(out_dir, exist_ok=True)
fams = sorted({family_of(e) for e in ALL_LAYOUTS})
CAP = int(os.environ.get("CAP", "3000"))

def describe(m, viol):
    hist = m.witness(viol["stage"] - 1, viol["state"]) if viol["stage"] > 0 else []
    return {"history": hist, "failing_obs": m.alpha.describe(viol["stage"], viol["example_obs"]), "order_now": list(ALL_ORDERS[viol["order_now"]]),
            "proposed": viol["proposed"], "n_bad_for_this_state": viol["n_bad"],
            "two_field_messages_in_history": sum(1 for h in hist + [m.alpha.describe(viol["stage"], viol["example_obs"])] if sum(x is not None for x in h["message"]) == 2)}

if sys.argv[2] == "merge":
    keys = ["raw36_checked", "raw36_wrong", "old_checked", "old_wrong", "old_wrong_unmapped_state", "old_wrong_mapped_rep", "old_missing_transitions",
            "old_transitions", "old_missing_codes", "fresh_checked", "fresh_wrong", "fresh_wrong_first_choice", "seconds"]
    tot = {k: 0 for k in keys}; fam_bad = {"raw36": [], "old": [], "fresh": []}; wit = {"raw36": [], "old_unmapped": [], "old_mapped": [], "fresh": []}; exploded = []; n = 0
    states = {"raw36": [0] * 6, "old": [0] * 6, "fresh": [0] * 6}
    for p in sorted(glob.glob(f"{out_dir}/chunk_*.json")):
        for f, v in json.load(open(p)).items():
            n += 1
            for k in keys: tot[k] += v.get(k, 0)
            for a in ("raw36", "old", "fresh"):
                if v.get(a + "_wrong", 0): fam_bad[a].append(f)
                for i, x in enumerate(v.get(a + "_states", [])): states[a][i] += x
            if v.get("exploded"): exploded.append(f)
            for a in wit: wit[a] += [{"family": f, **w} for w in v.get("witness_" + a, [])][:1]
    rep = {**tot, "families": n, "families_wrong": {a: sorted(v) for a, v in fam_bad.items()}, "exploded_families": exploded,
           "mean_states_per_family": {a: [round(x / max(1, n), 1) for x in v] for a, v in states.items()},
           "witnesses": {a: v[:3] for a, v in wit.items()}}
    json.dump(rep, open(f"{out_dir}/report.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "witnesses"})); sys.exit(0)

I, N = int(sys.argv[2]), int(sys.argv[3]); torch.set_num_threads(int(os.environ.get("THREADS", "1")))
model = load_checkpoint(os.path.join(run, "checkpoint.pt")); S = model.cfg.n_slots
old = json.load(open(f"results/v02/maps20/{name}/maps20.json"))
sel = os.environ.get("FAMS"); todo = sel.split(",") if sel else fams[I::N]
path = f"{out_dir}/chunk_{I}.json" if not sel else f"{out_dir}/profile.json"
out = json.load(open(path)) if os.path.exists(path) else {}          # resume: finished families are kept
for f in todo:
    if f in out: continue
    t0 = time.time(); L = [e for e in ALL_LAYOUTS if family_of(e) == f]; row = {}
    m = Machine(model, L, msgs=MSGS36, max_states=CAP)
    row.update(raw36_checked=m.checked, raw36_wrong=m.n_bad(), raw36_states=[len(c) for c in m.stage_codes], exploded=m.exploded,
               witness_raw36=[describe(m, v) for v in sorted(m.violations, key=lambda v: v["stage"])[:2]], raw_seconds=round(time.time() - t0, 1))
    # original maps, unchanged
    om = [{int(k): v for k, v in mp.items()} for mp in old[f]]; reps = [set(mp.values()) for mp in om]; stats = {}
    q = Machine(model, L, canon=om, msgs=MSGS36, max_states=CAP, canon_stats=stats)
    unm = [v for v in q.violations if v["stage"] > 0 and int(q.stage_codes[v["stage"] - 1][v["state"][0]]) not in reps[v["stage"] - 1]]
    mp_ = [v for v in q.violations if v not in unm]
    row.update(old_checked=q.checked, old_wrong=q.n_bad(), old_states=[len(c) for c in q.stage_codes],
               old_wrong_unmapped_state=sum(v["n_bad"] for v in unm), old_wrong_mapped_rep=sum(v["n_bad"] for v in mp_),
               old_transitions=sum(s["transitions"] for s in stats.values()), old_missing_transitions=sum(s["missing_transitions"] for s in stats.values()),
               old_missing_codes=sum(len(s["missing_codes"]) for s in stats.values()),
               witness_old_unmapped=[describe(q, v) for v in sorted(unm, key=lambda v: v["stage"])[:2]],
               witness_old_mapped=[describe(q, v) for v in sorted(mp_, key=lambda v: v["stage"])[:2]])
    # fresh maps from the 36-pattern machine (same procedure as v0.1)
    if not m.exploded:
        bad = [dict() for _ in m.stage_codes]
        for v in m.violations:
            if v["stage"] > 0:
                ci = v["state"][0]; bad[v["stage"] - 1][ci] = bad[v["stage"] - 1].get(ci, 0) + v["n_bad"]
        banned = [set() for _ in m.stage_codes]
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
        maps = build(); q2 = Machine(model, L, canon=maps, msgs=MSGS36, max_states=CAP); first = q2.n_bad(); tries = 0
        while q2.n_bad() and tries < 12:
            for v in q2.violations:
                if v["stage"] > 0: banned[v["stage"] - 1].add(int(q2.stage_codes[v["stage"] - 1][v["state"][0]]))
            maps = build(); q2 = Machine(model, L, canon=maps, msgs=MSGS36, max_states=CAP); tries += 1
        row.update(fresh_checked=q2.checked, fresh_wrong=q2.n_bad(), fresh_wrong_first_choice=first, fresh_states=[len(c) for c in q2.stage_codes],
                   fresh_ambiguous=sum(1 for s in range(len(m.stage_codes)) for v in m.spec_classes(s).values() if v == "AMBIGUOUS"),
                   witness_fresh=[describe(q2, v) for v in sorted(q2.violations, key=lambda v: v["stage"])[:2]],
                   fresh_maps=[{str(k): v for k, v in mp.items()} for mp in maps])
    row["seconds"] = round(time.time() - t0, 1); row["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6)
    out[f] = row; json.dump(out, open(path, "w"))
