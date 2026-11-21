"""M4: the whole system at batch one.   python v04/m4_bench.py SEED [--tag final]      (idle machine)

Reads the seed's procedural core (runs/v4f_proc_<size>_s<seed> or the name given with --core), its sleep results
(results/v04/m3/<core>/snapshot_v6.pt), and the neural comparators of the same seed if they exist.
Two workloads, each scored by the plain-Python grader from raw outputs:
  W2  the M2 test documents (base policies): 300 ordinary + 300 novel-combination documents
  W3  after the last sleep: 300 documents on the session's new policies + 300 on older active policies
Systems
  stillway_tables   compiled procedure tables + compiled bank (the consolidation+dreaming bank on W3)       plain Python
  retrieval_tables  compiled procedures + base bank + retrieval index (W3)                                     plain Python
  tracker           dependency tracker with every rule given (non-neural)                                      plain Python
  replay            rule engine replaying the history at every step (non-neural)                               plain Python
  proc_network      the procedural arm's network executor                                                      torch
  cont_network, vq_network   GRU arms (W2 only: they have no bank update defined)                              torch
  direct_network    the GRU re-reading the whole history at every step (W2)                                    torch
For each: grader success, latency per job and per event (median, p95), compute per successful job, deployed bytes,
and (in a fresh process) load time, first-job time and peak resident memory.
"""
import argparse, json, os, resource, subprocess, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway4.grader import grade
from stillway4.runtime import Replay, TableRuntime, Tracker, compile_procedures, save_job, load_job

N = 300


def setup(core, salt):
    import torch
    from stillway4 import approvals as A
    from stillway4.arms import load, make_data, sub
    from stillway4.sleep import row_table
    torch.set_num_threads(1); name = os.path.basename(core); man = json.load(open(f"{core}/manifest.json")); seed = man["args"]["seed"]; model = load(f"{core}/checkpoint.pt")
    uni, data = make_data(seed, salt=salt); snap = torch.load(f"results/v04/m3/{name}/snapshot_v6.pt", weights_only=False); gen = torch.Generator().manual_seed(4242 + seed)
    w2 = {k: torch.cat([data["test_iid"][k][:N], data["test_novel"][k][:N]]) for k in data["test_iid"]}
    u3 = A.Universe(snap["pid_rule"], snap["pid_tenant"]); ten = snap["tenant_changed"]; act = {t: torch.tensor(snap["active"][t]) for t in (0, 1)}
    a = A.sample_docs(u3, N, gen, active={ten: torch.tensor(snap["new"]), 1 - ten: act[1 - ten]}, combos="any", tenant=ten); b = A.sample_docs(u3, N, gen, active={t: torch.tensor(snap["old"][t]) for t in (0, 1)}, combos="any")
    w3 = {k: torch.cat([a[k], b[k]]) for k in a}
    pol = lambda u: {p: (A.RULES[int(u.pid_rule[p])].tolist() if int(u.pid_rule[p]) >= 0 else None) for p in range(1, len(u.pid_rule))}      # None = expired
    exp3 = [p for p in range(1, len(u3.pid_rule)) if int(u3.pid_rule[p]) < 0]
    proc = compile_procedures(model.tables()); t0 = time.perf_counter()
    bank2 = {p: row_table(model, model.bank.weight, p).tolist() for p in range(1, len(uni.pid_rule))}; compile_s = time.perf_counter() - t0
    def bank_of(arm):
        s_ = snap["arms"][arm]; return {p: row_table(model, s_["W"], p).tolist() for p in range(1, s_["W"].shape[0] - 1) if not bool(s_["unknown"][p])}, [p for p in range(1, len(s_["rowmap"])) if int(s_["rowmap"][p]) == 0]
    bd, ed = bank_of("dreaming"); bn, _ = bank_of("none"); lk = snap["arms"]["retrieval"]["lookup"]; idx = {(int(p), int(f)): int(lk[p, f]) for p, f in (lk >= 0).nonzero().tolist()}
    recs = lambda d: [A.record(d, i) for i in range(len(d["tenant"]))]
    return dict(model=model, name=name, seed=seed, w2=w2, w3=w3, docs2=recs(w2), docs3=recs(w3), pol2=pol(uni), pol3=pol(u3), exp3=exp3, proc=proc, bank2=bank2, bank3=bd, exp_reg=ed, bank_none=bn,
                index=idx, compile_s=compile_s, snap=snap, uni=uni, man=man)


def time_python(rt, docs):
    ev_ns, job_ns, outs = [], [], []
    for rep in range(3):
        for doc in docs:
            job = rt.new_job(); o = []; t0 = time.perf_counter_ns()
            for e in doc["events"]:
                t1 = time.perf_counter_ns(); o.append(rt.step(job, e)); t2 = time.perf_counter_ns()
                if rep: ev_ns.append(t2 - t1)
            if rep: job_ns.append(time.perf_counter_ns() - t0)
            if rep == 0: outs.append(o)
    return ev_ns, job_ns, outs


def summarise(ev_ns, job_ns, outs, docs, pol, extra=None):
    g = [grade(d, pol, o) for d, o in zip(docs, outs)]; succ = float(np.mean([x["success"] for x in g])); jm = float(np.median(job_ns)) / 1e3
    r = {"documents": len(docs), "grader_success": succ, "protected_statuses_changed": int(sum(x["protected_changed"] for x in g)),
         "job_us_median": jm, "job_us_p95": float(np.percentile(job_ns, 95)) / 1e3, "event_us_median": float(np.median(ev_ns)) / 1e3, "event_us_p95": float(np.percentile(ev_ns, 95)) / 1e3,
         "cpu_us_per_successful_job": (float(np.mean(job_ns)) / 1e3 / succ) if succ > 0 else None}
    r.update(extra or {}); return r


def time_torch(model, d, kind, n=150, **kw):
    """Batch one.  kind 'run': the arm's own run.  kind 'direct': the GRU from an empty memory over the whole history at every step."""
    import torch
    from stillway4.arms import sub
    from stillway4 import approvals as A
    job_ns, outs = [], []
    with torch.no_grad():
        for rep in range(2):
            for i in range(n):
                di = sub(d, slice(i, i + 1)); t0 = time.perf_counter_ns()
                if kind == "run": st = model.run(di, "hard", **kw)[0]
                else:
                    st = []
                    for t in range(A.T):
                        h = torch.zeros(1, model.cfg.width)
                        for u in range(t + 1): h = model.cell(model.encode(di, u), h)
                        st.append(model.head(h).view(1, A.S, 4).argmax(-1))
                    st = torch.stack(st, 1)
                dt = time.perf_counter_ns() - t0
                if rep: job_ns.append(dt)
                else: outs.append(st[0].tolist())
    return [x / A.T for x in job_ns], job_ns, outs


def child(system, core, salt):
    t0 = time.perf_counter(); c = None
    if system in ("tracker", "replay", "tables"):
        blob = json.load(open(f"results/v04/m4/deploy_{os.path.basename(core)}.json")); doc = blob["doc"]
        if system == "tables": rt = TableRuntime(blob["proc"], {int(k): v for k, v in blob["bank"].items()}, blob["expired"])
        else: rt = (Tracker if system == "tracker" else Replay)({int(k): v for k, v in blob["policies"].items()}, blob["expired_true"])
        load_s = time.perf_counter() - t0; t1 = time.perf_counter(); job = rt.new_job(); [rt.step(job, e) for e in doc["events"]]; first = time.perf_counter() - t1
    else:
        import torch; from stillway4.arms import load, make_data, sub
        torch.set_num_threads(1); m = load(f"{core}/checkpoint.pt"); man = json.load(open(f"{core}/manifest.json")); _, data = make_data(man["args"]["seed"], n_train=10, n_dev=10, n_test=10, salt=salt)
        load_s = time.perf_counter() - t0; t1 = time.perf_counter()
        with torch.no_grad(): m.run(sub(data["test_iid"], slice(0, 1)), "hard")
        first = time.perf_counter() - t1
    print(json.dumps({"load_seconds": load_s, "first_job_seconds": first, "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("seed", type=int); ap.add_argument("--core", default=""); ap.add_argument("--prefix", default="v4f"); ap.add_argument("--size", default="s")
    ap.add_argument("--salt", type=int, default=-1); ap.add_argument("--child", default=""); a = ap.parse_args()
    core = a.core or f"runs/{a.prefix}_proc_{a.size}_s{a.seed}"; man = json.load(open(f"{core}/manifest.json")); salt = man["args"].get("salt", 0) if a.salt < 0 else a.salt
    if a.child: return child(a.child, core, salt)
    import torch
    from stillway4.arms import load
    S = setup(core, salt); os.makedirs("results/v04/m4", exist_ok=True); res = {"seed": a.seed, "core": S["name"], "salt": salt, "W2": {}, "W3": {}, "bytes": {}, "process": {}}
    json.dump({"proc": S["proc"], "bank": S["bank3"], "expired": S["exp_reg"], "policies": S["pol3"], "expired_true": S["exp3"], "doc": S["docs3"][0]}, open(f"results/v04/m4/deploy_{S['name']}.json", "w"))
    T2 = TableRuntime(S["proc"], S["bank2"]); T3 = TableRuntime(S["proc"], S["bank3"], S["exp_reg"]); R3 = TableRuntime(S["proc"], S["bank_none"], S["exp_reg"], lookup=S["index"])
    for wname, docs, pol, exp, systems in (("W2", S["docs2"], S["pol2"], [], {"stillway_tables": T2, "tracker": Tracker(S["pol2"]), "replay": Replay(S["pol2"])}),
                                           ("W3", S["docs3"], S["pol3"], S["exp3"], {"stillway_tables": T3, "retrieval_tables": R3, "tracker": Tracker(S["pol3"], S["exp3"]), "replay": Replay(S["pol3"], S["exp3"])})):
        for sname, rt in systems.items():
            res[wname][sname] = summarise(*time_python(rt, docs), docs, pol); print(wname, sname, {k: round(v, 3) for k, v in res[wname][sname].items() if isinstance(v, float)}, flush=True)
    m = S["model"]; n = 150; d2 = S["w2"]; d3 = S["w3"]; sn = S["snap"]["arms"]
    ev, jb, o = time_torch(m, d2, "run"); res["W2"]["proc_network"] = summarise(ev, jb, o, S["docs2"][:n], S["pol2"], {"multiply_accumulates_per_job": None})
    kw = lambda arm: dict(bank_weight=sn[arm]["W"], rowmap=sn[arm]["rowmap"], unknown=sn[arm]["unknown"], lookup=sn[arm]["lookup"])
    for arm in ("dreaming", "consolidation", "rehearsal", "retrieval", "none"):
        ev, jb, o = time_torch(m, d3, "run", **kw(arm)); res["W3"][f"proc_network_{arm}"] = summarise(ev, jb, o, S["docs3"][:n], S["pol3"])
        # the same bank on the second half of W3 (older policies), so both halves are scored
        from stillway4.arms import evaluate
        e = evaluate(m, d3, **kw(arm)); g = [grade(S["docs3"][i], S["pol3"], e["outputs"][i].tolist())["success"] for i in range(len(S["docs3"]))]
        res["W3"][f"proc_network_{arm}"].update({"grader_success_all_600": float(np.mean(g)), "grader_success_new_policies": float(np.mean(g[:N])), "grader_success_older_policies": float(np.mean(g[N:]))})
    with torch.no_grad(): _, _, tr = m.run(d2, "hard")
    res["W2"]["proc_network"]["multiply_accumulates_per_job"] = float(tr["n_recomputed"].sum(1).float().mean()) * m.macs_per_slot(); res["W2"]["proc_network"]["slots_recomputed_per_job"] = float(tr["n_recomputed"].sum(1).float().mean())
    res["W2"]["stillway_tables"]["table_lookups_per_job"] = res["W2"]["proc_network"]["slots_recomputed_per_job"]
    from stillway4 import approvals as A
    for arm in ("cont", "vq"):
        p = core.replace("_proc_", f"_{arm}_")
        if p == core or not os.path.exists(f"{p}/checkpoint.pt"): continue
        g = load(f"{p}/checkpoint.pt"); ev, jb, o = time_torch(g, d2, "run"); res["W2"][f"{arm}_network"] = summarise(ev, jb, o, S["docs2"][:n], S["pol2"], {"multiply_accumulates_per_job": A.T * g.macs_per_step()})
        res["bytes"][f"{arm}_network"] = {"checkpoint_bytes": os.path.getsize(f"{p}/checkpoint.pt"), "active_parameters": g.active_params(), "fp16_bytes_active": 2 * g.active_params()}
        if arm == "cont":
            ev, jb, o = time_torch(g, d2, "direct", n=60); res["W2"]["direct_network"] = summarise(ev, jb, o, S["docs2"][:60], S["pol2"], {"multiply_accumulates_per_job": A.T * (A.T + 1) // 2 * g.macs_per_step()})
    for k in ("W2", "W3"):
        for sname in res[k]: print(k, sname, "success", round(res[k][sname]["grader_success"], 4), "job us", round(res[k][sname]["job_us_median"], 1), flush=True)
    # ---- bytes deployed ----
    jb_ = lambda x: len(json.dumps(x, separators=(",", ":")).encode())
    res["bytes"]["stillway_tables"] = {"procedure_tables_bytes": jb_(S["proc"]), "bank_bytes_one_byte_per_entry": 36 * len(S["bank3"]), "policies_in_bank": len(S["bank3"]), "registry_bytes": 2 * len(S["exp_reg"]),
                                       "total_runtime_bytes": jb_(S["proc"]) + 36 * len(S["bank3"]) + 2 * len(S["exp_reg"]), "needed_only_at_sleep_checkpoint_bytes": os.path.getsize(f"{core}/checkpoint.pt")}
    res["bytes"]["proc_network"] = {"checkpoint_bytes": os.path.getsize(f"{core}/checkpoint.pt"), "active_parameters": m.active_params(), "fp16_bytes_active": 2 * m.active_params(), "bank_rows": int(sn["dreaming"]["W"].shape[0]), "bank_fp16_bytes": int(2 * sn["dreaming"]["W"].numel())}
    res["bytes"]["retrieval_tables"] = {"index_entries": len(S["index"]), "index_bytes_4_per_entry": 4 * len(S["index"]), "base_bank_bytes": 36 * len(S["bank_none"]), "total_runtime_bytes": jb_(S["proc"]) + 4 * len(S["index"]) + 36 * len(S["bank_none"])}
    res["bytes"]["tracker"] = {"policies": len(S["pol3"]), "bytes_4_per_policy": 4 * len(S["pol3"])}
    # ---- resume against restart (tables): one more event on a saved job, or replay the job from its first event ----
    rs, fr = [], []
    for doc in S["docs3"][:200]:
        job = T3.new_job(); ev_ = doc["events"]
        for e in ev_[:12]: T3.step(job, e)
        blob = save_job(job); t0 = time.perf_counter_ns(); j2 = load_job(blob); T3.step(j2, ev_[12]); rs.append(time.perf_counter_ns() - t0)
        t0 = time.perf_counter_ns(); j3 = T3.new_job(); [T3.step(j3, e) for e in ev_[:13]]; fr.append(time.perf_counter_ns() - t0)
    res["resume"] = {"resumed_one_event_us_median": float(np.median(rs)) / 1e3, "fresh_replay_13_events_us_median": float(np.median(fr)) / 1e3, "saved_job_bytes_median": int(np.median([len(save_job(T3.new_job()))]))}
    # ---- fresh process: load, first job, memory ----
    for sysname in ("tables", "tracker", "replay", "proc_net"):
        r = subprocess.run([sys.executable, __file__, str(a.seed), "--core", core, "--salt", str(salt), "--child", sysname], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "."})
        res["process"][sysname] = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else {"error": r.stderr[-300:]}
    # ---- break-even of a sleep cycle ----
    m3 = json.load(open(f"results/v04/m3/{S['name']}.json")); sleep_s = float(np.mean([s_["sleep_seconds"]["dreaming"] for s_ in m3["sessions"]])) + S["compile_s"]
    tj = res["W3"]["stillway_tables"]["job_us_median"]; be = {}
    for comp in ("retrieval_tables", "tracker", "replay", "proc_network_dreaming"):
        save_us = res["W3"][comp]["job_us_median"] - tj; be[comp] = {"saving_us_per_job": save_us, "jobs_to_break_even": (sleep_s * 1e6 / save_us) if save_us > 0 else None}
    res["break_even"] = {"sleep_cycle_seconds_dreaming_plus_compile": sleep_s, "against": be,
                         "cost_per_job_us_by_jobs_per_sleep_cycle": {str(v): tj + sleep_s * 1e6 / v for v in (10, 100, 1000, 10000, 100000)}}
    json.dump(res, open(f"results/v04/m4/bench_{S['name']}.json", "w"), indent=1); print("saved", f"results/v04/m4/bench_{S['name']}.json")


if __name__ == "__main__":
    main()
