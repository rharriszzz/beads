"""Produce measured cost, initialization and native-accuracy comparisons."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/r301-mpl')
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .evidence import BASE,ROOT,read,save,utc
from .model import NAMES,BOUNDS

def main():
    runrows=[];histories={};timings={};bounds=[]
    for p in sorted((BASE/'results').glob('*/checkpoint.json.gz')):
        d=read(p);hist=d['history'];histories[p.parent.name]=hist
        if 'config' not in d:
            bucket=timings.setdefault('joint-section-calls',dict(evaluations=0,feasible=0,seconds=0.,geometry=0.,contact=0.,specular=0.,assignment=0.,secondary=0.))
            for row in hist:
                for r in row['sections']:
                    bucket['evaluations']+=1;bucket['feasible']+=int(r['feasible']);bucket['seconds']+=sum(r['timing'].values())
                    for k,v in r['timing'].items():bucket[k]+=v
            continue
        times=np.array([r['seconds'] for r in hist]);runrows.append(dict(name=p.parent.name,**d['config'],evaluations=len(hist),elapsed=d['elapsed'],compute_seconds=float(times.sum()),evaluations_per_wall_second=len(hist)/d['elapsed'],evaluations_per_compute_second=len(hist)/times.sum(),accepted=sum(r['feasible'] for r in hist),reasons=dict(Counter(r.get('reason','certified') for r in hist)),best=min(r['loss'] for r in hist)))
        bounds.extend(r['parameters'] for r in hist)
        group='accurate' if d['config']['resolution'] else 'coarse';bucket=timings.setdefault(group,dict(evaluations=0,feasible=0,seconds=0.,geometry=0.,contact=0.,specular=0.,assignment=0.,secondary=0.));bucket['evaluations']+=len(hist);bucket['feasible']+=sum(r['feasible'] for r in hist);bucket['seconds']+=float(times.sum())
        for r in hist:
            for k,v in r['timing'].items():bucket[k]+=v
    comparisons=[]
    for s in ['S1','S2','S3']:
      for hand in [-1,1]:
        rows=[r for r in runrows if r['section']==s and r['hand']==hand and r['resolution']==0]
        limit=min(r['compute_seconds'] for r in rows)
        for r in rows:
            h=histories[r['name']];cum=np.cumsum([z['seconds'] for z in h]);eligible=[z['loss'] for z,t in zip(h,cum) if t<=limit]
            comparisons.append(dict(name=r['name'],section=s,hand=hand,method=r['method'],equal_evaluations=len(h),best_at_equal_evaluations=r['best'],equal_compute_seconds=limit,best_at_equal_compute_time=min(eligible),initial_loss=h[0]['loss']))
    native=read(BASE/'results/native-manifest.json.gz');selected=[]
    for s in ['S1','S2','S3']:
      for hand in [-1,1]:
        group=[r for r in read(BASE/'results/refined-manifest.json.gz') if r['section']==s and r['hand']==hand];winner=min(group,key=lambda r:r['best']['loss']);selected.append(winner['name'])
    report=dict(utc=utc(),runs=runrows,timings=timings,budget_comparisons=comparisons,bounds_explored={n:dict(allowed=BOUNDS[j].tolist(),minimum=float(np.min(np.array(bounds)[:,j])),maximum=float(np.max(np.array(bounds)[:,j]))) for j,n in enumerate(NAMES)},selected_independent=selected,native=[dict(name=r['name'],section=r['section'],kind=r['kind'],feasible=r['result']['feasible'],parameters=r['result'].get('parameters'),summary=r['result'].get('summary'),secondary=r['result'].get('secondary'),withheld_material=r['result'].get('withheld_material'),guard_extension=r['result'].get('guard_extension')) for r in native])
    save(BASE/'results/analysis.json.gz',report)
    fig,axes=plt.subplots(1,3,figsize=(15,4),layout='constrained')
    for ax,s in zip(axes,['S1','S2','S3']):
        for r in runrows:
            if r['section']!=s or r['resolution']:continue
            h=histories[r['name']];ax.plot(np.cumsum([x['seconds'] for x in h]),np.minimum.accumulate([x['loss'] for x in h]),label=f"h{r['hand']} {r['method']} {r['seed']}")
        ax.set(title=s,xlabel='Measured evaluation time, seconds',ylabel='Best coarse loss');ax.set_ylim(0,180);ax.legend(fontsize=6)
    fig.savefig(BASE/'results/search-progress.png',dpi=140);plt.close(fig)
    make_report(report,native)

def make_report(d,native):
    def f(x):return '—' if x is None else f'{x:.2f}'
    lines=['# R301 — randomized local inverse geometry','',
    'Broad search finds a **shared, locally nonintersecting hand+ candidate** with better reflection predictions: pooled training RMS **8.72→5.98px** and withheld RMS **7.93→5.20px** versus R299, with all 30 observations matched. Against R298, withheld RMS improves **5.86→5.20px**. However, dimensions and material agreement regress, independent solutions disagree and synthetic geometry recovery fails. **Convincing physical reconstruction is not established.** No global count, physical index origin, repeating pattern or production model is adopted.','',
    '[Open the graphical comparison](review/r301/index.html) · [Search progress](r301/results/search-progress.png) · [Reproduce](R301_REPRODUCE.md)','',
    '## Evidence and construction constraints','',
    'The maker clarified that beads per minor turn is nearly 6.5 and essentially constant, with only a small closure twist. The final minimum count preference is **2,000**, superseding interim 6,000 and 2,698 minima. Allowing up to about ten bead positions of twist at 2,000 gives approximately 6.468–6.533; the search uses **6.465–6.535**, constant along each model and shared across sections in the joint fit. Total count is not an optimization parameter. These are construction priors, not a recovered count.','',
    'Three automatically selected, geographically separated 104px reference-arc windows each retain ten original R299 photographic measurements. They have different centerline orientations and include black reflections. Each has 7 training and 3 withheld reflections; all weaker/ambiguous measurements remain with weight 0.2. All 810 earlier records, 52 historical selections, R257 cross-references and rejected/uncertain observations remain preserved. Selection used photographic strength, black evidence and geographic separation, never fitted residuals or bead owners. These withheld observations are excluded from R301 fitting but have historical exposure in earlier studies; this is retrospective within-photo validation, not blind new-image generalization.','',
    'At the minimum/old approximate count the windows nominally span roughly 23–30 physical positions. Each local model has 25 central addresses plus 32 guard positions on each side. Dense hypotheses can put more than 30 axis positions in the frozen photographic window; this is explicitly recorded, not called a verified 25-bead inventory. Native export additionally checks 64 guards per side. No free per-bead displacement, rotation, light or material is allowed.','',
    'The common radius is fixed to one as a unit gauge. The rounded rectangular annulus is revolved about its hole axis and axially stretched; the historical surface is exactly within this family. A planar quadratic centerline, tangent-consistent frames and shared circumferential hole-axis tilt generate all beads. Camera yaw is a planar gauge; elevation and image roll are fitted. The model uses orthographic projection and one shared distant source. Perspective, finite lamps and extra optical degrees of freedom were not added to an already underidentified inversion. Roughness remains 10° in this bounded study.','',
    '## Search and positional objective','',
    'The bounded search uses scrambled Sobol initialization, population differential evolution, periodic global injections and joint mutation of the geometric/light variables. Both hands and two random seeds are retained independently in every section. The coordinate control starts from the same adapted historical dimensions and pose and receives the same 1,536 candidate evaluations. Accurate refinement retains distinct normalized parameter vectors, not only copies of one winner. Two accurate starts per section/hand each receive 384 evaluations. Reflection-only ablations use the identical initial candidate, seed and 384-evaluation budget as their secondary-constrained controls. The joint fit gives each hand 768 accurate evaluations with common physical/camera/light variables and six local variables per section.','',
    'Primary loss uses native-pixel squared distances passed through 576 d²/(576+d²). Hungarian assignment includes 400-weighted-squared-pixel unmatched-observation costs, a 4-squared-pixel unused-prediction cost and a bounded second-component slot costing 64. A bead can own at most two nearby components, separated by at most 12px; no unlimited dropping or duplicate ownership is possible. This sharing heuristic is not an exhaustive enumeration of every merged-lobe hypothesis. Competing assignments and their costs are exported. Withheld assignment cannot reuse owners already consumed by training.','',
    'Secondary terms are small penalties for paper occupation, missing colored material, approximate measured bead dimensions and envelope edges. They do not dominate via positive-region containment. Sixteen-pixel material bands are withheld. Existing R298 separator selections do not intersect these small windows; 23 additional image-only dark-valley profiles were frozen separately and used solely for withheld diagnostics, never training. A dark valley is not automatically a physical bead separator.','',
    '## Native reflection results','',
    'The following rows are chosen by the accurate training score before native withheld evaluation. Baselines use the unchanged historical geometry/light, evaluated anew against the identical local observations and assignment rules; these numbers are not the old fixed-owner R299 table. RMS is for finite matches. Unmatched counts remain explicit and count as infinite for median/p90; a dash therefore need not mean a small error.','',
    '| Section/model | Train matched | Train median / RMS px | Withheld matched | Withheld median / RMS px | All p90 px |','|---|---:|---:|---:|---:|---:|']
    for r in native:
        if r['name'] not in d['selected_independent'] and r['kind'] not in ['joint','baseline']:continue
        z=r['result'];
        if not z['feasible']:lines.append(f"| {r['name']} | rejected | — | — | — | — |");continue
        a=z['summary']['train'];b=z['summary']['withheld'];c=z['summary']['all'];flag=' †' if z.get('physical_accepted') is False else '';lines.append(f"| {r['name']}{flag} | {a['matched']}/{a['n']} | {f(a['finite_median'])} / {f(a['finite_rms'])} | {b['matched']}/{b['n']} | {f(b['median_including_unmatched'])} / {f(b['finite_rms'])} | {f(c['p90_including_unmatched'])} |")
    lines+=['','† These three candidates are **not physically accepted** after extending from 32 to 64 guards per side. S1 hand− independent and S3 hand+ independent each have 15 demonstrated sampled penetrating pairs in the extended section; joint hand− S1 has one unresolved pair. Joint hand+ certifies all three 153-position extended sections. Eighteen of the 21 new local exports certify with extended guards. These are finite-section certificates only, never a necklace certificate. Guard extension changes the joint hand− S1 highlight set, with a maximum common-prediction movement of 6.35px; that alternative is rejected. Every failure remains available.','',
    'The shared hand+ solution has axial/face ratio 0.593, minor-radius/bead-radius 3.061, pitch/bead-radius 0.276, 6.50374 beads/turn, hole-radius/outer-radius 0.112, rounding fraction 0.948, shared hole-axis tilt −13.64°, camera elevation 62.50°, roll −0.68°, face diameter 23.80px and light azimuth/elevation 49.52°/54.53°. These values are one compatible family, not recovered measurements. It places 32/36/32 model axis positions in the photographic windows, slightly exceeding the original 15–30 target; guard context is therefore essential.','',
    'For this shared candidate the full-observation RMS is 3.89/7.10/5.82px across S1/S2/S3 (0.164/0.298/0.245 face diameters). Mean signed tangent errors are +1.88/+2.17/+1.27px, and normal errors −0.55/+0.86/+0.85px. Tangent slopes are −7.11/−8.15/−1.74px per 100px of photographic reference, so a claim of no systematic local drift is unwarranted. Red, yellow and black evidence all has matched predictions, but yellow RMS is still 9.16px in S2.','',
    'All color-specific, signed tangent/normal, local-diameter-normalized and unmatched-inclusive summaries are in `results/analysis.json.gz` and the debugger. Signed slopes over these short, sparsely observed spans are descriptive; local reassignment can hide phase slips, so bounded local errors cannot certify full-loop indexing or closure.','',
    '## Does the inversion recover known geometry?','',
    '[Synthetic geometry comparison](r301/results/synthetic-recovery.png). Native implicit-surface tracing generated known targets; the coarse predictor uses a separate surface quadrature. Four compact runs used 2,048 broad evaluations plus 256 accurate refinements each, with known correspondence and with 1.5px feature noise, a false feature and uncertain correspondence. They ran before the real-photo experiment, during the count clarifications; both regimes and all failed hypotheses are preserved.','',
    '| Synthetic regime | Owners | True → recovered axial/face | Training matched | Finite training RMS px |','|---|---|---:|---:|---:|']
    for r in read(BASE/'results/synthetic-analysis.json'):
        lines.append(f"| {r['regime']} | {'known' if r['known_correspondence'] else 'uncertain'} | {f(r['truth']['axial'])} → {f(r['recovered']['axial'])} | {r['training_matched']}/{r['training']} | {f(r['training_finite_rms'])} |")
    lines+=['','At the exact generating parameters, native predicted coordinates replay with zero positional error. The two-pixel predictor has approximately 0.53/0.73px finite RMS in the two regimes, with one missing thin-case lobe; the coarse predictor has approximately 5.94/1.98px finite RMS, with one/three missing lobes. Thus the cheap forward approximation can reorder hypotheses, and the search itself does not reliably reach a known solution. Allowing unknown ownership can improve the score while concealing wrong physical geometry. This is a failed recovery validation, not evidence that the real photograph is insufficient or that the surface model is universally wrong. It limits every real-photo inference in this report.','',
    '## Equal-budget method comparison','',
    '| Region / hand | DE seed 3011 | DE seed 3012 | Coordinate control | Best DE beats coordinate? |','|---|---:|---:|---:|---|']
    for s in ['S1','S2','S3']:
      for hand in [-1,1]:
        rr=[r for r in d['runs'] if r['section']==s and r['hand']==hand and r['resolution']==0];de=sorted([r for r in rr if r['method']=='de'],key=lambda r:r['seed']);co=next(r for r in rr if r['method']=='coordinate');lines.append(f"| {s} / {hand:+} | {f(de[0]['best'])} | {f(de[1]['best'])} | {f(co['best'])} | {'yes' if min(r['best'] for r in de)<co['best'] else 'no'} |")
    lines+=['','Each column has 1,536 evaluations; the two DE seeds are separate experiments, not a 3,072-versus-1,536 budget claim. Broad search beats the coordinate strategy in three of six section/hand comparisons and loses in three. This does not establish a uniformly better search strategy. Exact fixed-compute-time comparisons, including initialization sensitivity, are in `results/analysis.json.gz`; compute-time excludes checkpoint overhead, which is separately recorded.','',
    '## Independent geometry and initialization','',
    '| Selected family | Axial/face | Minor radius / bead radius | Pitch / bead radius | Beads/turn | Tilt° | Elevation° | Roll° | Face diameter px |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in native:
        if r['name'] not in d['selected_independent']:continue
        p=r['result']['parameters'];lines.append('| '+r['name']+' | '+' | '.join(f(p[n]) for n in ['axial','minor','pitch','turn','tilt','elevation','roll'])+' | '+f(2*p['scale'])+' |')
    lines+=['','Physical/camera/light parameters are compared explicitly rather than averaged into a supposedly common geometry. The joint fits initialize common parameters from each independent section in turn; each local centerline/phase remains separate. Agreement within the narrowly prescribed turn range is primarily imposed by maker knowledge, not evidence that the photograph recovered that value. Radius and absolute units cannot be identified independently of camera scale. Hole size, roundedness, light direction and axial tilt remain coupled.','',
    '## Which photographic constraints help, and why stop?','',
    'Reflection agreement improves at the expense of other measured evidence. Relative to R299, shared hand+ S1 bead-extent MAE rises **1.20→5.90px**; S2 envelope-edge MAE **1.80→6.32px**; S3 edge MAE **5.62→11.34px**. Training colored-material omission rises from about **20–21% to 32–33%**. Withheld colored-material omission is **32/45/38%** in S1/S2/S3. The smaller 23.8px face diameter and altered packing can place highlights well while failing to cover visible material. This is a geometric contradiction, not an acceptable trade for a lower reflection loss.','',
    'Matched reflection-only ablations leave S1 and S2 unchanged. In S3, dropping secondary constraints worsens native training RMS **4.52→5.17px**, withheld RMS **8.47→9.85px**, and the secondary penalty **9.88→29.12**. The constrained fit therefore helps in that case, but these three controls do not identify a universally sufficient objective. Native dimensions/material boundaries are useful veto evidence; positive containment still must not substitute for reflection geometry.','',
    'This step stops because the maker has a new plan and explicitly requested complete closure of R301 with the reasons recorded. The scientific reason not to adopt or expand this reconstruction is that reflection improvements coexist with dimensional/material regressions, initialization/section disagreement, guard failures in several alternatives and unsuccessful known-geometry recovery. A successful synthetic fit at the true parameters shows the optimizer/approximation can fail even when a solution exists. None of this proves the photograph intrinsically lacks enough information. The new plan is not implemented here.','',
    '## Measured computational cost','',
    '| Resolution | Evaluations | Feasible | Evaluation seconds | Geometry | Contact | Reflections | Assignment | Secondary |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for key,r in d['timings'].items():lines.append('| '+key+' | '+str(r['evaluations'])+' | '+str(r['feasible'])+' | '+' | '.join(f(r[k]) for k in ['seconds','geometry','contact','specular','assignment','secondary'])+' |')
    lines+=['','The coarse surface quadrature is only a screening approximation. Final evidence uses native first-hit rays, surface normals and shadow rays against the actual implicit annuli. Contact screening checks every spatially close pair, including nonadjacent and guard positions, using analytic separating planes for a filled outer envelope. Failure of this sufficient certificate means unresolved/rejected, not automatically demonstrated penetration. The certificate covers only the exported finite section.','',
    'The saved timing tables separate evaluation work from checkpoint/driver overhead. Equal-time comparisons use measured candidate-computation seconds, not estimated wall-clock allocation; both equal-evaluation and equal-compute-time outcomes are retained. Checkpoints are atomic every 16 proposals and at graceful termination; uncommitted work after a hard kill is deterministically replayed. Source/evidence fingerprints and a writer lock protect resume. A complete-necklace extension would multiply visibility/contact work and introduce global phase/closure constraints that these local fits do not solve. No scaling benefit or complete-chain feasibility is claimed from simply multiplying bead counts.','',
    '## Bounds and limitations','',
    '| Parameter | Allowed interval | Actually sampled interval |','|---|---|---|']
    for n,r in d['bounds_explored'].items():lines.append(f"| {n} | {r['allowed'][0]:.5g} … {r['allowed'][1]:.5g} | {r['minimum']:.5g} … {r['maximum']:.5g} |")
    lines+=['','The broader search can produce alternative local geometries, but a score reduction is not geometric discovery. Only a handful of independently localized reflections occur per window, while dimensions, camera, illumination and unknown correspondence are coupled. Sparse black highlights are useful surface evidence but supply no complete black-body outline. Training failures cannot alone decide between geometry error, optical displacement, wrong ownership and non-specular contamination. The debugger reports physical-center and predicted-highlight errors for the same owner plus alternative-owner costs, without turning those diagnostics into ground-truth causal labels.','',
    'All original R297–R300 scientific files, live feedback and `beads.pov` are protected by a before/after hash manifest. Prior selections and synthetic diagnostics during the maker’s count clarifications remain in `checkpoints`; no real-photo fitting occurred under those interim minimum-count assumptions. The final fit seal precedes native evaluation. No Phase 3, color-pattern inference, adopted reconstruction, automatic R302 or full-necklace optimization follows. **Stop for review.**','']
    (ROOT/'photo2/R301_REPORT.md').write_text('\n'.join(lines))

if __name__=='__main__':main()
