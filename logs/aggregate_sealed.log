### A. Ordinary accuracy and the paired replay (sealed fixtures; mean over seeds, range in brackets; %)

| Arm | Seeds | Plain | Dynamic | Mid-plan reversal pairs | Targeted swap | Shuffled | Improvement | Unrelated drop | Slots |
|---|---|---|---|---|---|---|---|---|---|
| Discrete + interchange training | 5 | 99.6 (97.8–100.0) | 99.6 (98.4–100.0) | 99.1 (96.4–100.0) | 99.3 (96.8–100.0) | 50.4 (50.2–50.4) | 48.9 (46.6–49.5) | 0.0 (0.0–0.0) | [0]; [0]; [0]; [0]; [0] |
| Discrete, plain imitation | 3 | 99.1 (97.4–100.0) | 99.3 (98.0–100.0) | 98.4 (95.2–100.0) | 37.2 (36.0–38.5) | 28.4 (22.8–32.5) | 8.8 (6.0–13.3) | 31.8 (0.0–58.6) | [2, 3]; [1]; [1, 3] |
| Continuous, plain imitation | 3 | 99.3 (97.8–100.0) | 99.5 (98.8–100.0) | 98.6 (95.8–100.0) | 36.9 (28.1–45.8) | 24.0 (19.7–28.0) | 12.9 (8.5–17.8) | 51.6 (40.8–65.9) | [2, 3]; [1, 2]; [0, 1] |
| Continuous + interchange training | 3 | 99.0 (97.0–100.0) | 99.3 (97.8–100.0) | 98.4 (95.2–100.0) | 98.1 (94.2–100.0) | 50.3 (50.0–50.4) | 47.8 (44.2–49.5) | 0.0 (0.0–0.0) | [0]; [0]; [0] |
| Continuous, quantised after training | 3 | 99.3 (98.0–100.0) | 99.5 (98.8–100.0) | 98.6 (95.8–100.0) | 36.6 (28.9–44.4) | 24.8 (22.1–27.9) | 11.9 (6.8–16.4) | 51.0 (43.0–59.7) | [2, 3]; [0, 1]; [0, 1] |
| Continuous + interchange, quantised after | 3 | 99.0 (97.0–100.0) | 99.3 (97.8–100.0) | 98.4 (95.2–100.0) | 98.1 (94.2–100.0) | 50.3 (50.0–50.4) | 47.8 (44.2–49.5) | 0.0 (0.0–0.0) | [0]; [0]; [0, 3] |
| Discrete, world never changes in training | 2 | 97.0 (94.2–99.8) | 88.1 (83.8–92.4) | 42.2 (23.6–60.8) | 17.1 (13.2–21.1) | 18.6 (17.5–19.7) | -1.4 (-6.4–3.5) | 49.8 (48.4–51.1) | [2, 3]; [0, 3] |
| Discrete + planted hidden channel | 2 | 99.7 (99.4–100.0) | 99.6 (99.4–99.8) | 99.4 (98.8–100.0) | 29.8 (28.2–31.3) | 20.4 (18.6–22.2) | 9.4 (6.0–12.8) | 44.3 (33.7–55.0) | [2, 3]; [0, 1] |
| Discrete + interchange + planted channel | 1 | 99.2 | 99.4 | 96.8 | 99.6 | 51.0 | 48.5 | 0.0 | [0] |
| Discrete + planted channel (strong weight) | 1 | 100.0 | 99.8 | 99.6 | 60.8 | 43.5 | 17.2 | 7.4 | [3] |
| Discrete + planted channel (earlier recipe: ordinary training profile only) | 1 | 98.8 | 99.2 | 98.6 | 47.1 | 24.4 | 22.7 | 14.3 | [0, 2] |
| Discrete + effect head | 2 | 92.5 (92.0–93.0) | 91.7 (91.2–92.2) | 82.9 (79.0–86.8) | 32.1 (29.6–34.7) | 21.2 (19.1–23.2) | 11.0 (10.4–11.6) | 51.1 (48.8–53.4) | [0, 2]; [0, 3] |
| Discrete, flat reader | 1 | 93.0 | 93.4 | 84.0 | 32.4 | 23.2 | 9.2 | 50.4 | [0, 1] |

### B. Per-seed primary endpoint with 95% intervals (families resampled; %)

| Run | Targeted | Shuffled | Improvement [95% CI] | Unrelated drop [95% CI] | Both unmodified runs valid | Resume twice identical |
|---|---|---|---|---|---|---|
| f_iit_s1 | 96.8 | 50.2 | +46.6 [+41.4, +50.4] | 0.0 [0.0, 0.0] | 92.0 | 100.0 |
| f_iit_s2 | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_iit_s3 | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_iit_s4 | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_iit_s5 | 99.6 | 50.3 | +49.2 [+46.9, +51.4] | 0.0 [0.0, 0.0] | 99.7 | 100.0 |
| f_vq_s1 | 37.1 | 30.1 | +7.0 [+4.4, +9.8] | 36.7 [34.4, 38.8] | 89.8 | 100.0 |
| f_vq_s2 | 38.5 | 32.5 | +6.0 [+2.8, +8.9] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_vq_s3 | 36.0 | 22.8 | +13.3 [+10.8, +15.7] | 58.6 [56.5, 60.7] | 100.0 | 100.0 |
| f_cont_s1 | 45.8 | 28.0 | +17.8 [+14.8, +20.5] | 40.8 [38.1, 43.4] | 91.8 | 100.0 |
| f_cont_s2 | 28.1 | 19.7 | +8.5 [+6.9, +9.9] | 65.9 [64.1, 67.7] | 100.0 | 100.0 |
| f_cont_s3 | 36.9 | 24.4 | +12.5 [+10.1, +14.7] | 48.1 [46.0, 50.0] | 100.0 | 100.0 |
| f_contiit_s1 | 94.2 | 50.0 | +44.2 [+36.9, +49.7] | 0.0 [0.0, 0.0] | 88.3 | 100.0 |
| f_contiit_s2 | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_contiit_s3 | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_cont_s1_posthoc | 44.4 | 27.9 | +16.4 [+13.2, +19.5] | 43.0 [40.0, 45.9] | 91.5 | 100.0 |
| f_cont_s2_posthoc | 28.9 | 22.1 | +6.8 [+4.5, +9.3] | 59.7 [57.1, 62.2] | 100.0 | 100.0 |
| f_cont_s3_posthoc | 36.5 | 24.2 | +12.3 [+8.8, +15.5] | 50.1 [48.5, 51.9] | 100.0 | 100.0 |
| f_contiit_s1_posthoc | 94.2 | 50.0 | +44.2 [+37.0, +49.6] | 0.0 [0.0, 0.0] | 88.2 | 100.0 |
| f_contiit_s2_posthoc | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 [0.0, 0.0] | 99.8 | 100.0 |
| f_contiit_s3_posthoc | 100.0 | 50.4 | +49.5 [+47.2, +51.7] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_static_s1 | 21.1 | 17.5 | +3.5 [-3.8, +10.0] | 48.4 [46.9, 49.9] | 99.9 | 100.0 |
| f_static_s2 | 13.2 | 19.7 | -6.4 [-11.3, -0.1] | 51.1 [49.4, 52.7] | 76.7 | 100.0 |
| f_hidden_s1 | 31.3 | 18.6 | +12.8 [+10.2, +15.2] | 33.7 [31.2, 36.0] | 97.6 | 100.0 |
| f_hidden_s2 | 28.2 | 22.2 | +6.0 [+4.2, +8.0] | 55.0 [52.9, 57.0] | 100.0 | 100.0 |
| f_iithidden_s1 | 99.6 | 51.0 | +48.5 [+45.5, +51.1] | 0.0 [0.0, 0.0] | 96.6 | 100.0 |
| f_hiddenw_s2 | 60.8 | 43.5 | +17.2 [+14.8, +19.6] | 7.4 [6.4, 8.5] | 100.0 | 100.0 |
| f_hiddenx_s1 | 47.1 | 24.4 | +22.7 [+21.0, +24.2] | 14.3 [12.4, 16.4] | 97.4 | 100.0 |
| f_sat_s1 | 34.7 | 23.2 | +11.6 [+7.6, +16.0] | 48.8 [45.9, 51.8] | 85.0 | 100.0 |
| f_sat_s2 | 29.6 | 19.1 | +10.4 [+5.9, +14.8] | 53.4 [51.0, 55.8] | 79.7 | 100.0 |
| f_flat_s1 | 32.4 | 23.2 | +9.2 [+5.0, +12.5] | 50.4 [48.7, 52.4] | 82.2 | 100.0 |

### C. Replay controls (mean over seeds; %)

| Arm | Whole-state transplant: gate follows donor | Same-goal donor: stable | Blank memory: gate right | Message revision | Slots changed by a gate message | Restart from full order | Repaint: same actions | Slots changed by repaint |
|---|---|---|---|---|---|---|---|---|
| Discrete + interchange training | 99.2 (96.2–100.0) | 99.3 (96.5–100.0) | 50.2 (49.5–52.3) | 100.0 (100.0–100.0) | 3.8 (3.7–3.9) | 99.9 (99.5–100.0) | 95.1 (88.8–96.9) | 0.1 (0.0–0.3) |
| Discrete, plain imitation | 98.4 (95.2–100.0) | 57.3 (44.2–73.2) | 50.8 (49.6–52.1) | 100.0 (100.0–100.0) | 3.9 (3.8–4.0) | 100.0 (100.0–100.0) | 96.9 (96.0–97.8) | 0.2 (0.1–0.4) |
| Continuous, plain imitation | 98.5 (95.5–100.0) | 50.0 (40.2–64.1) | 50.0 (49.8–50.2) | 100.0 (100.0–100.0) | 4.0 (4.0–4.0) | 100.0 (99.9–100.0) | 95.1 (94.3–96.7) | 4.0 (4.0–4.0) |
| Continuous + interchange training | 98.1 (94.3–100.0) | 98.0 (94.1–100.0) | 49.5 (49.2–49.8) | 100.0 (100.0–100.0) | 4.0 (4.0–4.0) | 100.0 (100.0–100.0) | 95.5 (94.0–97.0) | 4.0 (4.0–4.0) |
| Continuous, quantised after training | 98.4 (95.1–100.0) | 53.9 (45.2–64.8) | 49.4 (48.4–50.0) | 100.0 (99.9–100.0) | 4.0 (4.0–4.0) | 100.0 (99.9–100.0) | 95.4 (94.3–97.2) | 0.1 (0.0–0.1) |
| Continuous + interchange, quantised after | 98.1 (94.3–100.0) | 98.0 (94.2–100.0) | 49.5 (49.2–49.7) | 100.0 (100.0–100.0) | 4.0 (3.9–4.0) | 100.0 (100.0–100.0) | 95.6 (93.8–97.4) | 0.1 (0.0–0.1) |
| Discrete, world never changes in training | 49.8 (29.1–70.5) | 46.2 (40.9–51.4) | 48.8 (48.7–48.9) | 95.2 (92.5–98.0) | 3.9 (3.7–4.0) | 93.8 (92.6–95.0) | 97.0 (96.0–97.9) | 0.3 (0.1–0.4) |
| Discrete + planted hidden channel | 99.4 (98.8–100.0) | 53.0 (37.9–68.0) | 49.4 (49.0–49.9) | 100.0 (100.0–100.0) | 4.0 (4.0–4.0) | 100.0 (100.0–100.0) | 93.8 (90.9–96.8) | 0.8 (0.7–1.0) |
| Discrete + interchange + planted channel | 98.0 | 98.2 | 47.9 | 100.0 | 4.0 | 100.0 | 95.0 | 0.1 |
| Discrete + planted channel (strong weight) | 100.0 | 72.0 | 50.5 | 100.0 | 3.1 | 100.0 | 97.7 | 0.4 |
| Discrete + planted channel (earlier recipe: ordinary training profile only) | 98.9 | 83.7 | 49.1 | 100.0 | 4.0 | 100.0 | 96.0 | 0.1 |
| Discrete + effect head | 91.7 (91.3–92.0) | 39.8 (37.5–42.1) | 50.0 (49.9–50.0) | 97.0 (96.2–97.8) | 3.6 (3.6–3.7) | 97.3 (97.2–97.4) | 95.0 (94.5–95.7) | 0.1 (0.1–0.1) |
| Discrete, flat reader | 89.5 | 48.9 | 50.4 | 85.2 | 4.0 | 85.4 | 98.0 | 0.8 |

### D. Exhaustive check: every reachable state against every observation, per family

| Run | Families | Pairs checked | Wrong | Wrong % | Families with a wrong pair | Code states per family (after INIT … BAY) | Meanings |
|---|---|---|---|---|---|---|---|
| f_iit_s1 | 100 | 98,176,640 | 30,010 | 0.0306 | 6 | 21 112 122 113 120 212 | 12 12 12 6 3 1 |
| f_iit_s2 | 100 | 126,197,760 | 151 | 0.0001 | 3 | 19 126 211 178 178 347 | 12 12 12 6 3 1 |
| f_iit_s3 | 100 | 72,407,040 | 21 | 0.0000 | 1 | 14 84 126 95 119 258 | 12 12 12 6 3 1 |
| f_iit_s4 | 100 | 174,345,600 | 3 | 0.0000 | 1 | 27 189 281 258 294 531 | 12 12 12 6 3 1 |
| f_iit_s5 | 100 | 133,248,000 | 24,077 | 0.0181 | 4 | 12 93 145 164 245 586 | 12 12 12 6 3 1 |
| f_vq_s1 | 100 | 146,609,280 | 45,092 | 0.0308 | 5 | 43 180 195 177 177 236 | 12 12 12 6 3 1 |
| f_vq_s2 | 100 | 117,161,600 | 257,329 | 0.2196 | 66 | 30 122 162 154 169 198 | 12 12 12 6 3 1 |
| f_vq_s3 | 100 | 66,565,120 | 120 | 0.0002 | 4 | 20 94 105 96 103 153 | 12 12 12 6 3 1 |
| f_cont_s1_posthoc | 100 | 115,235,840 | 143,455 | 0.1245 | 44 | 20 101 121 113 218 533 | 12 12 12 6 3 1 |
| f_cont_s2_posthoc | 100 | 139,784,960 | 1,045,202 | 0.7477 | 67 | 14 88 138 146 251 738 | 12 12 12 6 3 1 |
| f_cont_s3_posthoc | 100 | 118,383,360 | 150,441 | 0.1271 | 37 | 14 83 113 111 289 636 | 12 12 12 6 3 1 |
| f_contiit_s1_posthoc | 100 | 261,444,480 | 2,697,336 | 1.0317 | 68 | 24 156 279 274 388 653 | 12 12 12 6 3 1 |
| f_contiit_s2_posthoc | 100 | 194,311,680 | 758,881 | 0.3905 | 32 | 30 270 423 411 716 155 | 12 12 12 6 3 0 |
| f_contiit_s3_posthoc | 100 | 169,865,600 | 126,865 | 0.0747 | 14 | 21 160 233 208 442 955 | 12 12 12 6 3 1 |
| f_static_s1 | 100 | 67,546,880 | 1,871,930 | 2.7713 | 75 | 26 37 60 64 76 90 | 6 5 5 3 3 1 |
| f_hiddenw_s2 | 25 | 126,874,240 | 509,173 | 0.4013 | 19 | 101 549 607 666 447 357 | 12 12 12 6 3 1 |
| f_hiddenx_s1 | 25 | 86,169,600 | 323,175 | 0.3750 | 25 | 62 278 445 557 399 422 | 12 12 12 6 3 1 |

### E. Typed patch, quotient memory, corruption alarm (%)

| Run | Typed patch credit | Patch undefined | Plain: dynamic / mid-plan | Spec quotient: dynamic / mid-plan | Behaviour quotient: dynamic / mid-plan | One slot corrupted: harmful | Harmful caught by dictionary | Missed |
|---|---|---|---|---|---|---|---|---|
| f_iit_s1 | 96.0 | 0.0 | 98.4 / 96.4 | 98.4 / 96.4 | 98.4 / 96.4 | 45.1 | 99.6 | 4 |
| f_iit_s2 | 100.0 | 0.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 42.1 | 100.0 | 0 |
| f_iit_s3 | 100.0 | 0.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 41.9 | 100.0 | 0 |
| f_iit_s4 | 100.0 | 0.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 40.9 | 100.0 | 0 |
| f_iit_s5 | 99.6 | 0.0 | 99.8 / 99.0 | 99.8 / 99.0 | 99.8 / 99.0 | 42.1 | 100.0 | 0 |
| f_vq_s1 | 95.0 | 0.0 | 98.0 / 95.2 | 98.0 / 95.2 | 98.0 / 95.2 | 13.7 | 99.3 | 2 |
| f_vq_s2 | 100.0 | 0.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 29.3 | 100.0 | 0 |
| f_vq_s3 | 100.0 | 0.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 14.2 | 100.0 | 0 |
| f_cont_s1_posthoc | 95.3 | 0.0 | 98.8 / 95.8 | 98.6 / 95.8 | 98.8 / 95.8 | 5.5 | 98.2 | 2 |
| f_cont_s2_posthoc | 100.0 | 0.0 | 99.8 / 100.0 | 99.8 / 100.0 | 99.8 / 100.0 | 3.5 | 100.0 | 0 |
| f_cont_s3_posthoc | 100.0 | 0.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 6.9 | 100.0 | 0 |
| f_static_s1 | 68.3 | 31.6 | 92.4 / 60.8 | 92.2 / 59.8 | 92.4 / 60.8 | 0.4 | 100.0 | 0 |
| f_hiddenw_s2 | 100.0 | 0.0 | 99.8 / 99.6 | 100.0 / 100.0 | 99.8 / 99.6 | 32.7 | 100.0 | 0 |
| f_hiddenx_s1 | 98.4 | 0.0 | 99.2 / 98.6 | 99.0 / 98.2 | 99.2 / 98.6 | 18.8 | 100.0 | 0 |

### F. Planted hidden channel (bit accuracy; 50% is chance)

```json
{"f_hiddenw_s2": {"plain": {"task_all_valid": 0.9984999895095825, "own_head_bit_accuracy": 0.9398750066757202, "fresh_decoder_bit_accuracy": 0.9273750185966492, "unknown_state_rate": 0.0, "distinct_code_states_before_last_stage": 183}, "behaviour": {"task_all_valid": 0.9984999895095825, "own_head_bit_accuracy": 0.5077499747276306, "fresh_decoder_bit_accuracy": 0.5027499794960022, "unknown_state_rate": 0.0, "distinct_code_states_before_last_stage": 10}, "spec": {"task_all_valid": 0.9992499947547913, "own_head_bit_accuracy": 0.5077499747276306, "fresh_decoder_bit_accuracy": 0.5027499794960022, "unknown_state_rate": 0.0, "distinct_code_states_before_last_stage": 10}}}
{"f_hiddenx_s1": {"plain": {"task_all_valid": 0.9950000047683716, "own_head_bit_accuracy": 0.9679999947547913, "fresh_decoder_bit_accuracy": 0.9589999914169312, "unknown_state_rate": 0.0, "distinct_code_states_before_last_stage": 86}, "behaviour": {"task_all_valid": 0.9950000047683716, "own_head_bit_accuracy": 0.512624979019165, "fresh_decoder_bit_accuracy": 0.5086249709129333, "unknown_state_rate": 0.0, "distinct_code_states_before_last_stage": 4}, "spec": {"task_all_valid": 0.9919999837875366, "own_head_bit_accuracy": 0.512624979019165, "fresh_decoder_bit_accuracy": 0.5086249709129333, "unknown_state_rate": 0.030458333333333334, "distinct_code_states_before_last_stage": 4}}}
```

### G. Monitoring readers

```json
{"f_iit_s1": {"n_train": 6000, "n_val": 3000, "n_test": 3000, "test_families": "sealed", "bad_rate_test": 0.46366666666666667, "code_reader_t0": {"recall": 0.9748382458662832, "false_alarm": 0.014294592914853946, "missed": 35, "bad_runs": 1391}, "public_reader_t0": {"recall": 0.035945363048166784, "false_alarm": 0.024860161591050343, "missed": 1341, "bad_runs": 1391}, "public_reader_t1": {"recall": 0.021567217828900073, "false_alarm": 0.016159105034182723, "missed": 1361, "bad_runs": 1391}, "public_reader_t2": {"recall": 0.5442127965492451, "false_alarm": 0.030453697949036667, "missed": 634, "bad_runs": 1391}, "public_reader_t3": {"recall": 0.6829618979151689, "false_alarm": 0.031696706028589185, "missed": 441, "bad_runs": 1391}, "dictionary_t0": {"recall": 0.9748382458662832, "false_alarm": 0.004972032318210068, "missed": 35, "bad_runs": 1391}, "gate_observation_mode": {"jobs": 3000, "bad_proposals": 1391, "bad_that_would_be_blocked": 1356, "valid_that_would_be_blocked": 8, "completed_jobs": 3000}, "seconds": 29.1}}
{"f_iit_s2": {"n_train": 6000, "n_val": 3000, "n_test": 3000, "test_families": "sealed", "bad_rate_test": 0.45466666666666666, "code_reader_t0": {"recall": 1.0, "false_alarm": 0.023227383863080684, "missed": 0, "bad_runs": 1364}, "public_reader_t0": {"recall": 0.030791788856304986, "false_alarm": 0.029339853300733496, "missed": 1322, "bad_runs": 1364}, "public_reader_t1": {"recall": 0.06085043988269795, "false_alarm": 0.017114914425427872, "missed": 1281, "bad_runs": 1364}, "public_reader_t2": {"recall": 0.5491202346041055, "false_alarm": 0.008557457212713936, "missed": 615, "bad_runs": 1364}, "public_reader_t3": {"recall": 0.5542521994134897, "false_alarm": 0.0, "missed": 608, "bad_runs": 1364}, "dictionary_t0": {"recall": 1.0, "false_alarm": 0.0, "missed": 0, "bad_runs": 1364}, "gate_observation_mode": {"jobs": 3000, "bad_proposals": 1364, "bad_that_would_be_blocked": 1364, "valid_that_would_be_blocked": 0, "completed_jobs": 3000}, "seconds": 39.9}}
{"f_iit_s3": {"n_train": 6000, "n_val": 3000, "n_test": 3000, "test_families": "sealed", "bad_rate_test": 0.45466666666666666, "code_reader_t0": {"recall": 1.0, "false_alarm": 0.013447432762836185, "missed": 0, "bad_runs": 1364}, "public_reader_t0": {"recall": 0.030791788856304986, "false_alarm": 0.029339853300733496, "missed": 1322, "bad_runs": 1364}, "public_reader_t1": {"recall": 0.07771260997067449, "false_alarm": 0.029339853300733496, "missed": 1258, "bad_runs": 1364}, "public_reader_t2": {"recall": 0.5608504398826979, "false_alarm": 0.04095354523227384, "missed": 599, "bad_runs": 1364}, "public_reader_t3": {"recall": 0.6444281524926686, "false_alarm": 0.011002444987775062, "missed": 485, "bad_runs": 1364}, "dictionary_t0": {"recall": 1.0, "false_alarm": 0.0, "missed": 0, "bad_runs": 1364}, "gate_observation_mode": {"jobs": 3000, "bad_proposals": 1364, "bad_that_would_be_blocked": 1364, "valid_that_would_be_blocked": 0, "completed_jobs": 3000}, "seconds": 29.1}}
{"f_iit_s4": {"n_train": 6000, "n_val": 3000, "n_test": 3000, "test_families": "sealed", "bad_rate_test": 0.45466666666666666, "code_reader_t0": {"recall": 1.0, "false_alarm": 0.014058679706601468, "missed": 0, "bad_runs": 1364}, "public_reader_t0": {"recall": 0.030791788856304986, "false_alarm": 0.029339853300733496, "missed": 1322, "bad_runs": 1364}, "public_reader_t1": {"recall": 0.024926686217008796, "false_alarm": 0.012836185819070905, "missed": 1330, "bad_runs": 1364}, "public_reader_t2": {"recall": 0.533724340175953, "false_alarm": 0.0, "missed": 636, "bad_runs": 1364}, "public_reader_t3": {"recall": 0.5967741935483871, "false_alarm": 0.009168704156479218, "missed": 550, "bad_runs": 1364}, "dictionary_t0": {"recall": 1.0, "false_alarm": 0.0, "missed": 0, "bad_runs": 1364}, "gate_observation_mode": {"jobs": 3000, "bad_proposals": 1364, "bad_that_would_be_blocked": 1364, "valid_that_would_be_blocked": 0, "completed_jobs": 3000}, "seconds": 26.6}}
{"f_iit_s5": {"n_train": 6000, "n_val": 3000, "n_test": 3000, "test_families": "sealed", "bad_rate_test": 0.456, "code_reader_t0": {"recall": 0.9963450292397661, "false_alarm": 0.009191176470588236, "missed": 5, "bad_runs": 1368}, "public_reader_t0": {"recall": 0.02850877192982456, "false_alarm": 0.026348039215686275, "missed": 1329, "bad_runs": 1368}, "public_reader_t1": {"recall": 0.03435672514619883, "false_alarm": 0.0, "missed": 1321, "bad_runs": 1368}, "public_reader_t2": {"recall": 0.5519005847953217, "false_alarm": 0.01715686274509804, "missed": 613, "bad_runs": 1368}, "public_reader_t3": {"recall": 0.6374269005847953, "false_alarm": 0.020833333333333332, "missed": 496, "bad_runs": 1368}, "dictionary_t0": {"recall": 0.9963450292397661, "false_alarm": 0.0006127450980392157, "missed": 5, "bad_runs": 1368}, "gate_observation_mode": {"jobs": 3000, "bad_proposals": 1368, "bad_that_would_be_blocked": 1363, "valid_that_would_be_blocked": 1, "completed_jobs": 3000}, "seconds": 28.5}}
```

### H. Continuous memory: swap along one direction

```json
{"f_cont_s1": {"mean_difference": {"n": 2000, "targeted": 0.913, "shuffled": 0.491, "improvement": 0.422, "ci95": [0.3634837329265018, 0.4633604799501768]}, "discriminant": {"n": 2000, "targeted": 0.9555, "shuffled": 0.4915, "improvement": 0.464, "ci95": [0.4140809047190405, 0.5015291489649939]}}}
{"f_cont_s2": {"mean_difference": {"n": 2000, "targeted": 0.3295, "shuffled": 0.2215, "improvement": 0.108, "ci95": [0.07970602766798418, 0.13482687939726332]}, "discriminant": {"n": 2000, "targeted": 0.6145, "shuffled": 0.306, "improvement": 0.3085, "ci95": [0.2788349364130126, 0.3418676012929738]}}}
{"f_cont_s3": {"mean_difference": {"n": 2000, "targeted": 0.3325, "shuffled": 0.332, "improvement": 0.0005, "ci95": [-0.027907271868728604, 0.0318073215491541]}, "discriminant": {"n": 2000, "targeted": 0.8415, "shuffled": 0.4185, "improvement": 0.423, "ci95": [0.3947080211103054, 0.4527914214747246]}}}
{"f_contiit_s1": {"mean_difference": {"n": 2000, "targeted": 0.9415, "shuffled": 0.4995, "improvement": 0.442, "ci95": [0.3762237494766, 0.49010435699699056]}, "discriminant": {"n": 2000, "targeted": 0.9415, "shuffled": 0.4935, "improvement": 0.448, "ci95": [0.3859738705189065, 0.4956313113144463]}}}
{"f_contiit_s2": {"mean_difference": {"n": 2000, "targeted": 0.9995, "shuffled": 0.5065, "improvement": 0.493, "ci95": [0.4737310362722729, 0.5092852667985213]}, "discriminant": {"n": 2000, "targeted": 1.0, "shuffled": 0.496, "improvement": 0.504, "ci95": [0.48410366376277647, 0.5230852637987131]}}}
{"f_contiit_s3": {"mean_difference": {"n": 2000, "targeted": 1.0, "shuffled": 0.5065, "improvement": 0.4935, "ci95": [0.47473415795088864, 0.5096646992089136]}, "discriminant": {"n": 2000, "targeted": 1.0, "shuffled": 0.496, "improvement": 0.504, "ci95": [0.48410366376277647, 0.5230852637987131]}}}
```

### I. Bits the code carries about the gate

```json
{"f_iit_s1": {"instructed": true, "stages": {"INIT": {"bits_about_gate": 0.013, "bits_about_decor_bit": 0.01, "distinct_code_states": 26}, "PLAN": {"bits_about_gate": 0.039, "bits_about_decor_bit": 0.047, "distinct_code_states": 114}, "LEG1": {"bits_about_gate": 0.038, "bits_about_decor_bit": 0.018, "distinct_code_states": 129}, "DOCK": {"bits_about_gate": 0.034, "bits_about_decor_bit": 0.015, "distinct_code_states": 111}, "LEG2": {"bits_about_gate": 0.035, "bits_about_decor_bit": 0.012, "distinct_code_states": 129}, "BAY": {"bits_about_gate": 0.162, "bits_about_decor_bit": 0.017, "distinct_code_states": 176}}, "all_valid": 0.9999499917030334}}
{"f_vq_s1": {"instructed": true, "stages": {"INIT": {"bits_about_gate": 0.04, "bits_about_decor_bit": 0.04, "distinct_code_states": 60}, "PLAN": {"bits_about_gate": 0.029, "bits_about_decor_bit": 0.047, "distinct_code_states": 171}, "LEG1": {"bits_about_gate": 0.033, "bits_about_decor_bit": 0.022, "distinct_code_states": 199}, "DOCK": {"bits_about_gate": 0.047, "bits_about_decor_bit": 0.024, "distinct_code_states": 167}, "LEG2": {"bits_about_gate": 0.043, "bits_about_decor_bit": 0.027, "distinct_code_states": 177}, "BAY": {"bits_about_gate": 0.18, "bits_about_decor_bit": 0.071, "distinct_code_states": 209}}, "all_valid": 1.0}}
```

### J. Timing

```json
{"f_iit_s1": {"cpu_1_thread": {"resume": {"median_us": 206.3, "p99_us": 228.8, "n": 600}, "restart": {"median_us": 592.8, "p99_us": 645.7, "n": 600}, "one_step": {"median_us": 193.5, "p99_us": 216.1, "n": 600}}, "mps": {"resume": {"median_us": 2575.8, "p99_us": 3061.0, "n": 600}, "restart": {"median_us": 6165.0, "p99_us": 7524.1, "n": 600}, "one_step": {"median_us": 1808.2, "p99_us": 2263.1, "n": 600}}, "exact_planner_full_restart_us": 2.21, "planning_steps": {"resume": 1, "restart": 3}, "peak_rss_mb": 356.8, "parameters": 194313}}
{"f_iit_s3": {"cpu_1_thread": {"resume": {"median_us": 213.4, "p99_us": 372.0, "n": 600}, "restart": {"median_us": 600.8, "p99_us": 953.6, "n": 600}, "one_step": {"median_us": 196.2, "p99_us": 323.2, "n": 600}}, "mps": {"resume": {"median_us": 3738.2, "p99_us": 4862.1, "n": 600}, "restart": {"median_us": 9164.1, "p99_us": 11064.5, "n": 600}, "one_step": {"median_us": 2700.8, "p99_us": 3461.2, "n": 600}}, "exact_planner_full_restart_us": 2.29, "planning_steps": {"resume": 1, "restart": 3}, "peak_rss_mb": 356.9, "parameters": 194313}}
```

### K. Budget

| Run | Parameters | Gradient steps | Episodes | Phase 2 from step | Wall seconds (8 runs in parallel, 1 thread each) | Supervision |
|---|---|---|---|---|---|---|
| f_iit_s1 | 194,313 | 10,150 | 10,393,600 | 4150 | 1650.5 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_iit_s2 | 194,313 | 11,528 | 11,804,672 | 5528 | 1748.5 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_iit_s3 | 194,313 | 10,272 | 10,518,528 | 4272 | 1665.8 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_iit_s4 | 194,313 | 10,311 | 10,558,464 | 4311 | 1663.4 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_iit_s5 | 194,313 | 10,187 | 10,431,488 | 4187 | 1621.9 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_vq_s1 | 194,313 | 10,150 | 10,393,600 | 4150 | 1322.9 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_vq_s2 | 194,313 | 11,528 | 11,804,672 | 5528 | 1469.1 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_vq_s3 | 194,313 | 10,272 | 10,518,528 | 4272 | 1331.0 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_cont_s1 | 194,313 | 10,150 | 10,393,600 | 4150 | 1285.9 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_cont_s2 | 194,313 | 11,528 | 11,804,672 | 5528 | 1456.7 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_cont_s3 | 194,313 | 10,272 | 10,518,528 | 4272 | 1300.2 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_contiit_s1 | 194,313 | 10,150 | 10,393,600 | 4150 | 1721.5 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_contiit_s2 | 194,313 | 11,528 | 11,804,672 | 5528 | 1887.6 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_contiit_s3 | 194,313 | 10,272 | 10,518,528 | 4272 | 1734.9 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_cont_s1_posthoc | 194,313 | 10,150 | 10,393,600 | 4150 | 1285.9 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_cont_s2_posthoc | 194,313 | 11,528 | 11,804,672 | 5528 | 1456.7 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_cont_s3_posthoc | 194,313 | 10,272 | 10,518,528 | 4272 | 1300.2 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_contiit_s1_posthoc | 194,313 | 10,150 | 10,393,600 | 4150 | 1721.5 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_contiit_s2_posthoc | 194,313 | 11,528 | 11,804,672 | 5528 | 1887.6 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_contiit_s3_posthoc | 194,313 | 10,272 | 10,518,528 | 4272 | 1734.9 | set-valued valid actions from the exact planner at 4 action stages per episode; plus interchange training with counterfactual labels from the exact planner |
| f_static_s1 | 194,313 | 8,464 | 8,667,136 | 2464 | 1121.6 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_static_s2 | 194,313 | 8,327 | 8,526,848 | 2327 | 1103.4 | set-valued valid actions from the exact planner at 4 action stages per episode |
| f_hidden_s1 | 194,313 | 11,612 | 11,890,688 | 5612 | 1426.2 | set-valued valid actions from the exact planner at 4 action stages per episode; plus irrelevant head: INIT decoration bits |
| f_hidden_s2 | 194,313 | 11,492 | 11,767,808 | 5492 | 1402.5 | set-valued valid actions from the exact planner at 4 action stages per episode; plus irrelevant head: INIT decoration bits |
| f_iithidden_s1 | 194,313 | 11,612 | 11,890,688 | 5612 | 1569.4 | set-valued valid actions from the exact planner at 4 action stages per episode; plus irrelevant head: INIT decoration bits; plus interchange training with counterfactual labels from the exact planner |
| f_hiddenw_s2 | 194,313 | 11,990 | 12,277,760 | 5990 | 1185.7 | set-valued valid actions from the exact planner at 4 action stages per episode; plus irrelevant head: INIT decoration bits |
| f_hiddenx_s1 | 194,313 | 13,500 | 13,824,000 | 9000 | 1566.2 | set-valued valid actions from the exact planner at 4 action stages per episode; plus irrelevant head: INIT decoration bits |
| f_sat_s1 | 194,313 | 8,000 | 8,192,000 | 2000 | 1016.8 | set-valued valid actions from the exact planner at 4 action stages per episode; plus effect head: per-route obligation outcome from exact rollouts |
| f_sat_s2 | 194,313 | 10,347 | 10,595,328 | 4347 | 1192.2 | set-valued valid actions from the exact planner at 4 action stages per episode; plus effect head: per-route obligation outcome from exact rollouts |
| f_flat_s1 | 154,633 | 8,225 | 8,422,400 | 2225 | 893.8 | set-valued valid actions from the exact planner at 4 action stages per episode |
