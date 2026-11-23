"""The guarded solver: the plain tool loop of repair/agent.py with the runner-side guard of repair/guard.py in front of DONE.

    python repair/agent_guard.py MODEL PUBLIC.jsonl OUT.jsonl --respond HIDDEN.jsonl [--only ID,ID] [--limit N]

Same model settings, same tools and the same limits as the plain loop; the guard's own model calls are charged to the
job's output-token limit and a refused done counts as a tool call.  Three things differ from the plain loop:
  the first message carries the report's examples as the runner reproduced them;
  after every edit the runner runs its checks and adds the result to the edit's result; when they all pass it ends the job;
  done is accepted only if the guard's checks pass, otherwise its result says what failed and the job goes on;
  a job that runs out of a limit with a change that passes every check ends with DONE;
  a job that ends without an accepted DONE hands the workspace back as it was found.
--respond names the hidden half of a development set: questions are then answered at once by the stand-in respondent
(repair/respond.py).  Without it the job stops at its first question (for a sealed, two-round exchange; not built yet)."""
import json, os, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repair import agent as A
from repair.core import Workspace, snapshot, fhash
from repair.guard import Guard, ADDENDUM

STRUCT_MAX = 600                                   # output tokens for one structured guard call


NO_FORMAT = set()                                  # models whose backend refuses a JSON schema (Ollama's MLX runner answers 501)
STRUCT = dict(schema=0, prose=0, failed=0)         # how the structured calls of this process went; copied into every record


def _json_in(text):
    """The first JSON object in a model's free text, or None."""
    i = text.find("{")
    while i >= 0:
        try: out, _ = json.JSONDecoder().raw_decode(text[i:]); return out if isinstance(out, dict) else None
        except ValueError: i = text.find("{", i + 1)
    return None


def structured(model, prompt, schema, budget, timeout=180):
    """One model call returning JSON.  With a schema where the backend takes one; otherwise the schema goes into the prompt
    and the object is read out of the text.  A call that fails is counted, never passed over in silence."""
    if budget < 40: return None, 0
    def post(body):
        return json.load(urllib.request.urlopen(urllib.request.Request(A.URL, json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=timeout))
    base = dict(model=model, stream=False, think=False, keep_alive="20m", options=dict(A.OPTIONS, num_predict=min(STRUCT_MAX, budget)))
    r = None
    if model not in NO_FORMAT:
        try: r = post(dict(base, messages=[dict(role="user", content=prompt)], format=schema)); how = "schema"
        except urllib.error.HTTPError as e:
            if e.code != 501: STRUCT["failed"] += 1; return None, 0
            NO_FORMAT.add(model)
        except (TimeoutError, OSError): STRUCT["failed"] += 1; return None, 0
    if r is None:
        try: r = post(dict(base, messages=[dict(role="user", content=prompt + "\n\nAnswer with one JSON object and nothing else. It must match this JSON schema:\n" + json.dumps(schema))])); how = "prose"
        except (TimeoutError, OSError): STRUCT["failed"] += 1; return None, 0
    text = r.get("message", {}).get("content") or ""
    try: out = json.loads(text)
    except ValueError: out = _json_in(text) if how == "prose" else None
    if not isinstance(out, dict): STRUCT["failed"] += 1; return None, r.get("eval_count", 0)
    STRUCT[how] += 1; return out, r.get("eval_count", 0)


def solve(model, task, ask, say=lambda s: None):
    L = A.LIMITS; files0 = snapshot(task); ws = Workspace(files0); tools = A.Tools(ws, task); s0 = dict(STRUCT)
    used = dict(calls=0, tests=0, tokens=0, prompt_tokens=0, turns=0, dropped=0, repeats=0, guard_tokens=0, refused=0); steps = []; end = None; silent = 0; last = None; accepted_by = None; t0 = time.time(); model_s = tool_s = guard_s = 0.0
    def struct(prompt, schema):
        out, tok = structured(model, prompt, schema, L["tokens"] - used["tokens"]); used["tokens"] += tok; used["guard_tokens"] += tok; return out, tok
    guard = Guard(task, files0, struct, ask)
    try:
        t = time.time(); found = guard.start(); guard_s += time.time() - t
        top = sorted(n + ("/" if os.path.isdir(os.path.join(ws.dir, n)) else "") for n in os.listdir(ws.dir) if not n.startswith("."))
        msgs = [dict(role="system", content=A.SYSTEM + ADDENDUM), dict(role="user", content=f"Bug report:\n{task['report']}{found}\n\nTop level of the repository:\n" + "\n".join(top))]
        while end is None:
            left = L["seconds"] - (time.time() - t0)
            if left <= 0: end = ("LIMIT", "time"); break
            if used["tokens"] >= L["tokens"]: end = ("LIMIT", "output tokens"); break
            t = time.time()
            try: r = A.chat(model, msgs, min(A.PER_TURN, L["tokens"] - used["tokens"]), left + 5)
            except (TimeoutError, OSError) as e:
                end = ("LIMIT", "time") if time.time() - t0 >= L["seconds"] else ("LIMIT", f"model call failed: {type(e).__name__}: {e}"[:200]); break
            dt = time.time() - t; model_s += dt; m = r.get("message", {}); calls = m.get("tool_calls") or []
            used["tokens"] += r.get("eval_count", 0); used["prompt_tokens"] += r.get("prompt_eval_count", 0); used["turns"] += 1
            step = dict(turn=used["turns"], think=(m.get("thinking") or "")[:3000], say=(m.get("content") or "")[:2000], tokens_in=r.get("prompt_eval_count", 0), tokens_out=r.get("eval_count", 0), model_s=round(dt, 2), stop=r.get("done_reason"), calls=[])
            steps.append(step); msgs.append(dict(role="assistant", content=m.get("content") or "", **({"tool_calls": calls} if calls else {})))
            if not calls:
                silent += 1
                if silent > A.MAX_SILENT: end = ("LIMIT", "no tool call"); break
                msgs.append(dict(role="user", content="Call a tool. Call done when the bug is fixed and checked, or ask if you cannot fix it.")); continue
            silent = 0
            for c in calls:
                fn = c.get("function", {}); name = fn.get("name"); args = fn.get("arguments") or {}
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except ValueError: args = {}
                if not isinstance(args, dict): args = {}
                if name == "ask": end = ("ASK", str(args.get("question", ""))[:1000]); step["calls"].append(dict(tool=name, args=args)); break
                if name == "done":                                                          # ---- the guard
                    t = time.time(); ok, why = guard.check(ws, len(guard.questions) + 1); dt = time.time() - t; guard_s += dt
                    step["calls"].append(dict(tool=name, args=args, accepted=ok, out=why[:4000], s=round(dt, 2))); say(f"    -- done {'accepted' if ok else 'refused: ' + why.splitlines()[0][:120] + (' | ' + why.splitlines()[1][:120] if len(why.splitlines()) > 1 else '')}")
                    if ok: accepted_by = "solver's done"; end = ("DONE", str(args.get("summary", ""))[:1000]); break
                    if guard.unresolved: q = guard.log[-1]; end = ("ASK", "The change alters calls the report does not mention and the question budget is spent."); break
                    used["refused"] += 1
                    if used["calls"] >= L["calls"]: end = ("LIMIT", "tool calls"); break
                    used["calls"] += 1; last = None
                    msgs.append(dict(role="tool", tool_name=name, content=f"{why}\n[{L['calls'] - used['calls']} tool calls left, {L['tests'] - used['tests']} run or test calls left, {max(0, L['tokens'] - used['tokens'])} tokens left]")); continue
                if used["calls"] >= L["calls"]: end = ("LIMIT", "tool calls"); break
                used["calls"] += 1; t = time.time(); sig = (name, json.dumps(args, sort_keys=True))
                if name in ("test", "run") and used["tests"] >= L["tests"]: out = "No run or test calls left."
                elif name in ("list", "read", "search") and sig == last: out = "Same call as your last one; the result has not changed. Take a different step: edit, test, done or ask."; used["repeats"] += 1
                elif name in ("list", "read", "search", "edit", "test", "run"):
                    used["tests"] += name in ("test", "run")
                    try: out = getattr(tools, name)(**args)
                    except ValueError as e: out = f"Refused: {e}"
                    except Exception as e: out = f"Tool error: {type(e).__name__}: {e}"[:300]
                else: out = f"No such tool: {name}. The tools are list, read, search, edit, run, test, done, ask."
                dt = time.time() - t; tool_s += dt; last = sig
                if name == "edit" and out.startswith(("Edited", "Created")):                 # ---- the guard, after every edit
                    t = time.time(); state, reason, text = guard.basic(ws)
                    if state != "none" or reason == "no example": out += "\n" + text
                    if state == "pass":
                        ok, why = guard.check(ws)
                        if ok: accepted_by = "runner, after an edit"; end = ("DONE", "Every check passed after an edit; the runner ended the job.")
                        elif guard.unresolved: end = ("ASK", "The change alters calls the report does not mention and the question budget is spent.")
                        else: out += "\n" + why
                    guard_s += time.time() - t
                step["calls"].append(dict(tool=name, args=args, out=out[:4000], s=round(dt, 2)))
                if end: say(f"    {used['calls']:>2} {name} -> {end[0]}: {end[1]}"); break
                msgs.append(dict(role="tool", tool_name=name, content=f"{out}\n[{L['calls'] - used['calls']} tool calls left, {L['tests'] - used['tests']} run or test calls left, {max(0, L['tokens'] - used['tokens'])} tokens left]"))
                say(f"    {used['calls']:>2} {name} {json.dumps(args)[:110]} -> {out.splitlines()[0][:90] if out else ''}")
            if r.get("prompt_eval_count", 0) + r.get("eval_count", 0) > 0.7 * A.NUM_CTX: used["dropped"] += A.trim(msgs, int(0.25 * A.NUM_CTX))
        files1 = ws.files()
        if end[0] == "LIMIT" and files1 != files0:                                               # ---- the guard, at the limit
            t = time.time(); ok, why = guard.check(ws); guard_s += time.time() - t
            if ok: accepted_by = "runner, at the limit"; end = ("DONE", f"Out of a limit ({end[1]}) with a change that passes every check; the runner ended the job.")
    finally: ws.close(); guard.close()
    left_as = {p: files1.get(p) for p in sorted(set(files0) | set(files1)) if files0.get(p) != files1.get(p)}
    changed = left_as if end[0] == "DONE" else {}                      # anything but an accepted DONE: the workspace goes back as it was found
    return dict(id=task["id"], repo=task["repo"], model=model, arm="guard", settings=A.SETTINGS, end=end[0], end_text=end[1], used=used, wall_s=round(time.time() - t0, 1), model_s=round(model_s, 1), tool_s=round(tool_s, 1), guard_s=round(guard_s, 1),
                changed=changed, discarded={} if end[0] == "DONE" else left_as, start_hash=fhash(files0), final_hash=fhash(files1) if end[0] == "DONE" else fhash(files0), accepted_by=accepted_by, guard=guard.summary(), structured={k: STRUCT[k] - s0[k] for k in STRUCT}, steps=steps)


def main():
    model, pub, out = sys.argv[1:4]; a = sys.argv[4:]
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None; limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    assert "--respond" in a, "a sealed exchange is not built yet: give --respond HIDDEN.jsonl (development sets only)"
    from repair.respond import Respondent
    ask = Respondent(pub, a[a.index("--respond") + 1])
    tasks = [json.loads(l) for l in open(pub)]; tasks = [t for t in tasks if only is None or t["id"] in only][:limit]; done = set()
    if os.path.exists(out):
        good = []
        for l in open(out):
            try: done.add(json.loads(l)["id"]); good.append(l)
            except ValueError: pass
        open(out, "w").writelines(good)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    A.chat(model, [dict(role="user", content="hi")], 1, 300, tools=None, think=False)
    for t in tasks:
        if t["id"] in done: continue
        print(f"{t['id']}  ({model}, guard)", flush=True); r = solve(model, t, ask, say=lambda s: print(s, flush=True)); g = r["guard"]
        print(f"  => {r['end']} ({r['end_text'][:100]})  calls {r['used']['calls']}, tests {r['used']['tests']}, tokens {r['used']['tokens']} (guard {r['used']['guard_tokens']}), {r['wall_s']} s, refused {r['used']['refused']}, questions {len(g['questions'])}, examples {len(g['examples'])}, structured {r['structured']}, files changed {list(r['changed'])}", flush=True)
        with open(out, "a") as f: f.write(json.dumps(r, sort_keys=True) + "\n")


if __name__ == "__main__": main()
