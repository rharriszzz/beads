"""Freeze balanced J differences and unseen photo validation before new methods.

Flags are measurements of algorithm disagreement, NOT bead truth. Reviewed
coordinates are evaluation selectors only. No selection data enters methods.py.
"""
import hashlib
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from photo2.r282.common import ROOT,read,save,photo,sha,pixels
from photo2.r282.phase1 import image_features
from photo2.r284.methods import color_domain,seed_color
from photo2.r284b.methods import colored
from photo2.r284b.run import mask_of
from photo2.r284b.review import get_target
from photo2.r284.assess import TARGETS
OUT=ROOT/'photo2/r285/results';OLD=ROOT/'photo2/r284b/results'

def bank():
    return [o for c in read(OLD/'cases.json') for o in read(OLD/(c['name']+'.json.gz'))['observations']]

def main():
    OUT.mkdir(parents=True,exist_ok=True);obs=[o for o in bank() if o['color']!='black'];_,rgb,meta=photo();f=image_features(rgb)
    # Execute the previous methods on the identical frozen bank. All returned
    # native masks must exactly equal the saved R284B controls.
    from photo2.r282.common import circular_distance
    replay=0
    for o in obs:
        seed=np.array(o['seed']);x,y=seed;origin=seed-24;lum=f['lum'][y-24:y+25,x-24:x+25];hs=f['hsv'][y-24:y+25,x-24:x+25]
        domain,local=color_domain(f,dict(xy=seed,color=o['color']));_,_,_,paper,dist,peak=local
        own=circular_distance(hs[:,:,0]*360,f['palette'][o['color']]);other=next(v for k,v in f['palette'].items() if k!=o['color']);rival=circular_distance(hs[:,:,0]*360,other)
        wide=domain|((hs[:,:,1]>.27)&(own<24)&(rival-own>2)&(lum>max(.012,.09*peak))&~paper&(dist<=24))
        initial=mask_of(o['initial_support'],origin)
        for m in ('A','T','E','W','L','I','J'):
            mask,_,_=colored(lum,wide if m=='J' else domain,initial,variant=m)
            np.testing.assert_array_equal(mask,mask_of(o['variants'][m]['measured_support'],origin));replay+=1
        a=o['variants']['A'];j=o['variants']['J'];pa=set(map(tuple,pixels(a['measured_support'])));pj=set(map(tuple,pixels(j['measured_support'])));lost=np.array(sorted(pa-pj),int).reshape(-1,2)
        vals=f['lum'][lost[:,1],lost[:,0]] if len(lost) else []
        overlap=0
        for q in obs:
            if q['id']==o['id'] or q['color']!=o['color'] or np.linalg.norm(np.array(q['seed'])-seed)>50:continue
            overlap=max(overlap,len(pj&set(map(tuple,pixels(q['initial_support'])))))
        o['selection_metrics']=dict(retained=j['metrics']['retained_fraction'],area=j['metrics']['area'],
            gain=j['metrics']['added'],loss=j['metrics']['removed'],shift=j['metrics']['centroid_shift'] or 0,
            clipping=j['method_evidence'].get('search_radius_contact_pixels',0),overlap_old_neighbor=overlap,
            lost_Y_integral=float(np.sum(vals)),gradient_delta=(j['metrics']['boundary_gradient'] or 0)-(a['metrics']['boundary_gradient'] or 0))
    selected=[]
    def add(o,kind,reason):
        selected.append(dict(example=f'e{len(selected)+1:02}',observation_id=o['id'],case=o['id'].split(':')[0],seed=o['seed'],color=o['color'],category=kind,selection_reason=reason,metrics=o['selection_metrics']))
    for label,xy in TARGETS['two-sided']+TARGETS['abstention']:
        o=min(obs,key=lambda o:np.linalg.norm(np.array(o['seed'])-xy));add(o,'mandatory-review',label+'; user evidence, not inference prior')
    specs=[('red-truncation','red',lambda m:(1-m['retained'])*min(600,m['loss']),2),
        ('yellow-neighbor-connection','yellow',lambda m:m['overlap_old_neighbor'],2),
        ('oversized','red',lambda m:m['area'] if m['area']>870 else -1,2),
        ('search-clipping',None,lambda m:m['clipping'],1),
        ('lost-bright-material',None,lambda m:m['lost_Y_integral'],1),
        ('centroid-movement',None,lambda m:m['shift'],2),
        ('potential-improvement',None,lambda m:m['gradient_delta']*np.sqrt(max(0,m['gain'])) if .65<m['retained'] and 0<m['gain'] and m['area']<870 and m['overlap_old_neighbor']<10 else -1,2)]
    for kind,color,score,n in specs:
        for rep in range(n):
            counts=Counter(r['case'] for r in selected)
            strong=(kind=='potential-improvement' or (kind in ('red-truncation','yellow-neighbor-connection') and rep==0))
            pool=[o for o in obs if (not strong or o['source_status']=='high') and (color is None or o['color']==color) and all(np.linalg.norm(np.array(o['seed'])-r['seed'])>=35 for r in selected) and counts[o['id'].split(':')[0]]<3]
            if not pool:raise RuntimeError('No balanced sample candidate '+kind)
            o=max(pool,key=lambda o:(score(o['selection_metrics']),o['id']));add(o,kind,f'Maximum {kind} diagnostic with ≥35px separation and at most3 per old crop; color={color}; score={score(o["selection_metrics"]):.6g}; strong-source stratum={strong}. Difference is not established regression.')
    baseline=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];oldcenters=[c['center'] for c in read(OLD/'cases.json')];hold=[]
    def far(p):return all(np.linalg.norm(np.array(p)-q)>180 for q in oldcenters+[r['seed'] for r in hold])
    def hashed(r):return hashlib.sha256(('R285-confirmation:'+r['record_id']).encode()).hexdigest()
    for color,status,count in [('red','high',2),('yellow','high',2),('red','unresolved',1),('yellow','unresolved',1),('black','high',1),('black','unresolved',1)]:
        for _ in range(count):
            pool=[r for r in baseline if r['color']==color and r['status']==status and r['centerline']['near'] and far(r['seed'])]
            r=min(pool,key=hashed);hold.append(dict(id=r['record_id'],seed=r['seed'],color=color,source_status=status,selection='Minimum SHA256(R285-confirmation:ID) within color/status, support-near, >180px from all old crops and previous confirmation anchors.'))
    # New mean3 maxima near the image-derived curve and not close to a historical
    # seed. These are tentative new photo cues, not certified missing bodies.
    lum=f['lum'];signal=ndi.uniform_filter(f['lum'],3);maxima=(signal==ndi.maximum_filter(signal,7))&(signal>.035)&~f['paper'];y,x=np.where(maxima);p=np.c_[x,y]
    curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);dist,_=cKDTree(curve).query(p);old_dist,_=cKDTree([r['seed'] for r in baseline]).query(p)
    p=p[(dist<=30)&(old_dist>=6)]
    for color in ('red','yellow'):
        pool=[dict(record_id=f'fresh-{x}-{y}',seed=[int(x),int(y)],color=color) for x,y in p if far([x,y]) and seed_color(f,[x,y])==color]
        if not pool:continue # Empty fresh stratum is evidence, not permission to invent a cue.
        r=min(pool,key=hashed);hold.append(dict(id=r['record_id'],seed=r['seed'],color=color,source_status='new-unresolved',selection='Fresh mean3 7px maximum >.035, within30px of image curve, ≥6px from every R283 seed; hash-ranked color cue, >180px from development/previous confirmation.'))
    save(OUT/'selection.json',dict(development=selected,confirmation=hold,control_replayed_masks=replay,
        candidate_count=len(obs),source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [OLD/'cases.json',ROOT/'photo2/r283/results/phase1.json.gz',ROOT/'beads-photo-2.jpg']},
        caution='Frozen before new algorithms. Flags do not establish bead identities or old-mask correctness. Confirmation crops are not inspected during development.'))
    save(OUT/'candidate-differences.json',[dict(id=o['id'],seed=o['seed'],color=o['color'],metrics=o['selection_metrics']) for o in obs])
    print('Control masks exact:',replay,'Development:',len(selected),'Confirmation:',len(hold))
    for r in selected:print(r['example'],r['category'],r['case'],r['color'],r['seed'])

if __name__=='__main__':main()
