"""Native visible principal lobes, complete-chain shadows, exact frozen minimax."""
from collections import OrderedDict
import time
import numpy as np
from photo2.r297.common import ROOT,read,digest
from photo2.r306.evidence import load
from photo2.r317.model import Chain as Previous
from photo2.r312.fast import Chain as Shadow
from photo2.r295.geometry import AXES,unit
from photo2.r314.geometry import contacts
from photo2.r315.model import refined_trace
from photo2.r307.fast import grid
from photo2.r299.forward import shade,light_params
from .detect import principal

LIGHT_KEYS={'light_az','light_el','roughness','light_inverse','light_width'}

def make_light(p,s):
    inv=p.get('light_inverse',0.)
    width=p.get('light_width',0.)
    if width:
        if inv:raise ValueError('Extended directional and finite point sources are separate hypotheses')
        return light_params([p['light_az'],p['light_el'],p['roughness'],width],'extended',s.centers.mean(0))
    values=[p['light_az'],p['light_el'],p['roughness']]+([1/inv] if inv else [])
    return light_params(values,'finite' if inv else 'directional',s.centers.mean(0))

class Chain(Previous):
    def blocked(self,points,direction,max_distance=np.inf):
        # Literal R312 kernel is exact for this epoch's fixed legacy profile.
        assert not self.exterior and self.hole==.14 and self.rounding==.8
        return Shadow.blocked(self,points,direction,max_distance)
    def camera(self,xy):
        xy=np.asarray(xy);tr=refined_trace(self,xy);tr['normal']=np.zeros((len(xy),3))
        ok=tr['owner']>=0;j=tr['owner'][ok];delta=tr['points'][ok]-self.centers[j]
        axes=[self.g[k][j] for k in AXES];q=np.stack([np.sum(delta*a,axis=1) for a in axes],axis=1);eps=1e-5
        grad=np.stack([(self.local_sdf(q+np.eye(3)[i]*eps)-self.local_sdf(q-np.eye(3)[i]*eps))/(2*eps) for i in range(3)],axis=1)
        n=unit(grad);tr['normal'][ok]=sum(n[:,i,None]*a for i,a in enumerate(axes));tr['xy']=xy
        tr['viewer']=unit(self.distance*self.eye-tr['points']) if np.isfinite(self.distance) else np.tile(self.eye,(len(xy),1))
        return tr

class Engine:
    def __init__(self,epoch):
        self.data=load()[0];self.epoch=epoch;self.obs=epoch['observations'];self.cache=OrderedDict()
        self.binding=digest(dict(observations=self.obs,mapping=epoch['mapping'],method=epoch['method']))
        if self.binding!=epoch['binding']:raise ValueError('Frozen epoch changed; a separate epoch is required')
        if set(epoch['mapping'])!={o['id'] for o in self.obs} or len(set(epoch['mapping'].values()))!=len(self.obs):raise ValueError('Cohort/map must be complete and one-to-one')
    def evaluate(self,p,detail=False):
        began=time.monotonic()
        assert self.binding==digest(dict(observations=self.epoch['observations'],mapping=self.epoch['mapping'],method=self.epoch['method']))
        key=digest({k:v for k,v in p.items() if k not in LIGHT_KEYS});reused=key in self.cache
        if reused:item=self.cache.pop(key);self.cache[key]=item;s=item['scene'];s.p=p
        else:
            s=Chain(p,self.data);cert=contacts(s,seconds=.3)
            if not cert['certified']:
                cert.pop('witnesses',None)
                return dict(feasible=False,classification=cert['classification'],physical=cert,seconds=time.monotonic()-began)
            js=np.array([np.flatnonzero(s.indices==i)[0] for i in self.epoch['mapping'].values()],int)
            xy=grid(s,1.,js);tr=s.camera(xy)
            if tr['unknown'].any():return dict(feasible=False,classification='unresolved-camera-rays',unknown=int(tr['unknown'].sum()),seconds=time.monotonic()-began)
            cert.pop('witnesses',None);item=dict(scene=s,xy=xy,tr=tr,physical=cert,js=js)
            self.cache[key]=item
            while len(self.cache)>3:self.cache.popitem(last=False)
        light=make_light(p,s)
        sh=shade(s,item['tr'],light);pred={};xy=item['xy'];tr=item['tr']
        for j in item['js']:
            ix=tr['owner']==j;h=principal(xy[ix],sh['intensity'][ix])
            if h:pred[int(s.indices[j])]=h
        rows=[]
        for o in self.obs:
            idx=self.epoch['mapping'][o['id']];h=pred.get(idx);point=h['point'] if h else None
            error=float(np.linalg.norm(np.array(point)-o['point'])) if h else None
            rows.append(dict(id=o['id'],index=idx,observed=o['point'],predicted=point,error_px=error,
                             predicted_lobe=h,localization_uncertainty_px=o['uncertainty_px'],
                             correspondence_confidence=o['correspondence_confidence'],color=o['color']))
        errors=[r['error_px'] for r in rows if r['error_px'] is not None];missing=sum(r['error_px'] is None for r in rows)
        result=dict(feasible=True,classification='certified-separation',physical=item['physical'],
                    emax_px=max(errors) if errors and not missing else None,maximum_is_infinite=bool(missing),
                    rms_px=float(np.sqrt(np.mean(np.square(errors)))) if errors else None,
                    median_px=float(np.median(errors)) if errors else None,missing=missing,rows=rows,
                    rays=len(xy),unknown_shadow_pairs=sh['unknown_shadow_pairs'],camera_reused=reused,
                    seconds=time.monotonic()-began)
        if detail:return result,s,dict(xy=xy,owner=tr['owner'],intensity=sh['intensity'],unknown=tr['unknown'],points=tr['points'],normal=tr['normal'],viewer=tr['viewer'])
        return result

def objective(r):
    if not r.get('feasible'):return 1e6
    if r.get('missing'):return 1e5+1000*r['missing']
    return r['emax_px']
