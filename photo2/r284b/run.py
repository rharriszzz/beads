"""Bounded comparison runner. Production R283/R284A remain immutable inputs."""
from pathlib import Path
import argparse, copy
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r282.common import ROOT,photo,read,save,sha,pixels,support,record,validate,circular_distance
from photo2.r282.phase1 import image_features
from photo2.r284.methods import cut_features,cues,infer,color_domain
from photo2.r284.run import shift_rows,in_case
from .methods import PARAMETERS,COLOR_METHODS,BLACK_METHODS,colored,reflection,metrics,contour
OUT=ROOT/'photo2/r284b/results'
OLD=ROOT/'photo2/r284/results'

def mask_of(region,origin):
    m=np.zeros((49,49),bool);p=pixels(region)-origin
    p=p[np.all((p>=0)&(p<49),axis=1)]
    if len(p):m[p[:,1],p[:,0]]=True
    return m

def choose_cases(baseline):
    cases=copy.deepcopy(read(OLD/'cases.json'))
    def separated(p):return all(np.linalg.norm(np.array(p)-c['center'])>180 for c in cases)
    pool=[r for r in baseline if r['color']=='black' and r['measured_support'] and separated(r['seed']) and r['centerline']['near']]
    # Select weak but nonempty photographic evidence, not physical-body truth.
    r=min(pool,key=lambda r:(r['illumination']['peak'],r['record_id']))
    cases.append(dict(name='auto-weak',center=r['seed'],origin=(np.array(r['seed'])-64).tolist(),size=128,
        selection_ids=[r['record_id']],selection_rule='Lowest stored native illumination.peak, stable ID tie break; nonempty black near observation, >180px from prior cases. Native weakness verified separately.'))
    pairs=[]
    for i,a in enumerate(baseline):
        if a['color'] not in ('red','yellow') or not a['measured_support']:continue
        for b in baseline[i+1:]:
            if b['color']!=a['color'] or not b['measured_support']:continue
            d=np.linalg.norm(np.array(a['seed'])-b['seed']);p=(np.array(a['seed'])+b['seed'])/2
            if 14<=d<=30 and separated(p):pairs.append((d,a['record_id'],b['record_id'],p))
    d,a,b,p=min(pairs,key=lambda v:v[:3]);cases.append(dict(name='auto-same-color',center=p.tolist(),origin=np.rint(p-64).astype(int).tolist(),size=128,
        selection_ids=[a,b],selection_rule='Closest pair of nonempty same-pigment cues at 14..30px, >180px from all earlier crops; stable ID tie breaks. Distinctness unverified.'))
    return cases

def centerline(region,seed,curve,tree,normals,arc,scale):
    p=pixels(region);_,j=tree.query(seed)
    out=dict(station=int(j),arc_px=float(arc[j]),local_support_scale=scale,near=False,crosses=False,side='no-support',signed_extent=None,unsigned_support_distance=None)
    if len(p):
        dist,ix=tree.query(p);signed=((p-curve[ix])*normals[ix]).sum(1);cross=bool(signed.min()<=0<=signed.max() and dist.min()<=1)
        out.update(near=bool(dist.min()<=scale/2),crosses=cross,side='crossing' if cross else 'positive' if np.median(signed)>=0 else 'negative',
            signed_extent=[float(signed.min()),float(signed.max())],unsigned_support_distance=float(dist.min()),
            arc_interval=[float(arc[ix].min()),float(arc[ix].max())])
    out['interpretation']='Measured-support geometry only; absence of crossing does not establish full-body absence.'
    return out

def main(out=OUT):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    native,rgb,photo_meta=photo();f=image_features(rgb);baseline=read(ROOT/'photo2/r283/results/phase1.json.gz')['records']
    bt=cKDTree([r['seed'] for r in baseline]);cases=choose_cases(baseline);save(out/'cases.json',cases)
    curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);tree=cKDTree(curve)
    tangent=np.roll(curve,-1,axis=0)-np.roll(curve,1,axis=0);tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-9)
    normal=np.c_[-tangent[:,1],tangent[:,0]];arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]
    summaries=[]
    for case in cases:
        name=case['name']
        if (OLD/(name+'.json.gz')).exists():
            old=read(OLD/(name+'.json.gz'));rows=old['methods']['A']['records']
        else:
            origin=np.array(case['origin'])-48;tile=cut_features(f,origin,[224,224])
            inherited=shift_rows([r for r in baseline if np.all(np.array(r['seed'])>=origin+24) and np.all(np.array(r['seed'])<origin+200)],-origin)
            bank,ledger=cues(tile,inherited);rr,_=infer(tile,bank,'A');rows=[r for r in shift_rows(rr,origin) if in_case(r,case)]
            save(out/(name+'-cues.json'),dict(origin=origin.tolist(),bank=bank,ledger=ledger))
        observations=[]
        for source in rows:
            if source['color'] not in ('red','yellow','black') or not source['measured_support']:continue
            seed=np.array(source['seed'],int);origin=seed-24;x,y=seed;lum=f['lum'][y-24:y+25,x-24:x+25];hs=f['hsv'][y-24:y+25,x-24:x+25]
            initial=mask_of(source['measured_support'],origin);isblack=source['color']=='black'
            if not isblack:
                domain,localdata=color_domain(f,dict(xy=seed,color=source['color']))
                _,_,_,paper,dist,peak=localdata
                own=circular_distance(hs[:,:,0]*360,f['palette'][source['color']])
                other=next(v for k,v in f['palette'].items() if k!=source['color'])
                rival=circular_distance(hs[:,:,0]*360,other)
                # Explicit radius ablation, not a seventh independent algorithm.
                wide_domain=domain|((hs[:,:,1]>.27)&(own<24)&(rival-own>2)&(lum>max(.012,.09*peak))&~paper&(dist<=24))
            else:domain=((hs[:,:,1]<.65)|(hs[:,:,1]*hs[:,:,2]<.12))&~f['paper'][y-24:y+25,x-24:x+25]
            _,bi=bt.query(seed);prior=baseline[bi];scale=prior['centerline']['local_support_scale']
            ob=dict(id=f'{name}:{source["record_id"]}',source_id=source['record_id'],seed=seed.tolist(),origin=origin.tolist(),color=source['color'],
                native_Y=lum.tolist(),initial_support=source['measured_support'],source_status=source['status'],variants={})
            for method in BLACK_METHODS if isblack else COLOR_METHODS:
                if method=='R283':
                    candidates=[r for r in baseline if r['color']==source['color'] and np.linalg.norm(np.array(r['seed'])-seed)<=6]
                    if not candidates:continue
                    oldr=min(candidates,key=lambda r:np.linalg.norm(np.array(r['seed'])-seed));m=mask_of(oldr['measured_support'],origin);c=contour(m);meta=dict(source_record=oldr['record_id'],historical_collar=True)
                elif isblack and method=='A':m=initial;c=contour(m);meta=dict(historical_collar=True)
                elif isblack:
                    m,c,meta=reflection(lum,domain,initial,variant=method)
                    perturb=[]
                    for sigma,delta in ((.50,-.02),(.80,.02)):
                        pm,pc,_=reflection(lum,domain,initial,variant=method,sigma=sigma,level_delta=delta)
                        perturb.append(dict(sigma=sigma,level_delta=delta,area=int(pm.sum()),
                            contour_mean_distance=float(cKDTree(c).query(pc)[0].mean()) if len(c) and len(pc) else None,
                            mask_iou=float((m&pm).sum()/max(1,(m|pm).sum()))))
                    meta['perturbations']=perturb
                else:m,c,meta=colored(lum,wide_domain if method=='J' else domain,initial,variant=method)
                meta['area_cap_exceeded']=bool(m.sum()>870)
                met=metrics(m,c,lum,initial,[24,24]);r=record(ob['id']+':'+method,'phase1');yy,xx=np.where(m)
                r.update(seed=seed.tolist(),color=source['color'],color_reliability=0.,color_reliability_kind='unrated inherited image-only color assignment; not probability',measured_support=support(np.c_[xx,yy]+origin),
                    measured_photo_location=(np.array(met['centroid'])+origin).tolist() if met['centroid'] else None,
                    status='rejected-area-cap' if meta['area_cap_exceeded'] else 'experimental-unresolved',phase1_reliability=0.,reliability_kind='not calibrated; all alternatives pending photographic review',
                    metrics=met,method=method,method_evidence=meta,subpixel_contour=(c+origin).tolist(),
                    support_type='specular-reflection region' if isblack else 'colored photographic interior',
                    peak_location=(np.array(meta['peak'])+origin).tolist() if 'peak' in meta else None,
                    physical_body_center=None,physical_body_centerline_crossing=None,
                    evidence_links=['beads-photo-2.jpg','photo2/r284/results/'+name+'.json.gz'] if (OLD/(name+'.json.gz')).exists() else ['beads-photo-2.jpg','photo2/r284b/results/'+name+'-cues.json'],
                    notes=['High importance; feature ownership and physical identity unresolved.','Historical dark-collar baseline; not compliant with new reflection contract.'] if meta.get('historical_collar') else ['High importance; feature ownership and physical identity unresolved.'])
                if r['measured_support']:r['measured_support']['kind']=r['support_type'] if not meta.get('historical_collar') else 'historical support; may include dark collar'
                r['centerline']=centerline(r['measured_support'],seed,curve,tree,normal,arc,scale)
                r['centerline']['measured_feature']='reflection' if isblack else 'colored interior'
                validate(r);ob['variants'][method]=r
            observations.append(ob)
        # Pair evidence is photographic only. No secondary feature is deleted.
        pairs=[]
        for i,a in enumerate(observations):
            for b in observations[i+1:]:
                d=float(np.linalg.norm(np.array(a['seed'])-b['seed']))
                if d>40:continue
                for method in sorted(set(a['variants'])&set(b['variants'])):
                    ra=a['variants'][method];rb=b['variants'][method];pa=set(map(tuple,pixels(ra['measured_support'])));pb=set(map(tuple,pixels(rb['measured_support'])))
                    overlap=len(pa&pb)
                    if overlap:pairs.append(dict(ids=[a['id'],b['id']],method=method,kind='overlap-owner-unresolved',shared_pixels=overlap))
                if a['color']==b['color']=='black' and d<=18:
                    pairs.append(dict(ids=[a['id'],b['id']],method='all',kind='multiple-reflections; possible secondary, physical ownership unresolved',distance=d))
        pairs.sort(key=lambda p:(p['ids'],p['method'],p['kind']))
        result=dict(case=case,observations=observations,pairs=pairs)
        save(out/(name+'.json.gz'),result)
        summaries.append(dict(case=name,observations=len(observations),by_method={method:aggregate([o['variants'][method] for o in observations if method in o['variants']]) for method in (*COLOR_METHODS,'R283','R1','R2','R3','R4')}))
        print(name,len(observations),flush=True)
    save(out/'summary.json',summaries)
    inputs=[ROOT/'beads-photo-2.jpg',ROOT/'photo2/r283/results/phase1.json.gz',ROOT/'photo2/r282/results/centerline.json',OLD/'cases.json']
    save(out/'freeze.json',dict(parameters=PARAMETERS,photo=photo_meta,input_hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs},
        source_hashes={str(p.relative_to(ROOT)):sha(p) for p in Path(__file__).parent.glob('*.py')},
        exclusion='No Phase2/3 input; no new production inventory. Seeds fixed across methods. Real recall and distinct-body precision unknown.'))

def aggregate(rows):
    nonempty=[r for r in rows if r['measured_support']]
    return dict(observations=len(rows),nonempty=len(nonempty),near=sum(r['centerline']['near'] for r in nonempty),
        measured_crossing=sum(r['centerline']['crosses'] for r in nonempty),
        mean_retained=float(np.mean([r['metrics']['retained_fraction'] for r in rows])) if rows else None,
        mean_shift=float(np.mean([r['metrics']['centroid_shift'] for r in nonempty])) if nonempty else None,
        mean_boundary_gradient=float(np.mean([r['metrics']['boundary_gradient'] for r in nonempty])) if nonempty else None,
        real_distinct_beads=None,real_leakage_count=None,real_false_partition_count=None,calibrated_high_confidence=None)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=OUT);main(p.parse_args().output)
