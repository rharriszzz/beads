"""Reproducible warm and cold subsystem timings, exact output comparisons."""
from pathlib import Path
import time, types
import numpy as np
from photo2.r297.common import ROOT,save,utc,environment
from photo2.r306.evidence import load
from photo2.r311.model import starts
from photo2.r309.geometry import Chain as Previous
from photo2.r306.geometry import Chain as PythonOriginal
from photo2.r299.forward import Surface
from photo2.r309.render import predict
from photo2.r309.measure import Measures
from .fast import Chain
from .profiling import Sampler,Timers

def run(out,repetitions=3):
    out=Path(out);data,m,obs=load();p=starts()[1]['parameters'];records=[];checks=[]
    for finite in [False,True]:
        q=dict(p,light_inverse=.001 if finite else 0.)
        for stage in ['200','whole']:
            saved={}
            with Sampler() as sampler:
                for label,cls in [('baseline',Previous),('optimized',Chain)]:
                    for rep in range(repetitions):
                        timer=Timers();began=time.perf_counter()
                        with timer.span('positions_orientations'):s=cls(q,data)
                        timer.bind(s)
                        with timer.span('contact'):cert=s.certify(witnesses=True)
                        owners=np.flatnonzero((s.indices>=-100)&(s.indices<=99)) if stage=='200' else np.arange(s.n)
                        with timer.span('reflection_assembly_and_shading'):pred,meta=predict(s,2.,owners=owners)
                        record=dict(label=label,finite=finite,stage=stage,repetition=rep,wall_seconds=time.perf_counter()-began,profile=timer.result(),rays=meta['rays'],predictions=len(pred),certified=cert['certified'])
                        records.append(record);print('benchmark',label,finite,stage,rep,round(record['wall_seconds'],3),flush=True)
                        if rep==0:saved[label]=(s,pred,meta,cert)
            save(out/f'samples-{stage}-finite{int(finite)}.json',sampler.result())
            a,pa,ma,ca=saved['baseline'];b,pb,mb,cb=saved['optimized']
            np.testing.assert_allclose(a.centers,b.centers,atol=0,rtol=0)
            assert pa==pb and ma==mb,(stage,finite,'native optical mismatch')
            assert ca['certified']==cb['certified']
            for w in cb['witnesses']:
                j,k=w['pair'];n=np.array(w['normal'])
                gap=(a.centers[k]-a.centers[j])@n-a.support(n,a.g['surface_tangent'][j])-a.support(n,a.g['surface_tangent'][k])
                assert gap>1e-6 and abs(gap-w['gap_units'])<1e-10
            # Literal Python camera and shadow marcher, independently of C++.
            old=Previous(q,data);old.trace=types.MethodType(PythonOriginal.trace,old);old.blocked=types.MethodType(Surface.blocked,old)
            selected=owners[::max(1,len(owners)//8)]
            fp,fm=predict(Chain(q,data),1.,owners=selected);sp,sm=predict(old,1.,owners=selected)
            assert {r['index'] for r in fp}=={r['index'] for r in sp}
            maxdiff=0.
            for x,y in zip(fp,sp):
                diff=float(np.linalg.norm(np.array(x['point'])-y['point']));maxdiff=max(maxdiff,diff)
                np.testing.assert_allclose(x['point'],y['point'],atol=1e-9,rtol=0)
            checks.append(dict(stage=stage,finite=finite,exact_baseline_predictions=True,exact_camera_and_shadow_counts=True,all_contact_witnesses_recomputed=True,python_original_rays=sm['rays'],maximum_python_centroid_difference_px=maxdiff))
    # Existing complete photographic objective, before any minimax changes.
    objective=Measures(data,m,obs);full=[]
    for label,cls in [('baseline',Previous),('optimized',Chain)]:
        t=time.perf_counter();r=objective.evaluate(cls(p,data),step=2.)
        full.append(dict(label=label,seconds=time.perf_counter()-t,metrics=r['metrics'],scores=r['scores'],rays=r['rays']))
    assert full[0]['metrics']==full[1]['metrics'] and full[0]['scores']==full[1]['scores']
    result=dict(utc=utc(),environment=environment(),records=records,accuracy_checks=checks,existing_full_objective=full,policy='Same annulus, lattice, native marcher, centroid rule, all bodies and shadows; speed measurements exclude sampling and independent Python audits.')
    save(out/'baseline.json',result);return result
