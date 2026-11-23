"""A solver: one local model in a tool loop over one repository.

    python repair/agent.py MODEL PUBLIC.jsonl OUT.jsonl [--only ID,ID] [--limit N]

Every model gets the same tools, the same limits and the same sampling settings (below).  The loop ends with DONE, ASK
or LIMIT.  A record holds every step, the tokens and seconds spent, and the files the solver changed; nothing in it is a
grade.  The output file is restartable: jobs already in it are skipped."""
import ast, hashlib, json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repair.core import Workspace, snapshot, run_tests, run_py, brief, fhash, SKIP_DIRS

LIMITS = dict(calls=30, tests=8, tokens=12000, seconds=600)     # per job, identical for every model; 'tests' counts test and run together
NUM_CTX, PER_TURN, SEED, MAX_SILENT = 32768, 2048, 7, 3
OPTIONS = dict(temperature=0, seed=SEED, num_ctx=NUM_CTX, presence_penalty=0, repeat_penalty=1.0)
READ_MAX, READ_DEFAULT, SEARCH_MAX, LIST_MAX, RUN_LINES = 200, 120, 40, 150, 40
URL = "http://localhost:11434/api/chat"

SYSTEM = f"""You are fixing one bug in a Python repository. You can only act through the tools.

The bug report describes what a user saw. The repository's existing tests all pass at the start: they do not cover the bug.

Work in small steps: find the code responsible, read it, change it with edit, then check your change. Use run to execute a short piece of Python, for example the call from the bug report, and test to run the repository's tests.

Limits for the whole job: {LIMITS['calls']} tool calls, of which at most {LIMITS['tests']} may be run or test, and {LIMITS['tokens']} tokens of your own output. Each tool result tells you what is left.

End the job with done when you have fixed the bug and checked the fix. End it with ask, putting one question to the user, if you cannot fix it with confidence. A wrong fix reported as done is worse than a question."""

def _f(name, desc, props, req): return dict(type="function", function=dict(name=name, description=desc, parameters=dict(type="object", properties=props, required=req)))
S, I = dict(type="string"), dict(type="integer")
TOOLS = [
    _f("list", "List the files under a directory of the repository, with their length in lines.", dict(path=dict(S, description="directory, relative to the repository root; default '.'")), []),
    _f("read", f"Read lines of one file, numbered. At most {READ_MAX} lines per call.", dict(path=S, start=dict(I, description="first line, default 1"), end=dict(I, description=f"last line, default start+{READ_DEFAULT - 1}")), ["path"]),
    _f("search", f"Find lines matching a regular expression in the repository's text files. Returns at most {SEARCH_MAX} lines as path:line: text.", dict(pattern=S, path=dict(S, description="file or directory to search; default '.'")), ["pattern"]),
    _f("edit", "Replace one exact span of text in a file with new text. 'old' must be copied exactly from the file (without line numbers) and must occur once. To create a new file, give its path and an empty 'old'.", dict(path=S, old=S, new=S), ["path", "old", "new"]),
    _f("test", "Run the repository's tests with pytest, or only the file or test given as target (for example tests/test_x.py or tests/test_x.py::test_name). Returns the counts and the first failure.", dict(target=dict(S, description="optional file or test id")), []),
    _f("run", f"Run a short piece of Python in the repository, with its packages importable, and return what it prints (the last {RUN_LINES} lines). If the last line is an expression, its value is printed.", dict(code=S), ["code"]),
    _f("done", "End the job: the bug is fixed.", dict(summary=dict(S, description="one or two sentences on what was wrong and what you changed")), ["summary"]),
    _f("ask", "End the job without a fix, with one question for the user.", dict(question=S), ["question"]),
]
SETTINGS = hashlib.sha256(json.dumps([LIMITS, NUM_CTX, PER_TURN, SEED, MAX_SILENT, OPTIONS, READ_MAX, READ_DEFAULT, SEARCH_MAX, LIST_MAX, RUN_LINES, SYSTEM, TOOLS], sort_keys=True).encode()).hexdigest()[:16]


def chat(model, messages, budget, timeout, tools=TOOLS, think=True):
    body = dict(model=model, messages=messages, tools=tools, stream=False, think=think, keep_alive="20m", options=dict(OPTIONS, num_predict=budget))
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


class Tools:
    def __init__(self, ws, task): self.ws, self.task = ws, task

    def _rel(self, path):
        path = str(path or ".").strip() or "."; full = self.ws.path(path); return full, os.path.relpath(full, self.ws.dir)

    def list(self, path=".", **_):
        full, rel = self._rel(path)
        if os.path.isfile(full): return f"{rel} is a file; use read."
        if not os.path.isdir(full): return f"No such directory: {rel}"
        rows = []
        for d, dirs, names in os.walk(full):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith("."))
            for n in sorted(names):
                p = os.path.join(d, n)
                try: k = sum(1 for _ in open(p, encoding="utf-8"))
                except (UnicodeDecodeError, OSError): continue
                rows.append(f"{os.path.relpath(p, self.ws.dir)}  ({k} lines)")
        more = f"\n... and {len(rows) - LIST_MAX} more files; list a subdirectory to see them" if len(rows) > LIST_MAX else ""
        return "\n".join(rows[:LIST_MAX]) + more if rows else "(empty)"

    def read(self, path=None, start=1, end=None, **_):
        full, rel = self._rel(path)
        if not os.path.isfile(full): return f"No such file: {rel}"
        lines = open(full, encoding="utf-8", errors="replace").read().splitlines(); n = len(lines)
        try: a = max(1, int(start or 1))
        except (TypeError, ValueError): a = 1
        try: b = int(end) if end not in (None, "") else a + READ_DEFAULT - 1
        except (TypeError, ValueError): b = a + READ_DEFAULT - 1
        b = min(b, a + READ_MAX - 1, n)
        if a > n: return f"{rel} has {n} lines."
        return f"{rel}, lines {a} to {b} of {n}:\n" + "\n".join(f"{i:>5}| {lines[i - 1]}" for i in range(a, b + 1))

    def search(self, pattern=None, path=".", **_):
        if not pattern: return "Give a pattern."
        full, rel = self._rel(path)
        try: rx = re.compile(str(pattern))
        except re.error: rx = re.compile(re.escape(str(pattern)))
        files = [full] if os.path.isfile(full) else [os.path.join(d, n) for d, dirs, names in os.walk(full) if not dirs.__setitem__(slice(None), sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith("."))) for n in sorted(names)]
        hits = []
        for p in files:
            try: text = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError): continue
            hits += [f"{os.path.relpath(p, self.ws.dir)}:{i}: {l.strip()[:160]}" for i, l in enumerate(text.splitlines(), 1) if rx.search(l)]
        if not hits: return "No match."
        return "\n".join(hits[:SEARCH_MAX]) + (f"\n... {len(hits) - SEARCH_MAX} more matching lines; narrow the pattern or the path" if len(hits) > SEARCH_MAX else "")

    def edit(self, path=None, old=None, new=None, **_):
        if path is None or old is None or new is None: return "edit needs path, old and new."
        full, rel = self._rel(path); old, new = str(old), str(new)
        if not os.path.exists(full):
            if old != "": return f"No such file: {rel}. To create it, give an empty 'old'."
            self.ws.write(rel, new); return f"Created {rel} ({len(new.splitlines())} lines)." + self._syntax(rel, new)
        if os.path.isdir(full): return f"{rel} is a directory."
        text = open(full, encoding="utf-8", newline="").read()
        if old == "": return f"{rel} exists. Give in 'old' the exact text to replace."
        k = text.count(old)
        if k == 0:
            if re.search(r"^\s*\d+\| ", old, re.M): return "Not found: 'old' contains line numbers. Copy the text without the 'NNN| ' prefix."
            first = next((l.strip() for l in old.splitlines() if l.strip()), ""); at = [i for i, l in enumerate(text.splitlines(), 1) if first and l.strip() == first]
            return "Not found: 'old' does not occur in the file exactly as given." + (f" Its first line does occur at line {', '.join(map(str, at[:5]))}; check the indentation and the following lines with read." if at else " Read the file again and copy the span exactly.")
        if k > 1: return f"'old' occurs {k} times in {rel}. Include more of the surrounding lines so that it occurs once."
        out = text.replace(old, new); self.ws.write(rel, out)
        a = text[:text.index(old)].count("\n") + 1; b = a + max(len(new.splitlines()), 1) - 1; lines = out.splitlines()
        lo, hi = max(1, a - 2), min(len(lines), b + 2, a + 13)
        return f"Edited {rel}: lines {a} to {b} now read\n" + "\n".join(f"{i:>5}| {lines[i - 1]}" for i in range(lo, hi + 1)) + self._syntax(rel, out)

    def _syntax(self, rel, text):
        if not rel.endswith(".py"): return ""
        try: ast.parse(text); return ""
        except SyntaxError as e: return f"\nWARNING: {rel} now has a syntax error at line {e.lineno}: {e.msg}"

    def run(self, code=None, **_):
        if not code or not str(code).strip(): return "Give Python code to run."
        code = str(code)
        try:
            tree = ast.parse(code)
            if tree.body and isinstance(tree.body[-1], ast.Expr):                      # show the value of a final expression, as a console would
                tree.body[-1:] = ast.parse("_ = None\nif _ is not None: print(repr(_))").body; tree.body[-2].value = ast.parse(code).body[-1].value; code = ast.unparse(ast.fix_missing_locations(tree))
        except SyntaxError as e: return f"SyntaxError in your code at line {e.lineno}: {e.msg}"
        text, rc = run_py(self.ws, self.task["pythonpath"], code); lines = text.strip().splitlines()
        return ("\n".join(lines[-RUN_LINES:]) or "(no output)") + ("" if rc == 0 else f"\n(exit status {rc})")

    def test(self, target="", **_):
        targets = self.task["tests"]
        if target and str(target).strip():
            t = str(target).strip(); f = t.split("::")[0]
            if t.startswith("-"): return "target must be a file or a test id."
            full, rel = self._rel(f)
            if not os.path.exists(full): return f"No such file: {rel}"
            targets = [rel + t[len(f):]]
        r = run_tests(self.ws, self.task["pythonpath"], targets); return brief(r)


def trim(msgs, need):
    """Blank the oldest tool results until about `need` tokens are freed.  The same rule for every model."""
    freed = n = 0
    for m in msgs:
        if freed >= need: break
        if m["role"] == "tool" and not m["content"].startswith("[result dropped"):
            freed += len(m["content"]) // 3; m["content"] = "[result dropped to save space; call the tool again if you need it]"; n += 1
    return n


def solve(model, task, say=lambda s: None):
    files0 = snapshot(task); ws = Workspace(files0); tools = Tools(ws, task)
    top = sorted(n + ("/" if os.path.isdir(os.path.join(ws.dir, n)) else "") for n in os.listdir(ws.dir) if not n.startswith("."))
    msgs = [dict(role="system", content=SYSTEM), dict(role="user", content=f"Bug report:\n{task['report']}\n\nTop level of the repository:\n" + "\n".join(top))]
    used = dict(calls=0, tests=0, tokens=0, prompt_tokens=0, turns=0, dropped=0, repeats=0); steps = []; end = None; silent = 0; last = None; t0 = time.time(); model_s = tool_s = 0.0
    try:
        while end is None:
            left = LIMITS["seconds"] - (time.time() - t0)
            if left <= 0: end = ("LIMIT", "time"); break
            if used["tokens"] >= LIMITS["tokens"]: end = ("LIMIT", "output tokens"); break
            t = time.time()
            try: r = chat(model, msgs, min(PER_TURN, LIMITS["tokens"] - used["tokens"]), left + 5)
            except (TimeoutError, OSError) as e:
                end = ("LIMIT", "time") if time.time() - t0 >= LIMITS["seconds"] else ("LIMIT", f"model call failed: {type(e).__name__}: {e}"[:200]); break
            dt = time.time() - t; model_s += dt; m = r.get("message", {}); calls = m.get("tool_calls") or []
            used["tokens"] += r.get("eval_count", 0); used["prompt_tokens"] += r.get("prompt_eval_count", 0); used["turns"] += 1
            step = dict(turn=used["turns"], think=(m.get("thinking") or "")[:3000], say=(m.get("content") or "")[:2000], tokens_in=r.get("prompt_eval_count", 0), tokens_out=r.get("eval_count", 0), model_s=round(dt, 2), stop=r.get("done_reason"), calls=[])
            steps.append(step); msgs.append(dict(role="assistant", content=m.get("content") or "", **({"tool_calls": calls} if calls else {})))
            if not calls:
                silent += 1
                if silent > MAX_SILENT: end = ("LIMIT", "no tool call"); break
                msgs.append(dict(role="user", content="Call a tool. Call done when the bug is fixed and checked, or ask if you cannot fix it.")); continue
            silent = 0
            for c in calls:
                fn = c.get("function", {}); name = fn.get("name"); args = fn.get("arguments") or {}
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except ValueError: args = {}
                if not isinstance(args, dict): args = {}
                if name == "done": end = ("DONE", str(args.get("summary", ""))[:1000]); step["calls"].append(dict(tool=name, args=args)); break
                if name == "ask": end = ("ASK", str(args.get("question", ""))[:1000]); step["calls"].append(dict(tool=name, args=args)); break
                if used["calls"] >= LIMITS["calls"]: end = ("LIMIT", "tool calls"); break
                used["calls"] += 1; t = time.time()
                sig = (name, json.dumps(args, sort_keys=True))
                if name in ("test", "run") and used["tests"] >= LIMITS["tests"]: out = "No run or test calls left."
                elif name in ("list", "read", "search") and sig == last: out = "Same call as your last one; the result has not changed. Take a different step: edit, test, done or ask."; used["repeats"] += 1
                elif name in ("list", "read", "search", "edit", "test", "run"):
                    used["tests"] += name in ("test", "run")
                    try: out = getattr(tools, name)(**args)
                    except ValueError as e: out = f"Refused: {e}"
                    except Exception as e: out = f"Tool error: {type(e).__name__}: {e}"[:300]
                else: out = f"No such tool: {name}. The tools are list, read, search, edit, run, test, done, ask."
                dt = time.time() - t; tool_s += dt; last = sig
                step["calls"].append(dict(tool=name, args=args, out=out[:4000], s=round(dt, 2)))
                msgs.append(dict(role="tool", tool_name=name, content=f"{out}\n[{LIMITS['calls'] - used['calls']} tool calls left, {LIMITS['tests'] - used['tests']} run or test calls left, {max(0, LIMITS['tokens'] - used['tokens'])} tokens left]"))
                say(f"    {used['calls']:>2} {name} {json.dumps(args)[:110]} -> {out.splitlines()[0][:90] if out else ''}")
            if r.get("prompt_eval_count", 0) + r.get("eval_count", 0) > 0.7 * NUM_CTX: used["dropped"] += trim(msgs, int(0.25 * NUM_CTX))
        files1 = ws.files()
    finally: ws.close()
    changed = {p: files1.get(p) for p in sorted(set(files0) | set(files1)) if files0.get(p) != files1.get(p)}
    return dict(id=task["id"], repo=task["repo"], model=model, arm="plain", settings=SETTINGS, end=end[0], end_text=end[1], used=used, wall_s=round(time.time() - t0, 1), model_s=round(model_s, 1), tool_s=round(tool_s, 1),
                changed=changed, start_hash=fhash(files0), final_hash=fhash(files1), steps=steps)


def main():
    model, pub, out = sys.argv[1:4]; a = sys.argv[4:]
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None; limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    tasks = [json.loads(l) for l in open(pub)]; tasks = [t for t in tasks if only is None or t["id"] in only][:limit]
    done = set()
    if os.path.exists(out):
        good = []
        for l in open(out):
            try: done.add(json.loads(l)["id"]); good.append(l)
            except ValueError: pass                                  # a torn last line from a killed run
        open(out, "w").writelines(good)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    chat(model, [dict(role="user", content="hi")], 1, 300, tools=None, think=False)             # load the model before any clock starts
    for t in tasks:
        if t["id"] in done: continue
        print(f"{t['id']}  ({model})", flush=True); r = solve(model, t, say=lambda s: print(s, flush=True))
        print(f"  => {r['end']} ({r['end_text'][:100]})  calls {r['used']['calls']}, tests {r['used']['tests']}, tokens {r['used']['tokens']}, {r['wall_s']} s, files changed {list(r['changed'])}", flush=True)
        with open(out, "a") as f: f.write(json.dumps(r, sort_keys=True) + "\n")


if __name__ == "__main__": main()
