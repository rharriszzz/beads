# R257 — native surface metrology and lighting inversion

## Outcome and scope

The R256 debugger now supports native first-hit measurements, source-surface normals,
shared-light highlight footprints, shadow diagnostics, asynchronous local calculation,
review findings and complete numerical exports. **Precise photographic lighting has
not been recovered.** The fitted configurations fail the held-out localization test
on the inherited geometry. They remain inspectable hypotheses, not accepted lamps.
The frozen N2696_h+1_f0 model, origin2162, indices and original reviews are preserved.
No global indexing, pattern optimization or broad color segmentation was performed.

[Clean bead2 comparison](review/r257/bead-2-clean.png) ·
[One location per panel](review/r257/bead-2-locations.png) ·
[All crops and machine-readable measurements](review/r257/README.md).

## What each location means

The physical center is the existing modeled 3D annulus center projected through
the saved camera. It need not lie on visible material. Local coordinates use x
along the planar centerline tangent, y along its planar normal and z normal to
paper. The actual `beads.pov` profile is an axially stretched rounded rectangle
revolved about x: major radius0.57R, unrounded half-extent0.086R, corner radius0.344R,
axial stretch0.7/0.43, hole radius0.14R. R=2.110915748921366 source units.

The outward point `center + R*minor_radial` is on the **outer cylindrical band**
and maximizes the minor-radial support. It is valid, but not unique: moving along
the tangent by up to0.14R gives the same support. We retain the symmetric midplane
representative, not a supposed photograph center. Its first-hit owner and front
surface distance establish modeled visibility separately. Projection does not
commute with finding a silhouette extremum. No projected-silhouette extremum is
claimed or substituted for this point.

Visible centroids integrate first-hit projected **area**, not surface area, volume,
color brightness or photographic interiors. Integer coordinates are pixel centers.
The native grid uses every pixel in a conservative neighborhood enclosing the selected
bead and its ±1/6/7 neighbors. Every ray considers all possible overlapping geometry,
not just those seven beads. Rays intersect the exact annular implicit shape; spheres
are acceleration bounds only. Holes remain holes. Completed first hits count; unresolved
grazing pairs are excluded. Boundary pixels with changing owners are subdivided into
four rays at offsets(±0.25,±0.25), each weight0.25. Empty support gives null centroids.
The full2×2 check detects limitations of the boundary-only heuristic; it is not a
mathematical error bound for arbitrarily tiny subpixel exposures.

Normals are analytic gradients of that stretched profile, including inverse axial
stretch, inner-hole sign, flat caps and curved fillets. The reflection diagnostic
uses the viewer/light half-vector and a shared Blinn lobe, exponent
`max(1, 2/radians(roughness)^2 - 2)`, multiplied by positive n·l. This is a relative
single-scattering lobe, not a calibrated full BRDF. Ambient does not create a point
highlight. Self-shadow, neighboring blockers and camera occlusion remove contributions.
A predicted highlight is the intensity-weighted centroid of samples at ≥50% of its
peak; its peak, covariance, principal-axis sigmas, orientation, region pixels and peak
3D surface point/normal are also reported. A maximum below1e-4 is undefined.
No predicted zero is presented as a photographic reflection.

## Photographic evidence and measurement path

Start with the [raw evidence montage](review/r257/reflection-evidence.png), then the
[coordinate/patch ledger](review/r257/observations.json). The existing **photo-only**
R256 bright-on-dark detector supplies119 candidates without old bead labels. A25×25
native neighborhood estimates a30th-percentile background in the minimum linearized
RGB channel. The connected half-contrast component containing the photographic seed
supplies intensity-weighted position, covariance and area. Reliability requires3–90
pixels, dark-surround fraction≥0.55, contrast≥0.35 and no component touching its window.
These conditions reduce diffuse-color and adjacent-body contamination; they do not
prove specularity. JPEG blur, diffuse colored highlights and camera processing remain.
This inversion uses black-surround evidence only; no arbitrary per-color calibration
or material inference is hidden in the result.

Eligibility for geometry-conditioned fitting additionally requires a completed
surface hit, ≥80% patch ownership by that same model bead, ≥20 native visible pixels,
and at most one candidate per owner (strongest contrast×dark-surround first). All119
remain in the ledger. In the primary geometry86 enter the comparison:49 training,
37 held out. Entire photo-angle sectors1,4,6 of8 are withheld before fitting.
The identities and excluded matches depend on geometry; they are not certified bead IDs.

For paper shadows, border-derived RGB chromaticity defines an input-specific candidate
paper class; no hard-coded magenta range is used. A broad locally smoothed upper
illumination envelope supplies a relative darkness deficit. Samples8px apart are
restricted to a25–95px diagnostic distance from model centers. The image supplies
chromaticity/darkness; geometry supplies this sampling region, not shadow labels.
There are893 training and767 held-out samples. Broad texture/color variation, shadowed
paper overlap and a conservative supporting plane make these **weak** constraints.
Local dark interbead pixels are not assigned to either bead as photographic evidence.
Modeled self-cast/neighbor-cast/back-facing channels are separate; photographic
internal darkness remains ambiguous with black material and gaps, rather than being
turned into false per-bead shadow observations.

## Global fit and uncertainty

Compared methods: directional+ambient; a rectangular extended source with a sharp
shared lobe (roughness2–5°); a rectangular source with a smoother lobe (9–15°).
Directions and extents are fitted from training evidence, not supplied by the maker.
The rectangle is a distant-source **finite angular extent** model, integrated with
solid-angle Jacobian weights. It does not claim a finite lamp distance: scaling source
size and distance together is unobservable in this approximation. A nearby finite
positional source is not fitted in this round. The supporting plane is the source
geometry's lower envelope z=−(4+R); its metric height and camera elevation are uncalibrated.

Frozen geometry is used for every fit. Objectives combine native centroid residuals,
covariance size/cross-term residuals, and low-weight paper-darkness residuals. The
paper fit has only two shared nuisance terms (offset and nonnegative shadow strength).
No per-bead position, light, gain or roughness is fitted. Shared material/diffuse and
ambient defaults in the UI are explicit display assumptions; only roughness and light
geometry are fitted, with a shared training gain used to assess relative brightness.

Robust least squares uses four directional starts, max32 evaluations each; extended
sources use two starts, max16 each. These are bounded local searches, not global
optimality proofs. The optimization uses3×3 angular quadrature; **final predictions
and interactive extended-light diagnostics use9×9**, with3/5/9 comparisons retained.
The search-budget limit and source-size/roughness tradeoff prevent interpreting
parameter values as confidence intervals. Heldout data never fits parameters.
Complexity penalty0.15px per parameter plus weak training shadow score nominates the
simplest diagnostic model. Poor shared prediction provides no justification for
adding a second lamp to absorb geometry errors.

See [metrics](review/r257/metrics.json) for exact fit/heldout RMS, median,90th percentile,
size/orientation/relative-intensity errors and shadow performance against a constant
paper-deficit baseline. **No tested source is accurate enough to accept as photographic
illumination.** These configurations are useful for locating systematic failures,
not for certifying predicted highlights or bead order. Their common tendency toward
an elevated source is conditional on camera, normals and index correspondence.

The two alternative global geometries receive the same directional family, objective,
budgets and geographic split. They are also evaluated under the primary directional
light without changing it. Eligibility changes with their footprints, so their raw
scores have different sample counts; they are sensitivity results, not an unbiased
ranking of handedness or total count. No alternative is silently adopted.

## Bead2 and numerical accuracy

Bead2/generator2164 physical center projects to(1353.655,320.046), its outward point
to(1356.319,336.319), and its boundary-adaptive visible centroid to approximately
(1355.819,328.462). The model exposes311.75px². Its4px centroid is(1355.200,329.000):
only about0.82px from the adaptive estimate;1px is about0.18px away. Changing the
marker can therefore move the display by about8.69px relative to the physical center,
while improving ray density moves it by less than one pixel. These are different effects.

The [clean image](review/r257/bead-2-clean.png) shows exactly where that footprint falls:
below the prominent red body, over a dark/reddish partially exposed region. It is
not evidence that there is *no* bead there. Fresh weak red proposals at(1359,324)
and(1358,334) remain ambiguous, and no reliable bright-on-dark reflection is assigned
to this index. Neither a photographed physical center nor a correct replacement
index is known. User feedback on the original cluttered panel confirms only that the
presentation was unclear, not any particular geometric diagnosis.

Beads3 and4 have no reliable visible support in the inspected neighborhood and get
null centroids/highlights. Bead9 in bead2's neighborhood demonstrates why native
tracing matters for small exposures: one4px sample gives a centroid nearly9px from
the adaptive result. The per-bead table preserves such cases instead of dropping them.
The distant straight section and strong bend are selected from low/high model tangent
change, shown on the whole-photo locator; their local shape/lighting failures remain
visible rather than refitted away.

Current evidence rules out the **outward definition** and **4px sampling alone** as
explanations for a large mismatch. It does not isolate camera/registration, minor
phase, bead orientation or index correspondence. Lighting cannot move first-hit
footprints. The next useful experiment is a bounded silhouette/neighbor correspondence
check for0–7, beginning with the visible extent of the red body above bead2 and its
±1/6/7 relationships. Keep the camera/phase alternatives explicit before refitting light.

## Reproduction, tests and provenance

```bash
.venv/bin/python -m photo2.bead_debugger.server --prepare-only
.venv/bin/python -m photo2.bead_debugger.lighting
.venv/bin/python -m photo2.bead_debugger.audit_r257 --alternatives
.venv/bin/python -m photo2.bead_debugger.report_r257
.venv/bin/python -m photo2.bead_debugger.audit_r257
.venv/bin/python -m photo2.bead_debugger.report_r257
.venv/bin/python -m unittest photo2.bead_debugger.test_debugger photo2.bead_debugger.test_surface -v
node --test photo2/bead_debugger/static/logic.test.mjs
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_debugger.browser_smoke
```

The first report pass attaches explicit fit-status/brightness diagnostics; curation
then freezes those complete configurations in its snapshots; the last report writes
shadow panels and hashes. Routine jobs/caches stay ignored. Curated evidence is tracked.
[Input/implementation/artifact hashes](review/r257/provenance.json) include original
photo, literal source geometry, seed spline and all camera hypotheses.

Tests cover profile support to1e-12 model units, analytic versus finite-difference
normals to1e-8, camera projection to1e-10px, first-hit overlap/hole visibility, hidden
beads, centroid convergence, directional half-vector behavior, moving highlights,
extended-source spread, self/neighbor blocker IDs, paper shadow displacement and
softness, synthetic light recovery (0.02° parameters; heldout intensity RMS<1e-5),
and real bead2/origin invariance. Camera marching epsilon is1e-5 source units,
shadow origin offset1e-3 units, outward visibility depth tolerance0.005 units. These
are numerical tolerances, not photographic accuracy. Browser tests use temporary
reviews and verify pan/zoom, both hands, origins, old backups, new actions, independent
layers, asynchronous races and complete exports. No production finding is fabricated.

The implementation follows the standard distinction between directional/extended
sources and shadow-ray visibility described in PBRT's
[light interface](https://pbr-book.org/4ed/Light_Sources/Light_Interface) and
[area-light sampling](https://www.pbr-book.org/3ed-2018/Light_Transport_I_Surface_Reflection/Sampling_Light_Sources).
The annular shape is this repository's geometry, not a sphere approximation.

### Final measured comparison

All37 held-out primary-geometry candidates are retained in these denominators.
The best heldout score is reported, not used to select fit parameters or to certify a source.

| Global source | Train RMS (px) | Heldout median / RMS (px) | Heldout within3px | Source angular extent | Shared roughness |
| --- | --- | --- | --- | --- | --- |
| Directional, default by complexity | 8.15 | 9.22 / 9.85 | 0/37 | point direction | 5.68° |
| Rectangle, sharper surface | 8.58 | 9.10 / 9.97 | 0/37 | 29.92° ×37.53° | 3.37° |
| Rectangle, smoother surface | 8.11 | 8.72 / 9.24 | 1/37 | 40.95° ×53.58° | 10.87° |

Directional fitted direction in source world coordinates is
(−0.24943,−0.07380,+0.96558), elevation74.92° above the assumed paper plane.
The alternatives span elevations62.88–78.34°. These are conditional effective
parameters, not measured lamp coordinates. Heldout paper-deficit RMSE is0.09937
(directional) versus0.10066 for a constant baseline, only a small improvement.
The smoother rectangle gives0.09856. Shadow evidence does not establish source
size/distance; relative intensity and orientation also remain imperfect.

Across unique inspected visible indices, centroid median / maximum differences
from the adaptive result are0.576/8.744px at4px,0.190/0.848px at2px, and
0.078/0.354px at1px. Native tracing reveals one tiny exposure missed by coarser grids.
Full2×2 supersampling differs from boundary-adaptive centroids by at most0.0058px
in the ten selected views. Extended-light3×3 versus9×9 highlight centroids differ
by up to0.538px (sharp) and0.277px (smooth) in the geographically distributed
quadrature subset. The final UI uses9×9; this angular convergence check does not
measure photographic accuracy.

The updated debugger passes22 Python tests, the JavaScript coordinate/navigation
contracts and the expanded actual-Chromium checks recorded in
[browser-verification.json](review/r257/browser-verification.json). The clean-view
presets and old-review preservation are exercised directly. Linux Chromium was
tested; Windows forwarding itself was not.
