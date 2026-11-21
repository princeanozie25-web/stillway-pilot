"""Score an externally authored approvals challenge.   python v04/score_external.py challenge.json runs/v4f_proc_s_s1
Format: docs/v04_external_challenge.md.  Systems: the core's compiled tables, and the dependency tracker with the rules given."""
import json, os, sys
import torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4.arms import load
from stillway4.grader import grade
from stillway4.runtime import TableRuntime, Tracker, compile_procedures
from stillway4.sleep import row_table
ch = json.load(open(sys.argv[1])); core = sys.argv[2].rstrip("/"); m = load(f"{core}/checkpoint.pt"); pol = {int(k): v for k, v in ch["policies"].items()}; exp = [p for p, v in pol.items() if v is None]
bank = {p: row_table(m, m.bank.weight, p).tolist() for p in range(1, m.cfg.n_pids - 1)}
systems = {"stillway_tables": TableRuntime(compile_procedures(m.tables()), bank, exp), "tracker_with_rules_given": Tracker({p: v for p, v in pol.items() if v is not None}, exp)}; out = {}
for name, rt in systems.items():
    ok = prot = 0; raw = []
    for d in ch["documents"]:
        job = rt.new_job(); o = [rt.step(job, e) for e in d["events"]]; g = grade(d, pol, o); ok += g["success"]; prot += g["protected_changed"]; raw.append(o)
    out[name] = {"documents": len(ch["documents"]), "success": ok / max(1, len(ch["documents"])), "protected_changed": prot, "outputs": raw}
    print(name, {k: v for k, v in out[name].items() if k != "outputs"})
json.dump(out, open(sys.argv[1].replace(".json", "_scored.json"), "w"))
