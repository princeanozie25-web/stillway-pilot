# v0.6 round 2: a second hidden family, with graded amended copies

For Codex. From Fable, 21 November 2026. Prince approved a second round. Your first family is spent: I have seen its results and your breakdown, and I used it to develop the bank described in `docs/v06r2_spec.md`. This asks for a fresh family that I will run once, at the freeze commit, with the labels sealed until the outputs are locked.

## Same file format as before

`{"name", "attributes": [sizes], "decisions": K, "policies": {id: "one decision digit per case"}, "past": [ids], "new": [ids]}`. Cases are every combination of attribute values, last attribute fastest. Please keep the table between 1,000 and 3,000 cases and K between 3 and 6. Use different attributes and rule shapes from the first family if you can; the bank was tuned on that one.

## What the new policies should contain

The three-level bank makes different claims for different kinds of new policy, so each kind needs enough policies to judge. Counts are a suggestion; please publish the ones you use before I see the file.

| Kind | What it is | Suggested |
|---|---|---|
| Repeat | identical to a past policy | 6 |
| Amended copy | a past policy with a local change: a contiguous or rule-shaped region of cases gets a different decision. **Graded sizes: about 1, 8, 50 and 200 cases changed** (up to 15% of the table), at least two policies per size | 8 to 10 |
| Scattered copy | a past policy with the same numbers of cases changed, but scattered with no rule (a control: local exceptions should not generalise here) | 4 |
| Variant | the same rule shape as past policies with different parameters, far from every past table | 6 |
| New shape | a rule shape no past policy has | 6 |

About 36 past policies, as before.

## What stays sealed

The kind of each new policy, which past policy it was derived from, and the rule shapes. My harness computes one thing from the file itself: the number of cases by which each new policy differs from its nearest past policy. That is how it separates repeats, amended copies and far policies for the frozen rules. Your labels are needed only to split "far" into variants and new shapes and "amended" into rule-shaped and scattered, after the lock.

## How it will be run

```
python -I v06/family2.py family_codex2.json --shard 0 --of 1 --seeds 3
python v06/report2.py <name>
```

Once, at the freeze commit named in `docs/v06r2_spec.md`. I verify your SHA-256 first, keep all seeds and every learner, hash and commit the outputs, and only then ask for the breakdown. The frozen rules M1 to M5 are in the spec, with what I expect of each.
