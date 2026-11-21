"""Exploratory, written AFTER the hidden family's outputs were locked and its breakdown was revealed (not a frozen test).

Question: the frozen bank is all or nothing (an exact past table, or start again).  Does a learner that is handed the past
policies' decisions as INPUTS do better on policies that are variants of past ones?

    python -I v06/x_features.py FAMILY.json --shard I --of N      # writes results/v06/x_features_<name>_shard<I>.json
    python -I v06/x_features.py report NAME [REVEAL.tsv]          # tables -> results/v06/x_features_<name>.md

Arms, all on the same passive audits (one random order per policy and seed; budgets are prefixes of it):
  scratch   5 small networks on the case attributes (the harness's scratch learner, same code)
  feat      the same 5 networks, with one extra block of inputs: what every past policy decides for that case (one-hot)
  patch     the past table that agrees with most audits, with the audited cases overwritten; never falls back
  pick      holds out a fifth of the audits and uses whichever of patch, feat, scratch gets most of them right (ties in that order)
"""
import glob, hashlib, json, os, sys, time
from itertools import product
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "v05"))
BUDGETS = (4, 8, 16, 32, 64, 128, 256, 512); ARMS = ("scratch", "feat", "patch", "pick"); INF = float("inf")


def run(path, shard, of, seeds=3):
    import torch, blind as B
    torch.set_num_threads(1); fam = json.load(open(path)); card = fam["attributes"]; K = fam["decisions"]; t0 = time.time()
    X = np.array(list(product(*[range(k) for k in card]))); n = len(X); X1 = np.concatenate([np.eye(k, dtype=np.float32)[X[:, i]] for i, k in enumerate(card)], 1)
    tab = lambda i: np.frombuffer(fam["policies"][i].encode(), np.uint8) - 48
    P = np.unique(np.array([tab(i) for i in fam["past"]]), axis=0); past_set = {t.tobytes() for t in P}
    X2 = np.concatenate([X1] + [np.eye(K, dtype=np.float32)[t] for t in P], 1)
    new = {}
    for i in sorted(fam["new"]): new.setdefault(tab(i).tobytes(), []).append(i)
    new = sorted(new.items(), key=lambda kv: kv[1][0]); mine = [x for j, x in enumerate(new) if j % of == shard]; budgets = [b for b in BUDGETS if b < n] + [n]
    def net(Xin, y, obs, seed): return B.committee(np.stack([B.net_fit(Xin, y, obs, K, seed * 100 + i) for i in range(5)]), K)[:2]
    def patch(y, obs):
        j = int((P[:, obs] == y[obs][None]).sum(1).argmax()); g = P[j].astype(np.int64).copy(); g[obs] = y[obs]; return g, np.ones(n, bool)
    def base(arm, y, obs, seed): return net(X1, y, obs, seed) if arm == "scratch" else net(X2, y, obs, seed) if arm == "feat" else patch(y, obs)
    res = {"family": fam["name"], "cases": n, "past_distinct": int(len(P)), "inputs_scratch": int(X1.shape[1]), "inputs_feat": int(X2.shape[1]), "budgets": budgets, "seeds": seeds, "policies": []}
    for key, ids in mine:
        y = np.frombuffer(key, np.uint8).astype(np.int64); row = {"ids": ids, "rule_seen_among_past": key in past_set, "nearest_past_distance": int((P != y[None]).sum(1).min()), "curves": {a: [[] for _ in budgets] for a in ARMS}}
        for seed in range(1, seeds + 1):
            rng = np.random.default_rng(int(hashlib.sha256((ids[0] + "x_features" + str(seed)).encode()).hexdigest()[:8], 16)); order = rng.permutation(n)
            for bi, Bn in enumerate(budgets):
                obs = np.zeros(n, bool); obs[order[:Bn]] = True; val = order[:Bn][rng.permutation(Bn)[:max(1, Bn // 5)]]; tr = obs.copy(); tr[val] = False; got = {}
                for arm in ("scratch", "feat", "patch"): got[arm] = base(arm, y, obs, seed)
                best = None
                for cand in ("patch", "feat", "scratch"):
                    if cand == "patch": j = int((P[:, tr] == y[tr][None]).sum(1).argmax()); gg = P[j]          # without overwriting: the held-out cases must test the table itself
                    else: gg = base(cand, y, tr, seed)[0]
                    sc = float((gg[val] == y[val]).mean())
                    if best is None or sc > best[0]: best = (sc, cand)
                got["pick"] = got[best[1]]
                for arm in ARMS:
                    g, u = got[arm]; row["curves"][arm][bi].append({"right_all": float((g == y).mean()), "cautious_wrong": float((u & (g != y)).mean()), "cautious_abstained": float((~u).mean()), "used": best[1] if arm == "pick" else None})
        res["policies"].append(row); print(ids[0], row["nearest_past_distance"], {a: [round(float(np.mean([r["right_all"] for r in row["curves"][a][bi]])), 2) for bi in range(len(budgets))] for a in ARMS}, round(time.time() - t0), "s", flush=True)
    res["seconds"] = round(time.time() - t0, 1); json.dump(res, open(os.path.join(ROOT, "results", "v06", f"x_features_{fam['name']}_shard{shard}.json"), "w")); print("done", fam["name"], shard)


def report(name, reveal=None):
    sh = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "results", "v06", f"x_features_{name}_shard*.json")))]; pol = sorted([p for s in sh for p in s["policies"]], key=lambda p: p["ids"][0]); B = sh[0]["budgets"]
    rev = {l.split("\t")[0]: l.rstrip("\n").split("\t") for l in open(reveal).readlines()[1:]} if reveal else {}
    show = lambda v: "never" if v == INF else f"{v:g}"
    def a99(p, a, thr=0.99):
        per = []
        for s in range(len(p["curves"][a][0])):
            hit = [B[i] for i in range(len(B)) if p["curves"][a][i][s]["right_all"] >= thr]; per.append(hit[0] if hit else INF)
        return float(np.median(per))
    grp = lambda p: rev[p["ids"][0]][1] if rev else ("seen" if p["rule_seen_among_past"] else "novel")
    P = [f"# Exploratory: past policies as inputs, {name}", "", f"Written after the outputs were locked and the breakdown revealed. {len(pol)} new policies, {sh[0]['seeds']} seeds, passive audits, budgets {B}. Inputs: scratch {sh[0]['inputs_scratch']}, feat {sh[0]['inputs_feat']}.", ""]
    P += ["## Audits to 99% of cases right (median of seeds), per policy", "", "| Policy | Group | Shape | Distance to nearest past | scratch | feat | patch | pick |", "|---|---|---|---|---|---|---|---|"]
    for p in pol:
        i = p["ids"][0]; P.append(f"| {i} | {grp(p)} | {rev[i][2] if rev else ''} | {p['nearest_past_distance']} | " + " | ".join(show(a99(p, a)) for a in ARMS) + " |")
    groups = {}
    for p in pol: groups.setdefault(grp(p), []).append(p)
    if rev:
        for p in pol: groups.setdefault("shape: " + rev[p["ids"][0]][2], []).append(p)
    P += ["", "## By group: median audits to 99%; policies on which the learner needs fewer / same / more audits than scratch", "", "| Group | Policies | scratch | feat | patch | pick | feat vs scratch | pick vs scratch |", "|---|---|---|---|---|---|---|---|"]
    for gname, g in groups.items():
        cmp_ = lambda a: " / ".join(str(sum(f(a99(p, a), a99(p, "scratch")) for p in g)) for f in (lambda x, y: x < y, lambda x, y: x == y, lambda x, y: x > y))
        P.append(f"| {gname} | {len(g)} | " + " | ".join(show(float(np.median([a99(p, a) for p in g]))) for a in ARMS) + f" | {cmp_('feat')} | {cmp_('pick')} |")
    P += ["", "## Mean share of cases right at each budget (%)", "", "| Group | Learner | " + " | ".join(str(b) for b in B) + " |", "|---|---|" + "---|" * len(B)]
    for gname, g in groups.items():
        if gname.startswith("shape"): continue
        for a in ARMS: P.append(f"| {gname} | {a} | " + " | ".join(f"{100 * np.mean([r['right_all'] for p in g for r in p['curves'][a][i]]):.1f}" for i in range(len(B))) + " |")
    P += ["", "## Cautious mode, mean over budgets below the full table: wrong / abstained (%)", "", "| Group | scratch | feat | pick |", "|---|---|---|---|"]
    for gname, g in groups.items():
        if gname.startswith("shape"): continue
        P.append(f"| {gname} | " + " | ".join(f"{100 * np.mean([r['cautious_wrong'] for p in g for i in range(len(B) - 1) for r in p['curves'][a][i]]):.2f} / {100 * np.mean([r['cautious_abstained'] for p in g for i in range(len(B) - 1) for r in p['curves'][a][i]]):.1f}" for a in ("scratch", "feat", "pick")) + " |")
    used = {}
    for p in pol:
        for i in range(len(B)):
            for r in p["curves"]["pick"][i]: used[r["used"]] = used.get(r["used"], 0) + 1
    P += ["", "Pick used: " + ", ".join(f"{k} {100 * v / sum(used.values()):.0f}%" for k, v in sorted(used.items(), key=lambda kv: -kv[1])) + "."]
    open(os.path.join(ROOT, "results", "v06", f"x_features_{name}.md"), "w").write("\n".join(P) + "\n"); print("\n".join(P))


if __name__ == "__main__":
    if sys.argv[1] == "report": report(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else: run(sys.argv[1], int(sys.argv[sys.argv.index("--shard") + 1]) if "--shard" in sys.argv else 0, int(sys.argv[sys.argv.index("--of") + 1]) if "--of" in sys.argv else 1)
