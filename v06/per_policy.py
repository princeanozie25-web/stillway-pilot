"""Per-policy and per-seed detail for one family run, from the raw shard files only.   python v06/per_policy.py FAMILY_NAME
Written after the codex_hidden run (post-hoc reading aid; it changes no frozen number).  Writes results/v06/<name>_per_policy.md."""
import glob, json, sys
import numpy as np
name = sys.argv[1]; sh = [json.load(open(f)) for f in sorted(glob.glob(f"results/v06/{name}_shard*.json"))]; pol = [p for s in sh for p in s["policies"]]; B = sh[0]["budgets"]; INF = float("inf")
ARMS = ("scratch", "bank_row", "tables", "programs", "selector", "index"); show = lambda v: "never" if v == INF else f"{v:g}"
def per_seed(p, key, thr=0.99):
    rows = p["curves"][key]; out = []
    for s in range(len(rows[0])):
        hit = [B[i] for i in range(len(B)) if rows[i][s]["right_all"] >= thr]; out.append(hit[0] if hit else INF)
    return out
P = [f"# {name}: per-policy and per-seed detail", "", f"Budgets: {B}. Every cell is read from the raw shard file; nothing is dropped.", ""]
n_seeds = len(pol[0]["curves"]["passive/scratch"][0]); cells = sum(len(r) for p in pol for k in p["curves"] for r in p["curves"][k])
P += [f"Policies {len(pol)}; curves per policy {len(pol[0]['curves'])}; budgets {len(B)}; seeds {n_seeds}; result cells present {cells} of {len(pol) * len(pol[0]['curves']) * len(B) * n_seeds}.", ""]
for mode in ("passive", "chosen"):
    P += [f"## Audits to 99% of all cases right, {mode} audits: each seed, per new policy", "", "| Policy | Group | " + " | ".join(ARMS) + " |", "|---|---|" + "---|" * len(ARMS)]
    for p in pol:
        P.append(f"| {'/'.join(p['ids'])} | {'seen' if p['rule_seen_among_past'] else 'novel'} | " + " | ".join(" / ".join(show(v) for v in per_seed(p, f"{mode}/{a}")) for a in ARMS) + " |")
    P.append("")
P += ["## The frozen medians, seed by seed (median over policies of each seed's own audits to 99%, passive)", "", "| Group | Seed | " + " | ".join(ARMS) + " |", "|---|---|" + "---|" * len(ARMS)]
for gname, g in (("novel", [p for p in pol if not p["rule_seen_among_past"]]), ("seen", [p for p in pol if p["rule_seen_among_past"]])):
    for s in range(n_seeds):
        P.append(f"| {gname} | {s} | " + " | ".join(show(float(np.median([per_seed(p, f'passive/{a}')[s] for p in g]))) for a in ARMS) + " |")
P += ["", "## Novel rules: on how many policies does each learner need fewer, the same or more passive audits to 99% than scratch (per-policy median of seeds)", "", "| Learner | fewer | same | more |", "|---|---|---|---|"]
nov = [p for p in pol if not p["rule_seen_among_past"]]; m = lambda p, a: float(np.median(per_seed(p, f"passive/{a}")))
for a in ARMS[1:]:
    d = [(m(p, a), m(p, "scratch")) for p in nov]; P.append(f"| {a} | {sum(x < y for x, y in d)} | {sum(x == y for x, y in d)} | {sum(x > y for x, y in d)} |")
P += ["", "## Mean share of all cases right at each budget, passive (mean over policies and seeds)", "", "| Group | Learner | " + " | ".join(str(b) for b in B) + " |", "|---|---|" + "---|" * len(B)]
for gname, g in (("novel", nov), ("seen", [p for p in pol if p["rule_seen_among_past"]])):
    for a in ARMS:
        P.append(f"| {gname} | {a} | " + " | ".join(f"{100 * np.mean([r['right_all'] for p in g for r in p['curves'][f'passive/{a}'][i]]):.1f}" for i in range(len(B))) + " |")
open(f"results/v06/{name}_per_policy.md", "w").write("\n".join(P) + "\n"); print("\n".join(P))
