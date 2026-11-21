"""Turn templates and skins into repositories, and check each one by execution."""
import hashlib, json, os, random
from string import Template
from . import sandbox as S
from .templates_train import T as TRAIN_T, MODEL, FEED, RATES
from .templates_dev import D as DEV_T
from .procedures import NAIVE

#          collection   item        class       number     category   category values
SKINS_TRAIN = [("orders", "order", "Order", "amount", "customer", ["acme", "birch", "corvo", "delta"]),
               ("readings", "reading", "Reading", "level", "sensor", ["north", "south", "east", "west"]),
               ("grades", "grade", "Grade", "score", "student", ["ana", "ben", "cho", "dev"]),
               ("shipments", "shipment", "Shipment", "weight", "route", ["r10", "r22", "r31", "r47"]),
               ("tickets", "ticket", "Ticket", "hours", "team", ["ops", "web", "data", "core"]),
               ("invoices", "invoice", "Invoice", "due", "client", ["hale", "ivory", "juno", "kite"]),
               ("trades", "trade", "Trade", "volume", "desk", ["fx", "bonds", "metals", "energy"]),
               ("visits", "visit", "Visit", "minutes", "page", ["home", "docs", "blog", "shop"]),
               ("parcels", "parcel", "Parcel", "grams", "depot", ["leeds", "york", "hull", "bath"]),
               ("samples", "sample", "Sample", "dose", "batch", ["b1", "b2", "b3", "b4"])]
SKINS_DEV = [("bookings", "booking", "Booking", "nights", "hotel", ["grand", "plaza", "harbour", "lodge"]),
             ("donations", "donation", "Donation", "pounds", "donor", ["mia", "noor", "omar", "pia"]),
             ("fixtures", "fixture", "Fixture", "goals", "club", ["rovers", "united", "city", "town"]),
             ("harvests", "harvest", "Harvest", "kilos", "field", ["upper", "lower", "river", "hill"])]

HELPERS = ['''

def describe_$I($I):
    """Return a one-line description of a $I."""
    return "%s: %s" % ($I.$K, $I.$V)
''', '''

def ${K}_names($C):
    """Return the distinct $K values, in first-seen order."""
    names = []
    for x in $C:
        if x.$K not in names:
            names.append(x.$K)
    return names
''', '''

def largest_$V($C):
    """Return the largest $V, or None when there are no $C."""
    values = [x.$V for x in $C]
    return max(values) if values else None
''', '''

def group_by_$K($C):
    """Return a dict from $K to the list of $C with that $K."""
    groups = {}
    for x in $C:
        groups.setdefault(x.$K, []).append(x)
    return groups
''']


def build(tpl, skin, split):
    C, I, Tn, V, K, kv = skin; rng = random.Random(int(hashlib.sha256(f"{tpl['id']}|{C}|v07".encode()).hexdigest()[:8], 16))
    N = rng.choice([5, 6, 7]); keys = [kv[0], kv[1]] + [rng.choice(kv) for _ in range(N - 2)]; rng.shuffle(keys); vals = rng.sample(range(3, 60), N); rows = list(zip(keys, vals)); rates = {k: rng.randint(2, 5) for k in kv}
    P = 2 if N % 2 else 4; part = sum(v for k, v in rows if k == keys[0])
    sub = dict(C=C, I=I, T=Tn, V=V, K=K, L=rng.choice(tpl["logic"]), N=N, NM1=N - 1, NM2=N - 2, NM3=N - 3, ROWS=repr(rows), RATES=repr(rates), P=P, NDP=N // P, NRP=N % P, K0=keys[0], KUP=keys[0].upper(),
               MEAN="%g" % (sum(vals) / N), PART=part, TOTAL=sum(vals))
    f = lambda text: Template(text).substitute(sub); ctx = dict(R=rows, N=N, vals=vals, keys=keys, rates=rates)
    repo = {f"{C}.py": f(MODEL + (FEED if tpl.get("model") == "feed" else ""))}
    if tpl.get("extra") == "rates": repo["rates.py"] = f(RATES)
    for p, text in tpl["files"].items():
        body = f(text)
        for h in rng.sample(HELPERS, rng.choice([0, 1, 2])): body += f(h)
        repo[f(p)] = body
    repo["tests/test_visible.py"] = f(tpl["visible"]); repo["ISSUE.md"] = f(tpl["issue"]) + "\n"
    task = {"id": f"{tpl['id']}__{C}", "template": tpl["id"], "skin": C, "split": split, "symptom": tpl["symptom"], "cause": tpl["cause"], "role": tpl.get("role"), "group": tpl.get("group"),
            "repo": repo, "code_hash": S.code_hash(repo), "logic_file": f("$L.py"), "hidden": f(tpl["hidden"]), "fix": {"file": f("$L.py"), "function": f(tpl["fix_fn"]), "code": f(tpl["fix"])},
            "oldfix": {"code": f(tpl["oldfix"])} if tpl.get("oldfix") else None}
    if "p1" in tpl:
        task["teacher"] = {"probes": [{"suspect": f(tpl["s1"]), "test": f(tpl["p1"]), "predict": tpl["e1"](ctx)}, {"suspect": f(tpl["s2"]), "test": f(tpl["p2"]), "predict": tpl["e2"](ctx)}], "cause": f(tpl["why"])}
        if tpl["id"] in NAIVE:
            nv = NAIVE[tpl["id"]]; task["naive"] = {"step": nv["step"], "suspect": f(nv["s"]), "test": f(nv["p"]), "predict": nv["e"](ctx)}
    return task


def verify(task):
    """Execute everything the teacher claims.  Returns (record, list of problems)."""
    repo, bad = task["repo"], []; vis0, t1 = S.run_tests(repo, repo["tests/test_visible.py"]); hid0, t2 = S.run_tests(repo, task["hidden"])
    if all(v == "PASS" for v in vis0.values()): bad.append("visible tests all pass at the savepoint")
    if all(v == "PASS" for v in hid0.values()): bad.append("hidden tests all pass at the savepoint")
    fixed, info = S.apply_patch(repo, task["fix"]["code"], task["fix"]["file"])
    if fixed is None: bad.append("fix does not apply: " + str(info)); return {}, bad
    vis1, _ = S.run_tests(fixed, repo["tests/test_visible.py"]); hid1, _ = S.run_tests(fixed, task["hidden"])
    if not all(v == "PASS" for v in list(vis1.values()) + list(hid1.values())): bad.append("fix fails tests: " + json.dumps({k: v for k, v in {**vis1, **hid1}.items() if v != "PASS"}))
    rec = {"savepoint": {"visible": vis0, "hidden": hid0}, "fix": {"changed_lines": info["changed_lines"], "diff": info["diff"], "hidden": hid1}, "seconds": round(t1 + t2, 2)}
    if task["oldfix"]:
        old, oinfo = S.apply_patch(repo, task["oldfix"]["code"], task["fix"]["file"])
        if old is None: bad.append("old fix does not apply: " + str(oinfo))
        else:
            hid2, _ = S.run_tests(old, task["hidden"], timeout=5.0); vis2, _ = S.run_tests(old, repo["tests/test_visible.py"], timeout=5.0)
            if all(v == "PASS" for v in hid2.values()): bad.append("old fix passes the hidden tests")
            rec["oldfix"] = {"diff": oinfo["diff"], "hidden": hid2, "visible": vis2, "regressions": sorted(k for k in hid0 if hid0[k] == "PASS" and hid2.get(k) != "PASS"), "visible_regressions": sorted(k for k in vis0 if vis0[k] == "PASS" and vis2.get(k) != "PASS")}
    if task.get("naive"):
        out, secs = S.run_script(repo, task["naive"]["test"]); task["naive"]["observed"] = out; task["naive"]["seconds"] = secs
        if out == task["naive"]["predict"]: bad.append("naive test was not contradicted")
    for i, p in enumerate(task.get("teacher", {}).get("probes", [])):
        out, secs = S.run_script(repo, p["test"]); p["observed"] = out; p["seconds"] = secs
        if out != p["predict"]: bad.append(f"probe {i + 1}: predicted {p['predict']!r}, observed {out!r}")
    return rec, bad


def all_tasks():
    out = []
    for tpl in TRAIN_T:
        for skin in SKINS_TRAIN: out.append(build(tpl, skin, "train"))
        for skin in SKINS_DEV[:2] if TRAIN_T.index(tpl) % 2 == 0 else SKINS_DEV[2:]: t = build(tpl, skin, "dev"); t["group"] = "G1"; out.append(t)
    for tpl in DEV_T:
        for skin in SKINS_DEV: out.append(build(tpl, skin, "dev"))
    return out
