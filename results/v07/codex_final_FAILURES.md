# v0.7 final run: execution failures in the raw records

From student-side fields only, before any grading. A test that was not well formed was not run; a test that raised printed an error as its observation (the student still saw it); a patch that was not well formed or could not be applied left the repository unchanged.
Run log: 0 tracebacks; 0 restarts; last line `RUN_FINAL EXIT 0 at 2026-11-22T11:04:18Z`.

| File | records | tests | tests not well formed | test timeouts | test raised | patches not well formed | patches not applied | records missing a part |
|---|---|---|---|---|---|---|---|---|
| base_s0__bank.jsonl | 96 | 192 | 6 | 4 | 16 | 0 | 1 | 0 |
| base_s0__example.jsonl | 96 | 192 | 0 | 0 | 186 | 0 | 30 | 0 |
| base_s0__plain.jsonl | 96 | 192 | 0 | 0 | 14 | 0 | 1 | 0 |
| experience@0.5_s1__plain.jsonl | 96 | 192 | 0 | 0 | 10 | 0 | 0 | 0 |
| experience@0.5_s2__plain.jsonl | 96 | 192 | 0 | 0 | 10 | 7 | 0 | 0 |
| experience@0.5_s3__plain.jsonl | 96 | 192 | 0 | 0 | 15 | 0 | 0 | 0 |
| experience_s1__plain.jsonl | 96 | 192 | 0 | 0 | 12 | 0 | 0 | 0 |
| experience_s2__plain.jsonl | 96 | 192 | 0 | 0 | 23 | 1 | 0 | 0 |
| experience_s3__plain.jsonl | 96 | 192 | 0 | 3 | 7 | 0 | 0 | 0 |
| experience_x@0.25_s1__plain.jsonl | 96 | 192 | 0 | 0 | 12 | 0 | 1 | 0 |
| experience_x@0.25_s2__plain.jsonl | 96 | 192 | 0 | 0 | 12 | 0 | 1 | 0 |
| experience_x@0.25_s3__plain.jsonl | 96 | 192 | 0 | 0 | 12 | 0 | 0 | 0 |
| experience_x@0.5_s1__bank.jsonl | 96 | 192 | 0 | 0 | 12 | 0 | 0 | 0 |
| experience_x@0.5_s1__plain.jsonl | 96 | 192 | 0 | 0 | 6 | 1 | 0 | 0 |
| experience_x@0.5_s2__bank.jsonl | 96 | 192 | 0 | 0 | 19 | 0 | 0 | 0 |
| experience_x@0.5_s2__plain.jsonl | 96 | 192 | 0 | 0 | 11 | 8 | 0 | 0 |
| experience_x@0.5_s3__bank.jsonl | 96 | 192 | 0 | 0 | 9 | 0 | 0 | 0 |
| experience_x@0.5_s3__plain.jsonl | 96 | 192 | 0 | 0 | 7 | 0 | 0 | 0 |
| experience_x@0.75_s1__plain.jsonl | 96 | 192 | 0 | 0 | 11 | 0 | 0 | 0 |
| experience_x@0.75_s2__plain.jsonl | 96 | 192 | 0 | 2 | 8 | 7 | 0 | 0 |
| experience_x@0.75_s3__plain.jsonl | 96 | 192 | 0 | 0 | 5 | 0 | 0 | 0 |
| experience_x_s1__bank.jsonl | 96 | 192 | 0 | 0 | 22 | 0 | 0 | 0 |
| experience_x_s1__bank_v1.jsonl | 96 | 192 | 0 | 0 | 11 | 0 | 0 | 0 |
| experience_x_s1__example.jsonl | 96 | 192 | 0 | 0 | 9 | 0 | 0 | 0 |
| experience_x_s1__plain.jsonl | 96 | 192 | 0 | 1 | 13 | 0 | 0 | 0 |
| experience_x_s1__wrong.jsonl | 96 | 192 | 0 | 0 | 10 | 0 | 0 | 0 |
| experience_x_s2__bank.jsonl | 96 | 192 | 2 | 3 | 9 | 1 | 0 | 0 |
| experience_x_s2__bank_v1.jsonl | 96 | 192 | 0 | 0 | 17 | 0 | 0 | 0 |
| experience_x_s2__example.jsonl | 96 | 192 | 0 | 3 | 10 | 0 | 0 | 0 |
| experience_x_s2__plain.jsonl | 96 | 192 | 0 | 0 | 15 | 1 | 1 | 0 |
| experience_x_s2__wrong.jsonl | 96 | 192 | 0 | 1 | 11 | 0 | 0 | 0 |
| experience_x_s3__bank.jsonl | 96 | 192 | 0 | 0 | 11 | 0 | 0 | 0 |
| experience_x_s3__bank_v1.jsonl | 96 | 192 | 0 | 0 | 5 | 0 | 0 | 0 |
| experience_x_s3__example.jsonl | 96 | 192 | 0 | 0 | 15 | 0 | 0 | 0 |
| experience_x_s3__plain.jsonl | 96 | 192 | 0 | 0 | 6 | 0 | 0 | 0 |
| experience_x_s3__wrong.jsonl | 96 | 192 | 0 | 0 | 4 | 0 | 0 | 0 |
| patches@0.5_s1__plain.jsonl | 96 | 192 | 0 | 0 | 26 | 0 | 0 | 0 |
| patches@0.5_s2__plain.jsonl | 96 | 192 | 0 | 0 | 28 | 0 | 0 | 0 |
| patches@0.5_s3__plain.jsonl | 96 | 192 | 0 | 2 | 24 | 0 | 0 | 0 |
| patches_s1__plain.jsonl | 96 | 192 | 12 | 0 | 38 | 0 | 0 | 0 |
| patches_s2__plain.jsonl | 96 | 192 | 16 | 0 | 27 | 0 | 0 | 0 |
| patches_s3__plain.jsonl | 96 | 192 | 13 | 0 | 46 | 0 | 0 | 0 |
| **All 42 files** | **4032** | **8064** | **49** | **19** | **774** | **26** | **35** | **0** |
