"""The guard for freely written patches: the runner checks a change before it accepts DONE.

It carries the Q5 procedure over to ordinary repositories.  A candidate is the solver's patch; the other candidate is
the repository as it was.  Nothing here reads a grade or a hidden test.

  at the start   the solver model writes the report's examples as runnable expressions with the value the user expects;
                 the runner runs each on an untouched copy of the snapshot and keeps those that reproduce the complaint
  after an edit  checks 1 to 3 below are run at once and their result is added to the edit's result; when they all pass
                 the runner goes on to check 4 and, if that passes too, ends the job itself with DONE
  at the limit   the same: a job that runs out of a limit with a change that passes every check ends with DONE
  at DONE        1  the repository's visible tests must pass
                 2  documented examples (doctests) in the changed files that held before must still hold  [public specification]
                 3  every reproduced example must now give the value the user expects
                 4  disposable probe: the model proposes a few other calls of the changed code; the runner runs each on the
                    untouched copy and on the patched workspace.  Where the two differ and the report does not say which
                    is right, the user is asked one focused question: this call, these two values, which is intended?
                    The answer may be neither.  At most two questions a job.
  refusal        a failed check is handed back to the solver as the result of its done call, with the concrete evidence
  fallback       if the job ends any other way than an accepted DONE, the workspace is put back as it was found

Every model call the guard makes is charged to the job's own output-token limit."""
import ast, difflib, json, os, re
from repair.core import Workspace, run_tests, evaluate, doc_examples, brief, is_test, fhash

QUESTIONS, PROBES, CONFIRM = 2, 6, 2          # question budget per job; probes per check; confirmations after which other differences are taken as explained
EX_SCHEMA = dict(type="object", properties=dict(examples=dict(type="array", maxItems=4, items=dict(type="object", properties=dict(setup=dict(type="string"), call=dict(type="string"), observed=dict(type="string"), expected=dict(type="string")), required=["setup", "call", "observed", "expected"]))), required=["examples"])
PR_SCHEMA = dict(type="object", properties=dict(probes=dict(type="array", maxItems=PROBES, items=dict(type="object", properties=dict(setup=dict(type="string"), call=dict(type="string")), required=["setup", "call"]))), required=["probes"])
EX_PROMPT = """A user reported this bug in a Python repository:

{report}

The importable top-level packages are: {packages}

Write the examples the report states as Python that can be run. For each example give
- setup: the import lines it needs, and any lines that build its input, separated by newlines
- call: one Python expression whose value shows the behaviour, written as the user would call it
- observed: the wrong value the user got, written exactly as Python's repr() would print it
- expected: the value the user says it should be, written exactly as Python's repr() would print it. If the user expects an exception, write: raises ErrorName

For instance, for a report saying "textkit.shorten('hello world', 5) returns 'hello world' but I expected 'hello'":
{{"setup": "import textkit", "call": "textkit.shorten('hello world', 5)", "observed": "'hello world'", "expected": "'hello'"}}

Use only examples the report states, with the values the report states. Return JSON only."""
PR_PROMPT = """A user reported this bug in a Python repository:

{report}

This change was made to fix it:

{diff}

Write up to {n} short Python expressions that call the changed code, to check that the change does what the report asks and nothing else. Cover: the inputs from the report; inputs of the kind the report says already work; and edge cases such as empty input, another argument type (a tuple, a string, an iterator), other argument values. Each expression must finish quickly and return a small value (wrap iterators in list()).

For each give setup (the import lines it needs) and call (one expression). Return JSON only."""
ADDENDUM = """

After every edit the runner checks your change at once: the examples from the bug report, the documented examples in the files you changed, and the repository's tests. The result is added to the edit's result. When all of them pass, the runner compares a few further calls before and after your change and then ends the job for you. If a check fails you are told what failed and you can continue."""


def _norm(s): return re.sub(r"\s+", " ", str(s)).strip()
def _canon(s):
    """A value as text, in one spelling: Python's own repr where the text is a literal; a literal quoted once too often is unquoted."""
    s = _norm(s)
    if re.fullmatch(r"[A-Za-z_]\w*(Error|Exception|Warning)", s): return "raises " + s            # a bare exception name
    try: v = ast.literal_eval(s)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        if len(s) > 2 and s[0] == s[-1] and s[0] in "'\"":                                     # a literal wrapped in quotes that do not parse as a string
            try: return repr(ast.literal_eval(s[1:-1]))
            except (ValueError, SyntaxError, MemoryError, RecursionError): pass
        return s
    if isinstance(v, str):
        try:
            inner = ast.literal_eval(v)
            if not isinstance(inner, str): return repr(inner)
        except (ValueError, SyntaxError, MemoryError, RecursionError): pass
    return repr(v)
BROKEN = ("no result", "raises NameError", "raises ModuleNotFoundError", "raises ImportError", "raises SyntaxError", "raises AttributeError")          # most likely the call itself could not be run
def _usable(v): return len(v) <= 300 and " at 0x" not in v and not v.startswith(BROKEN)


class Guard:
    def __init__(self, task, files0, structured, ask):
        """structured(prompt, schema) -> (dict or None, tokens): one model call returning JSON.  ask(question) -> answer."""
        self.task, self.files0, self.structured, self.ask = task, files0, structured, ask
        self.snap = Workspace(files0)                       # never edited: the 'before' side of every probe
        self.examples, self.log, self.questions = [], [], []; self.tokens = self.probe_runs = self.checks = 0; self.unresolved = False
        self._doc, self._basic, self._full = {}, {}, {}
        roots = [("" if r in (".", "") else r.rstrip("/") + "/") for r in task["pythonpath"].split(os.pathsep)]
        self.packages = sorted({p[len(r):].split("/")[0] for r in roots for p in files0 if p.startswith(r) and p.endswith("/__init__.py") and p[len(r):].count("/") == 1 and not is_test(p)})
        self.pre = "".join(f"try:\n    import {p}\n    from {p} import *\nexcept Exception: pass\n" for p in self.packages)
        self.where = {}                                     # top-level function and class names defined once in the repository's source -> their module
        for r in roots:
            for p, text in files0.items():
                if p.startswith(r) and p.endswith(".py") and not is_test(p):
                    mod = p[len(r):-3].replace("/", ".").removesuffix(".__init__")
                    for m in re.finditer(r"^(?:def|class) ([A-Za-z_]\w*)", text, re.M): self.where.setdefault(m.group(1), set()).add(mod)
        self.where = {k: next(iter(v)) for k, v in self.where.items() if len(v) == 1}

    def close(self): self.snap.close()

    def _fix(self, pairs):
        """The program for each call, fixed once on the untouched copy: the packages are imported, the model's own setup lines are
        tried and may fail without spoiling the call, and a name the model placed in the wrong module is bound from where the
        repository defines it.  Returns (values on the untouched copy, programs).  A program is the exact (setup, expression)
        that is then run unchanged on the patched workspace and sent unchanged to the user: all three sides answer one question."""
        wrap = lambda s: self.pre + f"try: exec({s!r}, globals())\nexcept BaseException: pass\n"
        progs = [(wrap(s), c) for s, c in pairs]; out = self._run(self.snap, progs)
        retry = [(i, self._resolve(c)) for i, (s, c) in enumerate(pairs) if out[i].startswith(("raises NameError", "raises AttributeError", "raises TypeError"))]; retry = [(i, x) for i, x in retry if x]
        if retry:
            alt = [(wrap(pairs[i][0]) + imp, c) for i, (imp, c) in retry]; again = self._run(self.snap, alt)
            for (i, _), prog, v in zip(retry, alt, again):
                if not v.startswith(("raises NameError", "raises AttributeError", "raises TypeError", "no result")): out[i] = v; progs[i] = prog
        return out, progs

    def _run(self, ws, progs):
        self.probe_runs += 1; return evaluate(ws, self.task["pythonpath"], [tuple(p) for p in progs])

    def _resolve(self, call):
        names = [n for n in set(re.findall(r"[A-Za-z_]\w*", call)) if n in self.where]
        if not names: return None
        fixed = call
        for n in names: fixed = re.sub(r"(?<![\w.])(?:[A-Za-z_]\w*\.)+" + n + r"\b", n, fixed)
        return "".join(f"try: from {self.where[n]} import {n}\nexcept Exception: pass\n" for n in names), fixed

    def _doctests(self, ws, files): self.probe_runs += 1; return doc_examples(ws, self.task["pythonpath"], files)

    def start(self):
        """Formalise the report.  Returns the lines to add to the solver's first message."""
        out, tok = self.structured(EX_PROMPT.format(report=self.task["report"], packages=", ".join(self.packages) or "(see the repository)"), EX_SCHEMA); self.tokens += tok
        cand = [(str(e.get("setup", "")), str(e.get("call", "")), _canon(e.get("expected", "")), _canon(e.get("observed", ""))) for e in (out or {}).get("examples", []) if isinstance(e, dict) and e.get("call")][:4]
        before, progs = self._fix([(s, c) for s, c, _, _ in cand]) if cand else ([], [])
        for (s, c, want, saw), got, prog in zip(cand, before, progs):
            if _canon(got) == want and saw and saw != want: want, saw = saw, want          # the repository gives the value filed as expected: the two were filed the wrong way round
            ok = _usable(got) and bool(want) and _canon(got) != want and (not saw or _canon(got) == saw)       # kept only if the repository shows exactly what the user saw
            self.log.append(dict(step="example", setup=s, expr=c, expected=want, observed=saw, before=got, reproduced=bool(ok)))
            if ok: self.examples.append(dict(setup=s, expr=c, prog=list(prog), expected=want, before=got, source="report"))
        if not self.examples: return ""
        return "\n\nThe runner ran the report's examples on the repository as it is now:\n" + "\n".join(f"  {e['expr']}  gives {e['before']}; the report expects {e['expected']}" for e in self.examples)

    def _changed(self, files1): return sorted(p for p in set(self.files0) | set(files1) if self.files0.get(p) != files1.get(p) and not is_test(p))

    def basic(self, ws):
        """Checks 1 to 3 on the workspace as it stands.  (state, reason, text): state is 'pass', 'fail' or 'none' (no source change, or nothing to judge by)."""
        files1 = ws.files(); h = fhash(files1)
        if h in self._basic: return self._basic[h]
        t = self.task; changed = self._changed(files1); rec = dict(step="basic", changed=changed); self.log.append(rec)
        def result(state, reason, text): rec.update(state=state, reason=reason); self._basic[h] = (state, reason, text); return self._basic[h]
        if not changed: return result("none", "no change", "You have not changed any source file of the repository.")
        lines, bad = [], None
        if self.examples:
            got = self._run(ws, [e["prog"] for e in self.examples]); rec["examples"] = [dict(expr=e["expr"], expected=e["expected"], now=g) for e, g in zip(self.examples, got)]
            for e, g in zip(self.examples, got):
                ok = _canon(g) == e["expected"]; lines.append(f"  {e['expr']}  gives {g}" + ("  (as expected)" if ok else f"; expected {e['expected']} ({'the user said so' if e['source'] == 'user' else 'from the report'})"))
                if not ok: bad = bad or "example"
        py = [p for p in changed if p.endswith(".py") and p in self.files0 and p in files1]
        if py:
            key = tuple(py)
            if key not in self._doc: self._doc[key] = self._doctests(self.snap, py)
            now = self._doctests(ws, py); lost = [k for k, v in self._doc[key].items() if v == "passed" and now.get(k, "passed") != "passed"]
            rec["doc_examples"] = dict(held_before=sum(v == "passed" for v in self._doc[key].values()), failing_before=sum(v != "passed" for v in self._doc[key].values()), lost=lost[:10])
            if lost: bad = bad or "documented example"; lines += ["  a documented example that held before your change does not hold now:"] + [f"    {k.split(': ', 1)[1]}   now {now[k].removeprefix('failed: ')}" for k in lost[:3]]
        r = run_tests(ws, t["pythonpath"], t["tests"]); self.probe_runs += 1; tests_ok = bool(r["results"]) and not any(v in ("failed", "error") for v in r["results"].values())
        lines.append("  the repository's tests: " + ("all pass" if tests_ok else brief(r, 12).replace("\n", "\n    ")))
        if not tests_ok: bad = bad or "visible tests"
        text = "Runner's check of your change:\n" + "\n".join(lines)
        if bad: return result("fail", bad, text)
        return result("pass" if self.examples else "none", "" if self.examples else "no example", text)

    def check(self, ws, n=0):
        """All four checks.  (accepted, feedback).  Sets self.unresolved when the question budget cannot settle what is left."""
        self.checks += 1; files1 = ws.files(); h = fhash(files1); t = self.task; state, reason, text = self.basic(ws)
        rec = dict(step="check", n=self.checks, basic=state); self.log.append(rec)
        def no(reason, text): rec.update(accepted=False, reason=reason); return False, "Not accepted. " + text
        if state == "fail" or reason == "no change": return no(reason, text)
        if h in self._full: rec.update(accepted=self._full[h][0], reason="seen before"); return self._full[h]
        changed = self._changed(files1)
        diff = "\n".join(l for p in changed for l in difflib.unified_diff((self.files0.get(p) or "").splitlines(), (files1.get(p) or "").splitlines(), "a/" + p, "b/" + p, lineterm="", n=2))
        out, tok = self.structured(PR_PROMPT.format(report=t["report"], diff="\n".join(diff.splitlines()[:120]), n=PROBES), PR_SCHEMA); self.tokens += tok
        seen = {_norm(e["expr"]) for e in self.examples}; pairs = []
        for e in (out or {}).get("probes", []):
            if not isinstance(e, dict) or not e.get("call"): continue
            k = _norm(e["call"])
            if k not in seen and len(k) <= 300: seen.add(k); pairs.append((str(e.get("setup", "")), str(e["call"])))
        pairs = pairs[:PROBES]; old, progs = self._fix(pairs) if pairs else ([], []); new = self._run(ws, progs) if pairs else []
        rec["probes"] = [dict(setup=s, expr=c, before=o, after=n_) for (s, c), o, n_ in zip(pairs, old, new)]
        core = lambda c: re.sub(r"^list\((.*)\)$", r"\1", _norm(c)); told = [core(e["expr"]) for e in self.examples]        # a probe that restates an example is settled by check 3
        settled = lambda c: any(x.endswith(core(c)) or core(c).endswith(x) for x in told)
        diffs = [(s, c, o, v, g) for (s, c), o, v, g in zip(pairs, old, new, progs) if _usable(o) and _usable(v) and _canon(o) != _canon(v) and not settled(c)]
        diffs.sort(key=lambda d: not d[3].startswith("raises"))                   # a change that makes a call fail is asked about first
        if not self.examples and not diffs: return no("no evidence", "Nothing the runner can run shows that your change alters the behaviour the report complains about. Reproduce the report's example with run, then change the code so that it gives the expected value.")
        confirmed = 0
        for s, c, o, v, prog in diffs:
            if confirmed >= CONFIRM: break
            if len(self.questions) >= QUESTIONS:
                self.unresolved = True; rec.update(accepted=False, reason="question budget")
                return False, "Not accepted: your change alters the result of calls the report does not mention, and no question is left to settle whether that is intended."
            q = dict(id=t["id"], round=len(self.questions) + 1, setup=s, expr=c, program=list(prog), predictions=[o, v]); a = self.ask(dict(q, setup=prog[0], expr=prog[1])); ans = a["value"]     # the user is asked about the program that was run, not the model's spelling of it
            self.questions.append(dict(q, answer=ans, agrees_with="after" if _canon(ans) == _canon(v) else "before" if _canon(ans) == _canon(o) else "neither"))
            if _canon(ans) == _canon(v): confirmed += 1; continue
            if _usable(ans): self.examples.append(dict(setup=s, expr=c, prog=list(prog), expected=_canon(ans), before=o, source="user"))
            self._basic.clear()
            return no("question", f"The user was asked about a call the report does not mention.\n{prog[1]}  should give {ans}. Before your change it gave {o}; with your change it gives {v}.")
        rec.update(accepted=True, confirmed=confirmed, differences=len(diffs)); self._full[h] = (True, ""); return True, ""

    def summary(self):
        return dict(examples=self.examples, questions=self.questions, checks=self.checks, probe_runs=self.probe_runs, tokens=self.tokens, unresolved=self.unresolved, log=self.log)
