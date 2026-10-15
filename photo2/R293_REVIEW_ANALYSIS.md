# Completed R293 review — proceed to bounded Phase 2 in R294

The completed local review contains **eight events for eight cases: six A
acceptances and two “substantially wrong, although the photograph is clear”
judgments**. All eight Start Here questions were answered, each at revision 1.
There are no revisions, optional diagnoses, ownership answers, partial answers,
insufficient-photograph answers or not-sure answers in this ledger. The review ran
from 2026-10-15T20:34:57.236624+00:00 to 20:37:58.815172+00:00.

**Decision: proceed next session to R294, a bounded, conditional Phase 2 experiment
using selected independent photographic observations.** This does not certify a
complete bead inventory or authorize treating every automatic mask as trustworthy.
This session archives and analyzes feedback only; it does not begin R294.

## Complete judgments and their meaning

Coordinates below are the original selected bright-feature points, in EXIF-oriented
native pixels (x right, y down). Each answer concerns the exact displayed A proposal;
none of these eight cases had a B alternative. The viewer asked for a good
**visible-region boundary**, not a complete physical silhouette. Photographic
interpretations below are analysis of the saved pixels, not optional user diagnoses.

| Case / native crop | Feature point | Frozen split | Final judgment | Interpretation |
|---|---|---|---|---|
| [central-2246-1448](review/r293/crops/central-2246-1448.png) | (2246, 1448) | Reserved | A | Useful yellow visible material; separation from the nearby yellow target is retained. |
| [central-2264-1469](review/r293/crops/central-2264-1469.png) | (2264, 1469) | Reserved | A | The other target in the opposite-side yellow pair is also accepted. |
| [central-0408-0762](review/r293/crops/central-0408-0762.png) | (408, 762) | Reserved | Wrong-clear | Proposed region extends through several red surfaces and some yellow material; target ownership fails despite a clear photograph. |
| [central-2140-2471](review/r293/crops/central-2140-2471.png) | (2140, 2471) | Reserved | Wrong-clear | Proposed yellow region spans multiple neighboring surfaces; this is an algorithmic merger, not photographic insufficiency. |
| [central-2266-2199](review/r293/crops/central-2266-2199.png) | (2266, 2199) | Development | A | Useful red visible material without requiring every physical boundary. |
| [central-0241-1177](review/r293/crops/central-0241-1177.png) | (241, 1177) | Reserved | A | Useful illuminated yellow region; full dark/diffuse extent need not be inferred. |
| [central-1088-2841](review/r293/crops/central-1088-2841.png) | (1088, 2841) | Development | A | Useful independent reflection region, not a measured black-body silhouette or physical bead center. |
| [central-0266-1021](review/r293/crops/central-0266-1021.png) | (266, 1021) | Reserved | A | Useful red region, despite another bright feature inside; this is not an explicit pair-ownership answer. |

Six reserved cases received four A and two wrong-clear answers; the two development
cases received A. All eight targets are within 26px of the image-derived centerline
and passed R293's illumination sampling proxies. They were deliberately selected
for review diversity, including suspected failures. The fraction 6/8 describes this
queue only; it is not an estimate of whole-necklace accuracy. Forty of the 48 new
R293 cases remain without human judgments. Older judgments remain separate.

## Mechanisms supported and limitations exposed

The accepted opposite-side yellow pair shows useful separation in a relevant
centerline neighborhood. Its saved A masks have 437 and 393 pixels and a common
61-sample tracked separator; neither crosses the saved separator samples. The
accepted red and yellow material examples support retaining complementary darkness,
illumination edges and local material continuity. The reflection acceptance supports
the permanent black-measurement contract: measure the illuminated reflection
independently and leave its physical body center and ownership unresolved.

These are qualitative validations of the combined proposals. They are not an
ablation proving which mechanism caused success, exact pixel truth, or new ownership
labels. In particular, central-2266-2199 is accepted with only 65.5% automatically
supported boundary sides, while the rejected yellow merger has 89.9%. A support
threshold would therefore be a poor substitute for photographed target ownership.

The two rejections share a general failure: **locally credible edges and connected
material do not ensure that the enclosed region belongs to the selected target**.
Same-color continuity can traverse several beads; material changes on the outside
of a merged group can provide a strong but irrelevant outer contour. The saved red
failure also contains yellow material. Enforcing already-detected local separators
does not discover every intervening separator or prevent extension in other directions.

| Saved diagnostic for A | Rejected red: 0408-0762 | Rejected yellow: 2140-2471 |
|---|---:|---:|
| Candidate pixels | 1877 | 3202 |
| Other detected bright features inside | 4 | 7 |
| Tracked separator arcs | 4 | 1 |
| Final saved valley crossings / both-bank inclusions | 0 / 0 | 0 / 0 |
| Unresolved separator endings | 8 | 2 |
| Automatically supported boundary sides | 68.7% | 89.9% |
| Minimum saved perturbation IoU | 0.9926 | 0.9972 |
| Candidate-centroid sensitivity | 0.154px | 0.084px |
| Independent patch to candidate centroid | 35.42px | 36.81px |

The last distance describes disagreement between two different measurements, not
physical-center error or a geometric rejection criterion. Large regions are not
wrong merely for being large. Here the saved pixels and human wrong-clear answers
establish the failures. Zero crossings and excellent stability establish neither
correct ownership nor accurate centroids. The zero bank counters concern the arcs
actually measured; they do not certify absence of all neighboring material.

All T1–T8 measurements and contradictions are retained in the archived candidates
and machine-readable analysis. In these examples T1 misses unmeasured interfaces;
T2/T3 continuity and color may support a merged group; T4 lists other highlights
without establishing their owners; T5 does not resolve every shading alternative;
T6 junctions are contextual evidence, not occluder identities; T7 leaves endings
unresolved; T8 stability can repeat the same wrong answer. Conversely, the accepted
central-0266-1021 contains one other feature, so “another highlight inside” is not
a universal rejection rule. No coordinate-specific or judgment-based runtime rule
has been introduced.

No reviewer answer identifies genuinely insufficient photographic evidence in this
queue. This does not imply that every dark silhouette is measurable; it means the
two rejected central cases must remain labeled clear-photo algorithmic failures.
No new internal-darkness false split or truncation was explicitly reported. Empty
optional diagnoses do not certify that every included or excluded pixel is correct.

## Relation to R291/R292 and Phase 1 readiness

R293 reused the frozen R292 inference unchanged. These are additional judgments on
new photographic locations, not improvements or regressions caused by a new detector.
The 13 R291 acceptances and four R292 acceptances remain intact, alongside their
partial/rejected cases and revision history. The six newly accepted R293 proposals
bring the linked review evidence to 23 accepted case-version proposals across these
rounds, **not 23 certified distinct beads**. No unchanged historical case was asked
again. The older Phase 1 export is preserved as delivered; this archive adds linked
evaluation evidence without rewriting that export or production measurements.

R291's 13/14 and R292's 4/11 acceptance fractions used different selected populations;
neither is directly comparable to R293's 6/8. R292's repaired reserved-yellow-05
remains accepted, while the new mergers show the limits of separator completeness.
There is useful accepted behavior to carry forward, and clear failures to retain
as regressions; another peripheral-silhouette campaign is not a prerequisite.

R293's coverage assessment still establishes independent feature availability in
385 inspection windows, both-side features in 358 and separator-supported context
in 303. It does not establish complete or distinct-bead coverage. The 271 nearby
feature ambiguity pairs and 28 historical-location discrepancies remain unresolved.
The feedback improves confidence in a selected observation subset, not all 1545
features, all 48 new masks or every centerline station.

For the future bounded R294 experiment:

- Use selected well-observed independent patches and exact reviewed visible-region
  versions; keep raw pixels, alternative measurements, uncertainty and provenance.
- Exclude the two rejected masks and their region centroids from trusted material
  inputs; retain their independently detected patches as observations with unresolved
  ownership. Do not discard the photographed targets or replace them with predictions.
- Keep reflections as reflections. Allow multiple or unmatched correspondences;
  neither reflection location nor visible-region centroid is a physical bead center.
- Assess a bounded conditional geometry/common-illumination interpretation on clear
  observations, with independently held-out observations and original-pixel checks.
  No inferred correspondence may certify, move, manufacture, recolor or replace its
  Phase 1 inputs. Do not require a complete necklace inventory or a fixed bead quota.
- Retain central ownership failures explicitly and defer difficult peripheral
  silhouettes. This decision does not authorize global indexing, Phase 3 pattern
  inference or production replacement.

This records the next-session decision and constraints, not a started Phase 2 fit,
chosen physical model, R294 implementation or finalized R294 experimental design.

## Archive, provenance and reproducibility

The [complete archive](r293/evidence/completed-r293-review.tar.gz) preserves all
17 live feedback files byte-for-byte: the original JSONL ledger and eight immutable
candidate JSON/native-crop pairs. A [standalone ledger archive](r293/evidence/completed-r293-review.jsonl.gz)
also preserves the original bytes. [Machine-readable analysis](r293/evidence/completed-r293-review-analysis.json)
records every original file hash/size, event/revision history, final answers, exact
coordinates, candidate digests, algorithm/parameter provenance, T1–T8 evidence,
position alternatives and tracked source hashes at commit
`7e30d3a6e2bed1848ff84f7670a8e6b5901fdb1b`.

Original ledger SHA256:
`c3bf6b1fc830076244652fb28f142a1f2bfdfb76f4a14b436cbf56410e114994`.
Original photograph SHA256:
`eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`.

Validation checked all eight event payloads against their immutable candidate
versions, algorithm/parameters, feature points, displayed masks/separators, question
and position fields; all snapshot digests and crop hashes match. All eight candidate/
crop pairs are byte-identical to the tracked R293 package. All eight decoded crops
match the EXIF-oriented original photograph exactly. Deterministic archive and
analysis replay pass. The live feedback is unchanged; archive creation refuses to
overwrite a different prior archive. No synthetic imagery or new segmentation was
used, and no scientific outputs, detector, viewer or production methods changed.
The [validation receipt](r293/evidence/completed-review-validation.json) also records
hash verification of all 12002 previously inventoried scientific files and 52 earlier
live feedback files: all unchanged. No browser rerun was needed because the viewer
was not modified.

Reproduce verification from the tracked archives (live feedback is not required):

```bash
.venv/bin/python -m photo2.r293.completed_review --check
```

To reproduce archive creation from the original local feedback, use the same command
without `--check`. Changes in later feedback require a separate archive version.
**Stop here. R294 is the next bounded experiment; it has not begun in this session.**
