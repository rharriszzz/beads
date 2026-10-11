# Local V/Y FFT helicity experiment — R243

**Completed bounded experiment; photographic helicity remains unresolved.** Local
FFTs recover persistent directional structure, including bands near 0°, +50° and
−45° relative to the centerline in reciprocal space. Both channels' primary
comparisons favor source winding h=+1 in five of six reserved sections, but **zero
reserved sections retain the required score margin across all perturbations**.
The opposite hand remains plausible. This is useful directional evidence, not a
recovered 1/6/7 assignment or a bead-index solution.

[Whole-photo locations](review/r243/locations.png) ·
[Matched channel results](review/r243/channel-comparison.png) ·
[Both-hand support and uncertainty](review/r243/helicity-support.png) ·
[Machine-readable summary](review/r243/summary.json)

## What was reused and what was added

The actual numerical functions from fft-image-explorer at
`2caf0707c2b63a0d7540e2cac447d2f1b883d8c1` are preserved unchanged in
[fft_explorer_core.py](fft_explorer_core.py): channel conversion, Gaussian mask,
radial filters, FFT products and conjugate-pair finder. An AST equality test checks
them against the pinned sibling source. The batch adapter excludes the forced DC
entry and requalifies peaks so the source top-k fallback cannot force six resolved
pairs. It uses actual integrated |F|² and local prominence; the original
`log_power_sum` remains separately labeled. Inverses retain the complex coefficients
at integer FFT bins, with even/odd-grid phase tests. Symmetric-lobe reconstruction
is an explicitly added display, separate from single-bin pairs.

New experimental work: candidate qualification, uncertainty estimates, short-gap
tracking, reciprocal-lattice hypothesis scoring, camera alternatives and reporting.
These are implemented here; the explorer's earlier notes did not already supply a
validated tracker or helicity classifier. Its background `hp_removed` map was not
used as a direction score, and the old HSV spline was not relabeled FFT-derived.

## Sampling and reproducible settings

[Raw crops before spectra](review/r243/raw-scale-review.png) and
[scale rulers](review/r243/scale-evidence.png) show the measurement context.
Eight sites were fixed at equal image arc lengths along the existing approximate
R187-provenance periodic spline; no site moved after spectral inspection. W1/W5
were development; W2/W3/W4/W6/W7/W8 were reserved. Sites cover red/black, yellow/black
and mixed sections. The guide curve and photograph were unchanged.

Cyan endpoints reuse approximate inner/outer boundary guides. Their distances to
the centerline give local R=43.1–57.1px; shadow bias remains possible. Approximate
raw-view bead scales d=32 or34px were fixed before spectra, with20% uncertainty.
**Yellow lines are diameter rulers near beads, not measured single-bead boundary
endpoints**: some cross neighboring surfaces. This annotation limitation is saved
in [scale clarification](review/r243/scale-clarification.json); no d value was
retuned afterward. These assisted guides are diagnostic input for this photo,
not an automatic location/scale estimator or a general reconstruction prior.

- Native2540×3182 decoded JPEG RGB; EXIF orientation respected, no downsampling,
  white balance, linearization, geometric straightening or per-color normalization.
- V=max(R,G,B); Y=0.299R+0.587G+0.114B. Identical pixels/windows/bands and display
  scales for both channels.
- Isotropic Gaussian σ=R, square support±3σ, primary hard radial band
  1/(3d)<f≤2/d cycles/native pixel. No extra zero padding or hard necklace mask.
- Up to6 qualified noncentral pairs; local prominence≥3, separation1.5 Gaussian
  frequency-resolution units. Broadness/resolution and perturbations describe
  uncertainty; they are not confidence intervals. Background/color harmonics can
  still pass qualification.
- Thirteen configurations at each review site: primary; σ×0.75/1.25; each cutoff
  ×0.8/1.2; centers±0.25d in tangent/normal directions; weighted-mean removal; and
  one10%-edge cosine band taper. This gives208 channel/configuration records.
- Dense step24.89px gives371 centers and742 channel-windows. Scale interpolates
  the fixed review-site estimates. All windows fit within the image. Tracking
  allows two missing windows and ambiguous alternatives; it imposes no loop closure.

[Sampling](review/r243/sampling.json), [initial freeze](review/r243/freeze.json),
[sensitivity matrix](review/r243/sensitivity.png), [sensitivity table](review/r243/sensitivity.csv).
The scalar score includes a5° tangent uncertainty floor; actual tangent variation
is reported separately. W3/W6 vary about13.5°/17.3° within one σ, making the local
straight-surface approximation particularly questionable there. See
[curvature accounting](review/r243/curvature.json).

## V versus Y and directional tracking

Neither channel wins universally. On mixed-color known-hand controls, Y favors
the correct hand in83/96 windows, versus70/96 for V. These are **known-camera,
correlated control windows**, not independent accuracy estimates for photographs.
Uniform and mixed conditions also differ in light and minor phase, so the contrast
between those groups does not isolate pigment alone.

| Control condition | V correct preference | Y correct preference |
| --- | ---: | ---: |
| Uniform, orthographic | 44/48 | 44/48 |
| Uniform, perspective | 43/48 | 42/48 |
| Mixed, orthographic | 38/48 | 42/48 |
| Mixed, perspective | 32/48 | 41/48 |

There are examples in both directions: [V advantage](review/r243/control-V-advantage.png)
has true-hand margins0.870(V)/0.098(Y); [Y advantage](review/r243/control-Y-advantage.png)
has0.062(V)/0.863(Y). These are deliberately selected extremes from all mixed-color
controls, with [the selection rule and truth](review/r243/channel-examples.json).
They demonstrate complementary evidence, not permission to select a channel
post hoc for the desired hand. No fusion was attempted.

On the photograph, [W1](review/r243/W1-comparison.png) illustrates substantial
changes in peak ranking between V and Y. [W3](review/r243/W3-comparison.png) is
an important disagreement, and [W8](review/r243/W8-comparison.png) is a sensitivity
failure despite a strong primary V score. All eight comparisons and all individual
pair contributions are linked below; top-three reconstructions are explicitly
illustrative, not automatically the three physical families.

[Unsmoothed reciprocal directions versus distance](review/r243/directions-tracking.png)
show persistent families and competing structures. Each channel retains2224
candidates. V creates201 tracks and Y183; both have median track length4 windows.
There are1252(V)/1255(Y) ambiguous associations. Some tracks persist for over100
windows, but continuity alone does not establish their geometric family. Colors
cycle through track IDs; exact IDs and alternative links are in the tables.

## Both helicities, reciprocal geometry and limitations

The source h=+1 convention is increasing minor angle with index in beads.pov.
The nominal unwrapped outward-reference directions are approximately+85.7°,
−48.0°,+43.6° for1/6/7; the other hand reverses signs. They are not direct FFT
angle predictions. For projected direct basis A=[v1 v6], use B=A^(-T): the reciprocal
vectors normal to rows1/6/7 are b2,b1,b1−b2. Camera-axis parity is explicit and
validated against the source frame; line angles are modulo180°. Reconstructions
keep phase but do not remove reciprocal-family or harmonic ambiguity.

Twelve matched render pairs (24 full-rope images, 1300 synthetic beads each) use
literal beads.pov parameters/macro/placement, both hands, elevations45/65/85°,
orthographic/perspective cameras, uniform/mixed pigments, two phase/light
conditions, and eight section directions per image. Both hands share each
condition and deterministic palette. This synthetic count is not a photo count.
[Render truth, scene/image hashes and commands](review/r243/controls-manifest.json),
[control measurements and failures](review/r243/controls-results.json).

The local scorer compares three row-normal candidates with uncertainty-scaled
angle/radius residuals, one-to-one assignments and a capped missing-family cost.
Unassigned extra peaks remain visible and are not evidence for a hand. Photo
hypotheses consider the same finite elevation/image-roll/surface-radius/front-offset
ranges for both hands. A shared camera for each hand/channel is selected using
only W1/W5; reserved sections are evaluated without tuning. Other shared cameras
are also reported. These are diagnostic hypotheses, not measured camera poses.

**Post-freeze correction:** an audit found the first world-azimuth sweep was a
coordinate gauge and did not vary image foreshortening. It was replaced by the
same four image-roll values and the scores were recomputed. The correction occurred
after reserved inspection and is openly recorded in
[model-correction.json](review/r243/model-correction.json). All208 measurement
records and extraction functions stayed unchanged; see
[extraction audit](review/r243/extraction-audit.json). The final comparison should
not be described as an untouched blind validation. An image-roll regression test
now catches the original error.

| Reserved section | Primary V margin | Primary Y margin | Robust unique hand |
| --- | ---: | ---: | --- |
| W2 | +0.252 | +0.488 | No |
| W3 | +0.071 | −0.455 | No |
| W4 | +0.403 | +0.186 | No |
| W6 | −0.032 | +0.123 | No |
| W7 | +0.348 | +0.348 | No |
| W8 | +1.050 | +0.015 | No |

Margin is score(h−1)−score(h+1), positive favoring h+1. The practical0.5 margin
is not a probability. Neither channel reaches it stably in any reserved section.
The known-camera mixed/perspective controls even contain a wrong preference above
0.5 in each channel. Thus the proposed convincing-evidence gate fails.

Nested EXIF reports iPhone11 Pro back triple camera4.25mm f/1.8, digital zoom1.96875,
and51mm equivalent. [Retained metadata](review/r243/exif.json). Unknown distance
and crop prohibit treating these as calibrated intrinsics. Perspective controls
are stress tests; the photo scorer remains locally orthographic and does not solve
the camera. Curvature, visibility, surface radius, highlights, color periodicity
and unresolved pair/harmonic assignments can share systematic bias across windows.
No complete-lattice closure test or bead inventory was required.

[Conditional direct-angle alternatives](review/r243/direct-angle-alternatives.png)
invert the observed reciprocal basis under tentative family assignments, preserving
both pair-sign branches. [Assignments](review/r243/assignments.json) also retain
third-pair consistency residuals. These are hypotheses, not inferred photo labels.

## Evidence, reproduction and stopping point

| Site | Matched raw/Gaussian/FFT views | Every pair's phase-preserving contribution |
| --- | --- | --- |
| W1 development | [comparison](review/r243/W1-comparison.png) | [pairs](review/r243/W1-pairs.png) |
| W2 reserved | [comparison](review/r243/W2-comparison.png) | [pairs](review/r243/W2-pairs.png) |
| W3 reserved | [comparison](review/r243/W3-comparison.png) | [pairs](review/r243/W3-pairs.png) |
| W4 reserved | [comparison](review/r243/W4-comparison.png) | [pairs](review/r243/W4-pairs.png) |
| W5 development | [comparison](review/r243/W5-comparison.png) | [pairs](review/r243/W5-pairs.png) |
| W6 reserved | [comparison](review/r243/W6-comparison.png) | [pairs](review/r243/W6-pairs.png) |
| W7 reserved | [comparison](review/r243/W7-comparison.png) | [pairs](review/r243/W7-pairs.png) |
| W8 reserved | [comparison](review/r243/W8-comparison.png) | [pairs](review/r243/W8-pairs.png) |

[All candidate measurements](review/r243/peaks.csv) include native frequencies,
angles, strengths, uncertainty, tentative assignments and unassigned cases;
[track associations](review/r243/tracks.csv) preserve competing links.
Routine spectra/model-bank JSON and render inputs/outputs stay ignored under
photo2/output/r243. Curated figures, parameter/provenance records and tables are
tracked. No original image, spline, detector, reference labels or beads.pov changed.

Run from repository root with the existing Python3.12 environment and POV-Ray:

```sh
.venv/bin/python -m unittest photo2.test_fft_helicity -v
.venv/bin/python -m photo2.fft_helicity_controls render
.venv/bin/python -m photo2.fft_helicity_controls evaluate
.venv/bin/python -m photo2.fft_helicity development
.venv/bin/python -m photo2.fft_helicity all
.venv/bin/python -m photo2.fft_helicity_report
```

Use the tracked frozen sampling protocol. `prepare` was the initial raw-only
selection step and deliberately refuses to overwrite that protocol. Routine curve
cache reconstructs from the tracked seed, so reproduction does not require the
sibling repository. The optional source-excerpt equality test uses it when present.
All seven numerical/geometry/tracking checks pass; final artifact reproduction
and preserved-source checks are recorded in [verification](review/r243/verification.json).

**Stop here:** no segmentation expansion, channel fusion, full-necklace geometry
optimization, bead indexing or repeat recovery. Next concrete task is review of
W3/W8 and the known-hand channel examples, then deciding whether a small validation
of reciprocal-family assignments is worthwhile. Carry forward the recorded
Astra/High recommendation without identifying the actual new-session model.
No /new needed for result review; consider /new before a separately authorized
implementation. User controls switching.
