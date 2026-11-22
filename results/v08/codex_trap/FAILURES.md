# v0.8 on Codex's trap set: execution failures in the raw records

From runner-side fields only, before any grading. A job that ends at a limit is not an execution failure of the runner; it is listed so that nothing is hidden. BAD and ERR are observations the model received (an illegal operation, or one that raised).
Run log: 4 runs, 0 non-zero exits, 0 tracebacks. start 2026-11-22T21:07:53Z commit 19ad8cdb737b416f080296b372679f5bd3f5b3f4 load { 2.74 2.43 2.34 }; end 2026-11-22T21:09:59Z load { 3.04 2.58 2.41 }.

| File | jobs | ended DONE | ended ASK | ended at a limit | call limit | operation limit | time limit | context full | malformed script | empty script | sandbox crash or timeout | script raised | ops BAD or ERR | scripts | operations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run/bank_s1.jsonl | 137 | 130 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 456 | 3131 |
| run/bankguard_s1.jsonl | 137 | 79 | 58 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 240 | 11001 |
| run/exec_s1.jsonl | 137 | 120 | 16 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 92 | 1035 | 2266 |
| run/search_s0.jsonl | 137 | 137 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 137 | 5900 |
| **All files** | **548** | **466** | **81** | **1** | **0** | **0** | **0** | **1** | **0** | **0** | **0** | **0** | **105** | **1868** | **22298** |
