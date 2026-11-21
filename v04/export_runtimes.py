"""Export a v0.3 register core's tables on every supported numeric runtime and certify each export.

    python v04/export_runtimes.py runs/v3o_s1 runs/v3r24fix_s1

Runtimes: torch CPU float32, torch CPU float64, torch MPS float32 (if present), NumPy float32 (own forward pass).
For each export: SHA-256 of the tables, the closure certificate (stillway4/gates.py checker), and the number of
table entries that differ from the CPU float32 export.  A certificate belongs to one export (one hash).
"""
import hashlib, json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway3.certify import LEGS_ALL, desc_vec
from stillway3.model import load_reg, expected_count
from stillway4.gates import Gates, certify

g = Gates(2); clo = g.exact_closure(); EX = g.compile_exact(clo); D = torch.stack([desc_vec(l) for l in LEGS_ALL]); JOINT = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]]).float()

def tables_torch(model, device, dtype):
    m = load_reg(model).to(device=device, dtype=dtype); K = m.cfg.n_codes; cb = m.codebook; Dd = D.to(device=device, dtype=dtype); J = JOINT.to(device=device, dtype=dtype)
    snap = lambda z: torch.cdist(torch.tanh(z), cb).argmin(1)
    r = torch.arange(3, device=device)
    with torch.no_grad():
        term = snap(m.term(torch.cat([m.emb_req(r.repeat_interleave(3)), m.emb_req(r.repeat(3))], 1)))
        cell = snap(m.cell(torch.cat([cb[:, None, :].expand(K, 64, -1), Dd[None].expand(K, 64, -1)], 2).reshape(K * 64, -1))).view(K, 64)
        rl = m.route(torch.cat([cb[:, None, None, :].expand(K, 64, 4, -1), Dd[None, :, None, :].expand(K, 64, 4, -1), J[None, None].expand(K, 64, 4, -1)], 3).reshape(K * 256, -1))
        if m.cfg.route_out != 2: rl = (torch.softmax(rl.view(-1, 2, 3), -1) * torch.tensor([0.0, 1.0, 2.0], device=device, dtype=dtype)).sum(-1)
    return {"term": term.cpu().numpy(), "cell": cell.cpu().numpy(), "route": rl.argmax(1).view(K, 64, 4).cpu().numpy().astype(np.uint8)}

def tables_numpy(model):
    m = load_reg(model); sd = {k: v.numpy().astype(np.float32) for k, v in m.state_dict().items() if v.dtype.is_floating_point}; K = m.cfg.n_codes; cb = sd["codebook"]
    def mlp(name, x):
        for i in (0, 2, 4):
            x = x @ sd[f"{name}.{i}.weight"].T + sd[f"{name}.{i}.bias"]
            if i < 4: x = np.maximum(x, 0)
        return x
    def snap(z):
        z = np.tanh(z); d = (z * z).sum(1, keepdims=True) - 2 * z @ cb.T + (cb * cb).sum(1)[None]; return d.argmin(1)
    Dn = D.numpy(); E = sd["emb_req.weight"]; r = np.arange(3)
    term = snap(mlp("term", np.concatenate([E[np.repeat(r, 3)], E[np.tile(r, 3)]], 1)))
    cell = snap(mlp("cell", np.concatenate([np.repeat(cb, 64, 0), np.tile(Dn, (K, 1))], 1))).reshape(K, 64)
    rin = np.concatenate([np.repeat(cb, 256, 0), np.tile(np.repeat(Dn, 4, 0), (K, 1)), np.tile(JOINT.numpy(), (K * 64, 1))], 1); rl = mlp("route", rin)
    if m.cfg.route_out != 2:
        x = rl.reshape(-1, 2, 3); x = np.exp(x - x.max(-1, keepdims=True)); x = x / x.sum(-1, keepdims=True); rl = (x * np.array([0, 1, 2], np.float32)).sum(-1)
    return {"term": term, "cell": cell, "route": rl.argmax(1).reshape(K, 64, 4).astype(np.uint8)}

out = {}
for run in sys.argv[1:]:
    run = run.rstrip("/"); name = os.path.basename(run); ck = f"{run}/checkpoint.pt"; exps = {"torch_cpu_float32": tables_torch(ck, "cpu", torch.float32), "torch_cpu_float64": tables_torch(ck, "cpu", torch.float64)}
    if torch.backends.mps.is_available(): exps["torch_mps_float32"] = tables_torch(ck, "mps", torch.float32)
    exps["numpy_float32"] = tables_numpy(ck); ref = exps["torch_cpu_float32"]; out[name] = {}
    for rt, t in exps.items():
        c = certify(t, EX); h = hashlib.sha256(t["term"].astype(np.int32).tobytes() + t["cell"].astype(np.int32).tobytes() + t["route"].tobytes()).hexdigest()
        # only entries the closure can reach matter for the certificate; count differences both ways
        pk = c["pair_keys"] // EX["n_codes"]; reach = np.unique(pk)
        out[name][rt] = {"tables_sha256": h, "certificate": {"pairs": c["pairs"], "route_checks": c["route_checks"], "route_wrong": c["route_wrong"], "codes_used": c["codes_used"]},
                         "entries_differing_from_torch_cpu_float32": {"term": int((t["term"] != ref["term"]).sum()), "cell_all_codes": int((t["cell"] != ref["cell"]).sum()),
                                                                       "cell_reachable_codes": int((t["cell"][reach] != ref["cell"][reach]).sum()), "route_reachable_codes": int((t["route"][reach] != ref["route"][reach]).sum())}}
        print(name, rt, h[:12], out[name][rt]["certificate"], out[name][rt]["entries_differing_from_torch_cpu_float32"], flush=True)
os.makedirs("results/v04/runtimes", exist_ok=True); json.dump(out, open("results/v04/runtimes/exports.json", "w"), indent=1)
