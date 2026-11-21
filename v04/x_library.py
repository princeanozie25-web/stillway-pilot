"""BEYOND THE BRIEF (exploratory, after the freeze): a bank of PROGRAMS, with a rule library learned from past policies.

    python v04/x_library.py SEED        # uses the seed's final core and its M3 snapshots; writes results/v04/x/library_s<SEED>.json

In v0.4 M3 the non-neural rule-induction baseline beat every neural arm, but it was GIVEN the family of 36 rules.
Here nobody gives the family.
  1. For every base policy, the shortest program in a generic language (a decision list of up to 3 rules, each a
     test of at most two facts, plus a default) that reproduces its logged decisions is found by search.
  2. Constants in those programs (a level threshold, an exception tag) become holes.  The distinct skeletons are the
     LIBRARY: reusable procedures with explicit arguments.  The family is every way of filling the holes.
  3. A new policy is consolidated by search: the library members consistent with its logged decisions.  Where they
     all agree the bank answers; where they disagree it ABSTAINS.  If no member fits, the family is violated:
     the shortest generic program is used, flagged, and its skeleton joins the library at the next sleep.
Scored on the SAME documents as the M3 arms (the raw files of the frozen runs), through the same compiled
procedure tables, by the plain grader.  Decisions on new policies are split into right, wrong and abstained.
Also: how many audited decisions it takes to pin a new policy down, passively and when the system chooses the case.
"""
import json, os, sys, time
from itertools import product
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4 import approvals as A
from stillway4.arms import load, make_data
from stillway4.grader import grade
from stillway4.runtime import TableRuntime, compile_procedures

seed = int(sys.argv[1]); core = f"runs/v4f_proc_s_s{seed}"; man = json.load(open(f"{core}/manifest.json")); salt = man["args"]["salt"]; torch.set_num_threads(1); t_start = time.time()
F = A.ALL_FACTS.numpy(); NB = 36; FULL = (1 << NB) - 1
bits = lambda cond: sum(1 << i for i in range(NB) if cond(F[i]))
LIT = [("lvl>=", 2, bits(lambda f: f[0] >= 2)), ("lvl>=", 3, bits(lambda f: f[0] >= 3)), ("lvl<", 2, bits(lambda f: f[0] < 2)), ("lvl<", 3, bits(lambda f: f[0] < 3)),
       ("stale", None, bits(lambda f: f[1] == 1)), ("fresh", None, bits(lambda f: f[1] == 0)), ("tag==", 1, bits(lambda f: f[2] == 1)), ("tag==", 2, bits(lambda f: f[2] == 2)),
       ("tag!=", 1, bits(lambda f: f[2] != 1)), ("tag!=", 2, bits(lambda f: f[2] != 2)), ("conflict", None, bits(lambda f: f[3] == 1)), ("consistent", None, bits(lambda f: f[3] == 0))]
CONDS = [((), FULL)] + [((i,), LIT[i][2]) for i in range(12)] + [((i, j), LIT[i][2] & LIT[j][2]) for i in range(12) for j in range(i + 1, 12)]
seen_m = set(); CONDS = [c for c in CONDS if c[1] and not (c[1] in seen_m or seen_m.add(c[1]))]          # distinct, non-empty; simpler tests first
STAT = (A.VALID, A.INVALID, A.ABSTAIN)


def shortest_program(obs, max_rules=3):
    """obs: 36 statuses, -1 where nothing was logged.  Returns (rules [(literal ids, status)], default) or None.  Iterative deepening."""
    S = {s: sum(1 << i for i in range(NB) if obs[i] == s) for s in STAT}; observed = S[A.VALID] | S[A.INVALID] | S[A.ABSTAIN]
    def dfs(rem, depth):
        ro = rem & observed
        for s in STAT:
            if ro & ~S[s] == 0: return [], s
        if depth == 0: return None
        for lits, mask in CONDS:
            mo = mask & ro
            if mo == 0: continue
            for s in STAT:
                if mo & ~S[s] == 0:
                    r = dfs(rem & ~mask, depth - 1)
                    if r is not None: return [(lits, s)] + r[0], r[1]
        return None
    for d in range(max_rules + 1):
        r = dfs(FULL, d)
        if r is not None: return r
    return None


def table_of(rules, default):
    t = [default] * NB; rem = FULL
    for lits, s in rules:
        m = FULL
        for i in lits: m &= LIT[i][2]
        for i in range(NB):
            if (m & rem) >> i & 1: t[i] = s
        rem &= ~m
    return tuple(t)


def skeleton(rules, default): return (tuple((tuple((LIT[i][0], LIT[i][1] is not None) for i in lits), s) for lits, s in rules), default)


def instantiate(skel):
    """Every way of filling the holes of a skeleton -> set of tables."""
    rules, default = skel; slots = [(ri, li, kind) for ri, (lits, _) in enumerate(rules) for li, (kind, hole) in enumerate(lits) if hole]; out = set()
    for vals in product(*[((2, 3) if k.startswith("lvl") else (1, 2)) for _, _, k in slots]):
        fill = {(ri, li): v for (ri, li, _), v in zip(slots, vals)}; prog = []
        for ri, (lits, s) in enumerate(rules):
            ids = tuple(next(i for i in range(12) if LIT[i][0] == kind and LIT[i][1] == (fill.get((ri, li)) if hole else None)) for li, (kind, hole) in enumerate(lits)); prog.append((ids, s))
        out.add(table_of(prog, default))
    return out


def entailed(family, obs):
    """Tables of the family consistent with obs; per cell the status they all give, else -1; and whether any fits."""
    ok = [t for t in family if all(o < 0 or o == t[i] for i, o in enumerate(obs))]
    if not ok: return None
    return [t0 if all(t[i] == t0 for t in ok) else -1 for i, t0 in enumerate(ok[0])]


# ---- 1, 2: the library, from the base policies' logged decisions ----
uni, data = make_data(seed, salt=salt); rec = A.decision_records(data["train"]); n_base = len(uni.pid_rule) - 1
base_obs = np.full((n_base + 1, NB), -1); base_obs[rec["pid"].numpy(), rec["fact"].numpy()] = rec["status"].numpy()
library = {}; base_tables = {}
for p in range(1, n_base + 1):
    r = shortest_program(base_obs[p].tolist()); base_tables[p] = base_obs[p].tolist()
    if r is not None: library.setdefault(skeleton(*r), []).append(p)
family = set()
for sk in library: family |= instantiate(sk)
TRUE = {r: tuple(A.RULE_TABLE[r].tolist()) if hasattr(A, "RULE_TABLE") else None for r in range(36)}
from stillway4.sleep import RULE_TABLE
TRUE = {r: tuple(RULE_TABLE[r].tolist()) for r in range(36)}; true_family = set(TRUE.values())
res = {"seed": seed, "library": {"skeletons": len(library), "base_policies_explained": sum(len(v) for v in library.values()), "base_policies": n_base, "family_tables": len(family),
                                 "true_rules_covered": sum(t in family for t in TRUE.values()), "reserved_rules_covered": sum(TRUE[r] in family for r in A.RESERVED_RULES), "reserved_rules": len(A.RESERVED_RULES),
                                 "family_tables_outside_the_true_family": len(family - true_family), "build_seconds": round(time.time() - t_start, 2),
                                 "example_skeletons": [str(sk) for sk in list(library)[:3]]}, "sessions": [], "audits": {}}
print("library:", {k: v for k, v in res["library"].items() if k != "example_skeletons"}, flush=True)

# ---- 3: the six sessions of the frozen M3 run, same documents, same compiled procedures ----
name = os.path.basename(core); base = f"results/v04/m3/{name}"; z = np.load(f"{base}/raw_outputs.npz"); model = load(f"{core}/checkpoint.pt"); proc = compile_procedures(model.tables())
RULES = [(th, w, st, cf) for th in (1, 2, 3) for w in (0, 1, 2) for st in (0, 1) for cf in (0, 1)]; FIELDS = A.FIELDS
def replay_pins(doc):
    """Which slots an event recomputes and the policy each is pinned to afterwards (own replay; the grader does not expose pins)."""
    jur = [-1] * 5; signed = [False] * 5; pin = [-1] * 5; pj = {}; out = []
    for e in doc["events"]:
        k = e["kind"]; hit = []
        if k == 0: signed[e["slot"]] = True; pin[e["slot"]] = pj.get(jur[e["slot"]], -1); hit = [e["slot"]]
        elif k == 1: hit = [e["slot"]]
        elif k == 2:
            jur[e["slot"]] = e["jur"]
            if signed[e["slot"]]: pin[e["slot"]] = pj.get(e["jur"], -1); hit = [e["slot"]]
        elif k in (3, 5):
            pj[e["jur"]] = e["pid"] if k == 3 else 0
            for i in range(5):
                if jur[i] == e["jur"] and signed[i]: pin[i] = pj[e["jur"]]; hit.append(i)
        elif k == 4: pj[e["jur"]] = e["pid"]
        out.append([(i, pin[i]) for i in hit])
    return out
learned_family = set(family); grown = []
PRIOR = {}
for p in range(1, n_base + 1):                                         # prior: how many base policies have exactly this table
    t = tuple(base_tables[p])
    if -1 not in t: PRIOR[t] = PRIOR.get(t, 0) + 1
for k in range(1, 7):
    snap = torch.load(f"{base}/snapshot_v{k}.pt", weights_only=False); look = snap["arms"]["retrieval"]["lookup"].numpy(); pr = z[f"s{k}_pid_rule"]
    pol = {i: (RULES[int(r)] if r >= 0 else None) for i, r in enumerate(pr) if i > 0}; new_all = [p for p in range(n_base + 1, len(pr))]; new_k = set(snap["new"])
    banks = {"library": dict(base_tables), "library_best_guess": dict(base_tables), "given_family": dict(base_tables), "generic_only": dict(base_tables)}; info = {"violations": 0, "undetermined_cells_new": {}}
    for p in range(1, len(pr)):
        obs = look[p].tolist() if p < len(look) else [-1] * NB
        if p <= n_base and not all(o == A.ABSTAIN or o < 0 for o in obs): obs = [o if o >= 0 else b for o, b in zip(obs, base_tables[p])]
        if all(o < 0 for o in obs): continue
        for arm, fam in (("library", learned_family), ("given_family", true_family)):
            if all(o == A.ABSTAIN for o in obs if o >= 0) and sum(o >= 0 for o in obs) == NB: banks[arm][p] = [A.ABSTAIN] * NB; continue      # the expiry notice
            e = entailed(fam, obs)
            if e is None:                                              # no member fits: the family is violated; shortest generic program, flagged
                r = shortest_program(obs); e = list(table_of(*r)) if r else [-1] * NB
                if arm == "library":
                    info["violations"] += 1
                    if r and sum(o >= 0 for o in obs) >= 30 and skeleton(*r) not in library: library[skeleton(*r)] = [p]; grown.append((k, p))
            banks[arm][p] = e
            if arm == "library":                                       # best-guess mode: undetermined cells take the vote of the fitting members, weighted by how many past policies each explains
                fit = [t for t in learned_family if all(o < 0 or o == t[i] for i, o in enumerate(obs))]
                g = list(e)
                for c in range(NB):
                    if g[c] < 0 and fit: g[c] = max(STAT, key=lambda s_: sum(PRIOR.get(t, 0.2) for t in fit if t[c] == s_))
                banks["library_best_guess"][p] = g
            if arm in ("library", "given_family") and p in new_k: info["undetermined_cells_new"].setdefault(arm, []).append(sum(x < 0 for x in e))
        r = shortest_program(obs); banks["generic_only"][p] = list(table_of(*r)) if r else [-1] * NB
    for sk, _ in list(library.items()): learned_family |= instantiate(sk)                                         # the library grows at the sleep
    row = {"session": k, "new_ids": sorted(new_k), "family_violations": info["violations"], "library_family_tables": len(learned_family),
           "undetermined_cells_per_new_policy": {a: float(np.mean(v)) for a, v in info["undetermined_cells_new"].items()}, "arms": {}}
    sets = {st: [{"events": [dict(zip(FIELDS, map(int, e))) for e in ev]} for ev in z[f"s{k}_{st}_events"][::2]] for st in ("learn", "retain")}                # every second document
    pins = {st: [replay_pins(d) for d in sets[st]] for st in sets}
    def split(st, outs):
        """Decisions on this session's new policies: right, wrong, abstained (abstained = said ABSTAIN where the right answer was not ABSTAIN)."""
        r_ = w_ = a_ = 0
        for d, o, pn in zip(sets[st], outs, pins[st]):
            from stillway4.grader import expected
            want = expected(d, pol)[0]
            for t, hits in enumerate(pn):
                if d["events"][t]["kind"] == 6: continue
                for (i, pid) in hits:
                    if pid in new_k:
                        if o[t][i] == want[t][i]: r_ += 1
                        elif o[t][i] == A.ABSTAIN: a_ += 1
                        else: w_ += 1
        return {"right": r_, "wrong": w_, "abstained": a_}
    for arm, bank in banks.items():
        rt = TableRuntime(proc, {p: [(x if x >= 0 else A.ABSTAIN) for x in t] for p, t in bank.items()}); row["arms"][arm] = {}
        for st in sets:
            outs = []
            for d in sets[st]:
                job = rt.new_job(); outs.append([rt.step(job, e) for e in d["events"]])
            row["arms"][arm][st] = {"documents": len(outs), "success": float(np.mean([grade(d, pol, o)["success"] for d, o in zip(sets[st], outs)]))}
            if st == "learn": row["arms"][arm]["new_policy_decisions"] = split(st, outs)
    for arm in ("dreaming", "consolidation", "rehearsal", "retrieval", "induction"):                                 # the frozen arms on the same documents
        row["arms"][f"m3_{arm}"] = {}
        for st in sets:
            outs = [o.tolist() for o in z[f"s{k}_{st}_{arm}_out"][::2]]
            row["arms"][f"m3_{arm}"][st] = {"documents": len(outs), "success": float(np.mean([grade(d, pol, o)["success"] for d, o in zip(sets[st], outs)]))}
            if st == "learn": row["arms"][f"m3_{arm}"]["new_policy_decisions"] = split(st, outs)
    res["sessions"].append(row)
    print("session", k, {a: (round(v["learn"]["success"], 3), round(v["retain"]["success"], 3), v["new_policy_decisions"]["wrong"], v["new_policy_decisions"]["abstained"]) for a, v in row["arms"].items()}, flush=True)
res["library_grown_at"] = grown
# ---- audits needed to pin a new policy down: passive (cases as they arrive) against chosen ----
rng = np.random.default_rng(seed); pf = np.array([(1 / 3) * (0.3 if f[1] else 0.7) * (0.6, 0.2, 0.2)[f[2]] * (0.15 if f[3] else 0.85) for f in F])
def audits(fam, truth, active):
    fam = list(fam); alive = list(range(len(fam))); n = 0; asked = set()
    while len({fam[i] for i in alive}) > 1 and n < 400:
        if active:                                                    # the case whose answer splits the remaining candidates most evenly
            best = min((max(sum(1 for i in alive if fam[i][c] == s) for s in STAT), c) for c in range(NB) if c not in asked)[1]; c = best
        else: c = int(rng.choice(NB, p=pf))
        n += 1; asked.add(c); alive = [i for i in alive if fam[i][c] == truth[c]]
    return n
for label, fam in (("learned_library", learned_family), ("given_family", true_family)):
    tr = [t for t in TRUE.values() if t in fam]
    res["audits"][label] = {"family_tables": len(fam), "passive_mean": float(np.mean([audits(fam, t, False) for t in tr for _ in range(20)])), "chosen_mean": float(np.mean([audits(fam, t, True) for t in tr])),
                            "chosen_max": int(max(audits(fam, t, True) for t in tr))}
need_all = []                                                    # no family at all (an index of seen cases): every one of the 36 cases has to turn up
for _ in range(300):
    seen_c = set(); n = 0
    while len(seen_c) < NB: seen_c.add(int(rng.choice(NB, p=pf))); n += 1
    need_all.append(n)
res["audits"]["no_family"] = {"passive_mean": float(np.mean(need_all)), "chosen_mean": 36.0, "chosen_max": 36}
json.dump(res, open(f"results/v04/x/library_s{seed}.json", "w"), indent=1); print("audits", res["audits"], "| seconds", round(time.time() - t_start, 1))
