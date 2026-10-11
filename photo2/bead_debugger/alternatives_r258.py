"""Equal-budget count/hand screens; no historical labels or remapped bead2."""
import copy,json,time
import numpy as np
from .refit import OUT,ROOT,initialize,BeadCurve,SurfaceLoss,fit,audit,physical
from .generate import save

def run():
    results=[]
    # N is explicit throughout; these are hypotheses, not optimized labels.
    for n in [2674,2681,2696,2700]:
        for h in [-1,1]:
            for name,k in [('origin',2),('straight-black',370),('bend',1695),('opposite',1100)]:
                ev=json.loads((OUT/(name+'-evidence.json')).read_text());rows=copy.deepcopy(ev['observations'])
                for r in rows:r['identity']=None # old k2 is not an established alternative-model index
                loss=SurfaceLoss(ev['box'],rows);c=initialize(n,h);c['phase_harmonics']=[0]*4;c['freeze_B_curve']=False
                t=((2162+k)%2696)/2696
                # Equal eight phase seeds; selection uses training only.
                seeds=[]
                for phase in np.arange(8)*2*np.pi/8:
                    cc=copy.deepcopy(c);cc['phase']=float(phase);seeds.append((loss.evaluate(BeadCurve(cc)),cc))
                c=min(seeds,key=lambda a:a[0])[1];found,log=fit(c,t,loss,'D',220);measured=audit(found,loss)
                mid=f'R258_alt_N{n}_h{h:+d}_{name}';found['id']=mid;found['section']=name;found['box']=ev['box'];save(OUT/(mid+'.json'),found)
                results.append(dict(id=mid,n=n,h=h,section=name,phase_starts=8,**log,**measured));save(OUT/'alternatives.json',results)
                print(mid,measured['metrics']['train']['ownership_mean'],measured['metrics']['holdout-body']['ownership_mean'],flush=True)
    ids=json.loads((OUT/'model-index.json').read_text());ids.extend(r['id'] for r in results if r['section']=='origin');save(OUT/'model-index.json',list(dict.fromkeys(ids)))
if __name__=='__main__':run()
