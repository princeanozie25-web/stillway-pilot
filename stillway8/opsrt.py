"""The operations, as they run inside a workspace.  Stand-alone: imports nothing from this repository.

    python -I opsrt.py WORKSPACE dsl|py < script        prints one JSON object

Every arm of every experiment gets exactly these operations.  A script is either lines of the small language below
(one operation per line) or, in `py` mode, Python that calls the same operations as functions.  One operation alone is
the smallest script.  Each operation returns a short line of tokens and is counted in the ledger, inside scripts too.

proj:  CHECK c | DEPS m | SHOW m | PROBE m c | PATCH m slot variant | REVERT
tab:   DIFF | FACT k | COPY k | KEEP k | DROP k | ADD k g | SKIP k | RECALC g | ROWS | CHECK c0|c1
bank:  USE (run the procedure the memory bank offered for this job, if any)"""
import csv, importlib, io, json, os, re, sys, time

SLOT_LINES = None
ROLE_SLOTS = {"clean": ("norm", "dedupe"), "filter": ("thr", "cmp"), "agg": ("col", "func"), "order": ("by", "dir")}
FIELDS = ["count", "groups", "total", "first"]


def _frag():
    global SLOT_LINES
    if SLOT_LINES is None:
        F = {("norm", "none"): "    return k", ("norm", "strip"): "    return k.strip()", ("norm", "lower"): "    return k.lower()", ("norm", "both"): "    return k.strip().lower()",
             ("dedupe", "on"): "        if sig in seen: continue", ("dedupe", "off"): "        if sig is None: continue",
             ("cmp", "gt"): '    return [r for r in rows if r["val"] > THR]', ("cmp", "ge"): '    return [r for r in rows if r["val"] >= THR]',
             ("cmp", "lt"): '    return [r for r in rows if r["val"] < THR]', ("cmp", "le"): '    return [r for r in rows if r["val"] <= THR]',
             ("col", "val"): '    xs = [r["val"] for r in rows]', ("col", "qty"): '    xs = [r["qty"] for r in rows]',
             ("func", "sum"): "    return sum(xs)", ("func", "mean"): "    return sum(xs) // len(xs)", ("func", "max"): "    return max(xs)", ("func", "min"): "    return min(xs)", ("func", "count"): "    return len(xs)",
             ("by", "key"): '    rows = sorted(rows, key=lambda r: r["key"])', ("by", "val"): '    rows = sorted(rows, key=lambda r: (r["val"], r["key"]))',
             ("dir", "asc"): "    return rows", ("dir", "desc"): "    return rows[::-1]"}
        for i in range(1, 10): F[("thr", f"n{i}")] = f"THR = {i}"
        SLOT_LINES = F
    return SLOT_LINES


def num(v): return f"n{max(0, min(63, int(v)))}"
def ktok(k): return "k-" if k == "-" else "k" + k.strip() + ("_" if k != k.strip() else "")


class Ops:
    def __init__(self, ws):
        self.ws = ws; self.ledger = []; self.job = json.load(open(os.path.join(ws, "job.json"))); self.dom = self.job["dom"]

    # ---------------------------------------------------------- files
    def _p(self, name):
        if not re.fullmatch(r"[A-Za-z0-9_.]+", name): raise ValueError("bad name")
        return os.path.join(self.ws, name)
    def _read(self, name): return open(self._p(name), newline="").read()
    def _write(self, name, text):
        with open(self._p(name), "w", newline="") as f: f.write(text)
    def _table(self, name): return list(csv.DictReader(io.StringIO(self._read(name))))
    def _save(self, name, cols, rows): self._write(name, ",".join(cols) + "\n" + "".join(",".join(str(r[c]) for c in cols) + "\n" for r in rows))

    # ---------------------------------------------------------- proj
    def _run(self, mod, data):
        for k in [k for k in sys.modules if re.fullmatch(r"m\d", k)]: del sys.modules[k]
        importlib.invalidate_caches(); sys.dont_write_bytecode = True; sys.path.insert(0, self.ws)
        try: return importlib.import_module(mod).run(self._p(data))
        finally: sys.path.remove(self.ws)
    def _role(self, m): return re.match(r'"""(\w+) stage', self._read(m + ".py")).group(1)

    def DEPS(self, m): return " ".join(sorted(re.findall(r"^import (m\d) as", self._read(m + ".py"), re.M))) or "none"
    def SHOW(self, m):
        role = self._role(m); inv = {v: k for k, v in _frag().items() if k[0] in ROLE_SLOTS.get(role, ())}; out = ["role", role]
        for line in self._read(m + ".py").splitlines():
            if line in inv: out += list(inv[line])
        return " ".join(out)
    def PROBE(self, m, c):
        v = self._run(m, json.loads(self._read("checks.json"))[c]["data"]); rows = lambda rs: " ".join(f"r {ktok(r['key'])} {num(r['val'])} {num(r['qty'])}" for r in rs) or "none"
        if isinstance(v, list): return rows(v)
        if isinstance(v, dict): return " ".join(f"{f} {ktok(v[f]) if f == 'first' else num(v[f])}" for f in FIELDS)
        return "v " + num(v)
    def _check_proj(self, c):
        ck = json.loads(self._read("checks.json"))[c]; got = self._run(self.job["entry"], ck["data"])
        for f in FIELDS:
            if f in ck["expect"] and got[f] != ck["expect"][f]:
                t = ktok if f == "first" else num; return f"FAIL {f} exp {t(ck['expect'][f])} got {t(got[f])}"
        return "PASS"
    def PATCH(self, m, slot, variant):
        F = _frag(); text = self._read(m + ".py"); lines = text.split("\n")
        if (slot, variant) not in F or slot not in ROLE_SLOTS.get(self._role(m), ()): return "BAD"
        hit = [i for i, l in enumerate(lines) if any(l == v for (s, _), v in F.items() if s == slot)]
        if len(hit) != 1: return "BAD"
        self._write(".undo", json.dumps([m, text])); lines[hit[0]] = F[slot, variant]; self._write(m + ".py", "\n".join(lines)); return "OK"
    def REVERT(self):
        if not os.path.exists(self._p(".undo")): return "BAD"
        m, text = json.loads(self._read(".undo")); self._write(m + ".py", text); os.remove(self._p(".undo")); return "OK"

    # ---------------------------------------------------------- tab
    def _diffs(self):
        led = {r["key"]: r for r in self._table("ledger.csv")}; st = {r["key"]: int(r["amt"]) for r in self._table("statement.csv")}; ign = {r["key"] for r in self._table("ignored.csv")}; out = []
        for k in sorted(set(led) | set(st)):
            if k in ign or (k in led and led[k]["st"] == "kept"): continue
            if k in led and k in st and int(led[k]["amt"]) != st[k]: out.append((k, led[k]["grp"], "amt", num(led[k]["amt"]), num(st[k])))
            elif k in led and k not in st: out.append((k, led[k]["grp"], "onlyL", num(led[k]["amt"])))
            elif k in st and k not in led: out.append((k, "onlyS", num(st[k])))
        return out
    def DIFF(self): return " ".join("d " + " ".join(d) for d in self._diffs()[:3]) or "none"
    def ROWS(self): return " ".join(f"r {r['key']} {r['grp']} {num(r['amt'])} {r['st']}" for r in self._table("ledger.csv")) or "none"
    def FACT(self, k): return {r["key"]: r["note"] for r in self._table("notes.csv")}.get(k, "nonote")
    def _edit(self, k, f):
        rows = self._table("ledger.csv"); hit = [r for r in rows if r["key"] == k]
        if not hit: return "BAD"
        rows = f(rows, hit[0]); self._save("ledger.csv", ["key", "grp", "amt", "st"], rows); return "OK"
    def COPY(self, k):
        st = {r["key"]: r["amt"] for r in self._table("statement.csv")}
        if k not in st: return "BAD"
        def f(rows, r): r["amt"] = st[k]; return rows
        return self._edit(k, f)
    def KEEP(self, k):
        def f(rows, r): r["st"] = "kept"; return rows
        return self._edit(k, f)
    def DROP(self, k): return self._edit(k, lambda rows, r: [x for x in rows if x is not r])
    def ADD(self, k, g):
        st = {r["key"]: r["amt"] for r in self._table("statement.csv")}; rows = self._table("ledger.csv")
        if k not in st or any(r["key"] == k for r in rows) or not re.fullmatch(r"g[0-2]", g): return "BAD"
        rows.append({"key": k, "grp": g, "amt": st[k], "st": "open"}); self._save("ledger.csv", ["key", "grp", "amt", "st"], sorted(rows, key=lambda r: r["key"])); return "OK"
    def SKIP(self, k):
        st = {r["key"] for r in self._table("statement.csv")}; ign = self._table("ignored.csv")
        if k not in st: return "BAD"
        self._save("ignored.csv", ["key"], ign + [{"key": k}]); return "OK"
    def _sum(self, g): return sum(int(r["amt"]) for r in self._table("ledger.csv") if r["grp"] == g)
    def RECALC(self, g):
        rows = self._table("summary.csv"); hit = [r for r in rows if r["grp"] == g]
        if not hit: return "BAD"
        hit[0]["total"] = self._sum(g); self._save("summary.csv", ["grp", "total"], rows); return "OK " + num(hit[0]["total"])
    def _check_tab(self, c):
        if c == "c0":
            for r in self._table("summary.csv"):
                if int(r["total"]) != self._sum(r["grp"]): return f"FAIL {r['grp']} exp {num(self._sum(r['grp']))} got {num(r['total'])}"
            return "PASS"
        d = self._diffs(); return f"FAIL {d[0][0]}" if d else "PASS"

    # ---------------------------------------------------------- shared
    def CHECK(self, c):
        if not re.fullmatch(r"c[01]", c): return "BAD"
        return self._check_proj(c) if self.dom == "proj" else self._check_tab(c)
    def USE(self):
        """Run the stored procedure the bank attached to this workspace: a short Python body over these operations."""
        p = self._p(".procedure.py")
        if not os.path.exists(p): return "BAD"
        env = api(self); env["result"] = "FAIL"; exec(compile(open(p).read(), "procedure", "exec"), env); return str(env["result"])

    PROJ = ("CHECK", "DEPS", "SHOW", "PROBE", "PATCH", "REVERT", "USE"); TAB = ("CHECK", "DIFF", "ROWS", "FACT", "COPY", "KEEP", "DROP", "ADD", "SKIP", "RECALC", "USE")
    def call(self, op, *args):
        """One counted operation.  Anything illegal or crashing is an observation, never an exception."""
        t0 = time.time()
        try:
            if op not in (self.PROJ if self.dom == "proj" else self.TAB): out = "BAD"
            else: out = getattr(self, op)(*args)
        except Exception as e: out = "ERR"; self.ledger.append({"op": op, "args": list(args), "obs": out, "s": round(time.time() - t0, 4), "error": f"{type(e).__name__}: {str(e)[:120]}"}); return out
        self.ledger.append({"op": op, "args": list(args), "obs": out, "s": round(time.time() - t0, 4)}); return out


def api(o):
    """The same operations as Python functions, for scripts in `py` mode and stored procedures."""
    return {n.lower(): (lambda *a, _n=n: o.call(_n, *[str(x) for x in a])) for n in set(Ops.PROJ + Ops.TAB)}


def execute(ws, mode, text):
    """Run one script.  Returns {'obs': [...], 'ledger': [...], 'stdout': str, 'error': str|None}."""
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
