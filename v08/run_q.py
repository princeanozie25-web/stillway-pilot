"""Run the questioning guard, pause on a question, resume on an answer.  Follow-up Q5 (docs/v08_q5_plan.md).

  python v08/run_q.py round1 bankq|searchq PUBLIC.jsonl OUTDIR [--ckpt C --bank SNAPSHOT]     -> OUTDIR/<arm>.r1.jsonl
  python v08/run_q.py questions OUTDIR ROUND                                                  -> OUTDIR/questions_r<ROUND>.jsonl, SEAL_r<ROUND>.json
  python v08/run_q.py resume bankq|searchq PUBLIC.jsonl OUTDIR ROUND ANSWERS.jsonl            -> OUTDIR/<arm>.r<ROUND+1>.jsonl

bankq    the execution-aware core with the bank's guarded procedure made to ask one focused question (stillway8/bank_q.py);
         jobs the bank declines go to the core, as in every bank arm.
searchq  the search script given the same rule; no model, no bank.

A stage file holds one record per job.  A paused job's record carries its whole paused state (`q.pending`): the question,
the surviving changes with the value each gives, the two runner outputs, the workspace hash.  A stage file is the
persisted state: round 1 appends and flushes job by job and can be restarted after a crash; a resume writes its stage to
a temporary file and renames it, and refuses to run twice.  `questions` writes exactly the fields id, round, rows, field,
predictions.  An answer line is {id, round, field, value}; it is used only if it belongs to the pending question and its
value is a legal scalar; several identical lines count once; conflicting, malformed or missing answers end the job with a
bare ASK and an untouched workspace.  The costs of every stage are added up in the record.  Reads only the public half.
The sandbox runs stillway8/opsrt_q.py; no locked file of v0.8 is changed."""
import argparse, datetime, hashlib, json, os, sys, time
sys.path.insert(0, ".")
from stillway8 import runner, opsrt_q, bank_q
runner.OPSRT = os.path.abspath(opsrt_q.__file__); runner.opsrt = opsrt_q
from stillway8 import agent
from stillway8.runner import Session

ARMS = ("bankq", "searchq"); FIVE = ("id", "round", "rows", "field", "predictions")
now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
stamp = lambda s: datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc).timestamp()
H = lambda files: hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:16]
sha = lambda path: hashlib.sha256(open(path, "rb").read()).hexdigest()
ledger = lambda x: [f"{l['op']} {' '.join(l['args'])}".strip() for l in x["ledger"]]


def pend(q, files):
    q = dict(q, workspace_hash=H(files), paused_at=now()); q["digest"] = hashlib.sha256(json.dumps({k: q[k] for k in FIVE}, sort_keys=True).encode()).hexdigest()[:16]; return q


def round1(a):
    jobs = [json.loads(l) for l in open(a.public)]; assert all(p["dom"] == "proj" for p in jobs), "project jobs only"; out = os.path.join(a.outdir, a.arm + ".r1.jsonl"); os.makedirs(a.outdir, exist_ok=True); done = set()
    if os.path.exists(out):                                    # restart after a crash: keep the complete lines, drop a torn one
        good = []
        for l in open(out):
            try: good.append(json.loads(l))
            except ValueError: break
        with open(out + ".tmp", "w") as f: f.writelines(json.dumps(r, sort_keys=True) + "\n" for r in good)
        os.replace(out + ".tmp", out); done = {r["id"] for r in good}
    if a.arm == "bankq":
        import torch
        from stillway8.model import load
        torch.set_num_threads(1); model = load(a.ckpt); snap = json.load(open(a.bank))
    t0 = time.time()
    with open(out, "a") as f:
        for p in jobs:
            if p["id"] in done: continue
            if a.arm == "bankq":
                r = agent.episode(model, p, procedure=bank_q.compile_q(snap["bank"], snap["gate"], p.get("entry"), p["id"])); first = r["steps"][0] if r["steps"] and r["steps"][0].get("bank") else None; lines = first["inner"] if first else []; gen_s = first["s"] if first else 0.0; gen_ops = r["bank_ops"]
            else:
                t = time.time(); s = Session(p); x = s.run(bank_q.search_q(p.get("entry"), p["id"]), mode="py"); final = s.files(); end = x["stdout"].split("END ")[-1].strip() if "END " in x["stdout"] else "BUDGET"; lines = ledger(x)
                if end != "DONE": final = dict(p["files"])    # anything but DONE hands the workspace back as it was found
                r = {"id": p["id"], "dom": p["dom"], "end": end, "why": x["error"], "steps": [{"script": lines, "obs": x["obs"], "s": x["s"], "error": x["error"]}], "changed": {n: v for n, v in final.items() if p["files"].get(n) != v},
                     "diff": s.diff() if end == "DONE" else {}, "calls": 1, "ops": s.ops(), "edit_scripts": 1 if any(l.split()[0] in agent.EDITS for l in lines) else 0, "failed_checks": sum(o.startswith("FAIL") for o in x["obs"]),
                     "bad_ops": sum(o in ("BAD", "ERR") for o in x["obs"]), "tokens_out": 0, "tokens_in": 0, "model_s": 0.0, "exec_s": x["s"], "wall_s": round(time.time() - t, 4), "final_hash": H(final)}
                s.close(); gen_s = x["s"]; gen_ops = r["ops"]
            q, notes, trials = bank_q.parse(lines); tried = sum(l == "REVERT" for l in lines); r["q"] = {"status": "none", "pending": None, "rounds": [], "notes": notes, "probe_executions": trials, "changes_tried": tried, "stages": [{"stage": 1, "ops": gen_ops, "machine_s": gen_s, "probe_executions": trials}], "waiting_s": 0.0}
            if q:
                assert r["end"] == "ASK" and not r["changed"] and r["final_hash"] == H(p["files"]), "a job that asks must leave the workspace as it found it"; r["q"].update(status="paused", pending=pend(q, p["files"]))
            f.write(json.dumps(r, sort_keys=True) + "\n"); f.flush()
    print(f"{a.arm} round 1: {len(jobs)} jobs ({len(jobs) - len(done)} run) in {time.time() - t0:.1f} s")


def questions(a):
    Q = {}; files = {}
    for arm in ARMS:
        path = os.path.join(a.outdir, f"{arm}.r{a.round}.jsonl")
        if not os.path.exists(path): continue
        files[os.path.basename(path)] = sha(path)
        for r in map(json.loads, open(path)):
            st = r["q"]["pending"]
            if r["q"]["status"] == "paused" and st["round"] == a.round:
                q = {k: st[k] for k in FIVE}; assert Q.setdefault(r["id"], q) == q, f"two arms put different questions for {r['id']}"
    out = os.path.join(a.outdir, f"questions_r{a.round}.jsonl"); open(out, "w").writelines(json.dumps(Q[i], sort_keys=True) + "\n" for i in sorted(Q))
    seal = {"made": now(), "round": a.round, "questions": len(Q), "questions_sha256": sha(out), "trace_sha256": files}; json.dump(seal, open(os.path.join(a.outdir, f"SEAL_r{a.round}.json"), "w"), indent=1, sort_keys=True)
    print(f"round {a.round}: {len(Q)} pending questions -> {out}  sha256 {seal['questions_sha256']}")


def resume(a):
    src = os.path.join(a.outdir, f"{a.arm}.r{a.round}.jsonl"); out = os.path.join(a.outdir, f"{a.arm}.r{a.round + 1}.jsonl")
    if os.path.exists(out): print(f"{out} exists: round {a.round} was already resumed; nothing done"); return
    pub = {p["id"]: p for p in map(json.loads, open(a.public))}; given = {}; bad_lines = 0
    for l in open(a.answers):
        if not l.strip(): continue
        try: x = json.loads(l); given.setdefault((x["id"], x["round"]), []).append(x)
        except (ValueError, KeyError, TypeError): bad_lines += 1
    recs = []; count = {"ok": 0, "duplicate": 0, "missing": 0, "invalid": 0}; t0 = time.time()
    for r in map(json.loads, open(src)):
        st = r["q"]["pending"]
        if r["q"]["status"] != "paused" or st["round"] != a.round: recs.append(r); continue
        p = pub[r["id"]]; got = given.get((r["id"], a.round), []); same = all(g == got[0] for g in got)
        status = "missing" if not got else "invalid" if not same or not bank_q.answer_ok(st, got[0]) else "duplicate" if len(got) > 1 else "ok"; count[status] += 1; at = now()
        entry = {"round": a.round, "question": {k: st[k] for k in FIVE}, "digest": st["digest"], "kinds": st["kinds"], "values_on_field": st["values_on_field"], "inputs_tried": st["inputs_tried"], "probe_executions": st["probe_executions"],
                 "paused_at": st["paused_at"], "answered_at": at, "waiting_s": round(stamp(at) - stamp(st["paused_at"]), 3), "answer_status": status, "answer": got[0] if status in ("ok", "duplicate") else None}
        r["q"]["rounds"].append(entry); r["q"]["waiting_s"] = round(r["q"]["waiting_s"] + entry["waiting_s"], 3); r["q"]["pending"] = None
        if status in ("missing", "invalid"): r["q"]["status"] = "clean_ask"; r["q"]["notes"].append({"fallback": f"{status} answer"}); recs.append(r); continue
        t = time.time(); s = Session(p); assert H(s.files()) == st["workspace_hash"], "the workspace is not the one that was paused"
        s.set_procedure(bank_q.resume_q(st, got[0])); x = s.run("USE"); lines = ledger(x)[:-1]; final = s.files(); q, notes, trials = bank_q.parse(lines); ok = x["obs"] == ["PASS"]
        if not ok: final = dict(p["files"])                    # anything but PASS hands the workspace back as it was found
        r["steps"].append({"script": ["USE"], "obs": x["obs"], "s": x["s"], "error": x["error"], "bank": True, "resume": a.round, "inner": lines}); r["changed"] = {n: v for n, v in final.items() if p["files"].get(n) != v}; r["diff"] = s.diff() if ok else {}
        r["final_hash"] = H(final); r["end"] = "DONE" if ok else "ASK"; dt = round(time.time() - t, 4); r["ops"] += s.ops(); r["exec_s"] = round(r["exec_s"] + x["s"], 4); r["wall_s"] = round(r["wall_s"] + dt, 4); r["bad_ops"] += sum(o in ("BAD", "ERR") for o in x["obs"]); s.close()
        r["q"]["notes"] += notes; r["q"]["probe_executions"] += trials; r["q"]["stages"].append({"stage": a.round + 1, "ops": len(x["ledger"]), "machine_s": x["s"], "probe_executions": trials})
        if ok: r["q"]["status"] = "done"
        elif q and x["obs"] == ["ASK"]: r["q"].update(status="paused", pending=pend(q, p["files"]))
        else:
            r["q"]["status"] = "clean_ask"
            if x["obs"] != ["ASK"]: r["q"]["notes"].append({"fallback": "the procedure failed on resuming; workspace discarded", "obs": x["obs"], "error": x["error"]})
        recs.append(r)
    with open(out + ".tmp", "w") as f: f.writelines(json.dumps(r, sort_keys=True) + "\n" for r in recs)
    os.replace(out + ".tmp", out); print(f"{a.arm} resume of round {a.round}: answers ok {count['ok']}, duplicate deliveries {count['duplicate']}, missing {count['missing']}, invalid {count['invalid']}, unreadable lines {bad_lines}; "
                                         f"now paused {sum(r['q']['status'] == 'paused' for r in recs)}, done after a question {sum(r['q']['status'] == 'done' for r in recs)}, bare ASK after a question {sum(r['q']['status'] == 'clean_ask' for r in recs)}; {time.time() - t0:.1f} s")


ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
x = sub.add_parser("round1"); x.add_argument("arm", choices=ARMS); x.add_argument("public"); x.add_argument("outdir"); x.add_argument("--ckpt", default=""); x.add_argument("--bank", default="")
x = sub.add_parser("questions"); x.add_argument("outdir"); x.add_argument("round", type=int)
x = sub.add_parser("resume"); x.add_argument("arm", choices=ARMS); x.add_argument("public"); x.add_argument("outdir"); x.add_argument("round", type=int); x.add_argument("answers")
a = ap.parse_args(); {"round1": round1, "questions": questions, "resume": resume}[a.cmd](a)
