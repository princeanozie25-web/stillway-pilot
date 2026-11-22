"""Grade records.   python v08/grade.py PUBLIC.jsonl HIDDEN.jsonl RECORDS.jsonl [more RECORDS...]

The only v0.8 script that opens a hidden file.  Writes <records>.graded.jsonl beside each input: the record plus the
independent outcome and the labels needed for the tables."""
import json, sys
sys.path.insert(0, ".")
from stillway8.agent import final_files
from stillway8.grade import grade

pub = {p["id"]: p for p in map(json.loads, open(sys.argv[1]))}; hid = {h["id"]: h for h in map(json.loads, open(sys.argv[2]))}
for path in sys.argv[3:]:
    out = []
    for r in map(json.loads, open(path)):
        p, h = pub[r["id"]], hid[r["id"]]; g = grade(p, h, final_files(p, r), r["end"])
        out.append({**{k: v for k, v in r.items() if k != "changed"}, "outcome": g["outcome"], "detail": g["detail"], "group": h["group"], "family": h["family"], "mech": h["mech"], "route": h["route"], "kind": h["kind"], "teacher": h.get("teacher")})
    open(path.replace(".jsonl", ".graded.jsonl"), "w").writelines(json.dumps(x, sort_keys=True) + "\n" for x in out)
    n = len(out); v = sum(x["outcome"] == "verified" for x in out); print(f"{path}: {v}/{n} verified, {sum(x['outcome'] == 'wrong' for x in out)} wrong, {sum(x['outcome'] == 'abstained' for x in out)} abstained, {sum(x['outcome'] == 'budget' for x in out)} out of budget")
