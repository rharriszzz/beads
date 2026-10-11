# Three local FFT approaches — R244–R246

All three approaches are implemented and compared: **select straight sections,
lengthen the Gaussian along the tangent, and straighten the image along the
centerline**. They remain useful complementary tools. None establishes a unique
photographic helicity in this experiment.

[Raw locations](review/r244/locations.png) · [raw crops](review/r244/raw-crops.png) ·
[method/control comparison](review/r244/controls-comparison.png) ·
[both-hand support](review/r244/helicity-support.png) ·
[summary and failures](review/r244/summary.json)

## Gaussian shape and how to read the angles

The maker asked for a circle-based Gaussian, then clarified that sufficiently
large square storage is acceptable because the Gaussian decays rapidly. **A is a
circular Gaussian**, with `g(u,v)=exp(-(u²+v²)/(2R²))`. It has no flat rectangular
interior or separate Gaussian edge treatment. B and C deliberately use an
**elliptical Gaussian**, `exp(-0.5*((u/(2R))²+(v/R)²))`. These are not claims that
rectangles are preferable. [Actual weight profiles and contours](review/r244/gaussian-weights.png).

The FFT array is square. Initially its half-width was `ceil(3*sigma_u)`, making
A's axial edge weight at most 1.11% of its center (corners about 0.0123%). B/C have
still smaller transverse edge weights because `sigma_v=R`. The explorer's
`Ellipse/circle` Gaussian additionally clips at an elliptical boundary; these
experiments initially clipped at the crop boundary. R245 retained that baseline
and checked **4σ support with the same circular Gaussian σ**, rather than silently
changing its width or replacing it with the explorer's hard circular cutoff.

For B the pixel grid is still square, with one native pixel per unit along both
axes. The ellipse only changes weights. A frequency peak `(fu,fv)` therefore has
angle `atan2(fv,fu)`; there is **no aspect-ratio correction to the angle**. Here
`fv` is image-up in the displayed tangent crop. The crop's rigid rotation puts
`fu` along the centerline, so the measured angle is already tangent-relative.
The image-frame angle adds the original image-up tangent angle, modulo 180°.

Rotating **both the image and its Gaussian** rotates their FFT by the same angle,
whether the Gaussian is circular or elliptical. A fixed ellipse would not have
the circle's rotation invariance. This implementation rotates the image into the
tangent frame and aligns the long Gaussian with that frame; it does not stretch
the image to make the ellipse round.

[Known-direction illustration](review/r244/gaussian-angle-explanation.png) shows
identical three-wave signals through circular and elliptical Gaussians, followed
by a 35° rotation of both. Crosses mark exact input frequencies, not fitted
outputs. A numerical 90° covariance test verifies the rotation rule. An elliptical
window's Fourier blur has reciprocal widths: increasing σu narrows blur along
fu. This changes peak breadth/strength, and can shift maxima when components
merge. The exact rule for isolated frequencies does not guarantee unbiased
angles for mixed, shadowed, finite bead patches.

C has an additional, different issue: it resamples `(s,v)` to
`centerline(s)+v*normal(s)`. The array uses image arc-length pixels along s and
normal pixels across it. This is a nonlinear coordinate change, not merely a
rotation. It removes centerline bending but can distort off-center bead texture;
it does not unroll the three-dimensional bead surface or calibrate the camera.
[Source sampling grid and straightened crop](review/r244/straightening-map.png).

## Fixed experiment and reusable implementation

The three options were presented before selection. The maker authorized the
experiment and explicitly requested experience with **all three**, including
straightening. Previous R243 work was already committed/pushed at `963a1b0`;
no older segmentation/indexing task was resumed.

| Approach | Window | What it tests | Limitation to retain |
| --- | --- | --- | --- |
| A: select straight regions | Circular Gaussian σ=R; rigid tangent crop | Avoid bending without a nonlinear transform; also evaluate curved comparators | Fewer repetitions; selection does not separate color, orientation and lighting effects |
| B: tangent elongation | Elliptical Gaussian σu=2R, σv=R | More repetitions and finer longitudinal frequency resolution | Accumulates curvature, color changes and camera variation; anisotropic uncertainty |
| C: curve straightening | Same Gaussian as B, in arc/normal coordinates | Remove image-plane bending before measuring periodicity | Depends on approximate centerline; spatial compression, interpolation and projected surface distortion |

[fft_curvature.py](fft_curvature.py) reuses the pinned explorer channel conversion,
FFT, radial filters and opposite-pair finder from R243. Its Gaussian formula is
the same centered Gaussian used by the source, with explicit σ values. New work
is the coordinate sampler, anisotropic candidate qualification and method
comparison. Existing [R243 analysis](FFT_HELICITY.md), its extracted source,
photograph, spline and beads.pov are unchanged. No background scan is rerun.

The saved approximate image centerline supplies 371 uniformly spaced candidates.
Before looking at new spectra, rank them by Gaussian-weighted RMS tangent turn:
pick six lowest, then six highest remaining, requiring arc separation at least
`6*(Ri+Rj)` and Euclidean separation at least `3*(Ri+Rj)`. Straight sites S1–S6
have RMS 0.07–1.73°; curved comparators C1–C6 have 2.58–11.55°. These are relative
groups after the separation constraint; C6 is only mildly curved. Elongated
windows extend farther and have larger turning RMS (up to 21.72°). This metric
is not R243's within-one-sigma angle range.

Radius and approximate bead diameter interpolate the existing R243 estimates.
They are diagnostic guides, not an automatic scale estimator or measured bead
endpoints. The same locations, widths and frequency limits apply to V and Y.
RGB is bilinearly sampled first, then V=maxRGB and source Y=0.299R+0.587G+0.114B
are computed. There is no white balance, channel fusion or color normalization.
A's rigid interpolation is new relative to the native R243 crop; native controls
are retained so this baseline difference is visible.

Primary band is `1/(3d)..2/d` cycles/pixel. Each location/method/channel has nine
configurations: primary; Gaussian widths ×0.8/1.2; center shifts along s ±0.25d;
each band limit ×0.8/1.2. **12×3×2×9 = 648 records**, including failures. The
protocol, pre-spectral amendment and freeze are saved in
[protocol.json](review/r244/protocol.json) and [freeze.json](review/r244/freeze.json).
The fold guard was strengthened and width tests added before any new spectra.
R245's later support check is explicitly separate from this freeze.

Up to six noncentral pairs survive prominence ≥3 and a 1.5-resolution-unit
separation test. Resolution uses separate frequency widths
`1/(2πσu)` and `1/(2πσv)`; angular and radial uncertainties follow their components
perpendicular/parallel to the peak vector. The origin and unqualified top-k
fallback entries are excluded. Integrated pair power, legacy log strength,
angle/radius uncertainty and alternative assignments remain separate.

Perturbation matching is one-to-one, with fixed ≤10° and ≤0.2 f*d gates. A pair
present in at least six of eight perturbations is called repeatable; alternative
matches are counted. This is repeatability, not a verified physical family.
The separated sites do not justify tracks across unsampled gaps; the earlier
[R243 dense continuity experiment](review/r243/directions-tracking.png) remains
available. No new global smoothing or tracking prior is imposed here.

Sampler guards reject >0.1% weighted support outside the photograph. For C,
`J=1-v*curvature` must remain positive over ±3 transverse sigmas and the main
longitudinal support. Gaussian tails beyond that transverse range are not
certified by the guard; positivity also does not prove global one-to-one mapping.
No intensity Jacobian multiplier is applied: interpolation preserves brightness.

## Results and what they establish

Eight existing e65 POV-Ray images cover both hands, uniform/mixed appearance,
orthographic/perspective cameras and eight section directions. Thus each arm
and channel has 64 correlated control windows. The 384 new arm/channel windows
plus 128 native R243 evaluations use identical render inputs and truth. This is
a diagnostic reuse of known controls, not new held-out validation.

| Method | V correct hand preference | Y correct hand preference | V/Y wrong margin >0.5 | V/Y all three families within true-hand model residual gate |
| --- | ---: | ---: | ---: | ---: |
| Native R243 | 50/64 | 56/64 | 1 / 0 | 19 / 23 |
| A compact circular Gaussian | 56/64 | 57/64 | 0 / 0 | 18 / 18 |
| B elongated tangent Gaussian | 41/64 | 48/64 | 1 / 1 | 6 / 7 |
| C elongated, straightened | 57/64 | 56/64 | 0 / 0 | 8 / 6 |

Straightening recovers much of the hand-preference performance lost by simple
elongation. It does **not** improve three-family agreement with the local model;
its narrower directional uncertainty makes some residuals less tolerable. The
last column is model compatibility, not ground-truth peak labeling. Neither a
correct score sign nor a cleaner spectrum establishes all three physical families.
The fixed local projection approximation remains imperfect on perspective,
curved, three-dimensional render surfaces. Uniform/mixed groups also differ in
lighting and minor phase, so their contrast is not a pigment-only experiment.

| Photograph group/method | V primary h+1 preferences | Y primary h+1 preferences | Median repeatable pairs V / Y |
| --- | ---: | ---: | ---: |
| Straight A | 6/6 | 4/6 | 5 / 4.5 |
| Straight B | 4/6 | 6/6 | 6 / 6 |
| Straight C | 6/6 | 6/6 | 6 / 6 |
| Curved A | 4/6 | 5/6 | 5 / 5 |
| Curved B | 2/5 | 2/5 | 5 / 6 |
| Curved C | 5/6 | 6/6 | 6 / 6 |

C4 B primary fails the image-edge rule in both channels, hence denominator five.
Across all configurations, 22 channel records fail: C3 B wide; C4 A/C wide and
C4 B all except narrow. They remain in the table/summary, without replacement
sites or relaxed thresholds. [C4 failure evidence](review/r244/C4-comparison.png).
No fold rejection occurred among the accepted photographic configurations.

At the almost-straight S1, B and C spectra/results are nearly identical, as expected.
At C1, Y's primary hand margin changes from −0.258 for B to +0.437 for C, but
C's perturbation range is only +0.176..+0.451, below the practical 0.5 margin.
Only S6 A Y clears 0.5 under all eight extraction perturbations (+0.508..+0.864);
its shared-camera alternatives span −0.074..+0.579. It therefore does not establish
a unique hand either. Across methods, **no repeated strong camera-robust result
supports a unique photographic helicity**. V and Y remain complementary.

Camera choices are reused from R243, not optimized on these new results. Both
hands retain the same nuisance grid, reciprocal basis `B=A^(-T)` and competing
assignments. FFT row normals are not the model's unwrapped 1/6/7 directions.
[Reciprocal measurements versus arc length](review/r244/directions.png) and
[conditional direct-basis alternatives](review/r244/direct-angle-alternatives.png)
show the distinction; C's angles belong to its straightened coordinates.
[Every candidate and sensitivity record](review/r244/peaks.csv),
[assignments](review/r244/assignments.json), and
[repeatability versus turning](review/r244/repeatability-curvature.png) retain
ambiguity. Larger repeatable-pair counts are not independent evidence of truth.

### Selected contrasts, including a deterioration

Selection rules and all corresponding scores are saved in
[selected-examples.json](review/r244/selected-examples.json). These deliberately
selected extremes illustrate behavior; they are not prevalence estimates.

- [Largest C-over-B gain](review/r244/control-example-1.png): mixed perspective,
  h−1, Y true-hand margin −0.404→+0.874.
- [Largest C-over-B loss](review/r244/control-example-2.png): uniform orthographic,
  h−1, Y +0.919→+0.423. Straightening is not uniformly beneficial.
- [V advantage within C](review/r244/control-example-3.png): mixed perspective,
  h−1, V +0.337 versus Y −0.005. This does not validate three families.
- [Y advantage within C](review/r244/control-example-4.png): mixed perspective,
  h+1, Y +0.276 versus V −0.343.

## Band-pass operation and boundary choices

[Annulus, transfer function and cutoff-sensitivity examples](review/r244/bandpass-explanation.png).
After Gaussian weighting and the 2D FFT, the filter multiplies each complex
coefficient by 1 where `flo < sqrt(fx²+fy²) <= fhi`, and by 0 elsewhere. Thus the
band is circular in frequency space for **all three spatial windows**, including
the elliptical ones. No frequency direction is favored by the filter itself.
Kept coefficients preserve phase; the log-magnitude image is only a display.
No amplitude thresholding is enabled in the source FFT function. Peak prominence
qualification happens afterward and is a distinct operation.

The lower boundary suppresses DC and broad illumination/background/rope-envelope
variations. The upper boundary suppresses finer bead-edge, highlight and pixel
texture. Neither operation can perfectly separate appearance from geometry:
color sequences can lie inside the retained band, and projected geometry can
fall outside it. The initial heuristic was wavelength `0.5d..3d`, or frequency
`1/(3d)..2/d`, with d the approximate photographic bead diameter. These are
**proposed broad bead-scale bounds, not boundaries derived from recovered lattice
peaks or optimized for a preferred helicity**. R244 inherited the R243 protocol
and did not tune them on its results.

For d=33px this means 0.01010..0.06061 cycles/pixel, wavelengths 99..16.5px.
The explorer sliders express radius as percent of FFT origin-to-corner distance,
so a square FFT uses `percent=100*sqrt(2)*f`: approximately 1.43% high-pass and
8.57% low-pass for this example. These settings are not the earlier 8% background
scanner experiment and do not use `hp_removed` as a direction measurement.

Each endpoint was changed independently by ×0.8 and ×1.2, identically for both
channels and all methods; widths and positions were perturbed separately.
All such results, including disagreements, remain in the tables. No favorite
cutoff was selected afterward. Current boundaries are **hard**, so their inverse
kernel can ring; selected-bin inverses also deliberately produce global waves.
R243 separately tested a tapered frequency boundary. R244 does not claim that
hard cutoffs are optimal, or that inverse-wave extrema mark bead centers.
A future tuning task would need a fixed control/validation split and an objective
based on known frequency families, before revisiting the photograph.

### What the original repository and maker preserve

A read-only search of explorer main `2caf070` and the available `radial-sum`
history found **no saved numeric pair of bead-direction band boundaries**.
The map metadata preserves only the background scan's 8% cutoff. Interactive
startup defaults are high-pass 0%, low-pass 100%; the notes' settings template is
blank and saving filter presets appears as a proposed feature, not implemented
persistence. [Source/hash audit](review/r244/explorer-settings-audit.json).

A useful separate clue is the default circular mask: diameter 200px, softness
0.20, hence σ=20px and support radius 5σ. Its Gaussian boundary weight is about
0.00037% of the center. This supports the maker's explanation about rapidly
vanishing tails; it does not establish which settings were used interactively.
It is also a substantially tighter Gaussian than σ=R in the current experiment.

**R246 maker clarification:** “basically set the lower bound so the bright
interior spike was removed, then decreased the upper bound so that the three
pairs of peaks were clearly visible.” [Exact preserved account](review/r244/maker-bandpass-method.json).
This is spectrum-led visual selection, not a bead-diameter formula. The present
experiment has **not reproduced that selection procedure** and should not be
presented as a decisive test of the maker's best-tuned direction FFTs. Its broad
bounds and limited perturbations may retain other texture/envelope peaks or miss
a clearer band. The next proposed test is to review a few examples with this
criterion, freeze chosen settings, then transfer them while preserving weak or
ambiguous cases. Do not equate “three clear pairs” with blindly taking the three
strongest candidates or selecting settings for the desired helicity.

## R245: is the finite square crop large enough?

The maker's later clarification prompted a separate support test; it did not
replace R244's frozen extraction. [Support protocol](review/r244/gaussian-support-protocol.json),
[paired example spectra](review/r244/gaussian-support-comparison.png), and
[all results](review/r244/gaussian-support-results.json).

Only A's support grows from ±3σ to ±4σ; σ, channel, location and band stay fixed.
The edge weight falls from at most 1.11% to 0.0335%. For an ideal continuous
circular Gaussian, the weight outside the corresponding square falls from about
0.539% to 0.0127%. This is a support test, **not** a wider Gaussian.

Among 22 accepted photographic channel-windows, adding those tails changes the
complex band spectrum by median 1.49%, maximum 1.97%, evaluated on a common FFT
grid to isolate the tail contribution. Both C4 channels fail the existing
missing-image-support rule at 4σ. The full pipeline's finer FFT-bin grid and
small tail changes together flip three weak preferences (S3 Y, S5 Y, C2 V).
Known-hand control correctness changes from 56→51/64 for V and remains 57/64
for Y; the larger crop has one wrong margin above 0.5 in V, zero in Y.

The tails are a modest spectral perturbation, consistent with the maker's point.
Larger storage alone does not fix ambiguous peak selection. The score changes
cannot be attributed solely to the tails, because the pipeline FFT grid also
changes. No support size was selected by its most favorable hand score, and
these checks add no convincing evidence for a unique photo helicity.

## Review evidence and reproduction

| Straight site | Matched three-method evidence | Curved comparator | Matched three-method evidence |
| --- | --- | --- | --- |
| S1 | [raw/Gaussian/FFT/inverses](review/r244/S1-comparison.png) | C1 | [raw/Gaussian/FFT/inverses](review/r244/C1-comparison.png) |
| S2 | [comparison](review/r244/S2-comparison.png) | C2 | [comparison](review/r244/C2-comparison.png) |
| S3 | [comparison](review/r244/S3-comparison.png) | C3 | [comparison](review/r244/C3-comparison.png) |
| S4 | [comparison](review/r244/S4-comparison.png) | C4 | [failure/comparison](review/r244/C4-comparison.png) |
| S5 | [comparison](review/r244/S5-comparison.png) | C5 | [comparison](review/r244/C5-comparison.png) |
| S6 | [comparison](review/r244/S6-comparison.png) | C6 | [comparison](review/r244/C6-comparison.png) |

All main cards include both Gaussian-windowed channels, marked FFT pairs and
phase-preserving top-three inverse contributions. The top three are illustrative,
not automatically the physical families. [S1 individual pairs](review/r244/S1-individual-pairs.png)
and [C1 individual pairs](review/r244/C1-individual-pairs.png) show each pair for
every method/channel. [Bent phase phantom](review/r244/phase-phantom.png) tests
straightening against an analytic signal, separately from POV-Ray appearance.

Run from the repository root with the saved protocol (do not rerun `prepare`,
which refuses to overwrite the frozen selection):

```bash
.venv/bin/python -m unittest photo2.test_fft_curvature photo2.test_fft_helicity
.venv/bin/python -m photo2.fft_curvature controls
.venv/bin/python -m photo2.fft_curvature photo
.venv/bin/python -m photo2.fft_curvature_report
.venv/bin/python -m photo2.fft_curvature_evidence
.venv/bin/python -m photo2.fft_gaussian_support
```

The inherited R243 control manifest supplies scene/image hashes and POV-Ray
commands. If ignored render files are absent, regenerate them using
`.venv/bin/python -m photo2.fft_helicity_controls render` first. The approximate
curve cache regenerates from the tracked seed. Numeric outputs/caches stay under
ignored `photo2/output/r244`; curated figures/tables are tracked. All source and
artifact hashes, environment and reproduction checks are in
[verification.json](review/r244/verification.json).

Fifteen tests cover pinned-source equivalence, phase, projection, tracking,
straight-map equivalence, curved-signal recovery, constant brightness, fold and
missing-support rejection, one-to-one perturbation matching, Gaussian tails and
elliptical rotation covariance. The new crop/straightening transforms are tested
capabilities; a reliable three-family photographic estimator is still unresolved.

Keep all three tools. Use A as an interpretable baseline, B where the longer
support remains sufficiently straight, and C when its mapping can be checked.
The next concrete task is to review the Gaussian-angle and band-pass illustrations
with S1/C1, then calibrate a small band-selection test using the maker’s visual
criterion and known-geometry controls, freezing choices before transfer. Stop here; no segmentation, channel fusion,
full inventory, global optimization/indexing or repeat recovery is authorized by
this bounded step. Carry forward Astra/High as a recommendation, not a claim of
current model identity. No `/new` is needed for review; consider it before another
implementation task. The user controls session/model changes.
