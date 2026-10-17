"""Fixed observations/conditional owners, Euclidean minimax and photographic guards.

No correspondence is removed or changed during either search. Initial association
is one-to-one bottleneck matching, then frozen per count/hand/topology family.
Ambiguous strong observations remain in the maximum. Weak observations remain in
the evidence catalog and are diagnosed separately; physical identity is unknown.
"""
from collections import OrderedDict
from copy import deepcopy
import time
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
from scipy.spatial import cKDTree
from scipy.ndimage import binary_erosion,binary_dilation,binary_fill_holes
from matplotlib.path import Path as Polygon
from photo2.r297.common import ROOT,read,pixels,digest
from photo2.r297.geometry import reference
from photo2.r306.evidence import load
from photo2.r309.structural import sample
from photo2.r307.fast import grid
from photo2.r299.forward import shade,light_params,highlight
from .model import scene,geometry_key
from .profiling import Timers

MISSING=10000. # Exceeds the image diagonal; no missing reflection earns improvement.

def bottleneck(observations,predictions,reserved=None):
    """Exact discrete minimax one-to-one assignment, Euclidean tie break."""
    reserved=reserved or {};used={v for v in reserved.values() if v is not None}
    oo=[o for o in observations if o['id'] not in reserved];pp=[p for p in predictions if p['index'] not in used]
    result=dict(reserved)
    if not oo:return result
    if not pp:return dict(result,**{o['id']:None for o in oo})
    cost=np.linalg.norm(np.array([o['point'] for o in oo])[:,None]-np.array([p['point'] for p in pp])[None],axis=2)
    # Dummy vertices expose missing observations without discarding them.
    matrix=np.c_[cost,np.full((len(oo),len(oo)),MISSING)]
    levels=np.unique(matrix);lo=-1;hi=len(levels)-1
    while hi-lo>1:
        mid=(lo+hi)//2
        match=maximum_bipartite_matching(csr_matrix(matrix<=levels[mid]),perm_type='column')
        if (match>=0).all():hi=mid
        else:lo=mid
    allowed=matrix<=levels[hi]
    ii,jj=linear_sum_assignment(np.where(allowed,matrix,1e12))
    for i,j in zip(ii,jj):result[oo[i]['id']]=pp[j]['index'] if j<len(pp) else None
    return result

def statistics(rows):
    errors=[r['error_px'] for r in rows if r['error_px'] is not None]
    missing=sum(r['error_px'] is None for r in rows)
    return dict(observations=len(rows),measured=len(errors),missing=missing,
                maximum_px=float(max(errors)) if errors else None,
                rms_px=float(np.sqrt(np.mean(np.square(errors)))) if errors else None,
                p95_px=float(np.percentile(errors,95)) if errors else None,
                objective_px=float(MISSING*missing+max(errors,default=0.)),
                identity_status='All bead identities are conditional, including initially unambiguous associations')

def cohort(data,observations):
    old=read(ROOT/'photo2/r311/results/campaign/metrics/R306-2405-baseline.json.gz')
    refs=sum([v['reflections'] for v in old['detail'].values()],[])
    selected={r['id'] for r in refs if r['index'] is not None and -100<=r['index']<=99}
    return [o for o in observations if o['id'] in selected]

class Engine:
    def __init__(self,stage,dense=False):
        self.stage=stage;self.dense=dense;self.data,self.m,self.allobs=load()
        self.local=cohort(self.data,self.allobs)
        self.obs=self.local if stage==1 else [o for o in self.allobs if o['strong']]
        from photo2.r311.model import starts
        base=scene(starts()[1]['parameters'],self.data)
        self.region_centers=base.pc[(base.indices>=-100)&(base.indices<=99)]
        self.localtree=cKDTree(self.region_centers)
        self.regions=[r for r in self.data['rows'] if r['kind']=='region' and not r['reflection'] and (stage==2 or self.in_roi([r['point']])[0])]
        self.parts=[pixels(r['pixels']) if dense else sample(pixels(r['pixels']),128) for r in self.regions]
        self.bounds=np.r_[0,np.cumsum([len(v) for v in self.parts])]
        raw=np.load(ROOT/'photo2/r296/evidence/cues.npz');keep=np.ones(len(raw['xy']),bool)
        if stage==1:keep&=self.in_roi(raw['xy'])
        if not dense:keep&=np.arange(len(keep))%2==0
        self.cues={k:raw[k][keep] for k in ['xy','paper','color','station']}
        self.contours=[]
        for r in self.m['beads']:
            if stage==1 and not self.in_roi([r['point']])[0]:continue
            p=np.array(r['polygon']);lo=np.floor(p.min(0)-20).astype(int);hi=np.ceil(p.max(0)+20).astype(int)
            step=1 if dense else 2;yy,xx=np.mgrid[lo[1]:hi[1]+1:step,lo[0]:hi[0]+1:step];xy=np.c_[xx.ravel(),yy.ravel()]
            inside=Polygon(p).contains_points(xy,radius=.01).reshape(xx.shape)
            self.contours.append(dict(id=r['id'],xy=xy,inside=inside,shape=xx.shape,step=step))
        self.xy=np.concatenate(self.parts+[self.cues['xy']]+[r['xy'] for r in self.contours])
        ref=reference();self.tangents={}
        for o in self.allobs:
            arc=(o['arc']+np.array([-1,1]))%ref.length
            pp=np.array([[np.interp(a,ref.arc,ref.points[:,k]) for k in range(2)] for a in arc])
            t=pp[1]-pp[0];self.tangents[o['id']]=t/np.linalg.norm(t)
        self.cache=OrderedDict();self.contact_cache={}
    def in_roi(self,xy):return self.localtree.query(xy)[0]<=65.
    def geometry(self,p,timer):
        key=geometry_key(p)
        if key in self.cache:
            item=self.cache.pop(key);self.cache[key]=item;item['scene'].p=p
            timer.bind(item['scene'])
            return item,True
        with timer.span('positions_orientations'):s=scene(p,self.data)
        timer.bind(s)
        contact_reused=key in self.contact_cache
        with timer.span('contact'):
            if contact_reused:cert=self.contact_cache[key]
            else:
                cert=s.certify(iterations=100,witnesses=False)
                if not cert['certified']:cert=s.certify(iterations=220,witnesses=False)
                self.contact_cache[key]=cert
        item=dict(scene=s,cert=cert,camera={},trace=None,contact_reused=contact_reused)
        # Bound retained camera buffers; no cross-candidate approximate geometry.
        self.cache[key]=item
        while len(self.cache)>2:
            _,old=self.cache.popitem(last=False)
            for attr in ['trace','blocked','camera','_r312_originals']:
                if attr in old['scene'].__dict__:delattr(old['scene'],attr)
        return item,False
    def optics(self,item,owners,step,timer):
        s=item['scene'];key=digest(dict(owners=owners.tolist(),step=step))
        reused=key in item['camera']
        if reused:xy,tr,order,cuts=item['camera'][key]
        else:
            with timer.span('outline_lattice'):
                xy=grid(s,step,owners)
                if len(xy)>2500000:raise ValueError('Numerical resource limit: >2.5M camera samples')
            tr=s.camera(xy)
            with timer.span('reflection_grouping'):
                order=np.argsort(tr['owner'],kind='stable');cuts=np.r_[0,np.flatnonzero(np.diff(tr['owner'][order]))+1,len(order)]
            item['camera'][key]=(xy,tr,order,cuts)
            while len(item['camera'])>2:item['camera'].pop(next(iter(item['camera'])))
        inv=s.p.get('light_inverse',0.);v=[s.p['light_az'],s.p['light_el'],s.p['roughness']]+([1/inv] if inv else [])
        light=light_params(v,'finite' if inv else 'directional',s.centers.mean(0))
        with timer.span('reflection_shading'):sh=shade(s,tr,light)
        with timer.span('reflection_centroids'):
            pred=[];allowed=set(owners);weight=sh['intensity']
            for a,b in zip(cuts[:-1],cuts[1:]):
                ix=order[a:b]
                if not len(ix):continue
                j=int(tr['owner'][ix[0]])
                if j<0 or j not in allowed:continue
                h=highlight(xy[ix],weight[ix],step)
                if h:pred.append(dict(index=int(s.indices[j]),point=h['centroid'],strength=h['peak_intensity'],area_px2=h['area_px2']))
        return pred,dict(rays=len(xy),camera_reused=reused,unknown_camera=int(tr['unknown'].sum()),unknown_shadow=sh['unknown_shadow_pairs'],step=step)
    def evaluate(self,p,mapping=None,step=1.,monitor=True,initial=False):
        began=time.perf_counter();timer=Timers();item,geometry_reused=self.geometry(p,timer);s=item['scene'];cert=item['cert']
        result=dict(physical=cert,feasible=cert['certified'],geometry_reused=geometry_reused,contact_reused=geometry_reused or item.get('contact_reused',False))
        if cert['certified']:
            # Every physical body remains in the scene and all ray/contact tests.
            if self.stage==1:owners=np.flatnonzero((s.indices>=-100)&(s.indices<=99))
            elif mapping is not None:owners=np.array(sorted({k-int(s.indices[0]) for k in mapping.values() if k is not None}),int)
            else:owners=np.array(sorted({j for z in s.tree.query_ball_point([o['point'] for o in self.obs],60.) for j in z}),int)
            pred,meta=self.optics(item,owners,step,timer)
            with timer.span('correspondence_objective'):
                if mapping is None:mapping=bottleneck(self.obs,pred)
                records=self.records(pred,mapping)
                result.update(metrics=statistics(records),reflections=records,numerics=meta,mapping=mapping)
            if monitor:
                if item['trace'] is None:item['trace']=s.trace(self.xy)
                with timer.span('visible_outlines_and_safeguards'):result['safeguards']=self.safeguards(item['trace'],s)
        result.update(seconds=time.perf_counter()-began,profile=timer.result())
        return result
    def records(self,pred,mapping):
        byindex={r['index']:r for r in pred};records=[]
        points=np.array([p['point'] for p in pred],float).reshape(-1,2)
        observed=np.array([o['point'] for o in self.obs],float).reshape(-1,2)
        distances=np.linalg.norm(points[None]-observed[:,None],axis=2)
        closest=np.argsort(distances,axis=1,kind='stable')[:,:4]
        for i,o in enumerate(self.obs):
            idx=mapping.get(o['id']);p=byindex.get(idx);x=np.array(o['point']);d=np.array(p['point'])-x if p else None;t=self.tangents[o['id']]
            alt=[dict(index=pred[j]['index'],distance_px=float(distances[i,j])) for j in closest[i]]
            ambiguous=len(alt)>1 and alt[1]['distance_px']-alt[0]['distance_px']<3
            records.append(dict(id=o['id'],observed=o['point'],predicted=p['point'] if p else None,index=idx,
                error_px=float(np.linalg.norm(d)) if p else None,dx_px=float(d[0]) if p else None,dy_px=float(d[1]) if p else None,
                tangent_px=float(d@t) if p else None,normal_px=float(d@[-t[1],t[0]]) if p else None,
                color=o['color'],strong=o['strong'],section=o['section'],arc=o['arc'],ambiguous=ambiguous,
                alternatives=alt,physical_identity_verified=False))
        return records
    def safeguards(self,tr,s):
        own=tr['owner'];unknown=tr['unknown'];support=[]
        for r,a,b in zip(self.regions,self.bounds[:-1],self.bounds[1:]):
            o=own[a:b];ii,c=np.unique(o[o>=0],return_counts=True);j=int(ii[c.argmax()]) if len(c) else -1
            support.append(dict(id=r['id'],point=r['point'],modal_fraction=float(c.max()/(b-a)) if len(c) else 0.,missing=float(np.mean(o<0)),index=int(s.indices[j]) if j>=0 else None))
        start=int(self.bounds[-1]);n=len(self.cues['xy']);o=own[start:start+n];un=unknown[start:start+n];start+=n
        paper=self.cues['paper'];color=self.cues['color']>0
        boundary=[];boundary_missing=0
        for c in self.contours:
            n=len(c['xy']);o=own[start:start+n];un=unknown[start:start+n].reshape(c['shape']);start+=n
            ii,count=np.unique(o[c['inside'].ravel()&(o>=0)],return_counts=True)
            j=int(ii[count.argmax()]) if len(count) else -2
            mask=(o==j).reshape(c['shape']);filled=binary_fill_holes(mask)
            edge=filled&~binary_erosion(filled)&~binary_dilation(un)
            observed=c['inside']&~binary_erosion(c['inside']);a=c['xy'][edge.ravel()];b=c['xy'][observed.ravel()]
            if len(a) and len(b):
                errors=np.r_[cKDTree(a).query(b)[0],cKDTree(b).query(a)[0]]
                boundary.append(dict(id=c['id'],rms_px=float(np.sqrt(np.mean(errors**2))),maximum_px=float(errors.max()),count=len(errors)))
            else:boundary_missing+=1;boundary.append(dict(id=c['id'],rms_px=100.,maximum_px=100.,count=1))
        return dict(ownership_percent=100*float(np.mean([r['modal_fraction'] for r in support])),
                    background_percent=100*float(np.mean((own[int(self.bounds[-1]):int(self.bounds[-1])+len(paper)][paper]>=0)|unknown[int(self.bounds[-1]):int(self.bounds[-1])+len(paper)][paper])) if paper.any() else 0.,
                    omission_percent=100*float(np.mean(own[int(self.bounds[-1]):int(self.bounds[-1])+len(color)][color]<0)) if color.any() else 0.,
                    boundary_rms_px=float(np.sqrt(np.average([r['rms_px']**2 for r in boundary],weights=[r['count'] for r in boundary]))) if boundary else 0.,
                    boundary_missing=boundary_missing,supports=support,boundaries=boundary,unknown_rays=int(unknown.sum()),boundary_policy='Supported exterior contours only; unannotated internal holes excluded from score, retained in native overlays')

def guard(result,baseline):
    if not result.get('feasible'):return False
    a=result['safeguards'];b=baseline['safeguards']
    return (a['ownership_percent']>=b['ownership_percent']-2. and a['background_percent']<=b['background_percent']+1.
            and a['omission_percent']<=b['omission_percent']+2. and a['boundary_rms_px']<=b['boundary_rms_px']+1.
            and a['boundary_missing']<=b['boundary_missing'])

def violation(result,baseline):
    if not result.get('feasible'):return 1e6
    a=result['safeguards'];b=baseline['safeguards']
    return float(sum([max(0,b['ownership_percent']-2-a['ownership_percent']),
        max(0,a['background_percent']-b['background_percent']-1),
        max(0,a['omission_percent']-b['omission_percent']-2),
        max(0,a['boundary_rms_px']-b['boundary_rms_px']-1),
        10*max(0,a['boundary_missing']-b['boundary_missing'])]))
