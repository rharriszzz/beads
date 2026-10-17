"""Finite causal reversions, fixed-owner accounting, and untouched bright evidence."""
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read,save,utc
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r315.model import refined_trace
from . import search
from .model import Chain
from .search import OUT,SPLITS

def main():
    data=load()[0];e=engine();search.Chain=Chain;base=read(OUT/'R316-model.json.gz')['parameters'];p=read(OUT/'joint-preserved-model.json.gz')['parameters'];controls=[]
    groups={'shared_shape':['radius','axial','rounding','exterior','edge','face','bore'],'shared_orientation':['tilt','radial_cant'],'radial_cant':['radial_cant','compact_cant'],'local_phase':['compact_phase'],'local_station':['compact_spacing'],'local_orientation':['compact_tilt','compact_cant'],'registration_camera':['translation','elevation','roll','perspective']}
    for label,keys in groups.items():
        q=deepcopy(p)
        for k in keys:
            if k in base:
                q[k]=deepcopy(base[k])
                if k.startswith('compact_'):q[k]+= [0]*(len(q['compact_centers'])-len(q[k]))
            else:q.pop(k,None)
        try:r,s,tr=search.evaluate(q,data,e)
        except ValueError as ex:r=dict(parameters=q,feasible=False,classification='exploration-bound',reason=str(ex))
        if 'physical' in r:r['physical'].pop('witnesses',None)
        r['revert']=label;controls.append(r)
    save(OUT/'attribution.json',dict(utc=utc(),controls=controls,policy='Revert one declared parameter group to R316 while retaining the other optimized groups. Interactions make changes non-additive; contact-invalid reversions do not identify causal photographic preference. Fixed-R316-owner comparisons are independently retained for all 40 measured cores.'))
    epoch=read(ROOT/'photo2/r314/results/bright-epoch.json.gz');pred=[]
    for name in ['R316','hypothesis-A','hypothesis-B','hypothesis-C','joint-preserved']:
        s=Chain(read(OUT/f'{name}-model.json.gz')['parameters'],data);xy=np.array([o['peak'] for o in epoch['observations']]);tr=refined_trace(s,xy)
        pred.append(dict(name=name,observations=[dict(id=o['id'],peak=o['peak'],conditional_first_hit_index=int(s.indices[j]) if j>=0 else None,unknown=bool(u),reliable_correspondence=False) for o,j,u in zip(epoch['observations'],tr['owner'],tr['unknown'])]))
    save(OUT/'bright-geometric-owners.json.gz',dict(models=pred,policy='Geometric first hit at an observed bright peak, including black-bead features. This is not a corresponding predicted specular peak; no nearest-optical assignment and no peak Emax claimed.'))
if __name__=='__main__':main()
