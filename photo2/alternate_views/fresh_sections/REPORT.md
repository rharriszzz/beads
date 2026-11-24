# A prediction test on eight fresh sections of the bracelet

The existing 208-position chart correctly predicted **87 of 87 readable bead colors** in eight previously untraced sections of the wood and white-plastic photos. One further bead was too unclear to score. The starting alignment was unique in all eight windows, and there were no contrary readings. [Site-by-site results with native pixel coordinates](results.csv)

| Photograph | Sections | Beads used to locate paths | Bridge beads | Correct predictions | Contrary | Ambiguous alignment | Unreadable |
|---|---:|---:|---:|---:|---:|---:|---:|
| Wood | 4 | 67 | 4 | 44 | 0 | 0 | 0 |
| White plastic | 4 | 63 | 4 | 43 | 0 | 0 | 1 |

## What was predicted

The windows start halfway between the previous quarter-start windows. I inspected only the first 300 strip columns of each new window to trace its starting path. The signed neighbor directions came from the earlier work on these photographs. Each of the 208 possible starting positions was tested against the readable starting colors. Before opening the endings, I committed a forecast table covering every possible combination of inward and outward steps for the next 12 beads. This let the chart predict a color conditional on the traced geometry while the ending colors were still hidden. [Protocol](PROTOCOL.md) · [Prefix-only commit](https://github.com/rharriszzz/beads/commit/0e8b65dd) · [Frozen forecasts](forecast.csv)

I then traced the endings with the forecast hidden, recorded the glass colors, and compared them against the table. The first continuation bead in every window fell inside the 20-pixel guard or earlier and served as a bridge. The 88 scored centers all lay beyond the guard. The readable endings comprised 39 red, 31 yellow and 17 black beads. The unclear bead in the plastic photo at native (2550, 1408) remains unknown; its predicted color was black. One analyst made the readings and had previously seen the full-loop overviews. This tests new paths with a prospective forecast. An independent reader could still check bead identity and adjacency. [Wood paths](wood-paths.jpg) · [White-plastic paths](plastic-paths.jpg) · [Recorded ending readings](suffix.csv)

## What the extra sections establish

- **Coverage rose from 125 to 171 of the 208 chart positions in the two alternate views.** Of the 46 newly covered positions, 25 appeared among the predicted endings, 25 among the starting paths and two among the bridges. These groups overlap. The remaining 37 positions still lack a readable check from these two views. These are distinct chart positions; repeated photographs of a physical bead can contribute the same position. [Coverage lists and per-window totals](summary.json)
- **Position 75 has a second readable black appearance on wood.** The earlier observation was beside the first-quarter path. This one is on the one-eighth path at site 5. As a sensitivity check, I omitted every black starting observation and treated the seven historically sparse chart positions as unknown. Red and yellow alone still gave exactly the same unique alignment for each window. The plastic one-eighth path supplies a black reading at position 82, where an earlier plastic crop was unclear. The new windows also reached sparse positions 43, 147 and 186. Position 140 still has just the earlier wood reading in these views. The physical repeat-copy assignments remain unresolved. [Earlier sparse-position evidence](../REPORT.md) · [New coordinates and readings](results.csv)
- **Two fresh plastic paths show red and yellow endpoints 104 string steps apart** under the established crochet rule. In the five-eighths window, sites 5 and 21 run from yellow to red. In the seven-eighths window, sites 12 and 28 run from red to yellow. Each path has eight inward and eight outward steps, so the difference is 8 × 6 + 8 × 7 under either assignment of the two directions. This check depends on the observed local links and colors and can be inspected without knowing a starting chart position. [Plastic paths](plastic-paths.jpg) · [All six differently colored endpoint pairs](summary.json)

## Replay

From the repository root, run the following commands. The first regenerates the prefix-only predictions. The scorer verifies the forecast SHA-256 against the pre-reveal version before reading any ending.

```sh
.venv/bin/python -m photo2.alternate_views.fresh_sections.forecast
.venv/bin/python -m photo2.alternate_views.fresh_sections.score
```
