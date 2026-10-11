"""Package reproducible R258 metrics and curated review images after all fits."""
import copy,csv,json
import numpy as np
from PIL import Image,ImageOps
from .refit import OUT,ROOT,BeadCurve,SurfaceLoss,physical
from .models import load,rays
from .generate import save,sha
from .report_r258 import panel


def run():
    results=json.loads((OUT/'results.json').read_text());alt=json.loads((OUT/'alternatives.json').read_text());compact=json.loads((OUT/'compact-controls.json').read_text());glob=json.loads((OUT/'global-summary.json').read_text());base=json.loads((OUT/'initial.json').read_text());ii=np.arange(base['n']);old=load('N2696_h+1_f0')[1];oldline=old.view.project(old.geometry(ii)['line'])
    names=['curve_constant_x_px','curve_constant_y_px','curve_linear_x_px','curve_linear_y_px','curve_quadratic_x_px','curve_quadratic_y_px','phase_delta_rad','phase_gradient_rad','elevation_delta_deg','roll_delta_deg','registration_x_px','registration_y_px','longitudinal_shift_px','camera_log_scale_delta']
    for rows,name in [(results,'results.json'),(alt,'alternatives.json'),(compact,'compact-controls.json')]:
        for r in rows:r['named_parameters']=dict(zip(names,r['parameters']))
        save(OUT/name,rows)
    ids=[r['id'] for r in results]+[r['id'] for r in alt if r['section']=='origin']+[r['id'] for r in compact]+['R258_distributed_C','R258_global_low_modes'];save(OUT/'model-index.json',ids)
    from scipy.spatial import cKDTree
    reference=cKDTree(old.seed_image_curve)
    displacements=[]
    for mid in ids:
        c=json.loads((OUT/(mid+'.json')).read_text())
        if c['n']!=base['n']:continue
        m=BeadCurve(c);q=m.view.project(m.geometry(ii)['line']);d=np.linalg.norm(q-oldline,axis=1);row=dict(id=mid,mean=float(d.mean()),rms=float(np.sqrt(np.mean(d**2))),max=float(d.max()),origin=float(d[base['origin']+2]));distance=reference.query(q)[0];row['nearest_historical_image_curve_px']=dict(mean=float(distance.mean()),rms=float(np.sqrt(np.mean(distance**2))),median=float(np.median(distance)),max=float(distance.max()),note='Nearest-curve reference comparison only; not an objective or acceptance score');displacements.append(row)
        if mid in [r['id'] for r in results]:
            a=next(r for r in results if r['id']==mid);a['curve_displacement_px'].update(mean=row['mean'],rms=row['rms'],maximum=row['max'])
    save(OUT/'curve-displacements.json',displacements);save(OUT/'results.json',results)
    j=base['origin']+2;g=old.geometry([j]);a=old.view.project(g['line'])[0];t=old.view.project(g['line']+g['tangent'])[0]-a;t/=np.linalg.norm(t);components=[]
    for variant in ['C2','C','D']:
        m=BeadCurve(json.loads((OUT/f'R258_origin_{variant}.json').read_text()));g=m.geometry([j]);b=m.view.project(g['line'])[0];delta=b-a;tt=m.view.project(g['line']+g['tangent'])[0]-b;tt/=np.linalg.norm(tt)
        components.append(dict(variant=variant,displacement=delta.tolist(),tangent_component=float(delta@t),normal_component=float(delta@np.array([-t[1],t[0]])),tangent_rotation_deg=float(np.degrees(np.arctan2(t[0]*tt[1]-t[1]*tt[0],t@tt)))))
    save(OUT/'origin-curve-components.json',components)
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');c2=json.loads((OUT/'R258_origin_C2.json').read_text());new=BeadCurve(c2)
    for k in range(8):
        gi=base['origin']+k;p=old.view.project(old.geometry([gi])['centers'])[0];box=[int(p[0]-43),int(p[1]-43),int(p[0]+43),int(p[1]+43)]
        panels=[panel(photo,box,title=f'Bead {k}: original'),panel(photo,box,old,gi,title='A: old footprint'),panel(photo,box,new,gi,title='C2: curve displacement only')]
        im=Image.new('RGB',(sum(p.width for p in panels),panels[0].height));x=0
        for p in panels:im.paste(p,(x,0));x+=p.width
        im.save(OUT/f'bead-{k}-compact-comparison.png')
    # Frozen-assignment neighbor audit, supplementary to dynamic matching.
    obs=json.loads((OUT/'origin-evidence.json').read_text())['observations'];a=next(r for r in results if r['id']=='R258_origin_A');ref={r['id']:r for r in a['observations']};fixed=[]
    for c in [json.loads((OUT/f'R258_origin_{v}.json').read_text()) for v in ['A','B','C','D','C2','C4']]:
        m=BeadCurve(c);g=m.geometry(ii)
        for r in obs:
            target=ref[r['id']]['owner'];pp=np.array(r['patch']);owner,_,un=rays(m,pp,g)
            fixed.append(dict(model=c['id'],observation_id=r['id'],reference_generator=target,reference_k=ref[r['id']]['k'],fraction=float(np.mean((owner==target)&(owner>=0)&(un==0))),status='Frozen fresh-A correspondence diagnostic, not a historical maker identity'))
    save(OUT/'fixed-neighbor-correspondences.json',fixed)
    # Separate raw ray ownership, including unknown/background sentinel, for
    # every native pixel in the origin crop. Reproducible arrays stay ignored.
    cache=ROOT/'photo2/output/debugger/r258';cache.mkdir(parents=True,exist_ok=True)
    box=json.loads((OUT/'origin-evidence.json').read_text())['box'];y,x=np.mgrid[box[1]:box[3],box[0]:box[2]];xy=np.c_[x.ravel(),y.ravel()]
    for variant in ['A','B','C','D','C2']:
        c=json.loads((OUT/f'R258_origin_{variant}.json').read_text());m=BeadCurve(c);own,_,un=rays(m,xy,m.geometry(ii));np.savez_compressed(cache/f'origin-{variant}-owners.npz',box=box,owner=own.reshape(x.shape),unfinished=un.reshape(x.shape))
    # Six-neighbor packing measurements (soft separation is not collision proof).
    packing=[]
    for mid in ['R258_origin_C2','R258_origin_C','R258_origin_D','R258_distributed_C']:
        c=json.loads((OUT/(mid+'.json')).read_text());m=BeadCurve(c);g=m.geometry(ii);dist={}
        for j in [1,6,7]:
            d=np.linalg.norm(g['centers']-np.roll(g['centers'],-j,axis=0),axis=1);dist[str(j)]=dict(min=float(d.min()),median=float(np.median(d)),max=float(d.max()))
        packing.append(dict(id=mid,physical=physical(m),six_neighbor_distance_units=dist))
    save(OUT/'packing.json',packing)
    # Tables summarize proposal-weighted ownership, never certify body counts.
    lines=['# R258 review artifacts and numerical summary','','[Scientific method and limitations](../../BEAD_DRIVEN_R258.md) · [Debugger instructions](../../bead_debugger/README.md)','','Only seven B pixels are maker-confirmed bead2 support. The 49-pixel union was rejected. Full visible area and boundary IoU remain unknown.','','## Primary comparison','','Ownership means below are averages over observations, using exact native rays on retained positive samples. Bodies are **conditionally distinct proposals**, not verified counts. Entire component groups are held out. Averages include unassigned proposals.','','| Section / variant | Train ownership | Held-out ownership | Explained distinct candidates (all) | Physical cost | Max curve movement px |','| --- | ---: | ---: | ---: | ---: | ---: |']
    for r in results:
        a=r['metrics'];lines.append(f"| {r['section']} {r['variant']} | {a['train']['ownership_mean']:.3f} | {a['holdout-body']['ownership_mean']:.3f} | {a['all']['explained_distinct_candidates']}/{a['all']['distinct_candidates']} | {r['physical']['cost']:.6f} | {r['curve_displacement_px']['maximum']:.2f} |")
    lines+=['','## Explicit post-hoc complexity control','','C2 and C4 were tried after the primary held-out regression was observed. These are exploratory controls, not untouched validation.','','| Control | Confirmed bead2 pixels owned | Train ownership | Held-out ownership | Max curve movement px |','| --- | ---: | ---: | ---: | ---: |']
    for r in compact:
        b=next(x for x in r['observations'] if x['identity']==2);d=next(x for x in displacements if x['id']==r['id']);lines.append(f"| {r['id']} | {round(b['owned_fraction']*7)}/7 | {r['metrics']['train']['ownership_mean']:.3f} | {r['metrics']['holdout-body']['ownership_mean']:.3f} | {d['max']:.2f} |")
    lines+=['','[C2 raw/old/new bead2 comparison](bead-2-compact-comparison.png). Equivalent clean comparisons are saved for beads0–7.','','## Matched count and helicity screens','','Each row averages four section holdouts after separate local fits: eight phase starts and220 joint-search evaluations per section, identical evidence, with no predetermined identities. These are not globally closed photo-identity solutions.','','| N | h−1 held-out mean | h+1 held-out mean |','| ---: | ---: | ---: |']
    for n in [2674,2681,2696,2700]:
        means=[np.mean([a['metrics']['holdout-body']['ownership_mean'] for a in alt if a['n']==n and a['h']==h]) for h in [-1,1]];lines.append(f'| {n} | {means[0]:.4f} | {means[1]:.4f} |')
    lines+=['','Both hands/counts remain viable; no exact N, hand, globally verified numbering or repeated color pattern is claimed. Untested counts2670–2700 are not excluded.','','## Files','','- `results.json`: all primary fit parameters, scores, per-observation residual distributions and spatial cross-evaluation.','- `alternatives.json`: all32 count/hand/section fits and exact evidence scores.','- `compact-controls.json`: C2/C4 exploratory controls.','- `*-evidence.json`: pixels, stable detector IDs, uncertainty, geographic boxes and group splits.','- `bead2-reviewed-support.json`, `questions.json`: maker correction, explicit seven-pixel support and answer history.','- `R258_*.json`: serialized absolute curve knots, camera, phase, winding, count, hand and explicit namespace.','- `model-index.json`:28 additive debugger models; old three models remain unchanged.','- `sensitivity.json`, `ablations.json`: one-parameter tests, bead dimensions and fitted-parameter removals.','- `native-neighbors.json`: native footprint areas/centroids for0–7 and every ±1/6/7 neighbor.','- `index-occlusion.json`: hypothetical index substitutions and explicit ownership limitations.','- `assignment-stability.json`, `fixed-neighbor-correspondences.json`: changed conditional indices and frozen fresh-A match audit.','- `curve-displacements.json`, `packing.json`, `global-summary.json`: geometric changes, six-neighbor distances and partial global curve.','- `synthetic-curve.json`, `synthetic-phase.json`, `validation.json`, `browser-verification.json`: validation.','- `provenance.json`, `artifact-hashes.json`, `immutable-inputs.json`: reproduction inputs and integrity.','','## Reproduce','','```bash','.venv/bin/python -m photo2.bead_debugger.refit --budget 400','.venv/bin/python -m photo2.bead_debugger.alternatives_r258','.venv/bin/python -m photo2.bead_debugger.compact_r258','.venv/bin/python -m photo2.bead_debugger.audit_r258','.venv/bin/python -m photo2.bead_debugger.global_r258','.venv/bin/python -m photo2.bead_debugger.report_r258','.venv/bin/python -m photo2.bead_debugger.package_r258','.venv/bin/python -m unittest photo2.bead_debugger.test_debugger photo2.bead_debugger.test_surface photo2.bead_debugger.test_refit','node photo2/bead_debugger/static/logic.test.mjs','PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_debugger.browser_smoke --output photo2/output/debugger/smoke-r258','.venv/bin/python -m photo2.bead_debugger.server','```','','Python3.12 and existing dependencies. Fresh detection can be reproduced with `python -m photo2.bead_debugger.generate`; normal server startup verifies its cached provenance. Generated native ownership NPZ files are under ignored `photo2/output/debugger/r258/`; the debugger exports selected native owners in each ZIP. Reviews are never automatically consumed by the fitter.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')
    save(OUT/'artifact-hashes.json',{p.name:sha(p) for p in OUT.glob('*.png')})
    provenance=json.loads((OUT/'provenance.json').read_text())
    for p in list((ROOT/'photo2/bead_debugger').glob('*.py'))+list((ROOT/'photo2/bead_debugger/static').glob('*')):
        if p.is_file():provenance['sources'][str(p.relative_to(ROOT))]=sha(p)
    provenance['audits']=[f'.venv/bin/python -m photo2.bead_debugger.{name}' for name in ['alternatives_r258','compact_r258','audit_r258','global_r258','report_r258','package_r258']]
    save(OUT/'provenance.json',provenance)
    with (OUT/'metrics.csv').open('w') as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(['model','section','variant','train_positive_ownership','heldout_positive_ownership','physical_cost','curve_max_px'])
        for r in results:writer.writerow([r['id'],r['section'],r['variant'],r['metrics']['train']['ownership_mean'],r['metrics']['holdout-body']['ownership_mean'],r['physical']['cost'],r['curve_displacement_px']['maximum']])
if __name__=='__main__':run()
