"""Raw timing samples (written after the freeze; the frozen benchmark keeps only medians and percentiles).
    python v04/timing_samples.py 1      -> results/v04/m4/timing_samples_s1.npz : nanoseconds per job and per event, every sample
Same code paths as v04/m4_bench.py (its functions are imported), workload W3, idle machine."""
import importlib.util, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("m4", os.path.join(os.path.dirname(__file__), "m4_bench.py")); m4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m4)
from stillway4.runtime import Replay, TableRuntime, Tracker
seed = int(sys.argv[1]); core = f"runs/v4f_proc_s_s{seed}"; man = json.load(open(f"{core}/manifest.json")); S = m4.setup(core, man["args"]["salt"]); out = {}
for name, rt in (("stillway_tables", TableRuntime(S["proc"], S["bank3"], S["exp_reg"])), ("retrieval_tables", TableRuntime(S["proc"], S["bank_none"], S["exp_reg"], lookup=S["index"])),
                 ("tracker", Tracker(S["pol3"], S["exp3"])), ("replay", Replay(S["pol3"], S["exp3"]))):
    ev, jb, _ = m4.time_python(rt, S["docs3"]); out[f"{name}_event_ns"] = np.array(ev, np.int64); out[f"{name}_job_ns"] = np.array(jb, np.int64)
sn = S["snap"]["arms"]["dreaming"]; ev, jb, _ = m4.time_torch(S["model"], S["w3"], "run", bank_weight=sn["W"], rowmap=sn["rowmap"], unknown=sn["unknown"], lookup=sn["lookup"])
out["proc_network_job_ns"] = np.array(jb, np.int64); np.savez_compressed(f"results/v04/m4/timing_samples_s{seed}.npz", **out)
print({k: (len(v), float(np.median(v)), float(np.percentile(v, 95))) for k, v in out.items()})
