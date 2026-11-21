### A. Ordinary accuracy and the paired replay (dev fixtures; mean over seeds, range in brackets; %)

| Arm | Seeds | Plain | Dynamic | Mid-plan reversal pairs | Targeted swap | Shuffled | Improvement | Unrelated drop | Slots |
|---|---|---|---|---|---|---|---|---|---|
| Discrete + interchange training | 5 | 99.9 (99.7–100.0) | 99.8 (99.0–100.0) | 99.1 (95.7–100.0) | 100.0 (100.0–100.0) | 49.9 (49.9–49.9) | 50.1 (50.1–50.1) | 0.0 (0.0–0.0) | [0]; [0]; [0]; [0]; [0] |
| Discrete, plain imitation | 3 | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 40.0 (38.9–41.8) | 27.7 (21.9–31.0) | 12.3 (7.9–17.5) | 30.3 (0.0–55.4) | [2, 3]; [1]; [1, 3] |
| Continuous, plain imitation | 3 | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 36.9 (29.2–45.1) | 23.7 (20.5–26.6) | 13.2 (8.8–18.5) | 51.7 (43.0–65.6) | [2, 3]; [1, 2]; [0, 1] |
| Continuous + interchange training | 3 | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 49.9 (49.9–49.9) | 50.1 (50.1–50.1) | 0.0 (0.0–0.0) | [0]; [0]; [0] |
| Continuous, quantised after training | 3 | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 36.7 (26.9–44.6) | 23.5 (19.5–25.6) | 13.2 (7.4–19.0) | 52.0 (45.9–63.4) | [2, 3]; [0, 1]; [0, 1] |
| Continuous + interchange, quantised after | 3 | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 49.9 (49.9–49.9) | 50.1 (50.1–50.1) | 0.0 (0.0–0.0) | [0]; [0]; [0, 3] |
| Discrete, world never changes in training | 2 | 96.8 (96.7–97.0) | 85.0 (83.3–86.7) | 25.0 (15.7–34.3) | 13.0 (7.4–18.6) | 17.8 (16.2–19.2) | -4.8 (-11.9–2.4) | 49.4 (48.2–50.5) | [2, 3]; [0, 3] |
| Discrete + planted hidden channel | 2 | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 31.6 (31.0–32.1) | 18.6 (17.0–20.2) | 12.9 (11.9–14.0) | 43.6 (35.4–51.7) | [2, 3]; [0, 1] |
| Discrete + interchange + planted channel | 1 | 100.0 | 100.0 | 100.0 | 100.0 | 49.9 | 50.1 | 0.0 | [0] |
| Discrete + planted channel (strong weight) | 1 | 100.0 | 99.7 | 99.7 | 58.1 | 43.8 | 14.4 | 6.2 | [3] |
| Discrete + planted channel (earlier recipe: ordinary training profile only) | 1 | 100.0 | 100.0 | 100.0 | 44.4 | 24.2 | 20.1 | 16.5 | [0, 2] |
| Discrete + effect head | 2 | 98.2 (96.7–99.7) | 98.5 (97.3–99.7) | 94.7 (90.7–98.7) | 33.8 (33.0–34.6) | 22.3 (22.1–22.5) | 11.5 (10.9–12.1) | 51.5 (51.0–52.0) | [0, 2]; [0, 3] |
| Discrete, flat reader | 1 | 88.0 | 89.3 | 64.3 | 33.1 | 22.2 | 10.9 | 51.1 | [0, 1] |

### B. Per-seed primary endpoint with 95% intervals (families resampled; %)

| Run | Targeted | Shuffled | Improvement [95% CI] | Unrelated drop [95% CI] | Both unmodified runs valid | Resume twice identical |
|---|---|---|---|---|---|---|
| f_iit_s1 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_iit_s2 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_iit_s3 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_iit_s4 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_iit_s5 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_vq_s1 | 38.9 | 31.0 | +7.9 [+3.3, +13.6] | 35.5 [32.3, 39.8] | 100.0 | 100.0 |
| f_vq_s2 | 41.8 | 30.1 | +11.6 [+7.1, +15.9] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_vq_s3 | 39.4 | 21.9 | +17.5 [+13.1, +21.0] | 55.4 [51.4, 59.6] | 100.0 | 100.0 |
| f_cont_s1 | 45.1 | 26.6 | +18.5 [+14.2, +23.1] | 43.0 [38.9, 46.4] | 100.0 | 100.0 |
| f_cont_s2 | 29.2 | 20.5 | +8.8 [+5.5, +12.6] | 65.6 [61.7, 69.3] | 100.0 | 100.0 |
| f_cont_s3 | 36.4 | 24.0 | +12.4 [+9.4, +15.7] | 46.5 [44.4, 48.3] | 100.0 | 100.0 |
| f_contiit_s1 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_contiit_s2 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_contiit_s3 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_cont_s1_posthoc | 44.6 | 25.6 | +19.0 [+15.2, +22.6] | 45.9 [41.4, 49.6] | 100.0 | 100.0 |
| f_cont_s2_posthoc | 26.9 | 19.5 | +7.4 [+4.0, +11.9] | 63.4 [59.1, 67.0] | 100.0 | 100.0 |
| f_cont_s3_posthoc | 38.6 | 25.5 | +13.1 [+9.9, +16.4] | 46.6 [45.6, 47.9] | 100.0 | 100.0 |
| f_contiit_s1_posthoc | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_contiit_s2_posthoc | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_contiit_s3_posthoc | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_static_s1 | 18.6 | 16.2 | +2.4 [-8.7, +11.0] | 48.2 [44.6, 51.7] | 93.5 | 100.0 |
| f_static_s2 | 7.4 | 19.2 | -11.9 [-16.9, -3.5] | 50.5 [46.3, 53.6] | 82.2 | 100.0 |
| f_hidden_s1 | 31.0 | 17.0 | +14.0 [+10.1, +17.3] | 35.4 [33.8, 37.3] | 100.0 | 100.0 |
| f_hidden_s2 | 32.1 | 20.2 | +11.9 [+8.9, +16.1] | 51.7 [47.1, 55.4] | 100.0 | 100.0 |
| f_iithidden_s1 | 100.0 | 49.9 | +50.1 [+46.8, +53.3] | 0.0 [0.0, 0.0] | 100.0 | 100.0 |
| f_hiddenw_s2 | 58.1 | 43.8 | +14.4 [+8.6, +19.3] | 6.2 [4.9, 7.5] | 96.2 | 100.0 |
| f_hiddenx_s1 | 44.4 | 24.2 | +20.1 [+16.7, +23.5] | 16.5 [13.1, 19.7] | 100.0 | 100.0 |
| f_sat_s1 | 34.6 | 22.5 | +12.1 [+6.7, +17.5] | 51.0 [46.9, 55.7] | 100.0 | 100.0 |
| f_sat_s2 | 33.0 | 22.1 | +10.9 [+8.7, +14.4] | 52.0 [46.4, 56.0] | 100.0 | 100.0 |
| f_flat_s1 | 33.1 | 22.2 | +10.9 [+4.7, +16.9] | 51.1 [47.2, 55.0] | 93.8 | 100.0 |

### C. Replay controls (mean over seeds; %)

| Arm | Whole-state transplant: gate follows donor | Same-goal donor: stable | Blank memory: gate right | Message revision | Slots changed by a gate message | Restart from full order | Repaint: same actions | Slots changed by repaint |
|---|---|---|---|---|---|---|---|---|
| Discrete + interchange training | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 49.5 (49.0–49.9) | 100.0 (100.0–100.0) | 3.9 (3.8–3.9) | 100.0 (100.0–100.0) | 95.5 (94.9–96.4) | 0.1 (0.0–0.2) |
| Discrete, plain imitation | 100.0 (100.0–100.0) | 56.3 (42.5–72.1) | 50.4 (50.0–50.7) | 100.0 (100.0–100.0) | 3.9 (3.8–4.0) | 100.0 (100.0–100.0) | 96.9 (95.6–97.6) | 0.3 (0.1–0.5) |
| Continuous, plain imitation | 100.0 (100.0–100.0) | 50.2 (41.8–64.8) | 49.9 (49.1–50.6) | 100.0 (100.0–100.0) | 4.0 (4.0–4.0) | 100.0 (100.0–100.0) | 94.9 (93.5–96.4) | 4.0 (4.0–4.0) |
| Continuous + interchange training | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 50.9 (50.0–52.8) | 100.0 (100.0–100.0) | 4.0 (4.0–4.0) | 100.0 (100.0–100.0) | 94.4 (90.4–96.5) | 4.0 (4.0–4.0) |
| Continuous, quantised after training | 100.0 (100.0–100.0) | 54.7 (43.6–66.6) | 49.1 (48.2–49.8) | 99.9 (99.8–100.0) | 4.0 (4.0–4.0) | 100.0 (100.0–100.0) | 94.8 (93.1–96.8) | 0.1 (0.0–0.1) |
| Continuous + interchange, quantised after | 100.0 (100.0–100.0) | 100.0 (100.0–100.0) | 50.7 (50.0–51.7) | 100.0 (100.0–100.0) | 4.0 (3.9–4.0) | 100.0 (100.0–100.0) | 94.3 (89.9–97.4) | 0.1 (0.0–0.1) |
| Discrete, world never changes in training | 38.2 (19.9–56.5) | 44.2 (42.1–46.2) | 47.9 (45.6–50.2) | 95.8 (94.2–97.4) | 3.8 (3.7–4.0) | 94.4 (94.2–94.5) | 95.8 (95.1–96.5) | 0.3 (0.1–0.4) |
| Discrete + planted hidden channel | 100.0 (100.0–100.0) | 53.1 (36.9–69.4) | 50.1 (50.0–50.1) | 100.0 (100.0–100.0) | 4.0 (4.0–4.0) | 100.0 (100.0–100.0) | 93.2 (89.1–97.2) | 0.7 (0.7–0.8) |
| Discrete + interchange + planted channel | 100.0 | 100.0 | 50.2 | 100.0 | 4.0 | 100.0 | 95.0 | 0.1 |
| Discrete + planted channel (strong weight) | 98.9 | 68.9 | 50.7 | 99.8 | 3.1 | 100.0 | 97.5 | 0.4 |
| Discrete + planted channel (earlier recipe: ordinary training profile only) | 100.0 | 83.8 | 50.1 | 100.0 | 4.0 | 100.0 | 96.1 | 0.1 |
| Discrete + effect head | 100.0 (100.0–100.0) | 39.1 (39.0–39.1) | 48.9 (47.9–50.0) | 98.9 (97.9–100.0) | 4.0 (3.9–4.0) | 99.8 (99.5–100.0) | 98.7 (98.5–98.9) | 0.1 (0.1–0.1) |
| Discrete, flat reader | 97.8 | 55.4 | 51.4 | 94.8 | 4.0 | 95.0 | 97.4 | 0.9 |

### D. Exhaustive check: every reachable state against every observation, per family

| Run | Families | Pairs checked | Wrong | Wrong % | Families with a wrong pair | Code states per family (after INIT … BAY) | Meanings |
|---|---|---|---|---|---|---|---|

### E. Typed patch, quotient memory, corruption alarm (%)

| Run | Typed patch credit | Patch undefined | Plain: dynamic / mid-plan | Spec quotient: dynamic / mid-plan | Behaviour quotient: dynamic / mid-plan | One slot corrupted: harmful | Harmful caught by dictionary | Missed |
|---|---|---|---|---|---|---|---|---|

### H. Continuous memory: swap along one direction

```json
{"f_cont_s1": {"mean_difference": {"n": 800, "targeted": 0.96625, "shuffled": 0.545, "improvement": 0.42125, "ci95": [0.3947351723216671, 0.45518207282913165]}, "discriminant": {"n": 800, "targeted": 1.0, "shuffled": 0.48875, "improvement": 0.51125, "ci95": [0.48471499855812805, 0.5445312721700388]}}}
{"f_cont_s2": {"mean_difference": {"n": 800, "targeted": 0.3125, "shuffled": 0.22, "improvement": 0.0925, "ci95": [0.059457141838408334, 0.12446640944495023]}, "discriminant": {"n": 800, "targeted": 0.565, "shuffled": 0.2725, "improvement": 0.2925, "ci95": [0.2574004700821133, 0.32841483543759203]}}}
{"f_cont_s3": {"mean_difference": {"n": 800, "targeted": 0.35375, "shuffled": 0.33, "improvement": 0.02375, "ci95": [-0.02083838996763754, 0.07159890791607294]}, "discriminant": {"n": 800, "targeted": 0.81875, "shuffled": 0.3875, "improvement": 0.43125, "ci95": [0.40118577075098816, 0.46659101234919315]}}}
{"f_contiit_s1": {"mean_difference": {"n": 800, "targeted": 1.0, "shuffled": 0.55, "improvement": 0.45, "ci95": [0.4315938601579582, 0.4752965421206701]}, "discriminant": {"n": 800, "targeted": 1.0, "shuffled": 0.48875, "improvement": 0.51125, "ci95": [0.48471499855812805, 0.5445312721700388]}}}
{"f_contiit_s2": {"mean_difference": {"n": 800, "targeted": 1.0, "shuffled": 0.55, "improvement": 0.45, "ci95": [0.4315938601579582, 0.4752965421206701]}, "discriminant": {"n": 800, "targeted": 1.0, "shuffled": 0.48875, "improvement": 0.51125, "ci95": [0.48471499855812805, 0.5445312721700388]}}}
{"f_contiit_s3": {"mean_difference": {"n": 800, "targeted": 1.0, "shuffled": 0.55, "improvement": 0.45, "ci95": [0.4315938601579582, 0.4752965421206701]}, "discriminant": {"n": 800, "targeted": 1.0, "shuffled": 0.48875, "improvement": 0.51125, "ci95": [0.48471499855812805, 0.5445312721700388]}}}
```

### I. Bits the code carries about the gate

```json
{"f_iit_s1": {"instructed": true, "stages": {"INIT": {"bits_about_gate": 0.013, "bits_about_decor_bit": 0.01, "distinct_code_states": 26}, "PLAN": {"bits_about_gate": 0.039, "bits_about_decor_bit": 0.047, "distinct_code_states": 114}, "LEG1": {"bits_about_gate": 0.038, "bits_about_decor_bit": 0.018, "distinct_code_states": 129}, "DOCK": {"bits_about_gate": 0.034, "bits_about_decor_bit": 0.015, "distinct_code_states": 111}, "LEG2": {"bits_about_gate": 0.035, "bits_about_decor_bit": 0.012, "distinct_code_states": 129}, "BAY": {"bits_about_gate": 0.162, "bits_about_decor_bit": 0.017, "distinct_code_states": 176}}, "all_valid": 0.9999499917030334}}
{"f_vq_s1": {"instructed": true, "stages": {"INIT": {"bits_about_gate": 0.04, "bits_about_decor_bit": 0.04, "distinct_code_states": 60}, "PLAN": {"bits_about_gate": 0.029, "bits_about_decor_bit": 0.047, "distinct_code_states": 171}, "LEG1": {"bits_about_gate": 0.033, "bits_about_decor_bit": 0.022, "distinct_code_states": 199}, "DOCK": {"bits_about_gate": 0.047, "bits_about_decor_bit": 0.024, "distinct_code_states": 167}, "LEG2": {"bits_about_gate": 0.043, "bits_about_decor_bit": 0.027, "distinct_code_states": 177}, "BAY": {"bits_about_gate": 0.18, "bits_about_decor_bit": 0.071, "distinct_code_states": 209}}, "all_valid": 1.0}}
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
