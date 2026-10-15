"""References and matching are evaluation-only; detector output is already saved."""
import argparse
from collections import Counter
from .common import *
METHODS=('raw_point','raw_patch','raw_weighted','constant_point','constant_patch','constant_weighted','geographic','orientation','darkness')

def region(xy):
    a=(np.arctan2(xy[1]-1590.5,xy[0]-1269.5)%(2*np.pi))*6/(2*np.pi)
    sec=int(a);split='evaluation' if sec in (1,4) else 'development'
    if split=='development' and min(abs(a-v) for v in (1,2,4,5))<.08:split='buffer'
    return sec,split

def references():
    old=read(ROOT/'photo2/review/r276/observations.json')['observations'];refs=[]
    for r in old:
        if r['color'] not in ('red','yellow') or r['interior_centroid'] is None:continue
        refs.append(dict(id=r['id'],reference='R275',color=r['color'],centroid=r['interior_centroid'],runs=r['region_runs'],reliable=r['strong'],old_point=r['xy'],old_patch=r['bright_patch']['centroid']))
    seen=set()
    for stage in ('development','confirmation'):
        for case in read(ROOT/f'photo2/r288/results/{stage}.json.gz')['cases']:
            for o in case['observations']:
                if o['id'] in seen:continue
                seen.add(o['id'])
                for method in ('J','W'):
                    r=o['variants'][method];s=r['measured_support']
                    if not s:continue
                    e=o['evidence']['candidates'][method]
                    reliable=o['source_status']=='high' and 60<=s['pixel_count']<=870 and e['stability']['minimum_iou']>=.7 and e['stability']['domain_minimum_iou']>=.9
                    refs.append(dict(id=o['id'],case=case['name'],reference=method,color=o['color'],centroid=s['centroid'],runs=s['runs'],reliable=reliable,old_point=o['seed'],old_patch=None))
    return refs

def assemble():
    det=read(OUT/'photo-landmarks.json.gz')['records'];good=[r for r in det if r['accepted']];refs=references();rows=[]
    # Exact peak-in-reference membership only. Never choose the nearest observation.
    for ref in refs:
        inside={(x,y) for y,a,b in ref['runs'] for x in range(a,b+1)}
        matches=[r for r in good if tuple(r['point']) in inside]
        rejected=[dict(id=r['id'],reasons=r['reasons']) for r in det if not r['accepted'] and tuple(r['point']) in inside]
        sec,split=region(ref['centroid']);r={k:v for k,v in ref.items() if k!='runs'}
        r.update(region=sec,split=split,matches=[q['id'] for q in matches],rejected=rejected,match_status='unique' if len(matches)==1 else 'missing' if not matches else 'multiple')
        if len(matches)==1:r['landmark']=matches[0]
        rows.append(r)
    # A peak shared by reference masks is ambiguous, even if each mask has one peak.
    counts=Counter((r['reference'],m) for r in rows for m in r['matches'])
    for r in rows:
        if r['match_status']=='unique' and counts[r['reference'],r['matches'][0]]>1:r['match_status']='shared-reference'
    # Spatial separation in addition to angular partition: exclude development within
    # 100px of ANY evaluation reference. Only positions determine this buffer.
    ev=np.array([r['centroid'] for r in rows if r['split']=='evaluation'])
    for r in rows:
        if r['split']=='development' and len(ev) and np.min(np.linalg.norm(ev-r['centroid'],axis=1))<100:r['split']='buffer'
    return rows

def point(r,kind):
    q=r['landmark'];return np.array(q['point'] if kind.endswith('point') else q['centroid'] if kind.endswith('patch') else q['weighted'])

def features(r,method):
    q=r['landmark']
    if method=='geographic':
        a=np.arctan2(q['point'][1]-1590.5,q['point'][0]-1269.5);return [1.,np.sin(a),np.cos(a)]
    if method=='orientation':
        a=np.radians(q['shape']['orientation_deg']*2);return [1.,np.sin(a),np.cos(a)]
    return [1.]

def fit(rows,method):
    kind=method if method.startswith('constant') else 'weighted'
    residual=np.array([np.array(r['centroid'])-point(r,kind) for r in rows])
    if method=='darkness':
        d=np.array([r['landmark']['dark']['offset'] for r in rows]);dc=d-d.mean(0);rc=residual-residual.mean(0)
        beta=float(np.sum(dc*rc)/max(np.sum(dc*dc),1e-9))
        return dict(intercept=(residual.mean(0)-beta*d.mean(0)).tolist(),beta=beta)
    x=np.array([features(r,method) for r in rows]);coef=np.linalg.lstsq(x,residual,rcond=None)[0]
    return dict(coef=coef.tolist(),rank=int(np.linalg.matrix_rank(x)),train=len(rows))

def predict(r,method,model=None):
    if method.startswith('raw'):return point(r,method)
    if method=='darkness':return point(r,'weighted')+model['intercept']+model['beta']*np.array(r['landmark']['dark']['offset'])
    return point(r,method if method.startswith('constant') else 'weighted')+np.array(features(r,method))@np.array(model['coef'])

def eligible(rows,ref,col,split):return [r for r in rows if r['reference']==ref and r['color']==col and r['split']==split and r['reliable'] and r['match_status']=='unique']

def develop():
    rows=assemble();save(OUT/'associations.json.gz',rows);models={};counts={}
    for ref in ('R275','J','W'):
        for col in ('red','yellow','pooled'):
            train=[r for r in rows if r['reference']==ref and (col=='pooled' or r['color']==col) and r['split']=='development' and r['reliable'] and r['match_status']=='unique']
            if len(train)<4:continue
            for m in METHODS:
                if m.startswith('raw'):continue
                model=fit(train,m);err=[np.linalg.norm(predict(r,m,model)-r['centroid']) for r in train]
                residual=np.array([predict(r,m,model)-r['centroid'] for r in train])
                model.update(train=len(train),training_error=stats(err),residual_covariance=np.cov(residual.T).tolist(),training_radius90=float(np.percentile(err,90)))
                models[f'{ref}/{col}/{m}']=model
    save(OUT/'calibration-frozen.json',dict(models=models,detector_sha256=sha(OUT/'photo-landmarks.json.gz'),associations_sha256=sha(OUT/'associations.json.gz'),source_hashes={p:sha(Path(__file__).parent/p) for p in ('landmark.py','calibrate.py')},rule='>=10% RMS gain and no worse p90 required for extra complexity; color from reference is evaluation stratification, not certified runtime color',split='Six angular regions; 1,4 evaluation; .08-sector and 100px training buffers'))
    print('Frozen',len(models),'models; associations',Counter((r['reference'],r['split'],r['match_status']) for r in rows))

def evaluate():
    frozen=read(OUT/'calibration-frozen.json')
    for p,h in frozen['source_hashes'].items():assert sha(Path(__file__).parent/p)==h
    assert sha(OUT/'photo-landmarks.json.gz')==frozen['detector_sha256']
    assert sha(OUT/'associations.json.gz')==frozen['associations_sha256']
    rows=read(OUT/'associations.json.gz');scores={};individual=[];coverage={}
    for ref in ('R275','J','W'):
        for col in ('red','yellow'):
            for split in ('development','evaluation','buffer'):
                rr=[r for r in rows if r['reference']==ref and r['color']==col and r['split']==split]
                coverage[f'{ref}/{col}/{split}']=dict(total=len(rr),reliable=sum(r['reliable'] for r in rr),matches=dict(Counter(r['match_status'] for r in rr)),scored=len(eligible(rows,ref,col,split)))
                rr=eligible(rows,ref,col,split)
                for m in METHODS:
                    model=frozen['models'].get(f'{ref}/{col}/{m}')
                    if not m.startswith('raw') and model is None:continue
                    residuals=[];by_region={}
                    for r in rr:
                        p=predict(r,m,model);e=float(np.linalg.norm(p-r['centroid']));residuals.append(e);by_region.setdefault(r['region'],[]).append(e)
                        individual.append(dict(reference=ref,color=col,split=split,region=r['region'],id=r['id'],landmark=r['landmark']['id'],method=m,prediction=p.tolist(),target=r['centroid'],error=e))
                    scores[f'{ref}/{col}/{split}/{m}']=dict(total=stats(residuals),regions={k:stats(v) for k,v in by_region.items()})
    # Historical patch and point on exactly the new unique R275 comparison set.
    historical={}
    for col in ('red','yellow'):
        tr=eligible(rows,'R275',col,'development');te=eligible(rows,'R275',col,'evaluation')
        for name in ('old_point','old_patch'):
            shift=np.mean([np.array(r['centroid'])-r[name] for r in tr],axis=0)
            historical[f'{col}/{name}']=dict(shift=shift.tolist(),raw=stats([np.linalg.norm(np.array(r[name])-r['centroid']) for r in te]),corrected=stats([np.linalg.norm(np.array(r[name])+shift-r['centroid']) for r in te]))
    # Pooled constant is deployable without trusting the uncertain color classifier.
    pooled={}
    for col in ('red','yellow'):
        rr=eligible(rows,'R275',col,'evaluation');model=frozen['models']['R275/pooled/constant_weighted']
        pooled[col]=stats([np.linalg.norm(predict(r,'constant_weighted',model)-r['centroid']) for r in rr])
    save(OUT/'photo-evaluation.json',dict(scores=scores,coverage=coverage,historical_paired=historical,pooled_constant=pooled,diameter_proxy_px=30,semantics='Proxy centroid errors conditional on unique exact membership in accepted reference interiors; missing/multiple/shared observations remain unscored, never silently substituted.'))
    save(OUT/'photo-residuals.json.gz',individual)
    for k,v in scores.items():
        if k.startswith('R275/') and '/evaluation/' in k:print(k,v['total'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['development','evaluation']);a=p.parse_args();develop() if a.stage=='development' else evaluate()
