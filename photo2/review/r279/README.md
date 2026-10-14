# R279 evidence and reproduction

[Full report](../../NEIGHBORS_R279.md) · [frozen protocol](../../r279/PROTOCOL.md)

No capability is certified. Both failed controls, ambiguous proposals and physically
rejected predictions are preserved. All real-photo identities are proposals.

## Real-photo cases

[Overview](real/anchors-overview.jpg) · [method/ID/cue table](real/cases.csv) ·
[full rankings](real/test1.json) · [frozen sample](real/frozen-sample.json) ·
[coordinate types](real/coordinate-types.json.gz)

Cyan A is the anchor interior centroid; green dots show candidate native supports.
Numbers refer to the ID key below each image. Raw pixels are paired with annotation.
Appearance classes are automatic, not maker-confirmed colors. Distances are pixels.

| Case | Anchor | Appearance | Raw / annotated crop |
|---:|---|---|---|
| 1 | O0454-0743 | red | [View](real/anchor-01.jpg) |
| 2 | O3004-1691 | yellow | [View](real/anchor-02.jpg) |
| 3 | O1658-2310 | black | [View](real/anchor-03.jpg) |
| 4 | O0485-1961 | red | [View](real/anchor-04.jpg) |
| 5 | O1597-0404 | yellow | [View](real/anchor-05.jpg) |
| 6 | O2072-1294 | black | [View](real/anchor-06.jpg) |
| 7 | O2407-2180 | red | [View](real/anchor-07.jpg) |
| 8 | O2773-0964 | yellow | [View](real/anchor-08.jpg) |
| 9 | O0924-0330 | black | [View](real/anchor-09.jpg) |
| 10 | O1454-1569 | red | [View](real/anchor-10.jpg) |
| 11 | O1073-2127 | yellow | [View](real/anchor-11.jpg) |
| 12 | O1570-1100 | black | [View](real/anchor-12.jpg) |
| 13 | O0255-1355 | red | [View](real/anchor-13.jpg) |
| 14 | O1900-1733 | yellow | [View](real/anchor-14.jpg) |
| 15 | O2943-1224 | black | [View](real/anchor-15.jpg) |
| 16 | O2338-0950 | red | [View](real/anchor-16.jpg) |
| 17 | O2743-1973 | yellow | [View](real/anchor-17.jpg) |
| 18 | O0310-1749 | black | [View](real/anchor-18.jpg) |
| 19 | O1287-0191 | red | [View](real/anchor-19.jpg) |
| 20 | O2062-2238 | yellow | [View](real/anchor-20.jpg) |
| 21 | O0700-0480 | black | [View](real/anchor-21.jpg) |

## Blind geometric predictions

[Six real pairs and two-hand crops](real/pairs.json.gz). Each pair has:
`pair-NN-end-to-end-before-C.json.gz`, `...-after-C.json`, and a paired `.jpg`.
Conditional refits add `...-h±1-before-D.json.gz` and `...-after-D.json`.
Before files include parameters, generator-relative targets, visible surface pixels,
uncertainty, equal-hand budgets, non-neighbor alternatives and contact failures.
After files reference the exact before-file SHA-256; they never replace predictions.

| Real pair | Raw and opposite-hand C surfaces |
|---:|---|
| 1 | [View](real/pair-00-end-to-end.jpg) |
| 2 | [View](real/pair-01-end-to-end.jpg) |
| 3 | [View](real/pair-02-end-to-end.jpg) |
| 4 | [View](real/pair-03-end-to-end.jpg) |
| 5 | [View](real/pair-04-end-to-end.jpg) |
| 6 | [View](real/pair-05-end-to-end.jpg) |

## Synthetic examples

Examples are selected **after evaluation** for explanation, never for fitting.
Original scene photo, POV source, identity raster and evaluator-only truth are in
`synthetic-scenes/scene-NN`; observations and predictions are in `scene-NN`.

- [correct neighbor](scene-00/anchor-05.jpg): scene-00, method A, O0055-0183.
- [same-body duplicate](scene-00/anchor-01.jpg): scene-00, method A, O0061-0218.
- [wrong neighbor](scene-00/anchor-03.jpg): scene-00, method A, O0111-0156.
- [ambiguous decision](scene-00/anchor-02.jpg): scene-00, method B, O0136-0102.
- [correct image match, rejected packing](geometry-example-1.jpg): scene-00, oracle, h=-1, AB=-7.
- [incorrect image match, rejected packing](geometry-example-2.jpg): scene-00, end-to-end, h=+1, AB=-7.
- [unmatched alternative](geometry-example-3.jpg): scene-00, end-to-end, h=-1, AB=-7.

Green pixels in geometry examples are the **frozen predicted visible C surface**,
not a fitted overlay. Every shown construction fails packing. Correct image matches
are explicitly not accepted physical solutions.

## Numerical evidence

- [Synthetic summary and color/hand/light/pitch breakdowns](synthetic-summary.json)
- [Detection/missing-body accounting](detection-evaluation.json)
- [Test 1 decisions and evaluator-only identities](synthetic-test1-evaluation.json)
- [Test 2 per-hypothesis errors](synthetic-test2-evaluation.json)
- [Fourth-bead identity and held-out errors](synthetic-fourth-evaluation.json)
- [Interior localization errors and uncertainty coverage](localization-evaluation.json)
- [Visible-area sensitivity](visibility-sensitivity.json)
- [Supported versus true surface distances](surface-distance-evaluation.json)
- [Real-photo proposal accounting, no accuracy labels](real-results.json)
- [Identifiability matrices and null directions](identifiability.json.gz)
- [Packing illustration](packing-sections.png)
- [POV/Python projection comparison](synthetic-scenes/projection-check.json)
- [Freeze/native/geometry audit](audit.json), [sources](source-manifest.json), [environment](environment.json)

## Reproduction

From repository root, Python 3.12 environment with installed NumPy, SciPy, scikit-image,
Pillow, Matplotlib and POV-Ray:

```sh
.venv/bin/python -m photo2.r279.run generate
.venv/bin/python -m photo2.r279.run real
.venv/bin/python -m photo2.r279.run synthetic
# Only now open truth for evaluation:
.venv/bin/python -m photo2.r279.run evaluate
.venv/bin/python -m photo2.r279.audit
.venv/bin/python -m photo2.r279.postevaluate
.venv/bin/python -m photo2.r279.explain
.venv/bin/python -m photo2.r279.run manifest
.venv/bin/python -m unittest photo2.r279.test_r279 -v
```

The main commands deterministically regenerate the selected v2 outputs. For inspection
without writes, decompress the JSONs with Python `gzip`/`json`. Replays used `/tmp`
for duplicate outputs; full real observations and a synthetic pair's C/D files match
exactly. POV logs include machine/timing details and are not byte-replay targets.

`failed-hole-fill-control/source` preserves runnable v1 code and its protocol.
To replay that control in an isolated copy, restore that directory as `photo2/r279`
and run the same stage commands with seed 279013, keeping the control's original
output layout. Do not overwrite the selected results. The failed camera control is
the seed-279013 renderer with `look_at <0,0,0>` in place of explicit `direction -eye`;
its original `.pov` files and logs are preserved for direct POV replay. The selected
code never imports either failed control. No historical R278 fits need rerunning.
