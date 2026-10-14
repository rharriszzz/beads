"""Freeze photo-only central-heavy confirmation before candidate results exist."""
import hashlib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r282.phase1 import image_features
from photo2.r284.methods import seed_color
from .common import *

def main():
    _,rgb,_=photo();f=image_features(rgb);old=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];oldcenters=[c['center'] for c in read(ROOT/'photo2/r284b/results/cases.json')];oldcenters += [q['seed'] for q in read(OLD/'selection.json')['confirmation']];selected=[];pool=[]
    def far(p):return all(np.linalg.norm(np.array(p)-q)>145 for q in oldcenters) and all(np.linalg.norm(np.array(p)-q['seed'])>145 for q in selected)
    def rank(r):return hashlib.sha256(('R286-confirmation:'+r['record_id']).encode()).hexdigest()
    for r in old:
        if r['color'] not in ('red','yellow') or r['status']!='high':continue
        x,y=r['seed'];lum=f['lum'][y-5:y+6,x-5:x+6];q=float(np.quantile(lum,.5));peak=float(lum.max());r=dict(r,exposure_Y=q,peak_diffuse_ratio=peak/max(q,.001))
        if q>.025:pool.append(r)
    def add(r,stratum,extra=None):
        selected.append(dict(name=f'C{len(selected)+1:02}',id=r['record_id'],seed=r['seed'],color=r['color'],stratum=stratum,source_status=r['status'],exposure_Y=r['exposure_Y'],peak_diffuse_ratio=r['peak_diffuse_ratio'],companions=extra or []))
    for color in ('red','yellow'):
        for k in range(2):
            candidates=[r for r in pool if r['color']==color and r['centerline']['crosses'] and far(r['seed'])]
            if not candidates:raise RuntimeError('Empty crossing stratum '+color)
            add(min(candidates,key=rank),'central-crossing-'+color)
    candidates=[r for r in pool if r['color']=='red' and r['centerline']['near'] and far(r['seed'])];cut=float(np.quantile([r['peak_diffuse_ratio'] for r in candidates],.5));add(min([r for r in candidates if r['peak_diffuse_ratio']>=cut],key=rank),'central-red-highlight')
    for kind in ('same-color-dark-seam','opposite-side-near'):
        pairs=[]
        for a in pool:
            if not(a['centerline']['near'] and far(a['seed'])):continue
            for b in pool:
                if b['record_id']==a['record_id'] or not b['centerline']['near']:continue
                d=np.linalg.norm(np.array(a['seed'])-b['seed'])
                if not 12<=d<=42:continue
                if kind=='same-color-dark-seam':
                    if a['color']!=b['color']:continue
                    route=np.linspace(a['seed'],b['seed'],100);vals=ndi.map_coordinates(f['mean5'],route[:,::-1].T,order=1)
                    if vals.min()>.65*min(vals[0],vals[-1]):continue
                elif {a['centerline']['side'],b['centerline']['side']}!={'negative','positive'}:continue
                pairs.append((a,b))
        if not pairs:raise RuntimeError('Empty pair '+kind)
        a,b=min(pairs,key=lambda q:rank(q[0]));add(a,'central-'+kind,[b['record_id']])
    candidates=[r for r in pool if r['centerline']['near'] and far(r['seed'])];add(min(candidates,key=rank),'central-near-additional')
    for color in ('red','yellow'):
        candidates=[r for r in pool if r['color']==color and not r['centerline']['near'] and far(r['seed'])];add(min(candidates,key=rank),'secondary-clear-edge-'+color)
    # Freeze all neighboring old cues and complementary native maxima now, before inference.
    signal=ndi.uniform_filter(f['lum'],3);maximum=(signal==ndi.maximum_filter(signal,7))&(signal>.035)&~f['paper'];baseline_tree=cKDTree([r['seed'] for r in old]);curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);ct=cKDTree(curve)
    for c in selected:
        p=np.array(c['seed']);neighbors=[dict(id=r['record_id'],seed=r['seed'],color=r['color'],source_status=r['status'],source='R283 photo-only') for r in old if r['color'] in ('red','yellow') and np.linalg.norm(np.array(r['seed'])-p)<=40]
        x,y=c['seed'];yy,xx=np.where(maximum[y-35:y+36,x-35:x+36]);fresh=[]
        for px,py in zip(xx+x-35,yy+y-35):
            if baseline_tree.query([px,py])[0]<5 or ct.query([px,py])[0]>30:continue
            color=seed_color(f,[px,py])
            if color not in ('red','yellow'):continue
            fresh.append(dict(id=f'fresh-{px}-{py}',seed=[int(px),int(py)],color=color,source_status='unresolved',source='mean3/7px photograph maximum >=5px from every old cue'))
        c['observations']=neighbors+fresh
    save(OUT/'selection.json',dict(confirmation=selected,development=[dict(name=q['name'],old_example=q['old_example'],id=q['observation']['id'],seed=q['observation']['seed'],color=q['observation']['color']) for q in reviewed()],rule='SHA256 R286-confirmation:ID, high old photographic status with native median11>0.025; central crossing/near plus dark-profile pair/opposite signed pair, two secondary clear-edge cases; >145px from all R284B/R285 reviewed centers and earlier confirmation anchors. Fixed before new methods. Old high is not truth.',photo_sha256=sha(ROOT/'beads-photo-2.jpg'),prior_sha256=sha(ROOT/'photo2/r283/results/phase1.json.gz'),confirmation_images_opened=False))
    print([(c['name'],c['stratum'],len(c['observations'])) for c in selected])
if __name__=='__main__':main()
