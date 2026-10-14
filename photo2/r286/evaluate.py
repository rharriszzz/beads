"""Photographic diagnostics, not calibrated physical ownership accuracy."""
from collections import Counter
from itertools import combinations
import numpy as np
from scipy import ndimage as ndi
from .common import *
METHODS=('J','S','M','A','B','C')
def pset(r):return set(map(tuple,pixels(r['measured_support'])))
def avg(values):
    values=[v for v in values if v is not None];return float(np.mean(values)) if values else None

def summary(cases,anchors=False):
    obs=[min(q['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-q['seed'])) for q in cases] if anchors else [o for q in cases for o in q['observations']];out={}
    for m in METHODS:
        rr=[o['variants'][m] for o in obs];out[m]=dict(observations=len(rr),areas=[r['metrics']['area'] for r in rr],nonempty=sum(r['metrics']['area']>0 for r in rr),flagged=sum(bool(r['abstention_reasons']) for r in rr),flags=dict(Counter(f for r in rr for f in r['abstention_reasons'])),components=dict(Counter(str(r['metrics']['components']) for r in rr)),mean_boundary_gradient=avg([r['metrics']['boundary_gradient'] for r in rr]),mean_centroid_shift_from_S=avg([r['metrics']['centroid_shift'] for r in rr]),mean_retention_of_S=avg([r['metrics']['retained_fraction'] for r in rr]),support_near=sum(r['centerline']['near'] for r in rr),support_crossing=sum(r['centerline']['crosses'] for r in rr),reviewable_near=sum(r['centerline']['near'] and not r['abstention_reasons'] for r in rr),domain_sensitive=sum(r['method_evidence'].get('domain_sensitive',False) for r in rr),illumination_sensitive=sum(r['method_evidence'].get('illumination_sensitive',False) for r in rr),mean_domain_iou=avg([r['method_evidence'].get('domain_iou') for r in rr]),mean_illumination_iou=avg([p['iou'] for r in rr for p in r['method_evidence'].get('illumination_perturbations',[])]))
    return out

def main():
    development=read(OUT/'development.json.gz')['cases'];cases=read(OUT/'confirmation.json.gz')['cases'];native,rgb,_=photo()
    from photo2.r282.phase1 import image_features
    f=image_features(rgb);signal=ndi.uniform_filter(f['lum'],3);pairs=[];overlap=[];coverage=[]
    for case in cases:
        obs=case['observations']
        for a,b in combinations(obs,2):
            p,q=np.array(a['seed']),np.array(b['seed']);d=np.linalg.norm(p-q)
            if not 12<=d<=42 or a['color']!=b['color']:continue
            route=np.rint(np.linspace(p,q,int(np.ceil(d))*2+1)).astype(int);v=signal[route[:,1],route[:,0]];ref=min(v[0],v[-1]);ratio=float(v.min()/max(ref,1e-9));entry=dict(case=case['name'],ids=[a['id'],b['id']],distance=float(d),straight_valley_ratio=ratio,photo_seam_candidate=bool(ref>.025 and ratio<.65),route=route.tolist(),Y=v.tolist(),methods={})
            for m in METHODS:
                aa,bb=pset(a['variants'][m]),pset(b['variants'][m]);shared=len(aa&bb);iou=shared/max(1,len(aa|bb));cores=[]
                for xy in (p,q):cores.append({tuple(xy+[dx,dy]) for dx in range(-2,3) for dy in range(-2,3) if dx*dx+dy*dy<=4})
                owns_both=any(all(len(s&c)/len(c)>=.5 for c in cores) for s in (aa,bb));entry['methods'][m]=dict(overlap=shared,iou=iou,one_support_contains_both_native_cores=owns_both)
            pairs.append(entry)
        for m in METHODS:
            rows=[o['variants'][m] for o in obs];pp=[pset(r) for r in rows];edges=[]
            for i,j in combinations(range(len(rows)),2):
                intersect=len(pp[i]&pp[j]);iou=intersect/max(1,len(pp[i]|pp[j]));contain=intersect/max(1,min(len(pp[i]),len(pp[j])))
                if intersect:overlap.append(dict(case=case['name'],method=m,ids=[obs[i]['id'],obs[j]['id']],intersection=intersect,iou=iou,containment=contain,near_duplicate=iou>=.5))
                if iou>=.5:edges.append((i,j))
            parent=list(range(len(rows)))
            def root(i):
                while parent[i]!=i:i=parent[i]
                return i
            for i,j in edges:parent[root(j)]=root(i)
            near=[i for i,r in enumerate(rows) if r['centerline']['near'] and not r['abstention_reasons']];groups={root(i) for i in near};sides={rows[i]['centerline']['side'] for i in near};intervals=[]
            for i,j in combinations(near,2):
                ci,cj=rows[i]['centerline'],rows[j]['centerline'];ai,aj=ci.get('arc_interval',[0,0]),cj.get('arc_interval',[0,0]);gap=max(ai[0],aj[0])-min(ai[1],aj[1]);shared=len(pp[i]&pp[j])/max(1,min(len(pp[i]),len(pp[j])))
                if {ci['side'],cj['side']}=={'negative','positive'} and gap<=12 and shared<.2:intervals.append([obs[i]['id'],obs[j]['id']])
            coverage.append(dict(case=case['name'],method=m,stratum=case['stratum'],near_proposals=len(near),near_overlap_groups=len(groups),support_crossing=sum(rows[i]['centerline']['crosses'] for i in near),signed_sides=sorted(sides),flanking_pairs=intervals,interpretation='Overlap groups are photographic proposals, not verified beads; no-crossing interior does not rule out body crossing.'))
    seam_summary={m:dict(candidate_pairs=sum(p['photo_seam_candidate'] for p in pairs),dual_core_supports=sum(p['photo_seam_candidate'] and p['methods'][m]['one_support_contains_both_native_cores'] for p in pairs),overlap_pairs=sum(p['method']==m for p in overlap),near_duplicate_pairs=sum(p['method']==m and p['near_duplicate'] for p in overlap)) for m in METHODS}
    # Native dim S material retained: diagnostic reference only, not ground truth.
    retention=[]
    for case in development+cases:
        for o in case['observations']:
            s=pset(o['variants']['S']);lum=np.array(o['native_Y']);origin=np.array(o['origin']);pts=np.array(sorted(s),int).reshape(-1,2)-origin
            if not len(pts):continue
            vals=lum[pts[:,1],pts[:,0]];cut=float(np.median(vals));dim={tuple(p+origin) for p,v in zip(pts,vals) if v<=cut};retention.append(dict(case=case['name'],id=o['id'],color=o['color'],source_status=o['source_status'],S_dim_pixels=len(dim),methods={m:len(pset(o['variants'][m])&dim)/max(1,len(dim)) for m in METHODS}))
    save(OUT/'evaluation.json',dict(development=summary(development),confirmation_all=summary(cases),confirmation_anchors=summary(cases,True),central=summary(cases[:8]),edge=summary(cases[8:]),seam_summary=seam_summary,pairs=pairs,overlap=overlap,coverage=coverage,dim_S_retention=retention,limitations=['All real-photo measurements are evidence/proxies, not physical identity truth.','J/S lack the new full stability protocol; do not compare apparent acceptance rates.','Dual-core inclusion can be a false merger warning, or two cues on one bead; zero is not proof of no leakage.','Overlap can mean duplicate proposals, false partition or uncertain identity; no calibrated real precision/recall.']))
    print('seam',seam_summary)
if __name__=='__main__':main()
