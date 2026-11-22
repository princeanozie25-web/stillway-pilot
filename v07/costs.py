"""Costs that are not matched across arms, reported separately.   python v07/costs.py   -> results/v07/COSTS.json"""
import glob, json, os, re
T = lambda f: open(f).read(); out = {}
tr, dv, pr = T("stillway7/templates_train.py"), T("stillway7/templates_dev.py"), T("stillway7/procedures.py")
out["teacher_authoring"] = {"training_templates": len(re.findall(r"^T\.append", tr, re.M)), "development_templates": len(re.findall(r"^D\.append", dv, re.M)), "lines_training_templates": tr.count("\n"), "lines_development_templates": dv.count("\n"),
                            "lines_diagnostic_wording_and_naive_tests": pr.count("\n"), "author": "Fable (a much larger model than the student); not counted in any arm's budget",
                            "used_by": {"B final patches": "the reference fix of each training repository", "C, D, E, F, W": "the reference fix, two teacher tests per repository with predictions, the naive (contradicted) tests", "D, W only": "the diagnostic wording in the bank"}}
b = json.load(open("data/v07/BUILD_SUMMARY.json")); tasks = [json.load(open(f)) for f in glob.glob("data/v07/train/*.json")]
out["teacher_execution"] = {"build_and_verify_all_192_repositories_seconds": b["seconds"], "teacher_test_runs_on_training_repositories": sum(len(t["teacher"]["probes"]) + (1 if t.get("naive") else 0) for t in tasks), "prior_fix_executions_that_failed": sum(1 for t in tasks if t.get("oldfix"))}
base = [json.loads(l) for l in open("results/v07/records/base_on_train.jsonl")]
out["students_own_attempts_on_training_repositories"] = {"episodes": len(base), "first_patch_correct": sum(r["outcome"]["first_patch_correct"] for r in base), "generation_seconds": round(sum(r["generation_seconds"] for r in base), 1), "tool_seconds": round(sum(r["tool_seconds"] for r in base), 1),
                                                         "used_by": "B only: half of its training prompts carry the unchanged student's own two tests on that repository"}
out["adapter_training"] = {os.path.basename(f)[:-5]: {k: json.load(open(f))[k] for k in ("updates", "token_budget_per_update", "training_tokens", "examples_seen", "passes_started", "seconds")} for f in sorted(glob.glob("artifacts/v07/adapters/*.json"))}
bank = json.load(open("artifacts/v07/bank.json")); out["bank"] = {"bytes": os.path.getsize("artifacts/v07/bank.json"), "diagnostics": len(bank["diagnostics"]), "versions_kept": sum(len(d["versions"]) for d in bank["diagnostics"].values()), "training_records_behind_it": len(tasks)}
json.dump(out, open("results/v07/COSTS.json", "w"), indent=1); print(json.dumps({k: v for k, v in out.items() if k != "adapter_training"}, indent=1)[:1500]); print({k: (v["training_tokens"], v["examples_seen"], v["seconds"]) for k, v in out["adapter_training"].items()})
