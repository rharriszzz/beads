# R305 — 1,041-position graphical inspection

[Open the viewer](review/r305/index.html), or run `photo2/review/r305/launch.sh`.
The viewer starts at −40. Stepping genuinely recenters on the projected bead
center at unchanged zoom; Follow can be disabled for panning. Graph points,
category examples and the [17-image gallery](review/r305/index.html#gallery)
link back to bead navigation. Presets A/B/C provide vectors only, visible
boundaries only, or both. The raw photograph remains beside the enabled layers.

**The extended primary has fluctuating photographic errors and remains physically
invalid in its earlier sections.** Small reflection residuals do not establish
correct bead boundaries or physical identities. The new 330…1000 interval has
substantial material disagreement, local error jumps and recoveries, but no
new demonstrated penetrating pair involving those displayed positions.
No model or diagnostic control is adopted.

## Starting red beads: what the evidence actually supports

The following comparisons use unchanged R283 image-only colored interiors and
native first-hit ownership. Their conditional assignments come from the selected
global alignment. These are conservative automatic interiors, **not complete
photographic bead contours**. All masks, alternative owners and uncovered pixels
are retained in [starting-red-diagnosis.json](r305/results/starting-red-diagnosis.json).

| Primary observation / index | Assigned visible surface | Another owner | Outside union | Reflection error |
|---|---:|---:|---:|---:|
| [C-1130-0364 / 0](review/r305/diagnostic-02.png) | 96.6% | 3.4% | 0.0% | 2.65 px |
| [C-1116-0328 / −1](review/r305/diagnostic-01.png) | 99.7% | 0.0% | 0.3% | 2.36 px |
| [E9-1088-0322 / −8](review/r305/diagnostic-03.png) | 99.5% | 0.2% | 0.2% | 0.64 px |
| [C-1497-0271 / 103](review/r305/diagnostic-04.png) | 37.4% | 54.7% | 7.9% | 12.53 px |

The stronger boundary test is the existing **uncertain B15 outer polygon** near
index −1. Of its 540 native pixels, 500 (92.6%) belong to the assigned surface,
38 to other modeled beads and 2 to no resolved surface. Thirty-nine pixels
(7.2%) miss even the unobstructed assigned bead; neighbor occlusion is not the
main cause. One pixel has unresolved camera intersection and is reported
separately, rather than attributed to a neighboring body. Observed-contour to
visible-boundary distance has median 1.71 px, maximum 5 px. Eroding/dilating the
uncertain polygon by three pixel steps gives **99.7%/76.0%** assigned coverage;
these are sensitivity controls, not confidence limits. [Full contour comparison](r305/results/B15-contour-diagnosis.json).

At index 0, twelve of 351 saved red-interior pixels miss the assigned bead even
without occlusion. At crossing index 103, 246 of 393 miss it without occlusion.
Thus an incorrect shape/pose/projection or conditional owner can explain these
misses without invoking neighbor masking. At the starting point, the full
outer red margins remain insufficiently measured to quantify the entire visual
mismatch. The raw/enlarged images expose those margins; high interior coverage
must not be mistaken for a correct silhouette.

**Why can the highlight fit while the body does not?** A highlight constrains
one illuminated surface-normal neighborhood under the shared light. It is not
the bead center, body extent or silhouette. The fixed axial shape, tilt,
phase and camera can position that small neighborhood correctly while placing
other material on the wrong side of the visible boundary. These observations
do not uniquely isolate dimensions versus orientation, phase or projection.
The S1 owner is inherited, not independently verified. The hand− comparison
is especially cautionary: its inherited C-1116 owner is −3, whose visible
surface covers only 4.3% of the B15 polygon, with 63.0% hidden by modeled
neighbors. Feasible contacts alone do not establish photographic ownership.

The historical R294 zero is the red crossing at (1499.36,271.20), now near
primary **103**. It is never used as a new phase origin.

## First deterioration: the splice contributes, but is not the whole cause

The primary preserves the original circle within four radius units, transitions
with the original quintic, and reaches the photographic reference by twelve.
That is approximately indices 17…52. Curvature peaks at **0.06266/radius near
index 31**, versus the original circle's magnitude 0.00451/radius. There are
nine demonstrated penetrating pairs in the early 0…100 contact neighborhood.
This is a construction artifact capable of changing body frames and packing.
It is not evidence that the actual necklace construction has impossible packing.
See the [splice image](review/r305/diagnostic-05.png).

One prespecified diagnostic spreads the same quintic over 4…24 radius units,
with unchanged fitted parameters and **unchanged reflection owners**. It lowers
the early curvature peak to 0.03841/radius and early demonstrated penetrating
pairs from nine to seven, but strong-pair RMS at indices 30…79 worsens from
**13.61 to 15.04 px** (six pairs). At 80…100 it worsens from 14.06 to 17.07 px.
It is not substituted into the primary. [Control records](r305/results/transition-control.json).

Consequently the artificial splice contributes to early geometric failure, but
this control does not show that removing its curvature peak repairs the optical
mismatch. The image trace is an uncertain rope-axis proxy, and continuing the
local phase/shape/camera can disagree with the photograph after that transition.
There is no spacing discontinuity or phase reset: the maximum chord-versus-
arclength deficit per step is 0.00000202 radius. The 30…79 count here is by
paired **bead index**; R304's geographic-bin count was seven, so its 13.84 px
summary is not the identical cohort.

## Errors fluctuate, jump and recover

All 316 original-coordinate candidates remain: 105 strong and 211 weak/diffuse
or uncertain. Primary has 40 confident-conditional pairs, 267 ambiguous pairs
and 9 unmatched observations; 65 owners change under gap costs 12/24/48 px.
All 106 previous R304 primary assignments are unchanged. The selected alignment
is global and ordered outside the pinned S1 anchors. Competing owners are shown
separately; the no-gap ordinal control is retained. Low errors after allowing
skips cannot prove stable physical indexing or exclude a whole-turn slip.

Primary paired-strong RMS is **10.39 px** (103 pairs), calibrated hand+ 9.79 px
(102), hand− 12.86 px (95). These compare different conditional owner paths,
not independent measurements of geometric truth. The primary descriptive
magnitude slope is only +0.30 px per 100 indices and signed tangent slope
−0.009 px per 100. Neither represents a verified pitch-error accumulation rate.

| Primary indices | Strong pairs | RMS px | Colored omission | Main concern |
|---|---:|---:|---:|---|
| 160…209 | 7 | 3.72 | 4.1% | Earlier recovery, useful comparison |
| 310…359 | 3 | 15.32 | 29.7% | Large signed displacement, sparse evidence |
| 360…409 | 7 | 7.76 | 36.3% | 12.9% of paper samples occupied |
| 560…609 | 4 | 12.71 | 40.7% | Along-curve mismatch near the file seam |
| 710…759 | 4 | 5.03 | 37.6% | Optical recovery without material recovery |
| 760…809 | 7 | 6.11 | 41.2% | Largest grouped colored omission |
| 810…859 | 5 | 15.23 | 38.8% | Abrupt tangent shift; eight sensitive assignments |
| 860…909 | 4 | 6.89 | 30.8% | Recovery again |
| 910…959 | 4 | 15.30 | 23.2% | Renewed optical error; eight sensitive assignments |

The most informative new failures are [831](review/r305/diagnostic-09.png)
(19.37 px, almost entirely tangent), [941](review/r305/diagnostic-08.png)
(20.84 px, almost entirely normal), and [760](review/r305/diagnostic-11.png)
(low optical error with poor material coverage). They suggest different local
mechanisms, rather than one uniform pitch drift. The largest strong residual
overall remains [274](review/r305/diagnostic-17.png), 25.66 px.

[Interactive magnitude/signed graph](review/r305/index.html#errors),
[magnitude PNG](review/r305/primary-errors-index.png),
[signed PNG](review/r305/primary-signed-errors.png),
[CSV](r305/results/primary-errors.csv),
[50-position groups](r305/results/primary-groups.csv) and
[ranked intervals](r305/results/problem-intervals.json) retain individual points,
counts, raw values, sparse-evidence flags and abrupt changes. Rolling median/RMS
and segment means are optional in the viewer, descriptive only. Local signed
slopes are particularly unstable with three or four observations.

## Geometry, numerical integrity and the three families

Each family has 1,041 displayed bodies and 64 guards per end (1,169 total).
The original camera, dimensions, light, phase, advance and registration are
unchanged. The original photographic trace is closed; the new construction
unwraps that trace across its storage seam, near primary index 574. It never
extrapolates beyond the closed trace or resets phase. Original spline evaluation
is retained in its old domain. The seam position mismatch is below 3.2×10⁻¹⁴
radius and tangent mismatch below 4.6×10⁻¹⁰. Stations advance monotonically;
there is no detected branch jump or seam interpolation instability. Following
the chosen trace does not certify that trace as the physical rope axis.

All old R304 centers, phases, core owner pixels and core intensities replay
**exactly**. Native first-hit boundaries include holes and neighbor occlusion.
All spatially close body pairs are audited, including nonadjacent indices.

| Family | All audited close pairs | Uncertified / penetrating, including guards | Uncertified / penetrating touching −40…1000 |
|---|---:|---:|---:|
| Primary hand+ | 3493 | 39 / 37 | 29 / 27 |
| Hand− | 3493 | 0 / 0 | 0 / 0 |
| Calibrated hand+ | 3493 | 9 / 8 | 6 / 5 |

Primary has 25 penetrating pairs with **both** members displayed, plus two
crossing the left requested endpoint. Its ten additional penetrating pairs
are wholly in guards at 1022…1061. Calibrated's three additional failures are
also beyond 1000. No new penetrating pairs were found at 330…1000. The hand−
family certifies all 1,169 bodies, minimum separating margin **0.121301 radius**;
the 96-guard audit also certifies it. Neither finite audit certifies a complete
necklace. Failed/inconclusive witnesses and every body remain saved.

Increasing guards from 64 to 96 changes **zero requested-body owner pixels,
intensities or unknown-ray flags**. The enclosing rectangle additionally shows
2,522 primary / 2,073 calibrated changed pixels belonging only to newly added
far guards, addresses 1066…1093; these are context changes, not requested-body
convergence failures. Native/half-pixel centroid differences have median/max
0.089/2.097 px primary, 0.199/2.343 hand−, 0.095/2.062 calibrated. Lobe presence
changes in 7/5/8 marginal cases respectively. These numerical effects are saved
per bead and are much smaller than the principal 15–26 px residuals.

The streamed kernel evaluates only conservative projected-sphere candidates
inside 24,000-pixel chunks; empty background does not invoke the surface/shadow
kernel. Forward exports plus guards took **43.49 s**, analysis 16.22 s, the
final diagnosis pass about 4 s, and complete successful verification **92.45 s**.
Peak process RSS was about **613 MiB** in forward generation and **587 MiB** in
verification. Graphics, browser tests and development/rebuild passes are
separate. One full numerical replay completed before its preservation check
caught an output-directory error; its log is retained. The overwritten R304
viewer files were restored from their pre-work Git bytes, and the corrected
full replay verifies **17,057 historical files unchanged** before the additive
R305 handoff; all prior handoff text is preserved byte-for-byte. Initial nullable-
support and group-accounting failures are retained as implementation evidence.
No parameter optimization was performed.

## Categories and next questions

Primary totals are 9 unmatched observed candidates, 351 unassigned predicted
lobes, 380 visible beads with no predicted lobe, and 3 occluded beads. These
are different denominators: an incomplete catalog does not establish that an
unassigned real reflection is absent. Missing lobes and occluded bodies are
never plotted as zero error. Ambiguity is optical/assignment uncertainty;
penetration is a physical failure. The viewer gives definitions and clickable
examples for each group of 50 positions. Hand− reaches a shorter photographic
extent: 32 of its 33 unmatched candidates lie beyond it and are explicitly
outside its group counts, rather than assigned to an invented endpoint bead.

The most useful next geometric questions, recorded without starting further work:

1. Can independent dimensions and better observed outer contours separate axial
   shape/orientation from highlight-driven placement near S1?
2. What physical axis and transport rule can replace the artificial splice while
   maintaining contact clearance and the observed material envelope?
3. Can independently identified neighboring reflections constrain phase/pitch
   through 760…859 and 910…959 without relying on alignment skips?

Seven scientific contracts, full native/contact replay and Chromium navigation,
owner picking, graph interaction, raw-pixel invariance, desktop/narrow/offline
and actual-launcher checks are recorded in `r305/results/`. Windows dispatch was
mocked; an actual Windows browser opening is not claimed. **Stop for maker
review. No further optimization, FFT, pattern inference or Phase 3.**
