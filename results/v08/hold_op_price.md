# Holdout: what a verified job costs when an operation has a price

Cost per verified job = (seconds per job + price x operations per job) / verified share. Seconds are measured; the price of an operation is the unknown. Seeds pooled.

| | Seconds per job | Operations per job | Verified % | Cost per verified job at 0 s per operation | at 0.05 s | at 0.5 s | at 5 s |
|---|---|---|---|---|---|---|---|
| base, proj | 0.398 | 12.6 | 42.0 | 0.95 | 2.45 | 15.92 | 150.64 |
| exec, proj | 0.402 | 14.0 | 62.5 | 0.64 | 1.76 | 11.82 | 112.41 |
| shuf, proj | 0.451 | 16.3 | 40.8 | 1.11 | 3.11 | 21.13 | 201.32 |
| teacher, proj | 0.316 | 10.9 | 100.0 | 0.32 | 0.86 | 5.75 | 54.61 |
| search, proj | 0.088 | 45.8 | 100.0 | 0.09 | 2.38 | 22.96 | 228.85 |

On project jobs the execution-aware core costs less per verified job than the search script once an operation costs more than **24 ms** (below that, search is cheaper; search is also never wrong on these jobs, and the core is wrong on 22% of them).
The teacher's careful procedure, which is what the core imitates, would cross the search script at 7 ms per operation.
