# One concrete neighbor-inference failure — R041

The maker requested a hard case marked in the context of the whole image.
The [whole-render locator and detail](output/neighbor-failure/whole-image-failure.png)
show a verified error from R039's **synthetic** shape baseline. This is not an
indexed photo-2 example or evidence that the maker cannot identify the neighbors.
The [SVG](output/neighbor-failure/whole-image-failure.svg) embeds unchanged source
PNG bytes and keeps all annotations as separate vectors.

The saved convention +1 result for repeat-40-h+1-phase-0, T12, seed 17 proposes
611 → 613 as +7. The actual difference is +2, so it is not an immediate ±1/±6/±7
neighbor pair under either convention or global reversal. Bead 612 is retained
and visible; cyan dashes illustrate 611 → 612 → 613, two actual +1 steps.
Circles mark visible-mask centroids, which may differ from physical bead centers;
the connecting lines are schematic, not traced physical thread or surface paths.
This example was selected after examining saved errors for illustration, not as
a new accuracy trial. No human ambiguity or hidden intermediate bead is assumed.

Recreate from the preserved R039 and R030/R031 outputs:

```sh
.venv/bin/python photo2/show_neighbor_failure.py
```

Requires local Python 3.12/Pillow and system librsvg/Cairo for the PNG preview.
INFERENCE.md documents recreation of the underlying ignored evidence. The script
checks the three input JSON files and beauty image against their original
artifact manifests, asserts the exact saved false edge and visible intermediate
vertex, and records source/artifact hashes and crop coordinates in report.json.
The SVG uses one embedded image for both full context and magnified detail.
Generated diagrams and reports stay ignored. Two runs reproduced both artifacts
byte for byte; the final PNG was visually inspected. No inference algorithm,
scene, segmentation, material, sequence fit or photo indexing changed.

## Maker's clarification

R041: the maker finds neighbors unambiguous except close to the edge and advises
tracing **all three directions, 1, 6 and 7**. Treat algorithmic ambiguity as a
limitation of the present inference rule, not an established property of the
photo. The maker initially described spiral turns using +1, +7, -1, -7, then
corrected this in R042: the paths form a rough rectangle and probably use plus
and minus **6 and 7**. The exact directions remain uncertain; do not encode the
earlier ±1 recollection or the corrected recollection as a known exact pattern.

Next bounded algorithm task: trace the three families jointly and check local
1+6=7 consistency, retaining the fixed baseline and its controls. Stop after
synthetic edge/component-index evidence, before photo segmentation or fitting.
Stay in this conversation with gpt-6-astra / High for the maker's review of this
specific example; no further /new is needed now.
