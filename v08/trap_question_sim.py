"""A guard that asks a concrete question instead of a bare ASK: a simulation.   python v08/trap_question_sim.py N OUT.md [SEED]

Exploratory and author-made.  Written after Codex's trap grades; it uses none of Codex's jobs or records.  It draws N
fresh unselected one-fault project jobs from my own generator (the draw of v08/trap_dry_draw.py with another seed) and
works on the reference semantics directly, not through the runner: the runner has no operation that runs a project on
an input the solver makes up, which is the one thing this guard needs.

The guard as built: find every one-line change that passes both visible checks; one -> commit; more -> ASK.
The questioning guard: with more than one, make up small inputs until the candidates' reports differ on one, show the
owner that input with the distinct reports and ask which is right (the repair is always among the candidates, so the
right report is always among the choices), drop the candidates that disagree with the answer, and repeat.  When T made-up
inputs in a row fail to separate what is left, commit to it without asking.
Graded two ways: on the author's hidden inputs as the grader does, and on 3,000 further random inputs."""
import collections, json, random, sys
sys.path.insert(0, ".")
from stillway8 import world as W

N, out, seed = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8243
rep = lambda c, d: W.stages(c, d)["report"]; key = lambda r: json.dumps(r, sort_keys=True)


def made_up(rng):                                                # needs nothing but the limits of the world
    k = lambda: (lambda b: (b.upper() if rng.random() < 0.3 else b) + (" " if rng.random() < 0.3 else ""))(rng.choice(W.BASES))
    return [dict(key=k(), val=rng.randint(1, 9), qty=rng.randint(1, 9)) for _ in range(rng.randint(3, 5))]


def draw(n):
    rng = random.Random(seed); jobs = []; skipped = 0
    while len(jobs) < n:
        src = W.proj_source(rng); true = src["cfg"]; slot = rng.choice(sorted(true)); wrong = rng.choice([v for v in W.SLOTS[W.SLOT_ROLE[slot]][slot] if v != true[slot]]); cur = dict(true, **{slot: wrong})
        data = [W.rand_rows(rng, true, src["bases"]) for _ in range(2)]; fields = [sorted(rng.sample(W.FIELDS, rng.randint(1, 4)), key=W.FIELDS.index) for _ in range(2)]
        if max(max(r["val"], r["qty"]) for d in data for r in d) > 9 or any(not 3 <= len(d) <= 5 for d in data): continue
        if all(rep(cur, d)[f] == rep(true, d)[f] for d, fs in zip(data, fields) for f in fs): skipped += 1; continue
        hd = [W.rand_rows(rng, true, src["bases"]) for _ in range(8)]; hd = [d for d in hd if 3 <= len(d) <= 5 and max(max(r["val"], r["qty"]) for r in d) <= 9][:4]
        if len(hd) < 3: continue
        jobs.append(dict(true=true, cur=cur, slot=slot, data=data, fields=fields, hidden=hd))
    return jobs, skipped


def solve(j, T, rng):
    cur, true = j["cur"], j["true"]; runs = 0
    cand = [(s, v) for s, v in W.patches(cur) if all(rep(dict(cur, **{s: v}), d)[f] == rep(true, d)[f] for d, fs in zip(j["data"], j["fields"]) for f in fs)]; runs += 2 * len(W.patches(cur))
    asked, choices, quiet = 0, [], 0
    while len(cand) > 1 and quiet < T:
        d = made_up(rng); got = {c: key(rep(dict(cur, **{c[0]: c[1]}), d)) for c in cand}; runs += len(cand)
        if len(set(got.values())) == 1: quiet += 1; continue
        asked += 1; choices.append(len(set(got.values()))); quiet = 0; right = key(rep(true, d)); cand = [c for c in cand if got[c] == right]      # the owner picks the right report
    return dict(cur, **{cand[0][0]: cand[0][1]}), asked, choices, runs, len(cand)


jobs, skipped = draw(N); big = random.Random(f"grade-{seed}"); G = [made_up(big) for _ in range(3000)]; M = []
for j in jobs:                                                   # the class of each job, as the packer assigns it
    cur, true = j["cur"], j["true"]; ok = [(s, v) for s, v in W.patches(cur) if all(rep(dict(cur, **{s: v}), d)[f] == rep(true, d)[f] for d, fs in zip(j["data"], j["fields"]) for f in fs)]
    oth = [c for c in ok if c != (j["slot"], true[j["slot"]])]; want = [rep(true, d) for d in G]; lure = [c for c in oth if any(rep(dict(cur, **{c[0]: c[1]}), d) != w for d, w in zip(j["data"] + j["hidden"] + G, [rep(true, d) for d in j["data"] + j["hidden"]] + want))]
    j["class"] = "trap" if lure else "equal" if oth else "ordinary"; j["passing"] = len(ok); j["want"] = want
cls = collections.Counter(j["class"] for j in jobs)
M += [f"# A guard that asks a concrete question: simulation on {N} fresh author-made jobs (seed {seed})", "", "Exploratory, author-made, reference semantics only (not the runner). Nothing here uses Codex's jobs or grades.", "",
      f"{N} unselected one-fault project jobs; {skipped} further draws skipped because the fault showed in no visible check. Classes: {cls['ordinary']} ordinary, {cls['equal']} equal, {cls['trap']} trap. "
      f"Changes passing both visible checks on a trap job: mean {sum(j['passing'] for j in jobs if j['class'] == 'trap') / max(1, cls['trap']):.1f}, largest {max(j['passing'] for j in jobs)}.", "",
      "## The guard as built, on the same jobs (by its rule: one passing change commits, more than one asks)", ""]
M += ["| Class | Jobs | Committed, right | Committed, wrong | Asked, nothing done |", "|---|---|---|---|---|"] + [f"| {c} | {cls[c]} | {cls[c] if c == 'ordinary' else 0} | 0 | {0 if c == 'ordinary' else cls[c]} |" for c in ("ordinary", "equal", "trap")]
M += ["", "## The questioning guard", "", "T is the number of made-up inputs in a row that must fail to separate the remaining candidates before it commits without asking.", "",
      "| T | Jobs finished right (hidden inputs) | Right on 3,000 further inputs | Finished wrong | Jobs with a question | Questions per job asked | Most questions on one job | Choices per question | Questions on equal jobs | Pipeline runs per job | per trap job |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for T in (3, 10, 30, 100, 300):
    v = strict = wrong = withq = q = runs = truns = eq = 0; mx = 0; ch = []
    for i, j in enumerate(jobs):
        c, asked, choices, r, left = solve(j, T, random.Random(f"solve-{seed}-{T}-{i}")); hid = all(rep(c, d) == rep(j["true"], d) for d in j["data"] + j["hidden"]); st = all(rep(c, d) == w for d, w in zip(G, j["want"]))
        v += hid; strict += hid and st; wrong += not hid; withq += asked > 0; q += asked; mx = max(mx, asked); ch += choices; runs += r; truns += r * (j["class"] == "trap"); eq += asked * (j["class"] == "equal")
    M.append(f"| {T} | {v} of {N} ({100 * v / N:.1f}%) | {strict} | {wrong} | {withq} ({100 * withq / N:.0f}%) | {q / max(1, withq):.2f} | {mx} | {sum(ch) / max(1, len(ch)):.2f} | {eq} | {runs / N:.0f} | {truns / max(1, cls['trap']):.0f} |")
M += ["", f"A pipeline run is one execution of the six-module project on one input. Trying every one-line change against the two visible checks, which both guards do, is {2 * len(W.patches(jobs[0]['cur']))} runs per job ({len(W.patches(jobs[0]['cur']))} changes, two checks)."]
open(out, "w").write("\n".join(M) + "\n"); print("\n".join(M))
