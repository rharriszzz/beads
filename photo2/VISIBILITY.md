# Known repeat-slot visibility in the legacy scene — R023

The original 40-bead practice repeat exposes every slot many times in each
tested view. The 13-bead repeat has much less even support: one slot is visible
only through small gaps in its second phase. This is an illustrated check of
known indices in `beads.pov`, not an inverse reconstruction of photo 2.

## Reproduce

```sh
# Prerequisite if the R017 outputs are absent:
.venv/bin/python photo2/practice_legacy.py
.venv/bin/python photo2/legacy_visibility.py --output photo2/output/legacy-visibility-verified
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

Without `--output`, the new script writes `photo2/output/legacy-visibility/`.
It verifies all source and artifact hashes in the existing practice report
before reusing its two 2400x1800 beauty images. The 13-color source is
`visibility-pattern-13.json`; its two beauty images include the original
`beads.pov` with only the existing color/group override. Both color sequences
are invented and unrelated to the photographed pattern.

The final run uses 26 POV-Ray renders: four full ID passes, four original-palette
passes, sixteen isolated bodies and two 13-repeat beauty views. Each uses two
threads. Commands, logs, exported geometry, all original indices, missing-index
lists, per-bead pixel counts, per-slot support at three thresholds, selected
visibility fractions and SHA-256 hashes are in `report.json`. The report records
Python 3.12.14, NumPy 2.5.3 and Pillow 12.3.0; renderer logs identify
POV-Ray 3.7.0.10.unofficial. Sources and generated outputs remain separate.

## Geometry and closure

| Invented repeat | Groups | Beads | Turns | Beads/turn | Phase advance per repeat | Total closure adjustment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 40 colors (R017) | 20 | 800 | 123 | 6.504065041 | 54 degrees | -27.692307692 degrees |
| 13 colors | 60 | 780 | 120 | 6.5 | 0 degrees | 0 degrees |

The original scene computes every bead's placement and hole orientation. Python
derives repeat advance as `360 * turns / groups` modulo 360 and closure correction
as `360 * (turns - bead_count/6.5)`. The case-1 body has roundedness 0.8,
height/diameter 0.7, relative size 1 and hole-radius/body-radius ratio 0.14.
The unchanged perspective camera is at `<50,-600,500>`, looks at the origin,
and has angle 10 degrees. Its view direction relative to the rope changes around
the ring even when repeat occurrences have identical cross-section phase.

Clocks 0 and 0.0625 stay in case 1. As in R017, the second changes both row phase
by nearly 180 degrees and position around the central circle by nearly 30 degrees.
These are separate observations, not two photographs available for the real task.

## Instrumentation and validation

`legacy_visibility.py` makes an ignored, generated copy of `beads.pov`; the
tracked scene and shared bead macro are unchanged. Exact replacement anchors
and case-1 shape checks reject unexpected source changes. The copy removes
lights/ground and uses a black background, gamma 1, emission-only materials,
no antialiasing, no jitter and no dithering. `legacy-visibility-body.inc` assigns
RGB bytes of `bead_index + 1`; code 0 is background. It instantiates the same
shared bead shape and applies the original loop's transforms. Source IDs and
positions are exported directly from that loop.

An independent pass through the original palette bodies, with emission-only
red/green/blue materials, has an exactly equal foreground mask and exactly the
expected color for every visible ID/slot. This holds for all four full renders.
The selected isolated-body checks include a completely occluded bead, a tiny
sliver, a large visible body and the strongest occurrence of slot 0 in each view.
Every visible mask is a subset of its isolated body at the identical raster.
All four full masks have clear image borders. The ground cannot cut these beads:
their minimum center height is twice the body radius, above the ground plane.

These checks validate instrumentation. The original beauty images keep their
lighting, ground, materials and antialiasing. Appearance is not replaced with ID
colors for measurement, and no shaded-image segmentation is claimed.

## Results

All indices and slots below are **zero-based**. An occurrence counts at threshold
T only if that bead has at least T visible pixels. Thresholds 1, 12 and 100 are
sensitivity checks at this raster size, not calibrated color-readability limits.

| Repeat / phase | Beads with >=1 pixel | Beads with >=12 pixels | Slots with >=12 pixels somewhere | Slots with >=100 pixels somewhere |
| --- | ---: | ---: | ---: | ---: |
| 40 / phase 0 | 566 / 800 | 547 / 800 | 40 / 40 | 40 / 40 |
| 40 / phase half | 574 / 800 | 550 / 800 | 40 / 40 | 40 / 40 |
| 13 / phase 0 | 563 / 780 | 538 / 780 | 13 / 13 | 13 / 13 |
| 13 / phase half | 551 / 780 | 532 / 780 | 13 / 13 | 12 / 13 |

For the 40-color pattern, every slot has 12–16 occurrences with at least 12
visible pixels in either individual view; every slot also has at least ten
occurrences exceeding the 100-pixel threshold. Even each separate quarter-ring
has all 40 slots represented at the 12-pixel threshold.

For the 13-color pattern, slot 0 changes from 60 supported occurrences in phase
0 to only four in phase half at the 12-pixel threshold. Those four are bead
indices 520, 533, 546 and 559 with 29, 69, 35 and 14 pixels respectively. Five
additional occurrences have only 1–3 pixels; 51 have none. The strongest, #533,
exposes 69 of its 4,094 isolated-body pixels: **1.6854%**. No occurrence reaches
100 pixels. Keep that slot unsupported when applying the 100-pixel threshold;
do not fill it from the known source pattern in an inference task.

Quarter-ring measurements group bead centers by chain angle, not rectangular
image crops. At the 12-pixel threshold the 13-color phase-0 arcs 0–90 and 90–180
degrees each miss slots 4, 10 and 11; the 180–270 arc misses slot 3. In phase half,
the first two arcs each miss slots 0, 1 and 7. Full-ring coverage improves because
other sections expose them. The report also retains the 1- and 100-pixel arc
results and explicitly labels the union of two phases as using two observations.

This tested 13-repeat ring does **not** have a completely hidden slot across the
whole oblique view at the 1-pixel threshold. It demonstrates phase locking,
local missing slots and weak whole-ring support. It neither disproves the user's
possible hidden-side counterexample nor certifies complete recovery in another
view, geometry, raster or real photograph.

## Illustrations and checks

After reproduction, open these local generated artifacts:

- [Coverage chart](output/legacy-visibility-verified/coverage.png): rows are repeat
  occurrences, columns are slots; white is a zero-pixel observation.
- [40-repeat trace](output/legacy-visibility-verified/repeat-40-phase-0-trace.png):
  highlights known visible occurrences of slot 0, preserving original bead IDs.
- [13-repeat weak-slot trace](output/legacy-visibility-verified/repeat-13-phase-half-trace.png)
  and [close-up](output/legacy-visibility-verified/repeat-13-phase-half-detail.png):
  show the small gap exposing #533. The close-up preserves original pixels at 3x
  nearest-neighbor enlargement and compares beauty with an ID-based highlight.

All four full trace views, the coverage chart and the weak-slot close-up were
visually inspected. Initial weak-slot labels overlapped; moving those labels to
the lower margin fixed this in the final run. The first and final runs agree on
all original coverage/count/centroid results, all four geometry CSV files and
all 22 common renderer image pixel arrays. Figure formatting and four additional
isolated checks were added in the final run. PNG bytes may change with embedded
timestamps; actual file hashes are retained rather than claiming byte equality.

Seventeen tests pass, including four new checks for missing-slot indexing, RGB
ID byte boundaries, source-change rejection and actual original-palette/ID
render agreement. Compilation and whitespace checks pass. All seven recorded
source hashes and all 74 generated artifact hashes match disk. Final report:
`12ac2b92948e920b89e7da5a49ae1ecfdfcfb44c102d4c07e53606344489c7c0`.
Legacy source and photo settings did not change; R017's existing artifact/source
hashes were verified, so its before/after beauty regression was not rerun.
Legacy beauty gamma/version warnings remain; mask rendering uses explicit gamma.

No bead order, helicity, period or materials were recovered from photo 2. No
observation noise, resolution sweep or automatic beauty-image reading was tested.
The accepted working estimate remains 2,698 beads. Next: review established
registration and periodic-sequence methods in primary sources, choose an approach
compatible with missing bead slots and whole repeats, and specify its synthetic
validation. Stop at that method choice and test plan before implementation or
photo refitting.
