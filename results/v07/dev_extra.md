# v0.7 development: extra tables

## The bank's effect, seed by seed (first-patch successes on the 48 repositories that are not repeats)

| Seed | A unchanged | F bank disabled | D bank | W wrong diagnostic | E nearest example | D minus F | D better / worse than F |
|---|---|---|---|---|---|---|---|
| 1 | 12 | 14 | 13 | 11 | 16 | -1 | 2 / 3 |
| 2 | 12 | 12 | 13 | 14 | 11 | +1 | 2 / 1 |
| 3 | 12 | 13 | 19 | 15 | 12 | +6 | 9 / 3 |

## Which diagnostic the bank handed over (arm D, all seeds)

A repository's own symptom is S1, S2 or S3 where it shares a trained symptom; absent mechanisms (G4) have none, so any diagnostic is the wrong one there.

| Group | Episodes | Diagnostic matches the repository's symptom | First patch correct when it matches | First patch correct when it does not |
|---|---|---|---|---|
| G1 | 72 | 72 of 72 | 90% (65 of 72) | none |
| G2 | 48 | 48 of 48 | 73% (35 of 48) | none |
| G3 | 48 | 39 of 48 | 3% (1 of 39) | 22% (2 of 9) |
| G4 | 48 | 0 of 48 | none | 15% (7 of 48) |

## Lookalikes (G3): what the student did after its prediction was contradicted

| Arm | Episodes | Contradicted | Submitted the trained fix anyway (fails exactly as the trained fix does) | of those, after a contradiction | Broke a hidden test | Correct |
|---|---|---|---|---|---|---|
| A unchanged | 16 | 16 | 4 | 4 | 0 | 4 |
| B final patches | 48 | 48 | 9 | 9 | 8 | 4 |
| C experience | 48 | 48 | 18 | 18 | 34 | 3 |
| F bank disabled | 48 | 46 | 19 | 18 | 29 | 4 |
| D bank | 48 | 47 | 28 | 28 | 37 | 3 |
| D1 bank, version 1 only | 48 | 46 | 24 | 24 | 34 | 5 |
| W wrong diagnostic | 48 | 48 | 18 | 18 | 27 | 3 |
| E nearest example | 48 | 42 | 14 | 13 | 31 | 3 |

## Witnesses: repositories the unchanged student fixes and trained students mostly do not

### dev_000 (G3, look_split_window): unchanged student correct; trained runs correct in 3 of 21

Unchanged student's patch:
```
-    return window[:half], window[size:]
+    return window[:half], window[half:]
```
D (bank, seed 1): diagnostic handed over S1; stated cause: 'The islice window is a one-shot iterator walked twice. The feed never ends, so turn only the islice window into a list.'; hidden failures: ['test_first_half', 'test_odd_size', 'test_second_half']; broke: ['test_first_half']
```
-    window = [x.goals for x in itertools.islice(feed, size)]
+    window = list(itertools.islice(feed, size))
```
B (final patches, seed 1): hidden failures: ['test_odd_size', 'test_second_half']; broke: []
```
-    window = [x.goals for x in itertools.islice(feed, size)]
+    window = [x.goals for x in list(itertools.islice(feed, size))]
```

### dev_003 (G4, int_division): unchanged student correct; trained runs correct in 0 of 21

Unchanged student's patch:
```
-    return part // total * 100
+    return part / total * 100
```
D (bank, seed 1): diagnostic handed over S1; stated cause: 'The loop bound stops one short. Extend it by one.'; hidden failures: ['test_percent', 'test_percentages_add_up']; broke: []
```

```
B (final patches, seed 1): hidden failures: ['test_percent', 'test_percentages_add_up']; broke: []
```
+    fixtures = list(fixtures)
```

### dev_034 (G4, int_division): unchanged student correct; trained runs correct in 1 of 21

Unchanged student's patch:
```
-    return part // total * 100
+    return part / total * 100
```
D (bank, seed 1): diagnostic handed over S1; stated cause: 'The loop bound stops one short. Extend it by one.'; hidden failures: ['test_everything', 'test_percent', 'test_percentages_add_up', 'test_unknown_key']; broke: ['test_everything', 'test_unknown_key']
```
-    return part // total * 100
+    return part // total * 100 + 1
```
B (final patches, seed 1): hidden failures: ['test_percent', 'test_percentages_add_up']; broke: []
```
+    harvests = list(harvests)
```

### dev_038 (G3, look_split_window): unchanged student correct; trained runs correct in 2 of 21

Unchanged student's patch:
```
-    return window[:half], window[size:]
+    return window[:half], window[half:]
```
D (bank, seed 1): diagnostic handed over S1; stated cause: 'The islice window is a one-shot iterator walked twice. The feed never ends, so turn only the islice window into a list.'; hidden failures: ['test_first_half', 'test_odd_size', 'test_second_half']; broke: ['test_first_half']
```
-    window = [x.kilos for x in itertools.islice(feed, size)]
+    window = list(itertools.islice(feed, size))
```
B (final patches, seed 1): hidden failures: ['test_odd_size', 'test_second_half']; broke: []
```
-    window = [x.kilos for x in itertools.islice(feed, size)]
+    window = [x.kilos for x in list(itertools.islice(feed, size))]
```

### dev_043 (G4, int_division): unchanged student correct; trained runs correct in 0 of 21

Unchanged student's patch:
```
-    return part // total * 100
+    return part / total * 100
```
D (bank, seed 1): diagnostic handed over S1; stated cause: 'The loop bound stops one short. Extend it by one.'; hidden failures: ['test_everything', 'test_percent', 'test_percentages_add_up', 'test_unknown_key']; broke: ['test_everything', 'test_unknown_key']
```
-    return part // total * 100
+    return part // total * 100 + 1
```
B (final patches, seed 1): hidden failures: ['test_percent', 'test_percentages_add_up']; broke: []
```
+    donations = list(donations)
```

### dev_050 (G4, int_division): unchanged student correct; trained runs correct in 1 of 21

Unchanged student's patch:
```
-    return part // total * 100
+    return part / total * 100
```
D (bank, seed 1): diagnostic handed over S1; stated cause: 'The loop bound stops one short. Extend it by one.'; hidden failures: ['test_everything', 'test_percent', 'test_percentages_add_up', 'test_unknown_key']; broke: ['test_everything', 'test_unknown_key']
```
-    return part // total * 100
+    return part // total * 100 + 1
```
B (final patches, seed 1): hidden failures: ['test_percent', 'test_percentages_add_up']; broke: []
```
+    bookings = list(bookings)
```

### dev_052 (G3, look_split_window): unchanged student correct; trained runs correct in 2 of 21

Unchanged student's patch:
```
-    return window[:half], window[size:]
+    return window[:half], window[half:]
```
D (bank, seed 1): diagnostic handed over S1; stated cause: 'The islice window is a one-shot iterator walked twice. The feed never ends, so turn only the islice window into a list.'; hidden failures: ['test_first_half', 'test_odd_size', 'test_second_half']; broke: ['test_first_half']
```
-    window = [x.nights for x in itertools.islice(feed, size)]
+    window = list(itertools.islice(feed, size))
```
B (final patches, seed 1): hidden failures: ['test_odd_size', 'test_second_half']; broke: []
```
-    window = [x.nights for x in itertools.islice(feed, size)]
+    window = [x.nights for x in list(itertools.islice(feed, size))]
```

