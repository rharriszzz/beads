# Reusing the maker's Gaussian FFT experiments — R110

## R247 — maker method primary; next experiment proposed only

[Current spectrum-led/width proposal](FFT_SPECTRUM_LED_PLAN.md) is the active
next-step reference. Maker reaffirms lower cutoff clears bright central spike,
upper cutoff reveals three pairs, then peak/reconstruction inspection. Sigma20
and recent43–57 are candidates, not known correct user settings. Photograph-first
circular-width comparison with both V/Y; helicity-independent candidate selection,
explicit reciprocal/spatial explanations and a procedure freeze before transfer.
Manual replay recommended, profile assistance diagnostic, automation later.
User approval is required before implementation; this update preserves the
methodological clarification only. Prior fixed-band experiments are not a test
of the original interactive selection procedure.

## R244–R246 — three methods and maker cutoff clarification

[Completed comparison and illustrated explanations](FFT_CURVATURE.md). User wants
practice with all three methods: naturally straight selection, elongated Gaussian,
and curve straightening. They are implemented/tested, with controls, failures,
paired V/Y and no unique photo helicity. Circular Gaussian weights do not imply
circular array storage; an ellipse changes spectral blur, not pixel-coordinate
angle scale. Straightening is a separate nonlinear transform. Source Gaussian
startup circle200/softness.20 has sigma20/support5sigma; no saved numeric direction
band found in inspected main/radial-sum history, only background8% metadata.

R246 maker method: raise lower cutoff until the bright central spike is removed;
lower upper cutoff until three opposite pairs are clear. Current bead-scale
bounds plus±20% perturbations do not reproduce that spectrum-led procedure.
Preserve this as maker evidence, not a retrospective description of R243/R244.
Next review/calibration should use it explicitly with frozen transfer settings.
No automatic next-phase implementation at this review stop.

## R243 — authorized experiment completed

[Implementation, quantitative results, figures and reproduction](FFT_HELICITY.md).
R242 was authorized and run: matched raw V/Y at8 review sites and371 dense centers,
13 fixed configurations,24 known-hand renders. Persistent reciprocal directions
are visible, but no unique photo helicity survives sensitivity/projection checks.
Both channels favor h+1 in5/6 primary reserved comparisons;0/6 robust sections.
Mixed known-camera controls favor truth70/96(V),83/96(Y), with individual advantages
for either channel. No fusion or scope expansion. A disclosed post-reserved model
correction replaces redundant world azimuth with image roll; all measurements and
extraction functions remain unchanged. Stop for review of W3/W8 and control examples.

## R242 — paired V/Y local FFT helicity plan; awaiting review

This proposal supersedes R241's Value-only/eight-window implementation plan.
No FFT experiment, render, tracking implementation or helicity inference has run.
The current request requires repository implementation inspection, a concise plan,
then a review stop. No segmentation, complete inventory, global optimization,
full-string indexing, repeat recovery or exact 6/7 closure prerequisite.

### Actual source inspection

Read the six requested files in the clean sibling checkout, whose HEAD and remote
HEAD both equal `2caf0707c2b63a0d7540e2cac447d2f1b883d8c1`. Rechecked R187 spline
provenance, R191's rejection of the bend correction, DIRECTION_ANGLES and the
historical SHAPE_REASONING quick model. The source is unchanged since the earlier
audit. Implemented machinery is available; it has not yet been validated as a
photo helicity estimator.

- `fft_image_explorer.py`: reuse/adapt `rgb_to_hsv_np`, `make_channel_bank`,
  `make_mask`, `compute_fft_products`, `find_top_fft_peaks`, and complex-pair
  synthesis in `FFTExplorer.open_popup_peaks`. V=max(R,G,B);
  Y=0.299R+0.587G+0.114B on the same decoded JPEG RGB, without linearization.
  Disable the loader's default 1200-pixel downsampling for native-scale analysis.
- The peak finder always inserts DC, then groups opposite offsets. Its fallback
  relaxes minimum separation to fill top-k; do not retain that behavior as evidence
  of resolved peaks. Its fixed 6-bin separation and 8-bin support neighborhood
  need explicit scale-aware adaptation. `log_power_sum` is summed log magnitude,
  not integrated physical power or a confidence interval. Score raw coefficients,
  not percentile/gamma-normalized display pixels.
- The popup copies complex coefficients at individual bins, preserving phase.
  Retain that baseline, with optional symmetric lobe masks clearly marked as an
  extension. Validate integer bin mapping: the popup uses half-size-minus-0.5
  rounding whereas peak offsets use floor(size/2). Test odd/even grids, conjugates,
  sinusoid reconstruction, angle signs and tangent reversal before interpretation.
- `map_from_fft.py` confirms Y, Gaussian sigma=softness*size/2, and
  hp_removed=100*low-frequency retained power/total power. Saved metadata is
  128x128, stride8, cutoff8%, shape3182x2540. These background settings do not
  define the directional experiment's frequency band.
- `find_splines.py` has separate map and image-only paths. Saved JSON explicitly
  says `image_only_hsv`, with 303 closed centerline points and no saved radius
  array. The builder takes inner-to-nearest-outer polyline midpoints; it does not
  establish a measured physical centerline. `notes.md` describes proposed tracking,
  anisotropy/confidence/export work; these are not an existing tested tracker.

The earlier table below retains the first three file hashes. Additional audited
SHA-256 values:

| File | SHA-256 |
| --- | --- |
| notes.md | 67ec3f9609ade9f0c37b41f6821445e2ff7afe2656b5df8169afa13970303c1e |
| find_splines.py | a4f0795b01ff9871c9f67f4f7f39dc49cd75314784348b12625b49e8610f3ead |
| beads-photo-2_splines.json | 1e5f0d985be2dfb44b9fa3eac6ad54a0f1345c2ae9a6ed0a8bc3ca510b07dac7 |

Reproduce inspection with `git -C ../fft-image-explorer show 2caf070:<filename>`
for each of the six requested files; compare saved JSON with the actual builder
and the R187 provenance record. Do not launch the GUI or regenerate the map.

### Three approaches and selected implementation

1. Matched raw V/Y Gaussian band-pass FFTs: primary comparison.
2. Matched Gaussian-weighted mean removal: limited illumination/DC leakage control.
3. V/Y evidence fusion or per-color normalization: possible later experiment only.

Select (1), with (2) as one sensitivity variant. Reuse the numerical source in a
small headless adapter with pinned attribution and equivalence checks; no sibling
repository edits. New tracking, uncertainty and model comparison remain explicitly
new work. Python3.12 `.venv/bin/python`; POV-Ray for rendered appearance.

### Sampling, width and frequency choices

- Use the existing R187-provenance periodic image spline as an approximate guide,
  preserving R191's preferred existing bend. First show raw whole-photo overlay,
  local tangents and support; retain uncertain stretches instead of refitting
  the necklace or importing HSV bounds as a runtime detector.
- Freeze eight dispersed review locations from near-equal image arc length before
  spectra, covering tangent orientations and red/yellow/black, shadow and curvature
  conditions. Record any raw-image-based displacement. Two sectors for development,
  six for evaluation; keep the effective Gaussian supports separated from the
  development data. Fill the necklace with uniformly spaced tracking windows at
  step <= half the median projected rope radius. These overlapping windows provide
  continuity, not independent votes. Final count follows measured image scale.
- Estimate projected rope radius R and approximate bead diameter d from raw crops
  and existing boundary guides, with illustrated endpoints and uncertainty; freeze
  before spectra. No full bead inventory. Record pixel coordinates, image arc
  length, tangent, local radius, curvature and original-image/curve hashes.
- Primary Gaussian sigma=R (FWHM=2.355R), cropped at +/-3sigma on a square native
  pixel grid. This states explicitly what characteristic width means and replaces
  R241's FWHM=2R convention. No geometric straightening, hard rope mask, artificial
  square-edge tiling or optional zero padding; rotate vectors for comparison.
- Initial broad band 1/(3d) to 2/d cycles/native pixel, restricted below isotropic
  Nyquist. Adapt the explorer's hard radial masks first, preserving its baseline;
  percentages convert through the actual FFT dimensions. Verify band coverage on
  known-geometry controls. These limits are proposals, not recovered spacings.
- At the eight review locations, fixed one-at-a-time sensitivity: sigma=0.75R/1.25R;
  each cutoff +/-20%; center +/-0.25d along tangent and normal; weighted mean removal;
  one 10%-edge cosine-tapered band variant. Same variants for V/Y, no factorial
  search or tuning on reserved sections. Carry tangent/scale uncertainty separately.

### Candidates, channel comparison and helicity

- Extract up to six supported noncentral conjugate pairs; fewer is valid. Preserve
  competing peaks, harmonics and family assignments. Record radius (bins and
  cycles/pixel), absolute and tangent-relative angles modulo180, raw integrated
  pair power, fraction of band power, local prominence and peak breadth. Estimate
  stability from perturbations; breadth is resolution evidence, not a formal CI.
- Track by uncertainty-scaled changes in tangent-relative angle and normalized
  radius f*d, allowing unmatched peaks, disappearance, reappearance and ambiguous
  links. Strength is secondary to geometry. Inspect unsmoothed candidates beside
  tracks; continuity may not manufacture missing families or force one hand.
- V/Y get identical source pixels, centers, masks, band, extraction rules, parameter
  budgets and common display scales. Compare supported-family coverage, ambiguity,
  continuity, perturbation stability and both-model residuals by sector, including
  weak/failure windows. Do not choose a channel because it favors a preferred hand,
  or count correlated channels as independent evidence. Highlight V-better and
  Y-better examples if they exist; complementary evidence can motivate later fusion.
- In image x-right/y-up coordinates, compare reciprocal vectors, not raw FFT angles
  directly to the unwrapped +/-85.7, -/+48.0, +/-43.6 degree model directions.
  For a locally projected direct-lattice basis A, the reciprocal basis in cycles
  is A^(-T); map all plausible family/harmonic assignments and verify them with
  phase-preserving reconstructions and source-consistent renders. Projection over
  a curved visible tube is only locally affine, so validate the approximation.
- Calibrate both hands with matched uniform and mixed-color POV-Ray controls,
  several section orientations and a bounded set of camera/phase conditions.
  Use at most12 matched full-rope render pairs, extracting multiple orientations
  from each; include orthographic and perspective cases and changing reflections.
  Inspect available EXIF without treating unknown crop/distance as calibration.
  Use the same nuisance ranges for both hands, one shared planar-camera geometry
  within a hypothesis, and no independent local tilts or full-necklace optimization.
  Freeze ranges/thresholds on controls and two development sectors, then evaluate
  reserved sectors. Stop as view-limited if the bounded controls cannot resolve it.
- Use identical robust, uncertainty-scaled angle/radius residual scores for both
  hands, with symmetric unmatched penalties, alternate assignments and explicit
  per-sector contributions. Report score differences and their sensitivity range,
  not an uncalibrated posterior probability. A single informative window can favor
  a hand; convincing photograph-wide evidence requires correct recovery in
  informative known-hand controls and stable agreement in at least five of six
  separated reserved sectors spanning three orientations, with no strong contrary
  sector. The advantage must exceed empirical measurement/projection uncertainty
  and survive assignment, appearance and camera alternatives. Otherwise report
  both hands plausible or the FFT evidence insufficient. The 5/6 gate is a proposed
  practical replication criterion, not a statistical significance claim.

### Deliverable and stop

After authorization: raw location overview and representative crops; matched
Gaussian-windowed V/Y; marked band-pass spectra; single-pair and candidate-triplet
inverse reconstructions; full per-window candidate/assignment CSV and JSON;
tangent-relative direction-versus-image-arc-length plots with uncertainty and
unassigned peaks; paired channel and both-helicity support plots, sensitivity and
failure panels. Save parameters, hashes, source adaptations and reproduction
commands; track curated evidence and keep routine outputs ignored.

Now: documentation only, stop for review. No experiment implementation. Carry
forward the recorded Astra/High recommendation without identifying this new
session's active model; no /new needed for plan review. Next concrete task is
review of this protocol, followed only after authorization by the headless adapter
and source-equivalence/known-geometry controls.

## R241 — proposed bounded Value-channel helicity experiment

**Proposal only; stop for discussion before implementation.** This supersedes
R240's proposed D3 correspondence fit as the next experiment. The user's working
association is the three 1/6/7 direction families; the immediate problem is their
visibility in mixed-color, shadowed and highlighted windows, not inventing new
direction families. No full-necklace indexing or repeat recovery.

Three approaches considered: (1) Gaussian-windowed raw HSV Value with band-pass;
(2) Value with illumination detrending; (3) separately normalized color channels.
Select (1). Preserve raw spectra. A Gaussian-weighted mean subtraction is a limited
DC-leakage control, not per-color normalization; defer (2)/(3) unless this bounded
experiment fails and the user agrees to another step.

### Windows and finite parameter budget

- Select eight centers before viewing their FFTs, initially equally spaced by
  image arc length along the existing approximate centerline. Use raw views to
  ensure varied section orientations and bright/dark/color mixtures. Any move
  from equal spacing needs a recorded raw-image reason, never spectral quality.
  Keep a shadow-heavy and a more curved window as stress cases. Record center,
  tangent, local rope width W, bead-scale estimate d, curvature and source hashes.
  Respect R191's rejection of the candidate bend correction; no curve refitting.
- Mark two dispersed windows for inspection/development and six for a frozen
  evaluation, all chosen before spectra. These are reserved spectral evaluations,
  not previously unseen photographs. Report every selected window, including
  failures. Nearby shifts and overlapping windows are not independent votes.
- Primary isotropic Gaussian: FWHM=W, sigma=W/2.355, cropped at +/-3 sigma in x/y.
  FFT in native image coordinates without a hard necklace mask or geometric
  straightening. Rotate frequency vectors for comparison; tangent-aligned image
  displays are illustrative. Check FWHM=0.75W and1.25W one at a time. Record
  tangent variation over the effective window; severe curvature limits evidence.
- Use V=max(R,G,B)/255 from original JPEG RGB, with no white balance or color
  equalization. Primary FFT is FFT(G*V). Retain complex coefficients and power.
  Also inspect FFT(G*(V-weighted_mean(V))) as the single DC-leakage control.
- Start with radial frequencies 1/(3d) <= f <= 2/d cycles/native pixel, wavelengths
  0.5d to3d, with short cosine transitions rather than abrupt radial edges. Here d
  is an image-derived approximate projected bead diameter, not a spectral neighbor
  label. Freeze its estimator before reserved evaluation; preserve uncertainty.
  These are proposed broad limits, not recovered spacings or old explorer percent
  settings. Verify coverage on known-geometry controls before photo evaluation.
- Sensitivity only: shift each cutoff by +/-20% separately; keep the other fixed.
  Also shift the center by +/-0.25d along the tangent. Together with two alternate
  widths and mean-subtraction this is nine variants plus the primary per window;
  no Cartesian parameter sweep or reserved-window retuning. Clip to Nyquist and
  report unresolvable bands. Zero padding cannot improve intrinsic resolution.

### Candidate peaks, conventions and helicity comparison

Detect noncentral local power maxima, pair k with -k, and consolidate the same
broadened peak/harmonic family. Keep up to six candidate pairs with prominence
relative to their local spectral background, radius, angular width and stability.
Do not force three pairs when fewer are supported. Conjugate symmetry is automatic
for real input and is not itself supporting evidence. Display inverse transforms
of selected pairs beside the raw image to show which structures contribute.

Source coordinates are x right/y down; convert vectors to x right/y up for angles.
Use increasing stored centerline arc length for the tangent; compare unoriented
lines modulo180 degrees. Record signed relative angles in [-90,90). Tangent
reversal must leave them unchanged. A Fourier vector is a reciprocal-space
direction, not automatically a bead-connection vector or simply the same labeled
family after a90-degree rotation. Labels1/6/7 are index offsets, not radial ratios.

Calibrate family associations and hand signs with beads.pov-consistent known
opposite-helicity POV-Ray images: two hands, three section orientations, and two
appearance conditions (uniform pigment; mixed red/yellow/black with shadows and
highlights), at most12 matched renders, reusing suitable existing controls. Keep
camera/light fixed within comparisons; record phase/view and truth separately
from image-only estimates. Check image rotation/reflection and tangent-reversal
conventions. This is limited calibration, not an inverse-rendering project. If
plausible photo view/phase ambiguity changes the inferred hand, report ambiguity.

Only after candidate extraction, compare their tangent-relative angles and
dimensionless radii f*d across windows and fit/match the expected three-family
pattern for each hand. Retain alternate family assignments and penalize missing
or unexplained peaks equally for both hands. Use the same nuisance-parameter
freedom for each hand. Tangent compensation need not make angles identical:
projection and visibility vary with section orientation. Compare against the
calibrated orientation-dependent predictions; do not invent local out-of-plane
centerline tilts. If small controls do not bound this effect, stop as inconclusive
rather than expanding into camera/geometry fitting without discussion.

### Decision gate and deliverable

Freeze extraction rules and confidence thresholds using the controls and two
development windows before opening the six reserved spectra. Thresholds must
reflect peak width, local background and empirical perturbation stability, not
an arbitrary promise of angular accuracy or formal statistical significance.
Convincing evidence requires correct hand recovery in informative known-hand
controls, then the same hand supported by at least five of six reserved windows
across at least three distinct section orientations, with no comparably strong
contradictory window. Family assignment and hand preference must survive the
predeclared perturbations; the opposite hand must fit worse than the empirical
measurement uncertainty, not just have a slightly lower score. Report primary
and sensitivity outcomes separately, along with all excluded/weak cases. If
power spectra cannot distinguish hands under the allowed label/view alternatives,
the result is explicitly inconclusive. Do not count nine perturbations as votes.

Deliver one location overview and compact per-window cards: raw/tangent-aligned
context, Gaussian support, Value image, spectrum with physical frequency axes and
band mask, candidate pairs, pair reconstruction and both-hand comparison. Include
cross-window angle/score table, exact parameters, source hashes and reproduction
commands. Stop at this gate, even on failure; no automatic color-normalization
extension, segmentation revision, bead indexing or pattern inference. Preserve
R240's interior-observation objective for later geometry work.

Retain user-reported GPT-6 Astra / High for design and interpretation. No /new
needed for discussion; recommend /new before an authorized implementation.

## Historical R110 source inspection

The maker reports that Gaussian-window 2D FFT worked well both for background,
including shadows, and for bead directions. Preserve this as **prior practical
experience**, not just an untried suggestion. This review inspected code; it did
not rerun the photograph or measure a new classification/direction accuracy.

Read-only source: `fft-image-explorer` main at
`2caf0707c2b63a0d7540e2cac447d2f1b883d8c1`. Its local `radial-sum` branch has the
same `map_from_fft.py` and `fft_image_explorer.py` contents. No branch switch,
sibling edits or GUI launch. Older README/notes mention
`scan_highpass_removed_map.py`; the inspected current scanner is `map_from_fft.py`.

## Background: clarify which power is measured

R110 says **low-pass power**; R097 described removing the central peak and
inspecting remaining power. These are different raw quantities but can be
complementary fractions when calculated on the same spectrum with complementary
hard masks. Do not silently replace either statement with a new filter.

Let `F = FFT(image_patch * spatial_Gaussian)`, `P = sum(abs(F)**2)`, and `L` be
the central disk. Define `P_low = sum_L(abs(F)**2)` and `P_high = P - P_low`.
For nonzero P and complementary masks:

- Low-pass retained fraction: `P_low / P`.
- High-pass retained fraction: `P_high / P = 1 - P_low / P`.
- Scanner **hp_removed**: `100 * (P - P_high) / P`, hence `100 * P_low / P`.
- Explorer **low-pass removed**: `100 * (P - P_low) / P`, hence the high-frequency
  fraction when the disk cutoff is the same.

The scanner name can therefore be misleading: its background metric really is
low-frequency retained **fraction**, expressed as a percentage. R110 does not
specify whether every earlier interactive trial used a fraction or absolute
power; do not infer those settings from this saved scanner alone. The explorer's
remaining-power percentage uses all enabled filters, including optional thresholding.

[Scanner source](https://github.com/rharriszzz/fft-image-explorer/blob/2caf0707c2b63a0d7540e2cac447d2f1b883d8c1/map_from_fft.py)
uses the Gaussian-windowed luminance directly, with no weighted-plane subtraction.
Its hard disk radius is `highpass_percent / 100 * hypot(height/2, width/2)` in FFT
bins. For its square window, frequency in cycles/pixel is radius divided by window
size. Its Gaussian sigma in source pixels is `softness * size/2`, with softness0.2
in the scanner; window side length is not sigma. Edge padding is used at image
borders. Do not copy these cutoffs between different FFT grids without conversion.

[Saved metadata](https://github.com/rharriszzz/fft-image-explorer/blob/2caf0707c2b63a0d7540e2cac447d2f1b883d8c1/beads-photo-2_map_metadata.json)
records metric hp_removed, window128, cutoff8%, stride8 and a3182×2540 map.
This corresponds to sigma12.8 pixels and cutoff about0.05657 cycles/pixel for the
inspected scanner. The near100/alpha0.25 setting is a display transform, not a
new spectral measurement. These are **one saved run's parameters**, not universal
settings or a new recommended Gaussian width. The file alone does not establish
which code revision originally produced the map; no map provenance/accuracy audit
was performed here.

Uniform multiplicative intensity scaling cancels in this power fraction for an
ideal nonzero patch. That helps explain why it can be useful in a uniformly darker
paper region. A spatially varying or sharp shadow changes spectral shape, and
noise/clipping break that simple invariance. Small total power needs an explicit
weak-signal condition; the scanner returns0 when P is at most1e-12, which is a
numerical convention, not evidence that a black patch is a bead.

**R111 scope:** explore this raw-window low-pass-fraction baseline alongside
plane-detrended and spatial alternatives; final FFT adoption is optional. A new
FFT trial should preserve the source statistic as a fair reference, but it need
not precede useful bead index/color work. Compare against the current
beads probes on identical patches, storing numerator, denominator, mask, Gaussian
parameters and absolute power separately. The R099/R104 detrended high-band RMS
is a different statistic. Its successes/failures cannot by themselves validate
or reject this source baseline. Keep both empirical records.

## Directions: three opposite peak pairs in the bead-scale band

The maker's procedure is: Gaussian window at a centerline point; suppress low
and high frequencies outside anticipated bead spacings; look for **three pairs
of opposite noncentral peaks**; interpret those pairs as directions **1,6,7**.
Use direction1 relative to the local centerline tangent for the helicity cue.
This is the stated working association, to reproduce with the source explorer.

[Explorer source](https://github.com/rharriszzz/fft-image-explorer/blob/2caf0707c2b63a0d7540e2cac447d2f1b883d8c1/fft_image_explorer.py)
implements both radial filters. `find_top_fft_peaks` merges opposite offsets into
one entry, computes angles with y upward, and includes the origin in the selected
list. Default top_k7 therefore does **not** mean three pairs or seven independent
directions. Inspect three nonzero pair representatives for this task; do not count
the center, accept six unrelated maxima, or force the strongest three candidates
to be physical families when the evidence is poor.

The peak popup already reconstructs selected conjugate pairs using the original
complex coefficients and adjustable strengths. Reuse this display to connect each
pair to the image structure. Peak `log_power_sum` summarizes log-magnitude support;
it is not the physical sum(abs(F)**2) used for the background metric.

For real-valued input, conjugate pairs are expected; their existence alone does
not label the lattice families. Use the anticipated band, persistence under nearby
window changes, image reconstruction and known-helicity calibration to distinguish
bead families from harmonics/color-pattern peaks. Keep the maker's successful
three-pair interpretation as the target, without declaring any arbitrary three
pairs sufficient proof. Spectral-to-spatial direction and handedness conventions
remain as described in [the bead methods](../METHODS.md#b2--gaussian-fft-along-the-centerline).

## Reproduce the source inspection

```bash
git -C ../fft-image-explorer show 2caf070:map_from_fft.py
git -C ../fft-image-explorer show 2caf070:fft_image_explorer.py
git -C ../fft-image-explorer show 2caf070:beads-photo-2_map_metadata.json
git -C ../fft-image-explorer diff main radial-sum -- map_from_fft.py fft_image_explorer.py
```

SHA-256 of the pinned source blobs, verified against the clean working files:

| File | SHA-256 |
| --- | --- |
| `map_from_fft.py` | `7295aa5dac6810cfe4bb6137d02837bbae39689454473a720374ca77428858b4` |
| `fft_image_explorer.py` | `73ced947b1825e55ca0d1337fc508bbd4917e574cbea150ae660b61ee8013c24` |
| `beads-photo-2_map_metadata.json` | `a5e1d5fd6081dd517ad96a4abf411385e88bddf93ab2c70e4ee8af65741ccc54` |
