"""Operating contracts for the instruction-following runner, compared on development jobs only.

    python v08/prompt_compare.py run ARM OUT.jsonl      ARM: frozen | minimal | codex | fable
    python v08/prompt_compare.py report                 (after v08/grade.py on results/v08/prompt/*_s0.jsonl)

The runner is the pinned Qwen2.5-Coder-1.5B-Instruct in script mode with the limits of milestone 2.  Every arm gets the
same reference text (operations, what they mean, the table rules, what DONE and ASK are), the same two worked examples
and the same 72 development jobs.  Only the behavioural text at the top differs:
  frozen   the milestone-2 prompt as it was (its manual has guidance mixed into the reference); the incumbent
  minimal  one sentence
  codex    Codex's draft, transcribed from Prince's screenshot of 22 November
  fable    my draft, written after seeing Codex's and the failures of milestone 2
A reply ends the job when its first line is DONE or ASK (anything after it is kept as the model's report).
Selection rule, fixed before any arm was run: most verified jobs; arms within 2 jobs of the best are separated by fewer
jobs ended wrongly (a wrong DONE, or a change to a job that needed none); then by less time per solved job.
Codex's holdout is not used here and the chosen wording is not run on it."""
import collections, hashlib, json, os, re, sys, time
sys.path.insert(0, ".")
import importlib.util
spec = importlib.util.spec_from_file_location("m2", "v08/m2_harness.py"); m2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m2)
from stillway8.runner import Session
from stillway8.agent import EDITS

REFERENCE = '''Results are short lines of tokens: n7 is the number 7; a key token such as kA_ is the text "A " (capital A, trailing space) and ka is "a".

PROJECT jobs. A report module runs a chain of modules: load -> clean -> filter -> agg and order -> report. One setting in one module may be wrong, or nothing is wrong, or an expected value is itself out of date. Only modules reached from the entry module through deps are in use.
  check(c)           run visible check "c0" or "c1": PASS, or FAIL followed by every field the check asserts as: field exp X got Y (fields: count, groups, total, first)
  deps(m)            the modules that module m imports
  show(m)            its role and settings, for example: role filter thr n3 cmp gt
  probe(m, c)        what module m returns on the data of check c: rows "r key val qty", or "v n"
  patch(m, slot, v)  change one setting. clean: norm none|strip|lower|both, dedupe off|on. filter: thr n1..n9, cmp gt|ge|lt|le. agg: col val|qty, func sum|mean|max|min|count. order: by key|val, dir asc|desc
  revert()           undo the last patch
Meaning: clean normalises keys and, with dedupe on, drops repeated rows; filter keeps rows whose val compares with thr; agg applies func to col of the kept rows (mean is whole-number division); order sorts the kept rows by key or by (val, key), and desc reverses; the report gives count of kept rows, groups (distinct keys), total (agg) and first (first key in order).

TABLE jobs. A ledger is reconciled with a statement, and the summary of group totals is brought up to date.
  diff()             differences: "d key grp amt L S" (amounts differ), "d key grp onlyL L" (only in the ledger), "d key onlyS S" (only in the statement); or none
  fact(k)            the note on key k
  copy(k) keep(k) drop(k) add(k, g) skip(k)   resolve one difference
  recalc(g)          recompute the summary total of group g from the ledger
  rows()             the ledger
  check("c0")        the summary agrees with the ledger;  check("c1")  every difference is resolved
Rules: amt with note stmt_newer: copy. amt with ledger_newer: keep. onlyL with pending: keep. onlyL with void: drop. onlyS with "grp gX": add(k, "gX"). onlyS with dupstmt: skip. A note "nonote" means the evidence is missing.

DONE on the first line of a reply means the job is finished. ASK on the first line means the evidence needed to finish is missing (a difference with no note, or an expected value no single setting can produce); nothing should be left changed in that case.
'''
CONTRACT = {
 "minimal": "Finish the job using the operations below.",
 "codex": "Complete the user's task within the stated limits. Use the available evidence to choose your next action. Before editing, identify what you expect to change and what must stay true. When reusing a previous solution, check the assumption that makes it applicable here. Group operations into a script when you can choose them in advance. Pause when an observation could change your next action. If essential evidence is missing, leave the workspace as you found it and return ASK. After a change, check its effects. Return DONE when the available evidence supports completion. Report what you observed and distinguish it from what you predicted.",
 "fable": "Look before you change anything: run the checks, or the differences and their notes. If nothing is wrong, answer DONE and change nothing. Decide each change from what you observed, one change at a time, and only in a module the job uses. After a change, run the checks again; if the check you were fixing still fails, undo the change before trying anything else. Never send again a call that returned BAD or did not help. Put calls whose arguments you already know into one script, and end the script where the next call depends on a result. Answer DONE only after the checks pass. If a note is missing or no single change fits what you observed, undo your changes and answer ASK.",
}
MODE = m2.MODE["script"]


def system(arm): return (m2.MANUAL + "\n" + MODE) if arm == "frozen" else (CONTRACT[arm] + "\n\n" + REFERENCE + "\n" + MODE)


def episode(student, arm, p):
    """As m2_harness.episode in script mode, with the arm's system text and a first-line DONE / ASK."""
    L = m2.LIMITS; t0 = time.time(); sess = Session(p); msgs = [{"role": "system", "content": system(arm)}]
    for u, a in m2.EX["script"]: msgs += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
    msgs.append({"role": "user", "content": m2.statement(p)}); steps = []; end = "BUDGET"; why = None; tin = tout = 0; model_s = 0.0; report = ""
    try:
        for _ in range(L["calls"]):
            t = time.time(); texts, n_in, n_out = student.generate([student.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)], L["new_tokens"], max_prompt_tokens=6000)
            model_s += time.time() - t; tin += n_in[0]; tout += n_out[0]; reply = texts[0].strip(); msgs.append({"role": "assistant", "content": reply})
            first = re.sub(r"[^A-Za-z]", "", (reply.splitlines() or [""])[0]).upper()
            if first in ("DONE", "ASK"): end = first; report = reply[:400]; break
            m = re.search(r"```(?:python)?\n(.*?)```", reply, re.S); code = m.group(1) if m else re.sub(r"```(?:python)?", "", reply)
            r = sess.run(code, mode="py"); shown = (r["stdout"].strip() or "(nothing printed)")[:700] + (f"\nERROR {r['error']}" if r["error"] else "")
            steps.append({"script": [f"{l['op']} {' '.join(l['args'])}".strip() for l in r["ledger"]], "reply": reply[:600], "obs": r["obs"], "shown": shown, "s": r["s"], "error": r["error"]}); msgs.append({"role": "user", "content": shown})
            if sess.ops() > L["ops"]: why = "operation limit"; break
            if time.time() - t0 > L["seconds"]: why = "time limit"; break
        else: why = "call limit"
        final = sess.files(); changed = {n: t for n, t in final.items() if p["files"].get(n) != t}; diff = sess.diff(); ops = sess.ops()
    finally: sess.close()
    return {"id": p["id"], "dom": p["dom"], "arm": arm, "end": end, "why": why, "steps": steps, "changed": changed, "diff": diff, "calls": len(steps) + (end != "BUDGET"), "ops": ops, "final_report": report,
            "edit_scripts": sum(any(l.split()[0] in EDITS for l in s["script"]) for s in steps), "edit_ops": sum(l.split()[0] in EDITS and l.split()[0] != "REVERT" and o.startswith("OK") for s in steps for l, o in zip(s["script"], s["obs"])),
            "failed_checks": sum(o.startswith("FAIL") for s in steps for o in s["obs"]), "bad_ops": sum(o in ("BAD", "ERR") for s in steps for o in s["obs"]), "script_errors": sum(bool(s["error"]) for s in steps),
            "tokens_in": tin, "tokens_out": tout, "model_s": round(model_s, 3), "exec_s": round(sum(s["s"] for s in steps), 3), "wall_s": round(time.time() - t0, 3), "final_hash": hashlib.sha256(json.dumps(final, sort_keys=True).encode()).hexdigest()[:16]}


def jobs():
    want = {("proj", "familiar"): 12, ("proj", "altered"): 6, ("proj", "newmech"): 6, ("proj", "valid"): 6, ("proj", "unans"): 6, ("tab", "familiar"): 12, ("tab", "scattered"): 8, ("tab", "stale"): 6, ("tab", "valid"): 5, ("tab", "unans"): 5}
    path = "data/v08/prompt_jobs.json"
    if not os.path.exists(path):                               # the first jobs of each group of the development set, written once
        got = collections.Counter(); ids = []
        for h in map(json.loads, open("data/v08/dev/hidden.jsonl")):
            k = (h["id"].split("-")[0], h["group"])
            if got[k] < want.get(k, 0): got[k] += 1; ids.append(h["id"])
        json.dump(ids, open(path, "w"))
    ids = set(json.load(open(path))); return [p for p in map(json.loads, open("data/v08/dev/public.jsonl")) if p["id"] in ids]


def report():
    import numpy as np
    pub = {p["id"]: p for p in jobs()}; R = {a: [json.loads(l) for l in open(f"results/v08/prompt/{a}_s0.graded.jsonl")] for a in ("frozen", "minimal", "codex", "fable") if os.path.exists(f"results/v08/prompt/{a}_s0.graded.jsonl")}
    def substance(r): return any(n.endswith(".py") or n in ("ledger.csv", "summary.csv") for n in r["diff"])
    S = {}
    for a, rs in R.items():
        ok = [r for r in rs if r["outcome"] == "verified"]; nochange = [r for r in rs if r["kind"] in ("valid", "unans")]; un = [r for r in rs if r["kind"] == "unans"]; asks = [r for r in rs if r["end"] == "ASK"]; T = sum(r["wall_s"] for r in rs)
        S[a] = {"jobs": len(rs), "verified": len(ok), "verified_proj": sum(r["dom"] == "proj" for r in ok), "verified_tab": sum(r["dom"] == "tab" for r in ok), "wrong_done": sum(r["outcome"] == "wrong" and r["end"] == "DONE" for r in rs),
                "budget": sum(r["outcome"] == "budget" for r in rs), "needed_no_change": len(nochange), "changed_a_job_that_needed_none": sum(substance(r) for r in nochange),
                "ended_wrongly": sum((r["outcome"] == "wrong" and r["end"] == "DONE") or (r["kind"] in ("valid", "unans") and substance(r)) for r in rs),
                "edit_ops_per_job": float(np.mean([r["edit_ops"] for r in rs])), "reverts": sum(l.startswith("REVERT") for r in rs for s in r["steps"] for l in s["script"]), "asks": len(asks), "asks_on_unanswerable": sum(r["kind"] == "unans" for r in asks),
                "unanswerable": len(un), "asks_on_answerable": sum(r["kind"] != "unans" for r in asks), "seconds_per_solved_job": T / max(1, len(ok)), "seconds_per_job": T / len(rs), "calls": float(np.mean([r["calls"] for r in rs])),
                "ops": float(np.mean([r["ops"] for r in rs])), "tokens_per_job": float(np.mean([r["tokens_in"] + r["tokens_out"] for r in rs])), "bad_ops": sum(r["bad_ops"] for r in rs), "script_errors": sum(r["script_errors"] for r in rs),
                "system_words": len(system(a).split())}
    best = max(s["verified"] for s in S.values()); near = [a for a in S if S[a]["verified"] >= best - 2]; chosen = min(near, key=lambda a: (S[a]["ended_wrongly"], S[a]["seconds_per_solved_job"]))
    rows = [("verified", "Verified completions (of 72)"), ("verified_proj", "of which project jobs (36)"), ("verified_tab", "of which table jobs (36)"), ("wrong_done", "Said DONE and was wrong"), ("changed_a_job_that_needed_none", "Unnecessary edits: changed a job that needed none (of 22)"),
            ("ended_wrongly", "Jobs ended wrongly (either of the two above)"), ("edit_ops_per_job", "Editing operations per job"), ("reverts", "Reverts"), ("asks_on_unanswerable", "Appropriate ASKs (of 11 unanswerable)"), ("asks_on_answerable", "ASK on an answerable job"),
            ("budget", "Ran out of limits"), ("seconds_per_solved_job", "Seconds per solved job"), ("seconds_per_job", "Seconds per job"), ("calls", "Model calls per job"), ("ops", "Operations per job"), ("tokens_per_job", "Model tokens per job"),
            ("bad_ops", "Illegal or failed operations"), ("script_errors", "Scripts that crashed"), ("system_words", "Words in the system text")]
    f = lambda v: f"{v:.1f}" if isinstance(v, float) else str(v); arms = list(S)
    M = ["# v0.8: operating contracts for the instruction-following runner, development jobs only", "", "Qwen2.5-Coder-1.5B-Instruct (pinned), script mode, 72 development jobs, one run per arm, greedy. Same reference text, examples, jobs and limits; only the behavioural text differs (the `frozen` arm is the milestone-2 prompt as it was).", "",
         "| | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)] + [f"| {t} | " + " | ".join(f(S[a][k]) for a in arms) + " |" for k, t in rows]
    M += ["", f"Selection rule (fixed beforehand): most verified jobs; arms within 2 of the best ({', '.join(near)}) are separated by fewer jobs ended wrongly, then by less time per solved job. **Chosen: {chosen}.**"]
    ids = [r["id"] for r in next(iter(R.values()))]; A = {a: {r["id"]: r["outcome"] == "verified" for r in rs} for a, rs in R.items()}
    M += ["", "Jobs verified by one arm and not another: " + "; ".join(f"{a} not {b}: {sum(A[a][i] and not A[b][i] for i in ids)}" for a in arms for b in arms if a != b) + "."]
    open("results/v08/prompt_tables.md", "w").write("\n".join(M) + "\n"); json.dump({"arms": S, "chosen": chosen, "near_best": near}, open("results/v08/prompt_summary.json", "w"), indent=1); print("\n".join(M))


if __name__ == "__main__":
    if sys.argv[1] == "report": report()
    else:
        from stillway7.student import Student
        arm, out = sys.argv[2], sys.argv[3]; J = jobs(); done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set(); os.makedirs(os.path.dirname(out), exist_ok=True); s = Student(); t0 = time.time()
        with open(out, "a") as f:
            for n, p in enumerate(J):
                if p["id"] in done: continue
                r = episode(s, arm, p); f.write(json.dumps(r, sort_keys=True) + "\n"); f.flush(); print(f"{n + 1}/{len(J)} {p['id']} {r['end']} calls {r['calls']} ops {r['ops']} {r['wall_s']:.1f} s", flush=True)
        print(f"done in {time.time() - t0:.0f} s")
