"""Conservative image-only location experiment. No review coordinates or identities.

Inputs: original RGB, color-managed sRGB and fixed parameters. No region growth,
geometry, counting target or geographic quota. Every mean7 plateau is inventoried.
"""
from dataclasses import dataclass,asdict
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import local_maxima
from .brightness_r270 import linearize,sums,SCALE,Search
from .climb_r268 import background
from .search_r269 import Policy

@dataclass(frozen=True)
class Criteria:
    minimum_mean_y: float=.25
    minimum_lit_fraction: float=.85
    lit_fraction_of_peak: float=.5
    minimum_core_pixels: int=25
    core_fraction_of_peak: float=.8
    minimum_window_ratio: float=.65
    minimum_local_contrast: float=.15
    maximum_plateau_diameter: float=2.
    maximum_endpoint_spread: float=3.
    rival_min_distance: float=4.
    rival_score_ratio: float=.9
    separating_valley_fraction: float=.25
    final_conflict_distance: float=6.

EXPLANATIONS={
'incomplete-context':'Too close to the image edge to check the full neighborhood.',
'background-nearby':'The 9×9 patch touches paper or uncertain background.',
'insufficient-light':'The neighborhood is too dim for this conservative set.',
'uneven-light':'Too much of the neighborhood is in deep shade.',
'small-bright-patch':'The bright patch is too small to give a reliable location.',
'window-dilution':'The bright signal falls too much when the neighborhood gets larger.',
'weak-local-contrast':'The peak does not stand out clearly from its surroundings.',
'flat-maximum':'The top is too flat to choose a precise location.',
'unstable-location':'Reasonable neighborhood or search settings choose different locations.',
'better-nearby-peak':'The broader search finds a brighter location elsewhere.',
'competing-highlights':'Two nearby bright peaks lack a clear separating dark valley.',
'nearby-trusted-conflict':'Two otherwise qualifying locations are too close; both are withheld.'}

def detect(native,srgb=None,criteria=Criteria(),progress=None):
    if srgb is None:srgb=native
    hsv,paper,model=background(native)
    # Linearize native-resolution color-managed pixels before averaging.
    lum=255*(linearize(srgb.astype(np.float64)/255)@np.array([.2126,.7152,.0722]))
    q=np.rint(lum*SCALE).astype(np.int64)
    ss={n:sums(q,n) for n in (5,7,9)}
    mask=local_maxima(ss[7],connectivity=2,allow_borders=True)&(ss[7]>=0)
    labels,num=ndi.label(mask,np.ones((3,3)));objects=ndi.find_objects(labels)
    h,w=lum.shape;rows=[];traces=[]
    yy,xx=np.mgrid[-12:13,-12:13];annulus=(xx*xx+yy*yy>=64)&(xx*xx+yy*yy<=144)
    for i,sl in enumerate(objects,1):
        ly,lx=np.where(labels[sl]==i);ys=ly+sl[0].start;xs=lx+sl[1].start
        # A plateau is one candidate; retain every pixel, no arbitrary bead label.
        center=np.array([xs.mean(),ys.mean()]);j=min(range(len(xs)),key=lambda k:((xs[k]-center[0])**2+(ys[k]-center[1])**2,int(ys[k]),int(xs[k])))
        x,y=int(xs[j]),int(ys[j]);mean=float(ss[7][y,x]/(49*SCALE));reasons=[]
        row=dict(id=f'L{i:06d}',x=x,y=y,plateau_pixels=[[int(a),int(b)] for a,b in zip(xs,ys)],mean_y=mean/255,raw_y=float(lum[y,x]/255),mean5_y=float(ss[5][y,x]/(25*SCALE*255)),mean9_y=float(ss[9][y,x]/(81*SCALE*255)),background_code=int(paper[y,x]),reasons=reasons,search_checked=False)
        rows.append(row)
        if min(x,y,w-1-x,h-1-y)<21:reasons.append('incomplete-context');continue
        patch=lum[y-4:y+5,x-4:x+5];r=criteria
        row.update(lit_fraction=float(np.mean(patch>=mean*r.lit_fraction_of_peak)),core_pixels=int(np.sum(patch>=mean*r.core_fraction_of_peak)),window_ratio=float(ss[9][y,x]*25/(ss[5][y,x]*81)),local_contrast=float((mean-np.median(lum[y-12:y+13,x-12:x+13][annulus]))/max(mean,1e-9)),plateau_diameter=float(np.hypot(xs.max()-xs.min(),ys.max()-ys.min())),background_pixels=int(np.sum(paper[y-4:y+5,x-4:x+5]>0)))
        checks=[(row['background_pixels']>0,'background-nearby'),(row['mean_y']<r.minimum_mean_y,'insufficient-light'),(row['lit_fraction']<r.minimum_lit_fraction,'uneven-light'),(row['core_pixels']<r.minimum_core_pixels,'small-bright-patch'),(row['window_ratio']<r.minimum_window_ratio,'window-dilution'),(row['local_contrast']<r.minimum_local_contrast,'weak-local-contrast'),(row['plateau_diameter']>r.maximum_plateau_diameter,'flat-maximum')]
        reasons.extend(reason for failed,reason in checks if failed)
    if progress:progress('inventoried',len(rows),'cheap-pass',sum(not z['reasons'] for z in rows))
    xy=np.array([[z['x'],z['y']] for z in rows]);tree=cKDTree(xy) if len(xy) else None
    for i,row in enumerate(rows):
        if row['reasons']:continue
        x,y=row['x'],row['y'];cut=np.s_[y-21:y+22,x-21:x+22];qc=q[cut];hs=hsv[cut];pp=paper[cut];ends=[];records=[];graphs={}
        for n in (5,7,9):
            g=Search(qc,hs,pp,ss[n][cut],n,(21,21),'Y');graphs[n]=g
            for radius in (10,16):
                for raw,mean in ((12,2),(24,2),(24,6)):
                    policy=Policy(raw,mean);result=g.search(radius,policy);path=g.path(result['pred'],result['end']);g.audit_path(path,radius,policy)
                    end=(g.xy[result['end']]+[x-21,y-21]).astype(int).tolist();ends.append(end)
                    for p in path:p['x']+=x-21;p['y']+=y-21
                    records.append(dict(window=n,radius=radius,raw_allowance=raw,mean_allowance=mean,endpoint=end,path=path,floors=list(g.floors(policy))))
                    if n==7 and radius==16 and raw==24 and mean==2:row['primary_endpoint']=end
        endpoints=np.array(ends);spread=float(np.sqrt(((endpoints[:,None]-endpoints[None,:])**2).sum(axis=2)).max());row.update(search_checked=True,endpoint_spread=spread)
        if spread>criteria.maximum_endpoint_spread:row['reasons'].append('unstable-location')
        if row['primary_endpoint']!=[x,y]:row['reasons'].append('better-nearby-peak')
        # Rival peaks are never silently merged. Use the greatest possible mean
        # bottleneck with fixed color/background edges, including diagonal guards.
        g=graphs[7];cap,_=g.widest(16,Policy(256,256),'mean');rivals=[]
        for j in tree.query_ball_point([x,y],16):
            other=rows[j];dist=float(np.hypot(other['x']-x,other['y']-y))
            if dist<criteria.rival_min_distance or other['background_code'] or other['mean_y']<criteria.rival_score_ratio*row['mean_y']:continue
            idx=g.index((other['x']-x+21,other['y']-y+21));saddle=float(cap[idx]/255);floor=(1-criteria.separating_valley_fraction)*min(row['mean_y'],other['mean_y']);ambiguous=saddle>=floor
            rivals.append(dict(id=other['id'],distance=dist,mean_y=other['mean_y'],best_saddle_y=saddle,required_saddle_below=floor,ambiguous=bool(ambiguous)))
        if any(z['ambiguous'] for z in rivals):row['reasons'].append('competing-highlights')
        row['rivals']=rivals;traces.append(dict(id=row['id'],searches=records,rivals=rivals))
        if progress and len(traces)%100==0:progress('searched',len(traces))
    eligible=[i for i,z in enumerate(rows) if not z['reasons']];conflicts=[]
    if eligible:
        pairs=cKDTree(xy[eligible]).query_pairs(criteria.final_conflict_distance)
        for a,b in sorted(pairs):
            ia,ib=eligible[a],eligible[b];conflicts.append([rows[ia]['id'],rows[ib]['id']])
            for j in (ia,ib):
                if 'nearby-trusted-conflict' not in rows[j]['reasons']:rows[j]['reasons'].append('nearby-trusted-conflict')
    for row in rows:row['trusted']=not row['reasons'];row['explanations']=[EXPLANATIONS[k] for k in row['reasons']]
    summary=dict(candidates=len(rows),trusted=sum(z['trusted'] for z in rows),searched=len(traces),exclusions=dict(Counter(k for z in rows for k in z['reasons'])),conflicts=conflicts,criteria=asdict(criteria),background_model=model)
    return rows,traces,summary,mask,paper
