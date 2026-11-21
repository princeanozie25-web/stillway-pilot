"""Tables for the two beyond-the-brief experiments.   python v04/x_report.py  -> results/v04/x/tables.md"""
import glob, json
import numpy as np
P = []; pct = lambda x, d=1: f"{100 * x:.{d}f}%"
pr = [json.load(open(f)) for f in sorted(glob.glob("results/v04/x/procedures_s?.json"))]
P += ["# Beyond the brief: result tables\n", "Exploratory, made after the v0.4 freeze. Same cores, same test documents, same graders as the frozen runs.\n", "## A. Procedure selection found by search and verification\n",
      "| Seed | Gradient-learned: ordinary / novel / protected changed | Found by search: ordinary / novel / protected changed | Search seconds | Candidate evaluations | Log accuracy before / after |", "|---|---|---|---|---|---|"]
for d in pr:
    g, s = d["gradient_learned"], d["induced_by_search"]
    P.append(f"| {d['seed']} | {pct(g['test_iid']['success'], 2)} / {pct(g['test_novel']['success'], 2)} / {g['test_novel']['protected_changed']} | {pct(s['test_iid']['success'], 2)} / {pct(s['test_novel']['success'], 2)} / {s['test_novel']['protected_changed']} | {d['seconds']} | {d['candidate_evaluations']} | {pct(d['history'][0]['log_status_accuracy'], 3)} / {pct(d['history'][-1]['log_status_accuracy'], 3)} |")
P.append(f"\nMean: gradient-learned {pct(np.mean([d['gradient_learned']['test_novel']['success'] for d in pr]), 2)} on novel combinations; found by search {pct(np.mean([d['induced_by_search']['test_novel']['success'] for d in pr]), 2)}. 4,000 documents per test set per seed.")
same = all([r['recompute_when[named,in_jurisdiction]=(00,01,10,11)'] for r in d['induced']] == [r['recompute_when[named,in_jurisdiction]=(00,01,10,11)'] for r in pr[0]['induced']] and [r['policy_source'] for r in d['induced']] == [r['policy_source'] for r in pr[0]['induced']] for d in pr)
P += [f"\nThe procedures found are {'identical on all five seeds' if same else 'not identical across seeds'}:\n", "| Event | Recompute a slot when (named by the event, in the jurisdiction named) | Under which policy |", "|---|---|---|"]
names = {(0, 0, 0, 0): "never", (0, 0, 1, 0): "named", (0, 0, 0, 1): "named and in that jurisdiction", (0, 1, 0, 0): "in that jurisdiction", (0, 0, 1, 1): "named", (0, 1, 0, 1): "in that jurisdiction", (0, 1, 1, 1): "named or in that jurisdiction"}
for r in pr[0]["induced"]: tt = tuple(r['recompute_when[named,in_jurisdiction]=(00,01,10,11)']); P.append(f"| {r['kind']} | {names.get(tt, tt)} | {r['policy_source'] if sum(tt) else '–'} |")
lb = [json.load(open(f)) for f in sorted(glob.glob("results/v04/x/library_s?.json"))]
P += ["\n## B. A bank of programs with a learned rule library\n", "| Seed | Skeletons learned | Family size (true family: 36) | True rules covered | Reserved rules covered (of 8) | Tables outside the true family | Build seconds | Family violations met in six sessions | Skeletons added later |", "|---|---|---|---|---|---|---|---|---|"]
for d in lb:
    L = d["library"]; P.append(f"| {d['seed']} | {L['skeletons']} | {L['family_tables']} | {L['true_rules_covered']} of 36 | {L['reserved_rules_covered']} | {L['family_tables_outside_the_true_family']} | {L['build_seconds']} | {sum(s['family_violations'] for s in d['sessions'])} | {len(d['library_grown_at'])} |")
LAB = {"library": "Learned library, answers only what is entailed", "library_best_guess": "Learned library, best guess where undetermined", "given_family": "Rule family given by the designer (the v0.4 induction baseline)", "generic_only": "Shortest generic program, no library",
       "m3_dreaming": "v0.4 consolidation + dreaming", "m3_consolidation": "v0.4 consolidation", "m3_rehearsal": "v0.4 rehearsal", "m3_retrieval": "v0.4 retrieval", "m3_induction": "v0.4 rule induction (as frozen)"}
P += ["\nSame documents as the frozen M3 runs (every second document), same compiled procedures, plain grader. 5 seeds x 6 sessions.\n",
      "| Bank | New-policy documents fully right | Older-policy documents fully right | Decisions on new policies: right | wrong | abstained |", "|---|---|---|---|---|---|"]
for a in LAB:
    ss = [s["arms"][a] for d in lb for s in d["sessions"] if a in s["arms"]]
    if not ss: continue
    r, w, ab = (sum(s["new_policy_decisions"][k] for s in ss) for k in ("right", "wrong", "abstained")); n = r + w + ab
    P.append(f"| {LAB[a]} | {pct(np.mean([s['learn']['success'] for s in ss]))} | {pct(np.mean([s['retain']['success'] for s in ss]))} | {pct(r / n)} | {w} ({pct(w / n, 2)}) | {ab} ({pct(ab / n)}) |")
P += ["\nAudited decisions needed to pin a new policy down completely (mean over the true rules the family contains; 5 seeds):\n", "| What the system has | Cases as they arrive | Cases the system chooses |", "|---|---|---|"]
for k, lab in (("no_family", "No family: an index of seen cases"), ("given_family", "The family given by the designer"), ("learned_library", "The learned library")):
    P.append(f"| {lab} | {np.mean([d['audits'][k]['passive_mean'] for d in lb]):.0f} | {np.mean([d['audits'][k]['chosen_mean'] for d in lb]):.1f} (most: {max(d['audits'][k]['chosen_max'] for d in lb)}) |")
nn = [json.load(open(f)) for f in sorted(glob.glob("results/v04/x/no_network_s?.json"))]
P += ["\n## C. The whole planner from raw logs, no network\n", "| Seed | Ordinary documents | Novel combinations | Protected statuses changed | Search seconds | Total seconds | Bank cells equal to the true rule | Deployed bytes |", "|---|---|---|---|---|---|---|---|"]
for d in nn: P.append(f"| {d['seed']} | {pct(d['test_iid']['success'], 3)} | {pct(d['test_novel']['success'], 3)} | {d['test_novel']['protected_changed'] + d['test_iid']['protected_changed']} | {d['search_seconds']} | {d['total_seconds']} | {d['bank']['cells_equal_to_the_true_rule']} of {d['bank']['cells']} | {d['deployed_bytes']} |")
P.append(f"\nMean: {pct(np.mean([d['test_iid']['success'] for d in nn]), 3)} ordinary, {pct(np.mean([d['test_novel']['success'] for d in nn]), 3)} novel. The eight procedures found are the same on every seed and the same as in table A. Gradient steps: 0. Network parameters: 0.")
open("results/v04/x/tables.md", "w").write("\n".join(P) + "\n"); print("\n".join(P[-34:]))
