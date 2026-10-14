"""Bounded development/confirmation runner. No production or later-phase writes."""
import argparse,copy
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r282.common import ROOT,read,save,photo,pixels,support,record,validate,sha
from photo2.r282.phase1 import image_features,attempts
from photo2.r284.methods import prune,color_domain
from photo2.r284b.methods import colored as old_colored,metrics,contour
from photo2.r284b.run import centerline
from .select import OUT,OLD,bank
from .methods import infer,PARAMETERS

def local_mask(region,origin,shape):
    p=pixels(region)-origin;m=np.zeros(shape,bool);p=p[np.all((p>=0)&(p<np.array(shape)[::-1]),axis=1)]
    if len(p):m[p[:,1],p[:,0]]=True
    return m

def old_control(f,seed,color):
    from photo2.r282.common import circular_distance
    x,y=seed;origin=np.array(seed)-24
    alternative=next(a for a in attempts(f,seed) if a['method']=='C')
    initial=prune(local_mask(alternative['region'],origin,(49,49)),[24,24]);domain,data=color_domain(f,dict(xy=seed,color=color));_,hs,lum,paper,dist,peak=data
    own=circular_distance(hs[:,:,0]*360,f['palette'][color]);other=next(v for k,v in f['palette'].items() if k!=color);rival=circular_distance(hs[:,:,0]*360,other)
    wide=domain|((hs[:,:,1]>.27)&(own<24)&(rival-own>2)&(lum>max(.012,.09*peak))&~paper&(dist<=24))
    masks={'A':initial,'J':old_colored(lum,wide,initial,variant='J')[0]};out={}
    for m,mask in masks.items():
        yy,xx=np.where(mask);out[m]=dict(measured_support=support(np.c_[xx,yy]+origin),subpixel_contour=(contour(mask)+origin).tolist())
    return out

def main(stage='development',out=OUT):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);selection=read(OUT/'selection.json');_,rgb,photo_meta=photo();f=image_features(rgb);sources=bank();baseline=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];bt=cKDTree([r['seed'] for r in baseline])
    curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);tree=cKDTree(curve);tan=np.roll(curve,-1,axis=0)-np.roll(curve,1,axis=0);tan/=np.maximum(np.linalg.norm(tan,axis=1)[:,None],1e-9);normal=np.c_[-tan[:,1],tan[:,0]];arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]
    if stage=='development':entries=[dict(id=o['id'],seed=o['seed'],color=o['color'],controls=o['variants'],source_status=o['source_status']) for o in sources if o['color']!='black']
    else:
        freeze=read(OUT/'candidate-freeze.json');assert sha(Path(__file__).parent/'methods.py')==freeze['methods_sha256'],'Methods changed after freeze'
        entries=[dict(id=o['id'],seed=o['seed'],color=o['color'],controls=old_control(f,o['seed'],o['color']),source_status=o['source_status']) for o in selection['confirmation'] if o['color']!='black']
    result=[]
    for i,o in enumerate(entries):
        seed=np.array(o['seed']);x,y=seed;origin=seed-48;sl=np.s_[y-48:y+49,x-48:x+49];lum=f['lum'][sl];hs=f['hsv'][sl];paper=f['paper'][sl]
        initial=local_mask(o['controls']['A']['measured_support'],origin,lum.shape)
        all48=infer(lum,hs,paper,f['palette'],f['background_hue'],o['color'])
        all32=infer(lum[16:-16,16:-16],hs[16:-16,16:-16],paper[16:-16,16:-16],f['palette'],f['background_hue'],o['color'])
        _,ix=bt.query(seed);scale=baseline[ix]['centerline']['local_support_scale'];variants={}
        for m in ('A','J','D','S','G'):
            if m in ('A','J'):
                mask=local_mask(o['controls'][m]['measured_support'],origin,lum.shape);info=dict(control='Unchanged previous method; not truth');c=np.array(o['controls'][m]['subpixel_contour']).reshape(-1,2)-origin
            else:
                mask,info=all48[m];small=all32[m][0];padded=np.pad(small,16);iou=float((mask&padded).sum()/max(1,(mask|padded).sum()))
                info.update(domain32_area=int(small.sum()),domain48_area=int(mask.sum()),domain_iou=iou,domain_sensitive=iou<.95,
                    domain32_contact=all32[m][1].get('window_contact_pixels',0));c=contour(mask)
            met=metrics(mask,c,lum,initial,[48,48]);yy,xx=np.where(mask);r=record(o['id']+':'+m,'phase1')
            r.update(seed=seed.tolist(),color=o['color'],color_reliability=0.,color_reliability_kind='unrated photographic assignment',
                measured_support=support(np.c_[xx,yy]+origin),measured_photo_location=(np.array(met['centroid'])+origin).tolist() if met['centroid'] else None,
                method=m,method_evidence=info,metrics=met,subpixel_contour=(c+origin).tolist(),
                status='rejected-area-cap' if mask.sum()>870 else 'experimental-unresolved',
                photographic_reliability=dict(classification='unrated',calibrated_probability=None),
                physical_body_center=None,physical_body_centerline_crossing=None,support_type='colored photographic interior',
                evidence_links=['beads-photo-2.jpg','photo2/r285/results/selection.json'],
                notes=['Native photographic proposal; no verified distinct-body ownership.','No production adoption.'])
            if r['measured_support']:r['measured_support']['kind']='colored photographic interior'
            r['centerline']=centerline(r['measured_support'],seed,curve,tree,normal,arc,scale);validate(r);variants[m]=r
        result.append(dict(id=o['id'],seed=seed.tolist(),color=o['color'],source_status=o['source_status'],origin=origin.tolist(),native_Y=lum.tolist(),variants=variants))
        if i%25==0:print(stage,i+1,'/',len(entries),flush=True)
    pairs=[]
    for i,a in enumerate(result):
        for b in result[i+1:]:
            if np.linalg.norm(np.array(a['seed'])-b['seed'])>96:continue
            for m in ('A','J','D','S','G'):
                shared=len(set(map(tuple,pixels(a['variants'][m]['measured_support'])))&set(map(tuple,pixels(b['variants'][m]['measured_support']))))
                if shared:pairs.append(dict(ids=[a['id'],b['id']],method=m,shared_pixels=shared,kind='photographic-owner-conflict; not verified leakage'))
    save(out/(stage+'.json.gz'),dict(observations=result,pairs=pairs,stage=stage,parameters=PARAMETERS,photo=photo_meta))
    save(out/(stage+'-summary.json'),summarize(result,pairs));print(stage,'complete',len(result),flush=True)

def summarize(observations,pairs):
    out={}
    for m in ('A','J','D','S','G'):
        rr=[o['variants'][m] for o in observations];valid=[r for r in rr if 0<r['metrics']['area']<=870]
        out[m]=dict(candidates=len(rr),nonempty=sum(r['metrics']['area']>0 for r in rr),within_cap=len(valid),
            near=sum(r['centerline']['near'] for r in valid),crossing=sum(r['centerline']['crosses'] for r in valid),
            overlap_pairs=sum(p['method']==m for p in pairs),domain_sensitive=sum(r['method_evidence'].get('domain_sensitive',False) for r in rr),
            window_contact=sum(r['method_evidence'].get('window_contact_pixels',0)>0 for r in rr),
            mean_shift=float(np.mean([r['metrics']['centroid_shift'] for r in rr if r['metrics']['centroid_shift'] is not None])),
            real_bead_precision=None,real_recall=None,verified_leakage=None,verified_false_splits=None)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['development','confirmation'],default='development');p.add_argument('--output',type=Path,default=OUT);a=p.parse_args();main(a.stage,a.output)
