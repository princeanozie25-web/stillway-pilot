"""The teacher and the token format.

The teacher works a job through the runner, one script at a time, and every observation in its record comes from an
actual execution.  It follows a fixed, careful procedure that depends only on what it has observed; the hidden truth
is used solely to pick the repair that the evidence it has gathered determines.  With noise > 0 it sometimes acts
wrongly first (a wrong repair, a repair before the deciding fact, a forgotten recalculation), sees the failed check,
and recovers: those records carry ok=False on the wrong script.

A record is a list of steps {'script': [operation lines], 'obs': [observation lines], 'ok': bool} and an ending, DONE or
ASK.  `encode` turns it into tokens with a kind per token: 0 context, 1 action, 2 observation, 3 a wrong action."""
from stillway8.world import SLOTS, SLOT_ROLE, RULES, patches, BASES

SPECIAL = ["PAD", "BOS", "EOS", "ACT", "OBS", "EXEC", "END", ";", "|", "DONE", "ASK", "GOAL", "ENTRY", "MODS", "proj", "tab", "reconcile", "MEM", "USE", "NOMEM"]
OPS = ["CHECK", "DEPS", "SHOW", "PROBE", "PATCH", "REVERT", "DIFF", "ROWS", "FACT", "COPY", "KEEP", "DROP", "ADD", "SKIP", "RECALC"]
WORDS = ["c0", "c1", "role", "load", "clean", "filter", "agg", "order", "report", "norm", "dedupe", "cmp", "thr", "col", "func", "by", "dir", "none", "strip", "lower", "both", "off", "on", "gt", "ge", "lt", "le",
         "val", "qty", "sum", "mean", "max", "min", "count", "key", "asc", "desc", "groups", "total", "first", "exp", "got", "PASS", "FAIL", "ERR", "OK", "BAD", "r", "v", "d", "amt", "onlyL", "onlyS",
         "stmt_newer", "ledger_newer", "pending", "void", "dupstmt", "grp", "nonote", "open", "kept", "g0", "g1", "g2", "k-", "?"]
VOCAB = SPECIAL + OPS + WORDS + [f"m{i}" for i in range(8)] + [f"n{i}" for i in range(64)] + [f"k{i}" for i in range(8)] + [f"k{b}{s}" for b in BASES + BASES.upper() for s in ("", "_")]
TOK = {t: i for i, t in enumerate(VOCAB)}; assert len(TOK) == len(VOCAB)
UNK = TOK["?"]


def header(public):
    if public["dom"] == "proj": return ["BOS", "proj", "GOAL", public["goal"], "ENTRY", public["entry"], "MODS"] + public["mods"]
    return ["BOS", "tab", "GOAL", "reconcile"]


def step_tokens(step):
    """(tokens, kinds) of one executed step, as the runner appends them."""
    a = " ; ".join(step["script"]).split() + ["EXEC"]; o = " | ".join(step["obs"]).split() + ["END"]
    return ["ACT"] + a + ["OBS"] + o, [0] + [1 if step["ok"] else 3] * len(a) + [0] + [2] * len(o)


def encode(public, steps, end):
    toks = header(public); kinds = [0] * len(toks)
    for s in steps: t, k = step_tokens(s); toks += t; kinds += k
    return toks + ["ACT", end, "EOS"], kinds + [0, 1, 0]


def ids(toks): return [TOK.get(t, UNK) for t in toks]


# ------------------------------------------------------------------ the teacher
def teach(sess, public, hidden, rng=None, noise=0.0):
    return (teach_proj if public["dom"] == "proj" else teach_tab)(sess, public, hidden, rng, noise)


def teach_proj(sess, pub, hid, rng, noise):
    steps = []
    def do(lines, ok=True): r = sess.run("\n".join(lines)); steps.append({"script": lines, "obs": r["obs"], "ok": ok}); return r["obs"]
    slip = lambda: rng is not None and rng.random() < noise
    o = do(["CHECK c0", "CHECK c1"]); fails = [i for i in (0, 1) if o[i].startswith("FAIL")]
    if not fails: return steps, "DONE"
    reported = [o[i].split()[1] for i in fails]; cx = f"c{fails[0]}"; deps = do([f"DEPS {pub['entry']}"])[0].split()
    shows = do([f"SHOW {m}" for m in deps]); mod = {s.split()[1]: m for s, m in zip(shows, deps)}; cur = {}
    for s in shows: w = s.split()[2:]; cur.update(dict(zip(w[::2], w[1::2])))
    def wrong_patch():                                         # a plausible one-line change that is not the repair
        c = [(s, v) for s, v in patches({**{k: None for r in SLOTS.values() for k in r}, **cur}) if s in cur and (s, v) != (hid["slot"], hid["right"]) and SLOT_ROLE[s] in mod]
        s, v = rng.choice(c); return [f"PATCH {mod[SLOT_ROLE[s]]} {s} {v}", "CHECK c0", "CHECK c1"]
    local = hid["role"] in ("agg", "order"); revert = []
    if not any(r in ("count", "groups") for r in reported):
        do([f"PROBE {mod['filter']} {cx}"])
        if not local and slip(): do(wrong_patch(), ok=False); revert = ["REVERT"]     # acted before the deciding fact
    if not local:
        mc = do(revert + [f"DEPS {mod['filter']}"])[-1]; o = do([f"SHOW {mc}", f"DEPS {mc}"]); mod["clean"] = mc; w = o[0].split()[2:]; cur.update(dict(zip(w[::2], w[1::2]))); do([f"PROBE {o[1]} {cx}"]); revert = []
    if hid["kind"] == "unans":
        if slip(): do(wrong_patch(), ok=False); do(["REVERT"])
        return steps, "ASK"
    if slip(): do(wrong_patch(), ok=False); revert = ["REVERT"]
    o = do(revert + [f"PATCH {mod[hid['role']]} {hid['slot']} {hid['right']}", "CHECK c0", "CHECK c1"]); assert o[-2:] == ["PASS", "PASS"], o
    return steps, "DONE"


def tab_plan(diffs, notes, stale):
    """The careful plan for a tab job from what has been observed: (action lines, groups to recalculate)."""
    lines, groups = [], set([stale] if stale else [])
    for d, note in zip(diffs, notes):
        k = d[0]; kind = d[1] if d[1] == "onlyS" else d[2]; act = RULES[(kind, note.split()[0])]
        lines.append(f"ADD {k} {note.split()[1]}" if act == "ADD" else f"{act} {k}")
        if act in ("COPY", "DROP"): groups.add(d[1])
        if act == "ADD": groups.add(note.split()[1])
    return lines, sorted(groups)


def teach_tab(sess, pub, hid, rng, noise):
    steps = []
    def do(lines, ok=True): r = sess.run("\n".join(lines)); steps.append({"script": lines, "obs": r["obs"], "ok": ok}); return r["obs"]
    o = do(["DIFF", "CHECK c0"]); diffs = [x.split() for x in o[0].split("d ")[1:]] if o[0] != "none" else []; stale = o[1].split()[1] if o[1].startswith("FAIL") else None
    if not diffs and not stale: return steps, "DONE"
    notes = do([f"FACT {d[0]}" for d in diffs]) if diffs else []
    if any(n == "nonote" for n in notes): return steps, "ASK"
    lines, groups = tab_plan(diffs, notes, stale); tail = ["CHECK c0"] + (["CHECK c1"] if diffs else [])
    if groups and rng is not None and rng.random() < noise:    # forgot one recalculation; the check says which
        miss = rng.choice(groups); o = do(lines + [f"RECALC {g}" for g in groups if g != miss] + tail, ok=False)
        if o[len(lines) + len(groups) - 1].startswith("FAIL"): do([f"RECALC {miss}", "CHECK c0"])
    else: do(lines + [f"RECALC {g}" for g in groups] + tail)
    return steps, "DONE"
