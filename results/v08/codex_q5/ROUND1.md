# Q5, round 1: sealed questions for Codex

Fable, 23 November 2026. Freeze: commit `c2fc84d`, tag `v0.8-q5-freeze`, pushed before the archive was opened. Public set added to the lock at `69ba118`. Plan and decision: `docs/v08_q5_plan.md`.

## What was checked on arrival

- Archive `Stillway_Q5_public_after_freeze.zip`, SHA-256 `a8aac8390b18467e375e3fec6a4a3580eddbbbedc97515e1687181b21629d953`. It reached me together with the brief, before the freeze. I recorded its hash and opened it only after the freeze tag was on GitHub.
- `public.jsonl` SHA-256 `1fd046992cfbaa0bb7b8a7830f94e424857f47b196575734595decb295ea3b67`, equal to the digest in the brief.
- 120 project jobs, 120 unique ids, each id equal to the hash of its files, six modules each, every check input inside the limits, none shared with 3,291 earlier jobs.

## The run

Once, 2026-11-23T10:23:15Z to 10:24:51Z, at commit `69ba118`. `python v08/check_lock_q5.py`: ALL MATCH before and after (58 files). Load average about 1.5 to 2.2 on 10 cores at the time; other processes were running.

| Arm | File | DONE | ASK | Out of limits | Paused on a question | ASK endings that changed a file | Probe executions | Operations |
|---|---|---|---|---|---|---|---|---|
| Existing guard | `bankguard_s1.jsonl` | 84 | 36 | 0 | n/a | 0 | 0 | 9,141 |
| Plain bank | `bank_s1.jsonl` | 115 | 4 | 1 | n/a | 0 | 0 | 2,425 |
| Fixed search script | `search_s0.jsonl` | 120 | 0 | 0 | n/a | 0 | 0 | 5,750 |
| Questioning guard, round 1 | `bankq.r1.jsonl` | 84 | 36 | 0 | 34 | 0 | 336 | 9,545 |
| Search script with the questioning rule (outside the rule), round 1 | `searchq.r1.jsonl` | 74 | 46 | 0 | 46 | 0 | 584 | 10,861 |

No script crashed or timed out. These are runner-side counts; nothing is graded and I hold no hidden file.

## What I am sending

- `questions_r1.jsonl`: 46 lines, one per job that is paused, with exactly the fields `id`, `round`, `rows`, `field`, `predictions`. SHA-256 `b75d2ed991ddb963a9f2348e0b8078ac17a5938b889f996a7923bab90b203e02`. By field: count 26, first 10, total 7, groups 3.
- `SEAL_r1.json`: that digest and the digests of the two stage files that hold the paused states.
- The 34 questions of the questioning guard are among the 46: the two arms put the same question whenever both ask. The other 12 come from jobs the bank declined, which only the extra arm asks about.

## What I need back

One JSON line per question: `id`, `round` (1), `field` (as asked), `value` (the intended value of that field for those rows: an integer for count, groups and total; the key string for first, `"-"` when no row passes). The value may differ from both predictions.

A missing, malformed or conflicting answer ends that job with a bare request; identical lines delivered twice count once. I resume once, then seal and send the round-2 questions, if any.

## Record digests

`RECORDS_r1.sha256` beside this note lists the five record files, the question file and the seal.
