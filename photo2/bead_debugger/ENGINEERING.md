# R258 extension

`refit.py`: absolute periodic planar cubic, compact curve/phase modes, exact-ray
positive-footprint objective, unknown-identity matching, body/group holdout and
physical regularization. The confirmed R258 B pixels are separate input evidence.
`raycast.py`: dimension-parametric exact source annulus for sensitivity, regression
checked against the existing tracer at source dimensions. `alternatives_r258.py`:
matched counts/hands and phase starts. `compact_r258.py`: explicit post-hoc controls.
`global_r258.py`: ten unanchored whole-curve modes fitted to distributed training.
`audit_r258.py`, `report_r258.py`, `package_r258.py`: native neighbors, ablations,
physical/index/occlusion sensitivity, curve assembly, clean plots and numerical tables.
`test_refit.py`: inverse recovery, historical-input independence and additive reviews.

`registry.py` dispatches new models while leaving `models.py` byte-unchanged. Old
model version hashes therefore stay valid. The server and native Scene use the
registry; old reviews/origins and generated detector observations are untouched.
New models load on demand rather than tracing all alternatives at startup. Source
hashes include new parameters and geometry code; native caches remain separate
from the review store. No review migration or automatic fitting from user records.

R258 polygon fields are optional additions to review records. Old backup schema1
remains valid; imports retain all original fields and IDs. Polygon vertices are
validated as finite native image coordinates. The browser stashes polygons with
model-specific drafts and exports them together with geometry and native owners.
Model switching retains the displayed address and viewport, never relabels history.

[Full method, physical assumptions and unresolved limits](../BEAD_DRIVEN_R258.md).
Earlier engineering records follow for provenance.

# R257 engineering extension

`surface.py`: analytic source-annulus normals; existing camera SDF marcher;
all-scene shadow rays accelerated in the light-perpendicular plane; distant
rectangular source quadrature, half-vector lobe and highlight moments.
`lighting.py`: photo-derived reflection/paper evidence, geographic holdout and
bounded shared-light fits. `detail.py`: native/adaptive ownership, convergence,
local light/shadow measurements, full-provenance cache and one-worker job service.
`audit_r257.py` and `report_r257.py`: native crops, clean explanation panels,
matched geometry checks, quadrature/centroid tables and immutable evidence hashes.

The R256 `models.py` adapter and all geometric inputs are untouched: old model
versions, generator indices and origins stay valid. R257 numerical results use a
separate cache namespace and schema; new review records include lighting snapshots
and cache identity, and history distinguishes earlier R256 numerical measurements.
No migration overwrites findings or backups. Optional new store actions are additive.

`/api/lighting` supplies versioned curated configurations. `/api/surface?id=...&gi=...&light=...`
returns `working` or `ready` with a result. Polling does not block the browser; a
selection token discards stale results. Worker results are cached on disk, scene
geometry separately in memory; obsolete queued calculations are cancelled. Native
patches consider all camera occluders; shadow acceleration considers the entire
scene, including geometry distant in the camera image.

[Full scientific protocol, tolerances, assumptions, results and reproduction](../SURFACE_LIGHTING_R257.md).
Run both `test_debugger` and `test_surface`; the expanded `browser_smoke` uses
only temporary review directories and covers new controls/exports/races too.
The original R256 implementation record follows and describes coarse caches only.

# R256 generation, provenance, model boundaries and tests

[Launch and controls](README.md).

## What is independently regenerated

### Splines

`vendor/historical_splines.py` contains only the transitively required numerical
functions from `rharriszzz/fft-image-explorer/find_splines.py`, commit
`2caf0707c2b63a0d7540e2cac447d2f1b883d8c1`. Exact source hash, retained function list
and modifications are in [vendor/PROVENANCE.json](vendor/PROVENANCE.json).
Plotting/interactive failure handling and output writing were removed; numerical
ring tracing was preserved. Only NumPy and matplotlib's HSV conversion are used
by the port; SciPy performs the repository's periodic cubic refinement.

Historical parameters: ring radius 64px, 720 ring samples, max background gap 14,
Catmull–Rom edges (six samples per segment), clockwise threshold tracing at 50
on a binary 0/100 map. The historical **hand-calibrated** background predicate is
inclusive HSV-u8 `H=219..242, S=100..200, V=80..250`, obtained by rounding HSV×255.
This is a replay of a historical color calibration, **not** a new palette-independent
boundary algorithm. It uses no bead positions or adjacency. The background ring
helper's historical boolean convention is retained exactly, including its legacy
name; changing it would change the reproduction.

The port regenerates 152/142 closed edge control points, 907/847 edge samples and
303 boundary-midpoint centerline points. Compared separately with
`photo2/review/r255/historical-splines.json`, **maximum coordinate difference is
0px** for both controls, both edges and the midpoint centerline. Radius values
are newly recomputed; the archived reference does not contain radii. A periodic
cubic with the original 2px smoothing target reproduces the R175 curve within
**0.001px** (the R175 seed was rounded to four decimals). Neither numeric replay
nor smoothing establishes a true silhouette or removes possible shadow bias.
The archive is read only by comparison/tests and an optional viewer layer.

### Fresh observations

`generate.py` reads only the photograph and its own numerical code/parameters.
The detector receives neither splines nor legacy models. It estimates background
hue from generic image-border samples, finds bright non-background hue modes,
learns mode widths, and identifies positive chromatic interiors. Red/yellow names
are semantic labels on learned modes, not reused historical HSV boxes. Generic
brightness, area and distance parameters are recorded, not fitted bead identities.
For this photo the learned modes are red 355°±6° and yellow 28°±8°.

Distance/brightness maxima propose interiors; positive support pixels exclude
low-value/seam pixels and are kept separate from centroids and unestimated physical
centers. Connected color masks may contain multiple proposals. Straight routes
between nearby same-component interiors preserve V/chroma samples, endpoint
positions and valley depth. Two substantial interiors **plus** a measured valley
support a split hypothesis; weak split evidence marks both candidates ambiguous.
This is an inspectable heuristic, not a certified topology detector. A highlight
or brightness minimum alone does not establish a bead. Tiny proposals remain
rejected records instead of vanishing from diagnostic coverage.

The initial inventory has **2,750 proposals**, including **214 interior-class
points**, 1,450 ambiguous split proposals, 102 small patches, 865 rejected tiny
proposals, and 119 reflection-plus-dark-surround candidates. **These are not bead
counts.** Over-segmentation, omissions and shadow/color errors remain likely;
no precision/recall or generality claim is made. Black candidates locate a
reflection, not a center. No unexplained dark area becomes a bead or a missing
pattern color. No old “trusted” classification elevates any new candidate.

Stable IDs contain image hash, learned color label and integer native position;
generation manifests bind code, parameters, source image and output hashes.
A regression test copies only this generator, its vendor module and the original
photo to an isolated directory **without any historical annotation, graph, model,
or saved spline files** and reproduces the same inventories/splines byte for byte.

The viewer serves lossless decoded RGB, with no recoloring/white balance. The
original Apple ICC tag is omitted from the display PNG so browser conversion
does not change numeric channels relative to Python's unconverted JPEG decoding.
The original JPEG, including its profile/metadata, remains untouched and available
for download. All geometry and observations use integer pixel centers, x right,
y down, at native 2540×3182 resolution; image corners are at −0.5 offsets.

## What remains legacy-assisted or staged

All three geometric hypotheses—N2696/h+1/orthographic, N2674/h+1 and N2681/h−1—
retain their R254 fits and inherited R175 spline seed. Those fits used historical
manual identity/adjacency constraints. They are never described as independently
fitted geometry. The independent spline overlay is regenerated separately.
Fresh ray ownership and candidate alternatives are recomputed against each
saved model, without feeding assignments back into the detector or fit.

Visibility is exact rounded-annulus ray intersection **sampled at 4px spacing**,
not an exact silhouette-area integral. Empty sampled support is labeled “occluded
or smaller than 4px grid”; partial unresolved ray intersections are excluded.
The viewer does not claim an exact visible fraction or independently measured
surface ownership. A photographed point owned by a model is still only a
conditional candidate match. Surface centroids may lie outside a visible crescent.

The independent fit is explicitly staged, not silently substituted:

1. Freeze and hash the image-only detector, review split/merge examples using this
   app, and preserve unsupported candidates without treating review as automatic fit input.
2. Build an image-only likelihood from positive patches and explicit alternatives,
   using the regenerated curve. Reserve distributed image sectors for validation;
   do not import maker coordinates, graph edges, R252 acceptance, or old origin.
3. Fit equal-budget ±hand/count/camera/phase hypotheses initialized from image
   structure/FFT, with a separately confirmed fresh origin and explicit origin gauge.
   No manual observations may initialize or score an “independent” model.
4. Check surface ownership, local neighbor evidence, held-out residuals and count
   closure. Publish new immutable model IDs and provenance without remapping old reviews.

This round performs **no new global optimization or color-pattern campaign**.
The saved P337/P382 templates are contradictory legacy diagnostics. Other model
colors remain unknown. No valid pattern or independently recovered global order
is claimed.

## Reproduce and test

```bash
# Force fresh generation from the original image; keep reviews separate.
.venv/bin/python -m photo2.bead_debugger.generate --output photo2/output/debugger/generated
# Prepare all diagnostic models without opening a server.
.venv/bin/python -m photo2.bead_debugger.server --prepare-only
.venv/bin/python -m unittest photo2.bead_debugger.test_debugger -v
node --test photo2/bead_debugger/static/logic.test.mjs
# Optional browser test tooling only (not a runtime dependency):
.venv/bin/python -m pip install -r photo2/bead_debugger/requirements-test.txt
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_debugger.browser_smoke
```

The browser test uses an ephemeral port and temporary reviews. It exercises real
image pixels, clicking, wheel/pan, keys, wraparound, both hands, model switching,
all overlays, hidden indices, fresh origin, note/correction saves, backup/import,
debug crop export, restart restoration and label/draw performance. It requires
permission to launch Chromium and bind a local socket in restricted environments.
Linux Chromium is tested; the Windows browser/WSL forwarding path requires the
user's ordinary Windows session and is not claimed to have been exercised here.

[Curated screenshots, exact regression results and optional review questions](../review/r256/README.md).
