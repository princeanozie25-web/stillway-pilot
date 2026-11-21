"""Print a compact view of episode records.   python v07/show_records.py FILE.jsonl [n full examples]"""
import json, sys
rs = [json.loads(l) for l in open(sys.argv[1])]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 0
for r in rs:
    o = r["outcome"]; print(r["task"], "OK" if o["first_patch_correct"] else "--", "| fn", r["patch"]["info"]["function"] if r["patch"]["applied"] else "NOT APPLIED: " + str(r["patch"]["info"]), "| predicted right", [h["as_predicted"] for h in r["tests"]], "| regress", len(o["regressions"]), "| tok", r["prompt_tokens"], r["new_tokens"])
print("correct", sum(r["outcome"]["first_patch_correct"] for r in rs), "of", len(rs), "| applied", sum(r["patch"]["applied"] for r in rs), "| predictions right", sum(h["as_predicted"] for r in rs for h in r["tests"]), "of", sum(len(r["tests"]) for r in rs), "| mean new tokens", sum(r["new_tokens"] for r in rs) // len(rs))
for r in rs[:: max(1, len(rs) // max(n, 1))][:n]:
    print("=====", r["task"])
    for h in r["tests"]: print("--- test", h["step"], "| predict:", repr(h["predict"][:80]), "| observed:", repr(h["observed"][:100])); print(h["raw"][:320])
    print("--- patch raw:", r["patch"]["raw"][:500])
