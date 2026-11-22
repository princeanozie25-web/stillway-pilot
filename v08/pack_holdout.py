"""Turn a holdout author's plain specification into runner and grader files.   python v08/pack_holdout.py SPEC.json OUT_DIR

SPEC.json is a list of jobs written by the holder (format: docs/v08_holdout_brief.md).  For each job this builds the
public files exactly as the generator would, computes the hidden expectations from the reference semantics, works the
job with the careful procedure through the runner, grades the result, and refuses any job that is not well posed.
Writes OUT_DIR/public.jsonl (give to the runner) and OUT_DIR/hidden.jsonl (keep).  Nothing here reads a model."""
import json, os, random, sys
sys.path.insert(0, ".")
from stillway8 import dataset as D, expert as E, world as W
from stillway8.grade import grade
from stillway8.runner import Session

KEY = lambda k: len(k.strip()) == 1 and k.strip().lower() in W.BASES and k in (k.strip(), k.strip() + " ")


def proj(j, n):
    true = j["intended"]; cur = dict(true, **j.get("fault", {})); rng = random.Random(f"pack-{n}"); kind = "bug" if j.get("fault") else "unans" if j.get("stale_expectation") else "valid"
    assert set(true) == {"norm", "dedupe", "cmp", "thr", "col", "func", "by", "dir"} and all(true[s] in W.SLOTS[W.SLOT_ROLE[s]][s] for s in true) and len(j.get("fault", {})) <= 1, "settings"
    data = [[dict(key=r[0], val=int(r[1]), qty=int(r[2])) for r in c["rows"]] for c in j["checks"]]; assert len(data) == 2 and all(3 <= len(d) <= 5 and all(KEY(r["key"]) and 1 <= r["val"] <= 9 and 1 <= r["qty"] <= 9 for r in d) for d in data), "two checks of 3 to 5 rows, values 1 to 9"
    want = [W.stages(true, d)["report"] for d in data]; expect = [{f: w[f] for f in W.FIELDS if f in c["fields"]} for w, c in zip(want, j["checks"])]
    for i, f, v in j.get("stale_expectation", []): expect[i][f] = v
    got = [W.stages(cur, d)["report"] for d in data]; failing = [i for i in range(2) if any(got[i][f] != expect[i][f] for f in expect[i])]
    fixes = [(s, v) for s, v in W.patches(cur) if all(W.stages(dict(cur, **{s: v}), data[i])["report"][f] == expect[i][f] for i in failing[:1] for f in expect[i])] if failing else []
    slot = next(iter(j.get("fault", {})), None)
    if kind == "valid": assert not failing, "a valid job must pass both visible checks"
    if kind == "bug": assert failing and fixes == [(slot, true[slot])], f"not well posed: one-line changes that satisfy the first failing check: {fixes}"
    if kind == "unans": assert failing and not fixes, f"a stale expectation must not be reachable by one change: {fixes}"
    ids = [f"m{i}" for i in range(8)]; rng.shuffle(ids); roles = ["load", "clean", "filter", "agg", "order", "report"]; name = dict(zip(roles, ids)); files = {name[r] + ".py": W.source(r, cur, name) for r in roles}
    for k, dec in enumerate(j.get("unused_modules", [])[:2]): files[ids[6 + k] + ".py"] = W.source(dec["role"], dict(cur, **dec["settings"]), name)
    checks = {}
    for i in range(2): files[f"data_c{i}.csv"] = W.csv_text(data[i]); checks[f"c{i}"] = {"data": f"data_c{i}.csv", "expect": expect[i]}
    goal = f"c{failing[0]}" if failing else "c0"; files["checks.json"] = json.dumps(checks, indent=1) + "\n"; files["job.json"] = json.dumps({"dom": "proj", "entry": name["report"], "goal": goal}) + "\n"
    hd = [[dict(key=r[0], val=int(r[1]), qty=int(r[2])) for r in rows] for rows in j["hidden_inputs"]]; assert len(hd) >= 3, "at least three hidden inputs"
    hid = {"kind": kind, "slot": slot, "wrong": cur[slot] if slot else None, "right": true[slot] if slot else None, "true": true, "names": name, "role": W.SLOT_ROLE.get(slot),
           "tests": [{"csv": W.csv_text(d), "expect": W.stages(true, d)["report"]} for d in data + hd], "reported": [next(f for f in expect[i] if got[i][f] != expect[i][f]) for i in failing]}
    hid["family"] = slot or kind; hid["mech"] = D.mech(slot, cur[slot], true[slot]) if slot else kind
    hid["route"] = None if not slot else "local" if hid["role"] in ("agg", "order") else "deep-direct" if any(r in ("count", "groups") for r in hid["reported"]) else "deep-indirect"
    return {"dom": "proj", "goal": goal, "entry": name["report"], "mods": sorted(x[:-3] for x in files if x.endswith(".py")), "files": files}, hid


def tab(j, n):
    led = sorted(({"key": r[0], "grp": r[1], "amt": int(r[2])} for r in j["ledger"]), key=lambda r: r["key"]); st = {k: int(v) for k, v in j["statement"]}; notes = dict(j.get("notes", [])); summ = {g: 0 for g in W.GROUPS}; summ.update({g: int(v) for g, v in j["summary"]})
    assert 3 <= len(led) <= 5 and all(r["key"] in [f"k{i}" for i in range(8)] and r["grp"] in W.GROUPS and 1 <= r["amt"] <= 9 for r in led) and all(1 <= v <= 9 for v in st.values()), "ledger of 3 to 5 rows, keys k0..k7, groups g0..g2, amounts 1 to 9"
    truth = {r["key"]: dict(r) for r in led}; items = []; unans = False; lk = {r["key"] for r in led}
    for k in sorted(lk | set(st)):
        kind = "amt" if k in lk and k in st and truth[k]["amt"] != st[k] else "onlyL" if k in lk and k not in st else "onlyS" if k not in lk else None
        if kind is None: continue
        note = notes.get(k, "nonote"); head = note.split()[0]; items.append((kind, head))
        if head == "nonote": unans = True; continue
        act = W.RULES[(kind, head)]
        if act == "COPY": truth[k]["amt"] = st[k]
        if act == "DROP": del truth[k]
        if act == "ADD": truth[k] = {"key": k, "grp": note.split()[1], "amt": st[k]}
    assert len(items) <= 3, "at most three differences"; sums = lambda rows: {g: sum(r["amt"] for r in rows if r["grp"] == g) for g in W.GROUPS}; stale = [g for g in W.GROUPS if summ[g] != sums(led)[g]]; assert len(stale) <= 1, "at most one stale group total"
    files = {"ledger.csv": "key,grp,amt,st\n" + "".join(f"{r['key']},{r['grp']},{r['amt']},open\n" for r in led), "statement.csv": "key,amt\n" + "".join(f"{k},{st[k]}\n" for k in sorted(st)),
             "notes.csv": "key,note\n" + "".join(f"{k},{notes[k]}\n" for k in sorted(notes)), "summary.csv": "grp,total\n" + "".join(f"{g},{summ[g]}\n" for g in W.GROUPS), "ignored.csv": "key\n", "job.json": json.dumps({"dom": "tab", "goal": "reconcile"}) + "\n"}
    tl = led if unans else sorted(truth.values(), key=lambda r: r["key"]); kind = "unans" if unans else "valid" if not items and not stale else "stale" if not items else "diff"
    fam = kind if not items or unans else "+".join(sorted({f"{k}/{n}" for k, n in items}))
    return {"dom": "tab", "goal": "reconcile", "files": files}, {"kind": kind, "items": [list(i) for i in items], "stale": stale[0] if stale else None, "ledger": {r["key"]: [r["grp"], r["amt"]] for r in tl}, "summary": summ if unans else sums(tl), "family": fam, "mech": fam, "route": None}


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True); P, H, bad = [], [], []
    for n, j in enumerate(spec):
        try:
            p, h = (proj if j["domain"] == "proj" else tab)(j, n); h["group"] = j.get("group", "unlabelled"); h["author_id"] = j.get("id", n); h["split"] = "holdout"; h["index"] = n; p["id"] = h["id"] = f"{p['dom']}-holdout-{W.job_id(p)}"
            s = Session(p, fast=True); steps, end = E.teach(s, p, h); g = grade(p, h, s.files(), end); s.close(); assert g["outcome"] == "verified", f"the careful procedure does not verify: {g}"
            h["teacher"] = {"scripts": len(steps) + 1, "ops": sum(len(x["script"]) for x in steps), "end": end}; h["untouched_verifies"] = grade(p, h, p["files"], "DONE")["outcome"] == "verified"; P.append(p); H.append(h)
        except Exception as e: bad.append((j.get("id", n), f"{type(e).__name__}: {e}"))
    open(f"{out}/public.jsonl", "w").writelines(json.dumps(p, sort_keys=True) + "\n" for p in P); open(f"{out}/hidden.jsonl", "w").writelines(json.dumps(h, sort_keys=True) + "\n" for h in H)
    print(f"{len(P)} jobs packed, {len(bad)} refused"); [print("  refused", i, "|", why[:300]) for i, why in bad]
