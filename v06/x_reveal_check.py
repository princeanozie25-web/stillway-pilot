"""Check the author's post-lock breakdown against the family file and the locked raw outputs.
    python -I v06/x_reveal_check.py family_codex.json data/external/codex/reveal_2026-11-21.tsv
Run after the outputs were locked (commit b7120cd).  Reads the hidden tables only to count differing decisions."""
import json, sys
import numpy as np
fam = json.load(open(sys.argv[1])); rev = [l.rstrip("\n").split("\t") for l in open(sys.argv[2])][1:]; d = json.load(open("results/v06/codex_hidden_shard0.json")); B = d["budgets"]; INF = float("inf")
tab = lambda i: np.frombuffer(fam["policies"][i].encode(), np.uint8) - 48; past = sorted(fam["past"]); PT = np.array([tab(i) for i in past]); pol = {p["ids"][0]: p for p in d["policies"]}
def a99(p, arm):
    rows = p["curves"][f"passive/{arm}"]; per = []
    for s in range(len(rows[0])):
        hit = [B[i] for i in range(len(B)) if rows[i][s]["right_all"] >= 0.99]; per.append(hit[0] if hit else INF)
    return float(np.median(per))
bad = 0; out = []
for pid, grp, shape, closest, dist, sc, sel in rev:
    dd = (PT != tab(pid)[None]).sum(1); mn = int(dd.min()); ties = [past[i] for i in np.flatnonzero(dd == mn)]; s_ = a99(pol[pid], "scratch"); l_ = a99(pol[pid], "selector")
    ok = mn == int(dist) and closest in ties and s_ == float(sc) and l_ == float(sel) and (pol[pid]["rule_seen_among_past"] == (grp == "Repeat")); bad += not ok
    out.append({"policy": pid, "group": grp, "shape": shape, "distance_author": int(dist), "distance_file": mn, "closest_author": closest, "closest_file": ties, "share_differing": round(mn / len(dd and PT[0]) if False else mn / PT.shape[1], 4), "scratch": s_, "selector": l_, "agrees": bool(ok)})
    print(pid, grp, shape, "distance", mn, "(author", dist + ")", "closest", ties, "(author", closest + ")", "scratch", s_, sc, "selector", l_, sel, "OK" if ok else "MISMATCH")
shapes_past = None
print("rows", len(rev), "mismatches", bad); json.dump(out, open("results/v06/codex_hidden_reveal_check.json", "w"), indent=1)
