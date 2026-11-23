"""The guard for freely written patches: the runner checks a change before it accepts DONE.

It carries the Q5 procedure over to ordinary repositories.  A candidate is the solver's patch; the other candidate is
the repository as it was.  Nothing here reads a grade or a hidden test.

  at the start   the solver model writes the report's examples as runnable expressions with the value the user expects;
                 the runner runs each on an untouched copy of the snapshot and keeps those that reproduce the complaint
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
import difflib, json, re
from repair.core import Workspace, run_tests, evaluate, doc_examples, brief, is_test

QUESTIONS, PROBES, CONFIRM = 2, 6, 2          # question budget per job; probes per check; confirmations after which other differences are taken as explained
EX_SCHEMA = dict(type="object", properties=dict(examples=dict(type="array", maxItems=4, items=dict(type="object", properties=dict(setup=dict(type="string"), call=dict(type="string"), expected=dict(type="string")), required=["setup", "call", "expected"]))), required=["examples"])
PR_SCHEMA = dict(type="object", properties=dict(probes=dict(type="array", maxItems=PROBES, items=dict(type="object", properties=dict(setup=dict(type="string"), call=dict(type="string")), required=["setup", "call"]))), required=["probes"])
EX_PROMPT = """A user reported this bug in a Python repository:

{report}

The importable top-level packages are: {packages}

Write the examples from the report as Python that can be run. For each example give
- setup: the import lines it needs (and any lines that build its input), separated by newlines
- call: one Python expression whose value shows the behaviour
- expected: the value the user expects, written exactly as Python's repr() would print it. If the user expects an exception, write: raises ErrorName

Use only examples the report states. Return JSON only."""
PR_PROMPT = """A user reported this bug in a Python repository:

{report}

This change was made to fix it:

{diff}

Write up to {n} short Python expressions that call the changed code, to check that the change does what the report asks and nothing else. Cover: the inputs from the report; inputs of the kind the report says already work; and edge cases such as empty input, another argument type (a tuple, a string, an iterator), other argument values. Each expression must finish quickly and return a small value (wrap iterators in list()).

For each give setup (the import lines it needs) and call (one expression). Return JSON only."""
ADDENDUM = """

When you call done, the runner checks your change before accepting it: the repository's tests, the documented examples in the files you changed, the examples from the bug report, and a few further calls compared before and after your change. If a check fails, the result of done tells you what failed and you can continue."""


def _norm(s): return re.sub(r"\s+", " ", str(s)).strip()
def _usable(v): return len(v) <= 300 and " at 0x" not in v and not v.startswith("no result")


class Guard:
    def __init__(self, task, files0, structured, ask):
        """structured(prompt, schema) -> (dict or None, tokens): one model call returning JSON.  ask(question) -> answer."""
        self.task, self.files0, self.structured, self.ask = task, files0, structured, ask
        self.snap = Workspace(files0)                       # never edited: the 'before' side of every probe
        self.examples, self.log, self.questions = [], [], []; self.tokens = self.probe_runs = self.checks = 0; self.unresolved = False
        self._doc = {}

    def close(self): self.snap.close()

    def _eval(self, ws, pairs): self.probe_runs += 1; return evaluate(ws, self.task["pythonpath"], pairs)

    def start(self):
        """Formalise the report.  Returns the lines to add to the solver's first message."""
        pk = sorted({p.split("/")[-2] for p in self.files0 if p.endswith("/__init__.py") and not is_test(p) and p.count("/") <= 2})
        out, tok = self.structured(EX_PROMPT.format(report=self.task["report"], packages=", ".join(pk) or "(see the repository)"), EX_SCHEMA); self.tokens += tok
        cand = [(str(e.get("setup", "")), str(e.get("call", "")), _norm(e.get("expected", ""))) for e in (out or {}).get("examples", []) if isinstance(e, dict) and e.get("call")][:4]
        before = self._eval(self.snap, [(s, c) for s, c, _ in cand]) if cand else []
        for (s, c, want), got in zip(cand, before):
            ok = _usable(got) and want and _norm(got) != want
            self.log.append(dict(step="example", setup=s, expr=c, expected=want, before=got, reproduced=bool(ok)))
            if ok: self.examples.append(dict(setup=s, expr=c, expected=want, before=got, source="report"))
        if not self.examples: return ""
        return "\n\nThe runner ran the report's examples on the repository as it is now:\n" + "\n".join(f"  {e['expr']}  gives {e['before']}; the report expects {e['expected']}" for e in self.examples)

    def _doctests(self, ws, files): self.probe_runs += 1; return doc_examples(ws, self.task["pythonpath"], files)

    def check(self, ws, round_no):
        """(accepted, feedback).  Sets self.unresolved when the question budget cannot settle what is left."""
        self.checks += 1; files1 = ws.files(); t = self.task
        changed = sorted(p for p in set(self.files0) | set(files1) if self.files0.get(p) != files1.get(p) and not is_test(p))
        rec = dict(step="check", n=self.checks, changed=changed); self.log.append(rec)
        def no(reason, text): rec.update(accepted=False, reason=reason); return False, "Not accepted. " + text
        if not changed: return no("no change", "You have not changed any source file of the repository.")
        r = run_tests(ws, t["pythonpath"], t["tests"]); self.probe_runs += 1
        if any(v in ("failed", "error") for v in r["results"].values()) or not r["results"]: return no("visible tests", "The repository's tests no longer pass:\n" + brief(r, 25))
        py = [p for p in changed if p.endswith(".py") and p in self.files0 and p in files1]
        if py:
            key = tuple(py)
            if key not in self._doc: self._doc[key] = self._doctests(self.snap, py)
            now = self._doctests(ws, py); lost = [k for k, v in self._doc[key].items() if v == "passed" and now.get(k, "passed") != "passed"]
            rec["doc_examples"] = dict(held_before=sum(v == "passed" for v in self._doc[key].values()), failing_before=sum(v != "passed" for v in self._doc[key].values()), lost=lost[:10])
            if lost: return no("documented example", "A documented example in a file you changed held before your change and does not hold now:\n" + "\n".join(f"  {k.split(': ', 1)[1]}   now {now[k].removeprefix('failed: ')}" for k in lost[:3]))
        if self.examples:
            got = self._eval(ws, [(e["setup"], e["expr"]) for e in self.examples]); bad = [(e, g) for e, g in zip(self.examples, got) if _norm(g) != e["expected"]]
            rec["examples"] = [dict(expr=e["expr"], expected=e["expected"], now=g) for e, g in zip(self.examples, got)]
            if bad: return no("example", "\n".join(f"{e['expr']}  should give {e['expected']} ({'the user said so' if e['source'] == 'user' else 'from the report'}); with your change it gives {g}." for e, g in bad[:3]))
        diff = "\n".join(l for p in changed for l in difflib.unified_diff((self.files0.get(p) or "").splitlines(), (files1.get(p) or "").splitlines(), "a/" + p, "b/" + p, lineterm="", n=2))
        out, tok = self.structured(PR_PROMPT.format(report=t["report"], diff="\n".join(diff.splitlines()[:120]), n=PROBES), PR_SCHEMA); self.tokens += tok
        seen = {(_norm(e["setup"]), _norm(e["expr"])) for e in self.examples}; pairs = []
        for e in (out or {}).get("probes", []):
            if not isinstance(e, dict) or not e.get("call"): continue
            k = (_norm(e.get("setup", "")), _norm(e["call"]))
            if k not in seen and len(k[1]) <= 300: seen.add(k); pairs.append((str(e.get("setup", "")), str(e["call"])))
        pairs = pairs[:PROBES]; old = self._eval(self.snap, pairs) if pairs else []; new = self._eval(ws, pairs) if pairs else []
        rec["probes"] = [dict(setup=s, expr=c, before=o, after=n) for (s, c), o, n in zip(pairs, old, new)]
        told = [(_norm(e["expr"]), e["expected"]) for e in self.examples]                # a probe that restates an example is already settled
        settled = lambda c, n: any((x.endswith(_norm(c)) or _norm(c).endswith(x)) and _norm(n) == want for x, want in told)
        diffs = [(s, c, o, n) for (s, c), o, n in zip(pairs, old, new) if _usable(o) and _usable(n) and _norm(o) != _norm(n) and not settled(c, n)]
        diffs.sort(key=lambda d: not d[3].startswith("raises"))                   # a change that makes a call fail is asked about first
        if not self.examples and not diffs: return no("no evidence", "Nothing the runner can run shows that your change alters the behaviour the report complains about. Reproduce the report's example with run, then change the code so that it gives the expected value.")
        confirmed = 0
        for s, c, o, n in diffs:
            if confirmed >= CONFIRM: break
            if len(self.questions) >= QUESTIONS:
                self.unresolved = True; rec.update(accepted=False, reason="question budget")
                return False, "Not accepted: your change alters the result of calls the report does not mention, and no question is left to settle whether that is intended."
            q = dict(id=t["id"], round=len(self.questions) + 1, setup=s, expr=c, predictions=[o, n]); a = self.ask(q); v = a["value"]
            self.questions.append(dict(q, answer=v, agrees_with="after" if _norm(v) == _norm(n) else "before" if _norm(v) == _norm(o) else "neither"))
            if _norm(v) == _norm(n): confirmed += 1; continue
            self.examples.append(dict(setup=s, expr=c, expected=_norm(v), before=o, source="user"))
            return no("question", f"The user was asked about a call the report does not mention.\n{c}  should give {v}. Before your change it gave {o}; with your change it gives {n}.")
        rec.update(accepted=True, confirmed=confirmed, differences=len(diffs)); return True, ""

    def summary(self):
        return dict(examples=self.examples, questions=self.questions, checks=self.checks, probe_runs=self.probe_runs, tokens=self.tokens, unresolved=self.unresolved, log=self.log)
