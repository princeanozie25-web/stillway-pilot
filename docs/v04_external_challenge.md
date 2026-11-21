# External challenge for v0.4: format and scoring

The v0.4 holdout is internal (I wrote the generators). This file lets Prince or Codex author a challenge I have not seen and score the frozen systems on it. Publish it only after the candidate hashes in `results/v04/MANIFEST_RUNS.json` are fixed (they are, from commit `d9a9047` onward plus the final-run commit).

## Approvals workflow

One JSON file:

```json
{"policies": {"3": [2, 1, 0, 1], "17": null},
 "documents": [{"tenant": 0, "events": [{"kind": 2, "slot": 0, "jur": 1, "lvl": -1, "age": -1, "tag": -1, "evid": -1, "pid": -1, "ostat": -1}, "..."]}]}
```

- `policies`: policy ID → `[threshold 1..3, waiver 0 none / 1 A / 2 B, stale accepted 0/1, conflict is invalid 0/1]`, or `null` for an expired policy. The learner never sees this.
- A document is a list of events with the nine integer fields of `docs/v04_spec.md` section 2 (unused fields −1). Event kinds: 0 SIGN, 1 CORRECT, 2 MOVE, 3 AMEND_RETRO, 4 AMEND_PRO, 5 EXPIRE, 6 OVERRIDE, 7 WAIT. Any length. Set a slot's jurisdiction (MOVE) and a jurisdiction's policy (AMEND_PRO) before signing, as the generator's first 9 events do.
- Policy IDs must be ones the scored bank knows: 1 to 60 for a seed's base bank (their rules are in `runs/v4f_proc_s_s<seed>/raw_outputs.npz`, key `pid_rule`), or a later ID after a sleep. To test new policies, use the sleep protocol instead (below).

Score: `python v04/score_external.py challenge.json runs/v4f_proc_s_s1`. It runs the compiled tables of that core (plain Python) and the dependency tracker with your `policies`, and grades both with `stillway4/grader.py` from your raw events. Write your own grader from section 2 of the spec if you do not want to trust mine.

## Sleep protocol

Give a list of sessions. Each session: `{"new_policies": {"id": rule}, "expired": [ids], "wake_documents": [...], "test_documents": [...]}`. The scorer feeds each arm the wake documents' audited outcomes, runs the sleep, and grades the test documents. Not implemented as a one-file scorer yet: `stillway4/sleep.py` `run()` is the reference and takes generated sessions only. This is the gap an external author would have to close with me or without me.

## Dispatch certificates

`v04/runner` and the table files are enough: write jobs in the binary format at the top of `v04/runner.c`, run them through `results/v04/m1/exact_g3.bin` and a learned `runs/v4f_r_g3_w128_s1/tables.bin`, and compare with your own planner. The table-free exact planner is mode 2 of the same program.
