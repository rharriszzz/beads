"""Remove only compact phase/station NUMERICAL rate veto for saved proposals.

Rigid separation, exact optics and geometric evidence remain mandatory. This
counterfactual distinguishes a regularization bound from physical impossibility.
"""
import numpy as np
from scipy.spatial import cKDTree
from photo2.r314.geometry import ShapeChain
from photo2.r315.model import bump
from photo2.r318 import optics
from photo2.r318.search import compact
from .experiment import GeneralChain
from .common import *
from .evidence import Evidence,gate

class RelaxedCompact(GeneralChain):
    def __init__(self,p,data):
        # Same shape/base chain and dynamically dispatched placements, skipping
        # ONLY R315's compact rate validation; repeat its translation exactly.
        ShapeChain.__init__(self,p,data)
        self.offset=self.offset+np.array(p.get('translation',[0.,0.]));self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)

def rates(p):
    k=np.linspace(-110,110,1761);eps=.001;cs=p['compact_centers'];pw=p['phase_halfwidth'];sw=p['spacing_halfwidth']
    ph=sum(a*(bump(k+eps,c,pw)-bump(k-eps,c,pw))/(2*eps) for c,a in zip(cs,p['compact_phase']))
    sp=sum(a*((k+eps-c)*bump(k+eps,c,sw)-(k-eps-c)*bump(k-eps,c,sw))/(2*eps) for c,a in zip(cs,p['compact_spacing']))
    return dict(phase_rate_fraction=float(np.max(abs(ph))/(2*np.pi/6.5)),spacing_rate_fraction=float(np.max(abs(sp))),phase_worst_address=float(k[np.argmax(abs(ph))]),spacing_worst_address=float(k[np.argmax(abs(sp))]))

def main():
    epoch=read(OLD/'epoch2/epoch.json');b=read(OUT/'baseline.json.gz');eng=optics.Engine(epoch);orig=eng.evaluate(b['parameters']);optics.Chain=RelaxedCompact;eng=optics.Engine(epoch);rr=eng.evaluate(b['parameters']);np.testing.assert_allclose(positions(rr),positions(orig),atol=1e-12,rtol=0)
    ev=Evidence(epoch);out=[]
    for name in ['contact-constrained-full','contact-constrained-small']:
        for step in read(OUT/(name+'.json.gz'))['steps']:
            old=read(OUT/'trials'/f'{step["trial"]:05}.json.gz')
            if old.get('reason')!='compact rate bound':continue
            ans=eng.evaluate(old['parameters'],True)
            if isinstance(ans,tuple):
                r,s,a=ans;r=compact(r);r['geometry']=ev.measure(s);r['acceptance']=gate(r['geometry'],b['geometry'])
            else:r=compact(ans)
            out.append(dict(parent_trial=old['id'],stage=name,parameters=old['parameters'],rates=rates(old['parameters']),predicted_max=step['predicted_max'],result=r,relaxed='Only compact phase/station 5%/2% exploratory rate veto; no contact/visibility/shape constraint relaxed.'))
            save(OUT/'relaxed-rate-controls.json.gz',out)
    save(OUT/'baseline-rate-audit.json',dict(rates=rates(b['parameters']),zero_geometry_exact=True))
    print('BOUND CONTROLS',[(r['parent_trial'],r['rates'],r['result'].get('emax_px'),r['result']['classification']) for r in out],flush=True)
if __name__=='__main__':main()
