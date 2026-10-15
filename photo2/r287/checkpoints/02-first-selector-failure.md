# Checkpoint2 — first selector failure and retained revision rationale

All78 baseline J/M/B masks on26 development observations replay exactly. Sixteen
new regions/63 cues were already selected; none has been evaluated or viewed.
First v1 selector/source/evidence/results saved as selector_v1.py, evidence_v1.py,
development-v1.json.gz. No confirmation tuning.

V1 abstains P2 despite295 genuinely pigment-consistent M-only pixels, because its
boundary test demands outside intensity >=70% of inside. That is the wrong evidence
for diffuse shading: a valid decreasing brightness profile can cross J's high
isophote and remain same-colored material. The high gradient is not a separating
valley. Simply weakening that ratio until P2 passes would repeat the original error.

Revise the measurement idea: examine three nearby direct native routes from J to
M-only material. Preserve lower brightness if hue/material continues without a
valley followed by renewed rise. Report the added pixels supported by this test,
their brightness and failed routes; neighbor-seam and stability vetoes still apply.
This is selection evidence, not automatic pixel union or modified J/M masks.
Use both rather than forced preference when plausible disagreement remains.

P5's M664px nominal mask is good but the new sigma perturbation exposes a large
merger; J is stable. Preserve the perturbation failure. The selector may reasonably
prefer J there, based on stability rather than the user's answer. C02 weak-edge
cue already abstains; do not tune it. Some tiny tinted-highlight colored proposals
survive v1; choosing among supports does not resolve the upstream color/feature
classification. Preserve that limitation, do not certify them as physical beads.
