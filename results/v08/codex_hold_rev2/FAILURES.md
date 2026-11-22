# v0.8 on revision 2 of Codex's holdout: execution failures in the raw records

From runner-side fields only, before any grading. A job that ends at a limit is not an execution failure of the runner; it is listed so that nothing is hidden. BAD and ERR are observations the model received (an illegal operation, or one that raised).
Run log: 22 runs, 0 non-zero exits, 0 tracebacks. start 2026-11-22T17:31:54Z commit 85984433a5b1c78f378e713efa8cdcc50bf78002; end 2026-11-22T17:51:52Z.

| File | jobs | ended DONE | ended ASK | ended at a limit | call limit | operation limit | time limit | context full | malformed script | empty script | sandbox crash or timeout | script raised | ops BAD or ERR | scripts | operations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| core/base_s1.jsonl | 220 | 177 | 30 | 13 | 6 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 139 | 1068 | 2126 |
| core/base_s2.jsonl | 220 | 167 | 31 | 22 | 3 | 0 | 0 | 19 | 0 | 0 | 0 | 0 | 207 | 1111 | 2292 |
| core/base_s3.jsonl | 220 | 175 | 32 | 13 | 3 | 0 | 0 | 9 | 1 | 0 | 0 | 0 | 132 | 1049 | 2111 |
| core/exec_s1.jsonl | 220 | 179 | 36 | 5 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 | 106 | 1048 | 2332 |
| core/exec_s2.jsonl | 220 | 163 | 37 | 20 | 0 | 0 | 0 | 15 | 5 | 0 | 0 | 0 | 32 | 1038 | 2288 |
| core/exec_s3.jsonl | 220 | 158 | 40 | 22 | 0 | 0 | 0 | 15 | 7 | 0 | 0 | 0 | 44 | 1054 | 2328 |
| core/search_s0.jsonl | 220 | 196 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 220 | 6190 |
| core/shuf_s1.jsonl | 220 | 168 | 37 | 15 | 0 | 0 | 0 | 9 | 6 | 0 | 0 | 0 | 123 | 1111 | 2520 |
| core/shuf_s2.jsonl | 220 | 146 | 31 | 43 | 1 | 0 | 0 | 27 | 15 | 0 | 0 | 0 | 247 | 1198 | 2744 |
| core/shuf_s3.jsonl | 220 | 161 | 56 | 3 | 0 | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 215 | 1149 | 2671 |
| expl/obsonly_s1.jsonl | 220 | 190 | 25 | 5 | 0 | 0 | 0 | 2 | 3 | 0 | 0 | 0 | 15 | 943 | 1921 |
| expl/obsonly_s2.jsonl | 220 | 184 | 32 | 4 | 0 | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 36 | 947 | 1925 |
| expl/obsonly_s3.jsonl | 220 | 191 | 25 | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 923 | 1880 |
| expl/reconly_s1.jsonl | 220 | 171 | 37 | 12 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 0 | 122 | 1089 | 2448 |
| lim/base_s1.jsonl | 220 | 176 | 30 | 14 | 4 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 128 | 1063 | 2146 |
| lim/base_s2.jsonl | 220 | 169 | 36 | 15 | 2 | 0 | 0 | 11 | 2 | 0 | 0 | 0 | 138 | 1039 | 2110 |
| lim/base_s3.jsonl | 220 | 176 | 28 | 16 | 7 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 162 | 1085 | 2174 |
| lim/exec_s1.jsonl | 220 | 164 | 36 | 20 | 0 | 0 | 0 | 13 | 7 | 0 | 0 | 0 | 21 | 1064 | 2367 |
| lim/exec_s2.jsonl | 220 | 149 | 36 | 35 | 0 | 0 | 0 | 17 | 18 | 0 | 0 | 0 | 82 | 1049 | 2354 |
| lim/exec_s3.jsonl | 220 | 176 | 38 | 6 | 0 | 0 | 0 | 5 | 1 | 0 | 0 | 0 | 33 | 1016 | 2227 |
| mem/bank_s1.jsonl | 220 | 189 | 30 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 15 | 480 | 3197 |
| mem/bankguard_s1.jsonl | 220 | 191 | 28 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 9 | 416 | 9480 |
| **All files** | **4840** | **3816** | **735** | **289** | **26** | **0** | **0** | **188** | **75** | **0** | **0** | **0** | **2006** | **21160** | **61831** |
