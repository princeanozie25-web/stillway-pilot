"""The two loops must be the same loop.   python repair/loop_selftest.py

Drives the plain loop (repair/agent.py) and the guarded loop (repair/agent_guard.py) with the same scripted stand-in for
a model, the guard replaced by one that accepts everything and says nothing.  Their records must agree on the ending,
the files changed, every tool call and its result, and every counter.  Then, with the real guard and a scripted patch:
a refused done costs a tool call and the job goes on; a job that ends without an accepted DONE hands the workspace back."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repair import agent as A, agent_guard as G
from repair.respond import Respondent

PUB, HID = "data/repair/dev/public.jsonl", "data/repair/dev/hidden.jsonl"
T = {t["id"]: t for t in map(json.loads, open(PUB))}; fails = []
def say(n, ok, text): print(f"{n}  {'PASS' if ok else 'FAIL'}  {text}"); fails.append(n) if not ok else None
def call(name, **args): return dict(function=dict(name=name, arguments=args))
def scripted(turns):
    it = iter(turns)
    def chat(model, messages, budget, timeout, tools=A.TOOLS, think=True):
        try: calls = next(it)
        except StopIteration: calls = []
        return dict(message=dict(content="", tool_calls=calls), eval_count=10, prompt_eval_count=100, done_reason="stop")
    return chat
FIX = ("inflection/__init__.py", "if number % 10 in (11, 12, 13):", "if number % 100 in (11, 12, 13):"); BAD = (FIX[0], FIX[1], "if number % 10 in (1, 2, 3):")
script = lambda edit: [[call("list", path="inflection")], [call("read", path="inflection/__init__.py", start=220, end=230)], [call("read", path="inflection/__init__.py", start=220, end=230)], [call("nonsense")],
          [call("edit", path=edit[0], old=edit[1], new=edit[2])], [call("run", code="import inflection\ninflection.ordinalize(11)")], [call("test")], [], [call("done", summary="fixed")]]
class Yes:
    questions = []; unresolved = False; log = []
    def __init__(self, *a): pass
    def start(self): return ""
    def check(self, ws, n=0): return True, ""
    def basic(self, ws): return "none", "", ""
    def summary(self): return {}
    def close(self): pass
strip = lambda r: (r["end"], r["end_text"], r["changed"], r["final_hash"], {k: r["used"][k] for k in ("calls", "tests", "tokens", "prompt_tokens", "turns", "dropped", "repeats")}, [[(c["tool"], c["args"], c.get("out") or None) for c in s["calls"]] for s in r["steps"]])

t = T["inflection-1"]; real_chat, real_guard = A.chat, G.Guard
A.chat = scripted(script(FIX)); plain = A.solve("fake", t)
A.chat = scripted(script(FIX)); G.Guard = Yes; guarded = G.solve("fake", t, None); G.Guard = real_guard
say(1, strip(plain) == strip(guarded) and plain["end"] == "DONE" and plain["used"]["repeats"] == 1 and plain["used"]["calls"] == 7, f"same scripted model, guard that accepts everything: records agree ({strip(plain) == strip(guarded)}); ending {plain['end']}, {plain['used']['calls']} tool calls, {plain['used']['repeats']} repeat caught")

none = lambda prompt, schema, *a, **k: (None, 0); real_struct = G.structured; G.structured = lambda model, prompt, schema, budget, timeout=180: ({"examples": [dict(setup="import inflection", call="inflection.ordinalize(11)", expected="'11th'")]} if "examples" in schema["properties"] else {"probes": []}, 25)
A.chat = scripted(script(BAD) + [[call("done", summary="again")], [call("ask", question="?")]]); r = G.solve("fake", t, Respondent(PUB, HID))
say(2, r["end"] == "ASK" and r["changed"] == {} and r["discarded"] and r["used"]["refused"] == 2 and r["used"]["calls"] == 9 and r["final_hash"] == r["start_hash"] and r["used"]["guard_tokens"] == 25,
    f"over-broad fix: done refused {r['used']['refused']} times (each a tool call: {r['used']['calls']} in all), ending {r['end']}, files handed back changed: {len(r['changed'])}, patch kept aside for the record: {len(r['discarded'])}, guard tokens charged: {r['used']['guard_tokens']}")
A.chat = scripted(script(FIX)); r = G.solve("fake", t, Respondent(PUB, HID))
say(3, r["end"] == "DONE" and list(r["changed"]) == ["inflection/__init__.py"] and not r["discarded"] and r["guard"]["checks"] == 1, f"reference fix: ending {r['end']}, files changed {list(r['changed'])}, checks {r['guard']['checks']}, questions {len(r['guard']['questions'])}")
A.chat, G.structured = real_chat, real_struct
print("ALL PASS" if not fails else f"FAILED: {fails}"); sys.exit(1 if fails else 0)
