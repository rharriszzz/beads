# R303 — height-constrained pitch and cross-region consistency

**This bounded experiment does not establish a more convincing reconstruction
from fixed source-height coupling.** The source value is verified as0.975, but
the retained fixed-source candidates have photographic contradictions. Free
pitch and freely calibrated height-coupled pitch produce viable local alternatives;
their different finite-budget results do not establish different physical models.
No reconstruction or coefficient is adopted as recovered truth.

[Review](review/r303/index.html) · [Reproduce](R303_REPRODUCE.md) ·
[All component metrics](r303/results/comparison.csv)

## What the source actually says

In `beads.pov:150–157`, `exact_beads_per_row=nbeads/nrows` and
`chain_major=.65*(2*bead_radius)*1.05*nrows/(2*pi)`. Thus one minor-helix
revolution advances along the major centerline by0.6825 nominal face diameters.
The macro at169–181 sets axial half-height to
`height_per_bead_size*bead_actual_radius`; the usual0.70 argument and relative
size1 give axial height H=0.70D. Therefore row advance/H=0.6825/0.70=**0.975**.
Per-bead advance is row advance divided by `exact_beads_per_row`, approximately
0.105D at6.5 beads/turn. `photo2/bead_placement.py` implements the same major
radius, row count and mapping. Some macro calls use other heights, so0.975 is
the usual-source hypothesis, not an invariant of every macro argument.

Face diameter, hole-axis height, major-centerline advance per address, advance
per revolution, three-dimensional bead-center travel and thread length are
different quantities. The historical literal `sin(180/turn)` radius convention
does not change the dimensionless0.975 ratio. No thread path exists in this
model, so no string strain follows from an effective advance change.

R302's primary has D=2 radius units, H=1.338764, per-bead advance0.231089 and
per-revolution advance1.502081. Their ratio is**1.1220**. With its height and turn
unchanged, c=.975 would give per-bead advance about0.200815. It is a material
change in packing, not a unit correction. The source audit is saved in
[`source-relationship.json`](r303/evidence/source-relationship.json).

## Experiment and acceptance

Three families use identical S1 evidence: independent pitch, fixed c=.975, and
one free global c in `pitch=c*(2*axial)/turn`. Radius1 fixes the unit gauge.
Each family retains both hands. R302 shapes are the main starts, with historical
alternatives; this is a warm-start local experiment, not a search over every
possible construction. Native predictions and sensitivity-scaled hierarchical
coordinate/coupled moves reuse R302's approach. Complete close-pair certificates
are required over153 addresses at each fitted candidate.

The source substitution makes both R302 starting shapes uncertified. Their
initial two-sided sensitivity matrices have no fully usable rows and therefore
cannot guide the source search; it falls back to declared parameter steps until
feasible alternatives are found. This is an important optimization disadvantage,
not evidence that real crochet cannot have c=.975. All starts, physical rejects,
proposal histories and loss-only alternatives are retained.

S1 selection is sealed before transfer. S2/S3 first share the exact S1 shape,
pitch/coefficient, camera and illumination. Only local offset, centerline angle
and curvature, phase and smooth stitch correction vary. A short final stage
reopens one shared geometry/camera/light vector across all three regions.
The original30 reflections retain21 training/9 retrospective comparison records.
S1 has the uncertain B15 contour; S2/S3 each have two envelope profiles, but no
individual bead-height measurement. Material/paper pixels are correlated cues.
All23 dark-valley profiles remain comparison-only, not verified separators.

Local advance is `pitch*(1+spacing*tanh(k/14))`, explored within±2% as an initial
sensitivity range. This is not a strict mechanical bound, elastic string strain,
or a model of crochet thread paths. Circular centerlines preserve arclength;
the constant-turn construction prior remains the conditional N=2000 scenario.
The15–30-position gate is removed. Denser candidates face the same photographic
and contact checks. No physical count or index identity is inferred.

Selection first minimizes the number of predeclared training contradiction flags,
then the common native objective; it never consults comparison observations.
The flags concern local contact, missing reflections, extent/visible boundary,
envelope, paper and colored omission. They are engineering checks, not calibrated
truth criteria. Component regressions below thresholds remain regressions; a
lower reflection score never establishes a better reconstruction by itself.

## Numerical results

The following tables and audit conclusions are generated from the sealed outputs.

The numerical campaign took **574.99 seconds**, including44.99s of starting
sensitivity and38.61s of final sensitivity. Six S1 fits, twelve fixed-geometry
transfers and six shared refinements stayed within the600s allocation. Each
shared refinement received only13s (20–26 three-region proposals); these are
short transfer/falsification probes, not converged joint optima.

| S1 family / hand | c | Reflection train / comparison RMS px | B15 extent / boundary MAE px | Paper / colored omission train % | Positions | Training flags |
|---|---:|---:|---:|---:|---:|---:|
| independent / -1 | 1.3985 | 2.74 / 4.75 | 1.97 / 1.34 | 7.7 / 10.3 | 28 | 0 |
| source / -1 | 0.9750 | 5.40 / 6.13 | 8.75 / 5.86 | 41.0 / 5.1 | 144 | 3 |
| calibrated / -1 | 1.4178 | 2.65 / 5.19 | 2.22 / 1.41 | 7.7 / 10.3 | 28 | 0 |
| independent / +1 | 1.1068 | 2.01 / 3.16 | 0.21 / 1.30 | 7.7 / 0.0 | 29 | 0 |
| source / +1 | 0.9750 | 6.30 / 5.20 | 5.05 / 2.93 | 35.9 / 2.6 | 54 | 2 |
| calibrated / +1 | 1.1216 | 2.11 / 3.22 | 0.18 / 1.43 | 7.7 / 2.6 | 29 | 0 |

All ten S1 reflections match in each row. The dense source hand− row is
truncation-sensitive and is diagnostic only; its217-position audit is retained
separately. Source hand+ is stable under guard extension but has5.05px B15 extent
error and35.9% training paper occupation. Its lower colored omission cannot
excuse those contradictions.

| Shared final family / hand | c | All three training checks pass? | Reflection train / comparison RMS px | Mean paper train / held % | Mean colored omission train / held % |
|---|---:|---|---:|---:|---:|
| independent / -1 | 1.3985 | No | 6.22 / 7.31 | 5.6 / 8.1 | 15.5 / 22.6 |
| independent / +1 | 1.1068 | Yes | 6.75 / 5.64 | 8.0 / 12.0 | 10.5 / 16.8 |
| source / -1 | 0.9750 | No | 6.32 / 5.14 | 29.0 / 29.7 | 9.2 / 13.9 |
| source / +1 | 0.9750 | No | 6.39 / 7.74 | 18.5 / 27.9 | 8.6 / 9.8 |
| calibrated / -1 | 1.4178 | No | 6.99 / 6.33 | 4.6 / 8.1 | 14.5 / 24.9 |
| calibrated / +1 | 1.1216 | Yes | 7.82 / 7.73 | 8.0 / 12.0 | 12.4 / 16.8 |

These are equally weighted region summaries; all21 training and9 comparison
reflections match. Source hand− numbers above preserve the sealed153-position
outcomes, not validated complete-region predictions. Hand− independent and
calibrated alternatives still fail S3 envelope checks. Hand+ independent and
calibrated pass the training flags, but their comparison paper occupation in
S2/S3 is12.5%/17.6%, above the10% training criterion. They are not adopted.

The best shared candidate by the sealed training rule is **independent hand+**,
with mean objective93.09 versus100.94 for calibrated hand+. Its component results are:

| Region | Reflection train / comparison RMS px | B15 extent / boundary px | Envelope MAE px | Paper train / held % | Colored omission train / held % | Valley MAE px |
|---|---:|---:|---:|---:|---:|---:|
| S1 | 2.01 / 3.16 | 0.21 / 1.30 | not measured | 7.7 / 5.9 | 0.0 / 15.8 | 1.88 |
| S2 | 7.51 / 4.99 | not measured | 2.27 | 7.1 / 12.5 | 16.4 / 24.1 | 3.58 |
| S3 | 8.74 / 7.79 | not measured | 3.07 | 9.1 / 17.6 | 15.2 / 10.3 | 5.53 |

Fixed-geometry hand+ transfer already passes the training checks in all three
regions. Its pooled comparison reflection RMS is6.20px before the short joint
step and5.64px afterward. The calibrated equivalent goes8.05→7.73px. For these two hand+ free-parameter families, the brief
joint steps accepted **no shared geometry/camera/light/coefficient change**;
only local adjustments improved these incumbents. Cross-region data have therefore
not established a newly calibrated global coefficient. There is no per-region c
hidden in the transfer model.

Relative to R301 shared hand+, primary S1 extent error improves5.90→0.21px;
S2/S3 envelope error improves6.32→2.27 and11.34→3.07px. Training colored omission
falls from about32–33% to0/16.4/15.2%; held omission falls31.6/44.8/37.9% to
15.8/24.1/10.3%. However, pooled reflection RMS regresses5.98→6.75px training
and5.20→5.64px comparison. S3 comparison reflection error regresses4.04→7.79px
and its dark-valley error2.85→5.53px. S2 paper occupation regresses0→7.1% training
and0→12.5% held. These remain geometric/photographic contradictions, not successes
hidden by the combined loss.

Against R302 on S1 alone, primary reflections improve2.22→2.01px training and
3.78→3.16px comparison, and training colored omission2.6→0%. But B15 extent
error0.12→0.21px, boundary1.15→1.30px and valley1.72→1.88px worsen slightly.
There is no component-wise no-regression result. The report's interpretation
file retains every component delta against the independent control.

## Coefficient, identifiability and construction interpretation

The best explicitly calibrated hand+ coefficient is**1.12163**,15.0% above0.975.
The best shared independent model implies**1.10680**,13.5% above0.975. These
model differences exceed the±2% local correction scale and are meaningful
packing differences in this conditional family. They do **not** mean13–15%
string stretch. The hand− alternatives imply1.3985–1.4178 and still have a
regional boundary failure. Both hands and their failures remain inspectable.

No statistically justified coefficient interval or requirement for departure
from0.975 follows. The runs were short, source starts were initially uncertified,
and one source branch was truncated. Source hand+ provides a stable negative
result for the sampled geometry, but not a global falsification of the maker's
construction principle. The calibrated coefficient hardly moved from its R302
start, and joint refinement did not move it. Calling1.12163 a fully determined
cross-region mechanical constant would overstate this experiment.

Algebraically, at positive H and turn, `c=pitch*turn/H` is invertible. Free c and
free pitch each have18 parameters and represent the same family under the common
physical bounds. Shared c adds no more identifiability than shared pitch with
shared H and turn. Only fixed c removes a degree of freedom, leaving17. The
native equivalence contract confirms identical predictions for corresponding
independent/calibrated vectors; different local search steps explain different
finite-budget winners.

Starting free-family matrices show four singular directions above the declared
response scale. Final independent hand−/hand+ show five; calibrated hand− shows
four. Final calibrated hand+ sensitivity was not run because of the remaining
budget. These are different conditional poses, not statistical ranks or confidence
intervals. Final calibrated hand− retains axial/c sensitivity cosine0.955;
primary elevation/phase reaches0.954. Height/camera/phase/light ambiguity remains.
The final source matrices have no rows finite across every active derivative:
8/12 individual perturbations are uncertified. Their stored zero direction counts
are **unavailable diagnostics**, not proof of zero photographic information.

Cross-region sharing improves the opportunity to falsify a candidate, but the
same shared parameters are enforced by construction. Passing the training checks
is evidence of limited transfer compatibility, not three independent confirmations
of physical geometry. S2/S3 provide envelope/material constraints rather than
new measured bead heights. No successful identifiability improvement from the
height-to-pitch hypothesis is demonstrated here.

## Density, full local checks and finite-section failure

The removed density cap matters: independent/calibrated hand− S2 transfer retains
33/34 centerline addresses and passes its training checks. Source hand+ uses54
addresses in S1 and is stable with more guards. Neither is rejected for count.
All36 selected153-position models have full close-pair separation certificates,
and all36 extended217-position models also certify separation. Primary minimum
margin across the three selected sections is0.03613 bead radii. These certify
finite geometry only; no complete necklace or inextensible-thread construction
is certified.

Six source hand− exports change native predictions on217-position extension.
They cover roughly144–163 addresses in the photographic windows, so the original
153-address domain was insufficient. Common predicted reflections can move up
to11.67px; dozens of additional predicted lobes appear. **This is a retained
finite-domain failure, not a density veto or proof against c=.975.**

The review contains six additional `guard217-*` evaluation views. They recompute
native reflections, body coverage, dimensions, boundaries and contact at the same
sealed parameters, without optimization. The source hand− geometric failures
remain; in particular, the shared S3 envelope failure returns after extension.
These audit views expose the failure rather than replacing the original histories.
A future source search would need adequate/adaptive guards from the start, but
no such new fitting run is authorized or performed here.

## Delivery and limits

Six scientific contracts pass. Exact selected-vector replay covers36 models,
5,508 positions and19,650 separating-plane witnesses. The additional217-position
checks retain every certificate and finite-domain discrepancy. All16,856 protected
historical files are unchanged. Source/evidence hashes, S1 and transfer seals,
full proposal histories, withheld comparisons and evaluation-only guard audits
are retained. See [verification](r303/results/verification.json).

The reused viewer includes all36 selected models, six guard audits and38 earlier
comparisons. It shows raw photo pixels, actual visible surfaces, uncertain contour/
envelope marks, competing reflection assignments, component metrics and explicit
failure flags. No new synthetic campaign, whole-necklace optimization, production
adoption, pattern inference or Phase3 was performed. The hypothesis remains a
useful construction question, but **this experiment does not support replacing
independent pitch with the fixed0.975 relationship as a better reconstruction**.
Stop for maker review.

Chromium verification passes all80 model views, raw-image invariance, observation
navigation, links, desktop/narrow layouts, offline use and the actual launcher.
Windows browser dispatch is mocked; an actual Windows browser opening is not claimed.
[Browser receipt](r303/results/browser-check.json).

A post-seal CSV line-ending repair changes formatting only; parsed values are
identical and the sealed exporter source is archived. Fitting sources are unchanged.
[Format provenance](r303/results/post-seal-format-repair.json).

Scientific delivery: `91116f19f45415f0ce8cc5fdee06b1e83ecc05b4`, pushed to `origin/photo-2-strategy-v3`
and independently matched by `git ls-remote`. [Delivery receipt](r303/results/delivery.json).
The following metadata commit records the verified delivery. **STOP for review.**
