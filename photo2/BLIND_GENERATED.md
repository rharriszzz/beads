# Blind test of the seven existing generated JPEGs — R059

**No complete pattern was recovered from any of the seven images.** This is an
actual failure of the present detector/indexer, not evidence that the patterns
cannot be read from these images. No complete visible-bead inventory is yet
verified. The user explicitly puts these generated images before photographs,
and visible-bead identification before algorithms to infer the remaining beads.
The second-anchor experiment and pending pattern-advice questions are superseded.

Inputs are **beads1.jpg–beads7.jpg**, each 800×600. The executable pipeline reads
only these JPEGs and its own observation records. It does not read `beads.pov`,
stored pattern fixtures, ID passes, source layouts or previous audit results.
The seven palettes and classification boxes are assistant choices based on
viewing these JPEGs; they are not unsupervised palette estimates. Historical
construction knowledge (neighbor differences ±1/±6/±7) is retained. This is not
a fresh-agent experiment that erases all knowledge of prior work.

## Results

| Image | Brightness candidates | Flagged fragments/edge candidates | Unflagged candidates | Conflicting directed edges across four indexing attempts | Recovered repeat |
| --- | ---: | ---: | ---: | ---: | --- |
| beads1.jpg | 352 | 28 | 324 | 44–96 | unresolved |
| beads2.jpg | 392 | 60 | 332 | 28–50 | unresolved |
| beads3.jpg | 435 | 217 | 218 | 30–38 | unresolved |
| beads4.jpg | 410 | 68 | 342 | 66–118 | unresolved |
| beads5.jpg | 403 | 83 | 320 | 50–66 | unresolved |
| beads6.jpg | 354 | 70 | 284 | 54–80 | unresolved |
| beads7.jpg | 417 | 90 | 327 | 60 | unresolved |

These are **candidate counts, not visible-bead counts, precision or recall**.
Unflagged does not mean correct. Direct visual review of all seven original
images and all seven boundary overlays shows many separated front-facing beads,
but boundaries crossing bead bodies on the sides, omitted edge/sliver evidence,
and black/glint fragments. Gray/white classification and separation are also
unverified. Changing peak spacing 5→6 pixels lowers counts to respectively
328, 373, 379, 389, 386, 326 and 392. Raising contrast .025→.04 gives
340, 372, 413, 393, 394, 340 and 403. There is no validated completeness threshold.

The four index attempts use brightness markers versus candidate-region centroids,
each with both diagonal conventions. All fail full-graph consistency and have
duplicate index assignments. One angular seam is cut before propagation; no
unknown full-ring count is silently used as a modulus. Observations retain
anonymous IDs, candidate masks, bounding boxes, sample colors/unknowns and no
accepted chain index. Disconnected component offsets remain unknown.

Only beads3 has internally consistent components with at least twelve candidates:
marker variants have 14- and 12-candidate groups; centroid variants have a
17-candidate group. Their compatible local periods are retained in JSON, including
unsupported slots and competing lengths. Internal consistency and local color
compatibility do not establish correct neighbors or a complete image pattern.
The other images have no qualifying consistent local group. The program does
not scan a fabricated sequence built from inconsistent graph labels.

## Method and failed approaches

1. Threshold the minimum RGB channel below 190, close by four pixels, keep the
   largest connected annular component, and fill only enclosed holes below 300
   pixels. This assumes one bracelet on a light background. It can include
   shadows and omit tiny disconnected visible slivers.
2. Find local maxima of Gaussian-smoothed HSV value (sigma 1.25), minimum
   separation five pixels, value ≥.22 and contrast over sigma-four smoothing
   >.025. Peaks are highlight observations, not calibrated body centers.
3. Seed a compact watershed of negative smoothed value plus .3 times the RGB
   gradient; compactness .002. Record every candidate, including small regions
   and markers within two pixels of the uncertain silhouette. Sample nearby
   non-highlight/colorful pixels with explicit per-image palette boxes.
4. Apply existing image-only reciprocal neighbor-sector proposals to unflagged
   candidates, preserve both conventions, cut the annulus once, propagate exact
   signed differences and report conflicts and duplicates. Test strong periods
   only inside internally consistent groups of at least twelve candidates,
   preserving missing integer positions and arbitrary palette names.

The initial gradient-only watershed trapped many seeds inside their glints and
allowed other regions to spread across several beads. The final value/gradient
compact watershed improves the visual map but does not validate its boundaries.
This was development using the seven JPEGs, not a frozen holdout experiment.
No renderer truth was used to choose parameters.

Exploratory local sinusoidal and projected-torus fits to the detected glints also
failed visual alignment/reliable indexing. Important failure modes were omitted
ellipse rotation, local projection distortion, glint/body-center displacement,
and competing global count/phase fits. No such fit is an accepted observation,
sequence, total count or next default algorithm. Scratch scripts/results remain
local in `/tmp/beads_*explore.py`, `/tmp/beads_local_torus.py`,
`/tmp/beads_global_rot.py`, `/tmp/beads_global_refine.py` and
`output/blind-jpegs-r059-dev/`; the reported table uses only the reproducible
image/graph pipeline below. Do not restart source-calibrated fitting instead of
correcting the visible observations.

## Reproduce and inspect

```sh
.venv/bin/python photo2/blind_generated.py --output photo2/output/blind-generated-new
.venv/bin/python photo2/blind_generated_index.py \
  --observations photo2/output/blind-generated-new \
  --output photo2/output/blind-generated-new-index
.venv/bin/python -m unittest discover -s photo2 -p 'test_blind_generated.py' -v
.venv/bin/python -m unittest discover -s photo2 -p 'test_infer_neighbors.py' -v
.venv/bin/python -m unittest discover -s photo2 -p 'test_neighbor_graph.py' -v
```

Final observation directory: `output/blind-generated-r059-final/`.
Open **index.html** for all seven original images with hoverable candidate IDs,
colors and flags. IDs can be toggled. Each image also has a numbered PNG, a
boundary PNG, observation JSON and integer candidate-label NPY. All remain
ignored, as do the environment and exploratory outputs.

Observation report SHA-256:
`be59c090dbdb013ee4f14a2803622db2626e03fa4c9029f7efcc6b05c01ecba8`.
Index report: `output/blind-generated-r059-final-index/report.json`, SHA-256
`6fd94616bf6d53e22754160ca52e133fe2927afc8d6c16dd96027e174ca357e6`.

Nineteen relevant tests pass: five new image/period/contradiction controls,
seven existing neighbor-inference tests and seven propagation tests. The first
contradiction-control fixture accidentally placed its contradictory edge across
the intentional seam cut; corrected its coordinates and reran all nineteen.
Compilation passes. Two final runs produce identical 29 observation artifacts
and seven index artifacts; reports match after removing command paths. All seven
JPEG hashes, source hashes, observation-input bindings and artifact hashes verify.
No full prior rendering suite: existing sources and POV-Ray scenes are unchanged.
No new rendering, photo processing, hidden-bead completion or pattern-source check.

## Next task

Correct and review the visible-bead inventory on **beads1.jpg** from the JPEG
alone. Preserve full-image context and explicitly mark edge/sliver uncertainty,
missed beads, duplicates and merged regions. Save a reviewable instance map and
colors before attempting another index/repeat algorithm, then extend that
inventory work to beads2–7. Stop the next bounded step after the first image's
reviewed inventory and checks; do not claim the seven-pattern task complete.
Recommend gpt-6-astra / High, staying in the current conversation if convenient;
no additional pattern questions are needed.
