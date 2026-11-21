"""M1: collect every seed into results/v02/M1_report.md and archive both map versions.

    python v02/m1_report.py
"""
import glob, hashlib, json, os
rows = []; L = []
for s in (1, 2, 3, 4, 5):
    n = f"f_iit_s{s}"; rp = f"results/v02/maps20/{n}/recover_report.json"; ep = f"results/v02/expanded/{n}/report.json"
    if not (os.path.exists(rp) and os.path.exists(ep)): continue
    r = json.load(open(rp)); e = json.load(open(ep)); m = json.load(open(f"results/v02/matched/{n}.json"))["by_split"]["all"] if os.path.exists(f"results/v02/matched/{n}.json") else None
    fresh = {}
    for p in sorted(glob.glob(f"results/v02/expanded/{n}/chunk_*.json")):
        for f, v in json.load(open(p)).items():
            if "fresh_maps" in v: fresh[f] = v["fresh_maps"]
    blob = json.dumps(fresh, sort_keys=True, separators=(",", ":")).encode()
    open(f"results/v02/expanded/{n}/maps36.json", "wb").write(blob); e["fresh_maps_sha256"] = hashlib.sha256(blob).hexdigest(); e["fresh_maps_families"] = len(fresh)
    rows.append((s, r, e, m))
P = lambda a, b: f"{a:,} / {b:,} ({100 * a / max(1, b):.4f}%)"
L += ["# M1 report: the certificate with all 36 operator-message patterns", "",
      "Wrong / checked. A pair is one reachable saved state shown one observation. Per family; all 100 Dispatch-2 families.", "",
      "| Seed | v0.1 list (20 patterns), plain memory | v0.1 list, original maps | 36 patterns, plain memory | 36 patterns, original maps unchanged | 36 patterns, maps rebuilt |", "|---|---|---|---|---|---|"]
for s, r, e, m in rows:
    L.append(f"| {s} | {P(r['plain_wrong'], r['plain_checked'])} | {P(r['quot_wrong'], r['quot_checked'])} | {P(e['raw36_wrong'], e['raw36_checked'])} | {P(e['old_wrong'], e['old_checked'])} | {P(e['fresh_wrong'], e['fresh_checked'])} |")
L += ["", "Original maps applied to the 36-pattern run, in detail:", "",
      "| Seed | SHA-256 of the original maps | Reproduces archived v0.1 counts | Transitions onto a state the map does not know | Distinct unknown states | Wrong from an unknown state | Wrong from a known representative | Families with a wrong pair: plain / original maps / rebuilt maps |", "|---|---|---|---|---|---|---|---|"]
for s, r, e, m in rows:
    fw = e["families_wrong"]
    L.append(f"| {s} | `{r['maps_sha256'][:16]}…` | {r['matches_archived_counts']} | {P(e['old_missing_transitions'], e['old_transitions'])} | {e['old_missing_codes']:,} | {e['old_wrong_unmapped_state']:,} | {e['old_wrong_mapped_rep']:,} | {len(fw['raw36'])} / {len(fw['old'])} / {len(fw['fresh'])} |")
L += ["", "Same histories, three memories (2,000,000 sampled jobs per seed; every stage drawn uniformly from the 36-pattern alphabet of the family):", "",
      "| Seed | Jobs with a wrong decision: plain | original maps | rebuilt maps | Original maps: repaired / broken / tie-break only | Rebuilt maps: repaired / broken / tie-break only |", "|---|---|---|---|---|---|"]
for s, r, e, m in rows:
    if m: L.append(f"| {s} | {m['plain_jobs_with_a_wrong_decision']:,} | {m['old_jobs_with_a_wrong_decision']:,} | {m['fresh_jobs_with_a_wrong_decision']:,} | {m['old_repaired']:,} / {m['old_broken']:,} / {m['old_tie_break_only']:,} | {m['fresh_repaired']:,} / {m['fresh_broken']:,} / {m['fresh_tie_break_only']:,} |")
L += ["", "Archived maps: `results/v02/maps20/<run>/maps20.json` (original) and `results/v02/expanded/<run>/maps36.json` (rebuilt). Full hashes:", ""]
for s, r, e, m in rows: L.append(f"- seed {s}: original `{r['maps_sha256']}`, rebuilt `{e['fresh_maps_sha256']}`; CPU-seconds: recover {r['cpu_seconds']:,.0f}, expanded {e['seconds']:,.0f}")
open("results/v02/M1_tables.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
