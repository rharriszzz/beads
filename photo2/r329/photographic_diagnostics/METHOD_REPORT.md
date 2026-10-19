# R329 supplement: same-diagonal colored-material diagnostics

This is a new diagnostic experiment and a correction to the illustrated explanation. It does not replace the R328/R329 graphs or frozen models. See the [illustrated lesson](README.md) for what is actually visible. The original photo, historical observations, search results, reflection measurements and physical-model code are preserved.

## Findings and limits

| Case | Direct new comparison | Result | Interpretation |
|---|---|---|---|
| E, closest winding | Held-out yellow region reached using separate colored-row displacement fields | Working 0.55–9.08 px; closest alternative 24.43–32.60 px | Local mixed-family failure of the closest alternative; not certification of the full working graph |
| F, frozen N3000 | Colored pigment versus actual predicted visible glass bodies | Index 26: 39.4% covered; index 38: 20.2% | Visible mismatch conditional on correspondence; no black-light positioning inference |
| G, early departure | Same colored target and reference rows for both candidates | Working 18.68–21.16 px; alternative 8.66–10.71 px | Local transfer favors alternative, but family uncertain and curvature-sensitive; retain both |
| H, lower bend | Same colored target and reference rows; inventory comparison | Working 11.08–12.57 px; alternative 15.53–17.19 px; alternative omits visible C-1144-2947 | Weak geometric preference plus a real completeness problem; no demonstrated skipped physical bead |

All distances are native photograph pixels. Ranges span extraction settings, local averaging widths and admissible step orders. They are sensitivity ranges, not confidence intervals or independent repeated experiments.

**Correction:** historical support ownership near relative index 31 did not establish the first physical placement error. The frozen model already disagrees with colored material at reference index zero. We withdraw that physical-first-error interpretation rather than move it to another unproven location. Historical numerical ownership measurements remain unchanged.

## Three separate evidence layers

1. **Photograph:** pigment pixels and their spatial relationships, extracted independently of model positions. Historical colored observation locations seed region association only. A pigment centroid is not a whole-body center. Black observations are excluded from all new positional measurements.
2. **Lattice hypothesis:** proposed sequence membership, step counts and integer coordinates. Reference chains were selected from visible nearby colored rows in shared portions of the saved candidates, then inspected on the photograph. This is explicit diagnostic supervision, not a newly validated fully automatic row detector. Agreement between candidates does not independently certify those reference chains. Dashed two-step gaps remain conditional.
3. **Physical prediction:** frozen N3000 R321 glass-body positions, shapes and camera, with all bodies retained for visibility. No new registration, light fit or photographic relabeling enters the geometry export.

The tests have no black-center truth labels. They cannot establish an exact black position from a few reference intervals. Broad blue slot boxes make that limitation visible.

## Measure the diagonal before comparing it

`continuity.py` lists every reference row, its family and each proposed step count. `explore.py:measure` extracts a connected red or yellow component from original RGB around the associated colored observation. It uses color-specific ratios and a radius of 16, 18 or 20 pixels. Ratio thresholds vary by factors .95, 1 and 1.05. Components smaller than 30 pixels are unavailable; none of the selected measurements fails. Components are partial pigment regions, not complete contours. Every selected native pixel is serialized in `continuity.json.gz`.

For each reference interval, the measured displacement divided by the conditional step count gives a local vector. Cyan and green vectors are **never pooled**. Each family's vector field is a Gaussian-weighted average of that family's nearby measurements, with locality widths 35, 55 and 85 pixels. Both magnitude and direction can vary geographically. There is no imposed orthogonality, fixed straight-row angle or equal projected spacing between families.

To classify the colored bridge across a disputed gap, compare its undirected angle separately with each local family's estimated angle. A family is eligible if the bridge falls within that family's observed reference angular spread. Classification succeeds only if the same **single** family is eligible in all 27 extraction/locality variants. This empirical envelope is not statistically calibrated; reference selection and curvature can limit it.

- **E:** green in all 27 variants. Baseline bridge angle 12.18°; green 6.97° (5.21° departure, reference spread 19.89°); cyan 74.26° (62.08° departure, spread 21.56°).
- **G and H:** no robust unique family. No rejection follows from this diagnostic there.
- **F:** the colored bridge classifies green, but classification does not prove black identity or body placement.

For candidate predictions, integrate its integer steps through the corresponding family fields, with midpoint updates. Preserve both orders when a route mixes families. The E/G/H colored target is excluded from reference intervals, so the displayed miss is not a residual at a fitted endpoint. F uses direct material coverage and a reverse-cyan slot estimate; its displayed colored observations are not advertised as withheld prediction targets.

Leave-one-interval-out controls measure transfer error within each family. Blue slot boxes enclose extraction/locality/step-order predictions and expand by the maximum observed control error per step for the families traversed. These are development controls, not blind validation. Pigment asymmetry, partial occlusion, two-step gap assumptions and bends remain sources of error. We do not penalize candidates based on a black highlight's distance from a predicted slot.

Initial whole-row affine/quadratic experiments are retained in `exploration.json.gz`. Their preferences changed with curvature modeling, including at E and G. They are not discarded evidence or reported as confirming the final test. The final same-family test addresses the user's specific counterexample more directly, but needs broader validation before general deployment.

## Why E survived the original search

Exact parent hypotheses and connected patches are copied in `candidate-provenance.json.gz`. Parent sources are R327's bank; connected patches and search states are frozen R328 exports. Window numbers below identify overlapping computational crops, not beads or independent observations.

| Window | Working hypothesis / patch | Assignments | Score | Closest hypothesis / patch | Assignments | Score |
|---|---|---:|---:|---|---:|---:|
| 124 | 6 / 10 | 13 | 13.611708 | 39 / 29 | 11 | 10.155695 |
| 125 | 0 / 1 | 15 | 15.925882 | 21 / 6 | 14 | 14.123574 |
| 126 | 2 / 13 | 14 | 15.705853 | 0 / 0 | 19 | 19.605442 |

The working window-124 hypothesis came from bidirectional neighboring-candidate reuse, source window 125. The alternative came from changed-context transported fit `122-320-0`, source hypothesis 5. At 125 the working candidate is local/native; the alternative came from `126-240-18`, source hypothesis 0. Those transported candidates supplied internally consistent local equations, not independent colored-row validation.

The alternative loses about 5.258 points over 124–125 and gains about 3.900 at 126; the final score deficit is only **1.358732**. All six connected patches have **zero shared primitive-shape penalty**. Thus the existing shortest-direction check failed to detect this cross-row problem.

The historical score combines per-support utility (geometry/native response), run reward and discovery reward, less shape penalties. Geometry uses predicted historical support locations; black support tolerance is broader. Native brightness is evidence of photographed material, not proof of bead-body position. Positive rewards and overlapping contexts reuse observations. The 19-versus-14 support advantage is therefore not five independent confirmations. This audit explains how the candidate survived; it does not rehabilitate reflection ownership as positioning evidence.

Canonical relative coordinates make the error precise:

| Observation | Working `(a,b)` | Closest `(a,b)` | Working / closest index, `6a+7b` |
|---|---|---|---|
| C-1721-1566 | (137,131) | (138,130) | 1739 / 1738 |
| K-1740-1575 | (137,130) | (137,130) | 1732 / 1732 |
| C-1770-1577 | (137,129) | (137,129) | 1725 / 1725 |
| MAT25-K-1719-1592 | (136,131) | (136,131) | 1733 / 1733 |

The colored-to-colored bridge is `(0,-2)` working versus `(-1,-1)` alternative. This is the tested mismatch. The inferred K slot differs geometrically even though its canonical integer coordinates agree, because the neighboring colored anchor has changed coordinates. The unchanged predecessor is a historical index comparison, not new black-body positioning evidence. It is explicitly not shown in the replacement figure.

## Reversible connected-growth experiment

`check_growth.py` adds an isolated screen around windows 124–126. It excludes a local patch only when the measured colored bridge is robustly single-family and its proposed coordinate difference mixes families. It introduces no score weight, no new abstention rule and no global solver. Candidates missing a colored endpoint remain unassessed and retained. The original patch bank is never written back.

Of 180 patches, 55 have the mixed-family discrepancy, 30 preserve the measured family and 95 lack an endpoint for this check. The original single-seed R328 search at width 32 still completes with `(214,201)`. Its canonical 900-observation map equals the historical primary; 17 return observations are retained. This is a local failure diagnosis and reversible screen, **not adoption of a newly established reconstruction**. Missing-endpoint candidates remain a limitation: the screen is not a guarantee that all equivalent global failures are eliminated.

The original working, closest, early and lower paths all replay to completion with 17 returns, yielding `(214,201)`, `(215,200)`, `(214,176)` and `(213,201)`. The early saved history used a rotated starting window; replay normalizes its window order back to the original seed. These unscreened replays demonstrate reproducibility, not correctness.

Cached search took **10.58 seconds** in this run; saved-path replays took about .54/.020/.021/.019 seconds. Total screening/search/replay script took 17.65 seconds. These are local cached timings, not a cold feature-extraction benchmark. Historical R328 timings remain unchanged. No global reconstruction or rendering campaign was repeated.

## Actual model geometry and colored material

`model_geometry.py` constructs `photo2/r321/model.py:Chain` from the exact saved parameters in `r324/results/R321-geometry-best-frozen.json.gz`. Its projected centers match the export with maximum delta zero. It traces **175,840 camera rays** over native crop `[1230,208,1510,365]` at .5-pixel spacing, with all **3,000** bodies present. There are zero unresolved rays. Separate isolated traces for M−33 and M−27 show their own projected footprints. The geometry export took about .91 seconds; rendering light is unnecessary.

The displayed boundaries are raster boundaries of these real footprints, quantized to the sampling grid. They are not analytical contours, guessed ellipses or complete boundaries inferred from three support samples. The visible footprints include occlusion. Model centers are labeled separately from photographic pigment centroids.

`diagnose_model.py` compares native colored pixels with the frozen visible owner raster. At index zero / 26 / 38, assigned model addresses are −64 / −38 / −26. Baseline coverage is 194/327, 296/751 and 126/625 pixels. The mask variants and exact counts are in `colored-model-comparison.json`. These are conditional disagreement measurements; body placement, shape, camera, occlusion and correspondence are not separately identified. The low coverage at zero prevents a claim that the first physical mismatch begins at 31.

## Verification and reproduction

From the repository root, using the existing environment:

```bash
MPLCONFIGDIR=/tmp/r329-mpl .venv/bin/python -m photo2.r329.photographic_diagnostics.continuity
MPLCONFIGDIR=/tmp/r329-mpl .venv/bin/python -m photo2.r329.photographic_diagnostics.model_geometry
MPLCONFIGDIR=/tmp/r329-mpl .venv/bin/python -m photo2.r329.photographic_diagnostics.diagnose_model
MPLCONFIGDIR=/tmp/r329-mpl .venv/bin/python -m photo2.r329.photographic_diagnostics.check_growth
MPLCONFIGDIR=/tmp/r329-mpl .venv/bin/python -m photo2.r329.photographic_diagnostics.draw
MPLCONFIGDIR=/tmp/r329-mpl .venv/bin/python -m photo2.r329.photographic_diagnostics.verify
PLAYWRIGHT_BROWSERS_PATH=/home/rharris/.cache/beads-playwright .venv/bin/python -m photo2.r329.photographic_diagnostics.preview_check
```

The [verification receipt](verification.json) records protected-source hashes, raw pigment checks, family isolation controls, black-coordinate perturbation invariance, model/raster consistency, exact replay comparisons, Markdown links and figure inventories. The [browser receipt](browser-verification.json) covers desktop, narrow and offline loading of a local Markdown preview, not the live GitHub service. Every replacement PNG was separately inspected at reading size; the text distinguishes visible discrepancies from archived arithmetic not shown locally.

No R330, final count, period, physical-model adoption or historical graph replacement follows from this supplement. Stop for photographic review.
