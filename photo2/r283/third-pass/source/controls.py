"""Post-freeze local camera/phase and wrong-neighbor diagnostics; never refit."""
from copy import deepcopy
import numpy as np
from .common import OUT,read,save,pixels,sha
from .local import LOCAL,trace,light_evidence

def main():
    freeze=read(LOCAL/'prediction-freeze.json');evals=read(LOCAL/'evaluation.json')['results'];held=read(LOCAL/'withheld.json')['records'];results=[]
    for m,e in zip(freeze['models'],evals):
        mapping=[r['assigned_model_index'] for r in e['withheld']]
        for kind,key,delta in [('baseline',None,0),('inclination-minus5','inclination',-5),('inclination-plus5','inclination',5),
            ('phase-minus.2','phase',-.2),('phase-plus.2','phase',.2),('roll-minus3','roll',-3),('roll-plus3','roll',3)]:
            p=deepcopy(m['parameters'])
            if key:p[key]+=delta
            fractions=[]
            for r,k in zip(held,mapping):
                owner,_,u=trace(p,pixels(r['measured_support']));fractions.append(float(np.mean(owner==k)) if k!=-999 else 0.)
            le=light_evidence(p,held,mapping);angles=[float(np.degrees(np.arccos(np.clip(np.dot(v['direction'],m['light']['direction']),-1,1)))) for v in le if v['usable'] and v['color']=='yellow']
            results.append(dict(model=m['id'],kind=kind,fractions=fractions,mean=float(np.mean(fractions)),
                yellow_count=len(angles),yellow_median_angle=float(np.median(angles)) if angles else None))
        for shift in (-7,-6,-1,1,6,7):
            fractions=[]
            for r,k in zip(held,mapping):
                owner,_,_=trace(m['parameters'],pixels(r['measured_support']));fractions.append(float(np.mean(owner==k+shift)) if k!=-999 else 0.)
            results.append(dict(model=m['id'],kind=f'wrong-neighbor-label-{shift:+}',fractions=fractions,mean=float(np.mean(fractions))))
    save(LOCAL/'controls.json',dict(results=results,prediction_freeze_sha256=sha(LOCAL/'prediction-freeze.json'),
        limitation='Fixed correspondence stress tests; not a proof of real identity. No test changes pose, labels or measurements upstream.'))

if __name__=='__main__':main()
