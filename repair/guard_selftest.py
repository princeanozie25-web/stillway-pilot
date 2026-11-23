"""Development fixtures for the guard, with no model: scripted patches and scripted probe lists.   python repair/guard_selftest.py

 1  the reference fix is accepted, and a probe the report does not cover costs one question that the user confirms
 2  a fix that satisfies the report's examples but breaks a documented example is refused without a question
 3  a fix that works on the report's input and fails on another kind of input is refused after one question, with the
    user's value handed back as evidence
 4  a change that does nothing to the reported behaviour is refused
 5  a change that breaks a visible test is refused
 6  differences left when the question budget is spent are reported as unresolved
 7  the untouched copy of the snapshot is byte for byte unchanged after all of this"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repair.core import Workspace, snapshot, fhash
from repair.guard import Guard
from repair.respond import Respondent

PUB, HID = "data/repair/dev/public.jsonl", "data/repair/dev/hidden.jsonl"
P = {t["id"]: t for t in map(json.loads, open(PUB))}; H = {t["id"]: t for t in map(json.loads, open(HID))}; fails = []
def say(n, ok, text): print(f"{n}  {'PASS' if ok else 'FAIL'}  {text}"); fails.append(n) if not ok else None
def scripted(examples, probes):
    def f(prompt, schema): return ({"examples": examples} if "examples" in schema["properties"] else {"probes": probes}), 0
    return f
def setup(tid, examples, probes, edit):
    t = P[tid]; f0 = snapshot(t); g = Guard(t, f0, scripted(examples, probes), Respondent(PUB, HID)); first = g.start(); w = Workspace(f0)
    for path, old, new in edit: assert f0[path].count(old) == 1, (tid, old); w.write(path, f0[path].replace(old, new))
    return t, f0, g, w, first
I = "import inflection"; ex1 = [dict(setup=I, call="inflection.ordinalize(11)", expected="'11th'"), dict(setup=I, call="inflection.ordinalize(113)", expected="'113th'"), dict(setup=I, call="inflection.ordinalize(1)", expected="'1st'")]
pr1 = [dict(setup=I, call="inflection.ordinalize(1)"), dict(setup=I, call="inflection.ordinalize(212)"), dict(setup=I, call="inflection.ordinalize(23)")]

t, f0, g, w, first = setup("inflection-1", ex1, pr1, [("inflection/__init__.py", "if number % 10 in (11, 12, 13):", "if number % 100 in (11, 12, 13):")])
ok, fb = g.check(w); q = g.questions
say(1, ok and len(g.examples) == 2 and len(q) == 1 and q[0]["agrees_with"] == "after" and "ordinalize(11)" in first, f"reference fix accepted: {ok}; examples that reproduce: {len(g.examples)} of 3 stated; questions {len(q)} ({q[0]['expr'] if q else ''} -> {q[0]['answer'] if q else ''})")
snap_ok = g.snap.files() == f0; g.close(); w.close()

t, f0, g, w, _ = setup("inflection-1", ex1, pr1, [("inflection/__init__.py", "if number % 10 in (11, 12, 13):", "if number % 10 in (1, 2, 3):")])
ok, fb = g.check(w); say(2, not ok and g.log[-1]["reason"] == "documented example" and not g.questions, f"over-broad fix refused: {not ok}; reason: {g.log[-1].get('reason')}; questions {len(g.questions)}"); g.close(); w.close()

T = "import toolz, itertools"; ex4 = [dict(setup=T, call="list(toolz.interpose('a', [1, 2, 3]))", expected="[1, 'a', 2, 'a', 3]")]
pr4 = [dict(setup=T, call="list(toolz.interpose('a', []))"), dict(setup=T, call="list(toolz.interpose(0, itertools.repeat(1, 3)))"), dict(setup=T, call="list(toolz.interpose('-', 'abc'))")]
bad4 = [("toolz/itertoolz.py", """    inposed = concat(zip(seq, itertools.repeat(el)))
    try:
        next(inposed)
    except StopIteration:
        return iter([])
    return inposed""", """    if not seq:
        return iter([])
    inposed = concat(zip(seq[:-1], itertools.repeat(el)))
    return itertools.chain(inposed, [seq[-1]])""")]
t, f0, g, w, _ = setup("toolz-4", ex4, pr4, bad4); ok, fb = g.check(w); q = g.questions
say(3, not ok and g.log[-1]["reason"] == "question" and len(q) == 1 and q[0]["agrees_with"] == "neither" and "should give [1, 0, 1, 0, 1]" in fb, f"list-only fix refused: {not ok}; reason: {g.log[-1].get('reason')}; question: {q[0]['expr'] if q else ''} before {q[0]['predictions'][0] if q else ''}, after {q[0]['predictions'][1] if q else ''}, user says {q[0]['answer'] if q else ''}")
ok2, fb2 = g.check(w); say("3b", not ok2 and g.log[-1]["reason"] == "example" and len(g.questions) == 1, f"the same patch offered again is refused on the user's example without a new question: {not ok2 and len(g.questions) == 1}"); g.close(); w.close()

t, f0, g, w, _ = setup("toolz-4", [], [dict(setup=T, call="list(toolz.interpose('a', []))")], [("toolz/itertoolz.py", "def interpose(el, seq):", "def interpose(el, seq):  # checked")])
ok, fb = g.check(w); say(4, not ok and g.log[-1]["reason"] == "no evidence", f"change with no effect refused: {not ok}; reason: {g.log[-1].get('reason')}"); g.close(); w.close()

t, f0, g, w, _ = setup("toolz-4", ex4, pr4, [("toolz/itertoolz.py", "def cons(el, seq):", "def cons_(el, seq):")])
ok, fb = g.check(w); say(5, not ok and "the repository's tests:" in fb and "all pass" not in fb, f"change that breaks the visible tests refused: {not ok}; first failing check: {g.log[-1].get('reason')}"); g.close(); w.close()

pr6 = [dict(setup=I, call=f"inflection.ordinalize({n})") for n in (111, 212, 313, 1011)]
t, f0, g, w, _ = setup("inflection-1", ex1[:1], pr6, [("inflection/__init__.py", "if number % 10 in (11, 12, 13):", "if number % 100 in (11, 12, 13):")])
g.questions.append(dict(id=t["id"], round=1, expr="spent", predictions=["a", "b"], answer="a", agrees_with="before")); ok, fb = g.check(w)
say(6, not ok and g.unresolved and len(g.questions) == 2, f"four unexplained differences with one question left: accepted {ok}, unresolved {g.unresolved}, questions asked in all {len(g.questions)}"); snap_ok = snap_ok and g.snap.files() == f0; g.close(); w.close()
say(7, snap_ok, f"untouched copy unchanged: {snap_ok}")
print("ALL PASS" if not fails else f"FAILED: {fails}"); sys.exit(1 if fails else 0)
