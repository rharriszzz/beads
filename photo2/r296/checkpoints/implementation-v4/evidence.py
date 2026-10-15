"""Freeze existing observations and photograph-derived evaluation samples.

No detector outputs are created or changed. Palette/paper/edge diagnostics reuse
R295's existing photometric measurements; all segmentation supports are preserved.
"""
import argparse
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r293.geometry import Reference
from photo2.r282.phase1 import image_features
from photo2.r282.common import circular_distance
from .common import *

BUFFER = 60.

def station(xy, inputs, ref):
    return (inputs['direction'] * (ref.project(xy)['arc'] - inputs['arc0'])) % ref.length

def labels(stations, intervals, length):
    stations = np.asarray(stations)
    result = np.full(stations.shape, 'train', dtype='<U10')
    for split, ranges in intervals.items():
        for a, b in ranges:
            result[(stations >= a-BUFFER) & (stations <= b+BUFFER)] = 'buffer'
    for split, ranges in intervals.items():
        for a, b in ranges:
            result[(stations >= a) & (stations <= b)] = split
    return result

def freeze(destination=EVIDENCE):
    destination = Path(destination)
    if (destination/'freeze.json').exists():
        raise ValueError('Evidence is already frozen; never overwrite it.')
    inp = read(ROOT/'photo2/r294/evidence/inputs.json.gz')
    ref = Reference()
    source = read(ROOT/'photo2/r293/results/phase1-observations.json.gz')['records']
    old = read(ROOT/'photo2/r283/results/phase1.json.gz')['records']
    rows = []
    for r in source:
        support = r['native_bright_patch']
        if support['pixel_count'] >= 3 and r['intensity']['contrast_Y'] >= .03 and r['centerline']['distance'] <= 65:
            rows.append(dict(id=r['observation_id'], kind='patch', pixels=support,
                point=r['representative_bright_patch_location'], color=r['source_context_color'],
                reflection=r['reflection_like_patch'], provenance=dict(source='photo2/r293/results/phase1-observations.json.gz', id=r['observation_id']),
                trust='Independent bright patch; ownership unknown', accepted=False))
        v = r['accepted_visible_measurement']
        if v:
            rows.append(dict(id='accepted:'+r['observation_id'], kind='region', pixels=v['native_pixels'],
                point=v['representative_centroid'], color=r['source_context_color'], reflection='reflection' in v['kind'],
                provenance=v['provenance'], trust=v['limits'], accepted=True))
    for r in old:
        if r['color'] in ('red', 'yellow') and r['measured_support'] and r['status']=='high':
            rows.append(dict(id=r['record_id'], kind='region', pixels=r['measured_support'], point=r['measured_photo_location'],
                color=r['color'], reflection=False, accepted=False,
                provenance=dict(source='photo2/r283/results/phase1.json.gz', id=r['record_id']),
                trust='Historical automatic interior; fallible extent and ownership'))
    for r in inp['completed_r293_reviews']:
        if r['answer'] != 'A':
            continue
        a = r['accepted_candidate']
        feature = next(x for x in source if x['observation_id']==r['feature_id'])
        rows.append(dict(id='accepted293:'+r['case_id'], kind='region', pixels=a['candidate_pixels'], point=a['candidate_centroid'],
            color=feature['source_context_color'], reflection=feature['reflection_like_patch'], accepted=True,
            provenance=dict(source=r['source'], sha256=r['source_sha256'], answer='A', case_id=r['case_id']),
            trust='Qualitatively accepted exact candidate; not calibrated pixels or physical identity'))
    for r in rows:
        q = ref.project([r['point']])
        r['station'] = float(station([r['point']], inp, ref)[0])
        r['stratum'] = 'central' if q['distance'][0] <= 26 else 'peripheral'
    accepted_stations = [r['station'] for r in rows if r['accepted']]
    # Entire R294 inspected window excluded, plus all accepted human cases.
    centers = np.arange(1550., ref.length-400, 160.)
    centers = [float(c) for c in centers if all(min(abs(c-a), ref.length-abs(c-a))>220 for a in accepted_stations)]
    # Fixed seed used only to designate geographic blocks, never from fit outcomes.
    rng = np.random.default_rng(29601)
    ordered = sorted(centers)
    centers = []
    for c in ordered:
        if all(abs(c-v)>350 for v in centers):
            centers.append(c)
    centers = list(np.asarray(centers)[rng.permutation(len(centers))])
    if len(centers)<6:
        raise ValueError('Insufficient unexposed geographic intervals')
    intervals = {k:[[float(c-85),float(c+85)] for c in centers[j:j+3]] for k,j in [('validation',0),('reserved',3)]}
    for r in rows:
        labs = labels(station(pixels(r['pixels']), inp, ref), intervals, ref.length)
        r['split'] = str(labs[0]) if np.all(labs==labs[0]) else 'buffer'
        if r['accepted'] and r['split']!='train':
            raise ValueError('Human-reviewed case leaked into withheld geography')
    native, rgb, meta = photo()
    f = image_features(rgb); hsv, lum = f['hsv'], f['lum']
    color = np.zeros(lum.shape, np.int8)
    for j,c in enumerate(('red','yellow'),1):
        color[(circular_distance(hsv[:,:,0]*360,f['palette'][c])<23)&(hsv[:,:,1]>.30)&(lum>.035)&~f['paper']] = j
    sm = ndi.gaussian_filter(lum,1)
    gradient = np.hypot(ndi.sobel(sm,0),ndi.sobel(sm,1))/8
    dark = np.maximum(ndi.gaussian_filter(lum,3)-sm,0)
    strength = ndi.maximum_filter(np.maximum(np.clip(gradient/.035,0,1),np.clip(dark/.055,0,1)),size=3)
    yy,xx = np.mgrid[0:lum.shape[0]:5,0:lum.shape[1]:5]
    xy = np.c_[xx.ravel(),yy.ravel()]
    q = ref.project(xy); keep = q['distance']<85
    xy = xy[keep]; distance = q['distance'][keep]
    st = station(xy,inp,ref); lab = labels(st,intervals,ref.length)
    # Guard against different portions of the curve being close in Euclidean space.
    held_xy = np.concatenate([pixels(r['pixels']) for r in rows if r['split'] in ('validation','reserved')]+[xy[np.isin(lab,['validation','reserved'])]])
    tree = cKDTree(held_xy)
    for r in rows:
        if r['split']=='train' and np.min(tree.query(pixels(r['pixels']))[0])<35:
            r['split']='buffer'
    lab[(lab=='train') & (tree.query(xy)[0]<35)] = 'buffer'
    look = {tuple(p):i for i,p in enumerate(xy)}; pairs=[]
    for i,(x,y) in enumerate(xy):
        for dx,dy in ((5,0),(0,5)):
            j=look.get((x+dx,y+dy))
            if j is not None and lab[i]==lab[j]:
                pairs.append((i,j))
    pairs=np.asarray(pairs); mid=np.rint((xy[pairs[:,0]]+xy[pairs[:,1]])/2).astype(int)
    # Neighbor separator cues for ownership graph, entirely photographic.
    regions=[r for r in rows if r['kind']=='region']; edges=[]
    for i,j in sorted(cKDTree([r['point'] for r in regions]).query_pairs(58)):
        a,b=regions[i],regions[j]
        if a['split']!=b['split']: continue
        route=np.array(a['point'])+np.linspace(0,1,31)[:,None]*(np.array(b['point'])-a['point'])
        v=ndi.map_coordinates(lum,[route[:,1],route[:,0]],order=1)
        valley=float(np.clip(1-np.min(v[5:-5])/max(.02,min(np.median(v[:5]),np.median(v[-5:]))),0,1))
        edges.append(dict(ids=[a['id'],b['id']],split=a['split'],valley=valley,
            separation_weight=.35*(a['color']!=b['color'])+.18*max(0,valley-.25)))
    destination.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(destination/'cues.npz',xy=xy,station=st,split=lab,distance=distance,
        color=color[xy[:,1],xy[:,0]],paper=f['paper'][xy[:,1],xy[:,0]],lum=lum[xy[:,1],xy[:,0]],
        pairs=pairs,edge=strength[mid[:,1],mid[:,0]],mid_lum=lum[mid[:,1],mid[:,0]])
    sources=['beads-photo-2.jpg','photo2/r293/results/phase1-observations.json.gz','photo2/r283/results/phase1.json.gz',
        'photo2/r282/results/centerline.json','photo2/r294/evidence/inputs.json.gz','photo2/r295/results/joint.json','photo2/r295/results/hand-plus-evaluation.json']
    save(destination/'inputs.json.gz',dict(rows=rows,edges=edges,anchor=inp['anchor'],arc0=inp['arc0'],direction=inp['direction'],
        photo=meta,length=ref.length,intervals=intervals,buffer_px=BUFFER,sources={p:sha(ROOT/p) for p in sources},
        rejected_human_cases=[r['case_id'] for r in inp['completed_r293_reviews'] if r['answer']!='A'],
        limits='No new Phase1 masks. Same previously exposed photograph; fresh geographic withholding is not globally blind confirmation.'))
    trainxy=np.concatenate([pixels(r['pixels']) for r in rows if r['split']=='train'])
    save(destination/'freeze.json',dict(utc=utc(),inputs_sha256=sha(destination/'inputs.json.gz'),cues_sha256=sha(destination/'cues.npz'),
        intervals=intervals,counts={s:{k:sum(r['split']==s and r['kind']==k for r in rows) for k in ('patch','region')} for s in ('train','validation','reserved','buffer')},
        accepted=sum(r['accepted'] for r in rows),min_train_withheld_pixel_distance=float(tree.query(trainxy)[0].min()),
        reference_closure='Input reference endpoints coincide by construction; physical closure remains a hypothesis.',
        sources={p:sha(ROOT/p) for p in sources},implementation_sha256=sha(Path(__file__))))
    return read(destination/'freeze.json')

if __name__=='__main__':
    print(freeze())
