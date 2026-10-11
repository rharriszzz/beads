# Bead reconstruction debugger (R257)

A local application for inspecting the real photograph, fresh interior proposals,
and competing **legacy-assisted** geometric hypotheses. Reviews do not change the
detector, geometry, correspondence, or pattern.

## Start here

From the `beads` repository in WSL:

```bash
.venv/bin/python -m photo2.bead_debugger.server
```

Open **http://localhost:8767** in your Windows browser. Keep the terminal running;
Ctrl+C stops the server. The first launch regenerates missing data and prepares
three model caches; wait for the printed browser address. Later launches reuse
hash-checked caches. No JavaScript build, npm install, cloud service, API key, or
other working repository is required. Runtime dependencies are the existing
Python 3.12 environment and [photo2/requirements.txt](../requirements.txt).
Use `--port 8768` if needed, then open the corresponding address.

1. Click **Bead 0**, then **k+1** to inspect 1, 2, 3. Left/right arrows do the same
   when focus is on the photograph. **Home** jumps to 0.
2. **Q/E** navigate −6/+6; **A/D** navigate −7/+7. Buttons also work. Every index,
   including hidden beads, remains navigable; indices wrap modulo the chosen N.
3. Enter an index or a fresh observation ID in the search field. Partial IDs show
   suggestions. Click a photographic marker or a modeled center to select it.
4. Wheel zoom follows the pointer; drag pans. **Fit photograph/F** and **Reset
   view** show the whole image. **Center selection/C** zooms to the selected area.
   Turn **Follow selection** off to walk indices without moving the photograph.
5. Select another named model at the top. Zoom/pan and the selected photographic
   observation stay fixed; its conditional index and modeled location can change.

Keys are inactive while typing into fields or operating buttons. Click the
photograph to return keyboard focus. The side panel scrolls independently.


## R257: native surfaces and lighting

Restart the same local server after updating. Begin at bead0, then use **Inspect →
Selected footprint only** for a clean view with one modeled bead's pixels. **Selected
locations** adds just the physical center and three calculated locations. Native
layers default to the selected bead; clear **Show native overlays for selected bead
only** to include its ±1/6/7 neighbors. Pan/zoom stays responsive while the server
calculates; stale results from earlier selections are discarded.

**Layers → E2** controls each item separately:

| Overlay | Meaning |
| --- | --- |
| Selected physical center | Blue ring, projected 3D annulus center |
| Audited radial extremum | Orange × if visible; gray × if occluded |
| Native visible area centroid | Green dot, first-hit pixel area after boundary supersampling |
| Predicted highlight location | Pink ×, intensity-weighted centroid; undefined means no marker |
| Predicted highlight region | Pink intensity pixels on visible source-compatible surface |
| Observed photo reflections | White rings, independently detected candidates; no forced match |
| Native owned pixels | Owner-colored native1px footprint; selected-only by default |
| Shadow diagnostics | Purple modeled cast shadow, yellow back-facing surface, orange observed paper darkness |

The older **E** group remains explicitly coarse4px for comparison; do not confuse
it with E2. Select **Inspect → Global illumination** to switch directional,
rectangle-sharp or rectangle-smooth configurations. **All are diagnostic fits with
poor held-out accuracy**, not recovered room lighting. Model switching keeps the
same illumination so geometry errors stay exposed; the displayed heldout score
belongs to the primary geometry unless stated otherwise.

Inspect lists original-image coordinates, 4/2/1px and adaptive centroid differences,
outward first owner, highlight peak/centroid/shape, observed candidates and a
reflection discrepancy only for a unique reliable conditional match. The expandable
surface record includes3D points, camera-ray failures, self/neighbor blockers and
uncertainties. The clean [bead2 comparison](../review/r257/bead-2-clean.png) and
[one-marker panels](../review/r257/bead-2-locations.png) avoid the rejected cluttered
question image. [Scientific findings and limitations](../SURFACE_LIGHTING_R257.md).

New Review findings cover visible-centroid errors, predicted-reflection errors,
incorrect/missing photographic reflections, and likely lighting mismatch. Notes,
Shift-click correction positions and old findings still work. R256 history is
labeled as coarse measurements; it is not rewritten. New records also preserve
selected lighting parameters and the numerical cache identity. Geometry hashes,
indices, saved origins and the review/backup storage format remain unchanged.

Debug ZIP now includes full native ownership/highlight pixels, all selected-neighbor
3D/projected points, convergence/visibility/shadow diagnostics, lighting parameters,
observed candidates, uncertainty and saved findings, alongside its exact original
crop. Detail JSON uses both original generator IDs and explicitly named legacy k;
the top-level review record preserves your chosen origin separately.

Missing local detail caches are computed on demand under
`photo2/output/debugger/surface-r257/`. Keys include the source photo, geometry/camera,
source code, photographic observations, light parameters and numerical resolution.
They never modify `reviews/`. The global4px navigation cache remains unchanged.

## Inspect and toggle evidence

The **Inspect** tab separates the predicted center, minor-outward point, geometric
visible-area centroid, photographed interior/reflection, and candidate template
color. Original and annotated crops are shown together. Numerical evidence includes
positive patch area/radius, HSV, representative ray ownership, patch ownership
fraction, center residual, six nearby competing indices, and same-component
intensity/chroma profiles. A center residual is **not** physical-center error.
Multiple interiors may compete for the same modeled surface; no one-to-one
assignment is silently imposed.

The **Layers** tab has independent switches, a shared opacity slider, and a
**Photograph only** button. Toggling preserves selection and view. Selection
locators are suppressed in photograph-only mode; a clicked review correction
remains visible until cleared. Dense labels appear at ≥1.5× and are collision
culled; observation labels appear at ≥3×. Selected/neighborhood labels take
priority.

| Category | Available controls / diagnostics |
| --- | --- |
| A | Original full-resolution photograph; untouched original JPEG download in Diagnostics |
| B | Regenerated inner/outer edges, refined centerline, raw boundary midpoints, tangents/normal guides, registered model line, archived spline comparison |
| C | Independent colored interiors, ambiguous/small patches, rejected proposals, reflection-on-dark-body candidates, positive support pixels |
| D | R200/R252 and maker marks; separate historical withheld proposals; both **off by default** and marked legacy-assisted |
| E | Modeled centers, minor-outward points, visible-area centroids, ray-owned surface footprints |
| F | Selected ±1 (white), ±6 (cyan), ±7 (orange) vectors; negative directions dashed, conditional on the model/hand |
| G | Signed `(n1,n6,n7)` algebraic triples; legacy maker topology is separately accessible in Diagnostics |
| H | Conditional string indices and optional original generator indices |
| I | Fresh interior-to-model-owner links, failed-hit crosses, competing indices and patch ownership in Inspect |
| J | Saved R250 FFT frequency axes, nearby candidate measurements, raw candidate CSV/measurements and track/angle figures |
| K | Rejected legacy P337/P382 residue proposals, contradictions, unknowns and selected fresh color; never repaint original pixels |
| L | Longitudinal displacement vectors, stretch/twist curves, N/hand/turns/camera/registration, and saved alternative-model comparison |

Normal cross-section lines are ±50px **guides**, not freshly measured widths.
FFT vectors represent frequency axes, not observed bead-neighbor directions. The
whole-photo FFT layer samples drawing locations for legibility; all 32,000 raw
candidates remain available. There is **no newly established adjacency graph**.
The legacy maker graph is a linked diagnostic, not imported into new detection.

Display triples use the balanced signed index `s=k` for `k≤floor(N/2)`, otherwise
`s=k−N`; `n7=floor((s+3)/7)`, `n6=0`, `n1=s−7*n7`. Thus
`k ≡ n1 + 6*n6 + 7*n7 (mod N)`. These are algebraic addresses, **not independent
observed walks**. Neither sign convention nor a saved global fit proves helicity.

## Record a finding and resume

Open **Review**, select a finding, and enter a note. Optionally Shift-click the
photograph to attach a native-coordinate correction, or enter another candidate
ID/index. Click **Save review** or **Save & next**. The visible reviewed count
counts distinct generator indices for the **exact model and detector versions**.
**Next unchecked/N** wraps through increasing indices until it finds an unchecked
one. “Cannot determine” is still a completed review, not an accepted reconstruction.

Your place, view, layer settings and drafts save automatically after a brief
pause. The footer reports the saved revision or a failure. Findings require the
Save button. Drafts also survive navigation/reload in browser local storage.
Opening the same address after restarting restores the saved position. Multiple
browser tabs use revision checks: a stale write fails visibly instead of replacing
another tab's work; use **Reload saved state**, inspect the retained draft, then save.

The server stores reviews under **`photo2/output/debugger/reviews/`**:

- `latest.json` is an atomic, fsynced snapshot.
- Every mutation also creates an immutable `revision-*.json` snapshot.
- Findings are append-only, with model/version, detector generation, generator
  index, displayed index/origin, stable observation ID, source/correction pixels,
  note, enabled layers and saved time.
- The **Download review backup** link and **Import backup** control work in the
  browser. Imports merge by record ID, reject conflicting content and wrong-image
  files, and restore the backed-up session. They never refit anything.
- A corrupted latest snapshot causes an explicit startup error; it never resets
  reviews. An earlier revision is a complete backup, usable with Import in another
  `--work` directory or as a deliberately restored `latest.json`.

Generated outputs and reviews are intentionally Git-ignored. Download a backup
before deleting `photo2/output/`, moving machines, or replacing the working copy.
A second `--work /path/to/directory` gives an independent review workspace.

**Fresh origin:** select a fresh colored-interior observation, then press
**Confirm selected fresh observation as index 0**. This records your explicit
choice and the selected modeled generator index, without importing the old
C252-A948 identity. It changes only the review numbering for that model. Select
saved origins from the dropdown. The initial R255 origin remains an explicitly
legacy reference. No origin is asserted to be the manufacturing seam.

**Export selected bead debugging ZIP** downloads `debug-record.json` and a
pixel-exact `original-crop.png`. It includes model and detector hashes, indices,
source/crop coordinates, enabled layers/opacity/view, candidate measurements,
all selected split profiles, correspondence alternatives, note/correction, and
saved reviews for that model bead. Send that ZIP back for a focused investigation.

## Independence and known limits

- Splines and fresh color/reflection proposals are regenerated from the photo.
  The spline algorithm retains its historical hand-calibrated HSV background box.
- All three global geometric fits remain **legacy-assisted**. Independent fitting
  is staged, and no new observed adjacency graph or valid color pattern is claimed.
- Candidate over-splitting and missed beads remain likely. Whole-photo footprints retain
  a4px grid; E2 selected/neighbor tracing uses1px plus boundary2×2. Extremely small
  subpixel exposure can still be unresolved.
- Actual Chromium interaction tests pass. Windows browser/WSL forwarding was not
  exercised from this environment. No known blocking viewer defect remains.

[Exact algorithm provenance, numerical tolerances, detector accounting, staged
independent fit and reproduction/tests](ENGINEERING.md) ·
[Curated verification and two review examples](../review/r256/README.md).
