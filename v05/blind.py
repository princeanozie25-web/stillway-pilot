"""v0.5: the program-search bank on rule sets I did not write.  Spec: docs/v05_spec.md (frozen before any data was fetched).

    python -I v05/blind.py DATASET [--tests 2] [--seeds 5]        # writes results/v05/<dataset>_t<tests>.json
    python -I v05/blind.py selftest                               # a made-up rule, to check the code only

A dataset is a complete or near-complete table: every combination of attribute values with the decision someone
else's rule gives it.  The table is used as an auditor: a learner may ask for the decision of a case (an audit).
After n audits each learner answers EVERY case in the table, so generalisation is measured exactly.

Learners
  program    decision lists found by greedy search: a rule is a test of at most `tests` attributes (attribute = value or
             attribute != value) with a decision; the rule that covers most audited cases with no exception is taken
             first.  A list must reproduce every audited case, or it is flagged.  A committee of 7 lists (different
             random tie-breaks and scoring subsamples).  Best guess = majority; cautious = answer only when unanimous.
  program+net  the same search, with a small network proposing decisions for unaudited cases; among rules equally
             good on the evidence, the one that agrees with more proposals is preferred.  Evidence still has to be reproduced.
  net        5 small networks (one-hot input, two hidden layers of 64); majority; cautious = unanimous.
  tree, forest   scikit-learn decision tree and 50-tree random forest on the same one-hot input (forest cautious = unanimous)
  index      answers audited cases only; best guess for the rest = most common audited decision.
Audits:  passive (random order) and chosen (each learner asks for the cases its own committee disagrees on most).
"""
import argparse, json, os, sys, time
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SPECS = {  # file, separator, class column, columns to drop
    "car": ("car.data", ",", -1, []), "nursery": ("nursery.data", ",", -1, []), "balance": ("balance-scale.data", ",", 0, []),
    "monks1": ("monks-1.test", " ", 0, [-1]), "monks2": ("monks-2.test", " ", 0, [-1]), "monks3": ("monks-3.test", " ", 0, [-1]),
    "lenses": ("lenses.data", " ", -1, [0]), "tictactoe": ("tic-tac-toe.data", ",", -1, [])}


def load(name):
    if name == "selftest":                                         # 4 attributes with 3 values; a made-up rule (code check only)
        X = np.array([(a, b, c, d) for a in range(3) for b in range(3) for c in range(3) for d in range(3)]); y = ((X[:, 0] == 1) | ((X[:, 1] != 0) & (X[:, 2] == 2))).astype(int)
        return X, y, [3, 3, 3, 3]
    f, sep, cc, drop = SPECS[name]; rows = [l.strip().split(sep) if sep != " " else l.split() for l in open(os.path.join(ROOT, "data", "external", "uci", f)) if l.strip()]
    rows = [r for r in rows if len(r) == len(rows[0])]; ncol = len(rows[0]); cc = cc % ncol; dropc = {c % ncol for c in drop} | {cc}
    cols = [c for c in range(ncol) if c not in dropc]; enc = [sorted({r[c] for r in rows}) for c in cols]; cls = sorted({r[cc] for r in rows})
    X = np.array([[enc[j].index(r[c]) for j, c in enumerate(cols)] for r in rows]); y = np.array([cls.index(r[cc]) for r in rows])
    _, first = np.unique(X, axis=0, return_index=True); first = np.sort(first)                 # one row per case
    return X[first], y[first], [len(e) for e in enc]


def conditions(X, card, tests):
    """Every test of up to `tests` attributes.  Returns bool (m, n)."""
    lit = []
    for a, k in enumerate(card):
        for v in range(k):
            lit.append((a, X[:, a] == v))
            if k > 2: lit.append((a, X[:, a] != v))
    out = [m for _, m in lit]
    def grow(prev, depth):
        if depth == tests: return
        nxt = []
        for attrs, m in prev:
            for a, lm in lit:
                if a > attrs[-1]: mm = m & lm; nxt.append((attrs + (a,), mm))
        out.extend(m for _, m in nxt); grow(nxt, depth + 1)
    grow([((a,), m) for a, m in lit], 1)
    C = np.array(out); C = C[C.any(1)]; C = np.unique(C, axis=0)
    return C


def fit_list(Cf, Cb, y, obs, K, rng, prop=None, lam=0.25, max_rules=400):
    """Greedy decision list.  Returns (decisions for every case, number of rules, reproduces the evidence exactly)."""
    n = len(y); rem = np.ones(n, bool); pred = np.full(n, -1); Y = np.eye(K, dtype=np.float32)[y]; sub = obs & (rng.random(n) < 0.7); nr = 0; exact = True
    maj = int(np.bincount(y[obs], minlength=K).argmax())
    while True:
        ro = rem & obs
        if not ro.any(): pred[rem] = maj; break
        labs = np.unique(y[ro])
        if len(labs) == 1: pred[rem] = labs[0]; break
        if nr >= max_rules: pred[rem] = int(np.bincount(y[ro], minlength=K).argmax()); exact = False; break
        cnt = Cf @ (Y * ro[:, None]); tot = cnt.sum(1); bc = cnt.argmax(1); pure = (cnt.max(1) == tot) & (tot > 0)
        if not pure.any(): pred[rem] = int(np.bincount(y[ro], minlength=K).argmax()); exact = False; break
        score = (Cf @ (ro & sub).astype(np.float32)) + 0.5 * tot / max(1.0, tot.max()) + rng.random(len(tot)) * 0.01
        if prop is not None:
            agree = Cf @ (np.eye(K, dtype=np.float32)[prop] * (rem & ~obs)[:, None]); score = score + lam * agree[np.arange(len(bc)), bc]
        score[~pure] = -1; j = int(score.argmax()); pred[rem & Cb[j]] = bc[j]; rem &= ~Cb[j]; nr += 1
    return pred, nr, exact


def net_fit(X1, y, obs, K, seed, steps=300):
    torch.manual_seed(seed); d = X1.shape[1]; m = torch.nn.Sequential(torch.nn.Linear(d, 64), torch.nn.ReLU(), torch.nn.Linear(64, 64), torch.nn.ReLU(), torch.nn.Linear(64, K))
    opt = torch.optim.Adam(m.parameters(), lr=0.01); xo, yo = torch.tensor(X1[obs]), torch.tensor(y[obs])
    for _ in range(steps): loss = torch.nn.functional.cross_entropy(m(xo), yo); opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad(): return m(torch.tensor(X1)).argmax(1).numpy()


def committee(preds, K):
    votes = np.stack([(preds == k).sum(0) for k in range(K)], 1); return votes.argmax(1), votes.max(1) == len(preds), 1.0 - votes.max(1) / len(preds)


def learners(name, C, X1, y, obs, K, rng, seed):
    out = {}; Cf, Cb = C
    P = [fit_list(Cf, Cb, y, obs, K, rng) for _ in range(7)]; g, u, dis = committee(np.stack([p[0] for p in P]), K)
    out["program"] = (g, u, dis, {"rules_median": float(np.median([p[1] for p in P])), "lists_that_reproduce_the_evidence": int(sum(p[2] for p in P))})
    N = np.stack([net_fit(X1, y, obs, K, seed * 100 + i) for i in range(5)]); gn, un, dn = committee(N, K); out["net"] = (gn, un, dn, {})
    P2 = [fit_list(Cf, Cb, y, obs, K, rng, prop=gn) for _ in range(7)]; g2, u2, d2 = committee(np.stack([p[0] for p in P2]), K)
    out["program+net"] = (g2, u2, d2, {"rules_median": float(np.median([p[1] for p in P2])), "lists_that_reproduce_the_evidence": int(sum(p[2] for p in P2))})
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    t = DecisionTreeClassifier(random_state=seed).fit(X1[obs], y[obs]).predict(X1); out["tree"] = (t, np.ones(len(y), bool), np.zeros(len(y)), {})
    rf = RandomForestClassifier(50, random_state=seed).fit(X1[obs], y[obs]); F = np.stack([e.predict(X1).astype(int) for e in rf.estimators_]); F = rf.classes_[F] if F.max() < len(rf.classes_) else F
    gf, uf, df = committee(F, K); out["forest"] = (gf, uf, df, {})
    maj = int(np.bincount(y[obs], minlength=K).argmax()); gi = np.where(obs, y, maj); out["index"] = (gi, obs.copy(), (~obs).astype(float), {})
    return out


def run(name, tests, seeds, max_budget):
    X, y, card = load(name); n, K = len(y), int(y.max()) + 1; t0 = time.time(); Cb = conditions(X, card, tests); Cf = Cb.astype(np.float32)
    X1 = np.concatenate([np.eye(k, dtype=np.float32)[X[:, a]] for a, k in enumerate(card)], 1)
    budgets = []; b = 16
    while b < min(n, max_budget): budgets.append(b); b *= 2
    budgets.append(min(n, max_budget))
    res = {"dataset": name, "cases": n, "attributes": card, "decisions": K, "tests_per_rule": tests, "conditions": int(len(Cb)), "budgets": budgets, "seeds": seeds, "curves": {}, "majority_share": float(np.bincount(y).max() / n)}
    for mode in ("passive", "chosen"):
        for arm in ("program", "program+net", "net", "tree", "forest", "index"): res["curves"][f"{mode}/{arm}"] = [[] for _ in budgets]
        for seed in range(1, seeds + 1):
            rng = np.random.default_rng(1000 * seed + (mode == "chosen")); order = rng.permutation(n)
            obs_by = {arm: np.zeros(n, bool) for arm in ("program", "program+net", "net", "tree", "forest", "index")}
            for arm in obs_by: obs_by[arm][order[:budgets[0]]] = True
            for bi, B in enumerate(budgets):
                done = {}
                for arm in obs_by:
                    key = obs_by[arm].tobytes()
                    if key not in done: done[key] = learners(name, (Cf, Cb), X1, y, obs_by[arm], K, rng, seed)
                    g, u, dis, extra = done[key][arm]; obs = obs_by[arm]
                    res["curves"][f"{mode}/{arm}"][bi].append({"right_all": float((g == y).mean()), "right_unaudited": float((g[~obs] == y[~obs]).mean()) if (~obs).any() else 1.0,
                                                               "cautious_answered": float(u.mean()), "cautious_wrong": float((u & (g != y)).mean()), "cautious_abstained": float((~u).mean()), **extra})
                    if bi + 1 < len(budgets):                       # the next audits
                        need = budgets[bi + 1] - B; cand = np.flatnonzero(~obs)
                        if mode == "chosen" and arm != "index": pick = cand[np.argsort(-(dis[cand] + rng.random(len(cand)) * 1e-3))[:need]]
                        else: pick = rng.permutation(cand)[:need]
                        obs_by[arm] = obs.copy(); obs_by[arm][pick] = True
            print(name, mode, "seed", seed, {arm: [round(r[-1]["right_all"], 3) for r in res["curves"][f"{mode}/{arm}"]] for arm in ("program", "net", "tree")}, round(time.time() - t0), "s", flush=True)
    # summary: audits to reach 99% and 100% of all cases right (median over seeds; None = not reached)
    res["summary"] = {}
    for key, rows in res["curves"].items():
        def first(th):
            per = []
            for s in range(seeds):
                hit = [budgets[bi] for bi in range(len(budgets)) if rows[bi][s]["right_all"] >= th]; per.append(hit[0] if hit else None)
            return per
        res["summary"][key] = {"audits_to_99": first(0.99), "audits_to_100": first(1.0), "right_all_by_budget": [float(np.mean([r["right_all"] for r in rows[bi]])) for bi in range(len(budgets))],
                               "cautious_wrong_by_budget": [float(np.mean([r["cautious_wrong"] for r in rows[bi]])) for bi in range(len(budgets))],
                               "cautious_abstained_by_budget": [float(np.mean([r["cautious_abstained"] for r in rows[bi]])) for bi in range(len(budgets))]}
    res["seconds"] = round(time.time() - t0, 1); os.makedirs(os.path.join(ROOT, "results", "v05"), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, "results", "v05", f"{name}_t{tests}.json"), "w"), indent=1); return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dataset"); ap.add_argument("--tests", type=int, default=2); ap.add_argument("--seeds", type=int, default=5); ap.add_argument("--max-budget", type=int, default=4096)
    a = ap.parse_args(); torch.set_num_threads(1); r = run(a.dataset, a.tests, a.seeds, a.max_budget)
    print(a.dataset, "cases", r["cases"], "conditions", r["conditions"], {k: v["audits_to_99"] for k, v in r["summary"].items() if k.split("/")[1] in ("program", "net", "tree")}, r["seconds"], "s")
