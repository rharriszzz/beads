# Checkpoint5 — quantitative limits and mechanism validation

Mean J/M IoU0.515 across63 confirmation cues;43 below0.65. Choices:29M/18J/6both/
10abstain. Selected M proposals include6322 route-supported pigment pixels absent
from J; this is measured photographic continuation evidence, not6322 verified
true-body pixels. Same-color seams can still be missed when markers/candidate
material are wrong. No new cue detector, hence zero newly certified distinct beads.

Candidate instability (minimum perturbation IoU<0.7): J2/M19/B19. Domain IoU<0.9:
J5/M7/B5. M’s seed12 and background11 failures dominate; common brightness gain
alone is stable. This is why the new full protocol reveals limits not visible in
R286’s gain-only/ramp checks. Conditional: HSV/paper/learned palette/initial A stay
fixed; seed shifts also fit inside a93px M window. No physical-relighting claim.

N07 proves the false fallback:227/227 added pigment pixels have direct continuity,
but M becomes1325px under background-low or1275px under seed-right. The selector
therefore chooses J288px, losing genuine diffuse material. N11 similarly selects
J167px despite525/527 supported M-only pixels. Do not describe these choices as
reliable merely because their algorithmic reasons are interpretable. N12 both
includes a questionable M appendage. C02 weak-edge abstains, but its different
central context anchor chooses M; not an endorsement of the user's rejected edge.

Mathematical controls preserve monotone shading and narrow bright material100%;
only31.25% of added pixels survive a dark-seam/renewed-surface example. Identical
pixels assigned a deep-internal-texture explanation yield identical evidence;
physical identity cannot be recovered from those pixels alone. No new physical
rendering is needed to establish this selector-mechanism limit. Real photos remain
primary. Black data are hash-preserved, not re-estimated in R287.

108 tests pass (17new+91historical). Next exact replay, historical/native audit,
compact review browser check, final recommendation and scoped delivery. No tuning.
