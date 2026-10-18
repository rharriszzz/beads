# R318 — conditional reflection minimax, Stage 1 only

**Stage 1 does not achieve excellent agreement. No expansion or reconstruction adoption.**
The primary objective throughout is the exact maximum Euclidean observed–predicted
reflection displacement. All 22 observations remain in each fitting epoch; all
2405 rigid bodies remain in camera visibility, common-light shadows and contact.
No silhouette/coverage score replaces or contributes to the fitting objective.

[Compact review](r318/results/index.html) · [Full summary](r318/results/summary.json) ·
[Verification](r318/results/verification.json) · [Protocol](R318_SPECIFICATION.md)

## Direct answers

1. **Stage 1 contains 22 interior photographed reflection candidates**, with automatic
   pigment cues {'yellow': 4, 'black': 7, 'red': 11}. They occupy a compact photo-selected patch across
   a longer physical-address interval containing hidden and unmeasured bodies.
   Bead identities are explicitly provisional, one-to-one within each epoch.
2. **Localization:** intensity-weighted centroid of the brightest connected
   half-maximum component. Observed intensities are linearized minimum RGB,
   an achromatic reflection proxy; predicted intensities are the shared physical
   specular model. Both use the same connected-component rule, threshold and
   weighted-centroid calculation. Components never average across disconnected
   lobes. Peak and unweighted centroid alternatives, 40/50/60% threshold controls,
   saturated pixels, tied peaks and competing lobes are retained. This chooses
   a stable connected bright region rather than an arbitrary saturated pixel;
   it is not a claim of calibrated radiometry or proof every bright patch is
   pure front-surface reflection. The method is fixed before fitting.
3. **Emax before and after:** see both fixed-map epochs below. Their differing
   starting values are correspondence-only effects, not geometric progress.
4. **Worst displacement in diameter units:** best conditional epoch has
   11.995px = 0.358 of the fixed
   photographic diameter estimate (33.468px). Maximum error
   divided by each bead's fixed baseline model diameter is
   0.368; the baseline modeled
   median diameter is 32.567px. The conservative photo-scale
   reference is 21.659px. Diameter normalization is frozen
   and cannot improve just by making fitted beads larger.
   The fitted model median diameter is 32.207px;
   the largest individual error/fitted-model-diameter ratio is
   0.372. Both fixed and fitted scales are exposed.
5. **Worst bead:** auto-0063, conditional index 58, observed
   [1696.712583557614, 317.0880843086571], predicted [1700.3044926246732, 328.53290323380077], error 11.995px.
   Its photographic localization uncertainty estimate is
   3.346px. The vector and competing geometric
   assignments are retained. Its error is not removed or silently reassigned.
   In the camera-isolation diagnostic its error is
   11.995px, and the current
   full scene assigns the observed point to body
   52. Thus the
   remaining mismatch cannot be explained simply by hiding the principal
   predicted reflection; body placement/correspondence remains consequential.
6. **Limitation:** residual geometry/common-illumination/correspondence coupling
   remains unresolved. The magnitude exceeds the photo-only localization
   stability scale; that does not uniquely identify the physical cause.
   Different provisional maps give different optima. A single shared surface
   specular BRDF omits glass refraction, color-dependent diffuse contamination,
   and complex illumination. No unique causal attribution is established.
7. **Expansion justified? No.** Merely crossing below half a diameter is not
   excellent alignment. The predeclared excellent-agreement target was <=0.2
   diameter, with localization and sampling controls. It is not met.
8. **100 and several hundred beads:** not fitted. Stage 1's original observations
   and the full necklace remain preserved; time passing did not trigger expansion.
9. **Specific obstruction:** a common light and coherent rigid geometry still
   leave competing worst reflections displaced by a substantial fraction of a
   bead width. The fixed-map objectives cannot independently shift those points.
   The retained correspondence alternative changes the objective with identical
   geometry, demonstrating that assignment uncertainty is also material.

## Exact conditional objectives

| Frozen epoch | Beads | Before Emax px | After Emax px | After RMS px | Median px | After Emax / photo D | Missing |
|---|---:|---:|---:|---:|---:|---:|---:|
| stage1-epoch1 | 22 | 17.992 | 13.505 | 10.306 | 11.467 | 0.404 | 0 |
| stage1-epoch2-basin | 22 | 16.376 | 11.995 | 9.399 | 9.874 | 0.358 | 0 |

All 22 correspondences in each epoch remain provisional; this is a usable
conditional fit, not an empty reliable cohort. Missing predicted lobes would
make the exact maximum infinite; search penalties never become reported success.
The displayed conditional winner is stage1-epoch2-basin; it is not a verified
physical indexing solution. Total serialized evaluations: 9666.
The chosen epoch has 4 observed components with
tied maximum pixels and 8 with
localization uncertainty estimates above 2px. These remain in the maximum;
uncertainties are conservative localization indicators, not calibrated confidence
intervals. There is no ground-truth accuracy ranking of centroid versus peak.

Half-pixel controls are separate numerical diagnostics, not refits or changed
measurements. The chosen epoch has half-pixel Emax
12.074px,
with maximum native-to-half-pixel predicted-centroid shift
0.179px.
Every per-bead shift, including the larger lobe switch in epoch 1, is retained
in its half-pixel file. Principal lobes are never selectively changed to improve
a score.

| Epoch | Half-pixel Emax px | Largest centroid shift px | Missing |
|---|---:|---:|---:|
| stage1-epoch1 | 14.280 | 9.557 | 0 |
| stage1-epoch2-basin | 12.074 | 0.179 | 0 |

## Automatic evidence and correspondence controls

The native original photograph is the only source of observed intensities.
An automatic pigment/dark-material mask, closing and small-hole filling define
the rope silhouette. Candidates require >=11px inward distance from that
silhouette, not distance from the image boundary. A compact set of 22 stable
interior components is chosen within inherited −100…99 geographical context
before any optical predictions. The image-only choice is not the patch with
the lowest modeled residual. All 1217 detected candidate
observations are retained; 1195 are outside the selected cohort,
including 7 in the patch with stated
photo-only exclusion reasons. These counts concern detected observations, not
a claimed inventory of every physical photographed bead. The address inventory
explicitly marks unmeasured/hidden slots rather than giving them zero error.

Epoch 1 assigns observed bright supports by visible model-body overlap and freezes
the map. Epoch 2 instead maximizes one-to-one overlap of full automatic
photographic luminance basins with visible body footprints. Its map is selected
without predicted reflection distances. Both retain all 22 observations and the
same localization rule. The unchanged-original-geometry control changes
Emax 17.992→16.376px
through 6 correspondence changes alone;
**none of that difference is geometric fitting progress**. The transferred
geometry control is separately saved. Alternative assignments remain visible.

## Diameter, optics and limits

The automatic photographic diameter estimate is an equivalent-area diameter of
luminance watershed basins inside the rope mask. Its quartiles and all individual
areas are saved; these are uncertain visible supports, not manually annotated
complete contours. The modeled diameter uses analytic projected solid support
over 181 directions. Reported pixel Emax remains primary; uncertain normalization
cannot turn an unconvincing fit into success.

One shared light source and one shared half-vector specular BRDF
predict the visible front-surface intensity. The complete necklace casts camera
occlusions and light shadows. One identical rigid legacy glass shape is retained
per setting; shared thickness, pose, camera, phase and small smooth station/phase/
orientation fields are coupled. There are no independent bead translations,
independent lights or relocated predicted points. Additional compact radial
orientation probes in the followup use this same reflection objective; this
is not a separate radial-tilt campaign. Numerical
parameter and smoothness bounds are exploration bounds, not crochet mechanics.
R312 exact camera reuse accelerates light-only controls; native ray grids and
the original full-chain support checks are retained. No new speedup claim.

Directional, finite-point and extended-directional illumination are explicitly
compared at fixed geometry and frozen correspondence. Zero inverse distance is
included in each finite-source grid; extended-source controls use one shared
square angular source and the inherited quadrature. No per-bead light is fitted.

| Epoch | Shared light hypothesis | Controls | Parent Emax px | Best control Emax px |
|---|---|---:|---:|---:|
| epoch1 | finite | 45 | 13.507 | 13.507 |
| epoch1 | extended | 27 | 13.505 | 13.585 |
| epoch2 | finite | 45 | 12.002 | 12.002 |
| epoch2 | extended | 27 | 11.996 | 12.027 |

These bounded tests do not rule out other lighting or glass optics. The final
parameters identify the selected light exactly; no rejected illumination control
is silently substituted in the displacement ledger.

## Verification and delivery

Independent verification reconstructs observed components directly from native
RGB pixels, checks the frozen cohort/map hashes, recomputes each Euclidean error
and maximum, checks every full-chain separating-plane witness with an independent
support formula, and compares sampled original Python camera/shadow rays.
Half-pixel principal-component controls, all failures, source snapshots and raw
photo crops are retained. These checks establish numerical reproducibility,
not correct physical identity or photographic truth.

Start 2026-10-18 01:38:55 UTC; scientific cutoff 02:02:55 UTC; hard deadline
02:08:55 UTC. See the delivery receipt for actual cutoff and verified commit.
**Stop for scientific review. No automatic R319, color-pattern inference or
beads.pov edits. Keep the current session/model; no /new is needed.**
