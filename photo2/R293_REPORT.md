# R293 — clear photographic observations first; conditional Phase 2 readiness

R293 refocuses assessment on the image-derived necklace centerline and nearby
independent observations. **No detector revision or production replacement was
needed for this bounded assessment.** The frozen R292 detector is unchanged; all77
historical proposals are identical. The improvements are the priority population,
coverage accounting, separation of observation types, and a much shorter review.

Completed R292 feedback is archived and analyzed: **four A, three partial, four
wrong-clear**, all11 cases present. The principal yellow repair is accepted. Clear
central failures remain, and the user's red-multiple-1 acceptance is preserved despite
automatic warnings. See [the full review analysis](R293_R292_REVIEW_ANALYSIS.md).

Launch:

```bash
photo2/review/r293/launch.sh
```

Open **http://127.0.0.1:8293/**. The first panel is the priority coverage overview:
whole original photograph, centerline, source features, signed-side/window evidence,
native unmarked window crops and links to available automatic proposals. Zoom/pan,
hide map marks, switch priority/source-material/window views, or inspect any window.
**Start Here asks eight new central questions.** Twenty-four old reviewed cases
remain read-only; no new answers are manufactured or requested for them. All125
old/new cases remain accessible, with raw photo, target, thin contour/separator
views, independent/candidate position explanations, six choices, optional diagnostics,
zoom/pan, undo/history/export/reopen and separate R293 feedback.

## Why the peripheral emphasis happened

Historical difficult cases were repeatedly reused as regression examples. R291/R292
then selected new targets by color/hash with100px exclusion around old targets,
which made already-covered central neighborhoods less available. R292's review
ranking favored separator conflicts, remaining detours and instability. Those are
useful causal tests but a poor denominator for overall Phase 1 progress.

The permanent contract already prioritized clear central material and allowed
difficult edges to remain unresolved; review selection drifted away from that
priority. Eight of11 R292 review targets are beyond the26px centerline point-reach
convention. They are192–836px from the photograph border: many difficult interfaces
concern the outside of the necklace arrangement or background-facing surfaces,
not literal photograph clipping. Signed curve side is not a global arrangement
inside/outside label. Neither spatial designation alone measures photographic quality.

Correction: use well-observed centerline/nearby features as the assessment population;
retain old difficult cases as regressions. Preserve clear peripheral observations,
central failures and weak observations, but defer difficult full silhouettes. Do not
sacrifice central quality or force two/three beads at a station. The
[priority policy](R293_PRIORITY_POLICY.md) restates the permanent Phase 1 contract.

## Representative frozen population and unchanged inference

Before opening new segmentation outcomes, R293 froze all1545 accepted independent
R289 bright features as the photographic evidence population. Of these,784 lie
within26px and1204 within40px of the unregistered R255-derived image curve. These
are **features, not physical beads**. Positions, source context labels, bright-patch
pixels and threshold sensitivity remain unchanged.

Photometric priority uses original ICC-managed luminance: median11px window Y≥.025,
feature contrast≥.03 and at least3 patch pixels. These measure illumination/contrast/
resolution for sampling, not contour accuracy or physical visibility. There are769
such features within26px,15 central measurement uncertainties,404 well-observed
nearby features,339 clear outside-band secondary observations and18 deferred weak
peripheral observations. Difficult ownership/silhouettes can remain unresolved even
when a bright patch passes these proxies.

A representative48 new targets were frozen:24 development and24 reserved. Twelve
arc strata, four sampling passes, source-context/signed-side diversity and hash
ranking select them; separation is45px from all77 old targets and24px between new
targets. This is a sampling design, never a bead quota. The sample has16 each red,
yellow and unknown source contexts; the full near26 population has508/231/45.
Thus it is balanced, not population-proportional, and pooled accuracy would require
careful weighting and human truth. All targets have well-observed sampling proxies;
neutral/tinted reflections can still have uncertain owners.

Collection freeze: **2026-10-15T20:05:36Z**. Inference/decision freeze:
**2026-10-15T20:08:03Z**, before reserved outcomes.

Development comparisons show many useful regions/reflections but also clear central
mergers (e.g. central-0345-1501, central-0949-2513, central-0999-0350). The
[development decision](R293_DEVELOPMENT_DECISION.md) therefore preserves independent
positions/partial material rather than inventing another large contour algorithm.
The existing algorithm is useful for many photographic observations, not uniformly
adequate for full target-owned material. No central failure is reclassified as
insufficient photograph or hidden by peripheral exclusion.

The decision/source freeze precedes the24 reserved outputs. Reserved comparisons
retain a clear yellow merger at central-2140-2471 and other uncertain ownership or
truncation cases. No inference tuning followed. All T1–T8 and sensitivity evidence
are saved. [Every new case](r293/results/case-evaluation.csv) and
[diagnostic strata](r293/results/evaluation.json) report automatic flags separately
from pending human correctness. No new contour-accuracy percentage is claimed.

## What the centerline overview establishes

The source is `photo2/review/r255/spline-samples.csv`, unregistered and image-derived;
R282's dense copy preserves its source hash. Reference length is9235.6 native pixels.
There are385 inspection windows at24px arc spacing. Each uses an actual26px Euclidean
footprint with a40px local arc guard, rather than an expected physical bead site.

| Evidence | Result | Meaning and limit |
|---|---:|---|
| Windows containing illuminated independent features |385/385|Feature availability, not every bead or complete material coverage|
| Windows with observations on both signed sides |358|Potential multi-surface context; no fixed number of beads|
| Windows with dark-separator-supported opposite-side context |303|Photographic support, not certified distinct physical owners|
| Opposite-side feature pairs examined / separator-supported |932 /328|Pairs can share features; internal shading remains an alternative|
| Nearby-feature ambiguity pairs within12px |271|Possible duplicates/multiple highlights, never automatic bead counts|
| Neutral/reflection-like patches within26px |235|Useful reflection candidates, not235 black beads or physical centers|
| Historical near-line locations without R289 feature within8px |28|22 black-context/6 red-context discrepancies; not28 verified missing beads|

The overview explicitly separates source red/yellow/unknown context from neutral
reflection-like patches. Tinted black reflections can inherit red context; neutral
highlights can belong to colored material. Physical material color/ownership is not
manufactured from these proxies. Existing user-reviewed reflection regions remain
reflection measurements only.

A previous narrow±18px arc-bin metric reported one false empty window, S083. Its
nearest independent feature is19.5px away but18.68px along the curve, just outside
that bin. R293 preserved the initial source/results under `checkpoints/arc-window-initial`
and corrected the generic footprint definition. It does not present that bookkeeping
artifact as a missing bead. All385 windows now contain source features; this still
cannot certify completeness.

The28 historical location discrepancies remain a concrete inspection list. Old R275
positions/masks are not ground truth; a shifted or unmatched feature is not proof of a
new or missing bead. Centerline ambiguity and distinct ownership remain unresolved.
The full [coverage matrix](R293_COVERAGE.md), [station table](r293/results/stations.csv),
and [coverage data](r293/results/coverage.json) preserve exact IDs/coordinates and limits.

## Useful independent observations for Phase 2

The experimental [Phase 1 export](r293/results/phase1-observations.json.gz) retains
all1545 original features, including lower-priority/uncertain ones. It also references
the unchanged810 historical R275 locations/807 native supports by source/hash, without
replacing them or automatically merging identities across the two collections. Every record has
original peak, unweighted representative patch centroid and original intensity-weighted
alternative, exact native patch pixels,
shape/intensity/color evidence, source-image/archive hashes, threshold sensitivity,
nearby alternatives, signed curve position and separate unknown ownership/visibility.
The representative follows R289's unweighted-centroid recommendation; no source
location is adjusted or replaced. Width/covariance describe the measured bright patch, not physical bead shape or a
calibrated localization confidence interval. Original RGB and source context remain.

Seventeen historical user-accepted visible-region measurements are linked at their
**exact accepted versions**, including R291 B where selected. Three have an automatic
reflection-region flag and14 are generic accepted photographed-material regions;
these are scope flags, not physical color truth. All black/reflection measurements
retain unknown dark-body center/crossing. Human acceptance is qualitative, not exact
pixel ground truth or proof of every included highlight's physical owner.

The48 new full masks are separate **unreviewed hypotheses**, not certified bead-owned
material. Partial/failed historical regions remain linked to original evidence;
their independently measured bright patches are retained. Candidate mask centroid,
independent bright-patch location and unknown physical center are distinct fields.
No production record, original observation, color or position is replaced.

**Readiness: yes for a future bounded, conditional Phase 2 experiment on a selected
observation subset; no for treating Phase 1 as a verified complete bead inventory.**
Use reviewed visible regions and independent bright/reflection patches, allow multiple
correspondences or no match, retain localization/ownership uncertainty and evaluate
against the original pixels. Phase 2 may interpret linked observations through
geometry/common illumination; it must not manufacture, move, recolor or replace them.
Do not wait to solve every peripheral silhouette before such an experiment.

Major remaining limits are distinct-bead ownership/duplicate highlights, same-color
region mergers in clear central photographs, tinted-reflection/material confusion,
unverified colored diffuse extent, and the28 historical location discrepancies.
A single feature near a reference window cannot establish complete two-sided inventory.
No Phase 2/3 fit, physical center, indexing or color-pattern inference is implemented.

## Review and validation

Start Here contains an opposite-side yellow pair, two possible clear central ownership
failures, two useful-looking colored visible regions, one reflection measurement and
one reserved central observation. All eight targets are new, within26px and selected
from well-observed context. Questions concern useful visible material/reflection, not
complete physical silhouettes. The17 earlier acceptances and all other prior judgments
are preserved; 24 previously reviewed cases are read-only, never copied into new human
answers. The difficult old bank remains accessible but does not dominate the queue.

Validation includes12 focused real-photo contracts, exact replay of both24-case
collections/all48 PNGs, exact full native overview/125 case crops/385 station crops,
all77 historical A/B/separator records unchanged,12002 historical files and52 feedback
files unchanged, and source-freeze verification. Actual Chromium checks the overview,
window inspection, map/contour zoom/pan/hide, all125 cases/T1–T8, eight new questions,
read-only prior judgments, feedback revisions/undo/export/reopen and desktop/narrow
layouts. See [reproduction instructions](R293_REPRODUCE.md) and saved receipts.

Presentation checks also caught a narrow-screen map retaining its desktop transform;
the final UI refits on resize and checks that the original image remains visible.
The first screenshot/test scope is retained under checkpoints/browser-responsive-first.
No scientific inference changed.

No synthetic images, artificial truth, production adoption or Phase 2/3 work.
**Stop after verified commit/push for user review; no automatic R294.**
