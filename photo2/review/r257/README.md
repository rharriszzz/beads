# R257 — native surfaces and global lighting diagnostics

[Working debugger and controls](../../bead_debugger/README.md) ·
[Scientific report](../../SURFACE_LIGHTING_R257.md).

Start with **[bead 2: original versus only its modeled footprint](bead-2-clean.png)**.
The cyan boundary encloses pixels assigned to bead 2 by the frozen model. It is
not a detected photographic boundary. There are no other bead markers in this view.
[One separately labeled location per panel](bead-2-locations.png) explains the
physical center, outward surface point, visible-area centroid and predicted reflection.
The earlier many-marker image was rejected as confusing; [the answer](questions.json)
is preserved without interpreting it as a geometry judgment.

## Native crops

Each `*-raw.png` is an exact decoded original-image crop, without ICC conversion.
`*-marked.png` has the same native dimensions. `*-comparison.png` enlarges both
by an integer factor using nearest-neighbor pixels. Marks are predictions;
white photographic-reflection candidates remain distinct and unconfirmed.

| Selected bead / section | Raw | Marked comparison | Full measurements |
| --- | --- | --- | --- |
| 0 | [raw](bead-0-raw.png) | [comparison](bead-0-comparison.png) | [JSON](bead-0-detail.json) |
| 1 | [raw](bead-1-raw.png) | [comparison](bead-1-comparison.png) | [JSON](bead-1-detail.json) |
| 2 | [raw](bead-2-raw.png) | [clean comparison](bead-2-clean.png) | [JSON](bead-2-detail.json) |
| 3 | [raw](bead-3-raw.png) | [comparison](bead-3-comparison.png) | [JSON](bead-3-detail.json) |
| 4 | [raw](bead-4-raw.png) | [comparison](bead-4-comparison.png) | [JSON](bead-4-detail.json) |
| 5 | [raw](bead-5-raw.png) | [comparison](bead-5-comparison.png) | [JSON](bead-5-detail.json) |
| 6 | [raw](bead-6-raw.png) | [comparison](bead-6-comparison.png) | [JSON](bead-6-detail.json) |
| 7 | [raw](bead-7-raw.png) | [comparison](bead-7-comparison.png) | [JSON](bead-7-detail.json) |
| Straight section | [raw](straight-raw.png) | [comparison](straight-comparison.png) | [JSON](straight-detail.json) |
| Strong bend | [raw](bend-raw.png) | [comparison](bend-comparison.png) | [JSON](bend-detail.json) |

[Whole-photo section locator](sections-locator.png) ·
[Photographic reflection evidence montage](reflection-evidence.png) ·
[Straight-section shadows](straight-shadows.png) · [Bend shadows](bend-shadows.png).

## Numerical evidence

- [Centroid convergence at 4/2/1px and boundary supersampling](centroid-convergence.csv)
- [Predicted versus observed reflection positions, sizes and orientations](reflection-errors.csv)
- [Photo-derived observations, coordinates, patches, reliability and spatial split](observations.json)
- [Global configurations and conditional validation](lighting.json), [metrics](metrics.json)
- [Alternative fixed geometries, matched directional fitting rules](alternative-geometries.json)
- [Angular light quadrature sensitivity](quadrature.json)
- [Full 2×2 versus boundary-adaptive pixel sampling](supersampling.json)
- [Source hashes and artifact manifest](provenance.json)

No configuration is certified as the actual illumination. The diagnostic fit's
poor held-out localization is an explicit negative result, not recovered room
geometry. Do not derive global bead indices or a repeating template from these
highlight predictions.
