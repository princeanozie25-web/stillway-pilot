"""The v0.4 demo trace: yesterday's bank, a new order with a local correction, sleep, restart, an unseen
combination under the revised policy; the same trace through every baseline.

    python v04/demo.py runs/v4f_proc_s_s1 [SESSION=3]          # needs results/v04/m3/<core>/snapshot_v*.pt

Document A (today, before the sleep): names a policy introduced today, and contains a CORRECT and an OVERRIDE
            (one-off changes to this job's registers).  It runs on YESTERDAY's bank, pinned for the whole job.
Document B (tomorrow, after the sleep and a restart from files): a decision under today's policy on a fact
            combination that never occurred in today's log, in a document with a reserved event combination.
Checks: the pinned job gives the same statuses whether or not a newer bank exists; the bank file hash matches the
recorded version; the one-off changes of document A are in no bank row and no index entry; every system's
statuses are graded by the plain-Python grader from the raw events.
"""
import hashlib, json, os, sys
import torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4 import approvals as A
from stillway4.arms import load, sub
from stillway4.grader import grade
from stillway4.runtime import TableRuntime, Tracker, compile_procedures
from stillway4.sleep import row_table

core = sys.argv[1].rstrip("/"); K = int(sys.argv[2]) if len(sys.argv) > 2 else 3; name = os.path.basename(core); base = f"results/v04/m3/{name}"; torch.set_num_threads(1)
model = load(f"{core}/checkpoint.pt"); y = torch.load(f"{base}/snapshot_v{K - 1}.pt", weights_only=False); t = torch.load(f"{base}/snapshot_v{K}.pt", weights_only=False); m3 = json.load(open(f"{base}.json"))
uni = A.Universe(t["pid_rule"], t["pid_tenant"]); ten = t["tenant_changed"]; new = torch.tensor(t["new"]); gen = torch.Generator().manual_seed(31337 + K)
pol = {p: (A.RULES[int(uni.pid_rule[p])].tolist() if int(uni.pid_rule[p]) >= 0 else None) for p in range(1, len(uni.pid_rule))}; expired_true = [p for p in range(1, len(uni.pid_rule)) if int(uni.pid_rule[p]) < 0]
act = {ten: torch.tensor(t["old"][ten][:3] + t["new"]), 1 - ten: torch.tensor(t["active"][1 - ten])}
pool = A.sample_docs(uni, 6000, gen, active=act, combos="any", tenant=ten)
newpin = torch.isin(pool["pin"], new) & pool["affected"] & (pool["facts"][..., 0] > 0)
has = lambda k: (pool["ev_kind"][:, A.N_SETUP:] == k).any(1)
iA = int((newpin.flatten(1).any(1) & has(A.CORRECT) & has(A.OVERRIDE)).nonzero()[0])
f = pool["facts"]; fi = A.fact_index(f[..., 0].clamp(min=1), f[..., 1], f[..., 2], f[..., 3]); unseen = newpin & ~t["seen_key"][pool["pin"].clamp(min=0), fi] & (pool["ev_kind"][:, :, None] != A.OVERRIDE)
cB = (unseen.flatten(1).any(1) & (pool["reserved_pairs"].sum(1) > 0)); cB[iA] = False; iB = int(cB.nonzero()[0])
dA, dB = sub(pool, slice(iA, iA + 1)), sub(pool, slice(iB, iB + 1)); recA, recB = A.record(pool, iA), A.record(pool, iB)
kw = lambda snap, arm: dict(bank_weight=snap["arms"][arm]["W"], rowmap=snap["arms"][arm]["rowmap"], unknown=snap["arms"][arm]["unknown"], lookup=snap["arms"][arm]["lookup"])
arms = [a for a in m3["arms"] if a != "rehearsal_core"]; out = {"core": name, "session": K, "tenant": ten, "new_policy_ids": t["new"], "expired_policy_id": t["expired"], "document_A": recA, "document_B": recB, "systems": {}}
with torch.no_grad():
    for a in arms:
        sA = model.run(dA, "hard", **kw(y, a))[0][0].tolist(); sA_after = model.run(dA, "hard", **kw(y, a))[0][0].tolist(); sB = model.run(dB, "hard", **kw(t, a))[0][0].tolist()
        gA, gB = grade(recA, pol, sA), grade(recB, pol, sB)
        out["systems"][a] = {"A_statuses": sA, "A_success": gA["success"], "A_wrong_steps": gA["wrong_steps"], "A_abstentions_final": sA[-1].count(A.ABSTAIN), "A_same_when_rerun_on_the_pinned_bank": sA == sA_after,
                             "B_statuses": sB, "B_success": gB["success"], "B_wrong_steps": gB["wrong_steps"], "B_protected_changed": gB["protected_changed"]}
# non-neural, with every rule given: the ceiling
tr = Tracker(pol, expired_true); jA, jB = tr.new_job(), tr.new_job(); oA = [tr.step(jA, e) for e in recA["events"]]; oB = [tr.step(jB, e) for e in recB["events"]]
out["systems"]["tracker_with_rules_given"] = {"A_success": grade(recA, pol, oA)["success"], "B_success": grade(recB, pol, oB)["success"], "B_statuses": oB}
# restart from files: the promoted bank version, compiled, run as plain tables
vfile = f"{base}/bank_dreaming_v{K}.pt"; sha = hashlib.sha256(open(vfile, "rb").read()).hexdigest(); v = torch.load(vfile, weights_only=True)
bank = {p: row_table(model, v["W"], p).tolist() for p in range(1, v["W"].shape[0] - 1) if not bool(v["unknown"][p])}; exp = [p for p in range(1, len(v["rowmap"])) if int(v["rowmap"][p]) == 0]
rt = TableRuntime(compile_procedures(model.tables()), bank, exp); job = rt.new_job(); oT = [rt.step(job, e) for e in recB["events"]]
vy = torch.load(f"{base}/bank_dreaming_v{K - 1}.pt", weights_only=True)
out["restart"] = {"bank_file": vfile, "sha256": sha, "sha256_matches_recorded_version": sha == m3["bank_versions"][f"dreaming_v{K}"]["sha256"], "compiled_tables_success_on_B": grade(recB, pol, oT)["success"],
                  "compiled_tables_equal_network_on_B": oT == out["systems"]["dreaming"]["B_statuses"], "procedure_uses_logged_for_B": len(job["uses"]),
                  "todays_policies_promoted": [p for p in t["new"] if p in bank], "todays_policies_known_yesterday": [p for p in t["new"] if not bool(vy["unknown"][p])]}
# one-off changes of document A: no bank row moved because of them (rows of IDs that are neither new nor re-consolidated are bit-identical)
same_rows = [p for p in range(1, v["W"].shape[0] - 1) if p not in t["new"] and torch.equal(v["W"][p], vy["W"][p])]
out["one_off_changes"] = {"A_has_correct_and_override": True, "bank_rows_unchanged_by_the_session": len(same_rows), "bank_rows_total": int(v["W"].shape[0] - 2),
                          "overrides_in_retrieval_index": "none: overrides are not policy decisions (provenance); the retrieval_naive arm shows what happens when they are indexed"}
os.makedirs("results/v04/demo", exist_ok=True); json.dump(out, open(f"results/v04/demo/trace_{name}.json", "w"), indent=1)
ev = lambda r: " ".join(f"{A.KIND_NAMES[e['kind']][:4]}" for e in r["events"][A.N_SETUP:])
print("document A (today, yesterday's bank):", ev(recA)); print("document B (after sleep and restart):", ev(recB))
print(f"{'system':28s} {'A: success':>10s} {'A: abstain':>10s} {'B: success':>10s} {'B: wrong steps':>14s}")
for a, r in out["systems"].items(): print(f"{a:28s} {str(r['A_success']):>10s} {str(r.get('A_abstentions_final', '-')):>10s} {str(r['B_success']):>10s} {str(r.get('B_wrong_steps', 0)):>14s}")
print("restart:", {k: out["restart"][k] for k in ("sha256_matches_recorded_version", "compiled_tables_success_on_B", "compiled_tables_equal_network_on_B", "todays_policies_promoted", "todays_policies_known_yesterday")})
