"""EXPLORATORY (not frozen): the continuous-carry arm with ten times the logged documents (200,000) and up to an hour.
    python v04/x_cont_10x.py SEED SALT
Question: is the continuous-carry arm's failure in M2 a matter of data?  Same model, same test sets as the final run of that seed."""
import json, os, sys, time, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4 import approvals as A
from stillway4.arms import ArmCfg, SIZES, build, evaluate, make_data, save, train
seed, salt = int(sys.argv[1]), int(sys.argv[2]); torch.set_num_threads(1); uni, data = make_data(seed, salt=salt)
gen = torch.Generator().manual_seed(555 + seed); data["train"] = A.sample_docs(uni, 200000, gen, combos="train")          # the same policies, ten times the documents
torch.manual_seed(seed); model = build(ArmCfg(arm="cont", width=SIZES["cont"]["s"])); log = []; steps, sec = train(model, data, seed, steps=60000, budget=3300.0, log=log)
out = f"runs/v4x_cont10x_s_s{seed}"; os.makedirs(out, exist_ok=True); sha = save(model, f"{out}/checkpoint.pt")
res = {"name": os.path.basename(out), "exploratory": True, "arm": "cont", "args": {"seed": seed, "salt": salt}, "training_documents": 200000, "train_steps": steps, "train_seconds": round(sec, 1),
       "status": "complete" if steps >= 60000 else "incomplete: budget", "checkpoint_sha256": sha, "active_parameters_per_decision": model.active_params(), "log": log[-5:]}
for k in ("test_iid", "test_novel"):
    e = evaluate(model, data[k]); res[k] = {x: e[x] for x in ("success", "status_accuracy", "protected_changed")}
json.dump(res, open(f"{out}/manifest.json", "w"), indent=1); print(res["status"], {k: res[k]["success"] for k in ("test_iid", "test_novel")})
