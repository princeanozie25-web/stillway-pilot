"""An experience: one worked job, kept whole, so it can be replayed and so a memory entry can cite it.

Fields: goal, visible initial state (files and their hash), every script with the effect predicted before execution,
the observed effect and the files it changed, the final diff, the independent verdict, compute and time, and the
candidate memory entry with its provenance.  Failures are kept exactly like successes."""
import hashlib, json
from stillway8 import expert as E
from stillway8.runner import Session

def fhash(files): return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def signature(public, steps):
    """What a later job can be matched on before any repair is tried: the domain and what the first look showed."""
    if not steps: return None
    if public["dom"] == "proj":
        f = sorted({x for o in steps[0]["obs"] for x in E.mismatches(o)}); return {"dom": "proj", "reported": f}
    notes = []
    for s in steps:
        for line, o in zip(s["script"], s["obs"]):
            if line.startswith("FACT"): notes.append(o.split()[0])
    d = steps[0]["obs"][0]; kinds = [w for w in d.split() if w in ("amt", "onlyL", "onlyS")]
    return {"dom": "tab", "kinds": kinds, "notes": notes}


def candidate(public, steps, verdict, exp_id, source):
    """The memory entry this experience proposes: only from a verified job that changed something."""
    if verdict["outcome"] != "verified": return None
    edits = [l for s in steps for l, o in zip(s["script"], s["obs"]) if l.split()[0] in ("PATCH", "COPY", "KEEP", "DROP", "ADD", "SKIP") and o.startswith("OK")]
    if public["dom"] == "proj":
        reverted = any(l == "REVERT" for s in steps for l in s["script"]); edits = edits[-1:] if edits else []
        if not edits: return None
        _, m, slot, variant = edits[0].split(); role = next((o.split()[1] for s in steps for l, o in zip(s["script"], s["obs"]) if l == f"SHOW {m}"), None)
        return {"signature": signature(public, steps), "procedure": {"role": role, "slot": slot, "variant": variant}, "provenance": {"experience": exp_id, "verdict": "verified", "source": source, "recovered": reverted}}
    keys = {}; seen_diff = False                                # per key: [kind, note, action]
    for st in steps:
        for l, o in zip(st["script"], st["obs"]):
            w = l.split()
            if w[0] == "DIFF" and not seen_diff:
                seen_diff = True
                for item in (o.split("d ")[1:] if o != "none" else []): i = item.split(); keys[i[0]] = ["onlyS" if i[1] == "onlyS" else i[2], None, None]
            elif w[0] == "FACT" and w[1] in keys: keys[w[1]][1] = o.split()[0]
            elif w[0] in ("COPY", "KEEP", "DROP", "ADD", "SKIP") and o.startswith("OK") and w[1] in keys: keys[w[1]][2] = w[0]
    if not keys or any(None in v for v in keys.values()): return None
    return {"signature": signature(public, steps), "procedure": {"rules": sorted(keys.values())}, "provenance": {"experience": exp_id, "verdict": "verified", "source": source, "recovered": False}}


def build(public, record, verdict, source):
    exp_id = f"x-{record['id']}-{hashlib.sha256((source + json.dumps(record['steps'], sort_keys=True)).encode()).hexdigest()[:8]}"
    return {"experience": exp_id, "job": public["id"], "source": source, "goal": " ".join(E.header(public)[1:]), "initial": {"files": public["files"], "sha256": fhash(public["files"])},
            "steps": record["steps"], "end": record["end"], "why": record.get("why"), "diff": record["diff"], "final_sha256_16": record["final_hash"], "verdict": verdict,
            "compute": {k: record.get(k) for k in ("calls", "ops", "tokens_in", "tokens_out", "model_s", "exec_s", "wall_s", "predict_s", "failed_checks", "edit_scripts")},
            "memory_candidate": candidate(public, record["steps"], verdict, exp_id, source)}


def replay(exp):
    """Run the stored scripts again from the stored initial state, in the sandbox.  Returns (same observations, same final state, session files)."""
    pub = {"files": exp["initial"]["files"]}; s = Session(pub); same = True
    try:
        for st in exp["steps"]:
            if not st["script"]: continue
            r = s.run("\n".join(st["script"])); same &= r["obs"] == st["obs"]
        final = s.files()
    finally: s.close()
    return same, fhash(final)[:16] == exp["final_sha256_16"], final
