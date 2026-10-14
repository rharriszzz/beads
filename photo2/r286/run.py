"""Same-cue native comparison; candidate freeze required for independent confirmation."""
import argparse
import numpy as np
from scipy.spatial import cKDTree
from photo2.r282.phase1 import image_features
from photo2.r284b.methods import metrics,contour
from photo2.r284b.run import centerline
from photo2.r285.run import local_mask,old_control
from photo2.r285.methods import measurements,basins
from .methods import infer,PARAMETERS
from .common import *

def controls(f,seed,color):
    old=old_control(f,seed,color);x,y=seed;origin=np.array(seed)-48;sl=np.s_[y-48:y+49,x-48:x+49];sm,pg,dm,rs,meta=measurements(f['lum'][sl],f['hsv'][sl],f['paper'][sl],f['palette'],f['background_hue'],color)
    if rs is None:mask=np.zeros_like(dm)
    else:mask,labels,group,refs,edges,markers=basins(sm,pg,dm,rs);meta.update(saddles=edges,merged_marker_ids=group)
    yy,xx=np.where(mask);old['S']=dict(measured_support=support(np.c_[xx,yy]+origin),subpixel_contour=(contour(mask)+origin).tolist(),method_evidence=meta);return old

def main(stage='development',out=OUT,cases_override=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);native,rgb,photo_meta=photo();f=image_features(rgb);old=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];bt=cKDTree([r['seed'] for r in old]);curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);tree=cKDTree(curve);tan=np.roll(curve,-1,axis=0)-np.roll(curve,1,axis=0);tan/=np.maximum(np.linalg.norm(tan,axis=1)[:,None],1e-9);normal=np.c_[-tan[:,1],tan[:,0]];arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]
    if stage=='development':cases=[dict(name=q['name'],seed=q['observation']['seed'],stratum='reviewed-development',observations=[dict(id=q['observation']['id'],seed=q['observation']['seed'],color=q['observation']['color'],source_status=q['observation']['source_status'],controls=q['observation']['variants'])]) for q in reviewed()]
    else:
        freeze=read(OUT/'candidate-freeze.json');assert freeze['method_sha256']==sha(Path(__file__).parent/'methods.py');assert freeze['selection_sha256']==sha(OUT/'selection.json');cases=read(OUT/'selection.json')['confirmation']
    if cases_override is not None:cases=cases_override
    results=[]
    for case in cases:
        obs=[]
        for o in case['observations']:
            x,y=o['seed'];origin=np.array([x,y])-48;sl=np.s_[y-48:y+49,x-48:x+49];lum=f['lum'][sl];hsv=f['hsv'][sl];paper=f['paper'][sl];oldmethods=o.get('controls') or controls(f,o['seed'],o['color']);initial=local_mask(oldmethods['S']['measured_support'],origin,(97,97));result=infer(lum,hsv,paper,f['palette'],f['background_hue'],o['color']);small=infer(lum[16:-16,16:-16],hsv[16:-16,16:-16],paper[16:-16,16:-16],f['palette'],f['background_hue'],o['color'])
            yy,xx=np.indices(lum.shape);illum=[]
            for gain in (.8,1.2):illum.append(infer(lum*gain,hsv,paper,f['palette'],f['background_hue'],o['color']))
            ramp=.8+.4*xx/96;illum.append(infer(lum*ramp,hsv,paper,f['palette'],f['background_hue'],o['color']))
            _,bi=bt.query(o['seed']);scale=old[bi]['centerline']['local_support_scale'];variants={}
            for method in ('J','S','M','A','B','C'):
                if method in ('J','S'):
                    mask=local_mask(oldmethods[method]['measured_support'],origin,(97,97));info=dict(oldmethods[method].get('method_evidence',{}),control='Unchanged historical method; not truth');barrier=np.zeros_like(mask)
                else:
                    mask,info,barrier=result[method];padded=np.pad(small[method][0],16);iou=float((mask&padded).sum()/max(1,(mask|padded).sum()));perturb=[]
                    for k,alt in enumerate(illum):
                        pm=alt[method][0];a=np.argwhere(mask);b=np.argwhere(pm);perturb.append(dict(kind=['gain0.8','gain1.2','horizontal0.8to1.2'][k],iou=float((mask&pm).sum()/max(1,(mask|pm).sum())),centroid_shift=float(np.linalg.norm(a.mean(0)-b.mean(0))) if len(a) and len(b) else None))
                    info.update(domain32_area=int(small[method][0].sum()),domain_iou=iou,domain_sensitive=iou<.95,illumination_perturbations=perturb,illumination_sensitive=any(q['iou']<.8 for q in perturb))
                c=contour(mask);met=metrics(mask,c,lum,initial,[48,48]);py,px=np.where(mask);by,bx=np.where(barrier);flags=[]
                if not mask.any():flags.append('empty support')
                if mask.sum()>870:flags.append('area ceiling')
                if info.get('domain_sensitive'):flags.append('domain unstable')
                if info.get('window_contact_pixels'):flags.append('window contact')
                if info.get('illumination_sensitive'):flags.append('illumination sensitive')
                r=record(o['id']+':'+method,'phase1');r.update(seed=o['seed'],color=o['color'],method=method,measured_support=support(np.c_[px,py]+origin),measured_photo_location=(np.array(met['centroid'])+origin).tolist() if met['centroid'] else None,subpixel_contour=(c+origin).tolist(),barrier_pixels=support(np.c_[bx,by]+origin),metrics=met,method_evidence=info,status='diagnostic-abstention' if flags else 'reviewable-unrated',abstention_reasons=flags,photographic_reliability=dict(classification='unrated',calibrated_probability=None),color_reliability_kind='unrated image-only assignment',physical_body_center=None,physical_body_centerline_crossing=None,support_type='colored photographic interior',evidence_links=['beads-photo-2.jpg','photo2/r286/results/selection.json'])
                if r['measured_support']:r['measured_support']['kind']='colored photographic interior'
                r['centerline']=centerline(r['measured_support'],o['seed'],curve,tree,normal,arc,scale);validate(r);variants[method]=r
            obs.append(dict(id=o['id'],seed=o['seed'],color=o['color'],source_status=o['source_status'],origin=origin.tolist(),native_Y=lum.tolist(),variants=variants))
        results.append(dict(name=case['name'],seed=case['seed'],stratum=case['stratum'],observations=obs));print(stage,case['name'],len(obs),flush=True)
    save(out/(stage+'.json.gz'),dict(cases=results,parameters=PARAMETERS,photo=photo_meta,method_sha256=sha(Path(__file__).parent/'methods.py')))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['development','confirmation'],default='development');p.add_argument('--output',type=Path,default=OUT);a=p.parse_args();main(a.stage,a.output)
