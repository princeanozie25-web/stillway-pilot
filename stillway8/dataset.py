"""Splits, mechanisms and job recipes.  Everything is a pure function of (MASTER, split, index), so any job can be rebuilt.

Order of splitting: (1) source projects and source books are divided between splits by a hash of their content;
(2) mechanisms are divided into trained, held out (never a training bug: the 'newmech' group) and later (kept out of
pretraining altogether, for the memory experiments); (3) only then are jobs and their cosmetic variations drawn."""
import hashlib, json, random
from stillway8 import world as W

MASTER = 20261122
SPLITS = {"train": (0, 60), "dev": (60, 70), "hold": (70, 80), "day1": (80, 87), "day2": (87, 94), "fixture": (94, 100)}
TRAIN_SLOTS = ["norm", "dedupe", "cmp", "thr", "func", "dir"]; LATER_SLOTS = ["col", "by"]
HELD = {"norm:both>strip", "norm:none>lower", "norm:lower>strip", "cmp:ge>lt", "cmp:lt>le", "cmp:gt>le", "thr:-2", "func:max>mean", "func:count>sum", "func:sum>min", "func:mean>count"}
LATER_TAB = {("amt", "void"), ("onlyS", "pending")}; TRAIN_TAB = [k for k in W.RULES if k not in LATER_TAB]


def _h(obj): return int(hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:8], 16) % 100
def _rng(*key): return random.Random(hashlib.sha256(json.dumps([MASTER, *key]).encode()).hexdigest())


def sources(dom, split, n=4000):
    """The source projects (or books) that belong to a split."""
    rng = _rng("sources", dom); lo, hi = SPLITS[split]; out, seen = [], set()
    for _ in range(n):
        s = W.proj_source(rng) if dom == "proj" else W.tab_source(rng); key = json.dumps(s["cfg"] if dom == "proj" else [[r["key"], r["grp"]] for r in s["rows"]], sort_keys=True)
        if key not in seen and lo <= _h(key) < hi: out.append(s)
        seen.add(key)
    return out


def mech(slot, wrong, right): return f"thr:{int(wrong[1:]) - int(right[1:]):+d}" if slot == "thr" else f"{slot}:{wrong}>{right}"
def wrongs(slot, right):
    if slot == "thr": return [f"n{int(right[1:]) + d}" for d in (-2, -1, 1, 2) if 1 <= int(right[1:]) + d <= 9]
    return [v for v in W.SLOTS[W.SLOT_ROLE[slot]][slot] if v != right]


def proj_bug(rng, src, slots, held):
    """A (slot, wrong) for this project among `slots`; held=False only trained transitions, True only held-out ones, None any."""
    c = [(s, w) for s in slots for w in wrongs(s, src["cfg"][s]) if held is None or (mech(s, w, src["cfg"][s]) in HELD) == held]
    if not c: return None
    s = rng.choice(sorted({s for s, _ in c})); return rng.choice([x for x in c if x[0] == s])


def make(dom, split, i, group, srcs, pair=None):
    """One job of a named group, or None if the draw is not well posed.  Returns (public, hidden)."""
    rng = _rng(dom, split, i, group); src = srcs[rng.randrange(len(srcs))] if pair is None else pair["src"]
    if dom == "proj":
        if group in ("valid", "unans"): out = W.proj_job(rng, src, group)
        elif group == "trap":                                  # a trained fault where changing a later slot also satisfies the visible checks
            b = proj_bug(rng, src, ["func", "dir", "cmp", "thr", "dedupe"], False); out = W.proj_job(rng, src, "trap", *b, tries=300, also=LATER_SLOTS) if b else None
        else:
            later = group.startswith("later"); b = proj_bug(rng, src, LATER_SLOTS if later else TRAIN_SLOTS, None if later else group == "newmech")
            if b is None: return None
            if pair is not None:                               # altered precondition: same project, same first report, another cause
                for _ in range(40):
                    b = proj_bug(rng, src, [s for s in TRAIN_SLOTS if s != pair["slot"]], False)
                    out = W.proj_job(rng, src, "bug", *b, tries=60) if b else None
                    if out and out[1]["reported"][0] == pair["reported"]: break
                else: return None
            else: out = W.proj_job(rng, src, "bug", *b)
        if out is None: return None
        pub, hid = out; hid["family"] = hid["slot"] or hid["kind"]; hid["mech"] = mech(hid["slot"], hid["wrong"], hid["right"]) if hid["slot"] else hid["kind"]
        hid["route"] = None if not hid["slot"] else "local" if hid["role"] in ("agg", "order") else "deep-direct" if any(r in ("count", "groups") for r in hid["reported"]) else "deep-indirect"
    else:
        rules = TRAIN_TAB if not group.startswith("later") else sorted(LATER_TAB)
        if group == "valid": items, stale = [], False
        elif group == "stale": items, stale = [], True
        elif group == "unans": items = [rng.choice(TRAIN_TAB) for _ in range(rng.randint(0, 1))] + [(rng.choice(["amt", "onlyL", "onlyS"]), "nonote")]; rng.shuffle(items); stale = rng.random() < 0.2
        elif group == "scattered":                             # several differences whose notes call for different actions
            for _ in range(50):
                items = [rng.choice(rules if j == 0 else TRAIN_TAB) for j in range(rng.randint(2, 3))]
                if len({W.RULES[x] for x in items}) > 1: break
            rng.shuffle(items); stale = rng.random() < 0.25
        else: items, stale = [rng.choice(rules)], rng.random() < 0.25
        out = W.tab_job(rng, src, items, stale)
        if out is None: return None
        pub, hid = out
        if group == "stale" and hid["kind"] != "stale": return None
        hid["family"] = hid["kind"] if not items or hid["kind"] == "unans" else "+".join(sorted({f"{k}/{n}" for k, n in items})) if group == "scattered" else f"{items[0][0]}/{items[0][1]}"
        hid["mech"] = hid["family"]; hid["route"] = None
    hid["group"] = group; hid["split"] = split; hid["index"] = i; pub["id"] = hid["id"] = f"{dom}-{split}-{W.job_id(pub)}"
    return pub, hid


MIX = {"proj": [("familiar", 0.72), ("valid", 0.16), ("unans", 0.12)], "tab": [("familiar", 0.42), ("scattered", 0.30), ("stale", 0.10), ("valid", 0.08), ("unans", 0.10)]}
def train_group(dom, i):
    r = _rng("mix", dom, i).random(); acc = 0
    for g, p in MIX[dom]:
        acc += p
        if r < acc: return g
    return MIX[dom][-1][0]


EVAL = {"proj": [("familiar", 60), ("altered", 30), ("newmech", 40), ("valid", 20), ("unans", 20)], "tab": [("familiar", 50), ("scattered", 40), ("stale", 20), ("valid", 20), ("unans", 20)]}
def eval_set(split, spec=EVAL, scale=1.0):
    """A fixed evaluation set: [(public, hidden)], drawn group by group from the split's own source projects."""
    jobs = []
    for dom in ("proj", "tab"):
        srcs = sources(dom, split); fam = []
        for group, n in spec[dom]:
            n = max(1, int(round(n * scale))); got, i = 0, 0
            while got < n and i < n * 60:
                i += 1
                if group == "altered":
                    if not fam: break
                    base = fam[(got + i) % len(fam)][1]; j = make(dom, split, i, group, srcs, pair={"src": next(s for s in srcs if s["cfg"] == base["true"]), "slot": base["slot"], "reported": base["reported"][0]})
                    if j: j[1]["pair"] = base["id"]
                else: j = make(dom, split, i, group, srcs)
                if j is None or any(j[0]["id"] == x[0]["id"] for x in jobs): continue
                jobs.append(j); got += 1
                if group == "familiar": fam.append(j)
    return jobs
