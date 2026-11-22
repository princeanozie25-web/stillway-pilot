"""The v0.8 demo: give the small core a goal, see the script it proposes and the effect it predicts, execute it, and
look at what entered memory.

    python v08/demo.py --smoke                      two sessions end to end, no questions asked (about 10 s)
    python v08/demo.py                              choose a job from the fixture set and step through it
    python v08/demo.py --workspace DIR              your own job: a folder holding the public files of a job
    python v08/demo.py --new proj|tab [--seed N]    a job nobody has seen, drawn from the generator
Options: --ckpt FILE (default artifacts/v08/demo_core.safetensors), --memory DIR (default demo/v08/memory), --yes.

Session 1 works a job and writes the experience and any memory entry.  Session 2 takes the same project with one
precondition altered (the fault moved to another line): the bank offers yesterday's procedure first, execution shows it
no longer applies, the workspace is put back, and the core works the job itself.  Everything runs in the sandbox."""
import argparse, json, os, sys
sys.path.insert(0, ".")
from stillway8 import agent, bank as BK, dataset as D, experience as X, expert as E, world as W
from stillway8.model import decode, load
from stillway8.runner import Session

ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--workspace", default=""); ap.add_argument("--new", default=""); ap.add_argument("--seed", type=int, default=7); ap.add_argument("--yes", action="store_true")
ap.add_argument("--ckpt", default="artifacts/v08/demo_core.safetensors"); ap.add_argument("--memory", default="demo/v08/memory"); a = ap.parse_args(); auto = a.yes or a.smoke
os.makedirs(a.memory, exist_ok=True); EXP = f"{a.memory}/experiences.jsonl"; BANK = f"{a.memory}/bank.json"
if a.smoke:
    for f in (EXP, BANK):
        if os.path.exists(f): os.remove(f)
import torch; torch.set_num_threads(1); model = load(a.ckpt); say = print


def memory():
    exps = [json.loads(l) for l in open(EXP)] if os.path.exists(EXP) else []; bank = BK.promote(exps, min_support=1)
    gate = BK.learn_gate(bank, [e for e in exps if e["verdict"]["outcome"] == "verified"], lambda p: 1.0, lambda e, p: 0.01); return exps, {"bank": bank, "gate": gate}


def work(public, hidden=None, title=""):
    exps, snap = memory(); proc = BK.compile(snap["bank"], snap["gate"], public["dom"], public.get("entry")) if snap["bank"]["entries"] else None
    say(f"\n{'=' * 78}\n{title}\nGOAL   {' '.join(E.header(public)[1:])}\nSTATE  {len(public['files'])} files: {' '.join(sorted(public['files']))}\nMEMORY {len(snap['bank']['entries'])} entries in the bank")
    sess = Session(public); toks = E.header(public); steps = []; end = "BUDGET"
    try:
        if proc:
            sess.set_procedure(proc); r = sess.run("USE"); inner = [f"{l['op']} {' '.join(l['args'])}".strip() for l in r["ledger"][:-1]]
            say(f"\n  the bank's procedure goes first ({len(inner)} operations): " + " ; ".join(inner[:14]) + (" ..." if len(inner) > 14 else "")); say(f"    result: {r['obs'][0]}" + ("" if r["obs"] == ["PASS"] else "   (nothing was changed; the core takes over)"))
            steps.append({"script": ["USE"], "obs": r["obs"], "s": r["s"], "error": r["error"], "bank": True, "inner": inner})
            if r["obs"] == ["PASS"]: end = "DONE"
        while end != "DONE" and len(steps) < 16:
            toks.append("ACT"); act = [E.VOCAB[i] for i in decode(model, E.ids(toks), agent.STOP, 40)]
            if act[-1] in ("DONE", "ASK") and len(act) == 1: end = act[0]; break
            if act[-1] != "EXEC": say("  (the core produced a malformed script; stopping)"); break
            lines = [l.strip() for l in " ".join(act[:-1]).split(";") if l.strip()]; pred = " ".join(E.VOCAB[i] for i in decode(model, E.ids(toks + act + ["OBS"]), {E.TOK["END"]}, 64)[:-1]).split(" | ")
            say(f"\n  proposed script {len(steps) + 1}: " + " ; ".join(lines)); say("    predicted effect: " + " | ".join(pred))
            if not auto and input("    run it? [Enter = yes, n = stop] ").strip().lower().startswith("n"): break
            before = sess.files(); r = sess.run("\n".join(lines)); now = sess.files(); ch = sorted(n for n in now if now[n] != before.get(n))
            say("    observed effect:  " + " | ".join(r["obs"]) + (f"      [prediction {'matched' if pred == r['obs'] else 'differed'}]") + (f"   changed: {', '.join(ch)}" if ch else ""))
            steps.append({"script": lines, "obs": r["obs"], "s": r["s"], "error": r["error"], "predicted": pred, "changed_files": ch}); toks += act + ["OBS"] + " | ".join(r["obs"]).split() + ["END"]
        final = sess.files(); diff = sess.diff(); ops = sess.ops()
    finally: sess.close()
    import hashlib
    rec = {"id": public["id"], "dom": public["dom"], "end": end, "steps": steps, "diff": diff, "calls": len(steps), "ops": ops, "final_hash": hashlib.sha256(json.dumps(final, sort_keys=True).encode()).hexdigest()[:16],
           "wall_s": round(sum(s["s"] for s in steps), 3), "exec_s": round(sum(s["s"] for s in steps), 3), "failed_checks": sum(o.startswith("FAIL") for s in steps for o in s["obs"])}
    say(f"\n  ended: {end}    diff: {json.dumps(diff) if diff else 'nothing changed'}")
    if hidden is not None:
        from stillway8.grade import grade
        v = grade(public, hidden, final, end); say(f"  independent verdict: {v['outcome']}")
    else: v = {"outcome": "ungraded", "detail": None}; say("  independent verdict: none available for this job (no hidden tests); nothing from it can be promoted")
    e = X.build(public, rec, v, "demo")
    if steps and steps[0].get("bank") and end == "DONE" and len(steps) == 1: e["memory_candidate"] = None       # the bank repaired it: no new entry, the use is logged
    open(EXP, "a").write(json.dumps(e, sort_keys=True) + "\n"); exps, snap = memory(); json.dump(snap, open(BANK, "w"), indent=1, sort_keys=True)
    say(f"  experience {e['experience']} appended to {EXP}"); say(f"  candidate memory entry: {json.dumps(e['memory_candidate'])}")
    say(f"  the bank now holds {len(snap['bank']['entries'])} entries ({BANK}):")
    for b in snap["bank"]["entries"]: say("    - " + (f"leave a {b['dom']} job alone when nothing fails" if b.get("leave") else f"proj: try {b['role']}.{b['slot']} (seen after reports of {', '.join(b['signatures'])})" if b["dom"] == "proj" else f"tab: {b['kind']} with note {b['note']} -> {b['action']}") + f"   support {b['support']}, from {b['provenance'][0]}")
    return e


def from_dir(d):
    files = {n: open(os.path.join(d, n), newline="").read() for n in sorted(os.listdir(d)) if os.path.isfile(os.path.join(d, n)) and not n.startswith(".")}; job = json.loads(files["job.json"])
    p = {"dom": job["dom"], "goal": job["goal"], "files": files}
    if job["dom"] == "proj": p.update(entry=job["entry"], mods=sorted(n[:-3] for n in files if n.endswith(".py")))
    p["id"] = f"{job['dom']}-user-{W.job_id(p)}"; return p, None


if a.smoke:
    import random
    srcs = D.sources("proj", "fixture"); rng = random.Random(a.seed); src = srcs[3]; cfg = src["cfg"]
    w1 = next(v for v in W.SLOTS["agg"]["func"] if v != cfg["func"]); j1 = None
    while j1 is None or j1[1]["reported"] != ["total"]: j1 = W.proj_job(rng, src, "bug", "func", w1)
    p1, h1 = j1; p1["id"] = h1["id"] = "proj-demo-session1"; work(p1, h1, "SESSION 1: a report total is wrong")
    j2 = None                                                  # the same project; now the fault is upstream and the same field is reported
    while j2 is None or j2[1]["reported"][0] != "total":
        s2 = rng.choice(["cmp", "thr", "dedupe"]); cands = D.wrongs(s2, cfg[s2]); j2 = W.proj_job(rng, src, "bug", s2, rng.choice(cands), tries=80)
    p2, h2 = j2; p2["id"] = h2["id"] = "proj-demo-session2"; e2 = work(p2, h2, "SESSION 2: the same project next day, with an altered precondition (the fault has moved)")
    tb = D.sources("tab", "fixture")[2]; t = W.tab_job(rng, tb, [("amt", "stmt_newer"), ("onlyS", "dupstmt")], True); t[0]["id"] = t[1]["id"] = "tab-demo-session1"; work(t[0], t[1], "SESSION 1 (tables): reconcile a ledger")
    t2 = W.tab_job(rng, tb, [("amt", "ledger_newer"), ("onlyS", "dupstmt")], False); t2[0]["id"] = t2[1]["id"] = "tab-demo-session2"; work(t2[0], t2[1], "SESSION 2 (tables): a similar difference, but the note says the ledger is the newer one")
    say("\nSMOKE DEMO FINISHED")
elif a.workspace: p, h = from_dir(a.workspace); work(p, h, f"YOUR JOB from {a.workspace}")
elif a.new:
    import random
    rng = random.Random(a.seed); srcs = D.sources(a.new, "fixture"); j = None
    while j is None: j = D.make(a.new, "fixture", rng.randrange(10 ** 6), rng.choice(["familiar", "familiar", "valid", "unans"] + (["scattered"] if a.new == "tab" else ["newmech"])), srcs)
    work(j[0], j[1], f"A NEW {a.new} JOB (seed {a.seed})")
else:
    pub = [json.loads(l) for l in open("data/v08/fixture/public.jsonl")]; hid = {h["id"]: h for h in map(json.loads, open("data/v08/fixture/hidden.jsonl"))}
    for i, p in enumerate(pub): say(f"{i:3d}  {p['id']}  {' '.join(E.header(p)[1:6])}")
    while True:
        c = input("\njob number (or q): ").strip()
        if c.lower().startswith("q"): break
        if c.isdigit() and int(c) < len(pub): work(pub[int(c)], hid[pub[int(c)]["id"]], f"JOB {c}")
