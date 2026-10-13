# R271 — a conservative set of trusted location proposals

The review now shows **an original photograph beside the same photograph with
one cyan dot per accepted location**. There are no paths, ranks, candidate IDs or
outlines on the photographs. Exclusions have separate orange-dot photographs and
plain-English captions.

Start with [R00956](review/r271/R00956-trusted.png),
[R01284](review/r271/R01284-trusted.png), and the
[whole photograph](review/r271/whole-photo-trusted.png).
[All geographic areas and excluded examples](review/r271/README.md) are available
at larger scale.

**The goal is a widespread reliable subset, not every bead.** The isolated
experiment applies one automatic rule to the entire photograph. It proposes
453 locations across 15 of 16 fixed image areas. No area quota, target count,
review coordinate or manually assigned bead identity enters acceptance.
These are image locations for review, not verified physical bead centers or a
claim that all 453 are correct. Production detection and region growth remain
unchanged; geometry, indexing and the viewer were not touched.

## The shadowed neighbor

[R01284's shadowed neighbor is excluded](review/r271/R01284-excluded-shadowed-neighbor.png).
It remains a real, separate bead in the review record. Its mean relative luminance
is **0.149**, below the same **0.25** threshold applied everywhere. This exclusion
happens before search, without a coordinate exception. The three previously
reviewed R00956 yellow locations and R01284's central pale-yellow location pass.
Their cross-setting position spreads are respectively 1, 1, 0 and 1.41 pixels.

Old named coordinates enter only a separate, post-detection evaluation and the
rendering of familiar crops. They cannot create, remove or move a candidate.

## One measurable acceptance rule

Four approaches were considered: brightness alone, neighborhood stability alone,
competition between peaks, and background separation. Each has a failure mode
on its own, so the experiment requires **all** of the following checks. Parameters
were fixed before the full-photo and synthetic runs and were not swept to increase
coverage or fit the reviewed locations. They are conservative operational choices,
not statistically calibrated confidence probabilities.

| Evidence | Acceptance requirement | Plain meaning |
|---|---|---|
| Brightness | Mean linear relative luminance in 7×7 ≥ 0.25 | Withhold dim locations. |
| Broad illumination | At least 85% of 9×9 pixels have luminance ≥ half the 7×7 mean | Avoid a bright tip surrounded by deep shade. |
| Bright patch size | At least 25 of those 81 pixels have luminance ≥ 80% of the 7×7 mean | Avoid tiny glints and ambiguous small patches. |
| Window support | Mean9 / mean5 ≥ 0.65 | The signal must survive a larger neighborhood. |
| Local contrast | The 7×7 mean exceeds the raw median in the radius 8–12 annulus by ≥ 15% of that mean | Reject broad, weak bumps. |
| Background | Every pixel of 9×9 must clear the unchanged confident-paper and uncertain-paper maps | Keep the proposed location away from known or uncertain background. |
| Flat tops | Maximum plateau's bounding-box diagonal ≤ 2 pixels | Do not assign a precise coordinate to a broad flat top. |
| Neighborhood stability | The maximum distance between all 18 search endpoints ≤ 3 native pixels | Withhold locations that move when reasonable settings change. |
| Better competing peak | The primary broader search must keep this mean7 maximum | Do not force a weak maximum to become a trusted location. |
| Unresolved rivals | No rival 4–16 pixels away, ≥ 90% as bright, connected without a ≥ 25% mean-luminance valley | Withhold ambiguous nearby highlights instead of silently combining them. |
| Final close conflict | If otherwise accepted proposals are ≤ 6 pixels apart, withhold both | Avoid arbitrary selection between unresolved close proposals. |

Luminance uses R270's ICC-managed sRGB conversion and proper linearization, before
averaging. The source's Apple Wide Color Sharing Profile is preserved in the
metadata. The 7×7 mean is the location score; 5×5 and 9×9 test stability. All native
regional maxima of the mean7 surface are inventoried, including every pixel of an
equal-valued maximum plateau. There is no old V-prominence gate.

The 18 settings are three windows, two search radii (10 and 16), and three R270
raw/mean valley allowances (12/2, 24/2, 24/6 in neutral-gray-equivalent units).
The primary setting is mean7, radius16, raw24/mean2. Every search starts at the
candidate itself; no previous selected coordinates are required. Existing native
HSV color, background and diagonal-corner barriers remain fixed. Search allows
small downhill steps. Rival separation uses the greatest possible mean-brightness
bottleneck through color/background-compatible native paths. These are local
measurement and path checks, not region growth or inferred bead geometry.

**Image brightness is only an illumination proxy.** The method cannot disentangle
illumination from material reflectance. This intentionally strict floor favors
well-lit pale or colored bodies and excludes many valid dark, red or shadowed
beads. It also defers some clear black-bead reflections. Nothing attempts to recover
those exclusions to increase the count. Brightness and stability cannot prove
that a highlight is a physical center or resolve an invisible material boundary.

## Results and retained exclusions

The photograph contains 40,483 mean7 maximum plateaus. Of these, 493 pass the
inexpensive checks and receive the full stability/competition analysis; 453 pass
all checks. This is a candidate audit, not a bead census. No final close conflicts
remain. Every failed candidate survives with all measured values and the reasons
found at its evaluation stage. Expensive searches are intentionally skipped for
obvious exclusions, and `search_checked` distinguishes those cases.

The fixed 4×4 full-frame occupancy is measured **after** selection:

| | Left | Left middle | Right middle | Right |
|---|---:|---:|---:|---:|
| Top | 17 | 15 | 24 | 21 |
| Upper middle | 45 | 16 | 27 | 49 |
| Lower middle | 7 | 33 | 47 | 53 |
| Bottom | 0 | 35 | 33 | 31 |

This establishes broad image coverage without imposing a geographic selection
prior. It does not establish coverage of every necklace section or every color.

Across the 112 preserved synthetic scenes, the same rule accepts 61 locations:
36 in the 96 original stress scenes, 21 in the 12 colored-highlight scenes, and
4 in the invisible-interface controls. **Zero accepted locations lie on known
background; zero known bodies receive multiple accepted locations.** All 1,098
search routes attached to accepted synthetic locations stay on their starting
body. Seventy scenes receive no accepted location. The invisible-interface
controls each retain only the clear bright maximum; this does not mean their
hidden boundary has been recovered or that all invisible-boundary cases are safe.
Synthetic truth is used only after detection for evaluation. These limited tests
support conservative review, not a measured whole-photo precision guarantee.

Nine reproducible tests cover a nonempty clear-patch result, dim and tiny-highlight
exclusions, unresolved multiple highlights, uniform background, translation,
plain rejection reasons, a stricter brightness floor and saved path endpoints.
Saved-data validation checks all maximum pixels, native score samples, all 8,874
photographic stability routes and their selected endpoints, acceptance invariants,
synthetic accepted routes, and prior-file hashes. Exact counts are recorded in
[validation.json](review/r271/validation.json).

## Delivery and next review

[Evidence index and reproduction commands](review/r271/README.md) link the simple
photographs and full numerical inventory. R270 and the production source are
preserved. The reusable implementation is
[trusted_r271.py](bead_detection/trusted_r271.py), an isolated experiment whose
runtime inputs are image arrays and parameters.

Stop here after commit/push. Next, only when requested, review the cyan-dot set
for false trusted locations and the geographic gaps; tighten or reject the
acceptance rule on that evidence. Do not optimize count or resume geometry.
Keep the current model/reasoning; no `/new` is needed for this review.
