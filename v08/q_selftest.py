"""Development fixtures for the questioning guard.   python v08/q_selftest.py PUBLIC.jsonl HIDDEN.jsonl [N]

Uses development jobs whose hidden half I hold (the first N of the file, default 60) and the arm with no model.
 1  the equivalence rule is sound: settings with the same form give the same report on random legal inputs
 2  a disposable probe leaves the workspace byte for byte as it was, and leaves no scratch copy behind
 3  a crash in round 1 (process killed, last line torn) is recovered by running the same command again
 4  an answer delivered twice counts once; resuming twice does nothing the second time
 5  a missing answer ends in a bare ASK with the workspace untouched
 6  invalid answers (wrong field, wrong round, wrong type, extra key, two conflicting lines) do the same
 7  an answer that differs from both predictions and agrees with no surviving change does the same
 8  an exhausted question budget does the same
 9  a procedure that fails on resuming hands the workspace back as it was found
Prints one line per fixture and exits 1 if any fails."""
import hashlib, itertools, json, os, random, shutil, signal, subprocess, sys, tempfile, time
sys.path.insert(0, ".")
from stillway8 import runner, opsrt_q, bank_q, world as W
runner.OPSRT = os.path.abspath(opsrt_q.__file__); runner.opsrt = opsrt_q
from stillway8.runner import Session

PUB, HID, N = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 60
PY = sys.executable; H = lambda files: hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:16]; fails = []
tmp = tempfile.mkdtemp(prefix="qself_"); pub = os.path.join(tmp, "pub.jsonl"); jobs = [json.loads(l) for l in open(PUB)][:N]; open(pub, "w").writelines(json.dumps(p) + "\n" for p in jobs); P = {p["id"]: p for p in jobs}
hid = {h["id"]: h for h in map(json.loads, open(HID))}
def say(n, ok, text): print(f"{n}  {'PASS' if ok else 'FAIL'}  {text}"); fails.append(n) if not ok else None
def run(*a, **k): return subprocess.run([PY, "v08/run_q.py", *a], capture_output=True, text=True, env=dict(os.environ, PYTHONPATH="."), **k)
load = lambda path: [json.loads(l) for l in open(path)]
key = lambda r: (r["id"], r["end"], r["final_hash"], r["q"]["status"], (r["q"]["pending"] or {}).get("digest"))
def truth(q): return W.stages(hid[q["id"]]["true"], [dict(key=a, val=b, qty=c) for a, b, c in q["rows"]])["report"][q["field"]]
def stage(d, answers, rnd=1):
    path = os.path.join(d, f"a{rnd}.jsonl"); open(path, "w").writelines(json.dumps(x) + "\n" for x in answers); x = run("resume", "searchq", pub, d, str(rnd), path); assert x.returncode == 0, x.stderr[-400:]; return load(os.path.join(d, f"searchq.r{rnd + 1}.jsonl")), x.stdout
def fresh(name): d = os.path.join(tmp, name); os.makedirs(d); shutil.copy(os.path.join(tmp, "base", "searchq.r1.jsonl"), d); return d
untouched = lambda r: r["end"] == "ASK" and not r["changed"] and not r["diff"] and r["final_hash"] == H(P[r["id"]]["files"])

# 1 ---------------------------------------------------------------- soundness of the rule
env = {n: (lambda *a: None) for n in ("patch", "revert", "check", "trial", "question", "note", "answer")}; exec(bank_q._head("selftest"), env); canon = env["canon"]; rng = random.Random(1); made = [[dict(key=k, val=v, qty=q) for k, v, q in env["_made_up"](rng, [rng.randint(1, 9)])] for _ in range(300)]
S = W.SLOTS; cfgs = [dict(norm=a, dedupe=b, cmp=c, thr=d, col=e, func=f, by=g, dir=h) for a, b, c, d, e, f, g, h in itertools.product(S["clean"]["norm"], S["clean"]["dedupe"], S["filter"]["cmp"], S["filter"]["thr"], S["agg"]["col"], S["agg"]["func"], S["order"]["by"], S["order"]["dir"])]
cls = {}; [cls.setdefault(canon(c), []).append(c) for c in cfgs]; rep = lambda c: [json.dumps(W.stages(c, d)["report"], sort_keys=True) for d in made]; bad = pairs = 0
for members in cls.values():
    if len(members) > 1:
        first = rep(members[0])
        for m in members[1:]: pairs += 1; bad += rep(m) != first
say(1, bad == 0 and pairs > 0, f"{len(cfgs)} settings fall into {len(cls)} forms; {pairs} settings share a form with another and were compared on {len(made)} inputs; {bad} disagree")

# 2 ---------------------------------------------------------------- the probe is disposable
p = jobs[0]; s = Session(p); before = s.files(); mods = {}
for m in p["mods"]:
    w = s.run(f"SHOW {m}")["obs"][0].split(); mods[w[1]] = m
script = "\n".join(f'print(trial({mods["filter"]!r}, "thr", "n{1 + i % 9}", {json.dumps([["a", 1 + i % 9, 2], ["B ", 5, 5], ["c", 9, 1]])!r}))' for i in range(20)); x = s.run(script, mode="py")
left = [n for n in os.listdir(s.dir) if n.startswith(".probe")]; say(2, s.files() == before and not left and all(o.startswith("{") for o in x["obs"]) and len(x["obs"]) == 20, f"20 probes; workspace unchanged: {s.files() == before}; scratch copies left: {len(left)}"); s.close()

# 3 ---------------------------------------------------------------- crash and restart
base = os.path.join(tmp, "base"); x = run("round1", "searchq", pub, base); assert x.returncode == 0, x.stderr[-400:]; want = load(os.path.join(base, "searchq.r1.jsonl"))
crash = os.path.join(tmp, "crash"); pr = subprocess.Popen([PY, "v08/run_q.py", "round1", "searchq", pub, crash], env=dict(os.environ, PYTHONPATH="."), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(2.0); pr.send_signal(signal.SIGKILL); pr.wait()
part = os.path.join(crash, "searchq.r1.jsonl"); n_before = len(open(part).readlines()) if os.path.exists(part) else 0; open(part, "a").write('{"id": "torn-li')
x = run("round1", "searchq", pub, crash); got = load(part) if x.returncode == 0 else []
say(3, 0 < n_before < len(jobs) and list(map(key, got)) == list(map(key, want)), f"killed after {n_before} of {len(jobs)} jobs with a torn last line; after the restart {len(got)} records, identical to an uninterrupted run: {list(map(key, got)) == list(map(key, want))}")

paused = [r for r in want if r["q"]["status"] == "paused"]; qs = [{k: r["q"]["pending"][k] for k in run_fields} for r in paused] if (run_fields := ("id", "round", "rows", "field", "predictions")) else []
right = [{"id": q["id"], "round": 1, "field": q["field"], "value": truth(q)} for q in qs]; ids = [q["id"] for q in qs]; assert len(ids) >= 6, "too few paused jobs among the first N to build the fixtures"

# 4 ---------------------------------------------------------------- duplicate delivery, and resuming twice
once, _ = stage(fresh("once"), right); twice, out = stage(fresh("dup"), right + right[:5]); again = run("resume", "searchq", pub, os.path.join(tmp, "dup"), "1", os.path.join(tmp, "dup", "a1.jsonl"))
strip = lambda rs: [(key(r), r["changed"]) for r in rs]; say(4, strip(once) == strip(twice) and "duplicate deliveries 5" in out and "already resumed" in again.stdout and strip(load(os.path.join(tmp, "dup", "searchq.r2.jsonl"))) == strip(twice),
                                                         f"5 answers delivered twice: same result as once ({strip(once) == strip(twice)}); a second resume of the round did nothing ({'already resumed' in again.stdout})")

# 5 ---------------------------------------------------------------- missing answers
got, _ = stage(fresh("missing"), right[3:]); hit = [r for r in got if r["id"] in ids[:3]]
say(5, len(hit) == 3 and all(untouched(r) and r["q"]["status"] == "clean_ask" and r["q"]["rounds"][-1]["answer_status"] == "missing" for r in hit), "3 questions left unanswered: bare ASK, workspace untouched")

# 6 ---------------------------------------------------------------- invalid answers
other = lambda f: next(x for x in ("count", "groups", "total", "first") if x != f)
badset = [dict(right[0], field=other(right[0]["field"])), dict(right[1], round=2), dict(right[2], value=[1] if isinstance(right[2]["value"], int) else 3), dict(right[3], note="extra key"), right[4], dict(right[4], value="zz"), dict(right[5], value=True)]
got, out = stage(fresh("invalid"), badset + right[6:]); hit = [r for r in got if r["id"] in ids[:6]]
say(6, len(hit) == 6 and all(untouched(r) and r["q"]["status"] == "clean_ask" for r in hit) and sum(r["q"]["rounds"][-1]["answer_status"] == "invalid" for r in hit) == 5,
    f"wrong field, wrong round (counted as missing), wrong type, extra key, two conflicting lines, a boolean: all six end in a bare ASK with the workspace untouched ({out.split(';')[0].split(': ')[1]})")

# 7 ---------------------------------------------------------------- an answer that fits no surviving change
off = [dict(a, value=62 if isinstance(a["value"], int) else "-") for a in right[:3]]; ok3 = [o for o, r in zip(off, paused[:3]) if all(s[2] != o["value"] for s in r["q"]["pending"]["survivors"])]
got, _ = stage(fresh("nofit"), ok3 + right[3:]); hit = [r for r in got if r["id"] in [o["id"] for o in ok3]]
say(7, len(hit) >= 1 and all(untouched(r) and r["q"]["status"] == "clean_ask" and any(n.get("fallback") == "the answer agrees with no surviving change" for n in r["q"]["notes"]) for r in hit), f"{len(hit)} answers that differ from both predictions and from every surviving change: bare ASK, workspace untouched")

# 8 ---------------------------------------------------------------- the question budget
r = next(r for r in paused if r["q"]["pending"]["kinds"] >= 2); st = dict(r["q"]["pending"], round=bank_q.BUDGET); st["survivors"] = [[s, v, 0] for s, v, _ in st["survivors"]]; p = P[r["id"]]; s = Session(p)
s.set_procedure(bank_q.resume_q(st, {"id": st["id"], "round": bank_q.BUDGET, "field": "count", "value": 0})); x = s.run("USE"); notes = bank_q.parse([f"{l['op']} {' '.join(l['args'])}" for l in x["ledger"]])[1]
say(8, x["obs"] == ["ASK"] and s.files() == p["files"] and any(n.get("fallback") == "question budget exhausted" for n in notes), f"{st['kinds']} kinds still alive after question {bank_q.BUDGET}: result {x['obs'][0]}, workspace untouched: {s.files() == p['files']}"); s.close()

# 9 ---------------------------------------------------------------- a failure on resuming
d = fresh("broken"); recs = load(os.path.join(d, "searchq.r1.jsonl")); victim = ids[0]
for r in recs:
    if r["id"] == victim: r["q"]["pending"]["mods"] = {k: "m9" for k in r["q"]["pending"]["mods"]}; r["q"]["pending"]["survivors"] = r["q"]["pending"]["survivors"][:1]
open(os.path.join(d, "searchq.r1.jsonl"), "w").writelines(json.dumps(r, sort_keys=True) + "\n" for r in recs); got, _ = stage(d, [dict(right[0], value=paused[0]["q"]["pending"]["survivors"][0][2])] + right[1:]); hit = next(r for r in got if r["id"] == victim)
say(9, untouched(hit) and hit["q"]["status"] == "clean_ask", f"paused state pointing at a module that does not exist: ending {hit['end']}, workspace untouched: {untouched(hit)}, notes {[n.get('fallback') for n in hit['q']['notes'] if 'fallback' in n]}")

shutil.rmtree(tmp, ignore_errors=True); print("ALL PASS" if not fails else f"FAILED: {fails}"); sys.exit(1 if fails else 0)
