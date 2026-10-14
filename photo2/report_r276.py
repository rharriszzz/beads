"""Generate R276 comparison tables, native photo evidence and reproducibility report."""
from __future__ import annotations
import csv,gzip,json,platform,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from .reconstruct_r276 import OUT,ROOT,sha,save,observation_data,stats,NAMES


def ledger():
    summaries=[];individual=[]
    for p in sorted(OUT.glob('*-summary.json')):
        d=json.loads(p.read_text())
        if not isinstance(d,dict) or 'metrics' not in d:continue
        name=p.name.removesuffix('-summary.json');model=json.loads((OUT/(name+'.json')).read_text())
        summaries.append(dict(id=name,n=model['base']['n'],h=model['base']['h'],focal=model['base'].get('focal',0),light=model['light'],metrics=d['metrics'],physical=d['physical'],
            camera_unfinished=d['camera_unfinished'],shadow_unfinished=d['shadow_unfinished'],native_camera_unfinished=d['native_camera_unfinished'],color_conflicts=len(d['cross_split_color_conflicts'])))
        with gzip.open(OUT/(name+'-audit.json.gz'),'rt') as f:a=json.load(f)
        for r in a['records']:
            individual.append(dict(model=name,id=r['id'],color=r['color'],split=r['split'],strong=r['strong'],specular_candidate=r['specular_candidate'],conditional_owner=r['owner'],
                observed_peak_x=r['observed_peak'][0],observed_peak_y=r['observed_peak'][1],observed_bright_x=r['observed_bright_centroid'][0] if r['observed_bright_centroid'] else None,observed_bright_y=r['observed_bright_centroid'][1] if r['observed_bright_centroid'] else None,
                predicted_x=r['predicted']['centroid'][0] if r['predicted'] else None,predicted_y=r['predicted']['centroid'][1] if r['predicted'] else None,
                brightness_centroid_displacement_px=r['highlight_error'],native_peak_displacement_px=r['peak_error'],missing_prediction=r['missing_highlight'],uncertainty_px=r['uncertainty_px'],
                support_rms_px=r['support']['rms'],support_max_px=r['support']['maximum'],positive_pixels=r['positive_pixels'],native_owned_fraction=r['native_owned_fraction'],
                shape_sigma_error_px=r.get('shape_sigma_error'),shape_orientation_error_deg=r.get('shape_orientation_error_deg'),relative_brightness_error=r.get('relative_brightness_error')))
    save(OUT/'comparison.json',summaries)
    with (OUT/'individual-residuals.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(individual[0]),lineterminator='\n');w.writeheader();w.writerows(individual)
    return {r['id']:r for r in summaries}


def photographic_calibration():
    rows,rgb=observation_data(False);selected=[];measure=[]
    for sector in range(0,16,2):
        rr=sorted([r for r in rows if r['sector'] in (sector,sector+1) and r['color']=='yellow' and r['specular_candidate']],key=lambda r:r['id'])
        if rr:selected.append(rr[len(rr)//2])
    for j,r in enumerate(selected):
        x,y=r['xy'];box=[max(0,x-32),max(0,y-32),min(2540,x+33),min(3182,y+33)]
        raw=Image.fromarray(rgb).crop(box).resize((260,260),Image.Resampling.NEAREST);marked=raw.copy();draw=ImageDraw.Draw(marked)
        def project(p):return ((p[0]-box[0])*4,(p[1]-box[1])*4)
        draw.line([project(p) for p in r['outline']],fill='cyan',width=2)
        a,b=project(r['xy']);draw.rectangle((a-4,b-4,a+4,b+4),outline='white',width=2)
        a,b=project(r['bright_patch']['centroid']);draw.ellipse((a-5,b-5,a+5,b+5),outline='magenta',width=2)
        a,b=project(r['interior_centroid']);draw.line((a-5,b,a+5,b),fill='lime',width=2);draw.line((a,b-5,a,b+5),fill='lime',width=2)
        pair=Image.new('RGB',(520,295),'#202020');pair.paste(raw,(0,35));pair.paste(marked,(260,35));d=ImageDraw.Draw(pair);d.text((5,4),r['id']+' '+r['split']+' sector '+str(r['sector']),fill='white');d.text((5,19),'Raw | cyan interior, white peak, magenta bright centroid, green interior centroid',fill='white')
        pair.save(OUT/f'yellow-calibration-{j+1:02d}.png')
    for r in rows:
        if r['interior_centroid'] is not None:
            measure.append(dict(id=r['id'],color=r['color'],split=r['split'],specular_candidate=r['specular_candidate'],
                peak_minus_interior_centroid=(np.array(r['xy'])-r['interior_centroid']).tolist(),
                bright_minus_interior_centroid=(np.array(r['bright_patch']['centroid'])-r['interior_centroid']).tolist(),
                warning='Interior centroid is NOT a physical or visible-silhouette center'))
    save(OUT/'highlight-relative-interior.json',measure);save(OUT/'yellow-calibration-index.json',[dict(id=r['id'],sector=r['sector'],split=r['split']) for r in selected])


def plots(comp):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    main=[n for n in ('initial','light_only','interior_geometry','joint_refined','uniform_refined','mixed_joint','metric_refined','contact_joint') if n in comp]
    fig,axs=plt.subplots(1,3,figsize=(13,4),layout='constrained')
    for ax,col in zip(axs,('yellow','red','black')):
        for split,style in [('train','o--'),('holdout','s-')]:
            ax.plot(range(len(main)),[comp[n]['metrics'][split+'/'+col]['highlight']['rms'] for n in main],style,label=split)
        ax.set_title(col);ax.set_xticks(range(len(main)),main,rotation=65,ha='right');ax.set_ylabel('Brightness-patch displacement RMS (native px)');ax.grid(alpha=.25);ax.legend()
    fig.savefig(OUT/'fit-comparison.png',dpi=160);plt.close(fig)


def report(comp):
    main=[n for n in ('initial','light_only','interior_geometry','joint','joint_refined','uniform_before','uniform_refined','mixed_light','mixed_joint','metric_before','metric_refined','contact_light','contact_joint') if n in comp]
    lines=['# R276 — integrated 3D reconstruction and one shared distant light','',
      '**Working full-photo reconstruction and quantitative fitting are implemented. A physically certified reconstruction is not established.** All R259–R275 observations, masks and prior model artifacts remain unchanged.','',
      '[Numerical comparison and reproduction](review/r276/README.md) · [individual residuals](review/r276/individual-residuals.csv) · [shared-light POV-Ray appearance](review/r276/mixed_joint-pov.png) · [contact-constrained alternative](review/r276/contact_joint-pov.png) · [source photograph](../beads-photo-2.jpg)','',
      'The literal rounded, hole-bearing source bead is ray-traced with all necklace beads available as occluders and directional-light blockers. Unknown model colors stay gray; colored renders show conditional ownership, not a recovered string sequence.','',
      '| Experiment | Yellow train RMS | Yellow held-out RMS | Red held-out RMS | Black held-out RMS | Yellow held-out maximum |','|---|---:|---:|---:|---:|---:|']
    for n in main:
        m=comp[n]['metrics'];v=[m['train/yellow']['highlight']['rms']]+[m['holdout/'+c]['highlight']['rms'] for c in ('yellow','red','black')]+[m['holdout/yellow']['highlight']['maximum']]
        lines.append('| '+n+' | '+' | '.join(f'{x:.2f}' for x in v)+' |')
    lines+=['','All values are native pixels. Fixed photographic denominators: 175 training/37 held-out yellow specular candidates, 54/20 red, 160/39 black. Missing predictions remain as explicit 30px reporting sentinels, separately counted; every valid residual is untrimmed in the ledger. These are candidate brightness peaks, not verified mirror highlights. Later correction holdouts are exploratory because earlier outcomes had already been inspected.','',
       'Four methods were considered before implementation: frozen geometry/shared light; positive-interior geometry; joint geometry/light; and a normalized tangent/radial-frame empirical control. The first shared-light fit improves held-out yellow and black agreement. Subsequent pure-specular joint fitting improves yellow but worsens black, so it is not accepted as a universal improvement. At frozen light_only geometry, the empirical control loses to the directional model on paired held-out subsets.','',
       'Yellow peaks remain strongly colored. A neutral-only gate produced no reliable yellow calibration cases; that failed control is saved. The final photographic gate also accepts strong yellow peaks substantially desaturated relative to their own interiors. A shared diffuse/specular mixture is tested separately, preserving the pure-specular prediction. No red/yellow/black-specific light directions, finite-distance source or extra lamp is introduced.','',
       'The contact-constrained N1950/h−1 follow-up improves its held-out yellow brightness RMS from 11.95 to 11.25 px. It has zero sampled penetrations after 16,384 surface samples per bead, including flat faces; a bounding-sphere scan finds only the checked ±1/6/7 pair families. Minimum sampled clearance is 0.00457 source units. This is a plausible contact-consistent alternative, not a certified count: total native interior ownership is 65.7%, versus 74.3% for the inherited geometry, and black held-out RMS is 11.49 px. The extra 91-evaluation follow-up was selected by contact feasibility; do not use its extra budget as a fair count-ranking advantage.','',
       'The most important new failure is physical packing: the inherited literal source placement intersects its neighbors extensively. Small phase/strain adjustments do not remove this. Larger rope-radius, lower-count and absolute metric-calibration controls are retained, with their photographic costs; they are sensitivity hypotheses, not newly confirmed construction facts. The 15% projected-size metric control reduces the high-count contact violations to 235 sampled ±6 pairs, but held-out yellow interior ownership falls to 57.2%. It is not adopted. The source bead dimensions and shape are unchanged in the metric control; the centerline and camera unit calibration change together before a fixed-length fit.','',
       'Bending uses periodic normal displacement; longitudinal redistribution integrates a smooth strain field against physical arclength with zero net integral; twist changes a separate periodic phase field. Each hypothesis fixes its centerline length and integer winding. The inherited R258 material chart has about −11.3%/+10.4% local speed variation. The uniform-material correction explicitly removes this inherited variation before allowing small new strain. No individual bead translations are fitted.','',
       'R275 interiors constrain positive surface ownership only. Their boundaries are **not** complete visible silhouettes; symmetric outline error and silhouette IoU remain unavailable. Native ownership is checked at every one of the 807 exact masks; the three location-only observations have no invented area or mask error. Possible detection corrections are not applied. Large mismatches remain diagnosis candidates, not permission to move photographic measurements.','',
       'Count, helicity and camera alternatives have matched phase-start/search budgets. Their local objectives do not establish a unique bead count or physical correspondence. The broad inherited registration is a warm start, not an independent recovery of every centerline span. Geographic holdouts are withheld from R276 optimization, not from all historical fitting that produced the initialization. Relative gains, roughness, diffuse mixture and illumination direction remain conditional, without radiometric camera calibration.','',
       'The mixed fit’s shared direction is (−0.25218,+0.41879,+0.87236), versus (−0.06330,+0.18177,+0.98130) for the contact alternative, in the saved source world frame. This geometry dependence prevents identifying a unique lamp direction. Fixing the initial correspondences gives 11.78 px held-out yellow RMS for joint_refined, compared with 10.55 px when rematched: some improvement is correspondence-dependent.','',
       'Validation: 38 scientific tests pass; 810 locations, 807 masks and 4,166 preexisting files are unchanged. A saved mixed-model numerical/array/render replay is exact. One historical R258 immutable-review test expects an older ignored user-review hash; that review is preserved and the stale check is reported separately. Camera grazing rays remain conservatively unknown (180 of 220,131 native positive pixels in mixed_joint), with their coordinates saved; directional-shadow nonconvergence is counted and treated blocked. Native 1px sampling checks bound grid error separately from photographic error.','',
       'See the evidence index for light sensitivity, native-grid convergence, fixed-correspondence controls, material-normalized brightness/shape errors, closure/contact diagnostics, worst native crops and all saved alternatives. The stopping point is a reproducible integrated experiment with explicit failures. Next: resolve absolute bead-to-rope scale and noninterpenetrating placement against the photograph before extending deformation freedom or recovering string indices. Keep the current model/reasoning; no `/new` is required for reviewing this evidence.']
    (ROOT/'photo2/RECONSTRUCTION_R276.md').write_text('\n'.join(lines)+'\n')
    index=['# R276 evidence and reproduction','', '[Main report](../../RECONSTRUCTION_R276.md)','',
       '- `observations.json`: unchanged R275 measurements plus documented photo-only gates and fixed sector splits; all810 records,807 exact masks. The295 uncertain source candidates remain separate in R275.',
       '- `neutral-only-observations-control.json`: failed initial yellow-neutrality selection, preserved before fitting.',
       '- `protocol.json`: bounds, priors, four methods and assumptions.',
       '- `MODEL.json`: complete base spline, count/hand/camera, parameters, shared light and fit trace.',
       '- `MODEL-audit.json.gz`: all810 individual predictions, alternatives, uncertainties, exact native ownership, shape/brightness residuals and maximum errors.',
       '- `MODEL-surfaces.npz`: exact first-hit samples on the full2px grid, owner, world normals, specular and diffuse response. Hidden beads remain in the scene, not fabricated surfaces.',
       '- `MODEL-prediction.png`, `MODEL-highlights.png`, `MODEL-worst-*.png`: full photo prediction, cyan observed/magenta predicted peaks, and raw/marked native worst crops. White dots are predicted surface samples; cyan contours are conservative interiors.',
       '- `yellow-calibration-*.png`: distributed raw photographic evidence; native brightest pixels,85%-bright-patch centroids and interior centroids kept distinct.',
       '- `*-collisions.json`, `packing-*-screen.json`, `metric-calibration-screen.json`: sampled exact-surface interpenetration tests. A zero sampled violation does not prove global noninterpenetration.',
       '- `maker-B-positive-audit.json`: the preserved maker-confirmed seven yellow B pixels, audited separately without inserting legacy index2 into fitting.',
       '- `*-unfinished-rays.json`: native positive-pixel and full-grid grazing rays left unknown; no fabricated completed ownership.',
       '- `*-full-profile-collisions.json`: denser 16,384-point contact checks including flat faces, plus all bounding-sphere pair families.',
       '- `*-fixed-correspondence.json`: performance with frozen owner hypotheses from the same count/hand. Contact uses its N1950/h−1 screen, never N2696 indices. The invalid first cross-count diagnostic is archived and superseded; a regression test guards the correction. Improvements from rematching remain visible.',
       '- `*-implied-light.json`: mirror-normal diagnostic at observed peaks, conditional on geometry and source ownership.',
       '- `*-native-convergence.json.gz`:1px versus2px highlights and visible surfaces on a deterministic distributed subset.',
       '- `*-empirical.json`: normalized tangent/radial control, singular-frame exclusions and paired physical scores.',
       '- `*-diffuse-control.json`, `*-shape-brightness.json`: shared yellow diffuse-mixture control, width/orientation discrepancies, material-normalized intensity errors.',
       '- `*-light-sensitivity.json`: training objective under direction/roughness perturbations. Local sensitivity is not a confidence interval.',
       '- `preserved-hashes.json`, `validation.json`, `provenance.json`: preservation, test results, native replay, source and artifact hashes.','',
       'The fit loss uses positive-support squared distance after raster-quantization allowance, divided by16; yellow brightness displacement squared, divided by36; and independent deformation priors. Support costs clip at144px², light costs at900px² during fitting. Mixed controls add half-weight black training reflection cost. Final ledgers retain untrimmed distances and explicit missing cases. Assignment is one-to-one within each split and based on positive support only, with unmatched alternatives; it is not photographic identity. Cross-split owner/color conflicts are reported.','',
       'Engineering uncertainty:2px for selected specular candidates,4px otherwise; neither is a calibrated posterior error. Bright-patch shapes use the same connected85%-of-peak convention as R275. Sharp lobes are sampling-sensitive; convergence controls quantify that limitation. Original unweighted patch centroids remain in bright_patch. Fitting uses a separately derived centroid weighted by ICC luminance minus the interior 30th-percentile floor, on the same preserved 85% patch. Material gains are one shared gain per color, trained without held-out brightness; they do not recover physical exposure/albedo.','',
       'Reproduce the complete dependency-ordered experiment with `OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r276`. The original neutral-only failed selection remains an archived control. Individual stages and cheap saved-model replay are available below. Python3.12, existing environment, no downloads:','',
       '```bash','OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reconstruct_r276 --stage fit',
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reconstruct_r276 --stage alternatives',
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.diagnose_r276 correction',
       "OPENBLAS_NUM_THREADS=1 .venv/bin/python -c 'from photo2.diagnose_r276 import mixed_correction,packing_fits; mixed_correction(); packing_fits()'",
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reconstruct_r276 --stage audit --names initial light_only interior_geometry joint joint_refined uniform_before uniform_joint uniform_refined mixed_light mixed_joint',
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.diagnose_r276 diagnostics --name mixed_joint',
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.diagnose_r276 contact',
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.diagnose_r276 checks --name contact_joint',
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.validate_r276',
       "OPENBLAS_NUM_THREADS=1 .venv/bin/python -c 'from photo2.diagnose_r276 import fixed_and_normals,convergence,material_control; fixed_and_normals(\"mixed_joint\"); convergence(\"mixed_joint\"); material_control(\"light_only\")'",
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.test_reconstruct_r276 photo2.bead_debugger.test_surface',
       'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.report_r276',
       'povray +Iphoto2/review/r276/light_only.pov +Ophoto2/review/r276/light_only-pov.png +W1016 +H1273 +FN -D +A0.2 +WT2','```','',
       'Saved models can be replayed directly with `--stage audit --names MODEL`; this does not rerun optimization. POV-Ray uses the literal source bead macro. Its display material differs from the quantitative Blinn-lobe diagnostic and is not a radiometric validation. Browser rendering was not needed for these standalone photographic/POV artifacts.','',
       '| Saved model | N | hand | focal px | held-out yellow RMS | held-out black RMS |','|---|---:|---:|---:|---:|---:|']
    for n,r in comp.items():index.append(f"| [{n}]({n}.json) | {r['n']} | {r['h']:+d} | {r['focal']} | {r['metrics']['holdout/yellow']['highlight']['rms']:.3f} | {r['metrics']['holdout/black']['highlight']['rms']:.3f} |")
    (OUT/'README.md').write_text('\n'.join(index)+'\n')


def main():
    comp=ledger();photographic_calibration();plots(comp);report(comp)
    save(OUT/'environment.json',dict(python=sys.version,platform=platform.platform(),numpy=np.__version__))

if __name__=='__main__':main()
