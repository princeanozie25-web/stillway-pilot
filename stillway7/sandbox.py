"""Repositories, savepoints and execution.  A repository is a dict {relative path: text}.  Every execution starts from a
fresh copy of the savepoint in a temporary directory ("alternate executions from the same savepoint")."""
import ast, difflib, hashlib, json, os, subprocess, sys, tempfile, textwrap, time

PY = sys.executable
RUNNER = '''
import importlib.util, json, signal, sys
def _late(signum, frame): raise TimeoutError("test took longer than 2 s")
signal.signal(signal.SIGALRM, _late)
spec = importlib.util.spec_from_file_location("t", sys.argv[1]); m = importlib.util.module_from_spec(spec); out = {}
try: spec.loader.exec_module(m)
except Exception as e: print(json.dumps({"__import__": "ERROR " + type(e).__name__ + ": " + str(e)[:200]})); sys.exit(1)
for name in sorted(n for n in dir(m) if n.startswith("test_")):
    signal.setitimer(signal.ITIMER_REAL, 2.0)
    try: getattr(m, name)(); out[name] = "PASS"
    except BaseException as e: out[name] = "FAIL " + type(e).__name__ + ": " + str(e)[:160]
    finally: signal.setitimer(signal.ITIMER_REAL, 0)
print("\\n@@RESULT@@" + json.dumps(out))
'''

# Everything a student or a patch runs is confined: no network, no writes outside its own temporary directory.
PROFILE = '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath "%s") (literal "/dev/null") (literal "/dev/dtracehelper"))'


def code_hash(repo):
    h = hashlib.sha256()
    for p in sorted(repo): h.update(p.encode()); h.update(b"\0"); h.update(repo[p].encode()); h.update(b"\0")
    return h.hexdigest()


def materialise(repo, root):
    for p, text in repo.items():
        f = os.path.join(root, p); os.makedirs(os.path.dirname(f), exist_ok=True); open(f, "w").write(text)


def _run(cmd, cwd, timeout):
    t0 = time.time(); env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": cwd, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}
    try:
        r = subprocess.run(["/usr/bin/sandbox-exec", "-p", PROFILE % os.path.realpath(cwd)] + cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout); out, code = r.stdout + (("\n" + r.stderr) if r.stderr.strip() else ""), r.returncode
    except subprocess.TimeoutExpired: out, code = f"TIMEOUT after {timeout} s", 124
    return out, code, round(time.time() - t0, 3)


def run_script(repo, script, timeout=5.0, limit=400):
    """The student's tool: run a Python script in a fresh copy of the savepoint.  Returns (output text, seconds)."""
    with tempfile.TemporaryDirectory() as d:
        materialise(repo, d); open(os.path.join(d, "_probe.py"), "w").write(script); out, code, secs = _run([PY, "-I", "-c", "import sys; sys.path.insert(0, '.'); exec(open('_probe.py').read())"], d, timeout)
    out = out.strip()
    if code not in (0, 124):                                    # keep the last line of a traceback, which names the error
        lines = [l for l in out.splitlines() if l.strip()]; head = "\n".join(l for l in lines if not l.startswith(("Traceback", "  "))) or (lines[-1] if lines else "error")
        out = head
    return (out[:limit] + (" ...[cut]" if len(out) > limit else "")) or "(no output)", secs


def run_tests(repo, test_text, timeout=10.0):
    """Run a test file (functions named test_*) against a repository.  Returns ({test: 'PASS' | 'FAIL ...'}, seconds)."""
    with tempfile.TemporaryDirectory() as d:
        materialise(repo, d); open(os.path.join(d, "_tests.py"), "w").write(test_text); open(os.path.join(d, "_runner.py"), "w").write(RUNNER)
        out, code, secs = _run([PY, "-I", "-c", "import sys; sys.path.insert(0, '.'); sys.argv = ['_runner.py', '_tests.py']; exec(open('_runner.py').read())"], d, timeout)
    if "@@RESULT@@" in out: return json.loads(out.split("@@RESULT@@")[-1].strip().splitlines()[0]), secs
    names = [n.name for n in ast.walk(ast.parse(test_text)) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    return {n: "FAIL " + (out.strip().splitlines()[-1][:160] if out.strip() else "no result") for n in names}, secs


def find_def(text, name):
    """(first line, last line, indent) of the first function or method called `name`; lines are 1-based, inclusive."""
    try: tree = ast.parse(text)
    except SyntaxError: return None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            first = min([n.lineno] + [d.lineno for d in n.decorator_list]); return first, n.end_lineno, n.col_offset
    return None


def apply_patch(repo, code, path=None):
    """Replace one function or method (matched by name) with `code`.  Returns (new repo, info) or (None, reason)."""
    code = textwrap.dedent(code).strip("\n")
    try: tree = ast.parse(code)
    except SyntaxError as e: return None, f"patch does not parse: {e.msg}"
    defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if not defs:
        cls = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        if cls: return None, "patch must be one function or method, not a class"
        return None, "patch has no function"
    order = ([path] if path in repo else []) + [p for p in sorted(repo) if p != path and p.endswith(".py") and not p.startswith("tests/")]
    lines_code = code.splitlines()
    for d in defs:                                                   # the first function of the patch that exists in the repository
        seg = lines_code[min([d.lineno] + [x.lineno for x in d.decorator_list]) - 1: d.end_lineno]
        for p in order:
            loc = find_def(repo[p], d.name)
            if loc:
                a, b, ind = loc; old = repo[p].splitlines(); new = old[:a - 1] + [(" " * ind + l if l.strip() else l) for l in seg] + old[b:]
                text = "\n".join(new) + "\n"; out = dict(repo); out[p] = text
                diff = [l for l in difflib.unified_diff(old, new, lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
                return out, {"file": p, "function": d.name, "changed_lines": len(diff), "diff": "\n".join(diff)}
    return None, "no function with that name in the repository"
