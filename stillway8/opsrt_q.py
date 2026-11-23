"""The operations of opsrt.py plus four, for a guard that asks one focused question.  Added after v0.8 (follow-up Q5).

    python -I opsrt_q.py WORKSPACE dsl|py < script        prints one JSON object

opsrt.py is not changed, so every earlier lock still matches.  The new proj operations:

  TRIAL m slot variant rows   a disposable probe: copy the project's modules into a scratch directory, apply the one-line
                              change there, run the entry module on `rows` (JSON, 3 to 5 legal rows [key, val, qty] the
                              solver made up), delete the copy, return the report as JSON.  The workspace's own files
                              are never touched.
  QUESTION json               put one question to the owner of the job and stop.  Returns WAIT.  The JSON holds the
                              question and everything needed to resume; the runner persists it.
  ANSWER json                 record the answer the runner was handed, on resuming.  Returns OK.
  NOTE json                   record why the procedure fell back to a bare request.  Returns OK.

No operation reads a hidden file: an answer reaches the runner from whoever holds the hidden half, between runs.
All four are counted in the ledger like every other operation."""
import importlib, io, json, os, re, shutil, sys, tempfile
try: from stillway8 import opsrt
except ImportError:                                            # run as a stand-alone script with -I: the sibling file
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import opsrt

KEYOK = lambda k: isinstance(k, str) and len(k.strip()) == 1 and k.strip().lower() in "abcdef" and k in (k.strip(), k.strip() + " ")
ROWSOK = lambda d: isinstance(d, list) and 3 <= len(d) <= 5 and all(isinstance(r, list) and len(r) == 3 and KEYOK(r[0]) and all(type(x) is int and 1 <= x <= 9 for x in r[1:]) for r in d)


class Ops(opsrt.Ops):
    def TRIAL(self, m, slot, variant, rows):
        d = json.loads(rows); F = opsrt._frag()
        if not ROWSOK(d) or (slot, variant) not in F or slot not in opsrt.ROLE_SLOTS.get(self._role(m), ()): return "BAD"
        tmp = tempfile.mkdtemp(prefix=".probe_", dir=self.ws)
        try:
            for n in os.listdir(self.ws):
                if re.fullmatch(r"m\d\.py", n): shutil.copy(os.path.join(self.ws, n), tmp)
            path = os.path.join(tmp, m + ".py"); lines = open(path, newline="").read().split("\n"); hit = [i for i, l in enumerate(lines) if any(l == v for (s, _), v in F.items() if s == slot)]
            if len(hit) != 1: return "BAD"
            lines[hit[0]] = F[slot, variant]
            with open(path, "w", newline="") as f: f.write("\n".join(lines))
            with open(os.path.join(tmp, "made_up.csv"), "w", newline="") as f: f.write("key,val,qty\n" + "".join(f"{k},{v},{q}\n" for k, v, q in d))
            purge = lambda: [sys.modules.pop(k) for k in [k for k in sys.modules if re.fullmatch(r"m\d", k)]]
            purge(); importlib.invalidate_caches(); sys.dont_write_bytecode = True; sys.path.insert(0, tmp)
            try: return json.dumps(importlib.import_module(self.job["entry"]).run(os.path.join(tmp, "made_up.csv")), sort_keys=True, separators=(",", ":"))
            finally: sys.path.remove(tmp); purge()
        finally: shutil.rmtree(tmp, ignore_errors=True)
    def QUESTION(self, q): return "WAIT" if isinstance(json.loads(q), dict) else "BAD"
    def ANSWER(self, a): return "OK" if isinstance(json.loads(a), dict) else "BAD"
    def NOTE(self, n): return "OK" if isinstance(json.loads(n), dict) else "BAD"
    def USE(self):
        p = self._p(".procedure.py")
        if not os.path.exists(p): return "BAD"
        env = api(self); env["result"] = "FAIL"; exec(compile(open(p).read(), "procedure", "exec"), env); return str(env["result"])
    PROJ = opsrt.Ops.PROJ + ("TRIAL", "QUESTION", "ANSWER", "NOTE")


def api(o): return {n.lower(): (lambda *a, _n=n: o.call(_n, *[str(x) for x in a])) for n in set(Ops.PROJ + Ops.TAB)}


def execute(ws, mode, text):
    o = Ops(ws); obs, err, out = [], None, ""
    if mode == "dsl":
        for line in [l.split() for l in text.strip().split("\n") if l.strip()]: obs.append(o.call(line[0], *line[1:]))
    else:
        buf = io.StringIO(); old = sys.stdout; sys.stdout = buf
        try: exec(compile(text, "script", "exec"), dict(api(o), __name__="script"))
        except BaseException as e: err = f"{type(e).__name__}: {str(e)[:160]}"
        finally: sys.stdout = old
        out = buf.getvalue()[-1500:]; obs = [l["obs"] for l in o.ledger]
    return {"obs": obs, "ledger": o.ledger, "stdout": out, "error": err}


if __name__ == "__main__":
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5)); resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20)); resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    print("@@" + json.dumps(execute(sys.argv[1], sys.argv[2], sys.stdin.read())))
