"""Separate shared-profile and discrete-family controls; never mixed into primary epoch."""
import time
from copy import deepcopy
from .experiment import GeneralChain
from photo2.r318 import optics
from photo2.r318.search import compact
from .common import *
from .evidence import Evidence,gate

def main():
    epoch=read(OLD/'epoch2/epoch.json');p=read(OLD/'epoch2/best.json.gz')['parameters'];p.update(hole=.14,rounding=.8);engine=optics.Engine(epoch);ev=Evidence(epoch);baseline=read(OUT/'baseline.json.gz');rows=[]
    def trial(q,stage,meta):
        t=time.time()
        try:
            ans=engine.evaluate(q,True)
            if isinstance(ans,tuple):
                r,s,a=ans;r=compact(r);r['geometry']=ev.measure(s);r['acceptance']=gate(r['geometry'],baseline['geometry'])
            else:r=compact(ans)
        except (ValueError,AssertionError) as ex:r=dict(feasible=False,classification='model-bound',reason=str(ex))
        r.update(parameters=q,stage=stage,meta=meta,seconds=time.time()-t);rows.append(r);save(OUT/'profile-discrete-controls.json.gz',rows);print(stage,meta,r.get('emax_px'),r.get('classification'),flush=True)
    for key,h in [('hole',.02),('rounding',.04)]:
        for f in [-1.,-.25,.25,1.]:trial(change(p,key,h*f),'legacy-profile',dict(key=key,delta=h*f))
    q=deepcopy(p);q.update(exterior=True,edge=.344,face=.8,bore=.14);trial(q,'independent-exterior-parent',{})
    for key,h in [('edge',.04),('face',.04),('bore',.02)]:
        for f in [-1.,-.25,.25,1.]:trial(change(q,key,h*f),'independent-exterior',dict(key=key,delta=h*f,parent='independent-exterior-parent'))
    for d in [-13,-1,1,13]:
        q=deepcopy(p);q['count']+=d;trial(q,'count-control',dict(delta=d,map='same conditional22; no identity proof'))
    q=deepcopy(p);q['hand']=1;trial(q,'opposite-hand',dict(rephased=False,limitation='direct control only; does not rule out refitted opposite-hand families'))
    q=deepcopy(p);q['topology']='closed';trial(q,'closed-topology',dict(winding=q['winding']))
    for d in [-.01,.01]:trial(change(p,'seam_fraction',d),'open-end-storage-control',dict(delta=d))
if __name__=='__main__':main()
