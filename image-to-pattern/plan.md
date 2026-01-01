Project goal: Build a Python tool that takes an input image and produces a `bead_pattern` payload compatible with the `beads.pov` case statement (essentially reversing the beads.pov rendering path). Use `beads1.jpg`-`beads7.jpg` as round-trip fixtures and `beads-photo-1.jpg`-`beads-photo-11.jpg` as the target photos.

High-level plan
- Understand target format: read `beads.pov` to document the bead grid dimensions, coordinate ordering, palette, and the exact `bead_pattern` representation expected in the case statement.
- Establish palette and sizing: infer bead size/layout from `beads1.jpg`-`beads7.jpg` (and any constants in `beads.pov`) to know how to rescale/crop/quantize incoming images onto the bead grid.
- Build conversion pipeline: Python script that loads an image, normalizes orientation/cropping, resizes to the bead grid, quantizes to the bead palette, and emits a structured `bead_pattern` (plus a ready-to-paste case clause).
- Validate against fixtures: run the pipeline on `beads1.jpg`-`beads7.jpg` and compare against the known patterns from `beads.pov` to verify correctness of ordering and palette mapping.
- Apply to target photos: process `beads-photo-1.jpg`-`beads-photo-11.jpg`, review outputs visually/numerically, and iterate on heuristics (palette thresholds, alignment) as needed.
- Document usage: add a README/usage section in this folder explaining CLI options, dependencies (e.g., Pillow), and how to drop generated patterns into `beads.pov`.

Notes from `beads.pov`
- There are 8 `bead_pattern` cases; each defines `color_pattern` (ints), `pattern_rows_per_group` (all but case 3), `beads_per_row` (always 6.5), and `ngroups`. Derived values: `pattern_length = len(color_pattern)`, `nbeads = ngroups * pattern_length`, `nrows = floor(0.5 + nbeads / beads_per_row)`, `exact_beads_per_row = nbeads / nrows`.
- Palette per case is defined in a second `#switch`; `color_pattern` indexes into the case-local `beads` array. Case summaries: 1 (3 colors, 4x6 pattern, 28 groups), 2 (4 colors, 5x7 pattern, 20 groups), 3 (3 colors, auto-built 372 length = (50+12)*3*2, 2 groups), 4 (5 colors, 6x7 pattern, 18 groups), 5 (6 colors, 6x7 pattern with trailing 7th row fragment, 18 groups), 6 (4 colors, 6x14 pattern, 9 groups), 7 (3 colors, 4x6 pattern, 28 groups), 8 (5 colors, 5x6 pattern, 24 groups). Need to decode how the 6.5 beads/row translates to alternating 6/7 rows when unwrapping.
- `bead_index` increments linearly; rendered position uses `chain_angle` (bead_index / nbeads) and `row_angle` (bead_index / exact_beads_per_row), implying a helical ordering. Reverse mapping likely requires simulating bead_index → (row, col) to align image pixels to the 1D `color_pattern` order.

Observations from fixtures
- `beads1.jpg`: 800x600; dominant colors are white with strong red/green/blue accents (matches case 1 palette), so it is a good alignment/palette sanity check.
- `beads-photo-2.jpg`: 2540x3182 (portrait); dominant purples/pinks with some darker reds, so expect quantization toward a purple/skin-tone palette and need to crop/resize before mapping to the bead grid.

Ordered processing steps (covers the requested tasks)
- Separate bracelet vs background: build a mask (color thresholding + morphology) to keep only bracelet pixels.
- Trace bracelet centerline: extract the bracelet band from the mask and fit a spline through its medial axis.
- Estimate bead spacing and radius: measure band width along the spline to set bead diameter and sampling interval.
- Establish bracelet coordinates: define an arc-length parameter along the spline and a radial offset axis; decide origin and axis orientation to express bead centers.
- Determine helicity: analyze how rows wrap around the spline (clockwise/counterclockwise) using shading cues or cross-section ordering to match `bead_index` winding.
- Sample visible bead centers: march along arc length at bead spacing and place bead centers on the band using the helicity/radial offset; this yields bead positions in the image frame.
- Identify bead colors: for each sampled bead region, extract dominant color (clustering or median) to classify into palette candidates; note uncertain/occluded beads.
- Map to `bead_index`: unwrap sampled beads into 1D order that matches the POV helical ordering (simulate chain_angle/row_angle to choose row/column ordering and alternating 6/7 rows).
- Infer invisible beads: fill missing beads along the chain by interpolating along the arc-length grid.
- Autocorrelate along `bead_index`: run autocorrelation on the color index sequence to infer pattern length and then the repeating `color_pattern`.
- Emit POV-ready output: format `color_pattern`, derived `pattern_rows_per_group`, `ngroups`, and palette mapping into a ready-to-paste `#case` block.

Testing plan and checkpoints
- Geometry/mapping unit tests: given known `color_pattern`/palette from `beads.pov`, simulate forward render ordering and ensure the reverse mapping reproduces bead_index sequences and alternating 6/7 row layout.
- Fixture round-trips: run the pipeline on `beads1.jpg`-`beads7.jpg` and assert recovered `color_pattern` matches the source case (tolerating color classification noise thresholds).
- Segmentation sanity: verify bracelet masks cover expected area (e.g., mask area within [x%, y%] of bounding box) and centerline continuity.
- Color quantization tests: feed synthetic bead crops of each palette color and ensure classifier labels them correctly; add a confusion matrix check against fixture crops.
- Autocorrelation robustness: test periodicity detection on synthetic sequences with noise/occlusion to ensure the detected pattern length remains stable.
