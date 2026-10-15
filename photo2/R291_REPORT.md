# R291 — complementary boundary evidence and a shorter review

R291 delivers revised automatic proposals and a **14-case Start Here review**.
Several named development failures look materially better: P2 retains broad red
material instead of a highlight-only contour, P5 and N06 avoid large adjacent
extensions, and Q14 proposes more of the diffuse red surface. Significant mergers,
truncations and dark-reflection ambiguities remain. **Complete-boundary accuracy
is not established; all68 primary cases retain partial/unresolved status.**

Launch from the repository root:

```bash
photo2/review/r291/launch.sh
```

Open **http://127.0.0.1:8291/**. Start Here is the default. One click can credit
useful partial segments, or say both proposals are wrong although the photograph
is clear. Optional explanations and ownership questions can be skipped entirely.
The new interface and feedback directory are separate from R290.

## What changed scientifically

R290's graph could connect across a bright detour around a dark seam. Its distant
frame also moved boundaries, and its stability requirement erased locally measured
edges. Simply increasing its support fraction would not solve these defects.
N06's old3458px merger had98.6% locally supported outer sides. R215-A's2797px
proposal included seven other features. Those scores did not establish one bead.

R291 uses one binary target graph with complementary local measurements:

- **A, coherent darkness:** normal profiles at2/4px with five adjacent tangent
  samples, plus five parallel straight profiles to each competing bright feature.
  Four aligned dark profiles including the central track protect a separator.
  Source-to-pixel paths also stop after sustained darkness across four of five
  nearby tracks. A brighter route around that measurement cannot erase it.
- **B, multiscale tracking:** signed illumination transitions persistent at
  Gaussian scales0.65/1.2/1.8 and along neighboring pixels. These can support an
  edge without a deep dark floor, while exposing ambiguity with smooth shading.
- **C, material transitions:** channel-difference color direction, with low-light
  and neutral-side evidence discounted. A local hue model supports continued
  diffuse material without assuming that a white specular patch is its boundary.
- **D, bright continuity:** target-local pigment, illumination and direct-path
  access provide soft foreground evidence. Continued same-material illumination
  opposes cutting a highlight or a normal shading gradient. Weak diffuse exposure
  relative to the peak reduces borrowing material from neighboring colored beads.
- **E, occlusion context:** terminating edges and junctions in the local edge
  skeleton identify ambiguous portions. They are context proxies, not certified
  T-junctions, physical occluder identities or a separate reconstruction algorithm.

Different portions use different evidence. A/B/C strengths combine locally as a
bounded union of evidence. Bright-continuity conflicts weaken the illumination
edge term without canceling a dark separator. Graph capacities discourage cutting
continuous material; soft unary costs favor illuminated target material and oppose
pixels beyond first-dark interruptions. A protected competing feature becomes a
non-target anchor in this one binary solve. It is not simultaneously segmented
or assigned a physical identity. The frame is computational background, never a
photographic boundary.

The result is the source-connected candidate, with exact native pixel-square sides.
Every supported side records A/B/C justification; D contradictions and E context
remain explicit. Local photographic support survives parameter instability, whose
separate flag remains visible. Internal dark edges survive even if the proposed
outer contour bypasses them. Holes are not automatically filled or connected to
the exterior. No shape, roundness, solidity, area or geometric plausibility gate
rejects a real object.

B is a meaningful alternative from the **same fused evidence graph**: it softens
first-dark interruptions and disputed separator ownership, allowing continuation
that could have been blocked by an internal shadow. A remains the fixed primary;
neither candidate is selected by visual attractiveness. There are13 alternatives.
They can also be wrong. The viewer can display only the differing portions.

Search begins at48px half-width and expands to96/144px on contact. Parameter
checks change the unary weight by±15%; a separate solve adds16px of context.
These differ from R290's conductance and19px frame perturbations, so their IoUs
are sensitivity diagnostics rather than a paired accuracy comparison.

## Development, freeze and actual changes

The original41 development cases were used for diagnosis and implementation.
The original17 reserved cases are explicitly **retrospective regressions**.
Ten new targets—four red-context, four yellow-context, two unknown-context—were
hash-selected and frozen before implementing R291. They are at least100px from
all58 old targets and earlier new targets. Larger contexts can overlap, and this
remains one historically studied photograph, not a new scene or calibrated test set.

Code and parameters were frozen at **2026-10-15T04:46:14Z**, before opening the ten
new outcomes. No inference code or parameters changed afterward. Review-priority
ranking, presentation and comparison documentation use the frozen results.

Two failed development versions remain in `r291/checkpoints/`: the first still
collapsed P2 to24px and borrowed red material around a dark reflection; the next
restored diffuse continuation but admitted long neighboring extensions. Replacing
a ridge prerequisite with sustained first-dark profile evidence addressed the
general missing measurement. No coordinate exception was added. Both full data
collections and their source versions survive.

| Development case | R290 → R291 pixels | Photographic assessment / remaining limits |
|---|---:|---|
| P2 |764 →495|Broad red proposal restored; illumination-versus-continuity conflict leaves much of the contour uncertain|
| P5 |878 →498|Large extension reduced; diffuse extent may still be too conservative|
| N06 |3458 →388|Large merger avoided; five previously included features removed; possible truncation remains|
| N07 |966 →436|Upper/lower extensions reduced; multiple internal highlights still need ownership review|
| N11 |888 →494|Less neighboring extension; outer material extent remains uncertain|
| Q14 |191 →295|More diffuse red material proposed; still not a certified complete surface|
| R215-A |2797 →297|Large connected merger removed; conservative truncation is possible|
| red-multiple-1 |673 →1494|Regression: new merged material and three additional feature inclusions|
| development-red-06 |604 →1409|Regression: substantial neighboring extension remains despite high stability|

Pixel counts describe changes, not the reason to prefer a contour. The named
assessments come from the actual original-photograph development comparisons.
No old mask, old centroid or previous method is treated as exact boundary truth.

Across41 development cases there are2295 newly located supported pixel sides and
2476 old supported sides without a new match at1.5px tolerance. Nine cases remove
previously included features; seven add features. These are **regression diagnostics**:
the evidence definitions differ, and features can share one physical bead.
They do not measure recovered correct pixels or neighbor-pixel precision.

Seven R291-supported separator/feature conflicts found inside old development
regions become zero in the new primary regions. This verifies enforcement of the
measured separator anchors; it does not prove that each separator divides physical
beads. A true internal hole or shadow can still create a false separation.

Median development local support is80.0%, and43.2% of sides are reinforced by
multiple A/B/C mechanisms. Median minimum perturbation/context IoU is.987. The
old17 retrospective cases have83.0% median local support and.981 median minimum
IoU. The ten new holdouts have78.7% median local support and.985 median minimum
IoU. **None of these numbers establishes boundary correctness.**

The3272 development-supported sides include162 supported by darkness alone,
852 by multiscale illumination alone,325 by material color alone, and1933 by
multiple mechanisms. Thus the contour combines different local analyses rather
than choosing one whole-mask method. These mechanisms share pixels and are not
statistically independent; their fused strength is not a probability.

All68 primary cases remain partial/unresolved. This reflects explicit remaining
gaps and conflicts; R291 never automatically asserts that the photograph itself
is insufficient. The new review can credit useful segments without forcing a
misleading “Neither” answer.

The new holdouts retain clear failures. `fresh-red-01` merges material;
`fresh-red-03` has competing material/illumination interpretations;
`fresh-unknown-02` grows into a15076px false region and reaches the144px analysis
limit. Its stability is high despite being wrong. It remains visible in the full
collection and coverage matrix; no repair was made after inspecting it.
Some older neutral/tinted reflections still outline a small highlight, and some
dark profiles truncate visible material. The improved method is not adopted into
production and is not a general complete-boundary solution.

## A smaller, clearer human review

Start Here uses fixed quotas: three likely useful contours balanced across color
strata, two mechanism-agreement cases, two disagreements, two same-color-neighbor
cases, one multiple-highlight example, one difficult dark boundary, one possible
occlusion and two low-diffuse/reflection examples. Ranking uses local support,
mechanism agreement, sensitivity, competing-feature ambiguity and old inclusion
changes. Targets are separated by at least12px to reduce duplicate questions.
Scores and reasons are saved in `results/start-here.json`; these are machine
review priorities, not human judgments or an unbiased accuracy sample.

All58 R290 cases and ten new cases remain available through the review-set filter
and full case menu. Only the target ring and boundary appear initially. Other bright
point labels appear on request. Raw photograph, hide-all, alternative differences,
R290 outline, internal dark edges, zoom/pan, keys1–6, H, arrows, filters, navigation,
undo/revisions and export are retained.

The six main choices distinguish good A/B, useful partial segments, wrong despite
clear photograph, genuine photographic insufficiency and uncertainty. Optional
diagnostics record neighbor inclusion, target exclusion, internal/highlight edges,
missed dark boundaries or another problem. They are never mandatory.

Canonical feature-pair ownership is reused across cases and can be revised. The
prior `red-worst` same-bead statement and R215 evidence appear read-only with
provenance, without new questions about already-confirmed old marks. These facts
do not enter detection. Machine scores never populate the human answer ledger.

Feedback is saved separately in `photo2/r291/feedback/judgments.jsonl` with immutable
candidate/native-photo snapshots, original coordinates, image/algorithm/parameter
hashes, six-choice assessments, optional diagnostics, pair ownership and complete
revision history. Undo appends a revision. R290 feedback and scientific files remain
unchanged. A concise history endpoint avoids downloading full masks after every click.

## Validation and stopping point

Sixteen focused real-photo tests pass. All68 crops match original native decoded
pixels. Independent replay matches all three result files byte-for-byte and all68
PNG files exactly. All11,430 historical files are unchanged. There were no existing
R290 feedback files in this checkout; no old feedback stream was created or changed.
Chromium loaded all68 cases and passed the14-case default, six answer choices,
optional diagnostics, actual zoom/pan, ownership reuse, revision/undo/export/reopen,
all eight evidence panels, and1400px desktop/520px narrow layouts. The initial
autosave checkbox presentation failure and a corrected browser-test navigation
assumption are retained in `checkpoints/browser-save/`; neither changed inference.

Human correctness, neighbor-pixel inclusion/exclusion precision and centroid accuracy
remain unmeasured. The [coverage matrix](R291_COVERAGE.md) reports category-specific
changes and missing new-holdout coverage. Subthreshold weak seeds, exact hole/occluder
ownership and pixel-accurate boundary truth remain missing. Only accepted R289
features were used as starts.

No synthetic image, artificial scene, renderer, geometry/light fit, indexing or
pattern experiment was run. Production and historical results remain unchanged.
Delivery/remote verification is recorded in `r291/results/delivery.json`.
**Stop for the user's review. No automatic R292 or holdout-driven repair.**
