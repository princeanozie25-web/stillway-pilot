"""M3 tables from the final (and dev) results:  python v02/m3_report.py"""
import json, numpy as np
IIT = [f"v2_iit_s{i}" for i in range(1, 6)]; PLAIN = ["v2_plain_s1", "v2_plain_s2"]
F = {n: json.load(open(f"results/v02/m3/{n}_final.json")) for n in IIT + PLAIN}; D = {n: json.load(open(f"results/v02/m3/{n}_dev.json")) for n in IIT + PLAIN}
ACC = json.load(open("results/v02/m3/core_accuracy_final.json"))
ST = ["A_unseen_families", "B_four_legs", "C_cross_gate"]; SN = {"A_unseen_families": "A: unseen families, 2-3 legs", "B_four_legs": "B: four legs", "C_cross_gate": "C: cross-gate legs"}
M = [("editor:predictor", "Predictor edit (primary)"), ("editor:slot_write", "Slot-write edit"), ("message", "Message and resume"), ("restart", "Full restart"), ("overwrite", "Shortcut: overwrite whole state"), ("actioncopy", "Shortcut: copy actions")]
def rng(v, k=100): v = np.array(v) * k; return f"{v.mean():.1f} ({v.min():.1f}–{v.max():.1f})"
L = ["### M3 final: joint edit success, % (mean over core seeds, range in brackets). Non-trivial eligible attempts; abstention counts as failure.", ""]
for group, runs in (("Interchange-trained cores (5 seeds)", IIT), ("Plain-imitation cores (2 seeds)", PLAIN)):
    L += [f"**{group}**", "", "| Method | " + " | ".join(SN[s] for s in ST) + " | Pooled |", "|---|---|---|---|---|"]
    for k, nm in M:
        cells = [rng([F[n]["strata"][s][k]["joint_success"] for n in runs]) for s in ST]
        pooled = [sum(F[n]["strata"][s][k]["joint_success"] * F[n]["strata"][s][k]["eligible"] for s in ST) / sum(F[n]["strata"][s][k]["eligible"] for s in ST) for n in runs]
        L.append(f"| {nm} | " + " | ".join(cells) + f" | {rng(pooled)} |")
    L.append("| Per-family dictionary (privileged, 400 attempts) | " + " | ".join(rng([F[n]["strata"][s]["dictionary_reference"]["joint_success"] for n in runs]) for s in ST) + " | – |")
    L.append("| Core alone, no edit: every step valid | " + " | ".join(rng([ACC[n][s]["no_events"] for n in runs]) for s in ST) + " | – |")
    L += ["", "Eligible attempts per core: " + ", ".join(f"{SN[s][:1]} {F[runs[0]]['strata'][s]['message']['eligible']:,} of {F[runs[0]]['strata'][s]['message'].get('eligible_before_nontrivial_filter', 0):,} before the non-trivial filter" for s in ST) + " (4,000 attempts each).", ""]
L += ["### Primary editor on interchange-trained cores, per seed (final strata)", "", "| Core | A joint [95% CI] | B joint [95% CI] | C joint [95% CI] | Pooled | Abstained (pooled) | Unrelated drop A / B / C (points) | Message pooled |", "|---|---|---|---|---|---|---|---|"]
for n in IIT:
    r = F[n]["strata"]; k = "editor:predictor"; el = sum(r[s][k]["eligible"] for s in ST)
    pooled = sum(r[s][k]["joint_success"] * r[s][k]["eligible"] for s in ST) / el; ab = sum(r[s][k]["abstained"] * r[s][k]["eligible"] for s in ST) / el
    mp = sum(r[s]["message"]["joint_success"] * r[s]["message"]["eligible"] for s in ST) / el
    L.append(f"| {n} | " + " | ".join(f"{100*r[s][k]['joint_success']:.1f} [{100*r[s][k]['joint_ci95'][0]:.1f}, {100*r[s][k]['joint_ci95'][1]:.1f}]" for s in ST) + f" | {100*pooled:.1f} | {100*ab:.2f} | " + " / ".join(f"{100*r[s][k]['unrelated_drop']:+.1f}" for s in ST) + f" | {100*mp:.1f} |")
L += ["", "### Secondary edit kinds on interchange-trained cores (final strata; mean over 5 seeds; joint success %)", "", "| Kind | Stratum | Predictor | Slot write | Message | Restart |", "|---|---|---|---|---|---|"]
for kind in ("noop", "impose", "withdraw", "two_edits_same", "two_edits_other", "mirror_pairs"):
    for s in ST:
        def g(m, key="joint_success"):
            vals = [F[n]["strata"][s].get(f"{kind}/{m}", {}).get(key) for n in IIT]; vals = [v for v in vals if v is not None]
            return f"{100*np.mean(vals):.1f}" if vals else "–"
        key = "pairs_both_right" if kind == "mirror_pairs" else "joint_success"
        L.append(f"| {kind.replace('_', ' ')}{' (both jobs right)' if kind == 'mirror_pairs' else ''} | {SN[s][:1]} | {g('editor:predictor', key)} | {g('editor:slot_write', key)} | {g('message', key)} | {g('restart', key)} |")
L += ["", "### Development families (selection data; mean over seeds)", "", "| Cores | Predictor | Slot write | Message | Restart | Predictor abstained | Dictionary (privileged) |", "|---|---|---|---|---|---|---|"]
for group, runs in (("Interchange-trained", IIT), ("Plain imitation", PLAIN)):
    g = lambda k, key="joint_success": rng([D[n]["strata"]["dev"][k][key] for n in runs])
    L.append(f"| {group} | {g('editor:predictor')} | {g('editor:slot_write')} | {g('message')} | {g('restart')} | {g('editor:predictor', 'abstained')} | {g('dictionary_reference')} |")
lat = {k: [F[n]["latency_cpu_1_thread"][k]["median_us"] for n in IIT] for k in F[IIT[0]]["latency_cpu_1_thread"]}; p99 = {k: [F[n]["latency_cpu_1_thread"][k]["p99_us"] for n in IIT] for k in lat}
L += ["", "### Latency, one job, one CPU thread, after warm-up (µs; median over 600 timed runs, mean over 5 cores; 99th percentile in brackets)", "", "| Path | Median | 99th percentile |", "|---|---|---|"]
for k, nm in (("core_step_with_message", "Message and resume: one core step that reads the message"), ("predictor_then_core_step", "Predictor edit, then one core step"), ("slot_write_then_core_step", "Slot-write edit, then one core step"),
              ("predictor_edit_only", "Predictor edit only (the saved state is corrected, the planner is not stepped)"), ("slot_write_edit_only", "Slot-write edit only"), ("symbolic_table_update_and_replan", "Symbolic: change the table entry and re-plan the next route exactly")):
    L.append(f"| {nm} | {np.mean(lat[k]):.1f} | {np.mean(p99[k]):.0f} |")
e = D[IIT[0]]["editors"]
L += ["", f"Editor setup, per core: {e['twin_pairs']:,} training-family state pairs in {e['twin_seconds']} s; predictor ({e['predictor_parameters']:,} parameters) fitted in {e['predictor_fit_seconds']} s; abstention thresholds chosen on dev: " + ", ".join(f"{n[3:]} {D[n]['editors']['predictor_tau']}" for n in IIT + PLAIN) + "."]
open("results/v02/M3_tables.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
