# R236 — Stage 1 failure diagnosis and proposed recovery experiment

Saved under R237. **Proposal only; implementation is not authorized.** Session
status reported by the user: **GPT-6 Astra, reasoning High**. Older Sol/High
recommendations do not identify the active model. The user will report changes.

The [R235 pilot](STAGE1_PILOT.md) found 76/109 provisional eligible observations
automatically, with 33 assisted additions. Overly restrictive acceptance rules
explain several clear failures. The approach has not reached a dead end, but
tests for a good interior seed do not match the current eligibility criteria.

## Diagnosis from the photograph and detector traces

Reviewed all four annotated sections, original D4/H4 crops, saved colored-candidate
profiles, and the unchanged black detector. This diagnoses traced examples, not
an exhaustive causal classification of all 33 misses.

| Stage | Evidence and implication |
| --- | --- |
| Candidate generation | Many missed colored beads already have candidates. H4-B12 has yellow support at its reference location but no nearby yellow candidate on that face, so generation also has gaps. |
| Color classification | D4-B02/B03/B05 and B24 already have correctly colored candidates. Their absence is not a red/yellow labeling error. M4 nevertheless requires consistent color along several cuts; highlights and partial surfaces can fail this requirement despite convincing colored pixels elsewhere. |
| Profile acceptance | M4 requires darker flanks in two perpendicular directions. The examined D3-B07 candidate passes color on all 12 cuts but fails the brightness-drop test on all 12. D4-B24 has good cuts without the required perpendicular arrangement. Recognizable surfaces are rejected. |
| Reflection detection/context | D4-B26's reflection is generated, then rejected as having an insufficiently dark surround. H4-B34's reflection is rejected as associated with a colored interior. The photograph supports examining neighboring-body contamination of these context tests. |
| Search-region exclusion | D4-B08 and H4-B13/B25 reach the black-candidate stage, then are excluded near the approximate search-band edge. Other features are excluded earlier. This conflicts with admitting sufficiently visible side faces. |
| Duplicate suppression | Fixed-distance suppression risks merging distinct observations, but it is not established as the cause of the examined misses. Loosening it blindly risks duplicates, especially in ambiguous groups such as H4-B22. |

See the [D4 image](review/r235/D4-reviewed.png) and
[H4 image](review/r235/H4-reviewed.png), alongside their
[D4 original](review/r235/D4-raw.png) and [H4 original](review/r235/H4-raw.png).
The colored evidence is archived in `output/r231/profile-pool.json` and
`output/r231/profiles.npz`, interpreted by [compare_seed_methods.py](compare_seed_methods.py).
For example, profile-pool entry 21 is the D3-B07 candidate at (1336,249);
entries 1934 and 1936 are D4-B24 candidates at (1799,1678) and (1788,1680).
Proximity locates candidates for inspection; it is not a proof of body ownership.
R192 records 585, 333 and 336 preserve the cited later edge exclusions.
The read-only black-detector rerun used [auto_label_beads.py](auto_label_beads.py),
whose SHA-256 still matches the R192 preserved source:
`57855ac1c9c382a2fe03ef4c49e1eb5c181df4aa9cbdd62299116954c01dbbcd`.

## What can likely improve

Relatively small repairs look promising: reconsider edge exclusions, retain
correctly colored candidates rejected solely by profile shape, and improve how
a reflection's dark-body support is distinguished from neighboring colored beads.
The deeper problem is equating one brightness feature with one bead and using
point distance to decide identity. Multiple highlights, touching same-color bodies
and partial exposure require local body evidence; thresholds alone will not resolve
them. Neither the size of the attainable gain nor its precision is established.

Use separate methods:

- **Red/yellow:** prioritize coherent colored patches; brightness profiles support
  acceptance rather than impose a mandatory bead-shaped signature.
- **Black:** detect compact reflections at native resolution, then examine dark
  support and competing colored-body ownership. Do not require a uniformly dark
  circular neighborhood. Black without recognizable reflection remains deferred.

## One bounded next task: recover rejected observations

**Inputs:** original photograph, frozen R235 references and section boxes, existing
colored candidate pool, and black candidate/rejection records. Preserve the R235
eligibility rules, uncertain references, five boundary credits and disclosed
reference amendment. Reference positions are evaluation data, not runtime seeds.

**Comparison:** (1) frozen baseline; (2) a supplement that re-evaluates existing
rejected candidates using local surface evidence; (3) the same supplement plus
a native-resolution reflection search for genuinely absent candidates. Record
which step supplies each recovery and every rejection/merge reason. This tests
whether the bottleneck is candidate availability or subsequent acceptance.

**Validation:** develop only on D3/D4, freeze the rules, then evaluate once on
H1/H4. These are transfer checks, not newly unseen holdouts. Audit every addition
for ownership, color, duplicates and paper/shadow confusion. Preserve ambiguity;
two reflections do not establish two beads. No manual additions count as automatic
recoveries, and unresolved additions do not count as successes.

**Proposed success target, not a forecast:** recover at least 8 of 16 colored
misses and 9 of 17 reflection-supported black misses, retain the existing 76
correct detections, and introduce zero confirmed false, duplicate or wrong-color
accepted observations. That would provide at least 93/109 conditional coverage,
not complete Stage 1. Report all new unresolved cases separately; zero confirmed
errors does not certify ambiguous candidates.

**Stopping point:** deliver the comparison and candidate-level audit, including
a failed result if the target is not met. Stop before global indexing, geometry
changes or repeating-pattern inference. Do not tune on H1/H4 after evaluating them.

## Observations already useful for an initial geometry test

[D3-B09–B14, B18, B19 and B21](review/r235/D3-reviewed.png) are nine automatically
supported observations spanning colored faces and black reflections. Their
arrangement can support testing local correspondence hypotheses and both helicities.
Locations remain surface evidence, not physical centers. Their availability does
not establish Stage 1 completion, unique helicity, or correct neighbor/index labels.
This is a possible subsequent experiment, not a second authorized implementation.

Current recommendation: review and approve or revise the bounded recovery task.
Retain the user-reported Astra/High session; no `/new` needed for discussion.
