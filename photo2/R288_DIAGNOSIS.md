# R288 diagnosis — completed before new segmentation implementation

The abrupt N07/N11 changes are demonstrated failures of M's minimum-interface
rule, not evidence that all fuller diffuse material is unreliable. Original M
preserves a separation only when it has at least three interface pixel pairs AND
its maximum saddle/reference ratio is below .65. A shorter interface defaults to
a merge, even if every available interface pixel is very dark.

## N07: a newly eligible two-pair connection admits an upper group

Baseline M has 515 pixels and one target marker at local(47,48). Lowering the
background changes the floor from .0607166 to .0570096. The target gains a two-pair
interface with the upper marker at(39,19). Its maximum ratio is only .16650 and
both pairs are dark, yet the three-pair requirement fails and M merges. The upper
marker already connects to another marker; the result is 1325 pixels. Seed-right
similarly produces 1275 pixels, with the same .16650 two-pair connector after
coordinate translation. Target feature identity is preserved; new group unions
cause the large expansion. Marker count also changes with eligibility, but loss
of the target or disappearance of a required competitor is not the demonstrated
cause here. Existing original masks and full replay ledgers are preserved.

## N11: stricter threshold paradoxically makes the support larger

Baseline M is 694 pixels. Target marker(48,46) is separated from marker(6,43) by
three pairs, maximum ratio .24169. Raising background changes the material floor
from .0438842 to .0470811 and removes one interface pair. Now two pairs remain,
still maximum ratio .24169 and all dark. The separation test becomes false and
five markers merge into the target group, producing 2018 pixels. The marker count
remains nine. Thus this particular instability is not missing-marker detection:
it is a discontinuity in how insufficient interface length is interpreted.

The nominal upper extension is a DIFFERENT issue. Its top 24 support pixels have
native Y .0393–.0935 (median .0549), hue0–9.80 degrees (median6.00), saturation
.921–1.0. Lower central material has median hue−1.57, while the lower diffuse area
has median−4.63. These upper pixels are dim, highly saturated and still compatible
with the broad learned red gate (prototype353 degrees). They approach yellow
material and have a color shift, but this alone does not establish another bead.
The old direct continuation test accepts525/527 M-only pigment pixels. Twenty-one
of the top24 pixels also survive at least85% of the original perturbations: stable
pixels can still have uncertain ownership. It would be unjustified to label their
removal a confirmed correction simply because a shorter contour looks cleaner.
R288 will test evidence-based construction, preserve residual uncertainty and
explicitly report if this extension remains unresolved.

## N06 and earlier controls

N06 nominal M1148 merges two yellows across two dark pairs (maximum ratio .19737).
Background-low yields three pairs and separates them, giving584 pixels. This is
the same interface-length defect, not a change from a dark to a bright boundary.
P5 can also remerge under perturbations, while P2 remains a stable495-pixel diffuse
interior. C05 remains acceptable but imperfect. These cases test whether an
improvement repairs the merging decision without reintroducing peak truncation.

## Next hypotheses and causal tests

1. Do not treat missing separation evidence as positive merge evidence. Preserve
   dark small interfaces and their uncertainty; require supported bright continuity
   to join basins. Prevent a later indirect union from undoing a supported seam.
2. Construct a supported interior from consistent results and direct pigment routes,
   rather than rejecting all material when one parameter setting merges a neighbor.
3. Stable material alone is not ownership truth: N11's upper extension may survive.
   Compare independent seam/profile evidence and preserve an alternative explanation.

See [N07 diagnostic](review/r288/N07-diagnosis.png),
[N11 diagnostic](review/r288/N11-diagnosis.png),
[N06 diagnostic](review/r288/N06-diagnosis.png) and
[all original-M replay ledgers](r288/results/diagnosis.json.gz).
These are demonstrated native-image mechanisms; no physical model was used.
