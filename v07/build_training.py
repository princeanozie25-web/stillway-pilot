"""Build the three training sets from the same 120 training repositories.   python v07/build_training.py
  patches       the final patch only (step 3).  Half of the prompts carry the unchanged student's own two tests on that repository, so the
                prompt looks like what this arm will see at test time; none carries a teacher test.
  experience    the teacher's executed trace: test 1, test 2 (each with its prediction and what was observed), then the patch with its cause.
  experience_x  the same traces; a third of the repositories carry a bank diagnostic, a third the nearest past example (never from the same
                template), a third nothing.  Used by the bank arm, the retrieval arm and the bank-disabled arm.
Writes data/v07/training/<name>.jsonl and a summary."""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stillway7 import bank as BK, episode as E
R = BK.Retriever(); bank = BK.Bank(); base = {json.loads(l)["task"]: json.loads(l) for l in open("results/v07/records/base_on_train.jsonl")}; os.makedirs("data/v07/training", exist_ok=True)
sets = {"patches": [], "experience": [], "experience_x": []}; conds = {}
for t in R.tasks:
    hist, naive = BK.trace(t); h = int(hashlib.sha256(t["id"].encode()).hexdigest()[:8], 16); fix = t["fix"]
    own = [{k: x[k] for k in ("step", "suspect", "test", "predict", "observed", "as_predicted")} for x in base[t["id"]]["tests"]] if h % 2 else []
    sets["patches"].append({"task": t["id"], "step": 3, "user": E.user_prompt(t["repo"], own, 3), "target": E.target_patch(fix["file"], fix["code"]), "history": "own tests" if own else "none"})
    cond = ("none", "bank", "example")[(h // 2) % 3]; conds[cond] = conds.get(cond, 0) + 1; prov = BK.provider(cond, R, bank, exclude_own_template=True)
    for step in (1, 2, 3):
        tgt = E.target_test(hist[step - 1]["suspect"], hist[step - 1]["test"], hist[step - 1]["predict"]) if step < 3 else E.target_patch(fix["file"], fix["code"], t["teacher"]["cause"])
        sets["experience"].append({"task": t["id"], "step": step, "user": E.user_prompt(t["repo"], hist[:step - 1], step), "target": tgt, "contradicted_trace": naive})
        ins, meta = prov(t, hist[:step - 1], step); sets["experience_x"].append({"task": t["id"], "step": step, "user": E.user_prompt(t["repo"], hist[:step - 1], step, ins), "target": tgt, "contradicted_trace": naive, "insert": meta})
from transformers import AutoTokenizer
from stillway7.student import PIN
tok = AutoTokenizer.from_pretrained(PIN["path"]); summ = {"insert_conditions_by_repository": conds}
for name, rows in sets.items():
    for r in rows: r["tokens"] = len(tok(tok.apply_chat_template([{"role": "system", "content": E.SYSTEM}, {"role": "user", "content": r["user"]}], tokenize=False, add_generation_prompt=True) + r["target"])["input_ids"]) + 1; r["target_tokens"] = len(tok(r["target"])["input_ids"]) + 1
    open(f"data/v07/training/{name}.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows))
    summ[name] = {"examples": len(rows), "source_repositories": len({r["task"] for r in rows}), "tokens_per_pass": sum(r["tokens"] for r in rows), "target_tokens_per_pass": sum(r["target_tokens"] for r in rows), "longest_example": max(r["tokens"] for r in rows),
                  "sha256": hashlib.sha256(open(f"data/v07/training/{name}.jsonl", "rb").read()).hexdigest()}
summ["traces_with_a_contradicted_prediction"] = sum(r["contradicted_trace"] for r in sets["experience"]) // 3; json.dump(summ, open("data/v07/training/SUMMARY.json", "w"), indent=1); print(json.dumps(summ, indent=1))
