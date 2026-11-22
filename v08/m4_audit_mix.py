"""Milestone 4, the prediction from v0.6 round 2: after an exception is found, does spending a small share of the
remaining audits away from it reduce interim regressions while keeping local learning fast?

    python v08/m4_audit_mix.py dev | final [--codex FAMILY.json]

The learner is the frozen `amend` level of v0.6 round 2 (copied from v06/family2.py at commit 6cc1613, unchanged): the
past table that agrees with most random audits, with local exceptions; an unaudited case takes an exception's decision
when more of its audited neighbours are exceptions than agree with the table.  Only the choice of the next audits
varies, at the same budget:
  local    as frozen: every new audit goes to an unaudited neighbour of a known exception while there is one
  random   every audit at random
  mix f    a share f of each batch of new audits is drawn at random, the rest go to neighbours of exceptions
Policies are new here: amended copies of generated past tables (dev: seed 1, final: seed 2), local amendments (a box
of cases) and scattered ones (the same number of cases at random).  The share f is chosen on dev only, by this rule fixed before the
final set is run: among the strategies whose median audits to every case right is no higher than `local` for each size
of local amendment, take the one with the smallest mean shortfall on local amendments.
Writes results/v08/m4_audit_mix_<set>.json and .md."""
import hashlib, json, os, sys
from itertools import product
import numpy as np

CARD = [5, 5, 4, 4, 4]; K = 4; BUDGETS = (4, 8, 16, 32, 64, 128, 256, 512, 724, 1024, 1600); STRATS = [("local", 0.0), ("mix 0.1", 0.1), ("mix 0.2", 0.2), ("mix 0.3", 0.3), ("mix 0.5", 0.5), ("random", 1.0)]; SEEDS = 5
X = np.array(list(product(*[range(k) for k in CARD]))); n = len(X); NEAR = (X[:, None, :] != X[None, :, :]).sum(2) <= 1


def family(seed, n_past=36):
    """Generated past tables (a lookup on two attributes, shifted by a third on part of its range) and their amended copies."""
    rng = np.random.default_rng(seed); P = []
    for _ in range(n_past):
        a, b, c = rng.choice(5, 3, replace=False); lut = rng.integers(0, K, (CARD[a], CARD[b])); bump = rng.integers(0, 2, CARD[c]) * rng.integers(0, 2); P.append((lut[X[:, a], X[:, b]] + bump[X[:, c]]) % K)
    P = np.unique(np.array(P), axis=0); new = []
    for size, lo, hi in (("small", 4, 16), ("medium", 40, 80), ("large", 160, 240)):
        for rep in range(4):
            base = P[rng.integers(len(P))]
            while True:                                        # a box: a subset of values on every attribute
                sub = [rng.choice(k, rng.integers(1, k + 1), replace=False) for k in CARD]; box = np.all([np.isin(X[:, i], s) for i, s in enumerate(sub)], 0)
                if lo <= box.sum() <= hi: break
            y = base.copy(); y[box] = (y[box] + rng.integers(1, K)) % K; new.append({"kind": "local", "size": size, "changed": int(box.sum()), "y": y})
            if rep < 2: s = rng.choice(n, int(box.sum()), replace=False); y2 = base.copy(); y2[s] = (y2[s] + rng.integers(1, K, len(s))) % K; new.append({"kind": "scattered", "size": size, "changed": int(len(s)), "y": y2})
    return P, new


def amend(P, y, obs, rnd):                                     # v06/family2.py, frozen at 6cc1613
    agree = (P[:, rnd] == y[rnd][None]).sum(1); top = P[agree == agree.max()]; votes = np.stack([(top == k).sum(0) for k in range(K)], 1); g = votes.argmax(1).astype(np.int64); same = votes.max(1) == len(top)
    exc = obs & (y != g); ok = obs & (y == g); n_exc = NEAR[:, exc].sum(1); n_ok = NEAR[:, ok].sum(1); out = g.copy(); flip = (~obs) & (n_exc > n_ok)
    for c in np.flatnonzero(flip): out[c] = int(np.bincount(y[exc & NEAR[c]], minlength=K).argmax())
    out[obs] = y[obs]; sel = rnd & ((n_exc - exc.astype(int)) == 0); bound = float((int((exc & sel).sum()) + 3) / max(1, int(sel.sum())))
    return out, obs | (same & (n_exc == 0) & (bound <= 0.05)), float(agree.max() / max(1, rnd.sum())), n_exc


def run(P, y, f, seed, tag):
    rng = np.random.default_rng(int(hashlib.sha256(f"{tag}-{seed}".encode()).hexdigest()[:8], 16)); order = rng.permutation(n); act = np.zeros(n, bool); act[order[:BUDGETS[0]]] = True; rnd = act.copy(); curve = []
    for bi, b in enumerate(BUDGETS):
        out, u, agree, n_exc = amend(P, y, act, rnd); curve.append({"right": float((out == y).mean()), "exact": bool((out == y).all()), "answered": float(u.mean()), "wrong_answered": float((u & (out != y)).mean())})
        if bi + 1 < len(BUDGETS):
            need = BUDGETS[bi + 1] - b; cand = np.flatnonzero(~act); hunt = agree >= 0.85; pri = (n_exc[cand] if hunt else np.zeros(len(cand))) + rng.random(len(cand)) * 1e-3
            k_front = min(int(round((1 - f) * need)), int((pri >= 1).sum())); pick = list(cand[np.argsort(-pri)][:k_front]); more = list(rng.permutation(np.setdiff1d(cand, pick))[:need - k_front])
            act = act.copy(); act[pick + more] = True; rnd = rnd.copy(); rnd[more] = True
    return curve


def evaluate(P, new, tag):
    res = []
    for j, p in enumerate(new):
        old = 1 - p["changed"] / n
        for name, f in STRATS:
            for s in range(SEEDS):
                c = run(P, p["y"], f, s, f"{tag}-{j}"); first = lambda t: next((BUDGETS[i] for i, r in enumerate(c) if t(r)), None)
                res.append({"policy": j, "kind": p["kind"], "size": p["size"], "changed": p["changed"], "strategy": name, "seed": s, "old": old, "right": [r["right"] for r in c], "answered": [r["answered"] for r in c],
                            "wrong_answered": [r["wrong_answered"] for r in c], "to_exact": first(lambda r: r["exact"]), "to_99": first(lambda r: r["right"] >= 0.99)})
    return res


def table(res, title):
    M = [f"## {title}", "", "Regression = a budget below 1,600 at which fewer cases are right than by keeping the old table. Shortfall = mean over those budgets of the points below the old table (0 where not below).", "",
         "| Amendment | Strategy | Runs | Budgets with a regression % | Mean shortfall, points | Shortfall from 64 audits on | Worst cell from 64 audits on, points | Median audits to every case right | Median audits to 99% | Error among answered at 256 audits % |", "|---|---|---|---|---|---|---|---|---|"]; S = {}
    for kind in ("local", "scattered"):
        for name, _ in STRATS:
            r = [x for x in res if x["kind"] == kind and x["strategy"] == name]
            if not r: continue
            d = np.array([[100 * (v - x["old"]) for v in x["right"][:-1]] for x in r]); i256 = BUDGETS.index(256); ans = sum(x["answered"][i256] for x in r); err = 100 * sum(x["wrong_answered"][i256] for x in r) / max(1e-9, ans)
            i64 = BUDGETS.index(64); st = {"runs": len(r), "regression_pct": float(100 * (d < -1e-9).mean()), "shortfall": float(np.minimum(d, 0).mean() * -1), "shortfall_64": float(np.minimum(d[:, i64:], 0).mean() * -1), "worst": float(d[:, i64:].min()), "to_exact": float(np.median([x["to_exact"] or 1600 for x in r])),
                  "to_99": float(np.median([x["to_99"] or 1600 for x in r])), "error_answered_256": float(err)}; S[f"{kind}/{name}"] = st
            M.append(f"| {kind} | {name} | {st['runs']} | {st['regression_pct']:.1f} | {st['shortfall']:.3f} | {st['shortfall_64']:.3f} | {st['worst']:+.1f} | {st['to_exact']:g} | {st['to_99']:g} | {st['error_answered_256']:.2f} |")
    M += ["", "### Local amendments by size: mean shortfall, points / median audits to every case right", "", "| Size | " + " | ".join(nm for nm, _ in STRATS) + " |", "|---|" + "---|" * len(STRATS)]
    for size in ("small", "medium", "large"):
        row = []
        for name, _ in STRATS:
            r = [x for x in res if x["kind"] == "local" and x["size"] == size and x["strategy"] == name]
            if r: d = np.array([[100 * (v - x["old"]) for v in x["right"][:-1]] for x in r]); row.append(f"{np.minimum(d, 0).mean() * -1:.3f} / {np.median([x['to_exact'] or 1600 for x in r]):g}")
        if row: M.append(f"| {size} | " + " | ".join(row) + " |")
    return M, S


if __name__ == "__main__":
    which = sys.argv[1]; P, new = family(1 if which == "dev" else 2); res = evaluate(P, new, which); M, S = table(res, f"Generated family, {which} (seed {1 if which == 'dev' else 2}): {sum(p['kind'] == 'local' for p in new)} local and {sum(p['kind'] == 'scattered' for p in new)} scattered amendments, {SEEDS} seeds")
    loc = lambda nm, size: np.median([x["to_exact"] or 1600 for x in res if x["kind"] == "local" and x["size"] == size and x["strategy"] == nm])
    okay = [nm for nm, _ in STRATS if all(loc(nm, z) <= loc("local", z) for z in ("small", "medium", "large"))]; chosen = min(okay, key=lambda nm: S[f"local/{nm}"]["shortfall"])
    M += ["", f"Selection rule applied to this set: strategies as fast as `local` on every size: {', '.join(okay)}; smallest shortfall among them: **{chosen}**." + ("" if which == "dev" else " (For the record only: the share was chosen on dev.)")]
    out = {"set": which, "strategies": STRATS, "summary": S, "selected_by_rule_on_this_set": chosen, "runs": res}
    if "--codex" in sys.argv:                                  # the spent hidden family of round 2, holder's labels; reported apart
        fam = json.load(open(sys.argv[sys.argv.index("--codex") + 1])); tab = lambda i: np.frombuffer(fam["policies"][i].encode(), np.uint8).astype(np.int64) - 48; Pc = np.unique(np.array([tab(i) for i in fam["past"]]), axis=0)
        lab = {**{i: "local" for i in "p037 p040 p041 p043 p052 p055 p059 p061".split()}, **{i: "scattered" for i in "p047 p049 p057 p058".split()}}
        newc = [{"kind": k, "size": "small" if d <= 16 else "medium" if d <= 80 else "large", "changed": int(d), "y": tab(i)} for i, k in lab.items() for d in [int((Pc != tab(i)[None]).sum(1).min())]]
        rc = evaluate(Pc, newc, "codex2"); M2, S2 = table(rc, "Codex's second hidden family (spent; holder's labels): 8 local and 4 scattered amendments"); M += [""] + M2; out["codex2_summary"] = S2; out["codex2_runs"] = rc
    os.makedirs("results/v08", exist_ok=True); json.dump(out, open(f"results/v08/m4_audit_mix_{which}.json", "w")); open(f"results/v08/m4_audit_mix_{which}.md", "w").write("\n".join([f"# Audit mixing, {which}", ""] + M) + "\n"); print("\n".join(M))
