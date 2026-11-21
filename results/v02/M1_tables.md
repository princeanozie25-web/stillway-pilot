# M1 report: the certificate with all 36 operator-message patterns

Wrong / checked. A pair is one reachable saved state shown one observation. Per family; all 100 Dispatch-2 families.

| Seed | v0.1 list (20 patterns), plain memory | v0.1 list, original maps | 36 patterns, plain memory | 36 patterns, original maps unchanged | 36 patterns, maps rebuilt |
|---|---|---|---|---|---|
| 1 | 30,010 / 98,176,640 (0.0306%) | 3,882 / 7,864,320 (0.0494%) | 8,173,197 / 528,416,640 (1.5467%) | 3,782,430 / 277,218,432 (1.3644%) | 3,193,175 / 56,040,192 (5.6980%) |
| 2 | 151 / 126,197,760 (0.0001%) | 4 / 7,864,320 (0.0001%) | 14,376,901 / 791,168,256 (1.8172%) | 7,025,676 / 417,898,368 (1.6812%) | 2,237,852 / 75,208,320 (2.9755%) |
| 3 | 21 / 72,407,040 (0.0000%) | 3 / 7,864,320 (0.0000%) | 4,365,307 / 309,550,464 (1.4102%) | 3,003,894 / 172,505,088 (1.7413%) | 39,314 / 34,019,712 (0.1156%) |
| 4 | 3 / 174,345,600 (0.0000%) | 0 / 7,864,320 (0.0000%) | 813,477 / 529,845,120 (0.1535%) | 414,171 / 183,220,992 (0.2260%) | 78,193 / 17,720,064 (0.4413%) |
| 5 | 24,077 / 133,248,000 (0.0181%) | 3,122 / 7,864,320 (0.0397%) | 4,089,114 / 707,908,608 (0.5776%) | 2,666,993 / 421,348,608 (0.6330%) | 5,640 / 32,245,632 (0.0175%) |

Original maps applied to the 36-pattern run, in detail:

| Seed | SHA-256 of the original maps | Reproduces archived v0.1 counts | Transitions onto a state the map does not know | Distinct unknown states | Wrong from an unknown state | Wrong from a known representative | Families with a wrong pair: plain / original maps / rebuilt maps |
|---|---|---|---|---|---|---|---|
| 1 | `06fcb534659806c0…` | True | 25,457,002 / 217,596,672 (11.6992%) | 98,251 | 2,968,601 | 813,829 | 95 / 95 / 79 |
| 2 | `056a4bffe2db639e…` | True | 32,472,422 / 326,848,896 (9.9350%) | 160,532 | 5,979,904 | 1,045,772 | 100 / 100 / 100 |
| 3 | `acf226a5131dfc16…` | True | 21,398,225 / 149,553,792 (14.3080%) | 85,463 | 2,707,428 | 296,466 | 72 / 72 / 15 |
| 4 | `24856aba6cd5c1cf…` | True | 12,782,671 / 175,045,248 (7.3025%) | 90,203 | 332,222 | 81,949 | 51 / 44 / 28 |
| 5 | `8d527c076d351ede…` | True | 47,556,406 / 360,432,000 (13.1943%) | 167,872 | 2,366,494 | 300,499 | 72 / 72 / 5 |

Same histories, three memories (2,000,000 sampled jobs per seed; every stage drawn uniformly from the 36-pattern alphabet of the family):

| Seed | Jobs with a wrong decision: plain | original maps | rebuilt maps | Original maps: repaired / broken / tie-break only | Rebuilt maps: repaired / broken / tie-break only |
|---|---|---|---|---|---|
| 1 | 6,786 | 6,794 | 8,434 | 2 / 10 / 19,204 | 560 / 2,208 / 18,676 |
| 2 | 8,040 | 8,044 | 8,459 | 418 / 422 / 29,001 | 615 / 1,034 / 31,117 |
| 3 | 434 | 654 | 97 | 2 / 222 / 33,569 | 354 / 17 / 35,915 |
| 4 | 98 | 106 | 505 | 3 / 11 / 42,162 | 10 / 417 / 51,098 |
| 5 | 6,265 | 6,125 | 2,685 | 258 / 118 / 31,143 | 3,698 / 118 / 42,168 |

Archived maps: `results/v02/maps20/<run>/maps20.json` (original) and `results/v02/expanded/<run>/maps36.json` (rebuilt). Full hashes:

- seed 1: original `06fcb534659806c07688c37032d16cf4b661d1aeae7c9b38ba4a90d6093e2a7e`, rebuilt `6cdd69a653df1091f4b38a32f2f23367a0e40a23a46a7e6234907cef6cec9f50`; CPU-seconds: recover 1,534, expanded 14,017
- seed 2: original `056a4bffe2db639e7617b307d8312d334ebad225ca1098eec2e8dafa86552802`, rebuilt `9354d4a100493bb1919d7a44ce6bb9c2ef2c82d0b0971c229da923a49494b509`; CPU-seconds: recover 1,732, expanded 26,647
- seed 3: original `acf226a5131dfc1631ffd6408a9e28b298e0179274be83567e8872669a84feca`, rebuilt `6219a9ccabcc679eec23f323ecd252bd003b3f6b639e03efd21440fd728f4757`; CPU-seconds: recover 1,344, expanded 7,290
- seed 4: original `24856aba6cd5c1cfb747aa395254e76dfa2037c9ba4e033184e31b5bc5d01c13`, rebuilt `b3de5307e9e210e620e058fb4ee2d14f784677e081a5333a7ba3dd605f45f7fa`; CPU-seconds: recover 2,236, expanded 11,765
- seed 5: original `8d527c076d351ede68360cc69aca186cc1155cff36f06732a3c8580e4e1b9750`, rebuilt `b05d101220f7be54b65d6f13774404043c2a852601bfb9d20e2e90ee2a33dd4f`; CPU-seconds: recover 1,607, expanded 12,601
