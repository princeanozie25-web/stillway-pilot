"""Freeze before the sealed run.

    python tools_freeze.py RUN [RUN ...]

Writes FREEZE.json with: every checkpoint hash, every slot selection made on dev data, the hash of
every file that takes part in scoring, the thresholds, and the hash of the sealed fixture file.
After this file exists the sealed fixtures can be opened.  Nothing listed here may change afterwards;
tools_check_freeze.py verifies that.
"""
import hashlib, json, os, subprocess, sys, time

FILES = ["stillway/world.py", "stillway/planners.py", "stillway/scorer.py", "stillway/replay.py", "stillway/fixtures.py",
         "stillway/automaton.py", "stillway/evaluate.py", "stillway/extras.py", "stillway/model.py", "stillway/vworld.py",
         "tools_extras.py", "tools_reader.py", "tools_hidden.py", "tools_cont_patch.py", "tools_certify_quotient.py", "tools_aggregate.py", "pipe.sh",
         "fixtures/dev/dev_in.jsonl", "fixtures/dev/dev_out.jsonl", "fixtures/sealed/sealed.jsonl"]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

if __name__ == "__main__":
    if os.path.exists("FREEZE.json"):
        sys.exit("FREEZE.json already exists; the freeze happens once")
    runs = {}
    for r in sys.argv[1:]:
        r = r.rstrip("/")
        runs[os.path.basename(r)] = {"checkpoint_sha256": sha(os.path.join(r, "checkpoint.pt")),
                                     "slots": json.load(open(os.path.join(r, "slots.json")))["slots"] if os.path.exists(os.path.join(r, "slots.json")) else None}
    out = {
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "thresholds": {"ordinary_heldout_accuracy_min": 0.90, "paired_improvement_over_shuffled_min": 0.10,
                       "paired_improvement_lower95_above": 0.0, "unrelated_obligation_drop_max": 0.05, "seeds": 5},
        "slot_selection_rule": "highest credit on dev swap fixtures over all non-empty slot sets; ties to the smaller set, then the first in order",
        "primary_arm": os.environ.get("PRIMARY", ""),
        "runs": runs,
        "files_sha256": {f: sha(f) for f in FILES},
    }
    json.dump(out, open("FREEZE.json", "w"), indent=1)
    print("frozen", len(runs), "runs;", "sealed fixtures sha256", out["files_sha256"]["fixtures/sealed/sealed.jsonl"])
