"""L4 under the frozen wording and under the post-freeze code, side by side.   python v06/l4_check.py FAMILY_NAME

Frozen spec (docs/v06_spec.md): "in both groups its audits to 99% are within one budget step of the best single learner".
Frozen code (commit 2b125d1):   step[selector] <= step[best] + 1, where step maps a budget to its position in the budget list.
                                 It fails with a KeyError when a median over an even number of rules falls between two budgets.
Post-freeze code (ea7d3f3):     selector <= 2 * best.
The two agree whenever both medians are budgets below the last doubling; they can differ at the top of the list, where the last
step (512 to the full table) is more than a factor of two.
A third reading is printed too: the spec's words taken literally (selector <= the budget one step above the best learner's).
"""
import glob, json, sys
import numpy as np
name = sys.argv[1]; sh = [json.load(open(f)) for f in sorted(glob.glob(f"results/v06/{name}_shard*.json"))]; pol = [p for s in sh for p in s["policies"]]; B = sh[0]["budgets"]; INF = float("inf"); step = {float(b): i for i, b in enumerate(B)}
def first(p, key):
    rows = p["curves"][key]; per = []
    for s in range(len(rows[0])):
        hit = [B[i] for i in range(len(B)) if rows[i][s]["right_all"] >= 0.99]; per.append(hit[0] if hit else INF)
    return float(np.median(per))
def nxt(v):      # the spec's words read literally: the budget one step above the best learner's (rounded up to a budget if it falls between two)
    i = min(j for j, b in enumerate(B) if b >= v); return B[min(i + 1, len(B) - 1)]
out = {"budgets": B, "groups": {}}
for gname, g in (("novel", [p for p in pol if not p["rule_seen_among_past"]]), ("seen", [p for p in pol if p["rule_seen_among_past"]])):
    if not g: out["groups"][gname] = "no policies in this group"; continue
    med = {a: float(np.median([first(p, f"passive/{a}") for p in g])) for a in ("scratch", "bank_row", "tables", "programs", "selector")}; best = min(med[a] for a in ("scratch", "bank_row", "tables", "programs")); s_ = med["selector"]
    on_grid = s_ in step and best in step
    frozen = (s_ < INF and (best == INF or step[s_] <= step[best] + 1)) if (on_grid or best == INF or s_ == INF) else None
    out["groups"][gname] = {"policies": len(g), "medians": {k: (None if v == INF else v) for k, v in med.items()}, "best_single": None if best == INF else best,
                            "L4_frozen_code": "undefined (a median is not a budget; the frozen code raises KeyError)" if frozen is None else bool(frozen),
                            "L4_post_freeze_code": bool(s_ < INF and (best == INF or s_ <= 2 * best)),
                            "L4_spec_wording": bool(s_ < INF and (best == INF or s_ <= nxt(best)))}
vals = [v for v in out["groups"].values() if isinstance(v, dict)]
out["L4_frozen_code_overall"] = None if any(isinstance(v["L4_frozen_code"], str) for v in vals) else all(v["L4_frozen_code"] for v in vals)
out["L4_post_freeze_code_overall"] = all(v["L4_post_freeze_code"] for v in vals); out["L4_spec_wording_overall"] = all(v["L4_spec_wording"] for v in vals)
out["frozen_code_runs_on_this_family"] = out["L4_frozen_code_overall"] is not None
out["all_available_readings_agree"] = len({x for x in (out["L4_frozen_code_overall"], out["L4_post_freeze_code_overall"], out["L4_spec_wording_overall"]) if x is not None}) == 1
json.dump(out, open(f"results/v06/{name}_L4_check.json", "w"), indent=1); print(json.dumps(out, indent=1))
