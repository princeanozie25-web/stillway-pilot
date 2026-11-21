"""Compact one-screen summary of eval_dev.json / eval_sealed.json for a list of runs."""
import json, os, sys
which = "eval_sealed.json" if "--sealed" in sys.argv else "eval_dev.json"
for n in [a for a in sys.argv[1:] if not a.startswith("--")]:
    p = os.path.join("runs", n, which)
    if not os.path.exists(p): print(n, "-- no", which); continue
    d = json.load(open(p))
    c = d.get("classes") or d["classes_dev_out"]; r = d.get("replay") or d["replay_dev_out"]
    f = lambda x: f"{x:.3f}"
    print(f"{n}: plain {f(c['plain'])} dyn {f(c['dynamic'])} midrev {f(c['midplan_reversal'])} wrev {f(c['wiring_reversal'])} rswap {f(c['route_swap'])}")
    pi = r["paired_improvement_over_shuffled"]
    print(f"   swap slots {d['slots']}: targeted {f(r['primary_targeted_credit']['mean'])} shuffled {f(r['shuffled_credit'])} improve {f(pi['mean'])} [{f(pi['ci95'][0])},{f(pi['ci95'][1])}] unrel-drop {f(r['unrelated_obligation_drop_vs_unchanged']['mean'])}")
    t = r["whole_state_transplant"]; m = r["message_revision"]; dc = r["decor"]
    print(f"   transplant gate {f(t['gate'])} | msg credit {f(m['credit'])} slots-changed {m['slots_changed']:.2f} | restart {f(r['restart_full_order'])} | same-goal {f(r['same_goal_donor_stable'])} | decor same-acts {f(dc['same_actions'])} slots {dc['slots_changed_next_step']:.2f} | blank gate {f(r['blank_memory']['gate'])}")
    m = d.get("machine")
    if m and "families_with_violations" in m: print(f"   certificate: {m['pairs_checked']:,} pairs, {m['violating_pairs']:,} bad ({100*m['violating_pairs']/m['pairs_checked']:.4f}%), {len(m['families_with_violations'])}/{m['families']} families bad; states/family {m['mean_per_family']['code_states']} beh {m['mean_per_family']['behaviour_classes']}")
