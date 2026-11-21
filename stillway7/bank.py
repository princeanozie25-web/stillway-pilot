"""Retrieval over training records, the versioned diagnostic bank, and the inserts each arm may receive.

Only training material is read here: training repositories, the teacher's executed traces and the bank file.  Nothing
about a development or final repository other than its own visible files is ever used."""
import glob, json, os
from sklearn.feature_extraction.text import TfidfVectorizer
from . import episode as E
from .procedures import PROC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def query_text(repo): return repo["ISSUE.md"] + "\n" + "\n".join(repo[p] for p in sorted(repo) if p.endswith(".py") and not p.startswith("tests/"))


def trace(task):
    """The teacher's executed trace for a training task: two tests, then the patch.  Half of the tasks that have a naive
    test use it, so the trace holds a prediction that execution contradicted."""
    pr = [dict(p) for p in task["teacher"]["probes"]]; nv = task.get("naive"); use_naive = bool(nv) and sum(map(ord, task["skin"])) % 2 == 0
    if use_naive: pr = [dict(nv), pr[0]] if nv["step"] == 1 else [pr[0], dict(nv)]
    hist = [{"step": i + 1, "suspect": p["suspect"], "test": p["test"], "predict": p["predict"], "observed": p["observed"], "as_predicted": E.norm(p["observed"]) == E.norm(p["predict"])} for i, p in enumerate(pr)]
    return hist, use_naive


class Retriever:
    """Ordinary nearest-example retrieval: TF-IDF over the issue and the source files of the training repositories."""
    def __init__(self):
        self.tasks = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "data", "v07", "train", "*.json")))]
        self.vec = TfidfVectorizer(sublinear_tf=True, token_pattern=r"[A-Za-z_][A-Za-z0-9_]*|\d+", ngram_range=(1, 2), min_df=2); self.M = self.vec.fit_transform([query_text(t["repo"]) for t in self.tasks])

    def nearest(self, repo, exclude_template=None, k=1):
        sims = (self.M @ self.vec.transform([query_text(repo)]).T).toarray().ravel(); order = sims.argsort()[::-1]
        out = [(self.tasks[i], float(sims[i])) for i in order if self.tasks[i]["template"] != exclude_template]; return out[:k]


def render_example(task):
    hist, _ = trace(task); fx = task["verified"]["fix"]
    return ("SIMILAR PAST BUG (its fix was verified)\nIssue: " + task["repo"]["ISSUE.md"].strip() + "\n" +
            "\n".join(f"Test {h['step']}: {h['suspect']}\n```python\n{h['test'].rstrip()}\n```\nPredicted: {h['predict']}\nObserved: {h['observed']}" for h in hist) +
            f"\nCause: {task['teacher']['cause']}\nFix in {task['fix']['file']}, function {task['fix']['function']}:\n{fx['diff']}")


class Bank:
    def __init__(self, path=None):
        self.data = json.load(open(path or os.path.join(ROOT, "artifacts", "v07", "bank.json"))); self.log = []

    def render(self, sym, version=None):
        e = self.data["diagnostics"][sym]; v = next(x for x in e["versions"] if x["version"] == (version or e["current"])); c = v["clauses"]
        text = f"DIAGNOSTIC {sym} (version {v['version']})\nSymptom: {c['symptom']}\nTest: {c['test']}\nIf the test confirms it: {c['confirmed']}\nScope: {c['scope']}"
        if "exception" in c: text += f"\nException: {c['exception']}"
        if "contradiction" in c: text += f"\nIf the test contradicts it: {c['contradiction']}"
        return text

    def notice(self, sym, history):
        """Status of the diagnostic for this repository, from the tests run so far.  A prediction that execution contradicted reopens it."""
        if not history: return "", "candidate"
        if all(h["as_predicted"] for h in history): return "\nStatus here: the tests so far came out as predicted.", "supported"
        return (f"\nStatus here: REOPENED. A test did not come out as predicted, so {sym} is not confirmed for this repository. "
                "Verify its exception or the alternative it names before using its fix; if neither fits, do not apply its fix."), "reopened"


def provider(kind, retriever, bank=None, wrong=False, exclude_own_template=False, bank_version=None):
    """kind: 'none' | 'example' | 'bank'.  Returns the function the episode runner calls for the insert at each step."""
    def f(task, history, step):
        if kind == "none": return None, None
        (near, sim), = retriever.nearest(task["repo"], task.get("template") if exclude_own_template else None)
        if kind == "example": return render_example(near), {"kind": "example", "nearest": near["id"], "similarity": round(sim, 3)}
        sym = near["symptom"]
        if wrong: syms = sorted(bank.data["diagnostics"]); sym = syms[(syms.index(sym) + 1) % len(syms)]
        note, status = bank.notice(sym, history); bank.log.append({"task": task["id"], "step": step, "diagnostic": sym, "status": status})
        return bank.render(sym, bank_version) + note, {"kind": "bank", "diagnostic": sym, "version": bank_version or bank.data["diagnostics"][sym]["current"], "status": status, "nearest": near["id"], "similarity": round(sim, 3), "deliberately_wrong": wrong}
    return f
