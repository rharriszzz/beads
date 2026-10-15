"""Freeze photographic supports, spatial splits and unmodified source hashes."""
import subprocess,datetime
import numpy as np
from scipy import ndimage as ndi
from photo2.r293.geometry import Reference
from photo2.r282.phase1 import image_features
from photo2.r282.common import circular_distance
from .common import *
DEV=[(170,210),(295,325)];RES=[(410,455),(575,620)]
def split(s,buffer=15):
    s=np.asarray(s)
    for name,intervals in [('reserved',RES),('validation',DEV)]:
        if any(np.any((s>=a)&(s<=b)) for a,b in intervals):return name
    if any(np.any((s>=a-buffer)&(s<=b+buffer)) for a,b in DEV+RES):return 'buffer'
    return 'train'
def along(xy,inp,ref):
    a=ref.project(xy)['arc'];return inp['direction']*((a-inp['arc0']+ref.length/2)%ref.length-ref.length/2)
def main():
    assert not (EVIDENCE/'freeze.json').exists()
    inp=read(ROOT/'photo2/r294/evidence/inputs.json.gz');ref=Reference();native,rgb,meta=photo();rows=[];accepted=[]
    # Inventory every accepted R291/R292 version, including out-of-run evidence.
    for r in read(ROOT/'photo2/r293/results/phase1-observations.json.gz')['records']:
        v=r['accepted_visible_measurement']
        if v:accepted.append(dict(id=r['observation_id'],along_px=float(along([r['representative_bright_patch_location']],inp,ref)[0]),measurement=v))
    for r in inp['completed_r293_reviews']:
        if r['answer']=='A':accepted.append(dict(id=r['case_id'],along_px=r['along_px'],measurement=r))
    for kind,source in [('patch',inp['records']),('region',inp['legacy_colored'])]:
        for r in source:
            if not r['fit_eligible']:continue
            f=r['source'];region=f['native_bright_patch'] if kind=='patch' else f['measured_support'];xy=pixels(region);station=along(xy,inp,ref)
            rows.append(dict(id=f['observation_id'] if kind=='patch' else f['record_id'],kind=kind,pixels=region,
                point=f['representative_bright_patch_location'] if kind=='patch' else f['measured_photo_location'],
                color=f['source_context_color'] if kind=='patch' else f['color'],reflection=f.get('reflection_like_patch',False),
                split=split(station),along_px=r['along_px'],station_extent=[float(station.min()),float(station.max())],
                historical_split=r['split'],trust='independent bright patch, unknown owner' if kind=='patch' else 'historical automatic interior, fallible ownership',
                original=f))
    f=image_features(rgb);hsv=f['hsv'];lum=f['lum'];color=np.zeros(lum.shape,np.int8)
    for j,c in enumerate(('red','yellow'),1):
        color[(circular_distance(hsv[:,:,0]*360,f['palette'][c])<23)&(hsv[:,:,1]>.30)&(lum>.035)&~f['paper']]=j
    # Photographic edges, not new bead proposals: local gradient or coherent dark ridge.
    sm=ndi.gaussian_filter(lum,1);gradient=np.hypot(ndi.sobel(sm,0),ndi.sobel(sm,1))/8
    dark=np.maximum(ndi.gaussian_filter(lum,3)-sm,0)
    strength=np.maximum(np.clip(gradient/.035,0,1),np.clip(dark/.055,0,1))
    strength=ndi.maximum_filter(strength,size=3)
    yy,xx=np.mgrid[180:830:5,1280:2240:5];xy=np.c_[xx.ravel(),yy.ravel()];station=along(xy,inp,ref);q=ref.project(xy)
    keep=(station>=-65)&(station<=760)&(q['distance']<63);xy=xy[keep];station=station[keep];ix=xy.astype(int)
    labels=np.array([split([s]) for s in station]);look={tuple(p):i for i,p in enumerate(xy)};pairs=[]
    for i,(x,y) in enumerate(xy):
        for dx,dy in ((5,0),(0,5)):
            j=look.get((x+dx,y+dy))
            if j is not None and labels[i]==labels[j]:pairs.append((i,j))
    pairs=np.array(pairs);mid=np.rint((xy[pairs[:,0]]+xy[pairs[:,1]])/2).astype(int)
    np.savez_compressed(EVIDENCE/'photographic-cues.npz',xy=xy,station=station,split=labels,
        color=color[ix[:,1],ix[:,0]],paper=f['paper'][ix[:,1],ix[:,0]],lum=lum[ix[:,1],ix[:,0]],pairs=pairs,
        edge=strength[mid[:,1],mid[:,0]],mid_lum=lum[mid[:,1],mid[:,0]])
    paths=subprocess.check_output(['git','ls-files','-z'],text=True).split('\0')
    hashes={p:sha(ROOT/p) for p in paths if p and (p.startswith('photo2/') or p in ('beads.pov','beads-photo-2.jpg')) and not p.startswith(('photo2/r295/','photo2/review/r295/','photo2/R295'))}
    feedback={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'photo2').glob('r*/feedback/**/*') if p.is_file()}
    save(EVIDENCE/'preservation.json.gz',dict(science=hashes,feedback=feedback))
    save(EVIDENCE/'inputs.json.gz',dict(r294=inp,rows=rows,accepted_inventory=accepted,photo=meta,source_hashes=inp['sources'],
        intervals=dict(validation=DEV,reserved=RES,buffer=15),limits='One exposed photograph; geographical withholding, not new-image validation. Automatic supports are not ownership truth.'))
    save(EVIDENCE/'freeze.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs_sha256=sha(EVIDENCE/'inputs.json.gz'),cues_sha256=sha(EVIDENCE/'photographic-cues.npz'),
        counts={k:{s:sum(r['kind']==k and r['split']==s for r in rows) for s in ('train','validation','reserved','buffer')} for k in ('patch','region')},accepted_in_requested_window=[r['id'] for r in accepted if -65<=r['along_px']<=760],sources=source_hashes()))
    print(read(EVIDENCE/'freeze.json')['counts'])
if __name__=='__main__':main()
