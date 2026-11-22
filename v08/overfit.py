"""Development overfit test: can each arm express and solve the elementary tasks at all?   python v08/overfit.py prepare | check ARM...

prepare  takes the first 240 proj and 160 tab training jobs, writes them as a job file (data/v08/overfit/) and their
         records as a small training file.
Then each arm is trained on those 400 records only (v08/train_core.py --data data/v08/overfit/records.jsonl) and run on the
same 400 jobs; `check` prints the verified share per domain.  Passing = every arm at 95% or more in both domains."""
import json, os, random, sys
sys.path.insert(0, ".")
from stillway8 import dataset as D, expert as E
from stillway8.runner import Session

if sys.argv[1] == "prepare":
    os.makedirs("data/v08/overfit", exist_ok=True); P, H, R = [], [], []
    for dom, n in (("proj", 240), ("tab", 160)):
        srcs = D.sources(dom, "train"); i = 0
        while sum(p["dom"] == dom for p in P) < n:
            g = D.train_group(dom, i); j = D.make(dom, "train", i, g, srcs); i += 1
            if j is None: continue
            p, h = j; rec = {"i": i - 1, "dom": dom}
            for name, noise in (("clean", 0.0), ("noisy", 0.3)):
                s = Session(p, fast=True); steps, end = E.teach(s, p, h, random.Random(f"{D.MASTER}-{dom}-{i - 1}"), noise); s.close(); t, k = E.encode(p, steps, end); rec[name] = [" ".join(t), "".join(map(str, k))]
            P.append(p); H.append(h); R.append(rec)
    for name, rows in (("public", P), ("hidden", H), ("records", R)): open(f"data/v08/overfit/{name}.jsonl", "w").writelines(json.dumps(x, sort_keys=True) + "\n" for x in rows)
    print(len(P), "jobs")
else:
    ok = True
    for arm in sys.argv[2:]:
        R = [json.loads(l) for l in open(f"results/v08/overfit/{arm}_s1.graded.jsonl")]
        for dom in ("proj", "tab"):
            r = [x for x in R if x["dom"] == dom]; v = 100 * sum(x["outcome"] == "verified" for x in r) / len(r); ok &= v >= 95; print(f"{arm} {dom}: {v:.1f}% verified of {len(r)}")
    print("OVERFIT TEST", "PASSED" if ok else "NOT PASSED")
