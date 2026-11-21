# For Codex: author a hidden family of related policies

Prince asked for this on 21 November 2026. The point: I (Fable) have only tested "a bank learns a new policy faster after seeing related ones" on policies I wrote and on public ones I chose. You write a family I have never seen. I run frozen code on it once.

## What to produce

One JSON file, `family_codex.json`:

```json
{"name": "codex_hidden",
 "attributes": [4, 3, 5, 2],
 "decisions": 4,
 "policies": {"p001": "0312...", "p002": "..."},
 "past": ["p001", "p002", "..."],
 "new":  ["p101", "..."]}
```

- `attributes`: how many values each attribute has. A **case** is one combination of attribute values. Cases are ordered with the last attribute changing fastest (attribute 0 slowest), so with `[4, 3, 5, 2]` there are 120 cases and case number `((a0 * 3 + a1) * 5 + a2) * 2 + a3`.
- `policies`: for each policy ID, one character per case, the decision digit `0` to `decisions - 1`.
- `past`: policies the bank has already learned (given to my code in full). `new`: policies it must learn from audits. My code asks your table for the decision of a case, a few at a time.

## Constraints

| | |
|---|---|
| Cases | between 200 and 5,000 (product of the attribute sizes) |
| Attributes | 3 to 7, each with 2 to 10 values |
| Decisions | 2 to 9 |
| Past policies | at least 30 |
| New policies | at least 15 distinct ones |

## What makes it a useful test

- The policies should be **related**: variations on a few rule shapes, the way one company's approval rules differ by region or customer. That is the claim under test.
- Mix the new policies. Some identical to a past one. Some the same shape with different constants or thresholds. Some of a shape no past policy has. Tell Prince the mix afterwards, not me.
- Include what would break my learners if you can think of it: rules that need three or more attributes at once, counting or arithmetic conditions, exceptions that hit a handful of cases, attributes that never matter.
- Deterministic. No noise in the first version. A noisy second file is welcome.
- Do not derive it from anything in this repository, and do not tell me the rules.

## How it will be run

```
python -I v06/family.py family_codex.json --shard 0 --of 1 --seeds 3
python v06/report.py codex_hidden
```

The code and the pass rules are frozen at the commit named in `results/v06/REPORT_v06.md`. Check that hash before you send the file, and check afterwards that `v06/family.py` still has it. The five rules in `docs/v06_spec.md` are applied as written. I will not tune anything after seeing your file; if something breaks I will report it as broken.

## If you would rather keep the tables too

Keep the `new` tables and send only `past`. Then run the two commands yourself with the full file; the output JSON and `results/v06/codex_hidden_tables.md` are all I need.
