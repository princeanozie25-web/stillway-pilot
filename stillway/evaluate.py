"""Evaluate one trained run.

    python -m stillway.evaluate runs/NAME            # development fixtures only
    python -m stillway.evaluate runs/NAME --sealed   # sealed fixtures (needs FREEZE.json)

Writes runs/NAME/eval_dev.json or eval_sealed.json.
"""
from __future__ import annotations

import json
import os
import sys
import time

import torch

from .automaton import Machine
from .fixtures import DEV_IN, DEV_OUT, families, layouts_of, load_sealed, read_jsonl
from .model import NeuralPlanner, load_checkpoint
from .replay import replay_all, summarise
from .scorer import score_file, select_slots
from .world import ALL_LAYOUTS, STAGE_NAMES, family_of


def class_rates(planner, items, slots):
    res = score_file(planner, items, slots)
    return {c: (v["rate"] if isinstance(v, dict) else v) for c, v in res.items()}


def describe_violations(m: Machine, k: int):
    return [{**{kk: v for kk, v in viol.items() if kk != "state"},
             "history": m.witness(viol["stage"] - 1, viol["state"]) if viol["stage"] > 0 else [],
             "failing_obs": m.alpha.describe(viol["stage"], viol["example_obs"])} for viol in m.violations[:k]]


def family_machines(model, layouts) -> dict:
    """Realistic certificate.  In the real world a layout can be re-wired (L and R swapped) but its
    mechanisms never change, so each family is its own closed world.  We extract one machine per
    family and check every history inside it."""
    fams = sorted({family_of(e) for e in layouts})
    per, checked, bad, bad_fams, viol = {}, 0, 0, [], []
    dictionary = {}
    n_stage = len(STAGE_NAMES)
    tot = {k: [0.0] * n_stage for k in ("code_states", "behaviour_classes", "spec_classes", "ambiguous_states", "silent_bits", "tiebreak_bits")}
    t0 = time.time()
    for f in fams:
        m = Machine(model, [e for e in layouts if family_of(e) == f])
        sm = m.summary()
        checked += sm["pairs_checked"]; bad += sm["violating_pairs"]
        if sm["violating_pairs"]:
            bad_fams.append(f)
            if len(viol) < 5:
                viol += describe_violations(m, 1)
        for i, row in enumerate(sm["stages"]):
            for k in tot:
                tot[k][i] += row[k]
        # dictionary: for every reachable code state, what it means and its canonical representatives
        spec_c, beh_c = m.spec_canon(), m.behaviour_canon()
        dictionary[f] = []
        for st in range(len(m.stage_codes)):
            sc = m.spec_classes(st)
            dictionary[f].append({str(int(c)): [None if sc[i] == "AMBIGUOUS" else list(sc[i]),
                                                spec_c[st].get(int(c)), beh_c[st][int(c)]]
                                  for i, c in enumerate(m.stage_codes[st])})
        per[f] = {"violating_pairs": sm["violating_pairs"], "pairs_checked": sm["pairs_checked"],
                  "code_states": [r["code_states"] for r in sm["stages"]],
                  "behaviour_classes": [r["behaviour_classes"] for r in sm["stages"]],
                  "spec_classes": [r["spec_classes"] for r in sm["stages"]]}
    n = len(fams)
    return {"families": n, "layouts": len(layouts), "pairs_checked": checked, "violating_pairs": bad,
            "families_with_violations": bad_fams, "seconds": round(time.time() - t0, 1),
            "mean_per_family": {k: [round(x / n, 3) for x in v] for k, v in tot.items()},
            "stage_names": STAGE_NAMES, "first_violations": viol, "per_family": per, "_dictionary": dictionary}


def main():
    run = sys.argv[1].rstrip("/")
    sealed = "--sealed" in sys.argv
    no_machine = "--no-machine" in sys.argv
    torch.set_num_threads(int(os.environ.get("THREADS", "2")))
    model = load_checkpoint(os.path.join(run, "checkpoint.pt"))
    planner = NeuralPlanner(model, os.path.basename(run))
    t0 = time.time()
    out = {"run": os.path.basename(run), "checkpoint_sha256": model.sha256, "discrete": planner.discrete}

    dev_in, dev_out = read_jsonl(DEV_IN), read_jsonl(DEV_OUT)
    dev_swaps = [i for i in dev_in + dev_out if i["kind"] == "swap"]
    sel_path = os.path.join(run, "slots.json")
    if sealed:
        sel = json.load(open(sel_path))                      # frozen on dev; never re-selected
    else:
        sel = select_slots(planner, dev_swaps)
        json.dump(sel, open(sel_path, "w"), indent=1)
    out["slots"] = sel["slots"]
    out["slot_table_dev"] = sel["table"]

    if sealed:
        items = load_sealed()
        out["classes"] = class_rates(planner, items, sel["slots"])
        rows = replay_all(planner, items, sel["slots"], seed=1)
        out["replay"] = summarise(rows)
        json.dump(rows, open(os.path.join(run, "replay_rows_sealed.json"), "w"))
        lay = ALL_LAYOUTS
    else:
        out["classes_dev_in"] = class_rates(planner, dev_in, sel["slots"])
        out["classes_dev_out"] = class_rates(planner, dev_out, sel["slots"])
        rows = replay_all(planner, dev_out, sel["slots"], seed=1)
        out["replay_dev_out"] = summarise(rows)
        out["replay_dev_in"] = summarise(replay_all(planner, dev_in, sel["slots"], seed=1))
        lay = layouts_of(families("train") + families("dev"))

    if planner.discrete and not no_machine:
        out["machine"] = family_machines(model, lay)
        json.dump(out["machine"].pop("_dictionary"),
                  open(os.path.join(run, "dictionary_sealed.json" if sealed else "dictionary_dev.json"), "w"))
    if planner.discrete and "--adversarial" in sys.argv:
        m = Machine(model, lay)
        out["machine_adversarial"] = m.summary()
        out["machine_adversarial"]["first_violations"] = describe_violations(m, 5)
    out["seconds"] = round(time.time() - t0, 1)
    name = "eval_sealed.json" if sealed else "eval_dev.json"
    json.dump(out, open(os.path.join(run, name), "w"), indent=1)
    brief = {k: out[k] for k in out if k.startswith("classes")}
    print(json.dumps(brief))
    for k in out:
        if k.startswith("replay"):
            r = out[k]
            print(k, "targeted", round(r["primary_targeted_credit"]["mean"], 3), "shuffled", round(r["shuffled_credit"], 3),
                  "improve", [round(x, 3) for x in [r["paired_improvement_over_shuffled"]["mean"]] + r["paired_improvement_over_shuffled"]["ci95"]],
                  "unrel drop", round(r["unrelated_obligation_drop_vs_unchanged"]["mean"], 3), "slots", out["slots"])
    if "machine" in out:
        print(json.dumps({k: v for k, v in out["machine"].items() if k not in ("first_violations", "per_family", "stage_names")}))


if __name__ == "__main__":
    main()
