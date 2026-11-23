"""A stand-in for the private respondent, for development jobs whose hidden half I hold.   python v08/q_dev_answer.py HIDDEN.jsonl QUESTIONS.jsonl ANSWERS.jsonl

For each question {id, round, rows, field, predictions} it writes {id, round, field, value}: the value of that field in the
report the intended project gives for those rows (reference semantics on the hidden intended settings).  It does not look
at the predictions.  On Codex's set the answers come from Codex's own respondent; this script is not used there."""
import json, sys
sys.path.insert(0, ".")
from stillway8 import world as W
hid = {h["id"]: h for h in map(json.loads, open(sys.argv[1]))}; n = 0
with open(sys.argv[3], "w") as f:
    for q in map(json.loads, open(sys.argv[2])):
        assert set(q) == {"id", "round", "rows", "field", "predictions"} and len(q["predictions"]) == 2 and q["predictions"][0] != q["predictions"][1], "a malformed question"
        v = W.stages(hid[q["id"]]["true"], [dict(key=a, val=b, qty=c) for a, b, c in q["rows"]])["report"][q["field"]]; f.write(json.dumps({"id": q["id"], "round": q["round"], "field": q["field"], "value": v}, sort_keys=True) + "\n"); n += 1
print(n, "answers")
