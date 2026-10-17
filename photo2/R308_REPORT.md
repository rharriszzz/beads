# R308 — global basins and bounded distributed corrections

**No: this run does not meet the stated substantial whole-necklace photographic improvement checks against both R306 and R307.**
Executed all three stages in **19.96 fitting minutes**, including initial native profiling, global sensitivities, response sweeps, distributed and joint work. R306 used87.78 aggregate minutes; R30720.00. The final all-candidate repaired-score audit adds approximately **1.76 minutes** (no new proposals); optimization plus this audit is **21.72 minutes**. These are warm starts using substantial historical computation, not equal cold-start benchmarks. The concrete scientific finding is an inherited false-boundary reward from unresolved native rays. It was repaired after 17.23 fitting minutes; the remaining 2.73 minutes test the corrected treatment, not a complete new global campaign.

[Launch viewer](review/r308/launch.sh) · [Reproduce](R308_REPRODUCE.md) · [JSON analysis summary](r308/results/campaign/analysis-summary.json) · [Before/after](r308/results/campaign/review/before-after.png).

## Which globals matter?

Pivoted QR selects **elevation, phase, turn, roll, minor, axial, tilt, scale** from the native full-circuit Jacobian with correction fields fixed. Finite-difference scales have physical units, so this ordering is conditional on the declared exploration scales; SVD values are not confidence intervals or a statistical identifiability rank. This initial ranking includes dropout/unknown-ray responses in the inherited score; it is not a claim to have identified eight physical constants. Corrected smaller-step matrices and unavailable derivative directions are saved separately.

| Parameter | Perturbation scale | Residual sensitivity norm | Independent QR order | Selected |
|---|---:|---:|---:|---|
| elevation | 1.2 | 2.165 | 1 | yes |
| phase | 0.08 | 1.223 | 2 | yes |
| roll | 1.5 | 1.174 | 4 | yes |
| turn | 0.0007 | 1.112 | 3 | yes |
| minor | 0.08 | 0.825 | 5 | yes |
| s0 | 1.5 | 0.725 | 9 | no |
| scale | 0.12 | 0.621 | 8 | yes |
| axial | 0.035 | 0.549 | 6 | yes |
| tilt | 1.2 | 0.533 | 7 | yes |

Strongest couplings: s0/elevation 0.695, minor/scale 0.620, roll/elevation 0.529, s0/roll 0.523, turn/phase 0.364. Shared directional illumination stays fixed. Integer count, helicity and topology remain discrete; five starts cover the R306/R307 primary and all four R306 physical families. Fixed count and true total arclength determine mean longitudinal spacing, so an independent redundant pitch variable is not added. No physical+1/+6/+7 neighbor identity is invented from highlights; exported neighbor geometry remains conditional.

## Periodic basins and stage contributions

Saved **4 broad one-dimensional curves**, phase/registration and sensitivity-selected coupled grids, and **1 qualifying refinement basin**. The phase sweep contains 7 sampled minima. No sampled phase minimum improves the corrected training score over the original basin. 1 basin(s) met the guard conditions for derivative refinement. Other sampled minima remain saved. Phase spans a complete2pi cycle; registration spans26px. Grid evaluations may cross worse intermediate states. Curves use native surface-compatible reassignment; derivatives inside each basin use fixed owners. Trial owners, missingness and physical failures are retained, so apparent periodic minima cannot be interpreted as verified bead identities.

The global-only training objective changed **20.7836→20.7836**. Stage training losses are **global 20.7836; distributed 20.7836; joint 22.6265** (distributed/joint include the declared small correction penalty). Earlier stage losses use the inherited treatment; repaired joint losses use the corrected treatment and cannot be directly subtracted. The common photographic table compares every stage consistently. This is an objective measurement, not independent evidence of photographic improvement. The following unchanged R307 common metrics determine the scientific conclusion. Comparison evidence has already been exposed historically; it is retrospective, never a new independent test.

| Model | Dense coherent ownership | Visible boundary MAE px | Strong RMS px | Paper | Unexplained color | Rope-width MAE px |
|---|---:|---:|---:|---:|---:|---:|
| R306-primary | 56.62% | 5.51 | 10.02 | 7.80% | 29.58% | 6.92 |
| R307-primary | 56.56% | 5.65 | 10.10 | 7.80% | 29.86% | 6.81 |
| stage-global | 56.56% | 5.65 | 10.10 | 7.80% | 29.86% | 6.81 |
| stage-distributed | 56.56% | 5.65 | 10.10 | 7.80% | 29.86% | 6.81 |
| stage-joint | 56.61% | 5.64 | 10.04 | 7.80% | 29.86% | 6.77 |
| primary | 56.62% | 5.57 | 10.04 | 7.80% | 29.79% | 6.81 |

Development and comparison components, signed tangent/normal errors, dimensions,
separator errors and worst-decile distributions are in comparison.json; all32
geographic regions and regression flags are in regional-changes.json and diagnosis.json.
Original R306 fixed owners have 2 missing lobes; RMS with24px penalties is 9.24px. Their surviving-only RMS is not evidence of identity recovery.

## Distributed corrections and physical validity

Fourier modes1–4 perturb the existing periodic32-knot axis, phase and spacing
fields. Global geometry is fixed during the distributed stage, then alternated
with four selected correction directions at a time. This avoids repeated dense
96-column local Jacobians. Full-chain arclength, phase and occlusion remain active
for every evaluation; no regions are detached and no bead has independent motion.

Maximum new increments: axis **0.0198px**,
phase **0.00023rad**, spacing **0.0016%**.
Their combined projected center displacement is at most **0.105px** (limit **3.112px**,10% of reference face diameter).
Total inherited-plus-new fields: axis_nodes max absolute 8.2671, knot RMS 3.7554; local_phase max absolute 0.42637, knot RMS 0.13996; local_spacing max absolute 0.0041675, knot RMS 0.0013636. Removing all inherited and new fields counterfactually changes projected centers by up to **23.91px**; the10%-diameter bound applies only to new R308 increments. Total phase-rate departure is **0.664%** and spacing departure **0.417%**. The inherited fields and total values are exported separately from new increments.
Conservative amplitude/rate limits and penalties are phenomenological exploration
controls, not measured thread strain or a complete mechanical crochet model.
The primary has **2405 bodies, hand-1, open string**,
one closed periodic geometric axis and **7166 certified spatial close pairs**.
All physical bodies and all811 photographic observations remain represented.

## Native numerical performance and limitations

There are **503 native trials**. Best retained score with no additional missing fitting owners: trial500. Raw minimum: trial133, with1 missing fitting owners. All proposals and repeated copies remain saved. No coarse optics guided this run.
The first five actual whole-chain objective evaluations serve as representative
profiling measurements; every sensitivity, response sweep and contact check is
charged to fitting time. Peak fitting memory **397.8MiB**;
export/diagnosis/verification **497.3s** separately.
Stopped because: **adaptive joint budget**. Native step-size adaptation, if present, is part of the final joint stage and the same cumulative budget; its protocol/source transition is explicitly archived. Per-type evaluation costs, accepted
improvements/time, Jacobians/SVDs and predicted-versus-actual trust reductions
are saved. Native raster ownership and reflection lobes are nonsmooth; a derivative
can mispredict even when the renderer is accurate. Rejected steps and unmatched
lobes stay visible rather than disappearing from the score.

[The S25 diagnostic](r308/results/campaign/review/unknown-ray-separator.png) shows why numerical uncertainty must stay distinct from photographic gaps. A verified inherited defect was repaired at 1033.904 fitting seconds in this delivered campaign: unresolved native rays had created false separator/contour edges and could appear as empty paper. S25 alone jumps5.31→9.62px under a0.06-degree tilt when one unknown ray resolves. The repair excludes uncertain edge transitions and treats uncertain paper conservatively. All old sources/trials survive; only the remaining original budget uses the repair. Post-seal response replays retrace the changed structural blocks at the SAME candidates, with original native optical blocks retained and independently checked against full predictions. Original and corrected objective losses are not interchangeable.

The principal remaining limitation is the measured inability of the tested global
basins plus small corrections to satisfy body ownership, visible boundaries,
background and reflections together. The acceptance record distinguishes actual
photographic gains from lower weighted loss. A failure here is evidence about this
bounded parameterization and explored basins, not proof that a longer run or new
maker labels would fix it. The(1110,336) case was never optimized separately;
before/after metrics and images remain in required-location.json and the atlas. Using only nonreflection positive interiors within90px, local coherence is **52.81% → 52.19% → 52.33%** (R306, R307, R308). This uses identical denominators across models; the earlier R307 local headline also included reflection regions and is not directly comparable. Most fitting predates the numerical-uncertainty repair, so this is not a complete-budget test of the corrected hierarchy.

## Delivery and stopping point

Standalone workflow: `python3 photo2/phase2_hierarchical_fit.py`; restart and output
options are documented in R308_REPRODUCE.md. Atomic transactions, native kernel and
periodicity/effect-bound contracts, original-Python geometry/contact/ray replays,
all-region preservation and actual browser navigation are recorded in the receipts.
The viewer preserves raw pixels, native owner picking, photographic/geometric axes,
recenter/follow, signed error plots, positive-interior overlap and competing owners.
Good, typical, poor and historical failure cases accompany all scientific plots.

Keep the strongest historical candidate available. No adoption unless the explicit
photographic checks pass; no Phase3, pattern inference or automatic R309. Stop after
verified commit/push. Current session/model may be retained for review; no /new needed.
