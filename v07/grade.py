"""Hidden grading of ungraded records.  The grader side: the only script that reads hidden tests.
    python v07/grade.py TASKS_DIR HIDDEN_DIR RECORDS_DIR
For each record the first submitted patch is applied to a fresh copy of the savepoint and the hidden and visible tests are run.
Writes RECORDS_DIR/graded/<same name>.jsonl (record plus outcome).  Group and template labels are added only here."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import episode as E, sandbox as S
tasks_dir, hidden_dir, rec_dir = sys.argv[1:4]; pub = {t["id"]: t for t in (json.load(open(f)) for f in glob.glob(os.path.join(tasks_dir, "*.json")))}; hid = {t["id"]: t for t in (json.load(open(f)) for f in glob.glob(os.path.join(hidden_dir, "*.json")))}
os.makedirs(os.path.join(rec_dir, "graded"), exist_ok=True)
for f in sorted(glob.glob(os.path.join(rec_dir, "*.jsonl"))):
    out = os.path.join(rec_dir, "graded", os.path.basename(f))
    if os.path.exists(out): continue
    rows = []
    for l in open(f):
        r = json.loads(l); t = pub[r["task"]]; h = hid[r["task"]]; assert r["code_hash"] == t["code_hash"]
        r["_patched"] = S.apply_patch(t["repo"], r["patch"]["code"], r["patch"]["file"])[0] if r["patch"]["code"].strip() else None
        E.grade(r, t["repo"], t["repo"]["tests/test_visible.py"], h["hidden"], h["verified"]["savepoint"])
        r["labels"] = {k: h.get(k) for k in ("group", "template", "symptom", "cause", "skin")}
        if h.get("oldfix") and r["patch"]["applied"]:      # did the student submit the trained fix where it does not belong?
            old = S.apply_patch(t["repo"], h["oldfix"]["code"], h["fix"]["file"])[0]; new = S.apply_patch(t["repo"], r["patch"]["code"], r["patch"]["file"])[0]
            r["outcome"]["same_failures_as_old_fix"] = (not r["outcome"]["first_patch_correct"]) and sorted(k for k, v in r["outcome"]["hidden"].items() if v != "PASS") == sorted(k for k, v in h["verified"]["oldfix"]["hidden"].items() if v != "PASS")
        rows.append(r)
    open(out, "w").write("".join(json.dumps(r) + "\n" for r in rows)); print(os.path.basename(f), "first patch correct", sum(r["outcome"]["first_patch_correct"] for r in rows), "of", len(rows), flush=True)
