"""Pack and classify one-fault project jobs whose visible checks may not pin the repair down.   python v08/pack_traps.py SPEC.json OUT_DIR

SPEC.json is a list of proj jobs in the format of docs/v08_holdout_brief.md, section 7, each with exactly one faulty
setting.  Unlike v08/pack_holdout.py, a job is NOT refused when several one-line changes make the visible checks pass.
Each job is classified instead, by execution of the reference semantics:

  ordinary  the true repair is the only one-line change that passes both visible checks            (hidden kind "bug")
  equal     other changes pass too, and each behaves like the repair on every input tried          (hidden kind "equal")
  trap      at least one other change passes both visible checks and behaves differently: a lure   (hidden kind "trap")

"Every input tried" is the author's hidden inputs plus 3,000 random inputs inside the limits of the brief, from a fixed
seed.  When a lure is not caught by the author's hidden inputs, one random input that catches it is appended to the hidden
tests, so the grader always tells a lure from the repair.  An optional "expect": "ordinary" | "equal" | "trap" makes the
packer refuse a job that classifies otherwise.  A job whose fault does not fail a visible check is refused.

Checked through the real runner and grader before a job is written: the careful procedure and the true repair are graded
verified, every equal change is graded verified, every lure passes both visible checks and is graded wrong.
Writes OUT_DIR/public.jsonl (give to the runner) and OUT_DIR/hidden.jsonl (keep).  Nothing here reads a model."""
import collections, json, os, random, sys
sys.path.insert(0, "."); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pack_holdout as PH
from stillway8 import dataset as D, expert as E, world as W
from stillway8.grade import grade
from stillway8.runner import Session

TRIES = 3000


def random_input(rng):
    key = lambda: (lambda k: (k.upper() if rng.random() < 0.3 else k) + (" " if rng.random() < 0.3 else ""))(rng.choice(W.BASES))
    return [dict(key=key(), val=rng.randint(1, 9), qty=rng.randint(1, 9)) for _ in range(rng.randint(3, 5))]


def job(j, n):
    true = j["intended"]; assert j.get("domain", "proj") == "proj" and len(j.get("fault", {})) == 1 and not j.get("stale_expectation"), "a proj job with exactly one faulty setting and no stale expectation"
    cur = dict(true, **j["fault"]); rng = random.Random(f"pack-{n}"); slot = next(iter(j["fault"])); repair = (slot, true[slot]); rep = lambda c, d: W.stages(c, d)["report"]
    assert set(true) == {"norm", "dedupe", "cmp", "thr", "col", "func", "by", "dir"} and all(cur[s] in W.SLOTS[W.SLOT_ROLE[s]][s] and true[s] in W.SLOTS[W.SLOT_ROLE[s]][s] for s in cur) and cur != true, "settings"
    rows = lambda rs: [dict(key=r[0], val=int(r[1]), qty=int(r[2])) for r in rs]; fine = lambda d: 3 <= len(d) <= 5 and all(PH.KEY(r["key"]) and 1 <= r["val"] <= 9 and 1 <= r["qty"] <= 9 for r in d)
    data = [rows(c["rows"]) for c in j["checks"]]; assert len(data) == 2 and all(map(fine, data)), "two checks of 3 to 5 rows, values 1 to 9"
    expect = [{f: rep(true, d)[f] for f in W.FIELDS if f in c["fields"]} for d, c in zip(data, j["checks"])]; assert all(expect), "each check asserts at least one field"
    got = [rep(cur, d) for d in data]; failing = [i for i in range(2) if any(got[i][f] != expect[i][f] for f in expect[i])]; assert failing, "the fault does not fail a visible check"
    others = [(s, v) for s, v in W.patches(cur) if (s, v) != repair and all(rep(dict(cur, **{s: v}), data[i])[f] == expect[i][f] for i in range(2) for f in expect[i])]
    hd = [rows(r) for r in j["hidden_inputs"]]; assert len(hd) >= 3 and all(map(fine, hd)), "at least three hidden inputs of 3 to 5 rows, values 1 to 9"
    r2 = random.Random(f"separate-{n}"); extra = [random_input(r2) for _ in range(TRIES)]; want = [rep(true, d) for d in extra]; lure, equal, added = [], [], []
    for x in others:
        c = dict(cur, **{x[0]: x[1]})
        if any(rep(c, d) != rep(true, d) for d in data + hd + added): lure.append(x); continue
        k = next((i for i, d in enumerate(extra) if rep(c, d) != want[i]), None)
        if k is None: equal.append(x)
        else: lure.append(x); added.append(extra[k])
    kind = "trap" if lure else "equal" if equal else "bug"; label = {"trap": "trap", "equal": "equal", "bug": "ordinary"}[kind]
    assert j.get("expect") in (None, label), f"expected {j.get('expect')}, classified {label}: lures {lure}, equally right {equal}"
    ids = [f"m{i}" for i in range(8)]; rng.shuffle(ids); roles = ["load", "clean", "filter", "agg", "order", "report"]; name = dict(zip(roles, ids)); files = {name[r] + ".py": W.source(r, cur, name) for r in roles}
    for k, dec in enumerate(j.get("unused_modules", [])[:2]): files[ids[6 + k] + ".py"] = W.source(dec["role"], dict(cur, **dec["settings"]), name)
    checks = {}
    for i in range(2): files[f"data_c{i}.csv"] = W.csv_text(data[i]); checks[f"c{i}"] = {"data": f"data_c{i}.csv", "expect": expect[i]}
    goal = f"c{failing[0]}"; files["checks.json"] = json.dumps(checks, indent=1) + "\n"; files["job.json"] = json.dumps({"dom": "proj", "entry": name["report"], "goal": goal}) + "\n"
    hid = {"kind": kind, "class": label, "slot": slot, "wrong": cur[slot], "right": true[slot], "true": true, "names": name, "role": W.SLOT_ROLE[slot], "lure": [list(x) for x in lure], "also_right": [list(x) for x in equal],
           "hidden_inputs_added": len(added), "tests": [{"csv": W.csv_text(d), "expect": rep(true, d)} for d in data + hd + added], "reported": [next(f for f in expect[i] if got[i][f] != expect[i][f]) for i in failing]}
    hid["family"] = slot; hid["mech"] = D.mech(slot, cur[slot], true[slot])
    hid["route"] = "local" if hid["role"] in ("agg", "order") else "deep-direct" if any(r in ("count", "groups") for r in hid["reported"]) else "deep-indirect"
    return {"dom": "proj", "goal": goal, "entry": name["report"], "mods": sorted(x[:-3] for x in files if x.endswith(".py")), "files": files}, hid


def after(p, h, slot, variant):
    """Apply one one-line change through the runner: (both visible checks pass, the grader's outcome)."""
    s = Session(p, fast=True); o = s.run(f"PATCH {h['names'][W.SLOT_ROLE[slot]]} {slot} {variant}\nCHECK c0\nCHECK c1")["obs"]; g = grade(p, h, s.files(), "DONE"); s.close()
    return o[-2:] == ["PASS", "PASS"], g["outcome"]


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True); P, H, bad = [], [], []
    for n, j in enumerate(spec):
        try:
            p, h = job(j, n); h["group"] = j.get("group", "unlabelled"); h["author_id"] = j.get("id", n); h["split"] = "trapset"; h["index"] = n; p["id"] = h["id"] = f"proj-trapset-{W.job_id(p)}"
            s = Session(p, fast=True); steps, end = E.teach(s, p, h); g = grade(p, h, s.files(), end); s.close(); assert g["outcome"] == "verified", f"the careful procedure with the true repair does not verify: {g}"
            h["teacher"] = {"scripts": len(steps) + 1, "ops": sum(len(x["script"]) for x in steps), "end": end}; h["untouched_verifies"] = grade(p, h, p["files"], "DONE")["outcome"] == "verified"
            assert after(p, h, h["slot"], h["right"]) == (True, "verified"), "the true repair must pass both visible checks and the hidden test"
            for s_, v_ in h["lure"]: assert after(p, h, s_, v_) == (True, "wrong"), f"lure {s_} {v_} must pass both visible checks and fail the hidden test"
            for s_, v_ in h["also_right"]: assert after(p, h, s_, v_) == (True, "verified"), f"{s_} {v_} classified as equally right must pass the hidden test"
            P.append(p); H.append(h)
        except Exception as e: bad.append((j.get("id", n), f"{type(e).__name__}: {e}"))
    assert len({p["id"] for p in P}) == len(P), "two jobs have identical files"
    open(f"{out}/public.jsonl", "w").writelines(json.dumps(p, sort_keys=True) + "\n" for p in P); open(f"{out}/hidden.jsonl", "w").writelines(json.dumps(h, sort_keys=True) + "\n" for h in H)
    c = collections.Counter((h["group"], h["class"]) for h in H); print(f"{len(P)} jobs packed, {len(bad)} refused"); [print(f"  {g}: {k} {v}") for (g, k), v in sorted(c.items())]; [print("  refused", i, "|", why[:300]) for i, why in bad]
