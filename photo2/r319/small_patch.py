"""Controlled narrower basis test on frozen compact interval; all22 guards retained."""
import numpy as np
from scipy.optimize import lsq_linear
from photo2.r315.model import bump
from photo2.r297.geometry import periodic_field
from photo2.r318 import optics
from .experiment import Run
from .local_model import Chain
from .common import *
from .refine import minimax,metric
from .contact_fit import fit

def main():
    run=Run();run.rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];run.baseline=read(OUT/'baseline.json.gz');run.deadline=__import__('datetime').datetime(2026,10,18,2,59,7,tzinfo=__import__('datetime').timezone.utc).timestamp()
    chosen=read(OUT/'small-selection.json')['chosen'];p=deepcopy(run.baseline['parameters']);p.update(patch_centers=[33.,40.],patch_halfwidth=10.,patch_phase=[0.,0.],patch_spacing=[0.,0.],patch_tilt=[0.,0.],patch_cant=[0.,0.])
    # Establish a concrete spatial-support limitation before optical testing.
    k=np.linspace(-100,120,881);columns=[np.ones(len(k))]+[bump(k,c,p['phase_halfwidth']) for c in p['compact_centers']]
    for j in range(32):v=np.zeros(32);v[j]=1;columns.append(periodic_field(v,k/p['count']))
    A=np.stack(columns,axis=1);target=.08*bump(k,33,10);sol=lsq_linear(A,target,bounds=(-.45,.45),tol=1e-10,max_iter=200)
    save(OUT/'narrow-basis-justification.json',dict(addresses=k.tolist(),target=target.tolist(),old_basis_prediction=(A@sol.x).tolist(),maximum_residual_rad=float(abs(A@sol.x-target).max()),rms_residual_rad=float(np.sqrt(np.mean((A@sol.x-target)**2))),coefficients=sol.x.tolist(),policy='Representation control, not measured phase. A 20-address support can localize near conditional33 without altering observations40+; old basis limited to ±.45rad coefficients. Optical necessity tested below, never assumed.'))
    old=run.e.evaluate(run.baseline['parameters']);optics.Chain=Chain;run.e=optics.Engine(run.epoch);zero=run.e.evaluate(p);np.testing.assert_allclose(positions(old),positions(zero),atol=1e-10,rtol=0)
    globals=[v for v in variables(p) if isinstance(v['key'],str) and v['key'] in ['phase','s0','tilt','axial','radius','minor','elevation','roll','scale','light_az','light_el','roughness']]
    vs=[dict(key=[key,j],scale=h,unit=u,interpretation='two shared C2 compact fields of halfwidth10, not per-bead transforms') for key,h,u in [('patch_phase',.04,'rad'),('patch_spacing',.002,'fraction'),('patch_tilt',1,'deg'),('patch_cant',1,'deg inward')] for j in range(2)]+[dict(key=['translation',j],scale=1,unit='px',interpretation='global registration') for j in range(2)]+globals
    base,records,_,_=run.probe(p,vs,'narrow-patch');cols=[];gcols=[];selected=[]
    for r in records:
        if '1.0' not in r:continue
        j=np.array(r['1.0']['central'])
        if np.linalg.norm(j)<.1:continue
        a,b=[run.rows[r['trials'][str(f)]] for f in [-1.,1.]];cols.append(j);gcols.append((metric(b)-metric(a))/2);selected.append(vs[r['variable']])
    J=np.stack(cols,axis=2);G=np.stack(gcols,axis=1)
    minimax(run,base,selected,J,G,'narrow-patch-minimax',chosen['cohort'],True)
    # contact_fit resolves its constructor at module scope.
    from . import contact_fit
    contact_fit.GeneralChain=Chain
    fit(run,base,selected,J,G,'narrow-patch-contact',chosen['cohort'])
    good=[r for r in run.rows if run.usable(r) and r.get('acceptance',{}).get('passed')];best=min(good,key=lambda r:r['emax_px']);save(OUT/'best-full.json.gz',best)
    guarded=[r for r in good if r['emax_px']<=run.baseline['emax_px']+.05];small=min(guarded,key=lambda r:max(r['rows'][i]['error_px'] for i in chosen['cohort']));save(OUT/'best-small.json.gz',small)
    save(OUT/'narrow-summary.json',dict(utc=utc(),trials=len(run.rows),best_full=best['id'],best_small=small['id'],zero_exact=True))
    print('NARROW COMPLETE',len(run.rows),best['emax_px'],max(small['rows'][i]['error_px'] for i in chosen['cohort']),flush=True)
if __name__=='__main__':main()
