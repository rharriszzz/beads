# Checkpoint 5 — additional real-photo validation

Ten disjoint native128px crops contain249 unique frozen image cues:130 red,
73 yellow,46 black, including unresolved proposals. The seven automatic crops
include strong red/yellow crossing supports, a strong black reflection, opposite
sides, a three-feature group, the weakest stored near black peak, and the closest
same-color cue pair at14..30px. Selection rules and source IDs are saved before
method comparisons; source-to-current cue distances are0..2.24px. These are not
blind recall ground truth or confirmed distinct bodies.

Inspection: T is conservative on the clear red/yellow examples; E/W leak into a
neighbor on auto-yellow. I/J make an artificial crescent on auto-red. The second
auto-same-color cue is itself unreliable near a reflection/material interface;
I/J wander and J exceeds870px. Keep this failed selection, not a hand-picked
replacement. Paper-facing false candidates remain visible in full overviews.

Critical black failure: on auto-weak, R1 joins a weak feature to a stronger upper
highlight,129px/5.43px shift. R3 inherits the merger. R2 retains25px/0.93px shift.
Therefore R1 alone cannot be recommended generally. Add R4: prominence watershed
of the reflection intensity field followed by R1's isophote and native threshold
inside the selected feature basin. Same16% contrast; prominence=max(.003,10% of
smoothed local peak). R4 retains22px/2.53px shift on auto-weak and keeps reviewed
upper/lower41/25px masks unchanged. It assigns intensity features, not bead bodies.
Basin clipping and false partitions remain explicit limitations.

A two-Gaussian weak/bright bridge mathematical control reproduces R1's merger;
R4 retains the weak peak and excludes the bright peak. R2 can substitute a nearby
component when its threshold excludes the weak seed: another preserved failure.
One black cue in auto-three has an ineligible pigment/paper peak; record the flag,
withhold any reliability claim. All methods remain unresolved; over870px outputs
are rejected diagnostics. Next finish quantitative tables, review browser/replay,
source-preservation audit, and final recommendation. No production adoption.
