"""Diff two failing-ID files of the seed-4 sweep (v04/seed4_ticket.py):   python v04/seed4_diff.py A.json B.json
Each file needs {"failing_ids": {episode ID: first invalid stage}} or a plain list of episode IDs."""
import json, sys
def load(p):
    d = json.load(open(p)); d = d.get("failing_ids", d) if isinstance(d, dict) else d
    return set(d)
a, b = load(sys.argv[1]), load(sys.argv[2])
print(len(a), "in A;", len(b), "in B;", len(a & b), "in both")
print("only in A:", sorted(a - b)); print("only in B:", sorted(b - a))
