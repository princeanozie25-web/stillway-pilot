"""Milestone 2: one frozen model, the same operations, called one at a time or composed in a script.

    python v08/m2_harness.py single|script PUBLIC.jsonl OUT.jsonl [--jobs IDS.json] [--limit N]

The model is the pinned Qwen2.5-Coder-1.5B-Instruct of v0.7, unchanged, greedy.  Both modes get the same system text
(operations manual, rules, one worked example per domain), the same jobs, the same limits: 14 model calls, 60 operations,
90 s per job, 220 new tokens per call.  The only difference is what one reply may be:
  single   exactly one operation call; the reply to it is what the operation returned
  script   a Python script that may call any of the operations, with variables, loops and conditions; the reply to it
           is what the script printed (and an error line if it crashed)
Every operation is counted in the ledger, inside scripts too.  Records are ungraded; v08/grade.py grades them."""
import argparse, ast, hashlib, json, os, re, sys, time
sys.path.insert(0, ".")
from stillway8.runner import Session
from stillway8.agent import EDITS

LIMITS = {"calls": 14, "ops": 60, "seconds": 90.0, "new_tokens": 220}
MANUAL = '''You finish small jobs in a sandbox by calling operations. Results are short lines of tokens: n7 is the number 7; a key token such as kA_ is the text "A " (capital A, trailing space) and ka is "a".

PROJECT jobs. A report module runs a chain of modules: load -> clean -> filter -> agg and order -> report. One setting in one module may be wrong, or nothing is wrong, or an expected value is itself out of date.
  check(c)           run visible check "c0" or "c1": PASS, or FAIL followed by every field the check asserts as: field exp X got Y (fields: count, groups, total, first)
  deps(m)            the modules that module m imports
  show(m)            its role and settings, for example: role filter thr n3 cmp gt
  probe(m, c)        what module m returns on the data of check c: rows "r key val qty", or "v n"
  patch(m, slot, v)  change one setting. clean: norm none|strip|lower|both, dedupe off|on. filter: thr n1..n9, cmp gt|ge|lt|le. agg: col val|qty, func sum|mean|max|min|count. order: by key|val, dir asc|desc
  revert()           undo the last patch
Meaning: clean normalises keys and, with dedupe on, drops repeated rows; filter keeps rows whose val compares with thr; agg applies func to col of the kept rows (mean is whole-number division); order sorts the kept rows by key or by (val, key), and desc reverses; the report gives count of kept rows, groups (distinct keys), total (agg) and first (first key in order).
Only modules reached from the entry module through deps are in use. If both checks pass, change nothing. If no single setting explains the expected values, answer ASK.

TABLE jobs. Reconcile a ledger with a statement, then bring the summary of group totals up to date.
  diff()             differences: "d key grp amt L S" (amounts differ), "d key grp onlyL L" (only in the ledger), "d key onlyS S" (only in the statement); or none
  fact(k)            the note on key k
  copy(k) keep(k) drop(k) add(k, g) skip(k)   resolve one difference
  recalc(g)          recompute the summary total of group g from the ledger
  rows()             the ledger
  check("c0")        the summary agrees with the ledger;  check("c1")  every difference is resolved
Rules: amt with note stmt_newer: copy. amt with ledger_newer: keep. onlyL with pending: keep. onlyL with void: drop. onlyS with "grp gX": add(k, "gX"). onlyS with dupstmt: skip. A note "nonote" means the evidence is missing: answer ASK and change nothing. After copy, drop or add, recalc the group affected. With no differences and c0 passing, change nothing.

When the job is finished answer DONE on its own. If evidence is missing answer ASK on its own.
'''
MODE = {"single": 'Reply with exactly one operation call and nothing else, for example check("c0"). You will be shown what it returned.',
        "script": "Reply with one short Python script in a ```python block. It may call several operations, keep results in variables, use loops and conditions, and must print what you need to see. You will be shown what it printed."}
EX = {"single": [("Project job. Entry module m2. Modules: m0 m1 m2 m3 m4 m5. Check c0 was reported failing.", 'check("c0")'), ("FAIL first exp kb got ka", 'check("c1")'), ("PASS", 'deps("m2")'), ("m0 m3 m5", 'show("m0")'),
                 ("role order by key dir asc", 'probe("m3", "c0")'), ("r ka n7 n1 r kb n7 n3", 'patch("m0", "dir", "desc")'), ("OK", 'check("c0")'), ("PASS", 'check("c1")'), ("PASS", "DONE"),
                 ("Table job. Reconcile the ledger with the statement.", "diff()"), ("d k2 g1 amt n6 n4 d k5 onlyS n3", 'fact("k2")'), ("stmt_newer", 'fact("k5")'), ("dupstmt", 'copy("k2")'), ("OK", 'skip("k5")'), ("OK", 'recalc("g1")'),
                 ("OK n9", 'check("c0")'), ("PASS", 'check("c1")'), ("PASS", "DONE")],
      "script": [("Project job. Entry module m2. Modules: m0 m1 m2 m3 m4 m5. Check c0 was reported failing.", '```python\nprint(check("c0"), "|", check("c1"))\nfor m in deps("m2").split():\n    print(m, show(m))\n```'),
                 ("FAIL first exp kb got ka | PASS\nm0 role order by key dir asc\nm3 role filter thr n6 cmp gt\nm5 role agg col val func sum", '```python\nprint(probe("m3", "c0"))\n```'),
                 ("r ka n7 n1 r kb n7 n3", '```python\nprint(patch("m0", "dir", "desc"), check("c0"), check("c1"))\n```'), ("OK PASS PASS", "DONE"),
                 ("Table job. Reconcile the ledger with the statement.", '```python\nd = diff()\nprint(d, "|", check("c0"))\nfor item in d.split("d ")[1:]:\n    k = item.split()[0]\n    print(k, fact(k))\n```'),
                 ("d k2 g1 amt n6 n4 d k5 onlyS n3 | PASS\nk2 stmt_newer\nk5 dupstmt", '```python\nprint(copy("k2"), skip("k5"), recalc("g1"), check("c0"), check("c1"))\n```'), ("OK OK OK n9 PASS PASS", "DONE")]}
OPNAMES = {"check", "deps", "show", "probe", "patch", "revert", "diff", "fact", "copy", "keep", "drop", "add", "skip", "recalc", "rows"}


def statement(p):
    return f"Project job. Entry module {p['entry']}. Modules: {' '.join(p['mods'])}. Check {p['goal']} was reported failing." if p["dom"] == "proj" else "Table job. Reconcile the ledger with the statement."


def one_call(text):
    """A reply in single mode -> one line of the small language, or None."""
    t = re.sub(r"```(?:python)?", "", text).strip().splitlines(); t = t[0].strip() if t else ""
    try: node = ast.parse(t, mode="eval").body
    except SyntaxError: return None
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in OPNAMES and not node.keywords and all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in node.args)): return None
    return " ".join([node.func.id.upper()] + [a.value for a in node.args])


def episode(student, mode, p):
    t0 = time.time(); sess = Session(p); msgs = [{"role": "system", "content": MANUAL + "\n" + MODE[mode]}]
    for u, a in EX[mode]: msgs += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
    msgs.append({"role": "user", "content": statement(p)}); steps = []; end = "BUDGET"; why = None; tin = tout = 0; model_s = 0.0; invalid = 0
    try:
        for _ in range(LIMITS["calls"]):
            t = time.time(); texts, n_in, n_out = student.generate([student.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)], LIMITS["new_tokens"], max_prompt_tokens=6000)
            model_s += time.time() - t; tin += n_in[0]; tout += n_out[0]; reply = texts[0].strip(); msgs.append({"role": "assistant", "content": reply})
            bare = re.sub(r"```(?:python)?", "", reply).strip()
            if bare in ("DONE", "ASK"): end = bare; break
            if mode == "single":
                line = one_call(reply)
                if line is None: invalid += 1; steps.append({"script": [], "reply": reply[:300], "obs": ["BAD"], "s": 0, "error": "not one operation call"}); msgs.append({"role": "user", "content": "BAD: reply with exactly one operation call, or DONE, or ASK."}); continue
                r = sess.run(line); shown = r["obs"][0] if r["obs"] else "ERR"
            else:
                m = re.search(r"```(?:python)?\n(.*?)```", reply, re.S); code = m.group(1) if m else bare
                r = sess.run(code, mode="py"); shown = (r["stdout"].strip() or "(nothing printed)")[:700] + (f"\nERROR {r['error']}" if r["error"] else "")
            steps.append({"script": [f"{l['op']} {' '.join(l['args'])}".strip() for l in r["ledger"]], "reply": reply[:600], "obs": r["obs"], "shown": shown, "s": r["s"], "error": r["error"]})
            msgs.append({"role": "user", "content": shown})
            if sess.ops() > LIMITS["ops"]: why = "operation limit"; break
            if time.time() - t0 > LIMITS["seconds"]: why = "time limit"; break
        else: why = "call limit"
        final = sess.files(); changed = {n: t for n, t in final.items() if p["files"].get(n) != t}; diff = sess.diff(); ops = sess.ops()
    finally: sess.close()
    return {"id": p["id"], "dom": p["dom"], "mode": mode, "end": end, "why": why, "steps": steps, "changed": changed, "diff": diff, "calls": len(steps) + (end != "BUDGET"), "ops": ops, "invalid_replies": invalid,
            "edit_scripts": sum(any(l.split()[0] in EDITS for l in s["script"]) for s in steps), "failed_checks": sum(o.startswith("FAIL") for s in steps for o in s["obs"]),
            "bad_ops": sum(o in ("BAD", "ERR") for s in steps for o in s["obs"]) , "script_errors": sum(bool(s["error"]) for s in steps), "tokens_in": tin, "tokens_out": tout,
            "model_s": round(model_s, 3), "exec_s": round(sum(s["s"] for s in steps), 3), "wall_s": round(time.time() - t0, 3), "final_hash": hashlib.sha256(json.dumps(final, sort_keys=True).encode()).hexdigest()[:16]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("public"); ap.add_argument("out"); ap.add_argument("--jobs", default=""); ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    from stillway7.student import Student
    jobs = [json.loads(l) for l in open(a.public)]
    if a.jobs: want = json.load(open(a.jobs)); jobs = [j for j in jobs if j["id"] in set(want)]
    jobs = jobs[:a.limit] if a.limit else jobs; done = {json.loads(l)["id"] for l in open(a.out)} if os.path.exists(a.out) else set(); os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    s = Student(); t0 = time.time()
    with open(a.out, "a") as f:
        for n, p in enumerate(jobs):
            if p["id"] in done: continue
            r = episode(s, a.mode, p); f.write(json.dumps(r, sort_keys=True) + "\n"); f.flush(); print(f"{n + 1}/{len(jobs)} {p['id']} {r['end']} calls {r['calls']} ops {r['ops']} {r['wall_s']:.1f} s", flush=True)
    print(f"done in {time.time() - t0:.0f} s")
