# R272 — coverage experiment, including black reflections

**869 proposed measured locations: 207 black, 363 red and 299 yellow. The 80%
photographic recall goal is not demonstrated.** The frozen geographic sample
matches 24/31 apparent bodies with the correct color (77.4%). Two additional
uncertain black bodies would lower that to 24/33 (72.7%). Multiple highlights,
color ambiguity and missing reflections still prevent a verified bead census.

[Open the simple viewer](coverage_inventory_r272/index.html) ·
[Whole photograph](review/r272-coverage/whole-photo.png) ·
[Evidence and reproduction](review/r272-coverage/README.md) ·
[Complete inventory](review/r272-coverage/inventory.json).

This request reuses R272 and supersedes the earlier conservative-subset objective.
The [earlier R272 inventory](TRUSTED_INVENTORY_R272.md), R271's 453 locations,
R259–R271 experiments, historical detectors and viewers remain intact. The new
algorithm runs uniformly on photograph pixels and fixed parameters. It has no
review coordinates, annotated identities, expected count, spatial quotas,
watershed, historical splines, geometry or physical-string indexing inputs.

## Black reflections restored

R259/R260's useful idea is a **first closed dark perimeter around a reflection**,
not recovering the full black body. This experiment implements it on native
pixels without blur. Every raw ICC-luminance maximum is retained for diagnosis;
small reflections bypass all colored broad-brightness, bright-patch-size and
uniform-illumination gates.

The initial native-HSV-Value control accepted only 50 reflection supports.
Value mistakes tinted dark material for relatively bright material, sometimes
connecting the glint to a neighbor. Five controlled alternatives use the same
original maxima and retain exact masks/reasons:

| Black pathway control | Retained supports |
|---|---:|
| Native V, 65% low-chroma dark surround | 50 |
| Native V, Gaussian sigma 0.55, same surround rule | 44 |
| ICC luminance expressed as neutral-gray sRGB, same surround rule | 138 |
| Native V, 50% low-chroma dark surround | 94 |
| **ICC neutral-gray brightness, 50% surround; final** | **207** |

[Distributed additions](review/r272-coverage/black-signal-additions.png) show the
photographic evidence. Blurring was not adopted. Threshold 0.32 is retained on
the encoded neutral-gray scale: `encode(Y)`, with proper sRGB encoding, so it
means linear luminance **0.083535**, not Y=0.32. For dim peaks the threshold is
`min(0.32, 0.60 × peak_encoded_Y)`. Peak must reach 0.22 and exceed the median
perimeter by 0.12 in this same encoded scale. These are explicit engineering
thresholds, not calibrated material probabilities.

Grow the eight-connected above-threshold reflection component and inspect its
one-pixel exterior shell. Every shell pixel must be at or below the dark threshold;
a connection reaching the context boundary is rejected. At least half the shell
must also satisfy native low-chroma evidence: S≤0.45 or channel spread≤0.10.
The peak's corrected S must be≤0.55; no more than 25% of the core may exceed
that saturation. Core and shell must avoid both existing background stop classes.
Retain the four-connected reflection interior, 3–220 native pixels, without
adding the dark shell or filling holes. Save the complete enclosing shell as
independent evidence. All 207 final shells pass the native signal audit.

119 of R260's 136 reflection seeds have a new black peak within six pixels.
That is correspondence, not proof of identity or recall. Some old supports are
still rejected; 207 is not a verified count of physical black beads.

## Colored interiors and individual rule controls

Use R270's ICC-corrected luminance and deterministic 7×7 mean maxima. Search a
16-pixel neighborhood with the unchanged R270 raw24/mean2 neutral-gray-equivalent
valley guards, photographic hue/saturation/background barriers and diagonal-corner
checks. Save 5×5 and 9×9 searches independently. Measurement-window size never
sets search radius. A mean7 candidate reached from a weaker maximum is considered
in its own right; the weaker maximum and route remain recorded.

The new cheap gates are mean7 Y≥0.04, lit fraction≥0.45, ≥6 supported bright
pixels, mean9/mean5≥0.35, local contrast≥0.12 and a background-clear 3×3 core.
**Every measured region pixel must still clear the background map.** Image-derived
circular hue clusters supply red/yellow prototypes. A candidate needs ≥10 reliable
color samples, ≥40% chromatic core pixels, hue-deviation90≤22°, prototype distance
≤16° and a ≥6° margin against the other prototype. The chromatic-core requirement
prevents a nearly neutral black glint borrowing a neighbor's red label. It also
misses some pale colored highlights, explicitly retained as a failure.

On a common final downstream population, restoring all six old R271 cheap gates
retains 399 colored interiors. Relaxing each gate individually gives:

| Only this old gate relaxed | Colored interiors | Additional interiors |
|---|---:|---:|
| Brightness | 474 | 75 |
| Uniform illumination | 500 | 101 |
| Background clearance, 9×9→3×3 | 427 | 28 |
| Local contrast | 400 | 1 |
| Bright-patch size | 399 | 0 |
| Window dilution | 399 | 0 |
| All six targeted relaxations | 662 | 263 |

These are exact post-filter controls on identical downstream candidates, **not a
rerun of R271's 18-way stability and rival rules**. Overlapping failures explain
why the individual increases do not sum to 263. [All IDs and gate failures](review/r272-coverage/gate-ablations.json)
are saved. No expected bead count was used to choose thresholds.

Interior growth uses straight native peak-to-pixel paths, relative hue≤18°,
saturation/color evidence, a luminance floor and irreversible stop after a rise
of >0.02 linear Y above the running minimum. One-pixel erosion retreats from
questionable edges. Try floors 0.32, 0.45, 0.60 and 0.75 of the peak, selecting the
largest bounded surviving support under the declared rules. A broader proposal
that reaches the context edge or exceeds the 870-pixel pre-retreat cap is saved
and retried with a brighter observed interior; no arbitrary clipped or fabricated
pixels are retained. Holes, inadequate interiors and ownership conflicts reject.
This is the largest support under these rules, not an optimum over all possible
bead segmentations or a claim to full-body area.

Overlapping proposals can suppress a duplicate **only when their color and exact
brightest native pixel agree**. Other overlaps withhold both proposals. Disjoint
peaks within six pixels are also withheld. Several separate glints on one black
body can still evade this test; the photo witness is retained rather than counted
as evidence of extra beads.

## Measurements and viewer

Each accepted record includes a stable source-image/pathway/anchor ID, sequential
inventory number, brightest native pixel maximizing ICC luminance within the
measured interior, native and corrected RGB/HSV, the connected ≥85%-peak patch
with centroid/count, exact inclusive mask runs, area centroid/count, color evidence,
confidence measurements, warnings and acceptance reasons. Coordinates are native
pixel centers; neither centroid is called a physical bead center. IDs are stable
for identical image/algorithm inputs, not cross-version resolved physical identity.

The 869 disjoint regions contain 94,977 native pixels; size minimum/median/maximum
is **7 / 82 / 641**. Two cyclic contour-vertex averages create moderately smooth
closed display outlines without changing any measured mask. The viewer sorts on
exact pixel count, with ascending ID tie-breaking in either direction. Selecting
an ID or region centers and zooms it; size/Nth/previous/next, pan/zoom and overlay
visibility are the only navigation controls. Optional excluded-candidate dots
are off initially and show plain-English reasons when clicked. Obvious background
maxima remain in the full diagnostic file, not thousands of default viewer dots.

[Black: smallest](review/r272-coverage/black-smallest.png),
[median](review/r272-coverage/black-median.png),
[largest](review/r272-coverage/black-largest.png) ·
[Red median](review/r272-coverage/red-median.png) ·
[Yellow median](review/r272-coverage/yellow-median.png).

375/453 R271 locations have a new anchor within six pixels. No claim is made that
all 453 qualify for this expanded measurement inventory. Geographic occupancy
is 15/16 fixed full-frame cells, measured afterward without a selection quota.
[R00956](review/r272-coverage/R00956.png) and
[R01284](review/r272-coverage/R01284.png) preserve familiar comparisons. The new
coverage objective permits dimmer proposals, including R01284's previously
withheld shadowed yellow neighbor. It remains a separate support and retains
the user's earlier distrust as review evidence; no coordinate override was used.

## Recall, false positives and remaining obstacles

Eight geographic photo contexts were selected from the unmarked overview before
new detections; one is a paper-only control. A single assistant reviewed the
unmarked photographs and froze 31 apparent body annotations plus two possible
additional black bodies. Matching uses evaluation-only envelopes, not detector
inputs or pixel truth. These are deliberately distributed samples, **not random
sampling, independent human adjudication or a held-out parameter-tuning test**.

| Color | Correctly matched / frozen visible bodies | Sample recall | Automated mismatch flags / associated proposals |
|---|---:|---:|---:|
| Black | 6/9 | 66.7% | 4/10 |
| Red | 7/8 | 87.5% | 2/9 |
| Yellow | 11/14 | 78.6% | 0/11 |
| Total | 24/31 | 77.4% | 6/30 |

The flags require interpretation. Three black peaks belong to real bodies whose
centers fall outside the counting frame while their reflections enter it; they
are **boundary-association errors, not established false beads**. Excluding those
leaves 0–1 possible duplicate among seven in-sample black proposals (0–14.3%
possible false discovery). Two red/color-ownership disagreements remain unresolved
(0–2/9, up to22.2%). Yellow has no flagged false proposal in this small sample;
that is not proof of zero false positives. Frozen annotations and the explicit
later boundary interpretation are both saved; no labels were silently changed.
[Multiple-glint witness](review/r272-coverage/failure-multiple-glints.png),
[color/ownership witness](review/r272-coverage/failure-color-ownership.png), and
[dim-yellow miss](review/r272-coverage/failure-dim-yellow.png) show the limitations.

| Known synthetic set | Black recall | Red recall | Yellow recall | False detections / duplicate extras / foreign mask pixels |
|---|---:|---:|---:|---:|
| 52 new scenes, 96 labeled bodies | 28/32 (87.5%) | 28/32 (87.5%) | 32/32 (100%) | 0 / 0 / 0 |
| 112 unchanged R270 scenes, 101 in-scope bodies | 32/32 (100%) | 15/24 (62.5%) | 29/45 (64.4%) | 0 / 0 / 0 |

New scenes test black/red/yellow neighbors, touching bodies, colored highlights,
multiple glints, uneven lighting, dim exposure, cast shadows and background.
The denominator includes four black bodies deliberately lacking reflections;
these are all missed. Earlier scenes expose difficult pale highlights and
intentionally invisible interfaces. Their other palette colors are outside the
requested taxonomy; falsely labeling those red/yellow/black still counts as an
error. Truth is withheld until after detection in both sets. Results are not
combined into a flattering aggregate that conceals the colored-highlight failures.

A whole-photograph visible-bead denominator remains unmeasured. Neither the 869
proposals nor their ratio to R271 estimates it. The sampled visible count is31–33,
and the corresponding matched fraction72.7–77.4%; boundary/class ambiguities add
uncertainty. Reliable whole-photo recall and acceptably low photographic false
positives therefore remain unproven. Main obstacles are distinct glints on one
body, white highlights with weak local color, ambiguous dark perimeters and
shadowed partial interiors. Those cases remain available for diagnosis.

## Verification and stopping point

23 Python tests pass (11 new, 12 preserved inventory tests), including nonempty
black/colored paths, bypass of the prohibited black gates, absent-reflection and
paper-shadow rejection, touching ownership, multiple highlights, exact centroids,
counts, classification, determinism and no merging from overlap alone. Native
validation checks all869 records and207 dark shells, all163,066 raw-luminance
maximum plateaus and40,483 mean7 plateaus, plus309 preserved evidence hashes.
All excluded candidates and reasons survive. The initial native-V pilot is saved.

31 checks execute the actual viewer JavaScript under a Node DOM/canvas stub.
**Real Chromium validation was skipped after a sandbox launch failure**, because
it would require new approval and the user instructed us to skip such actions.
The reproducible browser test remains available; rendered layout is not certified.
[Skipped-action record](review/r272-coverage/skipped-actions.json).

The saved budget records 23.4 minutes through final evidence and
validation, within the30-minute experiment allowance. No production detector,
old viewer, geometry or string indexing changed. Commit and push this bounded
experiment, then stop. Next task, only if requested: independently adjudicate
reflection identities and pale-highlight color failures, and run the saved real
browser check when authorized. Keep the current model/reasoning; no `/new` is
needed for photograph review.
