"""Sessions and sleep (v0.4, M3).  Protocol and arms: docs/v04_spec.md section 3.

    python -m stillway4.sleep runs/v4a_proc_s_s1 --seed 1        # writes results/v04/m3/<name>.json and bank files

The core (router, procedure codes, status function) is frozen.  What changes between sessions is the policy bank:
one row per policy ID, plus a registry (policy ID -> row, or EXPIRED) and, for the retrieval arm, an index.

Six sessions.  Odd sessions change tenant 0 only, even sessions tenant 1 only, so the other tenant is a probe for
interference.  A session brings 3 new policy IDs (half from reserved rules) and expires one earlier policy.
During the session ("wake") 120 documents arrive; their audited outcomes are logged as decision records
(policy ID, facts, status), operator overrides kept apart.  Then each arm updates ("sleep"), then fresh documents
are scored:  learn (the session's new policies), learn_unseen (decisions whose facts never occurred in that policy's
log), retain (older active policies, both tenants), expired (documents that name the expired ID), and interference
(decisions on the untouched tenant's fixed probe documents that changed across the sleep).

Arms
  none           the base bank; unknown IDs abstain
  retrieval      + an index of audited decisions (latest outcome per policy ID and facts); no row is trained
  retrieval_naive  the same index fed with operator overrides too (shows what provenance is for)
  rehearsal      one table, every row trainable, trained in place on a replay of all decision records
  consolidation  candidate rows for the session's new IDs, trained with every old row frozen; validated on held-out
                 records of the session; promoted or discarded; expiry is a registry change; versioned
  dreaming       consolidation plus dream cases: fact combinations the log lacks, labelled by randomly chosen existing
                 experts, kept only when every family rule consistent with the log gives that label
  induction      non-neural: the family rules consistent with the log; answers only where they agree
  rehearsal_core (ablation) rehearsal that also trains the status function
Update steps are equal: STEPS full-batch steps per new policy ID in every trained arm.
"""
from __future__ import annotations

import argparse, copy, hashlib, io, json, os, sys, time

import numpy as np
import torch
import torch.nn.functional as F

from . import approvals as A
from .arms import evaluate, load, make_data, sub

N_SESS, N_WAKE, N_EVAL, NEW_PER, STEPS, VAL_MIN = 6, 120, 600, 3, 200, 0.95
FO = torch.cat([F.one_hot(A.ALL_FACTS[:, 0], 4), F.one_hot(A.ALL_FACTS[:, 1], 2), F.one_hot(A.ALL_FACTS[:, 2], 3), F.one_hot(A.ALL_FACTS[:, 3], 2)], 1).float()     # (36,11)
RULE_TABLE = torch.stack([A.status_fn(torch.full((36,), r), A.ALL_FACTS[:, 0], A.ALL_FACTS[:, 1], A.ALL_FACTS[:, 2], A.ALL_FACTS[:, 3]) for r in range(36)])           # (36 rules, 36 facts)


def version_space(fact, status):
    """Family rules consistent with a policy's decision records; and, per fact combination, the label they all give (-1 if they disagree).
    All-ABSTAIN records with no consistent rule mean the EXPIRED policy."""
    if len(fact) == 0: return torch.ones(36, dtype=torch.bool), torch.full((36,), -1)
    ok = (RULE_TABLE[:, fact] == status[None]).all(1)
    if not ok.any(): return ok, (torch.full((36,), A.ABSTAIN) if (status == A.ABSTAIN).all() else torch.full((36,), -1))
    t = RULE_TABLE[ok]; agree = (t == t[0:1]).all(0)
    return ok, torch.where(agree, t[0], -1)


def expand(weight, n_rows, gen):
    """Bank with room for policy IDs up to n_rows - 2; the last row stays "no policy named"."""
    w = torch.zeros(n_rows, weight.shape[1]); k = weight.shape[0] - 1; w[:k] = weight[:k]; w[-1] = weight[-1]
    w[k:-1] = torch.randn(n_rows - 1 - k, weight.shape[1], generator=gen) * weight[1:k].std()
    return w


def fit_rows(model, W, rows, rec, steps, lr=0.05, train_expert=False):  # train_expert: the ablation that also trains the status function
    """Train the given bank rows (others frozen) on decision records {"pid","fact","status"}.  Full batch."""
    if len(rec["pid"]) == 0 or steps == 0: return W
    Wp = torch.nn.Parameter(W.clone()); mask = torch.zeros(W.shape[0], 1); mask[rows] = 1.0
    opt = torch.optim.Adam([{"params": [Wp], "lr": lr}] + ([{"params": list(model.expert.parameters()), "lr": 1e-3}] if train_expert else []))
    for _ in range(steps):
        lg = model.expert(torch.cat([Wp[rec["pid"]], FO[rec["fact"]]], 1)); loss = F.cross_entropy(lg, rec["status"])
        opt.zero_grad(); loss.backward(); Wp.grad.mul_(mask); opt.step()
    return Wp.detach()


@torch.no_grad()
def row_table(model, W, row):
    return model.expert(torch.cat([W[row][None].expand(36, -1), FO], 1)).argmax(1)


def cat_rec(a, b): return {k: torch.cat([a[k], b[k]]) for k in ("pid", "fact", "status")}
def sel_rec(r, m): return {k: r[k][m] for k in ("pid", "fact", "status")}
EMPTY = {"pid": torch.zeros(0, dtype=torch.long), "fact": torch.zeros(0, dtype=torch.long), "status": torch.zeros(0, dtype=torch.long)}


def run(core_path: str, seed: int, out_dir: str, log=print, salt: int = 0) -> dict:
    torch.set_num_threads(1); base = load(core_path); gen = torch.Generator().manual_seed(7919 * seed + 4 + salt)
    uni, _ = make_data(seed, salt=salt); n_base = len(uni.pid_rule) - 1; R = n_base + 1 + N_SESS * NEW_PER + 1                    # rows: EXPIRED, base IDs, new IDs, "none"
    W0 = expand(base.bank.weight.detach(), R, gen); ident = torch.arange(R)
    active = {t: [int(p) for p in (uni.pid_tenant == t).nonzero().squeeze(1)[torch.randperm(n_base // 2, generator=gen)[:8]]] for t in (0, 1)}
    arms = ["none", "retrieval", "retrieval_naive", "rehearsal", "consolidation", "dreaming", "induction", "rehearsal_core"]
    st = {a: {"W": W0.clone(), "rowmap": ident.clone(), "unknown": torch.zeros(R, dtype=torch.bool), "lookup": None, "model": base} for a in arms}
    for a in arms: st[a]["unknown"][n_base + 1:R - 1] = a not in ("rehearsal", "rehearsal_core")                       # rows never trained are unknown, except in the in-place table
    for a in ("retrieval", "retrieval_naive", "induction"): st[a]["lookup"] = torch.full((R, 36), -1)
    st["rehearsal_core"]["model"] = copy.deepcopy(base)
    all_rec = EMPTY; reh_rec = EMPTY; status = {a: {} for a in ("consolidation", "dreaming")}; steps_used = {a: 0 for a in arms}; res = {"core": core_path, "seed": seed, "sessions": [], "arms": arms, "bank_versions": {}}; os.makedirs(out_dir, exist_ok=True)
    kw = lambda a: dict(bank_weight=st[a]["W"], rowmap=st[a]["rowmap"], unknown=st[a]["unknown"], lookup=st[a]["lookup"])
    raw = {}; cur = {"k": 0}
    def score(a, d, mask_fn=None, tag=None):
        e = evaluate(st[a]["model"], d, **kw(a))
        if tag is not None:
            raw[f"s{cur['k']}_{tag}_{a}_out"] = e["outputs"].numpy().astype(np.int8)
            if f"s{cur['k']}_{tag}_events" not in raw:
                raw[f"s{cur['k']}_{tag}_events"] = torch.stack([d["ev_" + f] for f in A.FIELDS], -1).numpy().astype(np.int16); raw[f"s{cur['k']}_pid_rule"] = uni.pid_rule.numpy().astype(np.int16)
                raw[f"s{cur['k']}_{tag}_family"] = d["family"].numpy().astype(np.int16)
        o_ = None; o = {"documents": len(d["tenant"]), "success": e["success"], "status_accuracy": e["status_accuracy"], "protected_changed": e["protected_changed"]}
        if mask_fn is not None:
            m = mask_fn(d); o["decisions"] = int(m.sum()); o["decision_accuracy"] = float((e["outputs"][m] == d["labels"][m]).float().mean()) if m.any() else None
        return o, e["outputs"]
    for k in range(1, N_SESS + 1):
        ten = (k - 1) % 2; other = 1 - ten; t0 = time.time(); cur["k"] = k
        new = [uni.add(int(torch.tensor(A.RESERVED_RULES if i % 2 == 0 else A.TRAIN_RULES)[torch.randint(0, 8 if i % 2 == 0 else 28, (1,), generator=gen)]), ten) for i in range(NEW_PER)]
        expired = active[ten][int(torch.randint(0, len(active[ten]), (1,), generator=gen))]; old = {t: [p for p in active[t] if p != expired] for t in (0, 1)}
        uni.pid_rule[expired] = -1; active[ten] = old[ten] + new; act = {t: torch.tensor(active[t]) for t in (0, 1)}
        probe = A.sample_docs(uni, N_EVAL, gen, active={t: torch.tensor(old[t]) for t in (0, 1)}, combos="any", tenant=other)
        before = {a: score(a, probe)[1] for a in arms}
        wake = A.sample_docs(uni, N_WAKE, gen, active=act, combos="any"); wake_scores = {a: score(a, wake)[0] for a in arms}
        rec = A.decision_records(wake); srec = sel_rec(rec, torch.ones(len(rec["pid"]), dtype=torch.bool)); all_rec = cat_rec(all_rec, srec)
        nrec = {"pid": rec["override_pid"], "fact": rec["override_fact"], "status": rec["override_status"]}
        notice = {"pid": torch.full((36,), expired), "fact": torch.arange(36), "status": torch.full((36,), A.ABSTAIN)}     # the expiry notice, as records every arm receives
        reh_rec = cat_rec(cat_rec(sel_rec(reh_rec, reh_rec["pid"] != expired), srec), notice)                              # replay buffer: superseded records of the expired ID are dropped
        # ---- sleep ----
        info = {"session": k, "tenant_changed": ten, "new_ids": new, "new_rules": [int(uni.pid_rule[p]) for p in new], "expired_id": expired, "records_logged": len(srec["pid"]), "overrides_logged": len(rec["override_pid"])}
        sleep_sec = {}
        for a, src in (("retrieval", [srec, notice]), ("retrieval_naive", [srec, nrec, notice])):
            t1 = time.time()
            for r_ in src: st[a]["lookup"][r_["pid"], r_["fact"]] = r_["status"]                                             # latest outcome per key
            sleep_sec[a] = time.time() - t1
        t1 = time.time(); ind = st["induction"]["lookup"]; ind[expired] = A.ABSTAIN
        for p in set(srec["pid"].tolist()):
            if p > n_base:                                                                                                   # IDs introduced in a session: rules consistent with ALL their records
                m = all_rec["pid"] == p; _, lab = version_space(all_rec["fact"][m], all_rec["status"][m]); ind[p] = lab
        sleep_sec["induction"] = time.time() - t1
        dream_log = {}; n_cand = 0
        for a in ("consolidation", "dreaming"):
            t1 = time.time(); W = st[a]["W"].clone(); promoted, discarded, cands = [], [], list(new)
            st[a]["rowmap"][expired] = 0                                                                                    # the registry: an expired ID is the EXPIRED policy
            for p, s_ in status[a].items():                                                                                  # retry discarded candidates; re-consolidate promoted rows that a new record contradicts
                m = srec["pid"] == p
                if p == expired or not m.any(): continue
                if s_ == "discarded" or (row_table(base, W, p)[srec["fact"][m]] != srec["status"][m]).any(): cands.append(p)
            n_cand = max(n_cand, len(cands))
            for p in cands:
                m = (all_rec["pid"] == p).nonzero().squeeze(1); perm = m[torch.randperm(len(m), generator=gen)]; nv = max(1, len(perm) // 5) if len(perm) >= 5 else 0
                val, tr = sel_rec(all_rec, perm[:nv]), sel_rec(all_rec, perm[nv:])
                if a == "dreaming" and len(tr["pid"]):
                    _, entailed = version_space(tr["fact"], tr["status"]); seen = torch.zeros(36, dtype=torch.bool); seen[tr["fact"]] = True; cand = (~seen).nonzero().squeeze(1)
                    pool = torch.tensor([x for t in (0, 1) for x in old[t] if not st[a]["unknown"][x]])
                    donors = pool[torch.randint(0, len(pool), (3,), generator=gen)]                                          # randomly chosen existing experts propose labels
                    prop = torch.stack([row_table(base, W, int(dn))[cand] for dn in donors]) if len(cand) else torch.zeros(3, 0, dtype=torch.long)
                    keep = (prop == entailed[cand][None]) & (entailed[cand][None] >= 0); kept = keep.any(0)
                    dream_log[p] = {"fact_combinations_missing_from_log": int(len(cand)), "candidate_labels_proposed": int(prop.numel()), "candidates_confirmed": int(keep.sum()),
                                    "candidates_rejected": int(prop.numel() - keep.sum()), "dream_cases_kept": int(kept.sum())}
                    tr = cat_rec(tr, {"pid": torch.full((int(kept.sum()),), p), "fact": cand[kept], "status": entailed[cand][kept]})
                if len(tr["pid"]) == 0: discarded.append(p); status[a].setdefault(p, "discarded"); continue
                Wc = fit_rows(base, W, [p], tr, STEPS); steps_used[a] += STEPS
                acc = float((row_table(base, Wc, p)[val["fact"]] == val["status"]).float().mean()) if nv else 0.0
                old_acc = float((row_table(base, W, p)[val["fact"]] == val["status"]).float().mean()) if (nv and status[a].get(p) == "promoted") else -1.0
                if acc >= VAL_MIN and acc >= old_acc: W = Wc; promoted.append(p); status[a][p] = "promoted"
                else: discarded.append(p); status[a].setdefault(p, "discarded")
            st[a]["W"] = W
            for p in promoted: st[a]["unknown"][p] = False
            buf = io.BytesIO(); torch.save({"W": W, "rowmap": st[a]["rowmap"], "unknown": st[a]["unknown"]}, buf); data = buf.getvalue(); path = f"{out_dir}/bank_{a}_v{k}.pt"; open(path, "wb").write(data)
            res["bank_versions"][f"{a}_v{k}"] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "promoted": promoted, "discarded": discarded}
            info[f"{a}_promoted"], info[f"{a}_discarded"] = promoted, discarded; sleep_sec[a] = time.time() - t1
        for a in ("rehearsal", "rehearsal_core"):                                                                            # the same number of update steps as consolidation used this session
            t1 = time.time(); st[a]["W"] = fit_rows(st[a]["model"], st[a]["W"], list(range(R - 1)), reh_rec, STEPS * n_cand, train_expert=(a == "rehearsal_core")); steps_used[a] += STEPS * n_cand; sleep_sec[a] = time.time() - t1
        info["dreams"] = dream_log; info["sleep_seconds"] = {a: round(v, 4) for a, v in sleep_sec.items()}
        # ---- fresh documents after the sleep ----
        newt = torch.tensor(new); seen_key = torch.zeros(R, 36, dtype=torch.bool); seen_key[srec["pid"], srec["fact"]] = True
        d_learn = A.sample_docs(uni, N_EVAL, gen, active={ten: newt, other: act[other]}, combos="any", tenant=ten)
        d_ret = A.sample_docs(uni, N_EVAL, gen, active={t: torch.tensor(old[t]) for t in (0, 1)}, combos="any")
        d_exp = A.sample_docs(uni, N_EVAL, gen, active={ten: torch.tensor(old[ten][:2] + [expired]), other: act[other]}, combos="any", tenant=ten)
        def m_new(d): return d["affected"] & (d["facts"][..., 0] > 0) & torch.isin(d["pin"], newt) & (d["ev_kind"][:, :, None] != A.OVERRIDE)
        def m_unseen(d):
            f = d["facts"]; fi = A.fact_index(f[..., 0].clamp(min=1), f[..., 1], f[..., 2], f[..., 3]); return m_new(d) & ~seen_key[d["pin"].clamp(min=0), fi]
        def m_exp(d): return d["affected"] & (d["facts"][..., 0] > 0) & (d["pin"] == expired) & (d["ev_kind"][:, :, None] != A.OVERRIDE)
        sess = {**info, "wake": wake_scores, "arms": {}}
        for a in arms:
            sess["arms"][a] = {"learn": score(a, d_learn, m_new, "learn")[0], "learn_unseen": score(a, d_learn, m_unseen)[0], "retain": score(a, d_ret, None, "retain")[0], "expired": score(a, d_exp, m_exp, "expired")[0],
                               "probe_decisions": int(before[a].numel())}
            after = score(a, probe)[1]; sess["arms"][a]["interference_decisions_changed"] = int((after != before[a]).sum())
            sess["arms"][a]["interference_right_before_wrong_after"] = int(((before[a] == probe["labels"]) & (after != probe["labels"])).sum())
        res["sessions"].append(sess)
        torch.save({"arms": {a: {k_: (v_.clone() if torch.is_tensor(v_) else v_) for k_, v_ in st[a].items() if k_ != "model"} for a in arms}, "pid_rule": uni.pid_rule.clone(), "pid_tenant": uni.pid_tenant.clone(),
                    "active": {t: list(active[t]) for t in (0, 1)}, "old": old, "new": new, "expired": expired, "tenant_changed": ten, "seen_key": seen_key}, f"{out_dir}/snapshot_v{k}.pt")
        log(f"session {k}", {a: (round(sess['arms'][a]['learn']['decision_accuracy'], 3), round(sess['arms'][a]['learn_unseen']['decision_accuracy'] or 0, 3), round(sess['arms'][a]['retain']['success'], 3),
                                 round(sess['arms'][a]['expired']['decision_accuracy'] or 0, 3), sess['arms'][a]['interference_right_before_wrong_after']) for a in arms}, round(time.time() - t0, 1), "s")
    # ---- rollback and pinning: an older bank version still loads, hashes match, and gives its old answers ----
    v = torch.load(f"{out_dir}/bank_consolidation_v{N_SESS - 1}.pt", weights_only=True); e_old = evaluate(base, d_ret, bank_weight=v["W"], rowmap=v["rowmap"], unknown=v["unknown"])
    res["rollback"] = {"version_loaded": N_SESS - 1, "sha256_matches": hashlib.sha256(open(f"{out_dir}/bank_consolidation_v{N_SESS - 1}.pt", "rb").read()).hexdigest() == res["bank_versions"][f"consolidation_v{N_SESS - 1}"]["sha256"],
                       "retain_success_under_old_version": e_old["success"]}
    np.savez_compressed(f"{out_dir}/raw_outputs.npz", **raw)
    res["update_steps_used"] = steps_used
    res["index_entries"] = {a: int((st[a]["lookup"] >= 0).sum()) for a in ("retrieval", "retrieval_naive", "induction")}
    res["final_state"] = {a: {"rows_known": int((~st[a]["unknown"][1:R - 1]).sum())} for a in arms}
    torch.save({a: {k_: v_ for k_, v_ in st[a].items() if k_ != "model"} for a in arms}, f"{out_dir}/final_state.pt")
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("core"); ap.add_argument("--seed", type=int, default=1); ap.add_argument("--salt", type=int, default=-1); a = ap.parse_args()
    man = json.load(open(f"{a.core.rstrip('/')}/manifest.json")); salt = man["args"].get("salt", 0) if a.salt < 0 else a.salt
    name = os.path.basename(a.core.rstrip("/")); out = f"results/v04/m3/{name}"; res = run(f"{a.core.rstrip('/')}/checkpoint.pt", a.seed, out, salt=salt); res["salt"] = salt
    json.dump(res, open(f"results/v04/m3/{name}.json", "w"), indent=1); print("saved", f"results/v04/m3/{name}.json")


if __name__ == "__main__":
    main()
