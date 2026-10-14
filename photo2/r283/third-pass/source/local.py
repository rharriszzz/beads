"""Four-anchor cold local fit, frozen neighboring surfaces, then photo evaluation."""
import itertools
import os
from copy import deepcopy
import numpy as np
from scipy.optimize import least_squares,linear_sum_assignment
from scipy.spatial import cKDTree
from photo2.r279.geometry import R,centers,frame,project,trace as source_trace,sdf
from photo2.r280.contact import certificate
from photo2.r282.phase1 import image_features
from .common import OUT,OLD,ROOT,photo,read,save,sha,pixels,support

SHAPE=(220,280)
LOCAL=OUT/os.environ.get('R283_LOCAL_NAME','local')
INDICES=np.arange(-40,41)
FIT_INDICES=np.arange(-21,22)

def trace(p,xy,indices=INDICES):return source_trace(p,xy,indices)
def certify(p):
    from types import SimpleNamespace
    return certificate(SimpleNamespace(centers=centers(INDICES,p['hand'],p['phase'],p['pitch']),
        bound=R*np.sqrt(1+.7**2),radius=R,g={'surface_tangent':np.tile([1.,0,0],(len(INDICES),1))}))

def connected(indices):
    seen={0}
    while True:
        more={b for a in seen for b in indices if abs(a-b) in (1,6,7,12,13,14)}
        if more<=seen:return len(seen)==len(indices)
        seen|=more

def axis_error(roll,axis):
    angle=np.degrees(np.arctan2(axis[1],axis[0]));return abs((roll-angle+90)%180-90)

def select():
    doc=read(OUT/'phase1.json.gz');rows=doc['records'];curve=np.asarray(read(OLD/'centerline.json')['points'])
    good=[r for r in rows if r['status']=='high' and r['color'] in ('red','yellow') and r['metrics']['area']>=80 and r['illumination']['peak']>=.25]
    pts=np.array([r['measured_photo_location'] for r in good]);candidates=[]
    for j in range(0,len(curve)-1,24):
        tangent=curve[(j+16)%(len(curve)-1)]-curve[(j-16)%(len(curve)-1)];tangent/=np.linalg.norm(tangent)
        if tangent[0]<0:tangent=-tangent
        normal=np.array([-tangent[1],tangent[0]]);along=(pts-curve[j])@tangent;cross=(pts-curve[j])@normal
        ids=np.flatnonzero((abs(along)<78)&(abs(cross)<29))
        if len(ids)<8 or abs(tangent[1])>.6:continue
        ordered=sorted(ids,key=lambda k:along[k]);trainpool=ordered[:max(4,len(ids)-4)]
        if len(trainpool)<4:continue
        # Spread anchors; prefer two yellow highlights but never use a manual ID.
        options=list(itertools.combinations(trainpool,4));best=None
        for ix in options:
            if not (min(cross[list(ix)])<0<max(cross[list(ix)])):continue
            ny=sum(good[k]['color']=='yellow' for k in ix)
            score=10*min(ny,2)+np.ptp(along[list(ix)])+.5*np.ptp(cross[list(ix)])
            if best is None or score>best[0]:best=(score,ix)
        if best is None:continue
        anchors=list(best[1]);held=[k for k in ordered if k not in anchors]
        nearby=curve[np.linalg.norm(curve-curve[j],axis=1)<80];curvature=float(np.std((nearby-curve[j])@normal))
        score=float(np.median([good[k]['illumination']['mean'] for k in ids]))-.02*curvature+.01*min(len(held),6)
        candidates.append(dict(score=score,center=curve[j].tolist(),axis=tangent.tolist(),
            anchor_ids=[good[k]['record_id'] for k in anchors],heldout_ids=[good[k]['record_id'] for k in held],curvature=curvature))
    assert candidates,'No sufficiently reliable two-sided region'
    if LOCAL.name!='local':
        previous=read(OUT/'local/anchors.json');previous_center=np.array(previous['origin'])+[140,110]
        candidates=[c for c in candidates if np.linalg.norm(np.array(c['center'])-previous_center)>=250]
    selected=max(candidates,key=lambda x:x['score']);origin=np.rint(np.array(selected['center'])-[140,110]).astype(int)
    by={r['record_id']:r for r in rows}
    def local(r):
        q=deepcopy(r);p=pixels(q['measured_support'])-origin;q['measured_support']=support(p);q['measured_photo_location']=p.mean(0).tolist();return q
    anchors=[local(by[k]) for k in selected['anchor_ids']];held=[local(by[k]) for k in selected['heldout_ids']]
    native,rgb,_=photo();from PIL import Image
    folder=LOCAL;folder.mkdir(parents=True,exist_ok=True)
    Image.fromarray(native).crop((*origin,*(origin+np.array(SHAPE[::-1])))).save(folder/'raw.png')
    np.save(folder/'managed-rgb.npy',rgb[origin[1]:origin[1]+SHAPE[0],origin[0]:origin[0]+SHAPE[1]])
    # Anchor luminance/reflections only: fit never opens the full crop.
    features=image_features(rgb)
    for r in anchors+held:
        p=pixels(r['measured_support']);pp=p+origin;lum=features['lum'][pp[:,1],pp[:,0]];sat=features['hsv'][pp[:,1],pp[:,0],1]
        use=(lum>=np.quantile(lum,.9))&(lum>.16)&((sat<.45)|(sat<np.median(sat)*.75))
        r['highlight']=dict(point=p[use].mean(0).tolist(),pixels=p[use].tolist()) if use.sum()>=3 else None
    save(folder/'anchors.json',dict(origin=origin.tolist(),anchors=anchors,axis=selected['axis'],phase1_sha256=sha(OUT/'phase1.json.gz'),
        selection_rule='Automatic straight two-sided bright region; left-side four anchors, remaining independently measured supports withheld. Selection is not blind to their existence.'))
    save(folder/'withheld.json',dict(records=held,selected=selected,candidates=candidates))
    print('local region',origin,'anchors',selected['anchor_ids'],'heldout',len(held),flush=True)


def vec(p):return np.array([*p['translation'],p['scale'],p['roll'],p['phase'],p['inclination'],p['pitch']])
def par(v,p):return {**p,'translation':v[:2].tolist(),'scale':float(v[2]),'roll':float(v[3]),'phase':float(v[4]),'inclination':float(v[5]),'pitch':float(v[6])}


def light_evidence(p,rows,assignments):
    rr,dd,eye=frame(p['inclination'],p['roll']);evidence=[]
    for r,k in zip(rows,assignments):
        if not r.get('highlight'):continue
        point=np.array(r['highlight']['point']);owner,depth,unknown=trace(p,point[None]);item=dict(id=r['record_id'],color=r['color'],point=point.tolist(),expected_owner=int(k),first_owner=int(owner[0]),usable=bool(k in INDICES and owner[0]==k and np.isfinite(depth[0]) and not unknown[0]))
        if item['usable']:
            base=((point-np.array(p['translation']))/p['scale'])@np.array([rr,dd]);xyz=base+depth[0]*eye
            q=xyz-centers([k],p['hand'],p['phase'],p['pitch'])[0]
            n=np.array([(sdf(q+np.eye(3)[j]*1e-4)-sdf(q-np.eye(3)[j]*1e-4))/2e-4 for j in range(3)])
            n/=max(np.linalg.norm(n),1e-12);direction=2*np.dot(n,eye)*n-eye
            item.update(direction=direction.tolist(),normal=n.tolist())
        evidence.append(item)
    return evidence


def light_fit(p,rows,idx):
    evidence=light_evidence(p,rows,idx);yellow=[r['direction'] for r in evidence if r['usable'] and r['color']=='yellow']
    # Yellow only; fewer than two cannot constrain cross-bead consistency.
    direction=np.mean(yellow,axis=0) if yellow else frame(p['inclination'],p['roll'])[2]
    direction/=max(np.linalg.norm(direction),1e-12)
    angles=[float(np.degrees(np.arccos(np.clip(np.dot(v,direction),-1,1)))) for v in yellow]
    return dict(direction=direction.tolist(),yellow_count=len(yellow),train_median_angle=float(np.median(angles)) if angles else None,
        evidence=evidence,constrained=len(yellow)>=2)


def fit():
    folder=LOCAL;data=read(folder/'anchors.json');anchors=data['anchors'];obs=np.array([r['measured_photo_location'] for r in anchors]);zc=obs[:,0]+1j*obs[:,1];zc-=zc.mean()
    assignments=np.array([(0,*p) for c in itertools.combinations([int(k) for k in FIT_INDICES if k],3) if connected((0,*c)) for p in itertools.permutations(c)])
    samples=[pixels(r['measured_support'])[np.linspace(0,len(pixels(r['measured_support']))-1,48).astype(int)] for r in anchors];xy=np.concatenate(samples)
    def assess(p,idx):
        owner,_,unknown=trace(p,xy);fractions=[float(np.mean(owner[i*48:(i+1)*48]==idx[i])) for i in range(4)]
        pred=project(p,centers(idx,p['hand'],p['phase'],p['pitch']));rms=float(np.sqrt(np.mean(np.sum((pred-obs)**2,axis=1))))
        penalty=max(0,axis_error(p['roll'],data['axis'])-15)/30
        return float(np.mean(fractions)-.4*(1-min(fractions))-.08*rms/(2*R*p['scale'])-.2*penalty),fractions,rms
    candidates=[]
    for hand,pitch,incl in itertools.product((-1,1),(1.12,1.20,1.45),(-35.,-17.5,0.,17.5,35.)):
        bucket=[]
        for phase in np.linspace(-np.pi,np.pi,24,endpoint=False):
            p=dict(hand=hand,pitch=pitch,inclination=incl,roll=0.,phase=float(phase),scale=1.,translation=[0.,0.])
            points=project(p,centers(FIT_INDICES,hand,phase,pitch))[assignments+21];z=points[:,:,0]+1j*points[:,:,1];zm=z.mean(1);zz=z-zm[:,None]
            a=(zz.conj()*zc).sum(1)/np.maximum((abs(zz)**2).sum(1),1e-9);scale=abs(a);err=np.mean(abs(zz*a[:,None]-zc)**2,axis=1);err[(scale<5)|(scale>13)]=1e6
            err[axis_error(np.degrees(np.angle(a)),data['axis'])>25]=1e6
            for j in np.argsort(err)[:2]:
                b=(obs[:,0]+1j*obs[:,1]).mean()-a[j]*zm[j];q={**p,'scale':float(scale[j]),'roll':float(np.degrees(np.angle(a[j]))),'translation':[float(b.real),float(b.imag)]}
                bucket.append(dict(parameters=q,assignments=assignments[j].tolist(),proxy_mse=float(err[j])))
        for r in sorted(bucket,key=lambda r:r['proxy_mse'])[:2]:
            p=r['parameters'];idx=r['assignments'];x=vec(p)
            def residual(v):
                q=par(v,p);return (project(q,centers(idx,q['hand'],q['phase'],q['pitch']))-obs).ravel()
            lower=[-100,-100,5,x[3]-20,x[4]-.4,max(-45,incl-8),pitch-.000001]
            upper=[380,320,13,x[3]+20,x[4]+.4,min(45,incl+8),pitch+.000001]
            sol=least_squares(residual,x,bounds=(lower,upper),max_nfev=45);q=par(sol.x,p)
            # A physical center is not a measured interior centroid. Preserve the
            # proxy assignment and compare exact first-hit one-to-one ownership.
            oo,_,_=trace(q,xy);matrix=np.array([[np.mean(oo[i*48:(i+1)*48]==k) for k in INDICES] for i in range(4)])
            aa,bb=linear_sum_assignment(-matrix);newidx=np.zeros(4,int);newidx[aa]=INDICES[bb]
            if assess(q,newidx)[0]>assess(q,idx)[0]:r['proxy_assignments']=idx;idx=newidx.tolist();r['assignments']=idx
            score,frac,rms=assess(q,idx);r.update(parameters=q,score=score,anchor_fractions=frac,centroid_proxy_rms=rms,
                loose_control=pitch>1.24,initial=p);candidates.append(r)
    refined=[]
    for hand in (-1,1):
        short=sorted([r for r in candidates if r['parameters']['hand']==hand and not r['loose_control']],key=lambda r:r['score'],reverse=True)[:4]
        for initial in short:
            for mode in ('support','shared-light'):
                p=deepcopy(initial['parameters']);idx=initial['assignments'];history=[]
                def objective(q):
                    sc,_,_=assess(q,idx);l=light_fit(q,anchors,idx)
                    if mode=='shared-light':sc-=.15*((l['train_median_angle']/90) if l['constrained'] else 1.)
                    return sc
                for step in (1.,.5):
                    for iteration in range(2):
                        x=vec(p);options=[p]
                        for j,delta in enumerate((2.,2.,.20,2.,.06,3.,.015)):
                            for sign in (-1,1):
                                v=x.copy();v[j]+=sign*step*delta
                                if 5<=v[2]<=13 and abs(v[5])<=45 and 1.12<=v[6]<=1.24 and axis_error(v[3],data['axis'])<=25:options.append(par(v,p))
                        p=max(options,key=objective);history.append(dict(parameters=p,objective=objective(p)))
                score,frac,rms=assess(p,idx);refined.append(dict(**{k:v for k,v in initial.items() if k not in ('parameters','score','anchor_fractions','centroid_proxy_rms')},
                    parameters=p,score=score,anchor_fractions=frac,centroid_proxy_rms=rms,mode=mode,history=history,light=light_fit(p,anchors,idx)))
        print('fit hand',hand,'completed',flush=True)
    selected=[]
    for hand,mode in itertools.product((-1,1),('support','shared-light')):
        pool=[r for r in refined if r['parameters']['hand']==hand and r['mode']==mode]
        def rank(r):return r['score']-(.15*((r['light']['train_median_angle']/90) if r['light']['constrained'] else 1.) if mode=='shared-light' else 0)
        selected.append(deepcopy(max(pool,key=rank)))
    models=[];yy,xx=np.indices(SHAPE);grid=np.c_[xx.ravel(),yy.ravel()]
    for j,r in enumerate(selected):
        p=r['parameters'];idx=r['assignments'];name=f'local-{j:02}';owner,depth,unknown=trace(p,grid);owner=owner.reshape(SHAPE)
        cert=certify(p);assert cert['certified'];pc=project(p,centers(INDICES,p['hand'],p['phase'],p['pitch']))
        predictions=[]
        for k in INDICES:
            mask=owner==k;coords=np.c_[xx[mask],yy[mask]]
            if k not in idx and mask.sum()>=50 and any(abs(k-a) in (1,6,7) for a in idx):
                predictions.append(dict(model_index=int(k),predicted_support=support(coords),physical_center=pc[k+40].tolist(),
                    relationships={a['record_id']:int(k-i) for a,i in zip(anchors,idx)},visible_pixels=int(mask.sum())))
        np.savez_compressed(folder/(name+'-prediction.npz'),owner=owner,unknown=unknown.reshape(SHAPE))
        r.update(id=name,certificate=cert,predictions=predictions,anchor_ids=[a['record_id'] for a in anchors],
                 local_count_is_not_global=True,physical_radius=R)
        models.append(r)
    save(folder/'fit-alternatives.json.gz',dict(assignments=len(assignments),candidates=candidates,refined=refined))
    save(folder/'prediction-freeze.json',dict(models=models,anchors_sha256=sha(folder/'anchors.json'),
        phase1_sha256=sha(OUT/'phase1.json.gz'),source_sha256=sha(__file__),
        inputs=['four measured supports and anchor highlights only','literal original physical construction'],
        limitation='Local labels, no recovered global index/count. Selection saw withheld locations; fitting and ranking do not.'))


def evaluate():
    folder=LOCAL;freeze=read(folder/'prediction-freeze.json');before=sha(folder/'prediction-freeze.json')
    held=read(folder/'withheld.json')['records'];anchors=read(folder/'anchors.json')['anchors'];rgb=np.load(folder/'managed-rgb.npy');features=image_features(rgb);results=[]
    for m in freeze['models']:
        p=m['parameters'];pred=m['predictions'];ks=[r['model_index'] for r in pred];hist=[];details=[]
        for r in held:
            xy=pixels(r['measured_support']);owner,_,unknown=trace(p,xy);co=Counter(owner.tolist());hist.append({int(k):co[k]/len(xy) for k in INDICES})
        cost=np.zeros((len(held),len(ks)+len(held)))+.7
        for i,h in enumerate(hist):
            for j,k in enumerate(ks):cost[i,j]=1-h[k]
        a,b=linear_sum_assignment(cost);mapping=np.full(len(held),-999);mapping[a[b<len(ks)]]=np.array(ks)[b[b<len(ks)]]
        for r,k,h in zip(held,mapping,hist):
            best=sorted(h.items(),key=lambda kv:kv[1],reverse=True);f=h.get(int(k),0);rival=max([v for j,v in h.items() if j!=k],default=0)
            details.append(dict(id=r['record_id'],assigned_model_index=int(k),containment=f,neighbor_alternative=rival,
                margin=f-rival,all_owner_fractions=h,photographic_compatibility=bool(f>=.8 and f-rival>=.2),
                identity_reliability='unresolved; overlap is not identity verification'))
        evidence=light_evidence(p,held,mapping);light=np.array(m['light']['direction'])
        for e in evidence:
            if e['usable']:e['angle']=float(np.degrees(np.arccos(np.clip(np.dot(e['direction'],light),-1,1))))
        yellow=[e['angle'] for e in evidence if e['usable'] and e['color']=='yellow']
        own=np.load(folder/(m['id']+'-prediction.npz'))['owner'];mask=np.isin(own,ks)
        unsupported=float(features['paper'][mask].mean()) if mask.any() else None
        # All pixels of anchors also assessed; fit used a bounded deterministic sample.
        full=[]
        for r,k in zip(anchors,m['assignments']):
            o,_,u=trace(p,pixels(r['measured_support']));full.append(float(np.mean(o==k)))
        results.append(dict(model=m['id'],hand=p['hand'],mode=m['mode'],withheld=details,
            mean_withheld_containment=float(np.mean([r['containment'] for r in details])),
            compatible=sum(r['photographic_compatibility'] for r in details),withheld_count=len(details),
            anchor_full_containment=full,light=evidence,yellow_heldout_count=len(yellow),
            all_anchors_supported80=bool(min(full)>=.8),all_withheld_supported80=bool(all(r['photographic_compatibility'] for r in details)),
            yellow_median_angle=float(np.median(yellow)) if yellow else None,
            predicted_material_on_photographic_paper=unsupported,
            packing=dict(pitch=p['pitch'],certificate_min_gap=m['certificate']['minimum_gap_units'],
                relative_to_R282_pitch_1_35=p['pitch']/1.35,
                caveat='Tighter pitch and separation are constraints, not a measured packing match.'),
            accepted_identity=False))
    assert sha(folder/'prediction-freeze.json')==before
    save(folder/'evaluation.json',dict(results=results,prediction_freeze_sha256=before,
        claim='Withheld support and common-light compatibility only. No independent real physical identity truth.'))
    print([(r['model'],r['compatible'],r['mean_withheld_containment'],r['yellow_median_angle']) for r in results],flush=True)

from collections import Counter
if __name__=='__main__':
    import sys
    {'select':select,'fit':fit,'evaluate':evaluate}[sys.argv[1]]()
