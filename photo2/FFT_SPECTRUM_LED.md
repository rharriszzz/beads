# Spectrum-led photographic FFT development — R248

**Subsequent R249:** the user authorized a provisional freeze and six-site
transfer, now [completed and reported](FFT_TRANSFER.md). This R248 report retains
its development-stage evidence and historical stopping point.

**First implementation milestone completed; stop for illustrated development
review before freezing or transfer.** Circular Gaussian width and the meaning of
the central spike materially affect the result. There are plausible reciprocal
trios in individual windows, with useful examples in both channels. This does
not yet establish consistent physical directions 1/6/7 across the necklace.

The user approved the [R247 proposal](FFT_SPECTRUM_LED_PLAN.md) with “ok, please
proceed.” During this experiment the maker answered **“Keep the side lobes”** to
the illustrated central-spike question. That clarification is now part of the
method: remove the DC-centered spike, without demanding that nearby bright
noncentral structure disappear. The maker did not specify an exact numeric
cutoff. [Question and answer](review/r248/maker-clarification.json).

The maker subsequently clarified that the aim is **three or four bright
noncentral peak pairs**, and an upper cutoff may be unnecessary. This is the
current primary development comparison: the same lower exclusions and widths,
no upper rejection, highlight the brightest three qualified pairs plus a fourth
alternative. The earlier annulus replay remains an optional comparison, not a
required step. [Exact clarification](review/r248/bright-pairs-clarification.json),
[comparison protocol](review/r248/shortlist-protocol.json), and
[no-upper measurements](review/r248/no-upper-measurements.json).

The current views are [D1](review/r248/D1-no-upper.png),
[D2](review/r248/D2-no-upper.png), and [D3](review/r248/D3-no-upper.png).
Brightness here means peak-bin |F|², not integrated lobe power or the source's
log-power sum. Qualification still excludes DC and artificial mask-rim maxima;
three or four peaks are not forced when fewer qualify. Larger sets of alternatives
remain in the data. A bright pair can represent a harmonic, appearance variation
or the rope outline rather than an independent bead direction.

Removing the upper cut preserves the same brightest three qualified pairs in
**23/24 cases** and the same brightest four in **19/24**, comparing conjugate
identities rather than arbitrary signs. This supports making upper rejection
optional at these locations. It is agreement between two settings, not an
accuracy score. D1 sigma20 Y is the top-three exception: two qualified pairs
inside the provisional annulus become a longer shortlist without the outer cut.
The [inverse mapping](review/r248/no-upper-comparison.json) reuses individual
two-bin inverse panels when their coefficients are unchanged and supplies new
cards for added pairs. All no-upper ranks, frequencies and strengths are in
[a separate CSV](review/r248/no-upper-peaks.csv).

Start with the [three raw locations](review/r248/raw-crops.png),
[channel examples](review/r248/channel-examples.png), and
[current versus superseded central cut](review/r248/central-ambiguity.png).
[Two review questions](FFT_SPECTRUM_LED_REVIEW.md) define the stopping point.

## What ran and what was reused

Three locations were selected from raw context and existing centerline geometry,
before new spectra: D1, a nearly straight yellow/black-rich section; D2, a straight
red-rich section; D3, a gently curved mixed section. All contain appearance
variation. Their coordinates, tangents, curvature measures, selection reasons,
six reserved locations and input hashes are in [sampling.json](review/r248/sampling.json).
[Location map](review/r248/locations.png). These are diagnostic coordinates from
a previously studied photograph, not automatic runtime selection or blind data.
**The six reserved locations were not evaluated.**

The pinned explorer numerical code in [fft_explorer_core.py](fft_explorer_core.py)
provides V=maxRGB, Y=.299R+.587G+.114B, the Gaussian, native complex FFT and
conjugate-pair proposals. [R243 inverse-pair code](fft_helicity.py) preserves the
complex phases. R248 adds the recorded spectrum-led sweeps, artifact rejection,
reciprocal alternatives and review figures. Source functionality and these new
experimental qualifications remain distinct. No helicity score or model fit is
used to choose locations, widths, cutoffs, peaks or examples.

Circular sigma20/30/40/55 native pixels gives 24 channel/width/location cases.
Support radius is 5σ, stored in a square array, with no flat rectangular interior.
The Gaussian is exp(−r²/(2σ²)), clipped at r=5σ; weight at that boundary is about
0.00000373. All source support is inside the photograph. Integer-centered native
crops have no rotation, resampling, padding, mean subtraction, normalization,
straightening or channel fusion. Tangent-relative angles are computed afterward.
The historical startup sigma20 is a tested candidate, not a known maker setting.

## Band-pass and selection trail

For centered frequency coordinates in cycles/native pixel, the filter retains
complex coefficients satisfying **lower < sqrt(fx²+fy²) ≤ upper**, setting the
others to zero. It changes neither phase nor magnitude inside the annulus.
There is no smooth frequency taper here; a hard edge can cause spatial ringing.
The explorer's percentage equals `100 × sqrt(2) × frequency` on these square
grids: .015/.060 corresponds to about 2.12%/8.49%. This is unrelated to the saved
8% background-scanner setting or `hp_removed` statistic.

The lower sequence is 0/.005/.010/.015/.020/.025/.030/.040, with no upper rejection.
After recording visual lower choices, the upper sequence is .7071/.25/.15/.10/
.08/.06/.05/.04/.03; empty bands are marked. These grids are a bounded replay of
the maker's procedure, not bands derived from bead diameter. The FFTs and profiles
guided the choices. V and Y get the same grid and refinement allowance.

Spectral displays are fixed: amplitude |F|/sum(G), shown as 20log10, with a full
view at −80..0dB and a detail view at −60..−20dB. This scaling affects display
only. It is **not a reproduction of an unknown interactive contrast setting**.
Radial profiles show mean power per bin in each ring, not shell-summed power.
Shrinking the band reduces outer clutter but cannot sharpen a retained lobe.

The first interpretation removed the entire bright merged feature in several
small windows. The maker's side-lobe clarification corrected that interpretation.
Seven channel cases received a recorded lower-cutoff refinement: D1 sigma20 V/Y,
D2 sigma20 V, and D3 sigma20/30 V/Y. Their former bounds remain in
[first-pass decisions](review/r248/first-pass/band-decisions.json), with the
original measurements and search trace. Current
[lower decisions](review/r248/lower-decisions.json) and
[band decisions](review/r248/band-decisions.json) preserve the rationale.
Upper bounds were held fixed for that controlled comparison and their full
sweeps replayed; they are provisional review bounds, not a uniquely selected
three-family band or a frozen procedure.

For D3 sigma20, lowering the inner radius from .040 to .020 preserves a feature
near .032–.033 cycles/pixel that the aggressive cut removed. At .040 all three
displayed candidates had clipped lobe neighborhoods. At .020 V has three
candidates, one clipped; Y has four, two clipped. The apparent count of three
under the aggressive cut was therefore poor evidence. The retained broad
central/side structure remains uncertain, as the maker's answer requires.

All channel-selected bands are cross-applied to the other channel in
[cross-applied-bands.json](review/r248/cross-applied-bands.json); the remaining
different choice, D2 sigma55, is [illustrated](review/r248/cross-applied.png).
The first-pass D2 sigma20 V/Y difference is preserved in its earlier numeric
record. Current D2 sigma20 uses identical bounds. There is no global V/Y winner.

## Candidates, geometry and uncertainty

The source peak finder forces an origin entry and can fall back to weaker peaks.
R248 excludes DC, rechecks pair separation, requires power prominence ≥3 against
a local annular median, and rejects a filtered maximum if it is not a maximum in
the unfiltered 3×3 neighborhood. This prevents cutting a smooth central lobe
into false peaks on the mask rim. Up to eight qualified alternatives are kept;
the cap is a review limit, not evidence that further peaks do not exist.

The window's frequency-resolution scale is δf=1/(2πσ): .00796/.00531/.00398/.00289
cycles/pixel for the four widths. Angular bars use atan(δf/f). These are blur
scales, **not statistical confidence intervals**; they do not include centerline,
projection, appearance, overlapping-lobe or assignment errors. A lobe is flagged
as potentially clipped within 1.25δf of either cutoff. Pair strengths integrate
|F|² within that radius around both conjugates and are divided by total retained
band power. Nearby neighborhoods can overlap; fractions need not partition power.
The explorer's `log_power_sum` is retained separately, not called physical power.

FFT coordinates use x right/y up. Angles are axial modulo180°, relative to the
saved x-right/y-up centerline tangent. A reciprocal vector is perpendicular to
its constant-phase spatial bands. Neither its angle nor its frequency is directly
a bead-neighbor direction or distance.

Two **provisional local A/B/C examples**, selected for explanation after the
cutoff sweeps, are useful:

| Example | Reciprocal offsets in FFT bins | Frequencies (cycles/pixel) | Tangent-relative reciprocal angles |
| --- | --- | --- | --- |
| D1 sigma30 V, candidates1/2/3 | (5,6), (9,−6), (−4,13) | .02595, .03594, .04519 | −53.4°, +42.7°, +3.5° |
| D2 sigma20 Y, candidates1/2/3 | (6,−4), (−9,−3), (3,7) | .03588, .04720, .03789 | −47.5°, +4.6°, +53.0° |

D1 has k2+k3≈k1, with one-bin residual (.00332 cycles/pixel). D2 has
k1+k2+k3=0 at bin precision. Both pass the deliberately loose √3δf closure
screen. For independent reciprocal columns B, the direct columns A=B⁻ᵀ satisfy
BᵀA=I. Example D1 basis k2/k3 gives direct lengths44.0/35.0px and relative angles
−86.5°/−47.3°; D2 basis k1/k3 gives28.3/26.8px and −37.0°/+42.5°. A third row
family can follow a direct sum/difference. Alternative signs, basis choices and
other qualifying trios are retained in [measurements](review/r248/measurements.json).
Those lengths are possible direct translations, not established nearest-neighbor
distances or a verified primitive cell. Accidental closure becomes easy when
many peaks and broad uncertainties are available.

The [individual D1 V inverses](review/r248/D1-s30-V.png) show diagonal rows and
near-transverse bands crossing several yellow bodies. The
[D2 Y inverses](review/r248/D2-s20-Y.png) show two diagonal arrangements and a
near-transverse family across the red/black region. This supports inspecting
them as possible row families, but some positive crests follow reflections;
neither brightness maxima nor phase crests are bead-center measurements.
V/Y differ in relative contrast and whether those lobes qualify as separate
maxima. The [matched-band examples](review/r248/channel-examples.png) explicitly
mark the reference channel's bins in both channels, including bins that do not
qualify in the other channel. Reconstructing chosen coefficients cannot itself
prove those choices correct.

For D1 sigma30 V, this proposed trio remains among candidates at upper .10/.08/
.06/.05; .05 clips its outer lobe. Increasing lower .015→.020 clips its inner
lobe. D2 sigma20 Y retains its proposed trio at upper .10/.08/.06; .05 clips one.
These are local cutoff checks, not evidence of transfer. Larger sigma does not
uniformly help: sigma55 separates more substructure and low-frequency competitors.
Smaller sigma can merge the desired structure with DC. Physical labels1/6/7,
harmonic alternatives and photographic helicity remain unresolved.

## Evidence and reproduction

The [decision table and full figure index](review/r248/INDEX.md) links every raw/
Gaussian/marked FFT/individual inverse card and every lower/upper sweep.
[Peak CSV](review/r248/peaks.csv) records frequency radii, angles, powers,
uncertainty scales, clipping and unassigned physical labels.
[Search trace](review/r248/search-trace.json) retains all408 cutoff states,
including empty bands; [direction plot](review/r248/direction-candidates.png)
shows all candidates at the three development arc distances, without inventing
tracks between widely separated sites. No global consistency or detection
accuracy is inferred from this small development set.

Known mirror-hand [render truth and source hashes](review/r243/controls-manifest.json)
and [projection/reciprocal checks](test_fft_helicity.py) remain available. R248
also tests three known waves and their mirror for signed closure, direct-basis
inversion and exact inverse phase. The waves are mathematical controls, not
rendered bead evidence. No new render sweep or photographic helicity comparison
ran. Unknown camera projection still prevents attaching unwrapped model angles
directly to these photo peaks.

Reproduce from tracked decisions with Python3.12, repository root:

```bash
.venv/bin/python -m photo2.fft_spectrum_led initial
.venv/bin/python -m photo2.fft_spectrum_led upper
.venv/bin/python -m photo2.fft_spectrum_led_evidence
.venv/bin/python -m photo2.fft_spectrum_led_evidence focus
.venv/bin/python -m photo2.fft_spectrum_led_evidence shortlist
.venv/bin/python -m unittest photo2.test_fft_spectrum_led photo2.test_fft_helicity
```

`prepare` is only for initial location declaration and refuses to overwrite the
saved sampling file. The commands above regenerate evidence; they do not redo
manual choices or run reserved sites. First-pass JSON is immutable provenance.
[Verification](review/r248/verification.json) records input/code hashes,
numerical replay, representative figure reproduction and the twelve passing
source/phase/geometry/artifact tests.

**Next task:** review the preserved side lobes and the two proposed A/B/C examples,
using the maker's latest brightest3/4, optional-upper interpretation; then decide
whether the visual rules are clear enough to freeze. No freeze,
transfer, full inventory, segmentation, indexing, pattern recovery or helicity
comparison follows automatically. Recommend Astra/High for the geometric review,
without asserting the active model. No `/new` needed for this review; read this
report and current handoff if starting a fresh session.
