"""Pack and check a folder of final repositories (for the holder of the final set).
    python v07/pack_final.py SOURCE_DIR OUT_DIR

SOURCE_DIR/<repository id>/
    public/ISSUE.md                 the bug report: symptoms only
    public/**/*.py                  the repository at the savepoint (standard library only)
    public/tests/test_visible.py    visible tests: plain functions named test_*
    hidden/test_hidden.py           hidden grading tests, same style
    hidden/meta.json                {"group": "...", "family": "...", "reference_fix": {"file": "...", "code": "..."},
                                     "old_fix": {"file": "...", "code": "..."} (optional: the trained fix applied where it does not belong)}

Writes OUT_DIR/public/<id>.json (what the student may see) and OUT_DIR/hidden/<id>.json (tests and labels: grader only), and checks by
execution: at the savepoint at least one visible and one hidden test fail; the reference fix makes every test pass; the old fix does not.
Ids in the public files should be neutral (no group or mechanism in the name)."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import episode as E, sandbox as S
src, out = sys.argv[1], sys.argv[2]; os.makedirs(os.path.join(out, "public"), exist_ok=True); os.makedirs(os.path.join(out, "hidden"), exist_ok=True); bad = 0; counts = {}
for d in sorted(glob.glob(os.path.join(src, "*", ""))):
    rid = os.path.basename(d.rstrip("/")); pub = os.path.join(d, "public"); repo = {}; problems = []
    for root, _, files in os.walk(pub):
        for f in files:
            if f.endswith(".py") or f == "ISSUE.md": repo[os.path.relpath(os.path.join(root, f), pub)] = open(os.path.join(root, f)).read()
    hidden = open(os.path.join(d, "hidden", "test_hidden.py")).read(); meta = json.load(open(os.path.join(d, "hidden", "meta.json")))
    if "ISSUE.md" not in repo or "tests/test_visible.py" not in repo: problems.append("ISSUE.md or tests/test_visible.py missing")
    else:
        vis0, _ = S.run_tests(repo, repo["tests/test_visible.py"]); hid0, _ = S.run_tests(repo, hidden); n = len(E.user_prompt(repo, [], 3)) // 3
        if all(v == "PASS" for v in vis0.values()): problems.append("no visible test fails at the savepoint")
        if all(v == "PASS" for v in hid0.values()): problems.append("no hidden test fails at the savepoint")
        if n > 2200: problems.append(f"repository too long for the prompt limit (about {n} tokens; keep under 2,200)")
        rec = {"savepoint": {"visible": vis0, "hidden": hid0}}
        if meta.get("reference_fix"):
            new, info = S.apply_patch(repo, meta["reference_fix"]["code"], meta["reference_fix"].get("file"))
            if new is None: problems.append("reference fix is not one function that exists in the repository: " + str(info))
            else:
                h1, _ = S.run_tests(new, hidden); v1, _ = S.run_tests(new, repo["tests/test_visible.py"]); rec["fix"] = {"hidden": h1, "changed_lines": info["changed_lines"], "diff": info["diff"]}
                if not all(v == "PASS" for v in list(h1.values()) + list(v1.values())): problems.append("reference fix fails a test")
        else: problems.append("no reference fix (needed to show a one-function patch can pass)")
        if meta.get("old_fix"):
            old, info = S.apply_patch(repo, meta["old_fix"]["code"], meta["old_fix"].get("file"))
            if old is None: problems.append("old fix does not apply: " + str(info))
            else:
                h2, _ = S.run_tests(old, hidden); rec["oldfix"] = {"hidden": h2, "regressions": sorted(k for k in hid0 if hid0[k] == "PASS" and h2.get(k) != "PASS")}
                if all(v == "PASS" for v in h2.values()): problems.append("old fix passes the hidden tests")
        json.dump({"id": rid, "repo": repo, "code_hash": S.code_hash(repo)}, open(os.path.join(out, "public", rid + ".json"), "w"), indent=1)
        json.dump({"id": rid, "group": meta.get("group"), "template": meta.get("family", rid), "symptom": meta.get("symptom"), "cause": meta.get("cause"), "skin": None, "hidden": hidden,
                   "fix": {"file": meta.get("reference_fix", {}).get("file"), "code": meta.get("reference_fix", {}).get("code")}, "oldfix": ({"code": meta["old_fix"]["code"]} if meta.get("old_fix") else None), "verified": rec}, open(os.path.join(out, "hidden", rid + ".json"), "w"), indent=1)
        counts[meta.get("group")] = counts.get(meta.get("group"), 0) + 1
    if problems: bad += 1; print("PROBLEM", rid, problems)
print(json.dumps({"repositories": sum(counts.values()), "by_group": counts, "with_problems": bad}, indent=1))
