"""Generate compact report and offline review from sealed evidence."""
from collections import Counter
from pathlib import Path
import numpy as np
from photo2.r297.common import ROOT,read,save,utc
OUT=ROOT/'photo2/r321/results'

def main():
 rows=[read(f) for f in sorted((OUT/'trials').glob('*.gz'))];sel=read(OUT/'selection.json')['models'];primary,rescue,trade=sel;perf=read(OUT/'performance.json');plan=read(OUT/'optimization-plan.json');ver=read(OUT/'verification.json');straight=read(OUT/'straight-audit.json')
 ranges={k:[min(r['parameters'][k] for r in rows),max(r['parameters'][k] for r in rows)] for k in ['count','radius','axial','phase','s0']};save(OUT/'actual-search-ranges.json',dict(ranges=ranges,counts=sorted({r['parameters']['count'] for r in rows}),hands=[-1,1],trials=len(rows),classifications=dict(Counter(r['contact']['classification'] for r in rows)),kinds=dict(Counter(r['kind'] for r in rows)),optical_evaluations=sum('optical' in r for r in rows),pre_camera_rejections=sum(not r['contact']['certified'] for r in rows)))
 table='| Model | Count | Diameter px | Emax px | Pigment omitted | Separator conflicts | Bracket p95 px |\n|---|---:|---:|---:|---:|---:|---:|\n| R319 (different map, open) | 2405 | 30.91 | 11.824 | 9.4% | 25.0% | 7.2 |\n| R320 derived-best | 2800 | 22.68 | 13.156 | 31.1% | 22.4% | 19.0 |\n'
 for m in sel:
  g=m['optical']['geometry'];table+=f"| R321 {m['label']} | {m['parameters']['count']} | {m['summary']['diameter_photo_px']:.2f} | {m['optical']['emax_px']:.3f} | {100*g['material_omission']:.1f}% | {100*g['seam_conflict_fraction']:.1f}% | {g['bracket_p95']:.1f} |\n"
 timing='| Scope | R320 historical geometry-changing median | R321 measured native median | R321 measured rays range |\n|---|---:|---:|---:|\n'
 for scope,old in [(100,.397),(200,.600),('all',7.021)]:
  rr=[r['optical'] for r in perf['native'] if r['scope']==scope and not r.get('skipped')];timing+=f"| {scope} | {old:.3f}s | {np.median([r['total_seconds'] for r in rr]):.3f}s | {min(r['camera_rays'] for r in rr)}–{max(r['camera_rays'] for r in rr)} |\n"
 paired='| Method | Construction median | Actual-solid check median | Total before-camera mean | Certified / 24 matched inputs |\n|---|---:|---:|---:|---:|\n'
 for method in ['R320','R321']:
  rr=[r[method] for r in perf['comparison']];paired+=f"| {method} | {np.median([r['construction_seconds'] for r in rr]):.4f}s | {np.median([r['contact_seconds'] for r in rr]):.4f}s | {np.mean([r['total_before_camera'] for r in rr]):.4f}s | {sum(r['classification']=='certified-separation' for r in rr)} |\n"
 sm=primary['summary'];base_length=1141.8848928422274;actual=rows[primary['trial']];counts=Counter(r['contact']['classification'] for r in rows)
 contact='| Model | Offset | Median lower / upper clearance, units | Upper ≤ .02r |\n|---|---:|---:|---:|\n'
 for v in ver['models']:
  for g in v['neighbors']:contact+=f"| {v['label']} | +{g['offset']} | {g['lower_median']:.5f} / {g['upper_median']:.5f} | {g['near_contacts_upper_le_002r']} |\n"
 text=f'''# R321 — contact-derived packing repairs the photo-sized collision

**No reconstruction is adopted. Stop for scientific review; no automatic R322.**

The full closed **N2800, radius1.95, axial0.85** chain now certifies nonintersection
with its original **33.767px** nominal diameter, both hands, and **zero centerline
movement**. R320's same physical inputs intersected. The repair is a deterministic
curvature-dependent distribution of major advance, together with contact-derived
minor radius and staircase orientation. It is not a mechanical equilibrium model.
The minor radius is not an independent photometric fitting coordinate.

This is a reusable partial construction, not a complete algebraic nonintersection
theorem. Finite-pair support/actual-glass verification remains mandatory. The
spacing law creates up to **10.565%** local rate departure and **72.785px** accumulated
station departure from uniform placement in the repaired N2800 model. Those are
reported derived geometric changes, **not measured crochet strain**. No large
centerline distortion is used to repair this candidate.

[Compact review](r321/results/index.html) · [Delivery receipt](r321/results/delivery.json) · [Specification](R321_SPECIFICATION.md) ·
[Reproduction](R321_REPRODUCE.md) · [All trial ranges](r321/results/actual-search-ranges.json)

## 1–3. Algebra, derived radius/pitch, and six-neighbor contact

For unit plane normal n, bead hole axis t, d=n·t, q=sqrt(1-d²), and
f=(.7/.43)a, the exact support of the shared legacy glass is

`h(n,t)=r[.656 q + .086 f |d| + .344 sqrt(q²+f²d²)]`.

This follows from the literal rounded rectangle revolved about the hole axis:
radial cross-section center .57r, half-flat .086r, rounding .344r. The exact full
axial thickness remains **H=1.4ra**, outer radius r, hole radius .14r. It is the
same support as the filled convex hull; its validity does not fill the actual bore
in ray tracing or actual-solid tests.

For offset d∈{{1,6,7}}, theta=pi*d/T, put the two centers at
`(+/-dP/(2T), +/-R sin(theta), R cos(theta))`. Their derived axes are
`(cos(alpha), sin(alpha)cos(theta), +/-sin(alpha)sin(theta))`,
with alpha=-atan(P/(2piR)) in the canonical hand. Reflection symmetry lets a
separating plane normal be chosen as n=(cos(beta),sin(beta),0). Hence

`g_d=max_beta [(dP/T)cos(beta)+2R sin(theta)sin(beta)-2h(n,t)]`.

This one-dimensional support calculation is independently checked against full
3D normal optimization. Positive g certifies separation. A negative value only
means that these convex envelopes cannot separate. It does not by itself prove
glass interpenetration. Numerical maximization is not exact symbolic arithmetic.

There is also an explicit radial-support constraint for +1. Set theta=pi/T,
A=P²cos(theta)/(2piT), B=(P cos(theta)/(2pi))², D=2r+epsilon. A plane perpendicular
to both hole axes has support r on each bead. X=R² satisfies

`4 sin²(theta) X² + (4 sin(theta) A-D²)X + A²-D²B = 0`.

The larger positive local-branch root derives R from P,r,T. The declared branch
is .85–1.15R0, with R0=r/sin(pi/T); it is a construction branch, not a physical
impossibility bound. Thickness enters the other support inequalities. On the
closed curve **P=L/W**, W=floor(N/6.5+.5), T=N/W, so P is not independently fitted.

Straight contact references solve g1=g6=0 and g1=g7=0 and then check the remaining
inequality. At T=2800/431 and a=.85, the feasible local branch gives
**R/r=2.14149098, P/r=1.21829737, P/H=1.0237793**. Its +7 clearance is
**.0131166r**. The alternative g1=g7 branch has g6=-.0128519r at the hull level.
Actual-glass support-face endpoints verify the +1 and +6 contacts within1e-6 units
for all30 references (six counts and five thicknesses). Small outward perturbed
41-bead scenes are independently checked. Endpoints lie on actual outer-side or
rounded-face glass, not in the bore.

Thus the tested dense reference has **four exact-within-numerical-tolerance
neighbors and two small positive gaps**, not six exact contacts. All six equations
are not simultaneously met in these local branches. This does not establish a
global impossibility theorem or a globally densest packing. The radius and pitch
are locally coupled by contact equations; the closed-chain pitch must additionally
satisfy its length/winding constraint. [Straight evidence](r321/results/straight-audit.json).

## 4–5. Curvature, changing contacts and guarantees

For the planar centerline's directed tangent t, normal m, curvature kappa and
minor phase phi, radial e=sin(phi)m+cos(phi)z. The exact differential trajectory is

`dc/ds=(1-R*kappa*sin(phi))*t + R*(dphi/ds)*circumferential`.

The inner side crowds while the outer side opens. The construction uses the
worst-side factor **rho(s)=1-R|kappa(s)|** and M=integral rho ds. Uniform bead index
in this integrated density gives **local P(s)=M/[W rho(s)]**. It allocates more
advance where the major curve bends tightly while keeping N,W, bead0 station and
the seam fixed. The normal is derived from radial × actual trajectory tangent,
including both curvature and variable advance. No tilt, radial cant, seam, local
phase or independent spacing field is fitted. The regular branch requires rho>.1.

The density formula is a first-order geometric hypothesis. It is **not** a theorem
about finite rounded beads, and the absolute-curvature envelope can leave more
gaps than necessary. The local contact set is allowed to change. No equal penalty
is applied to all missing contacts. Saved gap-versus-curvature/phase plots compare
nearly straight regions with inner and outer strongly curved regions. Near-contact
counts use explicit glass endpoint upper bounds; a broad bound is not evidence of
a large actual gap.

After the straight root, R receives a deterministic correction from all closed
+1 inequalities. Five explicit plane directions (center displacement, its
projections perpendicular to either/mean axis, and the cross-axis direction) give
exact support values. Any positive one proves that pair disjoint. Secant updates
of R are followed by fresh nonlinear checks; no monotonic/global-minimum claim is
made. Every spatial pair within conservative bounding spheres, including all seam
+1/+6/+7 pairs, then gets the inherited support certificate. Pairs farther apart
are excluded by containing spheres. Failed envelopes get actual annular-volume
subdivision. Shared points strictly inside both implicit solids prove penetration;
exhausted subdivision remains unresolved. There is no necessary-and-sufficient
cheap global test here, and no optimizer is allowed to render/adopt uncertified
geometry.

{contact}

The +6/+7 positive lower bounds in the selected chains show real residual gaps;
the construction repairs collisions but does not establish dense six-neighbor
contact throughout the necklace. Some upper bounds remain loose on flat faces.
[All selected pairs and normals](r321/results/photo-sized-rescue-neighbor-gaps.json.gz).

## 6–8. Why R320 intersected, and the photo-sized repair

At R0, hand−1 pair **−1077/−1070 (+7)** has an independently retained shared
interior point. Neighbor +6 also has failed hull inequalities. The local directed
curvatures are −.031343/−.032800 inverse units; the inner metric factors are
.8830/.8625. The overlap lies near axial shoulders/flat faces: axial coordinates
.981/−.913 of half-thickness and radial coordinates .729/.730 of r. It is not a
bore artifact. Hand+1's witness is pair **−1074/−1067**. Normal vectors, local
coordinates and original witnesses are serialized in the
[failure diagnosis](r321/results/failure-diagnosis.json).

Holding P,R,r,a fixed but removing the major bend certifies separation. Increasing
R from R0 to1.16R0 worsens the +7 support deficit from −.09703 to−.10938 units
for hand−1; it increases inner crowding. The improved radius relationship alone
changes the deficit only to about−.09663. Thus an inaccurate minor-radius formula
is not the main cause. Uniform major spacing and curvature together cause this
particular failure. These are unavoidable collisions **for the specified saved
placements**, not an impossibility for all legitimate constructions of N,r,a.
Derived spacing supplies an explicit counterexample to that broader claim.

The repaired N2800 model uses **R=4.17520646**, versus R0=4.19397752; global P is
unchanged2.64938490, P/H=1.14173019, but local P varies2.52821–2.92930. Its shape,
count, radius, thickness, global phase, station, centerline and shared camera/light
remain as specified; only contact-derived R and curvature spacing/orientation
change. It certifies all8400 relevant spatial pairs. This answers the central
question affirmatively: **33.77px beads are possible without shrinking them**.
It does not establish that the new station distribution matches real crochet.

## 9–10. Actual search and centerline changes

The saved campaign contains **{len(rows)} trials: {counts['certified-separation']} certified,
{counts['demonstrated-interpenetration']} demonstrated penetrations, zero unresolved** at its
selected final fallback budgets. Unresolved is still a distinct API outcome; the
absence here is not a guarantee for future inputs. There are **166 optical trials**;
54 rejected geometries never reach camera rays. The initial84-trial numerical
uniform-spacing epoch, later density controls and all failures are retained.
Distinct counts are2200,2400,2600,2800,2801,3000,3200; both hands; radius
**{ranges['radius'][0]:.3f}–{ranges['radius'][1]:.3f}**, axial **{ranges['axial'][0]:.3f}–{ranges['axial'][1]:.3f}**.
The 30 straight controls additionally explore axial.55–1.25 and winding-transition
counts2401/2402. Centerline optimizers retain439 intermediate fixed-plane support calculations
separately. These are unresolved until full-chain audit, have no photo evaluation,
and have no retained per-probe timer; total solver times are saved. They are not
presented as additional independently certified chains or camera trials.

The new centerline basis is periodic cubic B-splines at32 fixed knots, each
supported on4/32 of the circuit. Only knots0/14 and a five-knot neighborhood of
the diagnosed bend are actively tested. Total displacement stays≤3.3468px.
Eight literal two-harmonic ±3px controls all fail to repair the uniform-spacing
photo-sized case. Five local basis coefficients alone also leave demonstrated
penetration, despite about3.21px correction. Joint centerline/thickness solves
certify at axial.81667/.81215 for the two hands, keeping radius1.95, with
2.738/2.616px displacement. These controls show a modest local benefit; they do
not prove the harmonic family globally inadequate or identify physical strain.

The selected geometry diagnostic requires **{sm['axis_correction_px']:.6f}px =
{sm['axis_correction_px']/33.468:.5f} fixed photo diameters** of centerline displacement.
Its L changes1141.884893→{sm['length']:.6f} (**{sm['length']-base_length:+.6f} units,
{100*(sm['length']/base_length-1):+.5f}%**); global P changes2.47161232→{sm['rise']:.8f}.
Its absolute maximum curvature is **{actual['curvature']['absolute_max']:.8f}**, versus
.03279968 before correction. This selected joint intervention changes radius,
thickness, phase, station and centerline; its photo gain is not attributed to
centerline alone. Every isolated intervention's pitch, curvature and gap response
is retained. The repaired N2800 candidate needs **zero** centerline correction.

## 11. Photographic comparison and correspondence limits

{table}

All22 original photo-only half-maximum centroids remain, including seven black
reflections. Per-family maps are initialized from visible support overlap and
then frozen. The density continuation keeps the earlier uniform family's map;
several hand+ families lose a prediction and remain physically promising controls
with infinite maximum, rather than being discarded from the physical study.
No observation is dropped to improve Emax. Same-geometry support-rematching
controls are saved separately and never credited as geometry improvements.
Different-count and R319/R320 map comparisons are explicitly conditional.

The primary R321 diagnostic is trial{primary['trial']}: after requiring photo-sized
certified geometry, no dual-color claims and omission<15%, it minimizes confident
separator conflicts, then Emax. It still has **{100*primary['optical']['geometry']['seam_conflict_fraction']:.1f}%**
separator conflicts and does not pass a reconstruction acceptance gate. Trial
{trade['trial']} has lower reflection error but worse separators; both are retained.
The N2800 physical rescue improves pigment omission to4.93% but has50% separator
conflicts and Emax20.613px. This is a physical construction success, not superior
photographic ownership. Boundary and reflection vectors are native visible-surface
results with all necklace bodies present in camera rays and shadows. No black
silhouettes or complete hidden photo contours have been invented.

## 12. Measured computational cost

{paired}

{timing}

The matched comparison is eight physical input triples, three serial repetitions,
fixed hand−1. R320 and R321 use their respective placement constructions; matched
inputs do not imply identical output geometry. Timings include all physical bodies.
Construction splits algebraic root/support, geometry and curvature correction;
actual-solid certification is separate. Native scope tests retain every body for
visibility/shadows, use100/200/all target bodies and six measurements per scope.
The22-observation timing cohort differs from R320's broader benchmark cohorts;
ray counts and unknowns are explicit. A finite maximum is not required for a timing.
Larger beads change the ray workload. These figures do not establish a camera-kernel
speedup. Pilot/search timings overlapped other work and are excluded from this
sequential benchmark.

Both R320 and R321 already reject failed physical proposals before rendering.
Thus 54 camera evaluations avoided in this pilot are **not claimed as an incremental
speedup over R320**. The new construction makes some previously impossible saved
placements feasible rather than merely rejecting them. The plan retains R320's
phase counts, uses measured new costs, and shows **{plan['all_render_total_hours']:.2f}h** if every proposal
renders, or **{plan['pilot_yield_scenario_hours']:.2f}h** using the purposive matched-pilot feasibility
fraction as a scenario. That fraction is not a population estimate. Setup overhead
is not newly measured and the10× verification allowance remains unmeasured. No
multi-hour search is authorized or launched. [Cost data](r321/results/performance.json)
· [Updated scenario plan](r321/results/optimization-plan.json).

## 13. Verification and what must precede a larger run

Six contracts cover3D-versus-reduced support, closure across winding changes,
photo-sized collision/repair, local basis support/budget, competing contact branches, and actual side-segment upper bounds. Independent literal support recomputation verifies **{sum(v['witnesses'] for v in ver['models'])}**
selected full-chain witnesses. A doubled-resolution independent density integral
agrees in station to **{max(v['doubled_density_station_difference_units'] for v in ver['models']):.2g} source units**;
analytic staircase normals agree within **{max(v['analytic_orientation_max_difference'] for v in ver['models']):.2g}**.
Original Python camera and shadow implementations check540 camera samples plus
corresponding shadow queries. Actual-glass gap endpoints and every selected
+1/+6/+7 pair, including seams, are checked independently. Thirty straight
references have explicit glass contact endpoints; no sphere-distance substitute
is used. Raw RGB centroid reconstruction, all trial maxima/cohorts, browser
checks and preservation hashes accompany delivery.

Initial failures are retained: the uniform straight-only construction collided
at+1; a conservative cross-axis-only correction opened excessive radial gaps;
the first endpoint audit needed exposed-face subgradients; a basis-support test
used the historical field's shifted coordinate origin; refinement initially
assumed a finite reflection score in a physically valid missing-lobe family.
A first side-segment tightening encountered a nearly axial normal; explicit local-frame radial directions repaired the degenerate endpoint. The repaired paths preserve failed records and keep missing Emax infinite.

Before a larger run: validate the density/strain hypothesis against photographic
neighbor order; reduce the large accumulated station redistribution if evidence
rejects it; seek denser +6/+7 contact without forcing curvature-opened gaps shut;
resolve separator ownership and missing-lobe identities; test more local curvature
support and broader actual-solid branches; and benchmark broader workloads plus
full original-kernel verification. Neither a recovered count nor a color pattern
nor mechanical equilibrium is established. The fixed light/camera and rounded
shape remain hypotheses. **Stop for scientific review.**
'''
 (ROOT/'photo2/R321_REPORT.md').write_text(text)
 figures=[('Original photograph (same crop)','original-crop.png'),('R320 derived-best','../../r320/results/derived-best-overlay.png'),('R321 geometry diagnostic','geometry-best-overlay.png'),('R321 photo-sized collision repair','photo-sized-rescue-overlay.png'),('Actual 3D contact geometry','contact-geometry.png'),('Measured curvature-dependent gaps','curvature-gaps.png')]
 cards=''.join(f'<figure><figcaption>{title}</figcaption><a href="{src}"><img src="{src}" alt="{title}"></a></figure>' for title,src in figures)
 (OUT/'index.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R321 contact-constrained packing</title><style>body{{font:16px system-ui;margin:24px auto;max-width:1150px;padding:0 14px;color:#17232e;background:#f7f6f1}}h1{{font-size:27px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}}figure{{margin:0;padding:12px;background:white;border:1px solid #ccd3d8}}img{{width:100%;height:auto}}figcaption{{font-weight:650;margin-bottom:8px}}a{{color:#19537b}}@media(max-width:650px){{.grid{{grid-template-columns:1fr}}body{{margin:14px auto}}}}</style><h1>R321 — photo-sized beads can separate</h1><p>N2800, radius1.95, axial.85: full-chain certificate at33.77px diameter, no centerline change. Curvature-derived spacing changes local advance by10.6% and accumulated station by72.8px. No reconstruction adoption.</p><p>Selected geometry: N{primary['parameters']['count']}, D{sm['diameter_photo_px']:.2f}px, Emax{primary['optical']['emax_px']:.3f}px, pigment omission{100*primary['optical']['geometry']['material_omission']:.1f}%, separator conflicts{100*primary['optical']['geometry']['seam_conflict_fraction']:.1f}%. Cyan: predicted visible boundaries; yellow: observed reflection; magenta: predicted reflection; white: displacement. Correspondences remain provisional.</p><p><a href="../../R321_REPORT.md">Report / all13 questions</a> · <a href="../../R321_REPRODUCE.md">Reproduce</a> · <a href="../../../beads-photo-2.jpg">Full original photograph</a> · <a href="performance.json">Measured costs</a> · <a href="optimization-plan.json">Future plan</a> · <a href="contact-geometry.json">Six-neighbor gap ledger</a> · <a href="actual-search-ranges.json">Actual coverage</a></p><div class="grid">{cards}</div><p>Contact surfaces are actual rounded annuli. Positive clearance bounds allow curvature-opened gaps. Green means upper gap≤.02r, amber means a positive gap; no force or equilibrium model. Full records preserve conservative bound widths.</p></html>''')
 print('REPORT',len(text),flush=True)
if __name__=='__main__':main()
