# v0.6 round 2: where things are

Freeze commit: `6cc1613b192e89e03eaffafe5cce2cd207cb3c95` (branch `v0.7`). The second hidden family is run once at this commit.

| Path | What |
|---|---|
| `docs/v06r2_spec.md` | The three-level bank, the frozen rules M1 to M5, the development record, what I expect |
| `docs/v06r2_codex_family_brief.md` | What the second hidden family should contain and what stays sealed |
| `v06/family2.py`, `v06/report2.py` | Harness and report (frozen) |
| `results/v06r2/` | Development runs on the three spent families, every design kept |

Check that nothing changed since the freeze: `git diff 6cc1613 -- v06/family2.py v06/report2.py docs/v06r2_spec.md` prints nothing.
