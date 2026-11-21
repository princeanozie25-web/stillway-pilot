"""v0.6 round 2: a bank with three levels of reuse.  Spec: docs/v06r2_spec.md.

    python -I v06/family2.py FAMILY.json [--shard I --of N] [--seeds 3]      # writes results/v06r2/<name>_shard<I>.json

Learners (passive audits unless stated: one random order per new policy and seed, budgets are prefixes of it)
  scratch     5 small networks on the case attributes; no experience (unchanged from v0.6)
  recognise   level 1: the past tables that agree with every audit; None when there is none
  amend       level 2: the past table (or tables) that agree with most audits, with local exceptions.  An audit that
              contradicts the table is an exception; an unaudited case takes an exception's decision when more of its audited
              neighbours (cases that differ in at most one attribute) are exceptions than agree with the table.  No network.
              Cautious: answers only where the best tables agree and no audited exception is a neighbour.
  parts       level 3: 5 small networks whose inputs are the attributes plus what every past policy decides for the case
  bank3       the bank.  A table level is used only on evidence: recognise when some past table agrees with every audit; amend
              when the best table agrees with at least 60% of the random audits and at least one audit contradicts it.  With
              fewer than 20 audits an eligible table level is used as it is.  From 20 on, a fifth of the random audits is held
              out, and the better of scratch and parts replaces the table level only if it beats it by a margin: two standard
              errors for recognise and for a table that holds on 85% or more of the audits, shrinking to nothing at 60%.  With no eligible table level the better of scratch and parts is used.
              Cautious mode: an answer for an unaudited case is given only when the residual bound of the level in use is at most
              5%.  For a table: (exceptions found + 3) / (random audits looked at), counted over audits with no other audited
              exception next to them; with no exception at all that needs 60 audits.  For a network: (held-out errors among
              its unanimous answers + 3) / (held-out unanimous answers).
  bank3a      the same bank choosing its audits.  While several past tables still fit every audit, the next audits go to the cases
              where those tables disagree.  While amend is in use on a table that holds on at least 85% of the random audits,
              they go first to the unaudited neighbours of the exceptions found so far.  The rest are random.
              This is the system under test.
Best guess = majority.  Cautious = answer only when every candidate or committee member agrees.
Also recorded for the bank at each budget: the level it used and, for levels 1 and 2, the residual bound.
"""
import argparse, hashlib, json, os, sys, time
from itertools import product
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "v05"))
import blind as B

BUDGETS = (4, 8, 16, 32, 64, 128, 256, 512, 724, 1024); ARMS = ("scratch", "recognise", "amend", "parts", "bank3", "bank3a", "index")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("family"); ap.add_argument("--shard", type=int, default=0); ap.add_argument("--of", type=int, default=1); ap.add_argument("--seeds", type=int, default=3); a = ap.parse_args()
    torch.set_num_threads(1); fam = json.load(open(a.family)); card = fam["attributes"]; K = fam["decisions"]; t0 = time.time()
    X = np.array(list(product(*[range(k) for k in card]))); n = len(X); X1 = np.concatenate([np.eye(k, dtype=np.float32)[X[:, i]] for i, k in enumerate(card)], 1)
    tab = lambda i: np.frombuffer(fam["policies"][i].encode(), np.uint8) - 48
    P = np.unique(np.array([tab(i) for i in fam["past"]]), axis=0); eye = np.eye(K, dtype=np.float32); X2 = np.concatenate([X1] + [eye[t] for t in P], 1)
    NEAR = (X[:, None, :] != X[None, :, :]).sum(2) <= 1                          # cases that differ in at most one attribute (a case is its own neighbour)
    new = {}
    for i in sorted(fam["new"]): new.setdefault(tab(i).tobytes(), []).append(i)
    new = sorted(new.items(), key=lambda kv: kv[1][0]); mine = [x for j, x in enumerate(new) if j % a.of == a.shard]; budgets = [b for b in BUDGETS if b < n] + [n]

    def amend(y, obs, rnd):
        """rnd marks the audits that were drawn at random; only they are used to pick the table and to estimate how much of it holds."""
        agree = (P[:, rnd] == y[rnd][None]).sum(1); top = P[agree == agree.max()]; votes = np.stack([(top == k).sum(0) for k in range(K)], 1); g = votes.argmax(1).astype(np.int64); same = votes.max(1) == len(top)
        exc = obs & (y != g); ok = obs & (y == g); n_exc = NEAR[:, exc].sum(1); n_ok = NEAR[:, ok].sum(1); out = g.copy(); flip = (~obs) & (n_exc > n_ok)
        for c in np.flatnonzero(flip): out[c] = int(np.bincount(y[exc & NEAR[c]], minlength=K).argmax())
        out[obs] = y[obs]
        # how often is a case with no (other) audited exception next to it an exception itself?  95%-style upper bound: (found + 3) / looked at
        sel = rnd & ((n_exc - exc.astype(int)) == 0); bound = float((int((exc & sel).sum()) + 3) / max(1, int(sel.sum())))
        return out, obs | (same & (n_exc == 0) & (bound <= 0.05)), {"audited_agreement_with_table": float(agree.max() / max(1, rnd.sum())), "exceptions_audited": int(exc.sum()), "answers_changed_from_table": int((out != g).sum()), "tables_tied": int(len(top)), "residual_bound": bound}, n_exc

    def base(arm, y, obs, rnd, seed):
        """-> (guess, answers given in cautious mode, info) or None"""
        if arm == "scratch": return B.committee(np.stack([B.net_fit(X1, y, obs, K, seed * 100 + i) for i in range(5)]), K)[:2] + ({},)
        if arm == "parts": return B.committee(np.stack([B.net_fit(X2, y, obs, K, seed * 100 + i) for i in range(5)]), K)[:2] + ({},)
        if arm == "recognise":
            ok = P[(P[:, obs] == y[obs][None]).all(1)]
            if len(ok) == 0: return None
            votes = np.stack([(ok == k).sum(0) for k in range(K)], 1); return votes.argmax(1), votes.max(1) == len(ok), {"consistent_tables": int(len(ok))}
        if arm == "amend": return amend(y, obs, rnd)[:3]

    def bank(y, obs, rnd, seed, rng):
        """All four levels on these audits, and the level in use.
        A table level is used only on evidence: recognise when some past table agrees with every audit; amend when the best table agrees with at
        least 60% of the random audits and at least one audit contradicts it.  With fewer than 20 audits an eligible table level is used as it is.
        From 20 audits on, a fifth of the random audits is held out: the better of scratch and parts replaces the table level only if it beats it
        by a margin: two standard errors for recognise and for a table that holds on 85% or more of the audits, shrinking to nothing at 60%.  With no eligible table level the better of scratch and parts is used (ties: scratch).
        Cautious mode: an answer for an unaudited case is given only when the residual bound of the level in use is at most 5%."""
        ridx = np.flatnonzero(rnd); val = rng.permutation(ridx)[:max(1, len(ridx) // 5)]; tr = obs.copy(); tr[val] = False; got = {arm: base(arm, y, obs, rnd, seed) for arm in ("scratch", "recognise", "amend", "parts")}
        am = got["amend"][2]; table = "recognise" if got["recognise"] is not None else "amend" if (am["audited_agreement_with_table"] >= 0.6 and am["exceptions_audited"] > 0) else None; elig = ([table] if table else []) + ["scratch", "parts"]
        held = {}
        if not (table and obs.sum() < 20):
            for cand in elig:
                r = base(cand, y, tr, rnd & tr, seed)
                if r is not None: held[cand] = (float((r[0][val] == y[val]).mean()), r)
        if table and (obs.sum() < 20 or table not in held): use = table
        else:
            net = max(("scratch", "parts"), key=lambda c: (held[c][0], c == "scratch")); use = net
            if table:                                    # a network displaces the table only when clearly better on the held-out audits
                pt, pn, m = held[table][0], held[net][0], len(val); w = 1.0 if table == "recognise" else float(np.clip((am["audited_agreement_with_table"] - 0.6) / 0.25, 0, 1))
                use = net if pn - pt > 2 * w * np.sqrt(max(pt * (1 - pt), pn * (1 - pn), 1e-9) / m) else table
        g, u, info = got[use]; info = dict(info, used=use, eligible=elig, residual_bound=None)
        if use in ("recognise", "amend"):
            info["residual_bound"] = am["residual_bound"]
            if use == "recognise" and am["residual_bound"] > 0.05: u = obs.copy()
        else:                                             # a network's unanimous answers count in cautious mode only if they held up on the held-out audits
            gv, uv, _ = held[use][1]; m = int(uv[val].sum()); k = int((uv[val] & (gv[val] != y[val])).sum()); info["residual_bound"] = float((k + 3) / max(1, m))
            if info["residual_bound"] > 0.05: u = obs.copy()
        got["bank"] = (g, u, info); return got

    res = {"family": fam["name"], "cases": n, "attributes": card, "decisions": K, "past_distinct": int(len(P)), "new_distinct": len(new), "budgets": budgets, "seeds": a.seeds, "policies": []}
    for key, ids in mine:
        y = np.frombuffer(key, np.uint8).astype(np.int64); d = (P != y[None]).sum(1); row = {"ids": ids, "nearest_past_distance": int(d.min()), "curves": {arm: [[] for _ in budgets] for arm in ARMS}}
        def put(arm, bi, r, obs):
            if r is None: row["curves"][arm][bi].append(None); return
            g, u, info = r; row["curves"][arm][bi].append(dict(info, right_all=float((g == y).mean()), exact=bool((g == y).all()), cautious_wrong=float((u & (g != y)).mean()), cautious_abstained=float((~u).mean())))
        for seed in range(1, a.seeds + 1):
            rng = np.random.default_rng(int(hashlib.sha256((ids[0] + "family2" + str(seed)).encode()).hexdigest()[:8], 16)); order = rng.permutation(n); act = np.zeros(n, bool); act[order[:budgets[0]]] = True; act_rnd = act.copy()
            for bi, Bn in enumerate(budgets):
                obs = np.zeros(n, bool); obs[order[:Bn]] = True; got = bank(y, obs, obs, seed, rng)
                for arm in ("scratch", "recognise", "amend", "parts"): put(arm, bi, got[arm], obs)
                put("bank3", bi, got["bank"], obs); maj = int(np.bincount(y[obs], minlength=K).argmax()); put("index", bi, (np.where(obs, y, maj), obs.copy(), {}), obs)
                ga = bank(y, act, act_rnd, seed, rng); put("bank3a", bi, ga["bank"], act)
                if bi + 1 < len(budgets):       # the next audits: while amend is in use on a table that mostly holds, the neighbours of known exceptions first
                    need = budgets[bi + 1] - Bn; info = ga["bank"][2]; hunt = info["used"] == "amend" and info["audited_agreement_with_table"] >= 0.85
                    n_exc = amend(y, act, act_rnd)[3].astype(float) if hunt else np.zeros(n)
                    if info["used"] == "recognise" and info["consistent_tables"] > 1:      # several past tables still fit: audit where they disagree
                        okt = P[(P[:, act] == y[act][None]).all(1)]; n_exc = 1.0 - np.stack([(okt == k).sum(0) for k in range(K)], 1).max(1) / len(okt)
                    cand = np.flatnonzero(~act); pri = n_exc[cand] + rng.random(len(cand)) * 1e-3
                    front = cand[np.argsort(-pri)]; k_front = min(need, int((n_exc[cand] > 0).sum())); pick = list(front[:k_front]); rest = np.setdiff1d(cand, pick); more = list(rng.permutation(rest)[:need - k_front])
                    act = act.copy(); act[pick + more] = True; act_rnd = act_rnd.copy(); act_rnd[more] = True
        res["policies"].append(row)
        print(ids[0], row["nearest_past_distance"], {arm: [round(float(np.mean([r["right_all"] for r in row["curves"][arm][bi] if r])), 2) if any(row["curves"][arm][bi]) else None for bi in range(len(budgets))] for arm in ("scratch", "amend", "bank3", "bank3a")}, round(time.time() - t0), "s", flush=True)
    res["seconds"] = round(time.time() - t0, 1); os.makedirs(os.path.join(ROOT, "results", "v06r2"), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, "results", "v06r2", f"{fam['name']}_shard{a.shard}.json"), "w")); print("done", fam["name"], "shard", a.shard, len(mine), "new policies", res["seconds"], "s")


if __name__ == "__main__": main()
