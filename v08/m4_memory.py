"""Milestone 4: what yesterday's experience buys tomorrow.   python v08/m4_memory.py sets | day1 CKPT | night CKPT MODE | report

sets    day 1 and day 2 job files.  Day 1 mixes the later mechanisms (never a fault in pretraining) with ordinary work.
        Day 2 has a retention set (earlier skills), a transfer set (later mechanisms, new projects and books) and
        traps (a later-slot change also satisfies the visible checks, but the real fault is elsewhere).
day1    the frozen core works day 1 with its predictions recorded; the independent verdict is attached; jobs it did
        not verify are then worked by the teacher.  Everything is kept as experiences.
night   from the day-1 experiences only: promote procedures to bank version 1, learn the gate, build the overnight
        corpora (ordinary replay; sleep-inspired: verified dreams, rehearsal, a validation gate with rollback) and
        update the weights at the same number of steps.  Costs are logged.
The day-2 runs use v08/run_core.py with and without --bank; `report` builds the tables."""
import collections, hashlib, json, os, random, subprocess, sys, time
sys.path.insert(0, ".")
from stillway8 import agent, bank as BK, dataset as D, experience as X, expert as E
from stillway8.grade import grade
from stillway8.runner import Session

OUT = os.environ.get("M4_OUT", "results/v08/m4"); PY = sys.executable; os.makedirs(OUT, exist_ok=True)
TOKENS = float(os.environ.get("M4_TOKENS", 3e6)); LR = os.environ.get("M4_LR", "2e-4"); POOL = int(os.environ.get("M4_POOL", 20000)); RATIO = int(os.environ.get("M4_RATIO", 1))     # update budget, learning rate, rehearsal pool, rehearsal records per new record
DAY1 = {"proj": [("later", 60), ("familiar", 40), ("valid", 10), ("unans", 10)], "tab": [("later", 40), ("familiar", 30), ("scattered", 20), ("stale", 8), ("valid", 8), ("unans", 8)]}
DAY2 = {"proj": [("familiar", 40), ("newmech", 20), ("valid", 10), ("unans", 10), ("later", 50), ("trap", 30)], "tab": [("familiar", 30), ("scattered", 20), ("stale", 10), ("valid", 10), ("unans", 10), ("later", 40)]}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); load = lambda p: [json.loads(l) for l in open(p)]
def dump(path, rows): open(path, "w").writelines(json.dumps(x, sort_keys=True) + "\n" for x in rows)
def teacher_record(p, h, noise=0.3, tag=""):
    rec = {"id": p["id"], "dom": p["dom"]}; ops = 0
    for name, z in (("clean", 0.0), ("noisy", noise)):
        s = Session(p, fast=True); steps, end = E.teach(s, p, h, random.Random(f"{D.MASTER}-m4-{p['id']}-{tag}"), z); ops += s.ops(); s.close(); t, k = E.encode(p, steps, end); rec[name] = [" ".join(t), "".join(map(str, k))]
    return rec, ops


def sets():
    info = {}
    for name, split, spec, start in (("day1", "day1", DAY1, 0), ("day2dry", "day2", DAY2, 0), ("day2", "day2", DAY2, 50000)):       # day2dry was used to debug the pipeline with a pilot core; day2 is a fresh draw
        jobs = D.eval_set(split, spec=spec, start=start); split = name; os.makedirs(f"data/v08/{split}", exist_ok=True)
        for p, h in jobs:
            s = Session(p, fast=True); steps, end = E.teach(s, p, h); g = grade(p, h, s.files(), end); s.close(); assert g["outcome"] == "verified", (p["id"], g); h["teacher"] = {"scripts": len(steps) + 1, "ops": sum(len(x["script"]) for x in steps), "end": end}
        dump(f"data/v08/{split}/public.jsonl", [p for p, _ in jobs]); dump(f"data/v08/{split}/hidden.jsonl", [h for _, h in jobs]); c = collections.Counter(f"{p['dom']}/{h['group']}" for p, h in jobs)
        info[split] = {"jobs": len(jobs), "groups": dict(sorted(c.items())), "public_sha256": sha(f"data/v08/{split}/public.jsonl"), "hidden_sha256": sha(f"data/v08/{split}/hidden.jsonl")}; print(split, info[split])
    json.dump(info, open(f"{OUT}/sets.json", "w"), indent=1)


def day1(ckpt):
    from stillway8.model import load as load_model
    import torch; torch.set_num_threads(1); model = load_model(ckpt); pub = load("data/v08/day1/public.jsonl"); hid = {h["id"]: h for h in load("data/v08/day1/hidden.jsonl")}; exps = []; t0 = time.time(); cost = collections.Counter()
    for p in pub:
        r = agent.episode(model, p, predict=True); v = grade(p, hid[p["id"]], agent.final_files(p, r), r["end"]); e = X.build(p, r, v, "core"); e["group"] = hid[p["id"]]["group"]; exps.append(e); cost["core_s"] += r["wall_s"]; cost["core_verified"] += v["outcome"] == "verified"
        if v["outcome"] != "verified":                         # the teacher works the job; its record is a second, verified experience
            h = hid[p["id"]]; s = Session(p, fast=True); steps, end = E.teach(s, p, h); s.close(); q = [" ; ".join(x["script"]).split() + ["EXEC"] for x in steps] + [[end]]; t = time.time()
            r2 = agent.episode(None, p, propose=lambda toks: q.pop(0)); v2 = grade(p, h, agent.final_files(p, r2), r2["end"]); e2 = X.build(p, r2, v2, "teacher-correction"); e2["group"] = h["group"]; exps.append(e2); cost["teacher_s"] += time.time() - t; cost["teacher_jobs"] += 1; cost["teacher_ops"] += r2["ops"]
    dump(f"{OUT}/day1_experiences.jsonl", exps); info = {"checkpoint": ckpt, "checkpoint_sha256": sha(ckpt), "jobs": len(pub), "experiences": len(exps), "wall_seconds": round(time.time() - t0, 1), **{k: round(v, 2) for k, v in cost.items()},
                                                             "experiences_sha256": sha(f"{OUT}/day1_experiences.jsonl")}
    json.dump(info, open(f"{OUT}/day1.json", "w"), indent=1); print(info)


def night(ckpt, mode):
    t_start = time.time(); exps = load(f"{OUT}/day1_experiences.jsonl"); pub = {p["id"]: p for p in load("data/v08/day1/public.jsonl")}; hid = {h["id"]: h for h in load("data/v08/day1/hidden.jsonl")}; cost = {}
    # 1. bank version 1 and the gate, from verified experiences only
    t = time.time(); ver = [e for e in exps if e["verdict"]["outcome"] == "verified"]; bank = BK.promote(ver); core = [e for e in exps if e["source"] == "core" and e["goal"].startswith("proj")]
    c_core = sum(e["compute"]["wall_s"] for e in core) / len(core); o_core = sum(e["compute"]["ops"] for e in core) / len(core); T_OP = 0.002
    snaps = {}
    for name, price in (("v1", 0.0), ("v1_priced", 0.5)):
        gate = BK.learn_gate(bank, ver, lambda pr: c_core + pr * o_core, lambda e, pr: (T_OP + pr) * (2 + 3 * (len(BK.VARIANTS[e["slot"]]) - 1) / 2), price); snaps[name] = {"version": name, "bank": bank, "gate": gate}
        json.dump(snaps[name], open(f"{OUT}/bank_{name}.json", "w"), indent=1, sort_keys=True)
    json.dump({"version": "v0", "bank": {"entries": []}, "gate": {"by_first_observation": {}}}, open(f"{OUT}/bank_v0.json", "w")); cost["bank_and_gate_s"] = round(time.time() - t, 2)
    # 2. the overnight corpora
    train = sorted(pub); t = time.time(); vj = []
    for dom in ("proj", "tab"):                                # fresh later-mechanism jobs from day-1 sources, kept out of the corpus, to validate an update
        srcs = D.sources(dom, "day1"); i = 200000
        while sum(j[0]["dom"] == dom for j in vj) < 30:
            i += 1; j = D.make(dom, "day1", i, "later", srcs)
            if j is not None and j[0]["id"] not in pub: vj.append(j)
    day = [teacher_record(pub[i], hid[i])[0] for i in train]; cost["day_records"] = len(day)
    n_pre = json.load(open("data/v08/MANIFEST.json"))["pretrain"]["jobs_in_file"]; stride = max(1, n_pre // POOL)           # rehearsal: every stride-th pretraining job, so both domains are in it
    rehearsal = [json.loads(l) for i, l in enumerate(open("data/v08/pretrain/records.jsonl")) if i % stride == 0][:POOL]; dreams = []; d_ops = 0
    for dom in ("proj", "tab"):                                # dreams: fresh variations of the later mechanisms on day-1 sources, each verified by execution before it is used
        srcs = D.sources(dom, "day1"); want = 4 * sum(1 for i in train if hid[i]["group"] == "later" and pub[i]["dom"] == dom); i = 100000
        while sum(d["dom"] == dom for d in dreams) < want:
            i += 1; j = D.make(dom, "day1", i, "later", srcs)
            if j is None or j[0]["id"] in pub or any(j[0]["id"] == v[0]["id"] for v in vj): continue
            s = Session(j[0], fast=True); steps, end = E.teach(s, j[0], j[1]); ok = grade(j[0], j[1], s.files(), end)["outcome"] == "verified"; s.close()
            if ok: rec, ops = teacher_record(j[0], j[1]); dreams.append(rec); d_ops += ops
    cost["dreams"] = len(dreams); cost["dream_ops"] = d_ops; cost["corpus_s"] = round(time.time() - t, 2)
    mix = lambda new: new * max(1, round(len(rehearsal) / RATIO / max(1, len(new)))) + rehearsal
    corp = {"naive": day, "replay": mix(day), "sleep": mix(day + dreams)}
    for k, rows in corp.items(): dump(f"{OUT}/corpus_{k}.jsonl", rows)
    dump(f"{OUT}/val_public.jsonl", [j[0] for j in vj]); dump(f"{OUT}/val_hidden.jsonl", [j[1] for j in vj])
    # 3. the updates, same starting checkpoint, same steps
    for k in corp:
        t = time.time(); subprocess.run([PY, "v08/train_core.py", mode, "1", f"{OUT}/core_{k}.safetensors", "--init", ckpt, "--tokens", str(TOKENS), "--lr", LR, "--data", f"{OUT}/corpus_{k}.jsonl"], check=True, stdout=subprocess.DEVNULL); cost[f"train_{k}_s"] = round(time.time() - t, 1)
    # 4. validation of each update on fresh later-mechanism jobs and on the development set (earlier skills); the sleep update is promoted or rolled back on it
    def score(ck, tag):
        res = {}
        for name, pubf, hidf in (("new", f"{OUT}/val_public.jsonl", f"{OUT}/val_hidden.jsonl"), ("old", "data/v08/dev/public.jsonl", "data/v08/dev/hidden.jsonl")):
            o = f"{OUT}/val_{tag}_{name}.jsonl"
            if os.path.exists(o): os.remove(o)
            subprocess.run([PY, "v08/run_core.py", ck, pubf, o], check=True, stdout=subprocess.DEVNULL); subprocess.run([PY, "v08/grade.py", pubf, hidf, o], check=True, stdout=subprocess.DEVNULL)
            g = load(o.replace(".jsonl", ".graded.jsonl")); sel = [x for x in g if x["group"] == "later"] if name == "new" else g; res[name] = round(100 * sum(x["outcome"] == "verified" for x in sel) / max(1, len(sel)), 1); res[name + "_jobs"] = len(sel)
        return res
    from concurrent.futures import ThreadPoolExecutor
    t = time.time(); names = ["frozen"] + list(corp)
    with ThreadPoolExecutor(4) as ex: V = dict(zip(names, ex.map(lambda k: score(ckpt if k == "frozen" else f"{OUT}/core_{k}.safetensors", k), names)))
    cost["validation_s"] = round(time.time() - t, 1); promote = V["sleep"]["old"] >= V["frozen"]["old"] - 2.0 and V["sleep"]["new"] > V["frozen"]["new"]
    info = {"starting_checkpoint": ckpt, "starting_sha256": sha(ckpt), "update_token_budget": TOKENS, "learning_rate": float(LR), "rehearsal_pool": POOL, "rehearsal_records_per_new_record": RATIO, "mode": mode, "bank_entries": len(bank["entries"]), "bank_sha256": {k: sha(f"{OUT}/bank_{k}.json") for k in ("v0", "v1", "v1_priced")},
            "corpus_sha256": {k: sha(f"{OUT}/corpus_{k}.jsonl") for k in corp}, "corpus_records": {k: len(v) for k, v in corp.items()}, "checkpoints_sha256": {k: sha(f"{OUT}/core_{k}.safetensors") for k in corp}, "validation": V,
            "sleep_promoted": bool(promote), "promotion_rule": "earlier skills (the 320 development jobs) no more than 2 points below the frozen core, and later skills (60 fresh jobs from day-1 sources, not in the corpus) above it", "cost": cost, "night_seconds": round(time.time() - t_start, 1)}
    json.dump(info, open(f"{OUT}/night.json", "w"), indent=1); print(json.dumps(info, indent=1)[:2500])


if __name__ == "__main__":
    {"sets": sets, "day1": lambda: day1(sys.argv[2]), "night": lambda: night(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
