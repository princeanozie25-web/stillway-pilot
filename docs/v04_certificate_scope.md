# v0.4 certificates: scope

Earlier scopes stand unchanged: `docs/v02_certificate_scope.md` (Dispatch-2, with the v0.1 corrections) and `docs/v03_certificate_scope.md` (two gates, any length).

## 1. Route certificates for G gates (`stillway4/gates.py`, function `certify`)

**Statement, for one table file and one alphabet, when the result is clean and complete:**

> For the route core of Dispatch with G gates: for every job of any number of legs built from leg kinds in the alphabet, every requirement on every gate, and every state of the gates, the route the table file proposes at every leg is one the exact planner allows.

**One certificate per artifact.** A certificate names the SHA-256 of the table file it was made on and the alphabet. It says nothing about any other file. `tables.bin` of each final reader is listed with its hash in `results/v04/MANIFEST_RUNS.json`; the certificate fields are in `results/v04/m1/bench_<run>.json` (`certificate.artifact_sha256`).

**Bounds.**

| Dimension | Bound |
|---|---|
| World | Route decisions only: requirements, gates, legs ahead. Deliveries, waits and events are outside this module; v0.3 showed they do not enter a route decision when the order is held in registers written by rule. |
| Gates | G = 2 and 3 certified for learned tables. G = 4: exact tables only; no learned reader reached a clean certificate inside the one-hour cap. G = 5: see the exact-closure record in `results/v04/m1/exact_g5.json`. |
| Legs | Any number. |
| Alphabet | All (4G)² leg kinds. |
| Caps | 4 GB and one hour per closure. A closure that hits a cap is **incomplete** and certifies nothing; its frontier is checkpointed. |

**What "exact" means here.** The reference is the reverse dynamic program in the same file, compiled to tables. It was checked three ways: at two gates the new checker reproduces the v0.3 counts (42 pairs and 10,752 checks for `v3r24fix_s1`; 91 pairs and 960 wrong for `v3r24_s1`); the C program's table-free planner (mode 2) agrees with the exact tables on every benchmark job; witnesses are confirmed by `brute_valid`, which lists every route choice and uses no value vector.

**The checker detects a fault when one is planted.** Flipping one reachable route entry that has a single valid choice gives at least one wrong entry and a failing job, at 2, 3 and 4 gates (`results/v04/fixtures/m1_mutation_g3.json`, `./run_v04.sh` step 3).

**Released runtimes against the tables.** For each benchmarked reader, every closure entry (or 400,000 sampled entries when there are more) is turned into a job and run through the C program with the table file and through the network; both are compared with the table entry (`runtime_check` in the bench file).

**Per-runtime exports (v0.3 cores).** `results/v04/runtimes/exports.json`: the tables of `v3o_s1`, `v3r24fix_s1` and `v3r24fix_s2` were exported under torch CPU float32, torch CPU float64, torch MPS float32 and a NumPy float32 forward pass, and each export was certified. All twelve are clean. Eleven have the hash of their core's float32 export; the float64 export of `v3o_s1` differs in 78 route entries (ties between equally good routes) and has its own hash and its own clean certificate.

## 2. Bank certificates for the approvals workflow

A promoted bank row is a 36-entry status table (one entry per fact combination). What can be certified about it without the true rule:

- **Agreement with the log.** The row reproduces every logged decision it was trained and validated on (the promotion gate requires 95% on held-out records; the measured value is stored per candidate).
- **Entailed entries.** For each entry, whether every family rule consistent with the log gives the row's status. Entries where the consistent rules disagree are not certified; the row's value there is the status function's generalisation.

This is weaker than a route certificate. The route certificate is checked against the rules of the world; a bank row is checked against evidence and a declared rule family. The independent grader, which knows the true rules, scores every row's actual correctness in `results/v04/tables.md`.

**Substitution invalidates.** A bank certificate names the SHA-256 of the bank file (`results/v04/m3/<core>/bank_<arm>_v<k>.pt`) and of the core checkpoint. A job is pinned to the bank version it started with. Loading another bank under an old certificate is refused by comparing hashes (`v04/demo.py` checks the hash of the version it loads against the recorded one). A new version needs a new certificate.

## 3. What nothing here covers

- Learned route planning beyond three gates.
- The approvals arms' procedure selection: it is tested (five seeds, novel combinations, interventions), not certified. The compiled procedure tables are small enough to check by hand against the hand-coded macro; the differences are listed in `results/v04/tables.md`.
- Floating-point equality of a network across machines. The seed-4 ticket (`results/v04/seed4/report.json`) shows one v0.1 episode whose verdict flips between CPU and GPU because two codes are 0.00001 apart. Certified tables do not have this problem; a network deployed as a network does.
