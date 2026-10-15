"""Freeze principal models, then perform the single reserved evaluation/export."""
import csv,datetime,argparse
from copy import deepcopy
import numpy as np
from .common import *
from .geometry import Chain
from .evaluate import evaluate,summary
from .physical_audit import audit
from .sensitivity import mirror

def models():
    revision=read(OUT/'joint.json');opposite=max([r for r in revision['candidates'] if r['parameters']['hand']==-1],key=lambda r:r['train']['score'])
    return {'R294':read(ROOT/'photo2/r294/results/revised.json')['selected']['parameters'],
        'local':read(OUT/'local.json')['selected']['parameters'],'global':read(OUT/'global.json')['selected']['parameters'],
        'geometry':read(OUT/'revision.json')['selected']['parameters'],
        'R295':revision['selected']['parameters'],'opposite':opposite['parameters'],'light':read(OUT/'light-alternative.json')['selected']['parameters']}

def visibility(scene,shape):
    h,w=shape;mask=np.zeros((h,w),bool);bound=int(np.ceil(scene.query_radius))+2
    for cx,cy in scene.pc:
        x0,y0=np.maximum(0,np.floor([cx-bound,cy-bound]).astype(int));x1,y1=np.minimum([w,h],np.ceil([cx+bound,cy+bound]).astype(int)+1)
        if x1>x0 and y1>y0:mask[y0:y1,x0:x1]=True
    yy,xx=np.where(mask);xy=np.c_[xx,yy];d=scene.trace(xy);owner=np.full(len(xy),-999,int);good=d['owner']>=0;owner[good]=scene.indices[d['owner'][good]]
    return xy,owner,d

def export(name,scene,result,xy,owner,d,sensitivity):
    rows=[];obs=result['observations'];params=scene.p;cert=result['contact'];counts=d['isolated_counts'];samples=scene.surface_points();support=[]
    for j,k in enumerate(scene.indices):
        if not -20<=k<=200:continue
        pts=xy[owner==k];linked=[r for r in obs if r['index']==k];compatible=[r for r in linked if r['compatible']];alternatives=[dict(id=r['id'],fraction=a['fraction']) for r in obs for a in r['alternatives'] if a['index']==k and r['index']!=k]
        q=np.array([s.pc[j] for s in sensitivity]) if sensitivity else np.array([scene.pc[j]])
        rows.append(dict(index=int(k),conditional=True,center_xyz=scene.centers[j].tolist(),projected_geometric_center=scene.pc[j].tolist(),physical_parameters=params,
            visible_surface=dict(pixel_count=len(pts),runs=runs(pts),centroid=pts.mean(0).tolist() if len(pts) else None,source=f'{name}-visibility.npz'),
            projected_surface_samples=scene.project(samples[j][::8]).tolist(),isolated_pixels=int(counts[j]),visible_fraction=float(len(pts)/max(1,counts[j])),
            correspondences=[dict(id=r['id'],kind=r['kind'],source_color=r['color'],containment=r['containment'],compatible=r['compatible'],split=r['split']) for r in linked],
            alternative_assignments=alternatives,meaningful_photographic_support=bool(compatible),support_status='compatible photographed support, identity unverified' if compatible else 'geometric prediction without compatible observed support',
            disagreements=[dict(id=r['id'],containment=r['containment'],alternatives=r['alternatives']) for r in linked if not r['compatible']],
            uncertainty=dict(kind='Conditional finite parameter sensitivity, not CI; excludes unknown correspondence families',radius_px=float(np.linalg.norm(q-scene.pc[j],axis=1).max()),min_xy=q.min(0).tolist(),max_xy=q.max(0).tolist()),
            physical_feasibility=result['physical_audit']['state'],physical_identity_verified=False,model_color=None))
    assert len(rows)==221 and [r['index'] for r in rows]==list(range(-20,201))
    save(OUT/(name+'-positions.json.gz'),dict(model=name,records=rows,parameters=params,photo_sha256=read(EVIDENCE/'inputs.json.gz')['photo']['photo_sha256']))
    with (OUT/(name+'-positions.csv')).open('w') as f:
        writer=csv.writer(f);writer.writerow(['index','x','y','visible_pixels','visibility_fraction','compatible_support','sensitivity_px','physical_feasibility','conditional'])
        for r in rows:writer.writerow([r['index'],*r['projected_geometric_center'],r['visible_surface']['pixel_count'],r['visible_fraction'],r['meaningful_photographic_support'],r['uncertainty']['radius_px'],r['physical_feasibility'],True])
    result['run_summary']=dict(positions=221,supported_positions=sum(r['meaningful_photographic_support'] for r in rows),unsupported_positions=sum(not r['meaningful_photographic_support'] for r in rows),visibility_below_point_one=sum(r['visible_fraction']<.1 for r in rows))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume-frozen',action='store_true');args=parser.parse_args()
    data=read(EVIDENCE/'inputs.json.gz');principal=models()
    if args.resume_frozen:
        frozen=read(EVIDENCE/'final-freeze.json');assert principal==frozen['models'];assert sha(EVIDENCE/'inputs.json.gz')==frozen['inputs_sha256']
    else:
        assert not (EVIDENCE/'final-freeze.json').exists(),'Already frozen; use --resume-frozen without changing models.'
        save(EVIDENCE/'final-freeze.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),models=principal,
            source_hashes=source_hashes(),inputs_sha256=sha(EVIDENCE/'inputs.json.gz'),selection='R295 = joint ownership/material objective training winner; opposite hand and common-light alternatives retained. No reserved outcomes used.'))
    native,_,_=photo();perturb=[Chain(principal['R295'],data['r294'])];sens=[]
    for key,delta in [('radius',.03),('axial',.03),('pitch',.015),('turn',.015),('elevation',3.),('yaw',5.),('perspective',.0005),('phase',.08),('s0',1.)]:
        for sign in (-1,1):
            q=deepcopy(principal['R295']);q[key]+=sign*delta
            if key=='perspective' and q[key]<0:continue
            s=Chain(q,data['r294']);cert=s.certify(witnesses=False)
            sens.append(dict(parameter=key,delta=sign*delta,parameters=q,contact=cert))
            if cert['certified']:perturb.append(s)
    save(OUT/'final-sensitivity.json',dict(records=sens,limits='Finite one-factor sensitivities around primary model, only certified perturbations enter position envelopes. Not uncertainty coverage or independent evidence.'))
    results={}
    for name,p in principal.items():
        print('evaluate',name,flush=True);scene=Chain(p,data['r294']);r=evaluate(p,data);r['physical_audit']=audit(p,data['r294']);r['mirror_train']=mirror(scene,data,'train');held=mirror(scene,data,'reserved')
        if r['mirror_train'].get('direction') and held.get('evidence'):
            direction=np.array(r['mirror_train']['direction']);angles=[float(np.degrees(np.arccos(np.clip(np.dot(a['direction'],direction),-1,1)))) for a in held['evidence']]
            r['mirror_reserved']=dict(n=len(angles),angles=angles,median=float(np.median(angles)),light_fitted_to_training_only=True)
        xy,owner,d=visibility(scene,native.shape[:2]);np.savez_compressed(OUT/(name+'-visibility.npz'),xy=xy,owner=owner,unknown=d['unknown'])
        export(name,scene,r,xy,owner,d,perturb if name=='R295' else [])
        r['historical']={s:{k:summary([q for q in r['observations'] if q['historical_split']==s and q['kind']==k]) for k in ('patch','region')} for s in ('train','holdout')}
        save(OUT/(name+'-evaluation.json'),r);results[name]=r
    before={r['id']:r for r in results['R294']['observations']};changes=[]
    for r in results['R295']['observations']:
        a=before[r['id']];changes.append(dict(id=r['id'],kind=r['kind'],split=r['split'],point=r['point'],along_px=r['along_px'],old_index=a['index'],new_index=r['index'],old_containment=a['containment'],new_containment=r['containment'],delta=r['containment']-a['containment']))
    save(OUT/'comparison.json',dict(models={name:dict(summary=r['summary'],historical=r['historical'],diagnostics=r['diagnostics'],anchor=r['anchor_containment'],run=r['run_summary'],physical={k:v for k,v in r['physical_audit'].items() if k not in ('certificate','penetrations')},mirror_train=r['mirror_train'],mirror_reserved=r.get('mirror_reserved')) for name,r in results.items()},
        changes=changes,stable_assignments=sum(r['old_index']==r['new_index'] for r in changes),total_observations=len(changes),limits='Appearance compatibility is not recovered identity. Reserved automatic regions remain fallible; same photograph and multiple exposed historical rounds.'))
    print('final evaluation complete',flush=True)
if __name__=='__main__':main()
