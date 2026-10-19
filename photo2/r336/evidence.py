"""Correct the dark-pixel -> visible-body inference, preserving the old sampler.

Dark pixels are a photometric response, not an independently established bead.
Sampling at predictions and moving to response centroids cannot create ownership.
No proposal can propagate from this evidence alone. Historical R332 is immutable.
"""
import argparse,time
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from .common import *
SUSPECTS=['R332-B-0196-0183','R332-B-0138-0130']
def native_response(photo,query_xy,color='black'):
    """Literal R332 threshold/component reproduction, with truthful evidence type."""
    x,y=np.rint(query_xy).astype(int);x0=max(0,x-12);y0=max(0,y-12);x1=min(photo.shape[1],x+13);y1=min(photo.shape[0],y+13)
    rgb=photo[y0:y1,x0:x1].astype(np.float32)/255.;r,g,b=rgb.transpose(2,0,1);v=rgb.max(2)
    mask=(v<.36)&(v-rgb.min(2)<.13)&(v>.012) if color=='black' else (r>1.8*g)&(r>2.5*b)&(r>.16) if color=='red' else (g>.35*r)&(g>1.8*b)&(r>.9*g)&(r>.16)
    yy,xx=np.mgrid[y0:y1,x0:x1];disk=(xx-x)**2+(yy-y)**2<=144;labels,n=ndi.label(mask&disk,np.ones((3,3)));sizes=np.bincount(labels.ravel());sizes[0]=0
    points=np.c_[xx[labels==sizes.argmax()],yy[labels==sizes.argmax()]] if n else np.empty((0,2),int)
    return dict(query_xy=query_xy,rounded_query=[int(x),int(y)],pixels_xy=points,pixel_count=len(points),centroid=points.mean(0) if len(points) else None,
                evidence_kind='native threshold response; glass ownership unestablished',visible_body_established=False,can_create_bead=False)

def can_admit_identity(response,independent_identity=None):
    # A darkness mask, highlight, lattice prediction, centroid, classifier or
    # repeated motif cannot serve as its own independent identity witness.
    return bool(independent_identity and independent_identity.get('authority')=='maker visible-body review' and independent_identity.get('separate_body') is True)

def local_scale(g,xy,radius=135):
    obs={r['id']:r for r in g['observations']};families={k:[] for k in ['F0','F1','difference']};ids=[]
    for e in g['edges']:
        a,b=np.array(obs[e['source']]['xy']),np.array(obs[e['target']]['xy'])
        if np.linalg.norm((a+b)/2-xy)<radius:
            families[e['family']].append(float(np.linalg.norm(a-b)));ids.append([e['source'],e['target']])
    return dict(median_primitive_support_spacings={k:float(np.median(v)) if v else None for k,v in families.items()},reference_links=ids,
                interpretation='Same local metric for every color. Support spacings are not measured bead centers or exact outside diameters; combine with actual body boundaries and maker review.')

def run(out):
    t=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=False);raw=read(ROOT/'photo2/r332/results/graph.json.gz');g=read(ROOT/'photo2/r335/results/graph.json.gz');obs={r['id']:r for r in g['observations']}
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');photo=np.asarray(image);provisional={r['id']:r for r in raw['provisional_observations']};cases=[]
    for oid in SUSPECTS:
        r=provisional[oid];initial=native_response(photo,r['initial_prediction']);final=native_response(photo,r['xy']);assert final['pixels_xy'].tolist()==r['native']['pixels_xy'];assert np.allclose(initial['centroid'],r['xy'])
        nearest=sorted((float(np.linalg.norm(np.array(o['xy'])-r['xy'])),o['id']) for o in g['observations'])[:4]
        cases.append(dict(id=oid,recorded_support=r['xy'],predicted_site=r['prediction'],initial_prediction=r['initial_prediction'],cell=r['cell'],initial=initial,resampled=final,
                          nearest=nearest,local_geometry=local_scale(g,np.array(r['xy'])),pixel_coordinates_correct=True,classification='rejected visible body; maker sees no separate glass',
                          cause='Prediction-seeded threshold component -> centroid relocation -> resampling a larger dark component; nearby glass/shadow and filled foreground were not separated from target-body ownership.'))
    # Same defect audit across every retained R332 native candidate/addition.
    scan=[]
    for group,key in [('working-addition','accepted_additions'),('provisional','provisional_observations'),('unassociated','unrepresented_candidates')]:
        for r in raw[key]:
            if not r.get('native'):continue
            pp=np.array(r['native']['pixels_xy']);near=sorted((float(np.linalg.norm(np.array(o['xy'])-r['xy'])),o['id']) for o in g['observations'] if o['id']!=r['id'])[:1]
            centroid_gap=float(np.linalg.norm(pp.mean(0)-r['xy'])) if len(pp) else None;start_gap=float(np.linalg.norm(np.array(r.get('initial_prediction',r['xy']))-r['xy']))
            scan.append(dict(id=r['id'],layer=group,color=r['color'],body_only=r.get('body_only',False),pixel_count=len(pp),centroid_offset=centroid_gap,initial_relocation=start_gap,nearest=near,
                             evidence_kind='threshold response, not independently validated material ownership',admitted_by_darkness_alone=False,
                             risk_flags=(['prediction-seeded component'] if r.get('body_only') else [])+(['centroid migration >=6px'] if start_gap>=6 else [])+(['near another support <18px'] if near and near[0][0]<18 else [])))
    save(out/'investigation.json.gz',dict(cases=cases,all_native_evidence=scan,counts=dict(scanned=len(scan),dark_response_records=sum(r['color']=='black' for r in scan),prediction_seeded_black=sum(r['color']=='black' and r['body_only'] for r in scan),migration_ge6=sum(r['initial_relocation']>=6 for r in scan)),
         corrected_contract='Threshold/intensity samples never establish a separate visible bead. Independent ownership/shape evidence is required before admission. No new classifier or physical model.',seconds=time.perf_counter()-t))
    print('EVIDENCE',[(r['id'],r['initial']['pixel_count'],r['resampled']['pixel_count']) for r in cases],len(scan),'scanned',time.perf_counter()-t)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
