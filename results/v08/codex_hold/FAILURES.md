# v0.8 on Codex's holdout: execution failures in the raw records

From runner-side fields only, before any grading. A job that ends at a limit is not an execution failure of the runner; it is listed so that nothing is hidden. BAD and ERR are observations the model received (an illegal operation, or one that raised).
Run log: 22 runs, 0 non-zero exits, 0 tracebacks. start 2026-11-22T16:06:56Z commit eaecfcf04f92569694abdbd2390ad371b745a651; end 2026-11-22T16:27:17Z.

| File | jobs | ended DONE | ended ASK | ended at a limit | call limit | operation limit | time limit | context full | malformed script | empty script | sandbox crash or timeout | script raised | ops BAD or ERR | scripts | operations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| core/base_s1.jsonl | 220 | 168 | 30 | 22 | 9 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 233 | 1136 | 2239 |
| core/base_s2.jsonl | 220 | 170 | 32 | 18 | 3 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 165 | 1079 | 2217 |
| core/base_s3.jsonl | 220 | 175 | 24 | 21 | 5 | 0 | 0 | 16 | 0 | 0 | 0 | 0 | 180 | 1088 | 2210 |
| core/exec_s1.jsonl | 220 | 189 | 29 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 103 | 1069 | 2403 |
| core/exec_s2.jsonl | 220 | 162 | 36 | 22 | 0 | 0 | 0 | 14 | 8 | 0 | 0 | 0 | 21 | 1082 | 2404 |
| core/exec_s3.jsonl | 220 | 155 | 40 | 25 | 0 | 0 | 0 | 16 | 9 | 0 | 0 | 0 | 46 | 1088 | 2405 |
| core/search_s0.jsonl | 220 | 196 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 220 | 5935 |
| core/shuf_s1.jsonl | 220 | 173 | 31 | 16 | 0 | 0 | 0 | 9 | 7 | 0 | 0 | 0 | 167 | 1109 | 2576 |
| core/shuf_s2.jsonl | 220 | 152 | 30 | 38 | 3 | 0 | 0 | 18 | 17 | 0 | 0 | 0 | 201 | 1174 | 2667 |
| core/shuf_s3.jsonl | 220 | 157 | 51 | 12 | 0 | 0 | 0 | 5 | 7 | 0 | 0 | 0 | 185 | 1124 | 2616 |
| expl/obsonly_s1.jsonl | 220 | 187 | 23 | 10 | 0 | 0 | 0 | 1 | 9 | 0 | 0 | 0 | 17 | 956 | 1947 |
| expl/obsonly_s2.jsonl | 220 | 189 | 26 | 5 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 | 38 | 951 | 1941 |
| expl/obsonly_s3.jsonl | 220 | 196 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 933 | 1910 |
| expl/reconly_s1.jsonl | 220 | 175 | 37 | 8 | 0 | 0 | 0 | 6 | 2 | 0 | 0 | 0 | 130 | 1097 | 2462 |
| lim/base_s1.jsonl | 220 | 181 | 21 | 18 | 5 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 164 | 1090 | 2202 |
| lim/base_s2.jsonl | 220 | 163 | 35 | 22 | 2 | 0 | 0 | 16 | 4 | 0 | 0 | 0 | 184 | 1083 | 2174 |
| lim/base_s3.jsonl | 220 | 176 | 30 | 14 | 7 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 147 | 1086 | 2171 |
| lim/exec_s1.jsonl | 220 | 164 | 30 | 26 | 0 | 0 | 0 | 20 | 6 | 0 | 0 | 0 | 30 | 1100 | 2497 |
| lim/exec_s2.jsonl | 220 | 154 | 36 | 30 | 0 | 0 | 0 | 13 | 17 | 0 | 0 | 0 | 75 | 1064 | 2360 |
| lim/exec_s3.jsonl | 220 | 171 | 42 | 7 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 31 | 1048 | 2321 |
| mem/bank_s1.jsonl | 220 | 194 | 26 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 516 | 3129 |
| mem/bankguard_s1.jsonl | 220 | 195 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 433 | 9318 |
| **All files** | **4840** | **3842** | **682** | **316** | **34** | **0** | **0** | **195** | **87** | **0** | **0** | **0** | **2136** | **21526** | **62104** |
