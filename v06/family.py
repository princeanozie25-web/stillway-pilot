"""v0.6: does experience with past policies make a NEW policy cheaper to learn?  Spec: docs/v06_spec.md.

    python -I v06/family.py FAMILY.json [--shard I --of N] [--seeds 3]     # writes results/v06/<name>_shard<I>.json
    python -I v06/family.py selftest

A family file (docs/v06_family_format.md):
  {"name", "attributes": [cardinalities], "decisions": K, "policies": {id: "one decision digit per case"}, "past": [ids], "new": [ids]}
Cases are every combination of attribute values, last attribute fastest.  Past policies are known in full
("yesterday's bank").  Each distinct new policy is learned from audits: a learner asks for the decision of a
case, and after n audits answers every case.

Learners
  scratch     5 small networks trained on the audits alone (no experience); the v0.5 default
  bank_row    a network trained on all past policies with one 16-number row per policy; for the new policy only a new
              row is fitted, the rest is frozen (v0.4 consolidation).  5 rows from different starts.
  tables      the past policies themselves: those consistent with the audits; if none, falls back to scratch
  programs    past policies turned into decision-list programs by greedy search, plus every program that differs from one
              of them in at most two constants; those consistent with the audits; if none, falls back to scratch
  selector    holds out a fifth of the audits and uses whichever of the four gets most of them right (ties in that order:
              tables, programs, bank_row, scratch)
  index       audited cases only
Best guess = majority of the committee or of the consistent candidates; cautious = answer only when they all agree.
Audits: passive (random order) and chosen (the cases the learner's own candidates disagree on most).
"""
import argparse, hashlib, json, os, sys, time
from itertools import combinations, product
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "v05"))
import blind as B

BUDGETS = (4, 8, 16, 32, 64, 128, 256, 512)


def selftest_family():
    """A made-up family for checking the code only: 3 attributes of 4 values, rules 'attribute a = v -> 1, attribute b = w -> 2, else 0'."""
    card = [4, 4, 4]; X = np.array(list(product(*[range(k) for k in card]))); pol = {}
    for i, (a, v, b, w) in enumerate(product(range(3), range(4), range(3), range(4))):
        if a < b and (i * 7) % 5 < 2: pol[f"p{i}"] = "".join(str(1 if x[a] == v else (2 if x[b] == w else 0)) for x in X)
    ids = sorted(pol); return {"name": "selftest", "attributes": card, "decisions": 3, "policies": pol, "past": ids[: len(ids) * 2 // 3], "new": ids[len(ids) * 2 // 3:]}


def greedy_program(lits, y, K):
    """Decision list reproducing a full table: rules [(literal indices, decision)], default.  lits: list of (attr, op, val, mask)."""
    conds = [((i,), m) for i, (_, _, _, m) in enumerate(lits)] + [((i, j), lits[i][3] & lits[j][3]) for i, j in combinations(range(len(lits)), 2) if lits[i][0] != lits[j][0]]
    C = np.array([m for _, m in conds]); Cf = C.astype(np.float32); Y = np.eye(K, dtype=np.float32)[y]; rem = np.ones(len(y), bool); rules = []
    while True:
        labs = np.unique(y[rem])
        if len(labs) <= 1 or len(rules) >= 40: return rules, int(np.bincount(y[rem], minlength=K).argmax()) if rem.any() else 0
        cnt = Cf @ (Y * rem[:, None]); tot = cnt.sum(1); pure = (cnt.max(1) == tot) & (tot > 0)
        if not pure.any(): return rules, int(np.bincount(y[rem], minlength=K).argmax())
        score = np.where(pure, tot - 0.01 * np.array([len(c[0]) for c in conds]), -1); j = int(score.argmax()); rules.append((conds[j][0], int(cnt[j].argmax()))); rem &= ~C[j]


def run_program(lits_index, card, rules, default, n):
    out = np.full(n, default); rem = np.ones(n, bool)
    for tests, s in rules:
        m = np.ones(n, bool)
        for (a, op, v) in tests: m &= lits_index[(a, op, v)]
        out[rem & m] = s; rem &= ~m
    return out


def program_family(X, card, past_tables, K, cap=400000):
    """Programs of the past policies and every program within two constant changes of one of them -> distinct tables."""
    n = len(X); lits = []; idx = {}
    for a, k in enumerate(card):
        for v in range(k):
            for op in ("=", "!="):
                m = (X[:, a] == v) if op == "=" else (X[:, a] != v); lits.append((a, op, v, m)); idx[(a, op, v)] = m
    fam = {}; progs = []
    for t in past_tables:
        rules, default = greedy_program(lits, t, K); prog = [(tuple((lits[i][0], lits[i][1], lits[i][2]) for i in tests), s) for tests, s in rules]; progs.append((prog, default))
        slots = [(ri, ti) for ri, (tests, _) in enumerate(prog) for ti in range(len(tests))]
        def variant(changes):
            p2 = [(list(tests), s) for tests, s in prog]
            for (ri, ti), v in changes: a, op, _ = p2[ri][0][ti]; p2[ri][0][ti] = (a, op, v)
            return [(tuple(tests), s) for tests, s in p2]
        todo = [()] + [(((ri, ti), v),) for (ri, ti) in slots for v in range(card[prog[ri][0][ti][0]]) if v != prog[ri][0][ti][2]]
        if len(slots) <= 10:
            for s1, s2 in combinations(slots, 2):
                for v1 in range(card[prog[s1[0]][0][s1[1]][0]]):
                    for v2 in range(card[prog[s2[0]][0][s2[1]][0]]):
                        if v1 != prog[s1[0]][0][s1[1]][2] and v2 != prog[s2[0]][0][s2[1]][2]: todo.append(((s1, v1), (s2, v2)))
        for ch in todo:
            if len(fam) >= cap: break
            tb = run_program(idx, card, variant(ch), default, n).astype(np.uint8); fam.setdefault(tb.tobytes(), tb)
    return np.array(list(fam.values())), progs


def consistent(F, obs, y):
    """Candidates of F that agree with the audits -> (guess, unanimous, disagreement) or None."""
    ok = F[(F[:, obs] == y[obs][None]).all(1)] if obs.any() else F
    if len(ok) == 0: return None
    K = int(F.max()) + 1; votes = np.stack([(ok == k).sum(0) for k in range(K)], 1); return votes.argmax(1), votes.max(1) == len(ok), 1.0 - votes.max(1) / len(ok)


class Core(torch.nn.Module):
    def __init__(self, m, d, K):
        super().__init__(); self.emb = torch.nn.Embedding(m, 16); self.f = torch.nn.Sequential(torch.nn.Linear(16 + d, 128), torch.nn.ReLU(), torch.nn.Linear(128, 128), torch.nn.ReLU(), torch.nn.Linear(128, K))
    def forward(self, e, x): return self.f(torch.cat([e, x], 1))


def train_core(P, X1, K, steps=3000, seed=0):
    torch.manual_seed(seed); m, n = P.shape; core = Core(m, X1.shape[1], K); opt = torch.optim.Adam(core.parameters(), lr=3e-3); Xt = torch.tensor(X1); Pt = torch.tensor(P.astype(np.int64)); g = torch.Generator().manual_seed(seed)
    for _ in range(steps):
        pi = torch.randint(0, m, (2048,), generator=g); ci = torch.randint(0, n, (2048,), generator=g)
        loss = torch.nn.functional.cross_entropy(core(core.emb(pi), Xt[ci]), Pt[pi, ci]); opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad(): fit = float(np.mean([(core(core.emb(torch.full((n,), i)), Xt).argmax(1).numpy() == P[i]).mean() for i in range(m)]))
    return core, fit


def bank_rows(core, X1, y, obs, K, seed):
    Xt = torch.tensor(X1); xo, yo = Xt[obs], torch.tensor(y[obs].astype(np.int64)); preds = []
    for i in range(5):
        torch.manual_seed(seed * 100 + i); row = torch.nn.Parameter(torch.randn(1, 16) * 0.5); opt = torch.optim.Adam([row], lr=0.05)
        for _ in range(200):
            loss = torch.nn.functional.cross_entropy(core(row.expand(len(xo), -1), xo), yo); opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): preds.append(core(row.expand(len(Xt), -1), Xt).argmax(1).numpy())
    return B.committee(np.stack(preds), K)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("family"); ap.add_argument("--shard", type=int, default=0); ap.add_argument("--of", type=int, default=1); ap.add_argument("--seeds", type=int, default=3); a = ap.parse_args()
    torch.set_num_threads(1); fam = selftest_family() if a.family == "selftest" else json.load(open(a.family)); card = fam["attributes"]; K = fam["decisions"]; t0 = time.time()
    X = np.array(list(product(*[range(k) for k in card]))); n = len(X); X1 = np.concatenate([np.eye(k, dtype=np.float32)[X[:, i]] for i, k in enumerate(card)], 1)
    tab = lambda i: np.frombuffer(fam["policies"][i].encode(), np.uint8) - 48
    P = np.unique(np.array([tab(i) for i in fam["past"]]), axis=0); past_set = {t.tobytes() for t in P}
    new = {}
    for i in sorted(fam["new"]): new.setdefault(tab(i).tobytes(), []).append(i)                    # distinct new policies
    new = sorted(new.items(), key=lambda kv: kv[1][0]); mine = [x for j, x in enumerate(new) if j % a.of == a.shard]
    core, core_fit = train_core(P, X1, K); F, progs = program_family(X, card, P, K)
    budgets = [b for b in BUDGETS if b < n] + [n]; ARMS = ["scratch", "bank_row", "tables", "programs", "selector", "index"]
    res = {"family": fam["name"], "cases": n, "attributes": card, "decisions": K, "past_policies": len(fam["past"]), "past_distinct": int(len(P)), "new_distinct": len(new), "program_family_tables": int(len(F)),
           "core_fit_on_past": core_fit, "past_programs_rules_median": float(np.median([len(p[0]) for p in progs])), "budgets": budgets, "seeds": a.seeds, "policies": []}
    def base(arm, y, obs, seed):
        if arm == "scratch": return B.committee(np.stack([B.net_fit(X1, y, obs, K, seed * 100 + i) for i in range(5)]), K) + (False,)
        if arm == "bank_row": return bank_rows(core, X1, y, obs, K, seed) + (False,)
        r = consistent(P if arm == "tables" else F, obs, y)
        return (r + (False,)) if r is not None else (base("scratch", y, obs, seed)[:3] + (True,))
    for key, ids in mine:
        y = np.frombuffer(key, np.uint8).astype(np.int64); row = {"ids": ids, "rule_seen_among_past": key in past_set, "in_program_family": bool((F == y[None].astype(np.uint8)).all(1).any()), "curves": {}}
        for mode in ("passive", "chosen"):
            for arm in ARMS: row["curves"][f"{mode}/{arm}"] = [[] for _ in budgets]
            for seed in range(1, a.seeds + 1):
                rng = np.random.default_rng(int(hashlib.sha256((ids[0] + mode + str(seed)).encode()).hexdigest()[:8], 16)); order = rng.permutation(n)
                obs_by = {arm: np.zeros(n, bool) for arm in ARMS}
                for arm in ARMS: obs_by[arm][order[:budgets[0]]] = True
                for bi, Bn in enumerate(budgets):
                    for arm in ARMS:
                        obs = obs_by[arm]; chosen_from = None
                        if arm == "index": maj = int(np.bincount(y[obs], minlength=K).argmax()); g, u, dis, fb = np.where(obs, y, maj), obs.copy(), (~obs).astype(float), False
                        elif arm == "selector":
                            idx = np.flatnonzero(obs); val = rng.permutation(idx)[:max(1, len(idx) // 5)]; tr = obs.copy(); tr[val] = False; best = None
                            for cand in ("tables", "programs", "bank_row", "scratch"):
                                gg = base(cand, y, tr, seed)[0]; sc = float((gg[val] == y[val]).mean())
                                if best is None or sc > best[0]: best = (sc, cand)
                            chosen_from = best[1]; g, u, dis, fb = base(chosen_from, y, obs, seed)
                        else: g, u, dis, fb = base(arm, y, obs, seed)
                        row["curves"][f"{mode}/{arm}"][bi].append({"right_all": float((g == y).mean()), "cautious_wrong": float((u & (g != y)).mean()), "cautious_abstained": float((~u).mean()), "fell_back": bool(fb), "selector_used": chosen_from})
                        if bi + 1 < len(budgets):
                            need = budgets[bi + 1] - Bn; cand = np.flatnonzero(~obs)
                            pick = cand[np.argsort(-(dis[cand] + rng.random(len(cand)) * 1e-3))[:need]] if (mode == "chosen" and arm != "index") else rng.permutation(cand)[:need]
                            obs_by[arm] = obs.copy(); obs_by[arm][pick] = True
        res["policies"].append(row)
        print(ids[0], "seen" if row["rule_seen_among_past"] else "novel", {arm: [round(float(np.mean([r["right_all"] for r in row["curves"][f"passive/{arm}"][bi]])), 2) for bi in range(len(budgets))] for arm in ("scratch", "bank_row", "programs", "selector")}, round(time.time() - t0), "s", flush=True)
    res["seconds"] = round(time.time() - t0, 1); os.makedirs(os.path.join(ROOT, "results", "v06"), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, "results", "v06", f"{fam['name']}_shard{a.shard}.json"), "w")); print("done", fam["name"], "shard", a.shard, len(mine), "new policies", res["seconds"], "s")


if __name__ == "__main__":
    main()
