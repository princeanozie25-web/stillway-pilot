"""M1: recover the ORIGINAL per-family quotient maps of v0.1 (20 message patterns).

    python v02/m1_recover_maps.py runs/f_iit_s4 I N      # chunk I of N (families split round-robin)
    python v02/m1_recover_maps.py runs/f_iit_s4 merge    # totals + SHA-256 of all maps

v0.1 (tools_certify_quotient.py at commit 6588d9f) built these maps in memory and saved only the counts.
This file repeats that code line for line with the v0.1 extractor (stillway/automaton.py, unchanged) and
saves the maps.  The merge step must reproduce the archived counts in certify_quotient_sealed.json.
"""
import glob, hashlib, json, os, sys, time
import torch
from stillway.automaton import Machine
from stillway.model import load_checkpoint
from stillway.world import ALL_LAYOUTS, family_of

run = sys.argv[1].rstrip("/"); name = os.path.basename(run)
out_dir = f"results/v02/maps20/{name}"; os.makedirs(out_dir, exist_ok=True)
fams = sorted({family_of(e) for e in ALL_LAYOUTS})

if sys.argv[2] == "merge":
    tot = {"plain_checked": 0, "plain_wrong": 0, "quot_checked": 0, "quot_wrong": 0, "quot_wrong_first_choice": 0}
    maps = {}; secs = 0.0
    for p in sorted(glob.glob(f"{out_dir}/chunk_*.json")):
        d = json.load(open(p))
        for f, v in d.items():
            maps[f] = v["maps"]; secs += v["seconds"]
            for k in tot: tot[k] += v[k]
    assert sorted(maps) == fams, "some families are missing"
    blob = json.dumps(maps, sort_keys=True, separators=(",", ":")).encode()
    json.dump(maps, open(f"{out_dir}/maps20.json", "w"), sort_keys=True, separators=(",", ":"))
    arch = json.load(open(f"{run}/certify_quotient_sealed.json"))
    rep = {**tot, "families": len(maps), "maps_sha256": hashlib.sha256(blob).hexdigest(), "cpu_seconds": round(secs, 1),
           "map_entries": sum(len(m) for v in maps.values() for m in v),
           "matches_archived_counts": all(tot[k] == arch[k] for k in ("plain_checked", "plain_wrong", "quot_checked", "quot_wrong"))}
    json.dump(rep, open(f"{out_dir}/recover_report.json", "w"), indent=1); print(json.dumps(rep)); sys.exit(0)

I, N = int(sys.argv[2]), int(sys.argv[3])
torch.set_num_threads(1)
model = load_checkpoint(os.path.join(run, "checkpoint.pt"))
out = {}
for f in fams[I::N]:
    t0 = time.time()
    L = [e for e in ALL_LAYOUTS if family_of(e) == f]
    m = Machine(model, L)
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

    maps = build(); q = Machine(model, L, canon=maps); first_wrong = q.n_bad(); tries = 0
    while q.n_bad() and tries < 12:
        for v in q.violations:
            if v["stage"] > 0: banned[v["stage"] - 1].add(int(q.stage_codes[v["stage"] - 1][v["state"][0]]))
        maps = build(); q = Machine(model, L, canon=maps); tries += 1
    out[f] = {"maps": [{str(k): v for k, v in mp.items()} for mp in maps], "plain_checked": m.checked, "plain_wrong": m.n_bad(),
              "quot_checked": q.checked, "quot_wrong": q.n_bad(), "quot_wrong_first_choice": first_wrong, "tries": tries,
              "raw_states": [len(c) for c in m.stage_codes], "seconds": round(time.time() - t0, 1)}
    json.dump(out, open(f"{out_dir}/chunk_{I}.json", "w"))
