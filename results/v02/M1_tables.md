# M1 report: the certificate with all 36 operator-message patterns

Wrong / checked. A pair is one reachable saved state shown one observation. Per family; all 100 Dispatch-2 families.

| Seed | v0.1 list (20 patterns), plain memory | v0.1 list, original maps | 36 patterns, plain memory | 36 patterns, original maps unchanged | 36 patterns, maps rebuilt |
|---|---|---|---|---|---|
| 1 | 30,010 / 98,176,640 (0.0306%) | 3,882 / 7,864,320 (0.0494%) | 8,173,197 / 528,416,640 (1.5467%) | 3,782,430 / 277,218,432 (1.3644%) | 3,193,175 / 56,040,192 (5.6980%) |
| 4 | 3 / 174,345,600 (0.0000%) | 0 / 7,864,320 (0.0000%) | 813,477 / 529,845,120 (0.1535%) | 414,171 / 183,220,992 (0.2260%) | 78,193 / 17,720,064 (0.4413%) |

Original maps applied to the 36-pattern run, in detail:

| Seed | SHA-256 of the original maps | Reproduces archived v0.1 counts | Transitions onto a state the map does not know | Distinct unknown states | Wrong from an unknown state | Wrong from a known representative | Families with a wrong pair: plain / original maps / rebuilt maps |
|---|---|---|---|---|---|---|---|
| 1 | `06fcb534659806c0…` | True | 25,457,002 / 217,596,672 (11.6992%) | 98,251 | 2,968,601 | 813,829 | 95 / 95 / 79 |
| 4 | `24856aba6cd5c1cf…` | True | 12,782,671 / 175,045,248 (7.3025%) | 90,203 | 332,222 | 81,949 | 51 / 44 / 28 |

Same histories, three memories (2,000,000 sampled jobs per seed; every stage drawn uniformly from the 36-pattern alphabet of the family):

| Seed | Jobs with a wrong decision: plain | original maps | rebuilt maps | Original maps: repaired / broken / tie-break only | Rebuilt maps: repaired / broken / tie-break only |
|---|---|---|---|---|---|
| 4 | 98 | 106 | 505 | 3 / 11 / 42,162 | 10 / 417 / 51,098 |

Archived maps: `results/v02/maps20/<run>/maps20.json` (original) and `results/v02/expanded/<run>/maps36.json` (rebuilt). Full hashes:

- seed 1: original `06fcb534659806c07688c37032d16cf4b661d1aeae7c9b38ba4a90d6093e2a7e`, rebuilt `6cdd69a653df1091f4b38a32f2f23367a0e40a23a46a7e6234907cef6cec9f50`; CPU-seconds: recover 1,534, expanded 14,017
- seed 4: original `24856aba6cd5c1cfb747aa395254e76dfa2037c9ba4e033184e31b5bc5d01c13`, rebuilt `b3de5307e9e210e620e058fb4ee2d14f784677e081a5333a7ba3dd605f45f7fa`; CPU-seconds: recover 2,236, expanded 11,765
