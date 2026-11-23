"""Tables for a set of graded runs.   python repair/report.py OUT.md LABEL=FILE.graded.jsonl [LABEL=FILE ...]

Counts per arm, costs per job, and the paired comparison of every arm with the first one named.  Nothing is tuned here."""
import json, random, sys
from math import comb


def sign_p(a, b):
    n = a + b
    if n == 0: return 1.0
    k = min(a, b); return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def main(out, pairs):
    arms = [(l, {g["id"]: g for g in map(json.loads, open(f))}) for l, f in (p.split("=", 1) for p in pairs)]
    ids = sorted(set.intersection(*(set(a) for _, a in arms))); L = []; n = len(ids)
    L += [f"Jobs in every arm: {n}.", "", "| Arm | Verified | Wrong DONE | Asked | Out of limits | Patch right whatever the ending | Right file touched |", "|---|---|---|---|---|---|---|"]
    for l, a in arms:
        c = lambda k: sum(a[i]["outcome"] == k for i in ids)
        L.append(f"| {l} | {c('verified')} | {c('wrong')} | {c('abstained')} | {c('budget')} | {sum(bool(a[i]['patch_ok'] or a[i].get('discarded_ok')) for i in ids)} | {sum(bool(a[i]['right_file']) for i in ids)} |")
    L += ["", "| Arm | Tool calls | Run or test calls | Output tokens | Prompt tokens | Seconds | Endings that left files changed without DONE |", "|---|---|---|---|---|---|---|"]
    for l, a in arms:
        m = lambda f: sum(f(a[i]) for i in ids) / n
        L.append(f"| {l} | {m(lambda g: g['used']['calls']):.1f} | {m(lambda g: g['used']['tests']):.1f} | {m(lambda g: g['used']['tokens']):.0f} | {m(lambda g: g['used']['prompt_tokens']):.0f} | {m(lambda g: g['wall_s']):.0f} | {sum(a[i]['end'] != 'DONE' and not a[i]['clean'] for i in ids)} |")
    base_l, base = arms[0]; rng = random.Random(805)
    if len(arms) > 1: L += ["", f"Paired with {base_l} (exact two-sided sign test; bootstrap interval for the difference in verified share, 10,000 resamples, seed 805):", "", "| Arm | Verified here only | Verified there only | p | Difference, 95% interval | Wrong DONE here only | Wrong DONE there only |", "|---|---|---|---|---|---|---|"]
    for l, a in arms[1:]:
        v = [(a[i]["outcome"] == "verified") - (base[i]["outcome"] == "verified") for i in ids]; w = [(a[i]["outcome"] == "wrong") - (base[i]["outcome"] == "wrong") for i in ids]
        bs = sorted(sum(rng.choice(v) for _ in ids) / n for _ in range(10000))
        L.append(f"| {l} | {v.count(1)} | {v.count(-1)} | {sign_p(v.count(1), v.count(-1)):.3f} | {100 * sum(v) / n:+.0f} points ({100 * bs[250]:+.0f} to {100 * bs[9749]:+.0f}) | {w.count(1)} | {w.count(-1)} |")
    g_arms = [(l, a) for l, a in arms if any("guard" in g for g in a.values())]
    for l, a in g_arms:
        qs = [q for i in ids for q in a[i]["guard"]["questions"]]; ag = lambda k: sum(q["agrees_with"] == k for q in qs)
        L += ["", f"Guard, {l}: questions {len(qs)} on {sum(bool(a[i]['guard']['questions']) for i in ids)} jobs (user's value agreed with the patch {ag('after')}, with the old behaviour {ag('before')}, with neither {ag('neither')}); "
              f"jobs with a reproduced example {sum(bool(a[i]['guard']['examples']) for i in ids)}; done refused {sum(a[i]['used']['refused'] for i in ids)} times; probe executions per job {sum(a[i]['guard']['probe_runs'] for i in ids) / n:.1f}; "
              f"guard tokens per job {sum(a[i]['used']['guard_tokens'] for i in ids) / n:.0f}; patches put back {sum('discarded_ok' in a[i] for i in ids)}, of which right {sum(a[i].get('discarded_ok') is True for i in ids)}."]
    L += ["", "| Job | " + " | ".join(l for l, _ in arms) + " |", "|---|" + "---|" * len(arms)]
    for i in ids: L.append(f"| {i} | " + " | ".join(a[i]["outcome"] + (" (patch right)" if a[i]["outcome"] != "verified" and (a[i]["patch_ok"] or a[i].get("discarded_ok")) else "") for _, a in arms) + " |")
    open(out, "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__": main(sys.argv[1], sys.argv[2:])
