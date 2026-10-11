# R250 — Dense FFT tracking, four angle fits and conditional helicity cues

**The photograph repeatedly exhibits reciprocal-angle concentrations near −46°,
−19°, +6° and +53°.** The near-zero feature is the most persistent principal
feature. The three main concentrations recur much more consistently than any
single uninterrupted set of three track identities. Brightness ranks change
frequently; some spectral maxima drift between categories. The −19° category
contains multiple frequency bands and remains unresolved.

[Four-angle distribution](review/r250/angle-distribution.png) ·
[least-squares fits along the necklace](review/r250/four-angle-fits.png) ·
[V tracks](review/r250/V-tracks.png) · [Y tracks](review/r250/Y-tracks.png) ·
[complete evidence/data index](review/r250/INDEX.md).

The maker identifies the near-zero signed offset and the diagonal departures
from ±45° as helicity cues, and points out the intrinsic 6/7 asymmetry. Applying
that **conditional family interpretation**, the existing projected reciprocal
model favors source `h=+1` in both channels. This is stronger directional evidence
than R249, but not a unique calibrated hand determination. The unresolved −19°
category is excluded from that comparison, not discarded from the measurements.

## Four prevalent ranges and least-squares results

| Empirical angle range | V fitted angle | V residual RMS | Y fitted angle | Y residual RMS | Window coverage V / Y |
| --- | ---: | ---: | ---: | ---: | ---: |
| −68.5° to −29.5° | **−45.68°** | 5.95° | **−46.66°** | 5.14° | 81.1% / 93.6% |
| −29.5° to −7.5° | **−19.43°** | 4.37° | **−18.55°** | 4.18° | 25.1% / 30.1% |
| −7.5° to +19.5° | **+6.14°** | 4.20° | **+5.63°** | 3.56° | 67.5% / 96.3% |
| +38.5° to +76.5° | **+53.46°** | 6.56° | **+53.40°** | 5.43° | 57.9% / 79.4% |

These are **FFT reciprocal-vector angles**, modulo 180°, relative to the image
centerline tangent. They are not direct bead-to-bead angles. Constant-phase
spatial bands are perpendicular. Positive image angles use x right, y up;
image-array y is negated. Reversing traversal adds 180° and does not change axial
relative angles; mirroring the photograph does change their sign.

The user requested fits for four prevalent ranges during execution. Categories
were discovered afterward from the photographic distribution, without changing
extraction or tracking: brightest four, nonweak and nonclipped candidates; broad
candidates retained. Give each channel/window equal total weight across its
eligible candidates. A periodic 1° histogram, smoothed with sigma 3° only for
range discovery, identifies local maxima separated by at least 15°. Rank them
by mass within ±10°, retain four, and place bounds at neighboring pooled minima.
Minor modes near +30°/±90° and other tails remain unassigned. No peak is moved.

For each range/channel fit the constant minimizing
`sum w_i (theta_i - mu)^2`: `mu = sum(w_i theta_i)/sum(w_i)`. These intervals do
not cross the axial seam. Fits use **original unsmoothed angles**, not histogram
values or interpolated tracks. Multiple candidates in one range remain separate
observations. Bounds and fit are exploratory, not independent validation data.
RMS is residual spread, not uncertainty of the mean or a noise estimate.

A first-harmonic least-squares alternative versus arc distance, with a shared
constant plus sine/cosine, changes the three principal means very little.
Contiguous eight-block validation with a 300-pixel training embargo gives worse
RMS for every principal range/channel than the constant model. The −19° Y range
has only a small improvement, 4.24°→4.18°. Thus the data support relatively fixed
angular concentrations with **local variation**, not a useful single sinusoidal
trend around the necklace. This does not rule out higher-order projection effects
or local physical/appearance changes. Excluding broad peaks changes each fitted
mean by less than 0.7°. Spatial-block resampling intervals are recorded, but do
not include centerline, projection, range-selection or family-assignment bias.

## Full-loop sampling and unchanged extraction

The existing seed-based periodic spline is regenerated with its original fitting
settings, then represented by the existing periodic arc-parameterized curve.
Its approximate image length is **9,235.59 native pixels**. Samples store position,
arc distance, tangent and signed curvature from spline derivatives. This is the
existing approximate centerline, not a newly calibrated bead-row reference.
[Whole-photograph overview](review/r250/centerline.png).

Started at N=200 (46.18px spacing, 9.54s), expanded to N=1000 (9.24px spacing,
36.10s for 800 new locations), then N=2000 (**4.62px spacing**, 44.35s for 1000 new
locations). N=500 is a nested subset. The final 2000-site fresh replay took 87.55s.
All 4000 V/Y cases have full five-sigma image support; all retain eight qualified
alternatives, producing **32,000 original observations**, half in top-four
shortlists. These counts are candidate counts, not numbers of physical families.

Reuse R249 primary: circular sigma 30 native pixels in a 301×301 square storage
array; radius cutoff `2/(2*pi*30) = .0106103 cycles/pixel`; **no upper rejection**.
Same Gaussian, native RGB channels and peak qualification everywhere. The fast
adapter shares crop/channel conversion and frequency grids, computes the source
complex FFT path including its complex64 return, and omits unused GUI displays.
Original source masks, peak finder, qualification and reciprocal closure code
are reused. Exact parity with R249 is tested. Image decoding occurs once per
scan; measured sites are cached by input/geometry/scanner fingerprint.

Preserve image/tangent-relative angles, FFT-bin/native frequency radii, peak-bin
power, Gaussian-normalized peak power, integrated pair power, filtered-band
fraction, rank, prominence, weak/clipped flags and original rejected proposals.
A local log-power Hessian supplies a **diagnostic broadness** flag: nonconcave,
or inferred major amplitude width above twice the Gaussian Fourier width.
It does not alter extraction or claim statistical confidence. Frozen resolution
is .005305 cycles/pixel; discrete FFT-bin spacing is .003322 cycles/pixel.

## Association, gaps and density validation

Three methods were considered: nearest-neighbor matching, a competing-link graph,
and predictive motion models. Use the graph. For adjacent windows compare axial
frequency vectors in the tangent frame, taking the smaller distance between
`k_next` and either sign of `k_previous`, normalized by their combined Gaussian
resolution. All links with normalized distance ≤1 are retained. Accept only a
mutual nearest neighbor separated from either competing assignment by ≥.25.
**Rank, intensity and physical-family predictions never enter that cost.**

Accepted edges define track fragments. All eligible competing edges remain in
the associations table, and unresolved endpoints have ambiguity flags. A missing
or ambiguous association terminates the measured fragment. Endpoints with no
eligible adjacent continuation can propose reappearance within 60px using the
same vector gate; retain all proposals and their uniqueness flags, but **never
merge fragments or interpolate observations across those gaps**. Weak candidates
and ranks 5–8 can maintain a track even when absent from the brightest four.

The seam is treated like every adjacent pair. All eight candidates in each
channel have accepted links across s=0, but **no track closes uninterrupted around
the entire loop**. This separates a successful local seam match from proof of
whole-loop identity. Controlled tests verify seam-origin invariance, axial
89°↔−89° wrapping, rank inversions, measured changing-intensity waves,
disappearances/reappearances, ambiguous crossings and missing measurements.

From N=1000 to N=2000, **98.64% V / 98.96% Y** of accepted coarse links retain the
same endpoints through the measured intermediate point. Two V and one Y links
reach a different identity; 92 V / 73 Y paths reveal a break. N=200→1000 agreement
is only 87.75% / 90.43%. Use 2000 as the final diagnostic density; 1000 already
captures most associations. More points would mostly oversample the same Gaussian
support. The normalized weight overlap for a 4.62px displacement is about .994;
these are emphatically not 2000 independent measurements.

Association sensitivity uses the same observations: gates .8/1.2, margins .1/.4,
and original-image rather than tangent-frame vectors. Each changes fewer than
0.3% of accepted edges; longest tracks are unchanged. This tests local association
choices, not the physical identity of a continuously moving spectral maximum.

## Continuity, local changes and missing structure

| Measurement | V | Y |
| --- | ---: | ---: |
| Accepted adjacent links | 14,698 | 14,951 |
| All track fragments, including single observations/extras | 1,302 | 1,049 |
| Persistent prevalent fragments¹ | 79 | 79 |
| Longest measured fragment | 1,695px | 4,627px |
| Accepted steps that change brightness rank | 28.4% | 23.1% |
| Rank-1 steps continuing at another rank | 121 | 112 |
| Tentative reappearance proposals / unique proposals | 611 / 373 | 437 / 281 |
| Windows supporting an R249 primary reciprocal trio | 36.6% | 69.3% |
| Longest continuation of the same supported trio | 125px | 614px |

¹ At least 150px measured span and in the top four at least 25% of its observations.
No fragment or category is automatically a physical family. All fragments are
exported; plots highlight the longest prevalent twelve and show others in gray.

The near-zero Y0001 feature runs from s≈2932 to7559, usually around +5.6° and
.0443 cycles/pixel. Its 5th–95th ranges are −0.6°..+10.9° and .0416.. .0476, with
about **3.9-fold** 95th/5th normalized-power variation. Its frequency corresponds
to a spatial period around22.6px; that is a band period, not bead diameter. V's
longest near-zero feature has about3.8-fold power variation. A negative diagonal
Y0004 persists1127px near−47.1°; a positive diagonal Y0009 persists688px near53.7°.
Their shorter continuity should not be hidden by assigning every observation to
one of three globally smooth lines.

Typical accepted adjacent angle changes have central90% ranges about−2.46..+1.97°
(V) and−2.36..+1.74° (Y). Frequencies usually change by less than .002 cycles/pixel.
About42% of accepted links retain exactly the same FFT bin. The sawtooth angle
traces partly arise because an unchanged image FFT bin is corrected by a smoothly
changing tangent, then the measured maximum moves to a neighboring bin. This is
quantization plus geometry, not evidence that all fluctuations are random noise.

There are larger coherent changes. V0012 crosses a broad angular range while
satisfying local association gates; Y0002 migrates from a higher frequency toward
the near-zero branch. A continuous maximum can blend appearance-driven and lattice
contributions. Those cases are retained as limitations of feature identity, not
silently split into a tidier physical interpretation. Conversely, fragmentation
can come from a peak leaving the eight-candidate cap or failing qualification,
not necessarily disappearance of the underlying spatial structure.

Of accepted links, 8,000 V and 5,598 Y involve at least one weak observation:
the tracker can continue through reduced strength. About 75% V / 80% Y of all
fragment ends occur at ranks 5–8, so counts of all fragments exaggerate breaks
in the principal bright features. No uncaptured ninth peak is invented to bridge
them. At identical centers, 6,501 cross-channel matches involve top-four peaks in
both channels (out of 8,000 top-four observations per channel). Across all accepted
V/Y candidate matches, median angle/frequency differences are zero, with central
90% differences about −4.3..+4.1° and −.0021..+.0033 cycles/pixel. Agreement in these
shared-image channels is useful but not independent confirmation.

The common negative/near-zero/positive categories have typical frequencies near
.032–.035 / .045 / .032–.035 cycles/pixel. The **−19° category contains separate
bands near .035–.04 and .065–.075**, approximately a factor of two apart. Harmonic
or mixed-component explanations are plausible; neither is established here.
[Frequency graph by angle category](review/r250/four-range-frequencies.png).

## Curvature, appearance and the black-bead hypothesis

Supported-trio prevalence drops from the lowest to highest curvature quartile:
**43.2%→26.8% V**, **81.2%→52.6% Y**. Curvature is associated with difficulty, but
not a sufficient explanation. Within persistent fragments, frequency versus
absolute curvature has weak descriptive correlations, about−.07 V/−.03 Y.
Different families, local projection and appearance remain confounded.

Within-fragment log-power correlates positively with the yellow-image proxy
(.21 V/.36 Y), negatively with the dark proxy (−.16/−.33), and less strongly with
red/highlight proxies. These are Gaussian-weighted image fractions, not bead
inventories: paper can enter the red proxy, dark red/shadows enter the dark proxy,
and bright black reflections need not be dark. No runtime color selection or
color-normalization change is made from these associations.

The maker proposes that black-bead appearance explains most discontinuities.
A targeted check compares top-four fragment endpoint rates with the existing
`V<.2` dark fraction and its absolute arc derivative, using60/120/240px bins and
curvature adjustment. At120px, darkness versus endpoints has rho **+.06 V/−.01 Y**;
curvature has **+.25/+.33**. Adding darkness and its gradient to a curvature-only
linear model changes in-sample R² from .139→.149 V and .132→.172 Y. Other bin widths
also fail to show a consistent positive darkness–break relationship.

Thus this **simple darkness proxy does not establish that black beads explain
most breaks**. It also does not disprove the hypothesis: black-body/highlight
contrast and changing specular structure are poorly represented by one dark-area
fraction. Power does weaken with darker appearance while angle tracking can
survive. A controlled appearance ablation is better suited to causal attribution.
[Darkness check](review/r250/darkness-discontinuities.png),
[events and appearance/curvature context](review/r250/events-context.png).
All correlations are descriptive; no independent-window significance claims.

## Helicity cues and the intrinsic 6/7 asymmetry

The maker's near-zero and diagonal cues are now explicitly preserved. Unwrapped
physical direction angles cannot be compared directly to FFT peaks. The existing
model uses direct basis A=[v1 v6] and reciprocal B=A^(-T), with normals to rows
1,6,7 given by b2,b1,b1−b2. This retains unequal6/7 advances/angles.

For the overhead visible-front approximation at the nominal outer radius:

| Source winding | Negative diagonal FFT angle | Near-zero FFT angle | Positive diagonal FFT angle |
| --- | ---: | ---: | ---: |
| h=+1 | −42.00° | +4.29° | +46.41° |
| h=−1 | −46.41° | −4.29° | +42.00° |

The measured offsets from −45°,0°, +45° are **−.68,+6.14,+8.46° V** and
**−1.66,+5.63,+8.40° Y**. The positive near-zero and positive-diagonal cues favor
h+ under this mapping; the negative diagonal alone resembles the opposite hand's
overhead angle more closely. The correct comparison is joint projected geometry,
not demanding equal offsets or explaining every asymmetry as camera error.
[Signed-offset graph](review/r250/helicity-angle-cues.png).

A conditional least-squares comparison reuses `fft_helicity.predicted` on200
regularly spaced original windows, with both hands sharing the same finite bank:
elevation45/65/85/90°, roll0/45/90/135°, radius4/6.11, phase−25/0/25°. Nuisance
settings are shared across all locations per hand/channel; no local tuning.
Near-zero is hypothesized to be the normal to family1, diagonals are assigned by
sign; each available category/window has equal weight. Missing categories remain
missing. No −19° candidate is substituted.

| Conditional RMS angular residual | V h+ / h− | Y h+ / h− |
| --- | ---: | ---: |
| Near-zero cue alone | 4.26° / 10.58° | 3.51° / 9.75° |
| Three principal cues together | 6.06° / 9.81° | 5.23° / 9.11° |
| Three cues, allowing a common ±5° systematic angle bias | 5.91° / 6.85° | 5.16° / 6.07° |

**h+ is preferred throughout these tested comparisons.** Source h+ means the
`beads.pov` winding convention, not an undefined photographic “left/right” label.
This finite, unrolled, orthographic local model is not calibrated to the camera,
visible surface or bead-center row normals. The angle ranges were identified on
this same image; source/tangent/projection and appearance biases remain. The common
bias test narrows the separation substantially. These RMS differences are not
likelihood ratios or a confidence level, and do not establish a unique hand.
No indexing, repeating-pattern reconstruction or global bead optimization ran.

## Selected transitions and audit trail

The six [raw/weighted/FFT/inverse cards](review/r250/INDEX.md) are explanatory
post-extraction selections, not additional development or retuning:

1. **s≈4170:** a turning region with yellow/red/black and prominent reflections;
   V0012's accepted branch changes angular category. Local continuity alone does
   not prove the same geometric rows.
2. **s≈7619:** mixed red/black/yellow; V emphasizes a broad central competitor;
   Y shows cleaner separated lobes while a tracked branch changes frequency.
3. **s≈1810:** an actual accepted Y rank inversion. The saved edge identifies
   the same frequency feature before/after the brightness change.
4. **s≈480:** a competing V association amid moving highlight/color contributions;
   identity remains unresolved.
5. **s≈9162→9189:** a similar Y peak reappears after27.7px. The original endpoints
   and intervening crop are shown; the gap link remains tentative.
6. **s≈3957:** maximum spline curvature; changing projected rows and highlights
   contribute several structures. The raw comparison prevents treating all of
   them as a single clean three-family lattice.

All observations have stable `channel:index:rank` IDs, original FFT offsets and
ranks. `candidates.csv`, `windows.csv`, `associations.csv`, `events.csv`,
`angle-range-observations.csv` and compressed original records permit tracing
any graph point/model residual back to source measurements. Gap proposals and
fits occupy separate fields/files; no synthetic observation fills a gap.

## Reproduction, validation and stopping point

```bash
.venv/bin/python -m photo2.fft_dense 200
.venv/bin/python -m photo2.fft_dense 1000
.venv/bin/python -m photo2.fft_dense 2000
.venv/bin/python -m photo2.fft_dense_analysis
.venv/bin/python -m photo2.fft_dense_angles
MPLCONFIGDIR=/tmp/beads-matplotlib .venv/bin/python -m photo2.fft_dense_evidence
MPLCONFIGDIR=/tmp/beads-matplotlib .venv/bin/python -m photo2.fft_dense_hand_cue
MPLCONFIGDIR=/tmp/beads-matplotlib .venv/bin/python -m photo2.fft_dense_darkness
.venv/bin/python -m unittest photo2.test_fft_dense photo2.test_fft_transfer photo2.test_fft_spectrum_led photo2.test_fft_helicity
```

Twenty-five tests pass, including actual measured changing-intensity waves,
R249 extraction parity, disappearance/ambiguity/seam behavior, least-squares
minimum and reciprocal hand sign/asymmetry. A fresh full scan exactly reproduced
all4000 cases. Source hashes, protocol, original timings, final reproduction and
artifact checks are in [verification](review/r250/verification.json). R249 frozen
code/data, source photo, spline seed and scene remain unchanged. The final scanner
adds cache fingerprinting; early ignored exploratory caches remain preserved.
Before final analysis, ambiguity flags were clarified, same-fragment gap proposals
retained, and consistent-trio runs audited without changing measured peaks or
association thresholds. None changes the fitted angle conclusions.

**Recommended next bounded task:** controlled appearance and projection
calibration using the same known geometry in both helicities, comparing uniform
beads against red/yellow/black and controlled reflection changes. Apply this
same dense extractor/tracker and signed-angle fit to distinguish black-bead
appearance effects from geometric discontinuities and quantify systematic
helicity-cue bias. This follows the dense evidence without requiring another
round of individual photographic-window review or a bead inventory.

Stop after delivery and review; no next experiment starts automatically.
Recommend Astra/High for that calibration without asserting the active model.
No `/new` needed for reviewing the figures; a fresh session is reasonable before
separately authorized implementation. User controls model/session switching.


## R251 — Maker’s caution about the proposed synthetic test

> "A controlled comparison with identical geometry and changing bead appearance" is easy to do by modifying beads.pov, however the background material and the lighting and the absolute circles instead of splines may make this test a bit less meaningful

This cautions that changing bead appearance within beads.pov is straightforward,
but background material, lighting and circular rather than spline-shaped geometry
may limit the test’s relevance to the actual photograph. It does not establish
how large those effects are or authorize a new test design. Preserve these
limitations when considering the calibration proposed above.

The user requests committing this comment, then waiting. No new experiment or
scene modification accompanies this documentation update. Await further instruction.
