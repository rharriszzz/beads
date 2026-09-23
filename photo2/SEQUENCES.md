# Known-index sequence validation — R036

The sequence solver preserves unknown observations, rejects contradictory periods
with witness bead indices, and keeps unsupported slots and alternative patterns.
The maker's 30-bead example and both historical 40/13 patterns pass the synthetic
checks. This validates the sequence component with known indices and authored
color labels. It does not recover photo 2 or validate automatic color reading.

## Reproduce

Use Python 3.12 and the local environment, from the repository root:

```sh
.venv/bin/python photo2/sequence_audit.py --output photo2/output/sequence-audit-new
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The output directory must be new or empty. The default input is the preserved
`photo2/output/legacy-visibility-verified/` R023 report and artifacts. The audit
verifies all seven historical source hashes against Git
`ab7915841577c27cfb03f779cc765e556ffc9dcd` and all 74 artifact hashes before using
its per-bead visible pixel counts. It does not compare historical source hashes
against today's renamed `Helicity` sources.

If those ignored artifacts are absent, regenerate at the historical revision in
a separate checkout; keep the environment in the current beads checkout. With
POV-Ray installed and `/tmp/beads-sequence-r023` unused:

```sh
git worktree add --detach /tmp/beads-sequence-r023 ab7915841577c27cfb03f779cc765e556ffc9dcd
.venv/bin/python /tmp/beads-sequence-r023/photo2/practice_legacy.py --output /tmp/beads-sequence-r023/photo2/output/practice
.venv/bin/python /tmp/beads-sequence-r023/photo2/legacy_visibility.py --practice /tmp/beads-sequence-r023/photo2/output/practice --output /tmp/beads-sequence-r023/photo2/output/visibility
.venv/bin/python photo2/sequence_audit.py --visibility /tmp/beads-sequence-r023/photo2/output/visibility --output photo2/output/sequence-audit-new
```

These fallback commands follow the existing historical renderer interfaces; they
were inspected, not executed again in R036. Render timestamps can change report
and PNG byte hashes. The audit records the supplied report's actual hash and
whether it is the original R023 report, while always verifying its source and
artifact hashes. No new visibility rendering was required for this step.

Final inspected output: `photo2/output/sequence-audit-final/`. Its report SHA-256:
`b0a9fe4b011eeb3f95570cd1a3eb626bd3c80dcb8790e5fe1bc84132dede3b80`.

## Inputs and separation of evidence

The maker's example is stored in `staircase-pattern-30.json` as one concatenated
repeat: `123333, 112333, 111233, 111123, 111112`, with 1=red, 2=yellow, 3=black.
The authored block is primitive with length 30. Twenty complete repeats (600
beads) are a benchmark choice. Its omissions are artificial, with no rendered
visibility claim. The historical fixtures retain 800 beads for length 40 and
780 beads for length 13. Both views are tested separately at T=12 and T=100
visible pixels on the original 2400×1800 raster. Those thresholds remain
synthetic masks, not calibrated photo readability rules.

Historical symbols 0/1/2 are mapped to red/yellow/black for this symbolic test;
the older beauty renders retain their red/green/blue appearance. Authored colors
and absolute indices supply the experiment's observations. Neither their true
period nor source pattern is passed to the solver. Evaluation uses truth only
after scanning and fitting the observations.

Each of the nine base cases has eight variants: base, four Bernoulli-erasure
cases (rates 0.1/0.3, PCG64 seeds 17/43, readable positions in increasing original
index order), all unknown, one entirely erased supported slot, and one wrong
color at a position with another readable same-slot occurrence. Rates are draw
probabilities, not exact deleted fractions. Exact erased/changed indices are
retained. The wrong reading is a negative control, not a proposed maker error.

`partial_word.py` accepts a fixed-length array of integer colors 0/1/2 or `None`.
Missing beads and unreadable colors both preserve positions; this sequence-only
interface does not classify why a position is unknown. A trial period is strong
when every observed color at the same residue agrees. Conflicts include the first
witness pair of original positions. Supported slots retain **all** supporting
positions, while unsupported slots remain `None`. Observations are never filled
in or deleted in place. No majority vote, truth-based repair or color relabeling
is used.

The full benchmark range is 1..floor(N/2); each candidate separately records
whether it divides the known exact synthetic N. This domain requires at least
two repeats and is not a photo prior. The caller may omit `exact_count`, yielding
no closure flag. Photo 2's supplied <400 repeat bound is saved for future work;
its provisional 2,698 bead count is never used as an exact modulus/divisor filter.

## Results

| Base input | Readable beads | Compatible periods before exact closure | Slots supported at true L |
| --- | ---: | --- | ---: |
| Maker 30, complete | 600 | 30, 60, …, 300 | 30/30 |
| 40, phase 0, T12 | 547 | 40, 80, …, 400 | 40/40 |
| 40, phase 0, T100 | 515 | 40, 80, …, 400 | 40/40 |
| 40, phase half, T12 | 550 | 40, 80, …, 400 | 40/40 |
| 40, phase half, T100 | 493 | 40, 80, …, 400 | 40/40 |
| 13, phase 0, T12 | 538 | 13, 26, …, 390 | 13/13 |
| 13, phase 0, T100 | 489 | 13, 26, …, 390 | 13/13 |
| 13, phase half, T12 | 532 | 13, 26, …, 390 | 13/13 |
| 13, phase half, T100 | 494 | 13, 26, …, 390 | 12/13; slot 0 unknown |

The same candidate lists persist in the four random-erasure variants and the
missing-slot variants. The shortest compatible length matches truth in these
cases, but that is not a general uniqueness result. Longer accepted candidates
can contain unsupported slots and admit different completions. Only the complete
30-bead base has every compatible candidate fully specified and reducible to the
same primitive pattern.

Exact whole-repeat closure leaves:

- N=600: 30, 60, 120, 150, 300.
- N=800: 40, 80, 160, 200, 400.
- N=780: 13, 26, 39, 52, 65, 78, 130, 156, 195, 260, 390.

All 63 uncorrupted inputs retain their true period with correct supported slot
colors. Completely unknown inputs accept every tested period with no slot
support. Entirely erased slots remain unknown. At L=13, phase half/T100 slot 0
admits three different completions even after rotation/reversal normalization.
The missing-slot control in that view also erases slot 2, retaining both unknowns.

All nine wrong-color inputs reject the true period with a conflict witness. The
four length-40 cases nevertheless accept longer alternatives: 200/400 at phase 0
and 400 at phase half. The other five wrong-color cases reject every candidate
in the tested domain. Thus accepting some period cannot certify that observed
colors or bead correspondence are correct.

Four contiguous quarter holdouts per input produce **288 fold checks**. Each
fold first freezes its training-compatible candidates and slot colors, then
scores readable held-out positions with correct/wrong/abstained counts. Results
for every training-compatible candidate are retained, including those that fail
on held-out colors. Across the 63 uncorrupted inputs at the evaluator's true
period, there are 24,383 correct predictions, zero wrong, and 52 abstentions.
These totals pool overlapping benchmark variants; they are not independent-photo
accuracy estimates. The 52 abstentions occur when a slot has evidence only in the
held-out quarter. All-unknown folds have no readable held-out targets and therefore
zero predictions, not evidence of success.

## Presentations and completions

Complete patterns reduce to their primitive cyclic block, then choose the
lexicographically smallest rotation across both directions with physical color
labels fixed. A partial pattern keeps its stated length and explicit unknowns;
its canonical key describes a family of constraints. No inferred reduction of
an incomplete block merges different possible completions. Per-candidate support
remains in the original index convention, separate from presentation keys.

Equivalent complete presentations are grouped, but partial families of different
lengths are retained even if some completions overlap. The grouping is not a
count of disjoint complete patterns. For the evaluated true-period fit, up to
four free slots are exhaustively completed and normalized; larger families are
represented by the slot constraints and `3**free_slots` assignments rather than
listing exponentially many sequences. This count uses a three-symbol alphabet;
it does not impose that every hypothetical completion contains all three colors.
All other candidates likewise preserve full slot constraints without guessing.

## Artifacts and checks

`summary.csv` includes every case's complete candidate and closure lists.
`candidates.csv` includes support counts and unsupported indices for every accepted
candidate. `holdouts.csv` gives every frozen candidate's fold results. Each of the
72 `cases/*.json` files stores the original indexed observations, erased/changed
positions, accepted slots and supporting indices, rejection witnesses, canonical
families, frozen fold slot colors, and separate truth evaluation. `indexed-inputs.json`
retains source patterns, base masks and original visible pixel counts.

`evidence.png` illustrates original observations versus separately inferred colors
and unsupported slots, conditional on the stated L. Both panels were visually
inspected. It is a sequence chart, not a POV-Ray material or appearance result.

All 32 repository tests pass, including seven new sequence tests. An independent
pairwise oracle checks all 6,372 word/period combinations for lengths 1..5 over
three colors plus unknown. Tests cover the hole-between-conflicts counterexample,
unaltered unknowns, optional closure, frozen holdouts and abstention, rotation/
reversal and physical color identity, distinct completions and invalid inputs.
Compilation and whitespace checks pass. Existing scene sources are unchanged;
no additional full-render regression was needed beyond the existing suite.

Final and reproduced runs have all **77 output artifacts byte-identical**; reports
agree except for their command/output path. Six current source hashes, all seven
historical source hashes and 74 historical artifact hashes were verified.
`report.sha256` binds the report separately to avoid a self-referential checksum.
Generated artifacts (about 168 MB per run) and the environment stay ignored.
The earlier `sequence-audit-01` and `sequence-audit-verified` runs are development
records preceding the regenerated-report portability adjustment. No failed test
or audit assertion occurred.

## Next bounded task

Test automatic neighbor proposals on the existing synthetic views, using visible
mask centroids as supplied detections, with anonymous IDs and no source bead
indices or colors in edge construction. Evaluate proposed ±1/±6/±7 labels against
hidden truth, especially at bends, occluded edges and crossings; retain ambiguity
and abstentions. Mask-derived detections are still oracle segmentation, so this
would test edge inference only. Stop after an illustrated edge-accuracy/relative-
index report and checks, before beauty-image segmentation or photo fitting.
Use gpt-6-astra / High and a fresh `/new` for this separate perception task.
