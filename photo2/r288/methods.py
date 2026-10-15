"""E: ensemble plus photographed continuation. W: affirmative-evidence watershed.

Both are native photographic proposals, not certified bodies. No J-mask input,
review IDs, fixed reviewed coordinates, physical geometry or pattern hypotheses.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.segmentation import watershed
from photo2.r285.methods import component
from photo2.r286.methods import marker_field,watershed_support
from photo2.r287.evidence import diffuse_routes
from .fields import field,expand
from .chromatic import restrict
PARAMETERS=dict(ensemble_core_fraction=.8,ensemble_extension_fraction=.6,
    ensemble_sigma_delta=.15,ensemble_background_delta=.02,merge_ratio=.65,
    corridor_ratio=.55,corridor_min_routes=4,corridor_position_std=.15,require_central_route_dark=True,
    corridor_min_distance=6,corridor_max_distance=64,endpoint_pigment_fraction=.4,
    corridor_offsets=[-3,-1.5,0,1.5,3],semantics='Uncalibrated native interior hypotheses; stability is not ownership truth')

def corridor(sm,pg,p,q):
    p,q=np.array(p,float),np.array(q,float);delta=q-p;distance=float(np.linalg.norm(delta));yy,xx=np.indices(sm.shape);refs=[];fractions=[]
    for xy in (p,q):
        c=(xx-xy[0])**2+(yy-xy[1])**2<=36;fractions.append(float(pg[c].mean()));s=c&pg;refs.append(float(np.quantile(sm[s],.6)) if s.any() else 0.)
    ratios=[];positions=[];profiles=[]
    if PARAMETERS['corridor_min_distance']<=distance<=PARAMETERS['corridor_max_distance'] and min(refs)>.025:
        normal=np.array([-delta[1],delta[0]])/distance;t=np.linspace(0,1,max(25,int(distance)*2))
        for off in PARAMETERS['corridor_offsets']:
            route=p+t[:,None]*delta+off*normal;values=ndi.uniform_filter1d(ndi.map_coordinates(sm,route[:,::-1].T,order=1,mode='nearest'),3);valid=np.where((t>=.2)&(t<=.8))[0];ix=valid[np.argmin(values[valid])];ratios.append(float(values[ix]/min(refs)));positions.append(float(t[ix]));profiles.append(dict(offset=off,route=route.tolist(),Y=values.tolist(),trough_index=int(ix)))
    coherent=bool(ratios and ratios[2]<PARAMETERS['corridor_ratio'] and sum(r<PARAMETERS['corridor_ratio'] for r in ratios)>=PARAMETERS['corridor_min_routes'] and np.std(positions)<PARAMETERS['corridor_position_std'] and min(fractions)>=PARAMETERS['endpoint_pigment_fraction'])
    return dict(peaks=[p.tolist(),q.tolist()],distance=distance,references=refs,pigment_fractions=fractions,ratios=ratios,trough_positions=positions,coherent=coherent,profiles=profiles)

def positive_watershed(f):
    sm,pg,dm,paper,seed=(f[k] for k in ('smooth','pigment','domain','paper','seed'))
    if seed is None:return np.zeros_like(dm),dict(reason='no supported cue',interfaces=[],marker_ledger=[])
    markers,target,ledger=marker_field(sm,pg,dm,paper,seed);labels=watershed(-np.log(sm+.003),markers,mask=dm);yy,xx=np.indices(dm.shape);refs={};peaks={};interfaces={}
    for k in range(1,int(markers.max())+1):
        y,x=np.argwhere(markers==k)[0];peaks[k]=[int(x),int(y)];core=(labels==k)&pg&((xx-x)**2+(yy-y)**2<=36);refs[k]=float(np.quantile(sm[core],.6)) if core.any() else float(sm[y,x])
    for dy,dx in ((1,0),(0,1)):
        a=labels[:len(labels)-dy,:labels.shape[1]-dx];b=labels[dy:,dx:];ys,xs=np.where((a>0)&(b>0)&(a!=b))
        for y,x in zip(ys,xs):interfaces.setdefault(tuple(sorted((int(a[y,x]),int(b[y,x])))),[]).append([int(x),int(y),int(x+dx),int(y+dy)])
    edges=[];forbidden=set();parent=list(range(int(markers.max())+1))
    def root(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    for (a,b),points in sorted(interfaces.items()):
        q=np.array(points);ratios=np.minimum(sm[q[:,1],q[:,0]],sm[q[:,3],q[:,2]])/max(min(refs[a],refs[b]),1e-9);co=corridor(sm,pg,peaks[a],peaks[b]);dark=float(ratios.max())<PARAMETERS['merge_ratio'];block=dark or co['coherent']
        if block:forbidden.add((a,b))
        edges.append(dict(markers=[a,b],interface=points,maximum_ratio=float(ratios.max()),median_ratio=float(np.median(ratios)),short_interface=len(points)<3,dark_interface=dark,corridor=co,protected=block,affirmative_bright_connection=not block))
    for e in sorted(edges,key=lambda e:-e['maximum_ratio']):
        a,b=e['markers'];ra,rb=root(a),root(b);blocked=e['protected'] or any({root(x),root(y)}=={ra,rb} for x,y in forbidden);e['merge_blocked']=bool(blocked)
        if ra!=rb and not blocked:parent[rb]=ra
    group=[k for k in refs if root(k)==root(target)];owned=np.isin(labels,group);barrier=np.zeros_like(dm)
    for e in edges:
        a,b=e['markers'];e['separate_after_merging']=root(a)!=root(b)
        if e['separate_after_merging']:
            limit=.65*min(refs[a],refs[b])
            for x,y,qx,qy in e['interface']:
                if sm[y,x]<=limit:barrier[y,x]=True
                if sm[qy,qx]<=limit:barrier[qy,qx]=True
    mask=component(owned&~barrier,seed)
    return mask,dict(marker_ledger=ledger,target_marker=target,group=group,interfaces=edges,seam_pixels=int(barrier.sum()),short_dark_interfaces=sum(e['short_interface'] and e['dark_interface'] for e in edges),photographic_ownership='unknown; marker groups are not physical beads')

def infer(lum,hsv,paper,palette,bgh,color,**spec):
    args=(lum,hsv,paper,palette,bgh,color);f=field(*args,**spec);sm,pg,dm,seed=(f[k] for k in ('smooth','pigment','domain','seed'));w,wi=positive_watershed(f)
    sigma=spec.get('sigma',.65);bg=spec.get('bg_shift',0.);inner=[('baseline',{}),('sigma-low',dict(sigma=max(.2,sigma-.15))),('sigma-high',dict(sigma=sigma+.15)),('background-low',dict(bg_shift=bg-.02)),('background-high',dict(bg_shift=bg+.02))];masks=[];inner_info=[]
    for name,change in inner:
        ff=field(*args,**dict(spec,**change))
        if ff['seed'] is None:mm=np.zeros_like(ff['domain']);mi={}
        else:mm,mi,_=watershed_support(ff['smooth'],ff['pigment'],ff['domain'],ff['paper'],ff['seed'],False)
        masks.append(mm);y,x=np.where(mm);inner_info.append(dict(name=name,area=int(mm.sum()),pixels=np.c_[x,y].tolist(),field=ff['meta'],group=mi.get('group',[]),marker_ledger=mi.get('marker_ledger',[])))
    vote=np.mean(masks,axis=0);core=component(vote>=PARAMETERS['ensemble_core_fraction'],seed) if seed else np.zeros_like(dm);candidate=vote>=PARAMETERS['ensemble_extension_fraction'];routes=diffuse_routes(f['lum'],pg,core,candidate,f['meta']['diffuse_Y']);ext=np.zeros_like(dm)
    xy=np.array(routes.get('pixels',[]),int).reshape(-1,2)
    if len(xy):ext[xy[:,1],xy[:,0]]=True
    h,hi=restrict(f,w);e=component(core|ext,seed) if seed else core;cy,cx=np.where(core);ei=dict(core_pixels=np.c_[cx,cy].tolist(),core_area=int(core.sum()),extension_pixels=int((e&~core).sum()),routes=routes,ensemble=inner_info,frequency_kind='controlled parameter frequency, NOT ownership probability')
    return {name:(expand(mask,f),dict(f['meta'],**info,local_origin=f['origin'].tolist(),window_contact=int(mask[0].sum()+mask[-1].sum()+mask[:,0].sum()+mask[:,-1].sum()))) for name,mask,info in [('E',e,ei),('W',w,wi),('H',h,hi)]}
