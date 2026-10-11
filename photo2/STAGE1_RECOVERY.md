# R238 — bounded Stage 1 detection recovery

**Coverage improves from 76/109 to 103/109, but the experiment fails its
predetermined success gate.** It recovers 12 colored and 15 reflection-supported
black observations while retaining all 76 baseline detections. The accepted
supplement also introduces **3 confirmed duplicates, 9 false positives and
1 wrong-color assignment**. Seven new unresolved proposals remain. These errors
are scored, not removed by the visual audit. This is a useful proposal generator,
not a reliable automatic Stage 1 map or a replacement production detector.

The user authorized the [R236/R237 proposal](STAGE1_FAILURE_DIAGNOSIS.md), including
implementation, evaluation, scoped commit and push. D3/D4 alone informed development.
The final detector, parameters, automatic inputs and development output were
[sealed before transfer](review/r238/freeze.json). H1/H4 were then evaluated with
those rules; there was no subsequent detector change. Deterministic reruns are
verification, not further tuning. H1/H4 were previously inspected in R235/R236;
they are transfer checks, not unseen holdouts.

## Review the evidence

Start with the [five raw/measurement comparisons](review/r238/failure-paths.png):
a recovered colored face, a recovered black reflection, native reflection versus
paper edge, an incorrect colored-body merge, and suppression of a real reflection
by a false proposal. Cyan rings/disks show sampling neighborhoods, **not outlines**.
The [measurement records](review/r238/failure-paths.json) give coordinates, radii,
threshold evidence, original rejection and final decision.

| Section | Raw beside automatic proposals | Audited overlay | Every addition and reason |
| --- | --- | --- | --- |
| D3 development | [Comparison](review/r238/development/D3-comparison.png) | [Audit](review/r238/D3-audit.png) | [Table](review/r238/D3-audit.md) |
| D4 development | [Comparison](review/r238/development/D4-comparison.png) | [Audit](review/r238/D4-audit.png) | [Table](review/r238/D4-audit.md) |
| H1 transfer | [Comparison](review/r238/transfer/H1-comparison.png) | [Audit](review/r238/H1-audit.png) | [Table](review/r238/H1-audit.md) |
| H4 transfer | [Comparison](review/r238/transfer/H4-comparison.png) | [Audit](review/r238/H4-audit.png) | [Table](review/r238/H4-audit.md) |

Comparisons use original RGB with nearest-neighbor enlargement. Cyan points are
baseline proposals, yellow additions come from old pools, green from native search.
Audit marks: **+** supported, **D** duplicate, **F** false positive, **W** wrong
color, **U** unresolved, **C** halo context. A-numbers name proposals, B-numbers
are the unchanged R235 observations. Neither denotes a string index. The audit
shows all accepted additions, including errors. Consult the
[R235 numbered references](STAGE1_PILOT.md#sections-and-review-artifacts) for B IDs.

## Comparison and implementation

Three methods were selected by the approved proposal: frozen baseline; baseline
plus reconsidered old candidates; that union plus native-resolution reflections.
All original M4/R192 proposals are retained. This experiment adds separate
[detector](stage1_recovery.py) and [evaluation](evaluate_stage1_recovery.py)
modules; it does not modify historical detectors or their payloads.

Runtime inputs are original pixels, automatically learned appearance/scale,
automatic candidate pools, and fixed section boxes with 30px halos. No reference
locations, identities, eligibility, color judgments or fitted geometry enter
`detect_section`. Evaluation and illustrative coordinates are separate. The
[portable input archive](review/r238/inputs.json) contains every old candidate
in those halos, old rejection reasons, profile-cut counts, full-photo learned
parameters and source hashes. The old black detector was rerun unchanged to
recover its early rejection trace; its source hash still matches R192.

**Colored patches.** Reconsider R231 profile-pool candidates absent from M4.
Using the two image-learned hue modes, require hue distance <18 degrees,
saturation above the learned floor, and value above half the learned family
90th percentile. In a radius 0.32-diameter disk require at least 0.10 diameter²
compatible pixels and 0.09 diameter of inset at the sample. These are local
support tests, not estimates of the bead's visible fraction or a change to the
rough 10% eligibility rule. The learned diameter is 27.19 native pixels.

Group candidates using brightness watersheds: Gaussian sigma 0.10 diameter,
peak spacing 0.45 diameter, constrained by colored support. Retain the strongest
value×inset candidate per region unless a baseline sample already occupies it.
A baseline glint outside the colored mask can associate with nearest support
within 0.14 diameter. This prevents many duplicates but **does not establish body
identity**: touching beads can merge, and one bead can split into several regions.
Every suppression names the retained candidate. All 12 successful colored
recoveries had failed the original profile gate, not merely its spacing stage.

**Black reflections.** Reconsider old points, band-edge exclusions and context
rejections. Refine each only within 0.14 diameter of its old coordinate. The
third arm independently finds native local maxima of value after sigma 0.70px
minus sigma 0.30-diameter Gaussian filtering, with 2px peak separation. Both
arms use the same native evidence tests: response ≥0.045, peak value ≥0.28,
saturation ≤0.48; at least 18% of a 0.12–0.32-diameter annulus below value 0.40,
with at least one image-axis quadrant ≥55% dark. Reflections enclosed by closed,
hole-filled colored support are rejected as competing colored-body evidence.
Nearby black proposals within 0.32 diameter are suppressed, without claiming
that distance proves identity. These experimental constants are in [the freeze](review/r238/freeze.json).

Sampling starts at an automatic color sample or reflection maximum; colored
support is measured in its disk, and dark support between the annular radii,
separately in four quadrants. Brightest pixels are never used as bead boundaries.
Quadrants tolerate a colored neighbor but also allow a paper notch beside a dark
body to pass. The current tests do not demonstrate palette/background/placement
generality; no historical hand-picked hue boxes or bead coordinates were used.

Development tried four rule families, with one final correction assigning
baseline glints to nearby colored support. Permissive color disks admitted
shaded paper; longer brightness bridges merged neighboring yellow faces;
relaxed black support admitted colored highlights. The final brightness basins
and colored-enclosure guard improve some of these problems without solving them.
[Development history](review/r238/development-history.json) preserves parameters,
counts and archive hashes; earlier trials were not fully adjudicated and have
no claimed accuracy. Final frozen extraction has 1,144 trace records across the
four halos and 55 accepted additions. Every trace carries its rejection or merge
reason in the [development](review/r238/development/candidates.json) and
[transfer](review/r238/transfer/candidates.json) payloads.

## Measured results

Counts use unchanged R235 provisional agent judgments, not maker-confirmed or
independent ground truth. The five baseline boundary credits and H4-B34 amendment
remain. Thirteen uncertain references and six no-reflection black hypotheses
remain outside the eligible denominator. No new manual body is added to it.
Automatic proposals require visual ownership evaluation, just as in R235;
manual placement never counts as automatic recovery.

| Method | Covered / 109 | New colored | New black | Duplicates | False positives | Wrong color | Unresolved proposals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen baseline | 76 | 0 | 0 | 0 | 0 | 0 | 7 |
| + old-candidate recovery | 96 | 12 | 8 | 3 | 8 | 0 | 9 |
| + native reflections | **103** | **12** | **15** | **3** | **9** | **1** | **14** |

Eight halo-only proposals are explicitly context, not scored detections. Three
accepted samples outside the half-open boxes belong to already inventoried
border-crossing bodies: D3-A01→B16 and D4-A01/A06→B33. Both D4 samples are counted,
so their duplicate survives scoring. All in-box proposals receive a decision;
difficult cases are not labeled out of scope.

| Section | Baseline | Old recovery | + native | Final missing | New duplicates / false / wrong | New unresolved |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| D3, 22 eligible | 19 | 21 | 22 | 0 | 0 / 1 / 0 | 1 |
| D4, 32 eligible | 16 | 26 | 29 | 3 | 3 / 2 / 0 | 2 |
| H1, 27 eligible | 20 | 23 | 26 | 1 | 0 / 2 / 0 | 1 |
| H4, 28 eligible | 21 | 26 | 26 | 2 | 0 / 4 / 1 | 3 |

Development rises from 35/54 to 51/54; transfer from 41/55 to 52/55. Final color
coverage is red 28/29, yellow 43/46 and black 32/34. Of 55 additions, 27 cover
previously missed eligible bodies, 3 duplicate supported bodies, 9 are false,
1 has wrong color, 7 remain unresolved, and 8 are halo context. Removing known
errors after inspection would be an assisted correction, not this automatic score.

Native search contributes seven additional black bodies: D3-B22, D4-B07/B21/B29,
H1-B08/B17/B28. Their nearest original black candidates are 11.4–18.5px away;
the old pool has no candidate within the roughly 3.8px permitted refinement
radius of those accepted native peaks. This supports a genuine candidate-location
gap at that scale; it does not prove the nearest old feature is a different body.
In H1, the old edge candidates land on paper rims while native search locates
reflections inside the corresponding dark faces. H4 obtains no extra verified
body from native search despite five additional accepted proposals.

The predeclared requirements were ≥8 colored recoveries, ≥9 black recoveries,
retention of 76 correct detections, and zero confirmed new false/duplicate/wrong
assignments. **The first three pass; the last fails.** Unresolved additions do
not count toward the recovery target and would remain a precision limitation
even if confirmed errors were zero. Full [summary](review/r238/summary.json),
[observation/assignment report](review/r238/report.json), and
[explicit adjudications](review/r238/adjudication.json) preserve the accounting.

## Persistent misses and identified failure mechanisms

The [original-miss trace index](review/r238/original-miss-traces.json) retains
candidate evidence for all 33 original misses. Proximity there locates traces
for inspection; it is not an ownership decision. Six eligible observations
remain missed:

| Observation | Evidence and final failure |
| --- | --- |
| D4-B13 yellow | Candidate (1713,1610) has 186 compatible pixels and 5.10px inset, but its brightness basin merges into M4:346 on **B14**. |
| D4-B24 red | Candidate (1799,1678) has 237 compatible pixels and 8px inset, but merges into M4:370 on **B32**. Brightness-region identity is wrong. |
| D4-B20 black | Native peak (1733,1652) is present; only 10.8% of its ring and 23.5% of its best quadrant pass the dark cutoff. Neighbor/context contamination remains. |
| H1-B31 yellow | Candidates (165,1229)/(168,1227) have enough colored area but only 1px inset, below 2.45px. Thin eligible patches still fail the seed-interior requirement. |
| H4-B12 yellow | Nearest yellow pool candidate is 20px away, on another body. Reconsidering existing candidates cannot supply the missing face. |
| H4-B27 black | Native reflection (1559,3056) passes local evidence but is suppressed by stronger paper-notch proposal H4-A11 at (1552,3059), 7.62px away. This is an observed harmful suppression, unlike the earlier diagnosis's unproven risk. |

False positives concentrate on paper rims/notches beside dark bodies and on
red-brown paper/shadow fringes. A high local response plus a dark neighboring
sector does not establish that the bright feature belongs to a black bead.
D4-A06 duplicates B33; A08/A09 duplicate baseline B19/B22. H4-A13 mistakes a
highlight on yellow B14 for black. The seven new unresolved proposals include
D3's color-uncertain upper body, D4's shaded rear/upper patches, H1's threshold
patch, H4's ambiguous two-feature group, weak reflection, and possible second
feature on B16. Their original uncertainty is preserved.

## Validation, reproduction and stopping point

Python 3.12: **12 tests pass** (5 existing pilot accounting tests, 7 new tests).
New controls exercise translated known black reflections, a dark body without a
reflection, flat paper, colored highlights under two supplied learned palettes,
baseline immutability, no native search in the old-only arm, frozen photo
reproduction, and error/uncertainty accounting. These simple owner-known controls
do not model all photograph edge/shadow failures or establish generality.

```bash
.venv/bin/python -m unittest photo2.test_stage1_pilot photo2.test_stage1_recovery
.venv/bin/python -m photo2.stage1_recovery development --output photo2/output/r238/reproduce-development
.venv/bin/python -m photo2.stage1_recovery transfer --output photo2/output/r238/reproduce-transfer
.venv/bin/python -m photo2.evaluate_stage1_recovery --output photo2/output/r238/reproduce-evaluation
```

The tracked input archive suffices for reproduction without the old ignored
caches. `prepare` rebuilds it only when the R231 profile caches and old detector
rerun are available; do not overwrite a frozen archive during evaluation.
Original photo SHA-256:
`eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`.
[Verification and artifact seals](review/r238/verification.json) record exact
reproduction of 19 generated files and 68 unchanged historical tracked files. Visual interpretations can be
revisited through a disclosed scoring amendment, never silently used to tune
H1/H4. No masks/centroids/physical centers or full-string indices are inferred.

**Stop here.** Recommend a separately authorized, small ownership experiment:
distinguish body-interior reflections from neighboring paper rims and test
same-body versus separate-body grouping on these explicit failure pairs, with
new transfer sections reserved before development. Avoid another broad threshold
sweep; the dominant demonstrated problem is assigning features to bodies. A
later local correspondence test can still use the vetted D3 subset, but no
geometry, helicity, global indexing or repeat inference was begun here.

Retain **GPT-6 Astra / High**, the user-reported active status, for scientific
review and the next bounded design. Recommend `/new` before a new implementation
phase, using this report and the current handoff; no new session is needed merely
to review these results. The user controls switching.
