"""Conjunctive geometry acceptance; scalar search merit cannot waive a gate."""
import numpy as np
from photo2.r313.objective_v2 import SurfaceObjective
from photo2.r313.objective import boundaries,distances,stats

class Objective(SurfaceObjective):
    def measure(self,owner,unknown,indices,split=0,detail=False):
        r=super().measure(owner,unknown,indices,split,True)
        own=np.asarray(owner).reshape(self.shape);un=np.asarray(unknown).reshape(self.shape)
        # Only foreground/background changes can explain supported material/paper rims.
        ext=boundaries(np.where(own>=0,0,-1),un)
        dd=np.array([distances(e) for e in ext]);valid=self.m['roi']&(self.m['split']==split)
        r['external_transition']=stats(dd[self.m['external']&valid[None]])
        r['vector']=dict(omission=r['material_unexplained_percent'],paper=r['background_intrusion_percent'],ownership=100-r['modal_ownership_percent'],external=r['external_transition']['p95_px'] or 0.,seam=r['seam_same_owner_percent'],worst=r['owner_specific_terms']['worst_core_p95_px'])
        # Fixed engineering target scales; maximum, never weighted coverage compensation.
        r['search_merit']=max(v/t for v,t in zip(r['vector'].values(),[5.,.5,20.,3.,10.,3.]))
        r['absolute_failures']=absolute_failures(r)
        if not detail:
            for k in ['regions','worst_cores','owner_specific_cores']:r.pop(k,None)
        return r

def absolute_failures(r):
    v=r['vector'];limits=dict(omission=5.,paper=.5,ownership=20.,external=3.,seam=10.,worst=3.)
    fails=[k for k in limits if v[k]>limits[k]+1e-10]
    if any(c['modal_fraction']<.8 for c in r['cores']):fails.append('individual_core')
    if r['unknown_rays']:fails.append('unknown_rays')
    if not r['external_transition']['n']:fails.append('no_external_evidence')
    return fails

def acceptance(candidate,baseline):
    a=candidate['vector'];b=baseline['vector'];fail=[]
    for k in ['paper','external','seam','worst']:
        if a[k]>b[k]+1e-10:fail.append(k)
    if a['omission']>b['omission']-1:fail.append('material_improvement')
    if a['ownership']>b['ownership']-1:fail.append('ownership_improvement')
    before={c['id']:c for c in baseline['cores']}
    for c in candidate['cores']:
        if c['modal_fraction']<before[c['id']]['modal_fraction']-.02-1e-10:fail.append('core:'+c['id'])
    return dict(passed=not fail,failures=fail)

def dominates(a,b):
    x=np.array(list(a['vector'].values()));y=np.array(list(b['vector'].values()))
    return bool(np.all(x<=y+1e-10) and np.any(x<y-1e-10))
