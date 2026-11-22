"""The two task worlds of v0.8 and their generators.

proj: a small Python project, a chain of modules (load -> clean -> filter -> agg / order -> report) with one ordinary
      data-processing bug in one line, or none.  The repair is a one-line change chosen from a fixed table of lines.
tab:  a ledger, a bank statement, notes and a dependent summary.  The job is to reconcile the records according to the
      notes and bring the summary up to date, or to leave a valid book alone.

A job has a public half (the files and the goal: all a runner may see) and a hidden half (the truth: only the grader).
`stages` / `tab_truth` are the reference semantics; build_data checks every job against the real files by execution."""
import hashlib, json, random
from stillway8.opsrt import _frag

# ------------------------------------------------------------------ proj
SLOTS = {"clean": {"norm": ["none", "strip", "lower", "both"], "dedupe": ["off", "on"]},
         "filter": {"cmp": ["gt", "ge", "lt", "le"], "thr": [f"n{i}" for i in range(1, 10)]},
         "agg": {"col": ["val", "qty"], "func": ["sum", "mean", "max", "min", "count"]},
         "order": {"by": ["key", "val"], "dir": ["asc", "desc"]}}
SLOT_ROLE = {s: r for r, d in SLOTS.items() for s in d}
FRAG = _frag()                                                 # (slot, variant) -> the source line; one table, kept in opsrt
LINE = {v: k for k, v in FRAG.items()}
FIELDS = ["count", "groups", "total", "first"]
BASES = "abcdef"


def source(role, cfg, up):
    """The real text of one module.  `up` maps the names it imports."""
    L = [f'"""{role} stage."""']
    if role == "load":
        L += ["import csv", "", "", "def run(path):", "    rows = []", "    with open(path, newline=\"\") as f:", "        for r in csv.DictReader(f):",
              '            rows.append({"key": r["key"], "val": int(r["val"]), "qty": int(r["qty"])})', "    return rows"]
    elif role == "clean":
        L += [f"import {up['load']} as upstream", "", "", "def norm(k):", FRAG["norm", cfg["norm"]], "", "", "def run(path):", "    seen, out = set(), []", "    for r in upstream.run(path):",
              '        r = dict(r, key=norm(r["key"]))', '        sig = (r["key"], r["val"], r["qty"])', FRAG["dedupe", cfg["dedupe"]], "        seen.add(sig)", "        out.append(r)", "    return out"]
    elif role == "filter":
        L += [f"import {up['clean']} as upstream", "", FRAG["thr", cfg["thr"]], "", "", "def run(path):", "    rows = upstream.run(path)", FRAG["cmp", cfg["cmp"]]]
    elif role == "agg":
        L += [f"import {up['filter']} as upstream", "", "", "def run(path):", "    rows = upstream.run(path)", FRAG["col", cfg["col"]], "    if not xs:", "        return 0", FRAG["func", cfg["func"]]]
    elif role == "order":
        L += [f"import {up['filter']} as upstream", "", "", "def run(path):", "    rows = upstream.run(path)", FRAG["by", cfg["by"]], FRAG["dir", cfg["dir"]]]
    elif role == "report":
        imp = sorted((up["filter"], up["agg"], up["order"])); names = {up["filter"]: "rows_mod", up["agg"]: "agg_mod", up["order"]: "order_mod"}
        L += [f"import {m} as {names[m]}" for m in imp] + ["", "", "def run(path):", "    rows = rows_mod.run(path)", "    ordered = order_mod.run(path)",
              '    return {"count": len(rows), "groups": len({r["key"] for r in rows}), "total": agg_mod.run(path),', '            "first": ordered[0]["key"] if ordered else "-"}']
    return "\n".join(L) + "\n"


NORM = {"none": lambda k: k, "strip": str.strip, "lower": str.lower, "both": lambda k: k.strip().lower()}
CMP = {"gt": lambda a, b: a > b, "ge": lambda a, b: a >= b, "lt": lambda a, b: a < b, "le": lambda a, b: a <= b}
FUNC = {"sum": sum, "mean": lambda x: sum(x) // len(x), "max": max, "min": min, "count": len}


def stages(cfg, rows):
    """Reference semantics: the output of every stage for one input."""
    seen, c = set(), []
    for r in rows:
        r = dict(r, key=NORM[cfg["norm"]](r["key"])); sig = (r["key"], r["val"], r["qty"])
        if cfg["dedupe"] == "on" and sig in seen: continue
        seen.add(sig); c.append(r)
    thr = int(cfg["thr"][1:]); f = [r for r in c if CMP[cfg["cmp"]](r["val"], thr)]; xs = [r[cfg["col"]] for r in f]; total = FUNC[cfg["func"]](xs) if xs else 0
    o = sorted(f, key=(lambda r: r["key"]) if cfg["by"] == "key" else (lambda r: (r["val"], r["key"])))
    if cfg["dir"] == "desc": o = o[::-1]
    return {"load": rows, "clean": c, "filter": f, "agg": total, "order": o,
            "report": {"count": len(f), "groups": len({r["key"] for r in f}), "total": total, "first": o[0]["key"] if o else "-"}}


def csv_text(rows): return "key,val,qty\n" + "".join(f"{r['key']},{r['val']},{r['qty']}\n" for r in rows)


def rand_cfg(rng): return {"norm": rng.choice(SLOTS["clean"]["norm"]), "dedupe": rng.choice(["off", "on"]), "cmp": rng.choice(SLOTS["filter"]["cmp"]), "thr": f"n{rng.randint(2, 8)}",
                           "col": rng.choice(["val", "qty"]), "func": rng.choice(SLOTS["agg"]["func"]), "by": rng.choice(["key", "val"]), "dir": rng.choice(["asc", "desc"])}


def rand_rows(rng, cfg, bases):
    n = rng.randint(3, 5); thr = int(cfg["thr"][1:]); rows = []
    def key():
        k = rng.choice(bases)
        if rng.random() < 0.3: k = k.upper()
        return k + (" " if rng.random() < 0.3 else "")
    for _ in range(n):
        v = thr if rng.random() < 0.3 else rng.randint(1, 9); rows.append({"key": key(), "val": v, "qty": rng.randint(1, 9)})
    if rng.random() < 0.45:                                    # a repeated record, sometimes written differently
        i = rng.randrange(len(rows)); d = dict(rows[i]); b = rows[i]["key"].strip()
        d["key"] = rng.choice([rows[i]["key"], rows[i]["key"], b + " ", b.upper()]); rows[rng.choice([x for x in range(len(rows)) if x != i])] = d
    rng.shuffle(rows); return rows


def patches(cfg):
    """Every one-line change to the modules in use: (slot, variant)."""
    out = []
    for role, d in SLOTS.items():
        for s, vs in d.items(): out += [(s, v) for v in vs if v != cfg[s]]
    return out


def proj_source(rng):
    """A source project: the intended behaviour, the key alphabet and which stand-in modules lie around unused."""
    cfg = rand_cfg(rng); bases = rng.sample(BASES, rng.randint(3, 4)); decoys = rng.sample(["clean", "filter", "agg", "order"], rng.choice([0, 1, 1, 2]))
    return {"cfg": cfg, "bases": bases, "decoys": decoys}


def proj_job(rng, src, kind, slot=None, wrong=None, tries=400, also=()):
    """One job from a source project.  kind: valid | bug | unans | trap.  Returns (public, hidden) or None if no data makes
    the job well posed (exactly one one-line change makes the failing visible checks pass).  A trap is a fault for which
    a second one-line change, in one of the slots `also`, passes every visible check too and is wrong."""
    true = src["cfg"]; cur = dict(true)
    if kind in ("bug", "trap"): cur[slot] = wrong
    for _ in range(tries):
        data = [rand_rows(rng, true, src["bases"]) for _ in range(2)]; asserted = [sorted(rng.sample(FIELDS, rng.randint(1, 4)), key=FIELDS.index) for _ in range(2)]
        want = [stages(true, d)["report"] for d in data]
        if any(w["count"] == 0 for w in want): continue
        expect = [{f: w[f] for f in a} for w, a in zip(want, asserted)]
        if kind == "unans":                                    # a stale expectation: no one-line change produces it
            i = rng.randrange(2); f = rng.choice([x for x in asserted[i] if x != "first"] or ["first"])
            if f == "first": continue
            expect[i][f] = max(0, expect[i][f] + rng.choice([-2, -1, 1, 2, 3]))
        got = [stages(cur, d)["report"] for d in data]; failing = [i for i in range(2) if any(got[i][f] != expect[i][f] for f in expect[i])]
        passes = lambda c, idx: all(stages(c, data[i])["report"][f] == expect[i][f] for i in idx for f in expect[i])
        fixes = [(s, v) for s, v in patches(cur) if passes(dict(cur, **{s: v}), failing)] if failing else []
        if kind == "valid" and failing: continue
        if kind == "bug" and (not failing or fixes != [(slot, true[slot])]): continue
        if kind == "unans" and (not failing or fixes): continue
        if kind == "trap":
            lure = [(s, v) for s, v in fixes if s in also and passes(dict(cur, **{s: v}), [0, 1])]
            if not failing or (slot, true[slot]) not in fixes or not lure: continue
        if max(max(r["val"], r["qty"]) for d in data for r in d) > 9: continue
        break
    else: return None
    ids = [f"m{i}" for i in range(8)]; rng.shuffle(ids); roles = ["load", "clean", "filter", "agg", "order", "report"]; name = dict(zip(roles, ids)); files = {}
    for r in roles: files[name[r] + ".py"] = source(r, cur, name)
    for j, r in enumerate(src["decoys"]):                      # an unused stand-in for one stage, with one setting different
        s = rng.choice(list(SLOTS[r])); alt = dict(cur); alt[s] = rng.choice([v for v in SLOTS[r][s] if v != cur[s]]); files[ids[6 + j] + ".py"] = source(r, alt, name)
    checks = {}
    for i in range(2): files[f"data_c{i}.csv"] = csv_text(data[i]); checks[f"c{i}"] = {"data": f"data_c{i}.csv", "expect": expect[i]}
    goal = f"c{failing[0]}" if failing else f"c{rng.randrange(2)}"
    files["checks.json"] = json.dumps(checks, indent=1) + "\n"; files["job.json"] = json.dumps({"dom": "proj", "entry": name["report"], "goal": goal}) + "\n"
    hid_data = [rand_rows(rng, true, src["bases"]) for _ in range(4)]
    hidden = {"kind": kind, "slot": slot, "wrong": wrong, "right": true[slot] if slot else None, "true": true, "names": name,
              "tests": [{"csv": csv_text(d), "expect": stages(true, d)["report"]} for d in data + hid_data],
              "role": SLOT_ROLE.get(slot), "reported": [next(f for f in expect[i] if got[i][f] != expect[i][f]) for i in failing]}
    if kind == "trap": hidden["lure"] = [list(x) for x in lure]
    public = {"dom": "proj", "goal": goal, "entry": name["report"], "mods": sorted(n[:-3] for n in files if n.endswith(".py")), "files": files}
    return public, hidden


# ------------------------------------------------------------------ tab
RULES = {("amt", "stmt_newer"): "COPY", ("amt", "ledger_newer"): "KEEP", ("amt", "void"): "DROP", ("onlyL", "pending"): "KEEP", ("onlyL", "void"): "DROP",
         ("onlyS", "grp"): "ADD", ("onlyS", "dupstmt"): "SKIP", ("onlyS", "pending"): "SKIP"}
GROUPS = ["g0", "g1", "g2"]


def tab_source(rng):
    """A source book: its accounts, their groups and usual amounts."""
    keys = sorted(rng.sample([f"k{i}" for i in range(8)], rng.randint(4, 6)))
    return {"rows": [{"key": k, "grp": rng.choice(GROUPS), "amt": rng.randint(1, 9)} for k in keys]}


def tab_job(rng, src, items, stale=False):
    """items: list of (kind, note) differences to plant; note 'nonote' makes the job unanswerable."""
    led = [dict(r, amt=rng.randint(1, 9)) for r in src["rows"]]; rng.shuffle(led); led = sorted(led[:rng.randint(3, min(5, len(led)))], key=lambda r: r["key"])
    st = {r["key"]: r["amt"] for r in led}; notes = {}; truth = {r["key"]: dict(r) for r in led}; free = [k for k in (f"k{i}" for i in range(8)) if k not in st]; used = set()
    for kind, note in items:
        if kind in ("amt", "onlyL"):
            cand = [r["key"] for r in led if r["key"] not in used]
            if not cand: return None
            k = rng.choice(cand); used.add(k); act = RULES.get((kind, note))
            if kind == "amt": st[k] = rng.choice([v for v in range(1, 10) if v != st[k]])
            else: del st[k]
            if act == "COPY": truth[k]["amt"] = st[k]
            if act == "DROP": del truth[k]
        else:
            if not free: return None
            k = free.pop(rng.randrange(len(free))); st[k] = rng.randint(1, 9); g = rng.choice(GROUPS)
            if note == "grp": truth[k] = {"key": k, "grp": g, "amt": st[k]}; note = f"grp {g}"
        notes[k] = note
    sums = lambda rows: {g: sum(r["amt"] for r in rows if r["grp"] == g) for g in GROUPS}
    summ = sums(led); stale_g = None
    if stale: stale_g = rng.choice(GROUPS); summ[stale_g] = max(0, summ[stale_g] + rng.choice([-3, -2, -1, 1, 2, 3])); stale_g = stale_g if summ[stale_g] != sums(led)[stale_g] else None
    files = {"ledger.csv": "key,grp,amt,st\n" + "".join(f"{r['key']},{r['grp']},{r['amt']},open\n" for r in led),
             "statement.csv": "key,amt\n" + "".join(f"{k},{st[k]}\n" for k in sorted(st)), "notes.csv": "key,note\n" + "".join(f"{k},{notes[k]}\n" for k in sorted(notes)),
             "summary.csv": "grp,total\n" + "".join(f"{g},{summ[g]}\n" for g in GROUPS), "ignored.csv": "key\n", "job.json": json.dumps({"dom": "tab", "goal": "reconcile"}) + "\n"}
    unans = any(n == "nonote" for _, n in items); tl = sorted(truth.values(), key=lambda r: r["key"])
    if unans: tl = led
    hidden = {"kind": "unans" if unans else "valid" if not items and not stale_g else "stale" if not items else "diff", "items": [list(i) for i in items], "stale": stale_g,
              "ledger": {r["key"]: [r["grp"], r["amt"]] for r in tl}, "summary": sums(tl) if not unans else summ}
    return {"dom": "tab", "goal": "reconcile", "files": files}, hidden


def job_id(public): return hashlib.sha256(json.dumps(public["files"], sort_keys=True).encode()).hexdigest()[:12]
