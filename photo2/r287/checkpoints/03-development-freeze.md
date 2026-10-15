# Checkpoint3 — v2 development and freeze

V2 replaces v1's high outside/inside ratio with three direct J-to-M-only routes.
Normal declining brightness is allowed if pigment persists; a deep valley plus
renewed rise is not. At least2/3 routes must be supported; ≥85% of eligible added
pigment must pass, ≥50 pixels and ≥30% of J area for material significance. These
are explicit engineering criteria, not fitted probabilities or color-specific rules.
Seam/stability/material vetoes remain unchanged. No support union/intersection.

On26 development cues:13 preferM,4 preferJ,3 both,6 abstain. P5 chooses stable J;
nominal M664 is good but sigma0.5/background-high/seed-left/up merge to1270–1297px.
P2 chooses M:295/295 added pigment pixels have supported direct routes, preserving
495px versus J200. C05 anchor chooses M with279/279 supported additions, retaining
its imperfect527px support. C02 weak-edge E9 cue abstains. The separate C02 central
context anchor chooses M; this must not be presented as agreement with the user's
broad negative edge judgment. No extra C02 tuning. P1 both; P3 M due J background
sensitivity, even though the user previously liked J better: preserve that tension.

C04 fresh merger abstains through cue/domain/area evidence; C07 overlaps remain
multiple observations, not distinct beads. Tiny tinted features can still receive
a J/M preference. A selector does not solve upstream color or physical ownership;
all reliability remains unrated. No hybrid is justified. No manual answer input.

Freeze candidates.py/evidence.py/selector.py and selection hashes now, before any
new16-region/63-cue result is generated or inspected. Confirmation results, including
bad preferences, will be retained without retuning. Next: all new-region images,
quantitative choice/coverage/overlap, mechanism tests and final review package.
