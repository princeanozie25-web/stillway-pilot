"""The grader.  It is not imported by the solver and never runs while a solver does.

    python repair/grade.py PUBLIC.jsonl HIDDEN.jsonl RECORDS.jsonl OUT.graded.jsonl

For each record: start from the task's snapshot (the pinned repository with the bug in it) but with the repository's
own, complete tests; lay the solver's changed files over it, except tests and test configuration, which are always the
repository's own; run every test in the sandbox.
  verified   the solver said DONE, every test the bug broke now passes and no other test that passed before fails
  wrong      the solver said DONE and that is not so
  abstained  the solver ended with a question (ASK)
  budget     the solver ran out of a limit
patch_ok says whether the files as left would have passed, whatever the ending.  clean says an ASK or LIMIT ending left
no file changed."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repair.core import Workspace, base_files, is_test, run_tests


def grade(rec, task, hid):
    files = dict(base_files(task["repo"])); src = {p: t for p, t in rec["changed"].items() if not is_test(p)}
    files.update({p: t for p, t in task["overlay"].items() if not is_test(p) and t is not None})      # the bug itself; the tests stay the repository's own
    for p, t in src.items():
        if t is None: files.pop(p, None)
        else: files[p] = t
    w = Workspace(files); r = run_tests(w, task["pythonpath"], task["tests"], timeout=180); w.close(); res = r["results"]
    f2p = [t for t in hid["fail_to_pass"] if res.get(t) == "passed"]; broken = [t for t in hid["pass_to_pass"] if res.get(t) != "passed"]
    ok = len(f2p) == len(hid["fail_to_pass"]) and not broken
    outcome = {"DONE": "verified" if ok else "wrong", "ASK": "abstained", "LIMIT": "budget"}[rec["end"]]
    g = {k: v for k, v in rec.items() if k != "steps"}; g.pop("changed")
    g.update(outcome=outcome, patch_ok=ok, f2p_passed=len(f2p), f2p_total=len(hid["fail_to_pass"]), p2p_broken=len(broken), p2p_broken_ids=broken[:5], source_changed=sorted(src), tests_changed=sorted(p for p in rec["changed"] if is_test(p)),
             clean=not rec["changed"], bug_files=hid["bug_files"], right_file=bool(set(src) & set(hid["bug_files"])), kind=hid.get("kind", ""), grade_timeout=r["timeout"])
    return g


def main(pub, hidden, recs, out):
    P = {t["id"]: t for t in map(json.loads, open(pub))}; H = {t["id"]: t for t in map(json.loads, open(hidden))}; rows = []
    for l in open(recs):
        rec = json.loads(l); g = grade(rec, P[rec["id"]], H[rec["id"]]); rows.append(g)
        print(f"{g['id']:<14} {g['end']:<5} {g['outcome']:<9} patch_ok={g['patch_ok']!s:<5} fixed {g['f2p_passed']}/{g['f2p_total']} broke {g['p2p_broken']}  calls {g['used']['calls']:>2} tests {g['used']['tests']} tokens {g['used']['tokens']:>5} {g['wall_s']:>6} s  {g['source_changed']}", flush=True)
    open(out, "w").writelines(json.dumps(g, sort_keys=True) + "\n" for g in rows)
    n = lambda k: sum(g["outcome"] == k for g in rows); print(f"{len(rows)} jobs: verified {n('verified')}, wrong {n('wrong')}, abstained {n('abstained')}, budget {n('budget')}")


if __name__ == "__main__": main(*sys.argv[1:5])
