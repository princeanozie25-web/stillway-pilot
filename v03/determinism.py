"""Retrain one core and redo one repair; compare with the frozen checkpoints.   python v03/determinism.py
Compares every tensor of the state, and the stored config.  (A file hash also covers the stored config, and
the field `route_out` was added to the config after the first cores were saved, so file hashes of those
cores differ from a fresh save although every weight is equal.  This script shows which it is.)"""
import io, json, os, subprocess, sys, torch
PY = sys.executable; env = {**os.environ, "PYTHONPATH": "."}; out = {}
def ck(p): return torch.load(io.BytesIO(open(p, "rb").read()), map_location="cpu", weights_only=True)
def same(a, b):
    A, B = ck(a), ck(b); keys = sorted(A["state"]); assert keys == sorted(B["state"])
    return {"tensors": len(keys), "tensors_equal": sum(bool(torch.equal(A["state"][k], B["state"][k])) for k in keys),
            "config_frozen": A["cfg"], "config_fresh": B["cfg"]}
subprocess.run([PY, "-m", "stillway3.train", "--name", "zz_det", "--data", "t23", "--seed", "1"], env=env, capture_output=True, check=True)
out["v3r23_s1 retrained"] = same("runs/v3r23_s1/checkpoint.pt", "runs/zz_det/checkpoint.pt")
subprocess.run([PY, "-m", "stillway3.repair", "runs/v3r24_s1", "--alphabet", "all", "--out", "runs/zz_det_fix"], env=env, capture_output=True, check=True)
out["v3r24fix_s1 repaired again"] = same("runs/v3r24fix_s1/checkpoint.pt", "runs/zz_det_fix/checkpoint.pt")
import shutil; shutil.rmtree("runs/zz_det"); shutil.rmtree("runs/zz_det_fix")
os.makedirs("results/v03", exist_ok=True); json.dump(out, open("results/v03/determinism.json", "w"), indent=1); print(json.dumps(out, indent=1))
