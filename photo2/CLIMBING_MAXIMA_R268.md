# R268 — climbing local-average brightness

**Climbing improves several candidate coordinates, especially R01284's central
yellow, but does not establish one reliable endpoint per bead.** Nearby starts
can remain at different local maxima on one apparent bead; wider averaging can
also carry a shadowed-neighbor start onto the adjacent bright bead. The guarded
experiment prevents that named crossing, but synthetic weak-start failures remain at 9×9 and without visible neighbor boundaries.
**No production detector, prior result or outline rule was changed.**

[Photographs, tables and traces](review/r268/README.md) ·
[Current selected points: before/after](review/r268/CURRENT_POINTS.md).

## Photographic result

Start with the guarded 7×7 paths from the current supported coordinates:
[R00956](review/r268/R00956-current-selected12-paths7.png) and
[R01284](review/r268/R01284-current-selected12-paths7.png).
White squares are starts, cyan lines show every native step, orange rings are
endpoints. Separate [start cards](review/r268/START_CARDS.md) show **every** starting
coordinate with all three guarded paths and endpoint scores, without dense labels.

The following table uses the old **seed**, which can differ from the displayed
supported coordinate. Positional descriptions are photographic interpretations,
not manually assigned bead identities.

| Apparent location / old seed | Guarded 7×7 endpoint | Mean V before→after | Interpretation |
|---|---|---:|---|
| R00956 upper yellow P090697 (2279,1879) | (2282,1878) | 230.37→241.78 | Moves into the bright patch; still a separate local optimum from other starts |
| R00956 middle yellow P091868 (2275,1903) | (2274,1902) | 235.35→237.18 | Raw-valley guard stops early; higher-scoring alternatives remain |
| R00956 lower yellow P093030 (2262,1926) | (2260,1925) | 232.27→238.16 | Seed stops early; its supported coordinate instead reaches (2254,1924) |
| R01284 central yellow P128915 (983,2675) | (981,2673) | 229.76→241.18 | Old seed and R267's P128672 interior candidate converge |
| R01284 lower yellow P130055 (972,2698) | (972,2696) | 235.76→237.35 | Modest movement within the bright patch |
| R01284 shadowed yellow P129034 (994,2678) | (997,2677) | 156.80→169.80 | Remains separate from the central yellow at this scale |

[Central-yellow comparison](review/r268/R01284-central-yellow-witness.png):
P128915 and P128672 converge to the same point at **all three sizes**:
(981,2674), (981,2673), (980,2671) for 5/7/9. These endpoints are not constrained
to the original raw maxima. This is the clearest useful coordinate consolidation.

[Upper-yellow comparison](review/r268/R00956-upper-yellow-witness.png): P090697
and P090766 end at (2282,1878) and (2286,1878) under mean7, with scores 241.78
and 241.53. Both are genuine local maxima of that surface. Strict ascent cannot
cross even a small intervening mean-score dip, so improving the score does not
necessarily find the best representative of the whole apparent bead.

[Middle-yellow comparison](review/r268/R00956-middle-yellow-witness.png): the
old seed's raw peak is 250 DN. Its mean7 climb reaches a point whose higher-scoring
neighbors include raw values 233/235/234 DN, below the primary raw floor of 238.
The guard blocks them. R267's P091694 start separately reaches (2263,1898), mean
241.22. A guard that blocks an inter-bead valley can also block real within-bead
shading. The 6/12/24-DN controls expose this tradeoff; no setting was optimized.

**Neighbor-failure witness:** [R01284 5/7/9 side-by-side](review/r268/R01284-shadowed-neighbor-witness.png).
Unguarded 9×9 climbing moves P129034 onto the central yellow's endpoint (980,2671).
This is an apparent incorrect combination despite strictly increasing mean V.
Guarded12 stops at (998,2676): the next higher-score pixel has raw V170, below the
185−12=173 floor. Larger windows can average across a separation visible at the
native scale. No endpoints were automatically merged into bead identities.

## Exact experiment

- **Starts:** 242 unique coordinates in R00956 and 209 in R01284, with 3,163 source
  records. This includes every R267 raw maximum pixel, each intersecting plateau's
  original representative, all recorded R266 seed/support coordinates across six
  variants regardless of status, R267 frozen-growth coordinates and final candidate
  coordinates. Duplicate coordinate computations share a start ID; all provenance
  survives. Small/deferred candidates remain in the audit, while separate final
  R267 foreground/size-filtered path views retain the earlier review eligibility.
- **Scores:** whole-photo native square means of HSV V=max(R,G,B), in 0–255 DN.
  Compute exact integer sums over 25/49/81 pixels, then divide. The average is a separate score surface; raw pixels, original maxima and
  growth masks are unchanged. Incomplete image-edge
  windows are invalid; crop edges do not constrain climbing. Saved numerical
  surface crops include every visited pixel, including paths leaving the review box.
- **Steps:** examine eight neighbors and choose the highest strictly greater
  admissible sum; ties choose smallest y then x. Record raw V, H/S, exact sum,
  mean, running raw peak and every rejected higher neighbor with its reasons.
  Local barriers apply to each move; both orthogonal corner routes are checked
  before a diagonal step. There is no watershed or geometric bead model.
- **Equal plateaus:** never move sideways on equality. Inspect the equal-score
  component only to report its canonical label, size and whether a higher exit
  exists farther away. Distinguish a regional plateau maximum from a stop with an
  uphill exit reachable only through prohibited equal steps. The canonical label
  is not a relocated endpoint or a bead assignment.
- **Guards:** primary `guarded12` limits raw V drop from the highest raw V visited
  to 12 DN. Native reliable-color hue steps must stay within 12°, and hue relative
  to the start within 25°; reliable here means S≥.35, V≥.2, S×V≥.08. A saturation
  step above .22 stops when either pixel has V≥.2. Reuse established R266 confident background
  and R267 nearby smooth-paper uncertainty as distinct stop reasons. The latter
  is deferral, not a confident material label. No new background classifier or
  hue range was fitted.
- **Controls:** unguarded strict ascent; raw-valley budgets 6/12/24 with otherwise
  identical guards; and `confident-only12`, omitting the existing paper-uncertainty
  deferral. The initial color guard (requiring both pixels V≥.2) is retained as
  `legacy-color12`. All six variants run at all three sizes: **8,118 photographic traces**.
  A guarded stop can be below a score maximum; it is explicitly labeled as blocked.

## Convergence and limits

At mean7, 23/22 endpoint groups contain multiple original raw plateau IDs in
R00956/R01284. Restricting origins to R267's final foreground/size candidates gives
7/11 multi-candidate groups. These are candidate convergence counts, **not bead
counts or verified duplicate removals**. None of the distinct selected12 IDs
converges with another selected12 ID under guarded climbing at any of the three
sizes; that does not validate all the weaker starting alternatives.

All memberships are in `convergence-review.csv`; equal-score plateau associations
are kept separate from exact-coordinate convergence. Some weak/dark starts still
travel far: the longest guarded mean7 displacement is 29.53px / 77.39px in the
two crops. Such a path can satisfy all local rules without identifying the intended
bead. Every long route is visible in its start card and retains its full trace.
No distance cutoff or manual identity was introduced to conceal these cases.

## Synthetic validation

Run 96 preserved image-generated stress scenes covering multiple highlights,
same/different-color adjacency, uneven shading, gray reflections, placement and
0–3 DN noise. Add four deliberately continuous same-color adjacent regions whose
true internal interface has no visible cue. Starts come from raw regional maxima;
known identities and centers enter **evaluation only**, never climbing or gates.
All synthetic images, truth arrays, conditions and 243,450 traces are saved.

For the 96 stress scenes, each window tests the same **500 body-start maxima**:

| Window | Guarded12 endpoints on another body | Guarded12 endpoints on background |
|---|---:|---:|
| 5×5 | 0 | 0 |
| 7×7 | 0 | 0 |
| 9×9 | 0 | 1 |

At 7×7, unguarded ascent has 13 cross-body and 195 body-to-background endpoints.
The first guard reduced these to 7 and 5, but its saturation check ignored a
transition when the starting pixel was dark. The known failure image showed a
dark neutral start crossing directly into a bright colored neighbor. Checking
saturation when **either** pixel is bright enough removes those failures in the
96-scene 7×7 test: 0 cross-body, 0 background endpoints and 0 mixed-body endpoint
groups. Preserve the first guard and all its photographic paths exactly under
`legacy-color12`; [its cross-body witness](review/r268/synthetic-failure-legacy-cross-body.png)
remains visible. This is an experimental guard repair, not a production change.

One weak start still exits to background at 9×9; its full path and image are saved.
Among 244 starts passing prominence 12, both unguarded and final guarded variants
have zero cross-body/background endpoints at all three scales. The stronger
subset is therefore not evidence that climbing fixes the weaker-start problem.
The same scene/start population is reused across scales, not independent trials.

In the four deliberately unobservable-interface scenes, guarded mean7 crosses
bodies for 13 of 42 body starts. Local brightness ascent cannot infer an absent
identity boundary. [Synthetic failure images and full traces](review/r268/README.md)
include cross-body, background-exit and unobservable-interface witnesses.
Center-distance measurements are saved as diagnostics, not a fitted target or
proof of recovered physical centers.

## Delivery and stopping point

Thirteen numerical tests pass. Independent checks verify every photographic score
against the original pixels, 396 deterministic current-point replays, and all
**360,078 recorded moves** across photo/synthetic runs for strict ascent, native
adjacency and applicable guards, including diagonal barriers. Prior inputs and
production sources remain hash-identical. Native originals and all source/start
inventories are preserved. Reproduction commands are in the evidence index.

**Retain this as a coordinate-refinement experiment; do not change production.**
The next bounded task, only when requested, is to review converged versus competing
foreground endpoints and the weak-start cross-body witnesses before designing a
selection rule. Stop here; no outline, background, geometry or indexing phase.
Keep the user's current model/reasoning; no `/new` is needed for this review.
