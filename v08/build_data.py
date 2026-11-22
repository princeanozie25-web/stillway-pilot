"""Build the v0.8 data.   python v08/build_data.py eval | experiences | pretrain N_PROJ N_TAB [WORKERS]

eval      writes data/v08/<split>/public.jsonl and hidden.jsonl for dev, hold and fixture; every job is worked by the
          teacher through the runner and its final state graded (must verify), and the untouched job graded (must not,
          unless leaving it alone is the answer).
pretrain  writes data/v08/pretrain/records.jsonl: for each training job the teacher's careful record and, when the
          teacher slipped (noise 0.3 at each repair decision), a second record with the wrong action, the failed check
          and the recovery; all from actual executions.  The cost of the careful records (clean_*) and the extra cost of
          the slipped ones (slip_*) are logged apart.
Writes data/v08/MANIFEST.json with hashes of generators, splits and outputs."""
import collections, hashlib, json, os, random, sys, time
sys.path.insert(0, ".")
from stillway8 import dataset as D, expert as E
from stillway8.grade import grade
from stillway8.runner import Session

OUT = "data/v08"; NOISE = 0.3
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def manifest(update):
    p = f"{OUT}/MANIFEST.json"; m = json.load(open(p)) if os.path.exists(p) else {}
    m["generators"] = {f: sha(f) for f in ("stillway8/world.py", "stillway8/opsrt.py", "stillway8/dataset.py", "stillway8/expert.py", "v08/build_data.py")}
    m["master_seed"] = D.MASTER; m["splits_percent_of_source_hash"] = D.SPLITS; m["held_out_mechanisms"] = sorted(D.HELD); m["later_slots"] = D.LATER_SLOTS; m["later_tab_rules"] = sorted(map(list, D.LATER_TAB))
    m.update(update); json.dump(m, open(p, "w"), indent=1, sort_keys=True)


def build_eval():
    info = {}
    for split in ("dev", "hold", "fixture"):
        t0 = time.time(); jobs = D.eval_set(split, scale=0.25 if split == "fixture" else 1.0); os.makedirs(f"{OUT}/{split}", exist_ok=True); c = collections.Counter()
        for p, h in jobs:
            s = Session(p, fast=True); steps, end = E.teach(s, p, h); g = grade(p, h, s.files(), end); s.close(); assert g["outcome"] == "verified", (p["id"], g)
            h["teacher"] = {"scripts": len(steps) + 1, "ops": sum(len(x["script"]) for x in steps), "end": end}
            h["untouched_verifies"] = grade(p, h, p["files"], "DONE")["outcome"] == "verified"; c[(p["dom"], h["group"])] += 1
            assert not (h["untouched_verifies"] and p["dom"] == "proj" and h["kind"] == "bug")
        with open(f"{OUT}/{split}/public.jsonl", "w") as f: f.writelines(json.dumps(p, sort_keys=True) + "\n" for p, _ in jobs)
        with open(f"{OUT}/{split}/hidden.jsonl", "w") as f: f.writelines(json.dumps(h, sort_keys=True) + "\n" for _, h in jobs)
        info[split] = {"jobs": len(jobs), "groups": {f"{d}/{g}": n for (d, g), n in sorted(c.items())}, "public_sha256": sha(f"{OUT}/{split}/public.jsonl"), "hidden_sha256": sha(f"{OUT}/{split}/hidden.jsonl"),
                       "source_projects": len(D.sources("proj", split)), "source_books": len(D.sources("tab", split)), "seconds": round(time.time() - t0, 1)}
        print(split, info[split])
    manifest({"eval_sets": info})


def work(arg):
    dom, lo, hi = arg; srcs = D.sources(dom, "train"); out = []; cost = collections.Counter()
    for i in range(lo, hi):
        group = D.train_group(dom, i); j = D.make(dom, "train", i, group, srcs)
        if j is None: cost["skipped"] += 1; continue
        p, h = j; rec = {"i": i, "dom": dom, "group": group, "family": h["family"], "mech": h["mech"]}
        for name, noise in (("noisy", NOISE), ("clean", 0.0)):      # the careful record is the slipped one when the teacher did not slip
            if name == "clean" and not slips: rec["clean"] = rec["noisy"]; rec["noisy"] = None; cost["clean_ops"] += ops; cost["clean_tokens"] += len(toks); cost["clean_s"] += dt; continue
            t = time.time(); s = Session(p, fast=True); steps, end = E.teach(s, p, h, random.Random(f"{D.MASTER}-{dom}-{i}"), noise); toks, kinds = E.encode(p, steps, end); ops = s.ops(); s.close(); slips = sum(not x["ok"] for x in steps); dt = time.time() - t
            if name == "noisy" and slips: cost["slip_extra_s"] += dt; cost["slip_ops"] += ops; cost["slip_tokens"] += len(toks); cost["slip_wrong_scripts"] += slips; cost["slip_records"] += 1
            elif name == "clean": cost["clean_s"] += dt; cost["clean_ops"] += ops; cost["clean_tokens"] += len(toks)
            rec[name] = [" ".join(toks), "".join(map(str, kinds))]
        out.append(json.dumps(rec)); cost["jobs"] += 1
    return out, dict(cost)


def build_pretrain(n_proj, n_tab, workers):
    import multiprocessing as mp
    t0 = time.time(); os.makedirs(f"{OUT}/pretrain", exist_ok=True); chunks = [(d, a, min(a + 1000, n)) for d, n in (("proj", n_proj), ("tab", n_tab)) for a in range(0, n, 1000)]; tot = collections.Counter()
    with mp.Pool(workers) as pool, open(f"{OUT}/pretrain/records.jsonl", "w") as f:
        for out, cost in pool.imap(work, chunks):
            f.writelines(l + "\n" for l in out); tot.update(cost)
    info = {"requested": {"proj": n_proj, "tab": n_tab}, "noise": NOISE, "wall_seconds": round(time.time() - t0, 1), "workers": workers, **{k: (round(v, 1) if isinstance(v, float) else v) for k, v in sorted(tot.items())},
            "records_sha256": sha(f"{OUT}/pretrain/records.jsonl")}
    print(info); manifest({"pretrain": info})


def build_experiences():
    """Full experience records (stillway8/experience.py) for the fixture set: the teacher with slips, through the sandboxed
    loop, graded.  Failures and recoveries are kept.  The small core's own experiences, with its predictions, are written
    by milestone 4 (results/v08/m4/day1_experiences.jsonl)."""
    from stillway8 import agent, experience as X
    pub = [json.loads(l) for l in open(f"{OUT}/fixture/public.jsonl")]; hid = {h["id"]: h for h in map(json.loads, open(f"{OUT}/fixture/hidden.jsonl"))}; os.makedirs(f"{OUT}/experience", exist_ok=True); n = collections.Counter()
    with open(f"{OUT}/experience/teacher_fixture.jsonl", "w") as f:
        for p in pub:
            s = Session(p, fast=True); steps, end = E.teach(s, p, hid[p["id"]], random.Random(f"{D.MASTER}-x-{p['id']}"), 0.5); s.close(); q = [" ; ".join(x["script"]).split() + ["EXEC"] for x in steps] + [[end]]
            r = agent.episode(None, p, propose=lambda toks: q.pop(0)); v = grade(p, hid[p["id"]], agent.final_files(p, r), r["end"]); e = X.build(p, r, v, "teacher with slips"); e["group"] = hid[p["id"]]["group"]
            for st, src in zip(e["steps"], steps): st["slip"] = not src["ok"]
            f.write(json.dumps(e, sort_keys=True) + "\n"); n[v["outcome"]] += 1; n["with_a_failure_and_recovery"] += any(not x["ok"] for x in steps); n["memory_candidates"] += e["memory_candidate"] is not None
    info = {"experiences": len(pub), **n, "sha256": sha(f"{OUT}/experience/teacher_fixture.jsonl")}; print(info); manifest({"experience_dataset": info})


if __name__ == "__main__":
    if sys.argv[1] == "experiences": build_experiences()
    elif sys.argv[1] == "eval": build_eval()
    else: build_pretrain(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 6)
