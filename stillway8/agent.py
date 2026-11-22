"""One job with the small core, through the runner.  The same loop serves every arm of every experiment.

The core is asked for one script at a time (tokens up to EXEC), the runner executes it in the sandbox, the observations
are appended, and so on until the core says DONE or ASK or a limit is reached.  Nothing here sees a hidden file; the
record it returns holds only what a grader needs later (the final files) and what was spent."""
import hashlib, json, time
from stillway8 import expert as E
from stillway8.model import Reader
from stillway8.runner import Session

LIMITS = {"calls": 16, "ops": 48, "seconds": 20.0, "tokens_per_call": 40}
STOP = {E.TOK["EXEC"], E.TOK["DONE"], E.TOK["ASK"]}
EDITS = ("PATCH", "REVERT", "COPY", "KEEP", "DROP", "ADD", "SKIP", "RECALC", "USE")


def episode(model, public, limits=LIMITS, propose=None, predict=False, procedure=None):
    """Returns a record.  `propose(tokens) -> token list` replaces the core (used for the teacher and other references)."""
    t0 = time.time(); sess = Session(public); toks = E.header(public); steps = []; end = "BUDGET"; model_s = 0.0; gen = 0; fed = 0; why = None; predict_s = 0.0
    bank_ops = 0; reader = Reader(model) if model is not None and not propose else None; fed_upto = 0
    def ask(stop, n, keep=True, extra=()):                     # feed whatever the reader has not seen yet, then let it write
        nonlocal fed_upto
        reader.feed(E.ids(toks[fed_upto:])); fed_upto = len(toks)
        if extra: saved = (reader.state, reader.logits, reader.n); reader.feed(E.ids(list(extra)))
        out = [E.VOCAB[i] for i in reader.write(stop, n, keep)]
        if extra: reader.state, reader.logits, reader.n = saved
        return out
    try:
        if procedure:                                          # the bank goes first: one script; anything but PASS leaves the workspace as it was
            sess.set_procedure(procedure); r = sess.run("USE"); bank_ops = sess.ops(); steps.append({"script": ["USE"], "obs": r["obs"], "s": r["s"], "error": r["error"], "bank": True, "inner": [f"{l['op']} {' '.join(l['args'])}".strip() for l in r["ledger"][:-1]]})
            if r["obs"] == ["PASS"]: end = "DONE"
            if r["obs"] == ["ASK"]: end = "ASK"                  # a guarded bank found more than one change that satisfies the checks: it asks, and changes nothing
        while len(steps) < limits["calls"] and end not in ("DONE", "ASK"):
            toks.append("ACT"); t = time.time()
            a = propose(toks) if propose else ask(STOP, limits["tokens_per_call"], keep=False)
            model_s += time.time() - t; gen += len(a); fed += len(toks)
            if a and a[-1] in ("DONE", "ASK") and len(a) == 1: end = a[0]; break
            if not a or a[-1] != "EXEC": why = "malformed script"; break
            lines = [l.strip() for l in " ".join(a[:-1]).split(";") if l.strip()]
            if not lines or sess.ops() - bank_ops + len(lines) > limits["ops"]: why = "operation limit" if lines else "empty script"; break
            pred = None
            if predict and model is not None:                  # the effect the core expects, written down before anything runs
                t = time.time(); pred = " ".join(ask({E.TOK["END"]}, 64, keep=False, extra=a + ["OBS"])[:-1]).split(" | "); predict_s += time.time() - t
            before = sess.files() if predict else None
            r = sess.run("\n".join(lines)); obs = r["obs"]; steps.append({"script": lines, "obs": obs, "s": r["s"], "error": r["error"]})
            if predict: now = sess.files(); steps[-1].update(predicted=pred, changed_files=sorted(n for n in now if now[n] != before.get(n)))
            toks += a + ["OBS"] + " | ".join(obs).split() + ["END"]
            if time.time() - t0 > limits["seconds"]: why = "time limit"; break
            if len(toks) > model.ctx - limits["tokens_per_call"] if model is not None else False: why = "context full"; break
        else: why = None if end in ("DONE", "ASK") else "call limit"
        final = sess.files(); changed = {n: t for n, t in final.items() if public["files"].get(n) != t}; diff = sess.diff(); ops = sess.ops()
    finally: sess.close()
    exec_s = sum(s["s"] for s in steps)
    return {"id": public["id"], "dom": public["dom"], "end": end, "why": why, "steps": steps, "changed": changed, "diff": diff, "calls": len(steps) + (end != "BUDGET") - (1 if procedure and end in ("DONE", "ASK") and len(steps) == 1 else 0), "ops": ops, "bank_ops": bank_ops,
            "edit_scripts": sum(any(l.split()[0] in EDITS for l in s["script"]) for s in steps), "failed_checks": sum(o.startswith("FAIL") for s in steps for o in s["obs"]),
            "bad_ops": sum(o in ("BAD", "ERR") for s in steps for o in s["obs"]), "tokens_out": gen, "tokens_in": fed, "model_s": round(model_s, 4), "exec_s": round(exec_s, 4), "wall_s": round(time.time() - t0, 4), "predict_s": round(predict_s, 4),
            "final_hash": hashlib.sha256(json.dumps(final, sort_keys=True).encode()).hexdigest()[:16]}


def final_files(public, record): return {**public["files"], **record["changed"]}
