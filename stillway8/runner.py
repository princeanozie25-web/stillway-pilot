"""The local script runner: disposable workspaces, the sandbox, the ledger.  No grader is imported here.

A Session copies a job's public files into a fresh temporary directory.  `run` executes one script there in a separate
sandboxed process (no network, no writes outside the workspace, 5 s of CPU, 1 MB files, a wall-clock limit) and returns
the observations.  `fast=True` runs the same operations in-process: used only for the teacher's own trusted scripts
when building data, never for anything a model wrote."""
import json, os, shutil, subprocess, sys, tempfile, time
from stillway8 import opsrt

PY = sys.executable; OPSRT = os.path.abspath(opsrt.__file__)
PROFILE = '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath "%s") (literal "/dev/null") (literal "/dev/dtracehelper"))'


class Session:
    def __init__(self, public, fast=False, procedure=None):
        self.dir = os.path.realpath(tempfile.mkdtemp(prefix="sw8_")); self.fast = fast; self.log = []; self.initial = dict(public["files"])
        for n, t in public["files"].items():
            with open(os.path.join(self.dir, n), "w", newline="") as f: f.write(t)
        if procedure:
            with open(os.path.join(self.dir, ".procedure.py"), "w") as f: f.write(procedure)

    def set_procedure(self, text):
        with open(os.path.join(self.dir, ".procedure.py"), "w") as f: f.write(text)

    def run(self, text, mode="dsl", timeout=10.0):
        """One script.  Returns {'obs', 'ledger', 'stdout', 'error', 's'}; a crash or a timeout is an observation."""
        t0 = time.time()
        if self.fast: r = opsrt.execute(self.dir, mode, text)
        else:
            env = {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}
            try:
                p = subprocess.run(["/usr/bin/sandbox-exec", "-p", PROFILE % self.dir, PY, "-I", OPSRT, self.dir, mode], input=text, cwd=self.dir, env=env, capture_output=True, text=True, timeout=timeout)
                line = [l for l in p.stdout.splitlines() if l.startswith("@@")]
                r = json.loads(line[-1][2:]) if line else {"obs": ["ERR"], "ledger": [], "stdout": "", "error": "CRASH " + (p.stderr.strip().splitlines() or ["no output"])[-1][:160]}
            except subprocess.TimeoutExpired: r = {"obs": ["ERR"], "ledger": [], "stdout": "", "error": f"TIMEOUT after {timeout} s"}
        r["s"] = round(time.time() - t0, 4); self.log.append({"mode": mode, "script": text, **r}); return r

    def files(self):
        out = {}
        for n in sorted(os.listdir(self.dir)):
            if not n.startswith(".") and os.path.isfile(os.path.join(self.dir, n)): out[n] = open(os.path.join(self.dir, n), newline="").read()
        return out

    def diff(self):
        """What changed since the start: {file: [old line or None, new line or None] pairs}."""
        import difflib
        now = self.files(); out = {}
        for n in sorted(set(now) | set(self.initial)):
            a, b = self.initial.get(n, ""), now.get(n, "")
            if a != b: out[n] = [l for l in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
        return out

    def ops(self): return sum(len(e["ledger"]) for e in self.log)
    def close(self): shutil.rmtree(self.dir, ignore_errors=True)
