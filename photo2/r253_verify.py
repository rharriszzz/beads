"""Reproducibility/integrity and numerical-sensitivity audit for R253."""
import sys,json,csv,hashlib,platform
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from global_fit_r253 import OUT,ROOT,Model,data,save,table,weights,penalties,full_visibility,RADIUS,patch_points,exact_training_score


def evaluate(out=OUT):
    models=json.loads((out/'models.json').read_text());selected=json.loads((out/'selected.json').read_text());extras=[]
    for m in models:
        rr=json.loads((out/f'{m["model_id"]}-assignments.json').read_text());model=Model(m['n'],m['h'],m['p']);ids=np.array([r['generator_index'] for r in rr]);assert len(set(ids))==310
        g=model.geometry(ids);xy=np.array([[r['x'],r['y']] for r in rr]);delta=xy-model.view.project(g['centers']);r,d,_=model.view.basis();axis=np.c_[g['tangent']@r,g['tangent']@d]
        q=(np.sum(delta*delta,axis=1)+.51/(1-.51*np.sum(axis*axis,axis=1))*np.sum(delta*axis,axis=1)**2)/(RADIUS*model.view.scale)**2
        support=np.array([r['patch_support'] for r in rr]);cost=1-support+.15*q
        item=dict(model_id=m['model_id'],anchor=next(r for r in rr if r['observation_id']==m['anchor']))
        for split in ['train','test','test_core']:
            use=[i for i,r in enumerate(rr) if r['split']==('test' if split=='test_core' else split) and (split!='test_core' or min((r['arc_fraction']*32)%1,1-(r['arc_fraction']*32)%1)*9235.586/32>60)]
            item[split]=dict(n=len(use),balanced_full_patch_score=float(weights([rr[i] for i in use])@cost[use]),balanced_patch_support=float(weights([rr[i] for i in use])@support[use]))
        item['penalty']=float(np.sum(penalties(np.array(m['p']))**2));extras.append(item)
    save(out/'validation-scores.json',extras)
    prediction_checks=[]
    for mid in selected:
        rows=list(csv.DictReader((out/f'{mid}-predictions.csv').read_text().splitlines()));m=next(m for m in models if m['model_id']==mid)
        assert len(rows)==m['n'] and {int(r['k']) for r in rows}==set(range(m['n']))
        for r in rows:
            assert int(r['chart_A_u'])+7*int(r['chart_A_v'])==int(r['k'])
            assert -int(r['chart_B_u'])+6*int(r['chart_B_v'])==int(r['k'])
            assert r['predicted_color']=='unknown'
        prediction_checks.append(dict(model_id=mid,complete_indices=True,unique_indices=True,both_charts_consistent=True,no_predicted_color_invention=True))
    save(out/'prediction-checks.json',prediction_checks)


def resolution(out=OUT):
    selected=json.loads((out/'selected.json').read_text());models=json.loads((out/'models.json').read_text());results=[]
    for mid in [s for s in selected if s in ['N2671_h+1_both','N2671_h-1_rigid']]:
        m=next(m for m in models if m['model_id']==mid);model=Model(m['n'],m['h'],m['p']);g=model.geometry(np.arange(m['n']))
        for step in [2,1]:
            v=full_visibility(model,g,step=step);item=dict(model_id=mid,step_px=step,sampled_rays=v['sampled_rays'],uncertain_rays=v['uncertain_rays'])
            for name,floor,area in [('meaningful',.1,24),('distinguishable_proxy',.25,80)]:
                item[name]=int(((v['fraction']>=floor)&(v['area']>=area)).sum())
                item[name+'_numerical_lower']=int(((v['fraction_lower']>=floor)&(v['area']>=area)).sum())
                item[name+'_numerical_upper']=int(((v['fraction_upper']>=floor)&(v['area']+v['uncertain_area_bound']>=area)).sum())
            results.append(item);save(out/'visibility-resolution.json',results);print('resolution',item,flush=True)


def manifest(out=OUT):
    source_paths=['beads-photo-2.jpg','beads.pov','photo2/spline-seed-r175.json','photo2/count-seed-r175.json','photo2/manual-labels-r146.json','photo2/review/r144/corrected-report.json','photo2/review/r252/accepted.csv','photo2/review/r252/inventory.json','photo2/review/r250/angle-range-observations.csv','photo2/review/r250/candidates.csv']
    source_paths += ['photo2/'+name for name in ['global_fit_r253.py','r253_diagnostics.py','r253_verify.py','r253_replay.py','test_global_fit_r253.py','tangent_circles.py','bead_placement.py','curved_surface_fit.py','local_surface_fit.py','visible_correspondence.py']]
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    save(out/'verification.json',dict(python=platform.python_version(),numpy=np.__version__,scipy=__import__('scipy').__version__,pillow=__import__('PIL').__version__,matplotlib=__import__('matplotlib').__version__,source_hashes={p:sha(ROOT/p) for p in source_paths},artifact_hashes={str(p.relative_to(out)):sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='verification.json'},checks='See tests.txt, prediction-checks.json, source-integrity.json, numerical-replay.json and visibility-resolution.json; no independent photo precision assertion'))

if __name__=='__main__':
    if '--resolution' in sys.argv:resolution()
    elif '--manifest' in sys.argv:manifest()
    else:evaluate()
