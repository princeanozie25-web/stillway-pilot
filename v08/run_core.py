"""Run a core over a public job file, one job at a time, in the sandbox.   python v08/run_core.py CKPT PUBLIC.jsonl OUT.jsonl [--passes K] [--limit N]

Reads only the public half.  Writes one ungraded record per job; resumes if OUT exists.  CKPT may be the word `teacher`
with --hidden FILE: the careful teacher through the same loop, as a reference for the cost of the procedure itself."""
import argparse, json, os, sys, time
sys.path.insert(0, ".")
import torch
from stillway8 import agent, expert as E

ap = argparse.ArgumentParser(); ap.add_argument("ckpt"); ap.add_argument("public"); ap.add_argument("out"); ap.add_argument("--passes", type=int, default=0); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--hidden", default=""); ap.add_argument("--bank", default=""); ap.add_argument("--predict", action="store_true")
ap.add_argument("--jobs", default="")
a = ap.parse_args(); torch.set_num_threads(1); jobs = [json.loads(l) for l in open(a.public)]; jobs = jobs[:a.limit] if a.limit else jobs
if a.jobs: want = set(json.load(open(a.jobs))); jobs = [j for j in jobs if j["id"] in want]
done = {json.loads(l)["id"] for l in open(a.out)} if os.path.exists(a.out) else set(); os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
if a.ckpt == "teacher":
    from stillway8.runner import Session
    hid = {h["id"]: h for h in map(json.loads, open(a.hidden))}; model = None
    def plan(p):                                               # the teacher's scripts, obtained on a scratch copy, then replayed through the loop
        s = Session(p, fast=True); steps, end = E.teach(s, p, hid[p["id"]]); s.close(); q = [" ; ".join(x["script"]).split() + ["EXEC"] for x in steps] + [[end]]; return lambda toks: q.pop(0)
else:
    from stillway8.model import load
    model = load(a.ckpt, passes=a.passes or None); plan = lambda p: None
proc = lambda p: None
if a.bank:                                                     # a bank snapshot {bank, gate}: its compiled procedure goes first on every job
    from stillway8 import bank as BK
    snap = json.load(open(a.bank)); proc = lambda p: BK.compile(snap["bank"], snap["gate"], p["dom"], p.get("entry"))
t0 = time.time()
with open(a.out, "a") as f:
    for n, p in enumerate(jobs):
        if p["id"] in done: continue
        r = agent.episode(model, p, propose=plan(p), predict=a.predict, procedure=proc(p)); f.write(json.dumps(r, sort_keys=True) + "\n"); f.flush()
        if n % 50 == 0: print(f"{n}/{len(jobs)} {time.time() - t0:.0f} s", flush=True)
print(f"done {len(jobs)} jobs in {time.time() - t0:.1f} s")
