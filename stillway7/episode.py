"""One episode: two proposed tests, each with a prediction made before it is run, then one submitted patch.
Every arm gets the same system text, the same tools and the same limits.  Only the optional insert differs."""
import re, time
from . import sandbox as S

LIMITS = {"tests": 2, "patches": 1, "test_new_tokens": 160, "patch_new_tokens": 320, "prompt_tokens": 3072, "insert_tokens": 400, "test_seconds": 5.0, "observed_chars": 400}
SYSTEM = ("You fix bugs in small Python repositories. You work in three steps. In steps 1 and 2 you propose one short test script and predict its exact "
          "output before it is run. In step 3 you submit one patch: the full corrected text of the one function or method that contains the bug, and nothing else.\n\n"
          "Example of the three answers, for a bug where `area(w, h)` in shapes.py returns `w + h`:\n\n"
          "Step 1 answer:\nSUSPECT: area() may add the sides instead of multiplying them.\nTEST:\n```python\nfrom shapes import area\nprint(area(2, 5))\n```\nPREDICT: 7\n\n"
          "Step 2 answer:\nSUSPECT: If it adds, a zero side still gives a non-zero area.\nTEST:\n```python\nfrom shapes import area\nprint(area(0, 4))\n```\nPREDICT: 4\n\n"
          "Step 3 answer:\nFILE: shapes.py\n```python\ndef area(w, h):\n    return w * h\n```\n\n"
          "PREDICT is only the text the script will print, with no words around it. Each test must be different from the earlier ones. Stop after the answer.")
ASK_TEST = ("STEP %d OF 3. Write a short test script that helps find the cause of the issue. It runs in a fresh copy of the repository; print what you want to see.\n"
            "Answer in this format and then stop:\nSUSPECT: <one sentence>\nTEST:\n```python\n<script>\n```\nPREDICT: <the exact output you expect>")
ASK_PATCH = ("STEP 3 OF 3. Submit your patch. Rewrite in full the ONE function or method that contains the bug, changed so that the issue is fixed. Do not repeat any other code.\n"
             "Answer in this format and then stop:\nFILE: <path of the file that holds the function>\n```python\n<the whole corrected function>\n```")


def render_repo(repo):
    files = sorted(p for p in repo if p.endswith(".py") and not p.startswith("tests/")) + sorted(p for p in repo if p.startswith("tests/"))
    return "FILES\n" + "\n".join(f"### {p}\n```python\n{repo[p].rstrip()}\n```" for p in files) + "\n\nISSUE (reported by a user)\n" + repo["ISSUE.md"].strip()


def norm(text): return "\n".join(l.rstrip() for l in (text or "").strip().splitlines())


def render_history(history):
    out = []
    for i, h in enumerate(history):
        out.append(f"TEST {i + 1}\nSUSPECT: {h['suspect']}\n```python\n{h['test'].rstrip()}\n```\nPREDICTED: {h['predict']}\nOBSERVED: {h['observed']}\nRESULT: {'as predicted' if h['as_predicted'] else 'NOT as predicted'}")
    return "\n\n".join(out)


def user_prompt(repo, history, step, insert=None):
    parts = [render_repo(repo)]
    if insert: parts.append(insert.strip())
    if history: parts.append("EARLIER STEPS\n" + render_history(history))
    parts.append(ASK_TEST % step if step < 3 else ASK_PATCH); return "\n\n".join(parts)


def target_test(suspect, test, predict): return f"SUSPECT: {suspect}\nTEST:\n```python\n{test.rstrip()}\n```\nPREDICT: {predict}"
def target_patch(path, code, cause=None): return (f"CAUSE: {cause}\n" if cause else "") + f"FILE: {path}\n```python\n{code.rstrip()}\n```"

_BLOCK = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.S)


def parse_test(text):
    m = _BLOCK.search(text); script = m.group(1) if m else ""; s = re.search(r"SUSPECT:[ \t]*(.*)", text); p = re.search(r"PREDICT(?:ED)?:[ \t]*(.*)", text[m.end():] if m else text, re.S)
    pred = re.split(r"\n(?:OBSERVED|RESULT|SUSPECT|TEST|STEP|FILE)\b|\n```", p.group(1))[0] if p else ""; pred = norm(pred).strip("`")
    return {"suspect": (s.group(1).strip() if s else "")[:300], "test": script, "predict": pred[:400], "well_formed": bool(m and p)}


def parse_patch(text):
    m = _BLOCK.search(text); f = re.search(r"FILE:[ \t]*(\S+)", text); c = re.search(r"CAUSE:[ \t]*(.*)", text)
    code = m.group(1) if m else (text[text.index("def "):] if "def " in text else "")
    return {"file": f.group(1).strip("`'\"") if f else None, "code": code, "cause": (c.group(1).strip() if c else "")[:300], "well_formed": bool(m and f)}


def run_episodes(student, tasks, provider, arm, batch=8, log=None):
    """tasks: [{"id", "repo", "code_hash"}].  provider(task, history, step) -> (insert text or None, meta).  Returns one record per task, ungraded."""
    recs = {t["id"]: {"task": t["id"], "arm": arm, "code_hash": t["code_hash"], "accessible_files": sorted(t["repo"]), "limits": LIMITS, "tests": [], "inserts": [], "generation_seconds": 0.0, "tool_seconds": 0.0,
                      "prompt_tokens": 0, "new_tokens": 0, "tool_calls": 0} for t in tasks}
    hist = {t["id"]: [] for t in tasks}; order = sorted(tasks, key=lambda t: len(render_repo(t["repo"])))
    for step in (1, 2, 3):
        for i in range(0, len(order), batch):
            chunk = order[i:i + batch]; prompts = []
            for t in chunk:
                ins, meta = provider(t, hist[t["id"]], step); recs[t["id"]]["inserts"].append({"step": step, "meta": meta, "text": ins})
                prompts.append(student.chat(SYSTEM, user_prompt(t["repo"], hist[t["id"]], step, ins)))
            t0 = time.time(); texts, npr, nnew = student.generate(prompts, LIMITS["test_new_tokens"] if step < 3 else LIMITS["patch_new_tokens"], LIMITS["prompt_tokens"]); dt = time.time() - t0
            for t, text, a, b in zip(chunk, texts, npr, nnew):
                r = recs[t["id"]]; r["generation_seconds"] += dt / len(chunk); r["prompt_tokens"] += a; r["new_tokens"] += b
                if step < 3:
                    p = parse_test(text)
                    if p["test"].strip(): obs, secs = S.run_script(t["repo"], p["test"], LIMITS["test_seconds"], LIMITS["observed_chars"])
                    else: obs, secs = "(no test script was given)", 0.0
                    h = {"step": step, "raw": text, "suspect": p["suspect"], "test": p["test"], "predict": p["predict"], "observed": obs, "as_predicted": bool(p["predict"]) and norm(obs) == p["predict"], "well_formed": p["well_formed"], "seconds": secs}
                    hist[t["id"]].append(h); r["tests"].append(h); r["tool_seconds"] += secs; r["tool_calls"] += 1
                else:
                    p = parse_patch(text); new, info = S.apply_patch(t["repo"], p["code"], p["file"]) if p["code"].strip() else (None, "no code in the answer")
                    r["patch"] = {"raw": text, "file": p["file"], "code": p["code"], "cause": p["cause"], "well_formed": p["well_formed"], "applied": new is not None, "info": info}; r["_patched"] = new
            if log: log(f"{arm} step {step} {min(i + batch, len(order))}/{len(order)}")
    return [recs[t["id"]] for t in tasks]


def grade(rec, repo, visible, hidden, savepoint):
    """Hidden grading of the first submitted patch.  savepoint: test results before any patch."""
    new = rec.pop("_patched", None)
    if new is None: rec["outcome"] = {"first_patch_correct": False, "why": "patch did not apply", "hidden": None, "visible": None, "regressions": [], "visible_regressions": []}; return rec
    t0 = time.time(); hid, _ = S.run_tests(new, hidden); vis, _ = S.run_tests(new, visible)
    rec["outcome"] = {"first_patch_correct": all(v == "PASS" for v in hid.values()), "hidden": hid, "visible": vis, "visible_all_pass": all(v == "PASS" for v in vis.values()),
                      "regressions": sorted(k for k, v in savepoint["hidden"].items() if v == "PASS" and hid.get(k) != "PASS"), "visible_regressions": sorted(k for k, v in savepoint["visible"].items() if v == "PASS" and vis.get(k) != "PASS"), "grading_seconds": round(time.time() - t0, 2)}
    return rec
