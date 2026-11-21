"""M2: does the selected procedure code do the work?   python v04/m2_interventions.py runs/v4a_proc_s_s1 [SALT]

On novel-combination test documents, at one real event per document, the learned arm's procedure is intervened on:
  swap      the code is replaced by the code the router gives another event kind
  suppress  no slot is recomputed at that event
  argument  the slot argument (slot events) or the jurisdiction argument (jurisdiction events) is changed to another value
The prediction comes from the hand-coded macro on the SAME executor (same bank, same status function, selection
written by hand) under the same intervention.  Reported: how often the intervention changed the outcome at all,
how often the learned arm's statuses after the event equal the macro's, and how many protected statuses (slots
the macro does not recompute at that event) changed in the learned arm.  Also the plain, unintervened agreement.
Also checks that the compiled tables (stillway4/runtime.py) give the network's outputs.
"""
import copy, json, os, sys
import torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4 import approvals as A
from stillway4.arms import ArmCfg, Proc, load, make_data, sub
from stillway4.runtime import TableRuntime, compile_procedures
from stillway4.sleep import row_table

run = sys.argv[1].rstrip("/"); name = os.path.basename(run); man = json.load(open(f"{run}/manifest.json")); salt = int(sys.argv[2]) if len(sys.argv) > 2 else man["args"].get("salt", 0)
torch.set_num_threads(1); model = load(f"{run}/checkpoint.pt"); uni, data = make_data(man["args"]["seed"], salt=salt); d = sub(data["test_novel"], slice(0, 2000)); B = 2000; ar = torch.arange(B)
twin = copy.deepcopy(model); ref = Proc(ArmCfg(arm="macro", width=model.cfg.width, n_pids=model.cfg.n_pids, d_pid=model.cfg.d_pid))
for a in ("router", "gate", "src"): getattr(twin, a).data.copy_(getattr(ref, a).data)
gen = torch.Generator().manual_seed(99); kinds = d["ev_kind"]; real = torch.zeros(B, A.T, dtype=torch.bool); real[:, A.N_SETUP:] = kinds[:, A.N_SETUP:] != A.WAIT
tsel = torch.multinomial(real.float() + 1e-9, 1, generator=gen).squeeze(1); at = torch.zeros(B, A.T, dtype=torch.bool); at[ar, tsel] = True; k0 = kinds[ar, tsel]
code_l = model.router.argmax(1); code_m = twin.router.argmax(1); out = {"run": name, "documents": B, "learned_procedure_tables": model.tables(), "hand_coded_tables": twin.tables()}
with torch.no_grad():
    base_l, _, tr_l0 = model.run(d, "hard"); base_m, _, tr_m0 = twin.run(d, "hard")
    out["no_intervention"] = {"learned_equals_macro_documents": float((base_l == base_m).flatten(1).all(1).float().mean()), "learned_success": float((base_l == d["labels"]).flatten(1).all(1).float().mean()),
                              "macro_success": float((base_m == d["labels"]).flatten(1).all(1).float().mean())}
    def compare(tag, iv_l, iv_m):
        sl, _, _ = model.run(d, "hard", iv=iv_l); sm, _, tm = twin.run(d, "hard", iv=iv_m)
        after_l, after_m = sl[ar, tsel], sm[ar, tsel]; prev_l = sl[ar, (tsel - 1)]; gate_m = tm["gate"][ar, tsel]
        wrote = (d["ev_ostat"][ar, tsel] >= 0)[:, None] & (torch.arange(A.S)[None] == d["ev_slot"][ar, tsel][:, None])        # a status register written by rule (OVERRIDE)
        prot = ~gate_m & ~wrote
        out[tag] = {"outcome_changed_by_intervention": float((after_m != base_m[ar, tsel]).any(1).float().mean()),
                    "learned_equals_macro_prediction": float((after_l == after_m).all(1).float().mean()),
                    "protected_statuses": int(prot.sum()), "protected_statuses_changed": int(((after_l != prev_l) & prot).sum()),
                    "rest_of_document_equal": float((sl == sm).flatten(1).all(1).float().mean())}
        print(tag, out[tag], flush=True)
    k2 = (k0 + 1 + torch.randint(0, A.NK - 2, (B,), generator=gen)) % A.NK; k2 = torch.where(k2 == A.WAIT, (k0 + 1) % A.NK, k2)
    cl = torch.zeros(B, A.T, dtype=torch.long); cl[ar, tsel] = code_l[k2]; cm = torch.zeros(B, A.T, dtype=torch.long); cm[ar, tsel] = code_m[k2]
    compare("swap_code", [{"at": at, "code": cl}], [{"at": at, "code": cm}])
    compare("suppress", [{"at": at, "suppress": True}], [{"at": at, "suppress": True}])
    slot_ev = d["ev_slot"][ar, tsel] >= 0; ns = torch.full((B, A.T), -1); nj = torch.full((B, A.T), -1)
    ns[ar, tsel] = torch.where(slot_ev, (d["ev_slot"][ar, tsel] + 1 + torch.randint(0, A.S - 1, (B,), generator=gen)) % A.S, d["ev_slot"][ar, tsel])
    nj[ar, tsel] = torch.where(~slot_ev, (d["ev_jur"][ar, tsel] + 1 + torch.randint(0, A.NJ - 1, (B,), generator=gen)) % A.NJ, d["ev_jur"][ar, tsel])
    iv = [{"at": at & slot_ev[:, None], "slot": ns}, {"at": at & ~slot_ev[:, None], "jur": nj}]
    compare("perturb_argument", iv, iv)
    # the compiled tables against the network, document by document
    proc = compile_procedures(model.tables()); bank = {p: row_table(model, model.bank.weight, p).tolist() for p in range(1, len(uni.pid_rule))}; rt = TableRuntime(proc, bank); same = 0
    for i in range(500):
        job = rt.new_job(); o = [rt.step(job, e) for e in A.record(d, i)["events"]]; same += o == base_l[i].tolist()
    out["compiled_tables_equal_network_documents"] = same; out["compiled_documents_checked"] = 500
os.makedirs("results/v04/m2", exist_ok=True); json.dump(out, open(f"results/v04/m2/interventions_{name}.json", "w"), indent=1)
print(out["no_intervention"], "compiled == network:", same, "of 500")
