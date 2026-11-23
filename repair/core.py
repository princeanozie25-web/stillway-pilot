"""Shared pieces of the repository repair harness: pinned repositories, workspaces, the sandbox, running tests.

No grading logic and no model code here.  A workspace is a throwaway directory holding one repository snapshot.  Tests
run in a sandboxed process: no network, no writes outside the workspace, a CPU limit, a file-size limit and a wall-clock
limit.  Results come from pytest's own JUnit report, not from scraping its text."""
import hashlib, json, os, re, resource, shutil, signal, subprocess, tarfile, tempfile, time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PY = os.path.join(ROOT, ".venv-repair", "bin", "python")
VENDOR = os.path.join(HERE, "vendor")
PROFILE = '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath "%s") (literal "/dev/null") (literal "/dev/dtracehelper"))'
SKIP_DIRS = {"__pycache__", ".tmp", ".git", ".pytest_cache"}


def manifest():
    """Every pinned archive: the entries of all repair/vendor/MANIFEST*.json files, by repository name."""
    return {m["name"]: m for f in sorted(os.listdir(VENDOR)) if f.startswith("MANIFEST") and f.endswith(".json") for m in json.load(open(os.path.join(VENDOR, f)))}


def is_test(path):
    """Files the grader never takes from a solver: tests and their configuration."""
    parts = path.split("/"); base = parts[-1]
    return any(p in ("tests", "test") for p in parts[:-1]) or base.startswith("test_") or base.endswith("_test.py") or base == "conftest.py"


def base_files(repo):
    """{relative path: text} of the pinned archive, read straight from the tar; binary and oversized files are left out."""
    m = manifest()[repo]; path = os.path.join(VENDOR, m["file"]); data = open(path, "rb").read()
    assert hashlib.sha256(data).hexdigest() == m["sha256"], f"{m['file']} is not the pinned archive"
    out = {}
    with tarfile.open(path) as t:
        for ti in t:
            if not ti.isfile() or ti.size > 400_000: continue
            rel = ti.name.split("/", 1)[1] if "/" in ti.name else ti.name
            if any(p in SKIP_DIRS or p.endswith(".egg-info") for p in rel.split("/")): continue
            try: out[rel] = t.extractfile(ti).read().decode("utf-8")
            except UnicodeDecodeError: pass
    return out


def snapshot(task):
    """The files a solver starts from: the pinned archive with the task's overlay applied (None deletes a file)."""
    files = base_files(task["repo"])
    for p, text in task["overlay"].items():
        if text is None: files.pop(p, None)
        else: files[p] = text
    return files


def fhash(files): return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:16]


class Workspace:
    def __init__(self, files):
        self.dir = os.path.realpath(tempfile.mkdtemp(prefix="repair_"))
        for p, text in files.items(): self.write(p, text)

    def path(self, rel):
        full = os.path.realpath(os.path.join(self.dir, rel))
        if full != self.dir and not full.startswith(self.dir + os.sep): raise ValueError("path is outside the repository")
        return full

    def write(self, rel, text):
        full = self.path(rel); os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="") as f: f.write(text)

    def files(self):
        out = {}
        for d, dirs, names in os.walk(self.dir):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith(".probe"))
            for n in sorted(names):
                full = os.path.join(d, n)
                if os.path.islink(full) or os.path.getsize(full) > 400_000: continue
                try: out[os.path.relpath(full, self.dir)] = open(full, encoding="utf-8", newline="").read()
                except (UnicodeDecodeError, OSError): pass
        return out

    def close(self): shutil.rmtree(self.dir, ignore_errors=True)


def _limits():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60)); resource.setrlimit(resource.RLIMIT_FSIZE, (16 << 20, 16 << 20))


def run_tests(ws, pythonpath, targets, timeout=90.0, extra=()):
    """Run pytest on targets inside the sandbox.  Returns {'results': {test id: passed|failed|error|skipped},
    'files': {test id: (file, class or None, function)}, 'text': pytest's output, 'rc', 's', 'timeout'}."""
    d = ws.dir; tmp = os.path.join(d, ".tmp"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    env = dict(PATH="/usr/bin:/bin", HOME=tmp, TMPDIR=tmp, PYTHONPATH=os.pathsep.join(os.path.join(d, p) for p in pythonpath.split(os.pathsep)),
               PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0", LC_ALL="en_US.UTF-8", TZ="UTC", COLUMNS="100")
    cmd = ["/usr/bin/sandbox-exec", "-p", PROFILE % d, PY, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider", "-o", "addopts=", "-o", "junit_family=xunit1",
           "-o", "console_output_style=classic", "--junitxml", os.path.join(tmp, "junit.xml"), *extra, *targets]
    t = time.time(); p = subprocess.Popen(cmd, cwd=d, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", preexec_fn=_limits); timed_out = False
    try: text, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        text, _ = p.communicate()
    results, where = {}, {}
    try:
        for tc in ET.parse(os.path.join(tmp, "junit.xml")).iter("testcase"):
            cls, name, file = tc.get("classname", ""), tc.get("name", ""), tc.get("file")
            tid = f"{cls}::{name}"; kinds = {c.tag for c in tc}
            status = "error" if "error" in kinds else "failed" if "failure" in kinds else "skipped" if "skipped" in kinds else "passed"
            if results.get(tid) in ("failed", "error"): continue            # a failing sub-case keeps the test failed
            results[tid] = status
            if file:
                mod = file[:-3].replace("/", "."); tail = cls[len(mod) + 1:] if cls.startswith(mod + ".") else None
                where[tid] = (file, tail.split(".")[-1] if tail else None, name.split("[")[0])
    except (ET.ParseError, OSError): pass
    shutil.rmtree(tmp, ignore_errors=True)
    return dict(results=results, files=where, text=text[-20000:], rc=p.returncode, s=round(time.time() - t, 2), timeout=timed_out)


def brief(run, lines=40):
    """What a solver is shown after a test run: counts, then the first failure."""
    r = run["results"]; n = lambda k: sum(v == k for v in r.values())
    if run["timeout"]: return "TIMEOUT: the test run was stopped."
    head = f"{n('passed')} passed, {n('failed')} failed, {n('error')} errors, {n('skipped')} skipped"
    if not r: return "No test ran.\n" + "\n".join(run["text"].strip().splitlines()[-lines:])
    if n("failed") + n("error") == 0: return head
    bad = [t for t, v in r.items() if v in ("failed", "error")]; text = run["text"]
    m = re.search(r"^=+ (?:FAILURES|ERRORS) =+\n(.*?)(?=^_{3,} .* _{3,}\n(?!.*\A)|^=+ )", text, re.S | re.M)
    block = text[m.start(1):] if m else text; parts = re.split(r"^_{3,} .+ _{3,}\n", block, flags=re.M)
    first = (parts[1] if len(parts) > 1 else block).split("\n=====")[0].strip().splitlines()
    shown = first[:lines] + ([f"... ({len(first) - lines} more lines)"] if len(first) > lines else [])
    return head + "\nFailing: " + ", ".join(t.split(".")[-1] for t in bad[:8]) + (f" and {len(bad) - 8} more" if len(bad) > 8 else "") + "\nFirst failure:\n" + "\n".join(shown)


def run_py(ws, pythonpath, code, timeout=20.0, tail=8000):
    """Run a Python snippet inside the sandbox with the repository importable.  Returns (stdout+stderr, return code)."""
    d = ws.dir; tmp = os.path.join(d, ".tmp"); os.makedirs(tmp, exist_ok=True)
    env = dict(PATH="/usr/bin:/bin", HOME=tmp, TMPDIR=tmp, PYTHONPATH=os.pathsep.join(os.path.join(d, p) for p in pythonpath.split(os.pathsep)),
               PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0", LC_ALL="en_US.UTF-8", TZ="UTC")
    p = subprocess.Popen(["/usr/bin/sandbox-exec", "-p", PROFILE % d, PY, "-c", code], cwd=d, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", preexec_fn=_limits)
    try: text, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        text, _ = p.communicate(); text += "\nTIMEOUT"
    shutil.rmtree(tmp, ignore_errors=True); return text[-tail:], p.returncode


EVAL = """import ast, itertools, json, sys
out = []
for setup, expr in json.loads(sys.argv[1] if len(sys.argv) > 1 else %r):
    try:
        env = {}; exec(setup, env)
        try: code = compile(expr, "<call>", "eval")
        except SyntaxError:                                   # statements followed by an expression: run the statements, keep the value
            tree = ast.parse(expr)
            if not tree.body or not isinstance(tree.body[-1], ast.Expr): raise
            exec(compile(ast.Module(tree.body[:-1], []), "<call>", "exec"), env); code = compile(ast.Expression(tree.body[-1].value), "<call>", "eval")
        v = eval(code, env)
        if hasattr(v, "__next__"): v = list(itertools.islice(v, 50))          # an iterator is shown as the list of what it yields
        out.append(repr(v))
    except BaseException as e: out.append("raises " + type(e).__name__)
print("\\n@@EVAL@@" + json.dumps(out))
"""


def evaluate(ws, pythonpath, pairs, timeout=20.0):
    """repr of each expression (after its setup lines) in this workspace, or 'raises <Error>'.  pairs: [(setup, expr)].
    One sandboxed process for the batch; if that gives nothing (a hang, a crash), each pair gets a process of its own."""
    if not pairs: return []
    text, _ = run_py(ws, pythonpath, EVAL % json.dumps([list(p) for p in pairs]), timeout)
    if "@@EVAL@@" in text:
        try: return json.loads(text.rsplit("@@EVAL@@", 1)[1])
        except ValueError: pass
    if len(pairs) == 1: return ["no result (timeout or crash)"]
    return [evaluate(ws, pythonpath, [p], 6.0)[0] for p in pairs]


DOCEX = """import doctest, importlib, json, sys
out = {}
class R(doctest.DocTestRunner):
    def report_start(self, out_, test, example): pass
    def report_success(self, out_, test, example, got): out[f"{test.name}#{test.examples.index(example)}: {example.source.strip()[:120]}"] = "passed"
    def report_failure(self, out_, test, example, got): out[f"{test.name}#{test.examples.index(example)}: {example.source.strip()[:120]}"] = "failed: got " + got.strip()[:200]
    def report_unexpected_exception(self, out_, test, example, exc_info): out[f"{test.name}#{test.examples.index(example)}: {example.source.strip()[:120]}"] = "failed: raises " + exc_info[0].__name__
for name in json.loads(%r):
    try: mod = importlib.import_module(name)
    except BaseException as e: out[f"{name}: import"] = "failed: raises " + type(e).__name__; continue
    for t in doctest.DocTestFinder(exclude_empty=True).find(mod, name):
        try: R(verbose=False, optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE).run(t, out=lambda s: None)
        except BaseException as e: out[f"{t.name}: run"] = "failed: raises " + type(e).__name__
print("\\n@@DOC@@" + json.dumps(out))
"""


def doc_examples(ws, pythonpath, files):
    """Run the documented examples (doctests) of the given source files, one result per example.  {example id: 'passed' | 'failed: ...'}"""
    roots = pythonpath.split(os.pathsep); names = []
    for f in files:
        for r in roots:
            rel = os.path.relpath(f, r)
            if not rel.startswith(".."): names.append(rel[:-3].replace("/", ".").removesuffix(".__init__")); break
    if not names: return {}
    text, _ = run_py(ws, pythonpath, DOCEX % json.dumps(names), timeout=30.0, tail=2_000_000)
    try: return json.loads(text.rsplit("@@DOC@@", 1)[1]) if "@@DOC@@" in text else {}
    except ValueError: return {}
