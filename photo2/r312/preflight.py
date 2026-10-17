"""Profile complete minimax evaluations and verify ROI/caching exactness."""
from pathlib import Path
from copy import deepcopy
import time
import numpy as np
from photo2.r297.common import ROOT,save,utc
from photo2.r309.render import predict
from photo2.r309.geometry import Chain as Previous
from .model import seeds
from .objective import Engine
from .profiling import Sampler

def run(out):
    records=[];checks=[]
    for stage in [1,2]:
        e=Engine(stage);p=seeds()[0]['parameters'];cal=e.evaluate(p)
        for finite in [False,True]:
            q=dict(p,light_inverse=.001 if finite else 0.)
            with Sampler() as sampler:
                for rep in range(3):
                    if rep==0:e.cache.clear()
                    r=e.evaluate(q,cal['mapping'],step=1.)
                    records.append(dict(stage=stage,finite=finite,repetition=rep,seconds=r['seconds'],profile=r['profile'],numerics=r['numerics']))
                    print('minimax benchmark',stage,finite,rep,round(r['seconds'],3),flush=True)
            save(Path(out)/f'minimax-samples-stage{stage}-finite{int(finite)}.json',sampler.result())
            old=Previous(q,e.data)
            owners=np.flatnonzero((old.indices>=-100)&(old.indices<=99)) if stage==1 else np.array(sorted({v-int(old.indices[0]) for v in cal['mapping'].values() if v is not None}),int)
            began=time.perf_counter();pred,meta=predict(old,1.,owners=owners);baseline_seconds=time.perf_counter()-began
            rr=e.records(pred,cal['mapping'])
            assert rr==r['reflections'],(stage,finite,'native ROI/cached predictor differs')
            coarse=e.evaluate(q,cal['mapping'],step=2.)
            delta=[abs(a['error_px']-b['error_px']) for a,b in zip(r['reflections'],coarse['reflections']) if a['error_px'] is not None and b['error_px'] is not None]
            checks.append(dict(stage=stage,finite=finite,exact_native_previous_predictions=True,original_compiled_optics_seconds=baseline_seconds,original_rays=meta['rays'],coarse_minus_native_max_px=coarse['metrics']['maximum_px']-r['metrics']['maximum_px'],coarse_per_observation_error_change_max_px=max(delta),coarse_missing=coarse['metrics']['missing'],native_missing=r['metrics']['missing']))
    save(Path(out)/'minimax-preflight.json',dict(utc=utc(),records=records,accuracy_checks=checks,passed=True))
    return records,checks

if __name__=='__main__':run(ROOT/'photo2/r312/results/campaign/profiling')
