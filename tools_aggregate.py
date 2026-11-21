"""Collect every final run into markdown tables.

    python tools_aggregate.py [--sealed]      -> results/tables_dev.md or results/tables_sealed.md (+ .json)
"""
import glob, json, os, re, sys
import numpy as np
sealed = "--sealed" in sys.argv; tag = "sealed" if sealed else "dev"
J = lambda p: json.load(open(p)) if os.path.exists(p) else None
arms = {}
for d in sorted(glob.glob("runs/f_*")):
    n = os.path.basename(d); m = re.match(r"f_(.+?)_s(\d+)(_posthoc)?$", n)
    if not m: continue
    arm = m.group(1) + ("_posthoc" if m.group(3) else "")
    ev = J(f"{d}/eval_{tag}.json")
    if ev is None: continue
    arms.setdefault(arm, []).append({"name": n, "seed": int(m.group(2)), "ev": ev, "man": J(f"{d}/manifest.json"), "extras": J(f"{d}/extras_{tag}.json"),
                                     "reader": J(f"{d}/reader_{tag}.json"), "hidden": J(f"{d}/hidden_{tag}.json"), "patch": J(f"{d}/cont_patch_{tag}.json"),
                                     "timing": J(f"{d}/timing.json"), "explore": J(f"{d}/explore.json")})
NAMES = {"iit": "Discrete + interchange training", "vq": "Discrete, plain imitation", "cont": "Continuous, plain imitation", "contiit": "Continuous + interchange training",
         "cont_posthoc": "Continuous, quantised after training", "contiit_posthoc": "Continuous + interchange, quantised after", "static": "Discrete, world never changes in training",
         "hidden": "Discrete + planted hidden channel", "iithidden": "Discrete + interchange + planted channel",
         "hiddenw": "Discrete + planted channel (strong weight)", "hiddenx": "Discrete + planted channel (earlier recipe: ordinary training profile only)", "iithiddenw": "Discrete + interchange + planted channel (strong weight)", "sat": "Discrete + effect head", "unins": "Discrete, no gate instruction", "flat": "Discrete, flat reader"}
ORDER = [a for a in NAMES if a in arms]
cls = lambda r: r["ev"].get("classes") or r["ev"]["classes_dev_out"]
rep = lambda r: r["ev"].get("replay") or r["ev"]["replay_dev_out"]
def ms(vals, pct=True):
    v = np.array(vals, float); k = 100 if pct else 1
    return f"{v.mean()*k:.1f}" + (f" ({v.min()*k:.1f}–{v.max()*k:.1f})" if len(v) > 1 else "")
L = []; out = {}
L.append(f"### A. Ordinary accuracy and the paired replay ({tag} fixtures; mean over seeds, range in brackets; %)\n")
L.append("| Arm | Seeds | Plain | Dynamic | Mid-plan reversal pairs | Targeted swap | Shuffled | Improvement | Unrelated drop | Slots |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for a in ORDER:
    R = arms[a]
    L.append(f"| {NAMES[a]} | {len(R)} | {ms([cls(r)['plain'] for r in R])} | {ms([cls(r)['dynamic'] for r in R])} | {ms([cls(r)['midplan_reversal'] for r in R])} | "
             f"{ms([rep(r)['primary_targeted_credit']['mean'] for r in R])} | {ms([rep(r)['shuffled_credit'] for r in R])} | {ms([rep(r)['paired_improvement_over_shuffled']['mean'] for r in R])} | "
             f"{ms([rep(r)['unrelated_obligation_drop_vs_unchanged']['mean'] for r in R])} | {'; '.join(str(r['ev']['slots']) for r in R)} |")
    out[a] = [{"name": r["name"], "classes": cls(r), "replay": rep(r), "slots": r["ev"]["slots"]} for r in R]
L.append(f"\n### B. Per-seed primary endpoint with 95% intervals (families resampled; %)\n")
L.append("| Run | Targeted | Shuffled | Improvement [95% CI] | Unrelated drop [95% CI] | Both unmodified runs valid | Resume twice identical |")
L.append("|---|---|---|---|---|---|---|")
for a in ORDER:
    for r in arms[a]:
        p = rep(r); pi = p["paired_improvement_over_shuffled"]; ud = p["unrelated_obligation_drop_vs_unchanged"]
        L.append(f"| {r['name']} | {p['primary_targeted_credit']['mean']*100:.1f} | {p['shuffled_credit']*100:.1f} | {pi['mean']*100:+.1f} [{pi['ci95'][0]*100:+.1f}, {pi['ci95'][1]*100:+.1f}] | "
                 f"{ud['mean']*100:.1f} [{ud['ci95'][0]*100:.1f}, {ud['ci95'][1]*100:.1f}] | {p['both_unmodified_runs_valid']*100:.1f} | {p['resume_twice_identical']*100:.1f} |")
L.append(f"\n### C. Replay controls (mean over seeds; %)\n")
L.append("| Arm | Whole-state transplant: gate follows donor | Same-goal donor: stable | Blank memory: gate right | Message revision | Slots changed by a gate message | Restart from full order | Repaint: same actions | Slots changed by repaint |")
L.append("|---|---|---|---|---|---|---|---|---|")
for a in ORDER:
    R = arms[a]; g = lambda f: [f(rep(r)) for r in R]
    L.append(f"| {NAMES[a]} | {ms(g(lambda p: p['whole_state_transplant']['gate']))} | {ms(g(lambda p: p['same_goal_donor_stable']))} | {ms(g(lambda p: p['blank_memory']['gate']))} | {ms(g(lambda p: p['message_revision']['credit']))} | "
             f"{ms(g(lambda p: p['message_revision']['slots_changed']), False)} | {ms(g(lambda p: p['restart_full_order']))} | {ms(g(lambda p: p['decor']['same_actions']))} | {ms(g(lambda p: p['decor']['slots_changed_next_step']), False)} |")
L.append(f"\n### D. Exhaustive check: every reachable state against every observation, per family\n")
L.append("| Run | Families | Pairs checked | Wrong | Wrong % | Families with a wrong pair | Code states per family (after INIT … BAY) | Meanings |")
L.append("|---|---|---|---|---|---|---|---|")
for a in ORDER:
    for r in arms[a]:
        m = r["ev"].get("machine")
        if not m: continue
        L.append(f"| {r['name']} | {m['families']} | {m['pairs_checked']:,} | {m['violating_pairs']:,} | {100*m['violating_pairs']/m['pairs_checked']:.4f} | {len(m['families_with_violations'])} | "
                 f"{' '.join(str(round(x)) for x in m['mean_per_family']['code_states'])} | {' '.join(str(round(x)) for x in m['mean_per_family']['spec_classes'])} |")
        out.setdefault("machine", {})[r["name"]] = {k: v for k, v in m.items() if k not in ("per_family",)}
L.append(f"\n### E. Typed patch, quotient memory, corruption alarm (%)\n")
L.append("| Run | Typed patch credit | Patch undefined | Plain: dynamic / mid-plan | Spec quotient: dynamic / mid-plan | Behaviour quotient: dynamic / mid-plan | One slot corrupted: harmful | Harmful caught by dictionary | Missed |")
L.append("|---|---|---|---|---|---|---|---|---|")
for a in ORDER:
    for r in arms[a]:
        x = r["extras"]
        if not x: continue
        c = x["corrupt_one_slot"]; f = lambda k: f"{x[k]['dynamic']*100:.1f} / {x[k]['midplan_reversal']*100:.1f}"
        L.append(f"| {r['name']} | {x['typed_patch']['credit']*100:.1f} | {x['typed_patch']['patch_undefined']*100:.1f} | {f('classes_base')} | {f('classes_quotient_spec')} | {f('classes_quotient_behaviour')} | "
                 f"{c['harmful_rate']*100:.1f} | {c['harmful_caught']*100:.1f} | {c['missed_harmful']} |")
        out.setdefault("extras", {})[r["name"]] = x
for key, title in (("hidden", "F. Planted hidden channel (bit accuracy; 50% is chance)"), ("reader", "G. Monitoring readers"), ("patch", "H. Continuous memory: swap along one direction"), ("explore", "I. Bits the code carries about the gate"), ("timing", "J. Timing")):
    rows = [(r["name"], r[key]) for a in ORDER for r in arms[a] if r[key]]
    if rows:
        L.append(f"\n### {title}\n\n```json")
        for n, v in rows: L.append(json.dumps({n: v}))
        L.append("```"); out[key] = dict(rows)
L.append(f"\n### K. Budget\n")
L.append("| Run | Parameters | Gradient steps | Episodes | Phase 2 from step | Wall seconds (8 runs in parallel, 1 thread each) | Supervision |")
L.append("|---|---|---|---|---|---|---|")
for a in ORDER:
    for r in arms[a]:
        m = r["man"]
        if m: L.append(f"| {r['name']} | {m['parameters']:,} | {m['gradient_steps']:,} | {m['episodes_seen']:,} | {m.get('phase2_started_at_step')} | {m['wall_seconds']} | {m['supervision']} |")
os.makedirs("results", exist_ok=True)
open(f"results/tables_{tag}.md", "w").write("\n".join(L) + "\n"); json.dump(out, open(f"results/summary_{tag}.json", "w"), indent=1)
print("\n".join(L))
