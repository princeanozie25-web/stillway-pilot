"""M1: learned tables against exact tables in the same C program, on identical jobs; plus the network; plus
the full runtime check of every reachable module input.

    python v04/m1_bench.py runs/v4r_g2_w128_s1          # writes results/v04/m1/bench_<name>.json
    python v04/m1_bench.py exact 4                        # exact tables only (no learned run needed)

For each job length (2 to 64 legs) the same jobs go through v04/runner (exact tables, learned tables) and
through the network at batch one.  Every decision is checked against the exact planner's valid set.
"""
import json, os, struct, subprocess, sys, time
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4.gates import Gates, certify, read_tables, write_tables

OUT = "results/v04/m1"; os.makedirs(OUT, exist_ok=True); LENGTHS = (2, 4, 8, 16, 32, 64)
if not os.path.exists("v04/runner") or os.path.getmtime("v04/runner") < os.path.getmtime("v04/runner.c"):
    subprocess.run(["cc", "-O2", "-o", "v04/runner", "v04/runner.c"], check=True)


def write_jobs(path, q, s, L, legs):
    n, lmax = legs.shape
    rec = np.concatenate([q[:, None], s[:, None], L[:, None], legs], 1).astype(np.int32)
    with open(path, "wb") as f: f.write(struct.pack("<2i", n, lmax)); f.write(rec.tobytes())


def run_runner(tables, jobs, mode, repeat=200, passes=5):
    out = jobs + ".out"; r = subprocess.run(["v04/runner", tables, jobs, out, str(mode), str(repeat), str(passes)], capture_output=True, text=True, check=True)
    b = open(out, "rb").read(); n, p = struct.unpack("<2i", b[:8]); first = np.frombuffer(b, np.uint8, n, 8); fin = np.frombuffer(b, np.uint8, n, 8 + n)
    ns = np.frombuffer(b, np.float32, n * p, 8 + 2 * n).reshape(p, n); os.remove(out)
    return {**json.loads(r.stdout), "first": first, "final": fin, "ns_cold": ns[0], "ns_warm": ns[1:].reshape(-1)}


def stats(x): return {"median_ns": float(np.median(x)), "p95_ns": float(np.percentile(x, 95)), "mean_ns": float(np.mean(x))}


def main():
    exact_only = sys.argv[1] == "exact"; rng = np.random.default_rng(20261121)
    if exact_only: G = int(sys.argv[2]); name = f"exact_g{G}"
    else:
        run = sys.argv[1].rstrip("/"); name = os.path.basename(run); man = json.load(open(f"{run}/manifest.json")); G = man["G"]
    g = Gates(G); t0 = time.time(); clo = g.exact_closure(); ex = g.compile_exact(clo); exact_seconds = time.time() - t0
    ex_path = f"{OUT}/exact_g{G}.bin"; ex_bytes = write_tables(ex_path, G, ex["term"], ex["cell"], ex["route"])
    dp_path = f"{OUT}/dp_g{G}.bin"; write_tables(dp_path, G, ex["term"], ex["cell"][:0], ex["route"][:0])          # header only: the on-the-spot planner reads no table
    res = {"name": name, "G": G, "exact": {"dp_program_file_bytes": os.path.getsize(dp_path), "vectors": ex["n_codes"], "closure_depth": clo["depth"], "growth_by_depth": clo["growth_by_depth"], "closure_and_compile_seconds": round(exact_seconds, 3),
                                           "table_bytes": ex_bytes, "peak_rss_bytes_python_compile": clo["peak_rss_bytes"]}, "by_length": {}}
    if not exact_only:
        lt = read_tables(f"{run}/tables.bin"); res["learned"] = {k: man[k] for k in ("tables_bytes", "tables_codes", "train_seconds", "wall_seconds", "clean", "status", "active_parameters_per_decision", "resident_parameters", "checkpoint_sha256", "tables_sha256")}
        res["learned"]["checkpoint_bytes"] = os.path.getsize(f"{run}/checkpoint.pt")
        from stillway4.reader import load; model = load(f"{run}/checkpoint.pt"); torch.set_num_threads(1)
    for L in LENGTHS:
        n = 2000; q = rng.integers(0, g.NQ, n); s = rng.integers(0, g.NS, n); legs = rng.integers(0, g.NL, (n, L)); Ls = np.full(n, L); jp = f"{OUT}/jobs_{name}_{L}.bin"; write_jobs(jp, q, s, Ls, legs)
        row = {}
        for mode, mname in ((0, "one_decision"), (1, "whole_job")):
            e = run_runner(ex_path, jp, mode); row[mname] = {"exact_tables": {"warm": stats(e["ns_warm"]), "cold": stats(e["ns_cold"]), "load_ns": e["load_ns"], "peak_rss_bytes": e["peak_rss_bytes"]}}
            dp = run_runner(dp_path, jp, mode + 2); row[mname]["exact_dp_no_tables"] = {"warm": stats(dp["ns_warm"]), "cold": stats(dp["ns_cold"]), "load_ns": dp["load_ns"], "peak_rss_bytes": dp["peak_rss_bytes"]}
            assert (dp["first"] == e["first"]).all() or mode == 1, "the on-the-spot planner and the exact tables disagree"
            if not exact_only:
                l = run_runner(f"{run}/tables.bin", jp, mode); row[mname]["learned_tables"] = {"warm": stats(l["ns_warm"]), "cold": stats(l["ns_cold"]), "load_ns": l["load_ns"], "peak_rss_bytes": l["peak_rss_bytes"]}
                if mode == 0:                                   # validity of every learned decision against the exact valid set
                    c = ex["term"][q]
                    for j in range(L - 1, 0, -1): c = ex["cell"][c, legs[:, j]]
                    v = ex["valid"][c, legs[:, 0], s]; row["learned_decisions_valid"] = int(((v >> l["first"]) & 1).sum()); row["exact_decisions_valid"] = int(((v >> e["first"]) & 1).sum()); row["jobs"] = n
        if not exact_only:                                      # the network, batch one, same jobs (first 300)
            ts = []; ok = 0
            with torch.no_grad():
                for rep in range(2):
                    for i in range(300):
                        qi, si, lg = torch.tensor([int(q[i])]), torch.tensor([int(s[i])]), torch.tensor(legs[i:i + 1])
                        t = time.perf_counter(); c = model.codebook[model.nearest(torch.tanh(model.start(qi)))]
                        for j in range(L - 1, 0, -1): c = model.codebook[model.nearest(torch.tanh(model.step_leg(c, lg[:, j])))]
                        a = int(model.decide(c, lg[:, 0], si).argmax()); dt = time.perf_counter() - t
                        if rep: ts.append(dt * 1e9); ok += a == int(l["first"][i])
            row["one_decision"]["network_batch_one"] = stats(np.array(ts)); row["network_equals_learned_tables"] = ok; row["network_jobs"] = 300
        res["by_length"][str(L)] = row; os.remove(jp)
        print(name, "L", L, {k: (round(v["warm"]["median_ns"], 1) if "warm" in v else round(v["median_ns"])) for k, v in row["one_decision"].items()}, flush=True)
    if not exact_only:
        # every reachable module input through both released runtimes
        cert = certify(lt, ex, want_wrong=5); N = ex["n_codes"]; pairs = cert["pair_keys"]; par = cert["parents"]; t0 = time.time()
        def path(k):
            out = []
            while par[k][0] != -1: out.append(par[k][1]); k = par[k][0]
            return par[k][1], out
        cap = 400000; ent = [(int(k), l, s) for k in pairs.tolist() for l in range(g.NL) for s in range(g.NS)]
        if len(ent) > cap: idx = rng.choice(len(ent), cap, replace=False); ent = [ent[i] for i in idx]; sampled = True
        else: sampled = False
        paths = {int(k): path(int(k)) for k in pairs.tolist()}; lmax = 1 + max(len(p[1]) for p in paths.values())
        q = np.array([paths[k][0] for k, _, _ in ent]); s = np.array([x[2] for x in ent]); Ls = np.array([1 + len(paths[k][1]) for k, _, _ in ent]); legs = np.zeros((len(ent), lmax), np.int64)
        for i, (k, l, _) in enumerate(ent): legs[i, 0] = l; legs[i, 1:Ls[i]] = paths[k][1]
        want = lt["route"][[k // N for k, _, _ in ent], [l for _, l, _ in ent], s]
        jp = f"{OUT}/jobs_{name}_closure.bin"; write_jobs(jp, q, s, Ls, legs); r = run_runner(f"{run}/tables.bin", jp, 0, repeat=1, passes=1); os.remove(jp); c_ok = int((r["first"] == want).sum())
        with torch.no_grad():                                   # the network on the same jobs, batched
            net = np.zeros(len(ent), np.int64)
            for i0 in range(0, len(ent), 8192):
                qq, ss, ll, LL = torch.tensor(q[i0:i0 + 8192]), torch.tensor(s[i0:i0 + 8192]), torch.tensor(legs[i0:i0 + 8192]), torch.tensor(Ls[i0:i0 + 8192])
                c = model.codebook[model.nearest(torch.tanh(model.start(qq)))]
                for j in range(lmax - 1, 0, -1):
                    m = j < LL; c2 = model.codebook[model.nearest(torch.tanh(model.step_leg(c, ll[:, j])))]; c = torch.where(m[:, None], c2, c)
                net[i0:i0 + 8192] = model.decide(c, ll[:, 0], ss).argmax(1).numpy()
        res["runtime_check"] = {"closure_entries": int(len(pairs) * g.NL * g.NS), "entries_run": len(ent), "sampled": sampled, "longest_job_legs": int(lmax),
                                "c_runner_equals_tables": c_ok, "network_equals_tables": int((net == want).sum()), "seconds": round(time.time() - t0, 1)}
        res["certificate"] = {k: cert[k] for k in ("complete", "pairs", "depth", "growth_by_depth", "codes_used", "exact_vectors_reached", "route_checks", "route_wrong", "entries_with_one_valid_route", "shortest_witness_legs")}
        res["certificate"].update({"artifact": "tables.bin", "artifact_sha256": man["tables_sha256"], "alphabet": f"all {g.NL} leg kinds, {G} gates", "seconds": round(cert["seconds"], 3)})
        # break-even: what the learned route costs before the first call, against the exact tables and against the network
        d16 = res["by_length"]["16"]["one_decision"]; save = d16["network_batch_one"]["median_ns"] - d16["learned_tables"]["warm"]["median_ns"]
        res["break_even"] = {"learned_offline_seconds": man["wall_seconds"], "exact_offline_seconds": round(exact_seconds, 3),
                             "tables_against_network_calls_to_recover_learned_offline_cost_at_16_legs": (man["wall_seconds"] * 1e9 / save) if save > 0 else None,
                             "learned_tables_against_exact_tables_saving_ns_per_call_at_16_legs": d16["exact_tables"]["warm"]["median_ns"] - d16["learned_tables"]["warm"]["median_ns"],
                             "note": "the exact tables need no training; the learned tables break even against them only if their per-call saving is positive"}
        print(name, "runtime check", res["runtime_check"], "certificate wrong", cert["route_wrong"], flush=True)
    json.dump(res, open(f"{OUT}/bench_{name}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
