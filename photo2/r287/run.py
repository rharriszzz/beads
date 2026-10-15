"""Same-cue controls, conditional stability and independent photographic selector."""
import argparse
from scipy.spatial import cKDTree
from photo2.r282.phase1 import image_features
from photo2.r284b.methods import contour,metrics
from photo2.r284b.run import centerline
from photo2.r285.run import old_control,local_mask
from photo2.r285.select import bank
from .common import *
from .candidates import produce,PERTURBATIONS
from .evidence import measure
from .selector import decide,PARAMETERS

def main(stage='development',out=OUT):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if stage=='confirmation':
        freeze=read(OUT/'freeze.json')
        for name,h in freeze['source_hashes'].items():assert sha(Path(__file__).parent/name)==h,name
        assert sha(OUT/'selection.json')==freeze['selection_sha256']
    native,rgb,photometa=photo();f=image_features(rgb);saved={o['id']:o for o in bank()};rows=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];rt=cKDTree([r['seed'] for r in rows]);curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);ct=cKDTree(curve);tan=np.roll(curve,-1,axis=0)-np.roll(curve,1,axis=0);tan/=np.maximum(np.linalg.norm(tan,axis=1)[:,None],1e-9);normal=np.c_[-tan[:,1],tan[:,0]];arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]
    cases=development() if stage=='development' else read(OUT/'selection.json')['confirmation'];results=[];replayed=0
    for case in cases:
        obs=[]
        for o in case['observations']:
            x,y=o['seed'];origin=np.array([x,y])-48;sl=np.s_[y-48:y+49,x-48:x+49];lum,hs,paper=f['lum'][sl],f['hsv'][sl],f['paper'][sl]
            initial_region=saved[o['id']]['initial_support'] if o['id'] in saved else old_control(f,o['seed'],o['color'])['A']['measured_support'];initial=local_mask(initial_region,origin,(97,97));args=(lum,hs,paper,f['palette'],f['background_hue'],o['color'],initial);base=produce(*args);pert={m:[] for m in base};stability={}
            if 'variants' in o:
                for m,(mask,info) in base.items():np.testing.assert_array_equal(mask,local_mask(o['variants'][m]['measured_support'],origin,(97,97)));replayed+=1
            for spec in PERTURBATIONS:
                alt=produce(*args,**{k:v for k,v in spec.items() if k!='name'})
                for m,(mask,info) in alt.items():
                    original=base[m][0];a=np.argwhere(original);b=np.argwhere(mask);yy,xx=np.where(mask);pert[m].append(dict(name=spec['name'],iou=float((original&mask).sum()/max(1,(original|mask).sum())),centroid_shift=float(np.linalg.norm(a.mean(0)-b.mean(0))) if len(a) and len(b) else 99.,support=support(np.c_[xx,yy]+origin),area=int(mask.sum())))
            for m in base:
                pp=pert[m];stability[m]=dict(minimum_iou=min(q['iou'] for q in pp),mean_iou=float(np.mean([q['iou'] for q in pp])),maximum_centroid_shift=max(q['centroid_shift'] for q in pp),domain_minimum_iou=min(q['iou'] for q in pp if q['name'].startswith('domain')),window_contact=base[m][1].get('window_contact',0),by_family={family:dict(minimum_iou=min(q['iou'] for q in pp if q['name'].startswith(family)),maximum_centroid_shift=max(q['centroid_shift'] for q in pp if q['name'].startswith(family))) for family in ('gain','contrast','sigma','background','seed','domain')})
            evidence=measure(lum,hs,paper,f['palette'],f['background_hue'],o['color'],{m:v[0] for m,v in base.items()},stability);decision=decide(evidence);_,ix=rt.query(o['seed']);scale=rows[ix]['centerline']['local_support_scale'];variants={}
            for m,(mask,info) in base.items():
                yy,xx=np.where(mask);c=contour(mask);r=record(o['id']+':R287:'+m,'phase1');r.update(seed=o['seed'],color=o['color'],color_reliability_kind='unrated photographic assignment',photographic_reliability=dict(classification='unrated',calibrated_probability=None),measured_support=support(np.c_[xx,yy]+origin),measured_photo_location=(np.c_[xx,yy].mean(0)+origin).tolist() if len(xx) else None,subpixel_contour=(c+origin).tolist(),support_type='colored photographic interior',physical_body_center=None,physical_body_centerline_crossing=None,method=m,method_evidence=info,metrics=metrics(mask,c,lum,base['J'][0],[48,48]),perturbations=pert[m],status='experimental-unresolved',evidence_links=['beads-photo-2.jpg','photo2/r287/results/selection.json'])
                if r['measured_support']:r['measured_support']['kind']='colored photographic interior'
                r['centerline']=centerline(r['measured_support'],o['seed'],curve,ct,normal,arc,scale);validate(r);variants[m]=r
            selected=record(o['id']+':R287:selector','phase1');selected.update(color=o['color'],seed=o['seed'],status=decision['decision'],selection=decision,photographic_reliability=dict(classification='unrated',calibrated_probability=None),physical_body_center=None,physical_body_centerline_crossing=None,support_type='colored photographic interior',source_observations=[variants[m]['record_id'] for m in ('J','M')],alternative_records=[variants[m]['record_id'] for m in decision['alternatives']],evidence_links=['photo2/r287/results/'+stage+'.json.gz'],notes=['Both retains separate alternatives; no union, intersection or physical identity is manufactured.'])
            if len(decision['alternatives'])==1:
                chosen=variants[decision['alternatives'][0]];selected.update(measured_support=chosen['measured_support'],measured_photo_location=chosen['measured_photo_location'],centerline=chosen['centerline'])
            validate(selected);obs.append(dict(id=o['id'],seed=o['seed'],color=o['color'],source_status=o['source_status'],origin=origin.tolist(),initial_support=initial_region,native_Y=lum.tolist(),variants=variants,evidence=evidence,selector=selected))
        results.append(dict(name=case['name'],seed=case['seed'],stratum=case['stratum'],observations=obs));print(stage,case['name'],len(obs),flush=True)
    save(out/(stage+'.json.gz'),dict(cases=results,photograph=photometa,parameters=PARAMETERS,perturbations=PERTURBATIONS,baseline_masks_replayed=replayed,conditional_stability='Hold HSV/paper/palette/initial photographic A fixed; modify native Y and algorithm field/background/seed/domain. Seed offsets retain original A ring. Not physical relighting or new color calibration.',source_hashes={name:sha(Path(__file__).parent/name) for name in ('candidates.py','evidence.py','selector.py')}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',default='development',choices=['development','confirmation']);p.add_argument('--output',type=Path,default=OUT);a=p.parse_args();main(a.stage,a.output)
