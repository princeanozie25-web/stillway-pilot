"""Build development tasks from author-written bugs.   python repair/build_tasks.py OUTDIR

For every bug in repair/dev_bugs.py: put the bug into the pinned repository, run the repository's own tests, and split them.
  hidden   the tests the bug breaks (fail_to_pass) and every other test that passed before (pass_to_pass)
  visible  the repository's tests with the broken ones cut out, so that everything a solver can run passes at the start
A task is kept only if the bug breaks at least one test and at most 60, the visible tests pass with the bug in place, and
they pass again on the reference.  Writes OUTDIR/public.jsonl (what a solver gets) and OUTDIR/hidden.jsonl (the grader's)."""
import ast, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repair.core import Workspace, base_files, manifest, run_tests, evaluate
from repair.dev_bugs import REPOS, BUGS


def strip_tests(src, kill):
    """Cut the test functions named in kill, a set of (class or None, function), out of a test file."""
    lines = src.splitlines(keepends=True); cuts = []
    def visit(body, cls):
        for n in body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and (cls, n.name) in kill:
                cuts.append((min([n.lineno] + [d.lineno for d in n.decorator_list]), n.end_lineno, " " * n.col_offset + "pass\n" if len(body) == 1 else ""))
            elif isinstance(n, ast.ClassDef): visit(n.body, n.name)
    visit(ast.parse(src).body, None)
    for a, b, fill in sorted(cuts, reverse=True): lines[a - 1:b] = [fill] if fill else []
    out = "".join(lines); ast.parse(out); return out, len(cuts)


def run(files, cfg):
    w = Workspace(files); r = run_tests(w, cfg["pythonpath"], cfg["tests"]); w.close(); return r


def main(out):
    os.makedirs(out, exist_ok=True); man = manifest(); base_runs = {}; pub, hid = [], []
    for b in BUGS:
        repo, cfg = b["repo"], REPOS[b["repo"]]; base = base_files(repo)
        if repo not in base_runs:
            r = base_runs[repo] = run(base, cfg); again = run(base, cfg)
            assert r["results"] == again["results"], f"{repo}: the reference tests are not repeatable"
            n = lambda k: sum(v == k for v in r["results"].values()); print(f"{repo}: reference {n('passed')} passed, {n('failed') + n('error')} not passing (left out), {n('skipped')} skipped")
        ref = base_runs[repo]; good = {t for t, v in ref["results"].items() if v == "passed"}; never = {t for t, v in ref["results"].items() if v in ("failed", "error")}
        buggy = dict(base)
        for path, old, new in b["edits"]:
            assert buggy[path].count(old) == 1, f"{b['id']}: the span to replace occurs {buggy[path].count(old)} times in {path}"; buggy[path] = buggy[path].replace(old, new)
        r = run(buggy, cfg); broke = sorted(t for t in good if r["results"].get(t) != "passed")
        wb, wr = Workspace(buggy), Workspace(base); got, want = evaluate(wb, cfg["pythonpath"], b["examples"]), evaluate(wr, cfg["pythonpath"], b["examples"]); wb.close(); wr.close()
        for (_, e), g, w in zip(b["examples"], got, want): print(f"      {e}\n        with the bug: {g}\n        reference:    {w}")
        assert b["examples"] and all(g != w for g, w in zip(got, want)), f"{b['id']}: an example does not show the bug"
        if not 1 <= len(broke) <= 60: print(f"  !! {b['id']}: the bug breaks {len(broke)} tests; SKIPPED"); continue
        assert all(t in ref["files"] for t in broke), f"{b['id']}: a broken test has no source position"
        kill = {}
        for t in set(broke) | never:
            if t in ref["files"]: f, cls, fn = ref["files"][t]; kill.setdefault(f, set()).add((cls, fn))
        visible = dict(buggy); cut = 0
        for f, ks in kill.items(): visible[f], k = strip_tests(visible[f], ks); cut += k
        v1 = run(visible, cfg); bad1 = [t for t, v in v1["results"].items() if v in ("failed", "error")]
        if bad1:                                                       # tests inherited from a shared base class: cut them where they are defined
            names = {t.split("::")[-1].split("[")[0] for t in bad1}
            for f in list(visible):
                if f.endswith(".py") and any(n in visible[f] for n in names):
                    tree = ast.parse(visible[f]); ks = {(c.name, n.name) for c in ast.walk(tree) if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names}
                    if ks: visible[f], k = strip_tests(visible[f], ks); cut += k
            v1 = run(visible, cfg); bad1 = [t for t, v in v1["results"].items() if v in ("failed", "error")]
        assert not bad1 and v1["results"], f"{b['id']}: visible tests do not pass with the bug in place: {bad1[:3]}"
        fixed = dict(visible); fixed.update({p: base[p] for p, _, _ in b["edits"]}); v2 = run(fixed, cfg)
        assert not [t for t, v in v2["results"].items() if v in ("failed", "error")], f"{b['id']}: visible tests fail on the reference"
        overlay = {p: visible[p] for p in visible if visible[p] != base[p]}
        pub.append(dict(id=b["id"], repo=repo, archive_sha256=man[repo]["sha256"], report=b["report"], pythonpath=cfg["pythonpath"], tests=cfg["tests"], overlay=overlay))
        hid.append(dict(id=b["id"], repo=repo, fail_to_pass=broke, pass_to_pass=sorted(good - set(broke)), reference={p: base[p] for p in overlay}, bug_files=sorted({p for p, _, _ in b["edits"]}),
                        kind=b.get("kind", ""), examples=[dict(setup=s, expr=e, bug=g, reference=w) for (s, e), g, w in zip(b["examples"], got, want)]))
        print(f"  {b['id']}: breaks {len(broke)} tests; {cut} test functions cut from the visible copy; {len(v1['results'])} visible tests pass")
    for name, rows in (("public", pub), ("hidden", hid)): open(os.path.join(out, name + ".jsonl"), "w").writelines(json.dumps(x, sort_keys=True) + "\n" for x in rows)
    print(f"{len(pub)} tasks written to {out}")


if __name__ == "__main__": main(sys.argv[1])
