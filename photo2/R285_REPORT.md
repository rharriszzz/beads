# R285 — brightness-driven supports and Method J regression review

[Open the visual review](review/r285/index.html). Start with e01–e05, e07 and
unseen v04. Each case starts with raw/J/S; expand for original A, all alternatives,
exact native supports, gains/losses, brightness routes, centroid and centerline.
Six edge/shadow/material-interface disagreements are retained separately and
lower priority, following the user's latest instruction. No production inventory
or later-phase reconstruction changed.

**Recommendation:** retain J as the primary colored-support candidate. Its
brightness-profile interpretation is substantially better than shape pruning in
the approved yellow example. Compare it with **S**, the diffuse-intensity plus
persistent-saddle correction, especially on clear red interiors. S is the strongest
new direction, but a clear yellow confirmation failure prevents blanket adoption.
For black photographic reflections, use **R2 as the experimental default**, with
R1 reference and R4 retained when separate nearby highlights compete. These are
recommendations for review, not production changes. T is not recommended.

## Why the intended dark stopping weakened

[The pre-implementation diagnosis](R285_DIAGNOSIS.md) traces the change precisely.
R265 stopped straight native paths at darkness; later connected material domains
could route around a trench. R282–R284A imposed peak floors, fixed radii,
opening/erosion and shape checks without establishing an intensity saddle.
R284B T further privileged thickness. J restored intensity-contour growth, but
its peak-relative threshold truncates diffuse red under strong specular peaks;
its background ring depends on A, and weak thresholds can connect neighboring
material. The old connected-component helper can substitute a nearby component
when the cue is excluded. These are support-generation issues, not line styling.

The permanent [Phase1 contract](PHASE1_MEASUREMENTS.md) now explicitly makes
brightness/color and contextual dark transitions primary. Narrow material is not
invalid simply because it is narrow. Shadow/edge disagreements may be disregarded
for this round's reliable-interior objective; they remain documented rather than
being silently converted into successes. Clear-body failures remain important.

## Frozen comparison and distinct improvements

All seven R284B colored methods were rerun on the same203 photographic cues:
**1421 masks replay exactly**. The16 review examples comprise four mandatory
observations plus12 automatic disagreement/improvement selections, with spatial
and color/source-strength strata. The first extreme-only ranking overselected bad
shadow cues; its JSON and the reason for improving the selection are preserved.
No review coordinates or judgments enter inference. Ten confirmation anchors
(eight colored, two black) were hash-selected >180px from development crops and
one another. Method and selection hashes were frozen before opening their results.

| Method | Mathematical change | What the photographs show |
|---|---|---|
| A | Preserved compact/morphological baseline | Useful reference, sometimes already leaks or clips; not truth |
| J | Unchanged wide-domain local contrast isophote | Strong yellow results; peak-driven red truncation; some connections |
| D | J-like isophote anchored to diffuse60 pigment intensity and local dark baseline, not peak/A ring | Restores diffuse red but widely joins neighbors; failed ownership alternative |
| S | D plus watershed intensity features; merge weakly separated maxima, separate only sustained dark saddles | Best new clear-interior results; some real connection and material failures remain |
| G | Harmonic image-conductance ownership from S's bright cores and competing/background evidence | Often measures only the highlight; failed colored-interior alternative |

D/S/G use sigma0.65 noise smoothing, a20% diffuse-contrast floor, learned hue
prototypes and contextual pigment/background exclusion. S compares the **highest
connecting saddle**, not the darkest selected point, with65% of the weaker local
diffuse reference and requires at least3 interface pairs. Multiple maxima alone
never establish multiple beads: weakly separated basins merge. Full interfaces,
references, merges and separations are saved. G uses beta90 and potential0.55;
its graph potential is not a calibrated ownership probability. The solver emitted
range-tolerance warnings, another reason not to promote it.

No opening, erosion or compactness score selects new supports. Native masks are
separate from plotting contours. A97px computation window and a65px rerun expose
domain sensitivity; contact is uncertainty, never a photographic boundary.
The previously authorized870px ceiling is an abstention guard, not a shape goal.
No thresholds were tuned after confirmation.

## Principal photographic findings

| Reviewed feature | A px | J px | S px | Assessment |
|---|---:|---:|---:|---|
| e01 lower yellow | 516 | 439 | 540 | S stops the neighboring connection without thickness pruning |
| e02 left red crossing line | 537 | 200 | 495 | S restores substantial diffuse red that J cuts away |
| e03 right yellow | 490 | 499 | 614 | J already plausible; S adds a dimmer rim, not automatically an improvement |
| e04 approved yellow profile | 355 | 405 | 446 | J/S follow the intensity structure; D joins the left neighbor |
| e05 automatically selected clear red | 648 | 278 | 583 | S restores red and removes A's left lobe; dark lower extension remains doubtful |
| e07 visible yellow pair | 280 | 439 | 320 | J includes upper-neighbor material; S separates it |

All four mandatory S supports are identical at32/48px domains. All three two-sided
observations remain separately represented: lower yellow is support-near on the
positive side; left red and right yellow have measured crossing evidence. G loses
the lower yellow's support-near status by shrinking it. These are photographic
support facts, not a certification of all physical beads at that station.

The remaining cases explicitly distinguish old-mask disagreement from regression.
e08/e12 lose some old bright material because A included a neighbor; they are not
automatically J failures. e15/e16 show plausible J gains. e06/e09/e10/e11/e13/e14
are peripheral uncertain/shadow/interface cases and receive no tuning priority.
Each panel states its selection reason and interpretation; exact gained/lost pixels
are available in diagnostics and the native overlays.

Unseen confirmation is decisive. **v01/v02** restore clear red interiors under S;
v03 isolates a yellow neighbor. **v04** joins several clear yellow beads under S
(1817px, domain-sensitive) while J remains confined (511px): a real failure outside
the shadow/edge exception. v05 follows wrong material at margins, v06 retains a
lateral yellow connection, v07 retains a dark tendril. Fresh v08 separates a
lower-neighbor contribution that J includes. These failures are preserved and no
post-confirmation patch was made.

## Quantitative limits, coverage and ownership

All observations remain important and unrated; none receives newly certified
photographic/physical reliability. The full bank includes weak/shadow cues, so its
counts are an audit rather than the optimization target.

| All203 fixed colored cues | A | J | D | S | G |
|---|---:|---:|---:|---:|---:|
| Nonempty within870px | 203 | 179 | 72 | 142 | 192 |
| Support-near, within cap | 70 | 69 | 22 | 61 | 56 |
| Measured crossings, within cap | 36 | 31 | 13 | 43 | 27 |
| Overlapping proposal pairs, all masks | 89 | 117 | 374 | 167 | 48 |
|32/48 domain-sensitive | n/a | n/a | 141 | 82 | 30 |
|97px window contact | n/a | n/a | 120 | 64 | 11 |

The saved runner has zero placeholders for new-window diagnostics on old controls;
interpret them as **not evaluated**, not zero old clipping. The separate historical
contact audit finds **89 J radius-contact cases**. Larger domains alone are no fix.
All nonempty new supports have one connected component, which does not prove
single-body ownership. Overlap pairs can be duplicate cues, shared material or
leakage; these are not independently labeled real errors.

The74 old-high-source cues are a more relevant engineering stratum, still not
truth. J has73 within-cap supports,34 near and12 measured crossings; S has64,31
and19. Thus S improves crossing evidence in some locations but does **not** improve
every coverage measure. J has5 opposite-side pairs and6 groups with at least3
near observations within24px longitudinal position; S has1 and6. Groups are
photo-observation diagnostics, not verified distinct-body counts or quotas.

In the10 prioritized review cases, J and S both retain10 within-cap supports and
8 near/5 crossing observations. Median centroid shifts from A are2.58px and2.35px.
Median boundary gradients are0.0514 and0.0464 linear-Y/pixel. G's larger0.0576
comes from cutting near bright highlights: maximizing gradient alone would choose
the wrong objective. Boundary inside/outside intensity contrast and J-relative
retained/lost intensity are saved separately. They describe pixels, not calibrated
accuracy. S's own saddle-conflict diagnostic is explicitly not independent truth.

Eight colored confirmation anchors yield J8 within-cap/7 near/5 crossing and
S7/7/6. The two fresh mean3 maxima are retained with provenance, but are not
certified new beads: existing observations may refer to the same bodies. Every
visible crossing bead remains the goal; completeness and real distinct-body
precision/recall remain **unknown**. A black reflection cannot certify full-body
crossing, and compact colored supports can understate it.

## Separate black-reflection decision

Compared46 unchanged photographic cues plus2 frozen confirmation anchors.

| Reflection metric | R1 | R2 | R4 |
|---|---:|---:|---:|
| Nonempty native features | 48 | 47 | 47 |
| Median contour turn energy | .0456 | .0212 | .0450 |
| Median centroid shift from old A, px | .805 | .774 | .837 |
| Median perturbation-mask IoU | .957 | 1.000 | .945 |
| Brighter-neighbor flags | 1 | 0 | 0 |

R2 is smoother and appropriately localized in the reviewed upper reflection:
32native pixels, versus41 for R1/R4. The lower secondary remains a separate
15px R2 reflection (25px R1/R4), with no shared native pixels with the upper one.
No physical ownership is assigned. The red-right neighbor is displayed separately.
R2's single empty weak/material-ambiguous cue remains unresolved, not silently
replaced or counted as a bead. R4 retains an alternative when feature competition
matters; it may introduce a basin edge, so smooth appearance alone is insufficient.
Native intensities, thresholds, peaks, perturbations and subpixel isophote residuals
are preserved independently of contours. No speculative dark body is measured.

## Mechanism controls and independently rendered confirmation

Controlled intensity fields show S retains a narrow bright connection and shallow
shading, but separates a deep valley. A fourth control deliberately gives identical
pixels a same-body/deep-texture interpretation: S splits it too. This exposes an
unobservable identity ambiguity; a dark valley alone cannot always certify bodies.

Four fresh POV-Ray scenes (seed285501), including same-color neighbors and varied
specularity, were rendered independently. Detector inputs are pixels/automatic
cues only; inference was saved before rendering/opening identity truth.44 colored
cues are compared identically. At95% single-body purity, A/J/D/S/G have30/28/21/27/35
pure within-cap proposals; distinct recovered eligible bodies21/17/10/15/20 out
of69. Duplicate pure proposals9/11/11/12/15 remain. G's tiny interiors can look
pure while losing material, so these figures do not override photographic failure.
Synthetic results do not establish a superior whole-body detector, real precision,
or complete recovery. All source scenes, identity rasters and failures survive.

## Verification, unresolved work and stopping point

74 scientific tests pass, including15 new R285 checks and59 historical checks.
The first test attempt exposed incomplete shared fields in the new black-record
adapter; the adapter now uses/validates the shared schema. The test had also raced
an older output during regeneration; final verification ran after it completed.
No measurement algorithm changed. Preservation audit confirms10036 historical blobs unchanged (one explicit
permanent-contract exception),30 exact native crops and2 exact rerun files.
Chromium checks128 images,25 tables,30 sections and local links at desktop/600px.
Native crop/hash/replay and rendered browser results are recorded in `r285/results/audit.json` and `browser-check.json`.
[Reproduction instructions](r285/README.md) list commands and saved intermediates.

Recommend the brightness principle, diffuse-vs-specular distinction, contextual
saddle evidence, strict seed provenance and explicit domain uncertainty for the
next selected implementation. Do not adopt S wholesale, maximize counts, or restore
T. Material gates, ambiguous same-color connections and false partitioning remain
unresolved. After the user's choice, the next bounded task is to combine the
chosen J/S rules and test clear-material connection failures with independently
frozen confirmation before proposing an inventory replacement.

**Stop for user review now.** No production replacement, Phase2 fit or Phase3
search is authorized by this delivery. Keep current model/reasoning; no `/new`
needed. The user controls any session/model change.
