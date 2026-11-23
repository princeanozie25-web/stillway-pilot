"""The stand-in respondent for development: answers a guard's question from the reference repository.

A question is one Python expression (with its import lines) and the two values the solver saw for it, before and after
its change.  The answer is the value the reference gives, which may be neither.  This file reads the hidden half of the
development tasks; it is not used on any set whose hidden half I do not hold, where the questions are sealed and sent."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repair.core import Workspace, base_files, evaluate


class Respondent:
    def __init__(self, public, hidden):
        self.P = {t["id"]: t for t in map(json.loads, open(public))}; self.asked = []
    def __call__(self, q):
        """q: {'id', 'round', 'setup', 'expr', 'predictions'} -> {'id', 'round', 'expr', 'value'}"""
        t = self.P[q["id"]]; w = Workspace(base_files(t["repo"]))                 # the repository as published is the reference
        try: v = evaluate(w, t["pythonpath"], [(q["setup"], q["expr"])])[0]
        finally: w.close()
        a = dict(id=q["id"], round=q["round"], expr=q["expr"], value=v); self.asked.append((q, a)); return a
