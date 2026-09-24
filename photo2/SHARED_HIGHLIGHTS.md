# Shared bright cavities — R057

## Protocol frozen before scoring

Compare unchanged R055 conservative repair with two one-pass extensions. Only
enclosed eight-connected zero-label cavities whose every pixel has S<.20 and
V>=.75 qualify. Single-owner cavities keep R055 repair; shared cavities have
one candidate per adjacent existing label. Existing labels never change and no
new labels are created. No fits, clicks, jitter, masks or colors are retuned.

For **distance**, assign each cavity pixel to the owner with the shortest
eight-connected path from an adjacent boundary pixel. Orthogonal edges cost 1,
diagonal edges sqrt(2). Only cavity pixels may be traversed after the source.
For **gradient**, use the same paths with each edge cost multiplied by
`1 + RMS(delta_RGB/255)`, including the first boundary-to-cavity edge. Weight 1
is fixed before evaluation. This is a local RGB-change heuristic, not a recovered
lighting model. Retain zero for costs tied within atol=rtol=1e-12. Compare the
two fixed methods without selecting a weight from truth. Run once from the
original observed labels; filling repeatedly is outside this protocol.

Reuse the R052 fits and controls and verify conservative parity with R055.
Write predictions before loading trial truth. Evaluate total and incremental
pixel ownership, background, region/color/missing-index summaries, splits/merges,
anchor identity, all retained index alternatives and nominal/jitter acceptance.
Include existing black/shadow, background/duplicate/excluded-phase controls and
first-region deletion. Schematic controls cover ties, label permutation, gradient
effect, open/diagonal gaps, dark/saturated gaps and absent/missing regions.
Increased acceptance is not evidence of correct ownership, seed or helicity.

R057 maker context: photo taken on an iPhone, flash use unknown. Do not infer
light settings from the conditional camera-flash explanation. Color reflections
remain unspecified. Continue without further answers, as requested.

Stop after the comparison and checks, before ring growth, photo fitting or
repeat inference. Keep both hands, unknowns, provisional count 2,698 without
divisor filtering and repeat bound <400.


## Results and decision

Neither extension is adopted as the default repair. Both improve anchor
acceptance, but both assign some shared pixels to the wrong beads. Gradient
cost removes most distance ties without improving anchor/index outcomes and
adds more wrong or unresolved ownership. Keep R055 conservative abstention as
the baseline; retain these experimental methods and all failures for comparison.

Across 45 eligible shared cavities (1,687 pixels), distance assigns 1,465 pixels
and abstains on 222 ties; gradient assigns 1,679 and leaves eight ties. These
counts sum repeated perturbations of shared scenes, not independent beads.

| Added shared pixels only | Distance | Gradient |
| --- | ---: | ---: |
| Correct owner | 1,112 | 1,227 |
| Wrong owner | 137 | 151 |
| Unresolved owner | 216 | 301 |
| True background | 0 | 0 |

Ownership uses evaluator IoU>.5 region matches, including border/sliver records.
Unresolved means the assigned observed region lacks that match; it is not
counted as correct. Matching owners before or after extension gives exactly the
same counts. R055's 4,672 single-owner additions remain correctly owned for both
extensions. Preserving original labels does not establish correct new labels.
Every supported region/color/unknown/missing-index summary stays unchanged, as
do false-positive foreground, split and merge counts. Existing shadow errors
remain. No additional bead detection or correct helicity is established.

| Anchors | Conservative accepted /272 | Distance /272 | Gradient /272 | Accepted with any wrong index, all methods |
| --- | ---: | ---: | ---: | ---: |
| Three | 134 | 155 | 155 | 36 |
| Four | 115 | 140 | 140 | 36 |

No acceptance losses. Four-anchor accepted groups whose retained seed bodies
are all correct rise 99→121 for both methods. Twenty original-gray gains have
correct seeds; of five second-gray gains, two have correct seeds and three retain
the known 761-for-767 seed slip. Correct model output can coexist with a wrong
seed. All four gray conditions now accept all 17 four-anchor variants. Original
gray nominal identity/translation/smooth output has respectively 37/37, 34/34
and 38/38 correct matched indices and correct seeds. Second-gray nominal output
remains 35/35 with the wrong second seed. Every reported index is conditional on
the supplied calibrated geometry and retained candidate, not recovered photo order.

| Condition | Shared pixels distance / gradient | Wrong pixels distance / gradient |
| --- | ---: | ---: |
| Original gray identity | 284 / 318 | 30 / 34 |
| Original gray translation | 284 / 318 | 30 / 34 |
| Original gray smooth | 276 / 301 | 26 / 31 |
| Second gray | 383 / 411 | 50 / 51 |
| Second R/Y/black | 66 / 101 | 0 / 0 (52 / 84 unresolved) |
| Second black | 164 / 217 | 0 / 0 (all unresolved) |
| Second opposite-hand RGB | 8 / 13 | 1 / 1 |

Background and duplicate controls reject in all 32 group/condition combinations
for every method. Excluding true phase retains alternatives in 10/32 conservative
controls and **12/32 for each extension**, adding the original-gray smooth
three/four-anchor groups. This is a worsened rejection failure. Thirteen applicable
first-region deletions restore no deleted pixels and leave seeds unassigned;
three original-gray first clicks were already unassigned and remain explicitly
inapplicable. Second R/Y/black and all-black anchor failures persist; existing
wrong-hand alternatives remain. No threshold, cost weight, fit or click tuning
followed scoring.

## Reproduce and validation

```sh
.venv/bin/python photo2/shared_highlight_audit.py --output photo2/output/shared-highlights-new
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The default prerequisites are `output/region-anchors-r052-final` (`--previous`)
and `output/highlight-regions-r055-final` (`--conservative`). Reproduce
REGION_ANCHORS.md and HIGHLIGHT_REGIONS.md if absent. Bound reports contain local
absolute paths and require their recorded inputs. The runner verifies R052 and
R055 sources/artifacts, all five R052 bound reports and their manifests, including
the historical-source-aware baseline verifier. Reuses all 128 fits, both hands,
16 conditions, 544 positive anchor trials and 96 prior controls. No new fits or
candidate renders. Predictions and deletion ablations precede trial truth loading.

The report contains aggregate `summary`, per-condition results, all competing
hypotheses, unknowns/misses, parameters, package versions, commands, 16 source
hashes and 80 artifact hashes. Old R052 gates/scores and R055 masks, gates,
baselines, ownership, retained alternatives and scores reproduce exactly.
Eight new behavioral tests bring the suite to **86 passing tests**. Controls
exercise gradient-driven ownership changes, distance ties, rotation/label
permutation, multiple glints, dark/saturated/open/diagonal gaps and missing regions.
Compilation/dependency checks pass; pip warns about its nonwritable external cache
but finds no broken requirements and changes no environment. Small renderer tests
ran; full legacy rerender is skipped because tracked POV sources are unchanged.

After the initial run, only aggregate reporting and evaluator ownership colors
on panels were added; algorithm parameters and original results stay fixed.
Panels mark correct additions magenta, wrong owners orange and unresolved owners
blue; truth overlays are for evaluation only.

Two final runs reproduce all **80 artifacts byte for byte**, with reports equal
except command output path. All 16 current source hashes verify. Independent
checks confirm initial/final numerical trial equality and unchanged prediction,
evaluation and mask bytes, plus aggregate acceptance counts. All 16 initial
panels reviewed as a contact sheet; final original/second-gray, second-black and
warped R/Y/black panels reviewed full size. No failed runtime test/audit; no
post-score rule changes. Whitespace checks pass. Generated data stay ignored.

Final report: `output/shared-highlights-r057-final/report.json`, SHA-256
`6095d26bd555b5dde171d48f0df40557a102707db15989cbee8752cc5a0a1efd`.

## One next task

Test whether a second spatially separated group of observed bead regions within
each frozen crop rejects the surviving wrong-helicity/phase alternatives. Choose
that validation group from the beauty/observed regions before evaluator truth,
keep current fits and R055 conservative repair, and report lost correct as well
as rejected wrong candidates. Retain both hands, jitter and background/duplicate/
excluded-phase controls. Stop after local hypothesis/seed/index evidence and
checks, before ring growth or photo fitting. Recommend gpt-6-astra / High with a
fresh `/new` for this distinct step. No further advice questions this round.
