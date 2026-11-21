### M3 final: joint edit success, % (mean over core seeds, range in brackets). Non-trivial eligible attempts; abstention counts as failure.

**Interchange-trained cores (5 seeds)**

| Method | A: unseen families, 2-3 legs | B: four legs | C: cross-gate legs | Pooled |
|---|---|---|---|---|
| Predictor edit (primary) | 99.9 (99.8–100.0) | 41.5 (32.7–54.2) | 86.5 (85.9–87.2) | 73.3 (70.0–78.2) |
| Slot-write edit | 99.9 (99.7–100.0) | 41.3 (32.0–54.4) | 86.3 (85.7–87.2) | 73.2 (69.5–78.3) |
| Message and resume | 100.0 (99.8–100.0) | 42.2 (33.7–54.7) | 86.3 (85.8–86.9) | 73.5 (70.3–78.4) |
| Full restart | 99.9 (99.7–100.0) | 43.9 (35.1–56.0) | 86.7 (86.0–87.5) | 74.3 (70.9–79.1) |
| Shortcut: overwrite whole state | 49.4 (49.1–49.7) | 20.8 (17.7–23.7) | 42.2 (41.9–42.7) | 36.2 (34.8–37.2) |
| Shortcut: copy actions | 35.0 (34.8–35.5) | 14.4 (12.2–16.1) | 32.0 (31.7–32.3) | 26.2 (25.2–26.9) |
| Per-family dictionary (privileged, 400 attempts) | 25.2 (21.1–31.4) | 8.8 (5.0–12.5) | 22.5 (19.9–25.7) | – |
| Core alone, no edit: every step valid | 100.0 (100.0–100.0) | 49.9 (41.7–61.6) | 84.4 (83.0–85.5) | – |

Eligible attempts per core: A 1,844 of 2,430 before the non-trivial filter, B 2,317 of 2,745 before the non-trivial filter, C 1,900 of 2,512 before the non-trivial filter (4,000 attempts each).

**Plain-imitation cores (2 seeds)**

| Method | A: unseen families, 2-3 legs | B: four legs | C: cross-gate legs | Pooled |
|---|---|---|---|---|
| Predictor edit (primary) | 17.4 (11.8–23.0) | 6.1 (3.7–8.5) | 15.2 (11.3–19.1) | 12.4 (8.6–16.2) |
| Slot-write edit | 9.2 (0.0–18.3) | 3.7 (0.6–6.7) | 9.3 (0.6–18.0) | 7.1 (0.4–13.8) |
| Message and resume | 99.9 (99.9–100.0) | 36.9 (35.2–38.7) | 84.8 (83.9–85.7) | 70.9 (70.6–71.3) |
| Full restart | 100.0 (100.0–100.0) | 39.2 (37.9–40.5) | 84.8 (83.8–85.8) | 71.8 (71.7–72.0) |
| Shortcut: overwrite whole state | 44.7 (43.6–45.8) | 17.0 (17.0–17.1) | 39.4 (39.4–39.4) | 32.4 (32.0–32.7) |
| Shortcut: copy actions | 35.4 (35.2–35.6) | 12.9 (12.8–13.0) | 31.0 (31.0–31.0) | 25.3 (25.3–25.4) |
| Per-family dictionary (privileged, 400 attempts) | 56.0 (54.4–57.6) | 17.9 (15.4–20.4) | 41.5 (41.1–41.8) | – |
| Core alone, no edit: every step valid | 100.0 (100.0–100.0) | 44.0 (43.1–44.8) | 83.3 (82.8–83.8) | – |

Eligible attempts per core: A 1,846 of 2,432 before the non-trivial filter, B 2,330 of 2,751 before the non-trivial filter, C 1,868 of 2,507 before the non-trivial filter (4,000 attempts each).

### Primary editor on interchange-trained cores, per seed (final strata)

| Core | A joint [95% CI] | B joint [95% CI] | C joint [95% CI] | Pooled | Abstained (pooled) | Unrelated drop A / B / C (points) | Message pooled |
|---|---|---|---|---|---|---|---|
| v2_iit_s1 | 99.9 [99.8, 100.0] | 36.0 [34.1, 37.9] | 87.2 [85.3, 89.1] | 71.5 | 0.00 | +0.0 / -1.4 / -2.5 | 71.7 |
| v2_iit_s2 | 99.8 [99.6, 100.0] | 42.3 [40.2, 44.5] | 86.0 [83.9, 87.9] | 73.5 | 0.00 | +0.1 / -1.3 / -2.0 | 73.8 |
| v2_iit_s3 | 100.0 [100.0, 100.0] | 42.4 [40.5, 44.2] | 85.9 [83.9, 87.8] | 73.5 | 0.00 | -0.1 / -1.1 / -2.3 | 73.6 |
| v2_iit_s4 | 99.9 [99.8, 100.0] | 32.7 [30.5, 34.8] | 87.0 [85.1, 88.9] | 70.0 | 0.00 | +0.0 / -1.6 / -2.7 | 70.3 |
| v2_iit_s5 | 99.9 [99.7, 100.0] | 54.2 [51.9, 56.3] | 86.3 [84.4, 88.0] | 78.2 | 0.00 | +0.1 / -1.0 / -3.5 | 78.4 |

### Secondary edit kinds on interchange-trained cores (final strata; mean over 5 seeds; joint success %)

| Kind | Stratum | Predictor | Slot write | Message | Restart |
|---|---|---|---|---|---|
| noop | A | 100.0 | 99.9 | 100.0 | – |
| noop | B | 51.5 | 51.6 | 52.1 | – |
| noop | C | 86.7 | 86.3 | 86.3 | – |
| impose | A | 99.9 | 100.0 | 100.0 | – |
| impose | B | 49.9 | 50.1 | 49.8 | – |
| impose | C | 83.1 | 83.2 | 83.3 | – |
| withdraw | A | 100.0 | 100.0 | 100.0 | – |
| withdraw | B | 51.2 | 51.7 | 51.4 | – |
| withdraw | C | 93.5 | 92.6 | 93.5 | – |
| two edits same | A | 99.8 | 97.7 | 100.0 | 99.9 |
| two edits same | B | 16.7 | 15.8 | 20.0 | 26.8 |
| two edits same | C | 75.1 | 72.9 | 76.9 | 78.4 |
| two edits other | A | 99.7 | 99.6 | 100.0 | 99.9 |
| two edits other | B | 45.3 | 45.4 | 48.2 | 50.9 |
| two edits other | C | 91.6 | 90.2 | 91.4 | 91.2 |
| mirror pairs (both jobs right) | A | 99.8 | 99.7 | 100.0 | – |
| mirror pairs (both jobs right) | B | 38.7 | 38.2 | 38.8 | – |
| mirror pairs (both jobs right) | C | 83.3 | 83.2 | 82.7 | – |

### Development families (selection data; mean over seeds)

| Cores | Predictor | Slot write | Message | Restart | Predictor abstained | Dictionary (privileged) |
|---|---|---|---|---|---|---|
| Interchange-trained | 99.9 (99.9–99.9) | 99.8 (99.2–100.0) | 100.0 (99.8–100.0) | 99.8 (99.2–100.0) | 0.0 (0.0–0.0) | 25.4 (15.8–29.4) |
| Plain imitation | 16.1 (10.6–21.6) | 9.6 (0.0–19.2) | 99.9 (99.9–100.0) | 100.0 (100.0–100.0) | 83.7 (78.2–89.2) | 56.8 (53.6–60.1) |

### Latency, one job, one CPU thread, after warm-up (µs; median over 600 timed runs, mean over 5 cores; 99th percentile in brackets)

| Path | Median | 99th percentile |
|---|---|---|
| Message and resume: one core step that reads the message | 331.5 | 5675 |
| Predictor edit, then one core step | 423.6 | 6492 |
| Slot-write edit, then one core step | 355.1 | 5139 |
| Predictor edit only (the saved state is corrected, the planner is not stepped) | 103.2 | 1452 |
| Slot-write edit only | 34.6 | 179 |
| Symbolic: change the table entry and re-plan the next route exactly | 6.3 | 8 |

Editor setup, per core: 114,560 training-family state pairs in 10.2 s; predictor (136,064 parameters) fitted in 30.2 s; abstention thresholds chosen on dev: iit_s1 0.0, iit_s2 0.0, iit_s3 0.0, iit_s4 0.0, iit_s5 0.0, plain_s1 0.98, plain_s2 0.95.
