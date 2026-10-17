"""Measured Stage 2 improvements against the archived Stage 1 objective."""
import importlib.util,tarfile,tempfile,time
from pathlib import Path
import numpy as np
from photo2.r297.common import ROOT,read,save,utc
from .objective import Engine
from .model import seeds
from .profiling import Timers

def run():
    with tarfile.open(ROOT/'photo2/r312/evidence/stage1-source/source.tar.gz','r:gz') as archive:
        source=archive.extractfile('photo2/r312/objective.py').read()
    path=Path(tempfile.mkdtemp(prefix='beads-r312-old-objective-'))/'objective.py';path.write_bytes(source)
    spec=importlib.util.spec_from_file_location('photo2.r312._stage1_objective',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    p=seeds()[0]['parameters'];engine=Engine(2);cal=engine.evaluate(p)
    item,_=engine.geometry(p,Timers());s=item['scene'];owners=np.array(sorted({v-int(s.indices[0]) for v in cal['mapping'].values() if v is not None}),int)
    pred,_=engine.optics(item,owners,1.,Timers());before=old.Engine(2);matching={}
    for label,obj in [('stage1_original',before),('vectorized',engine)]:
        times=[]
        for _ in range(5):
            t=time.perf_counter();rows=obj.records(pred,cal['mapping']);times.append(time.perf_counter()-t)
        matching[label]=dict(median_seconds=float(np.median(times)),repetitions=times,rows=rows)
    aa=matching['stage1_original'].pop('rows');bb=matching['vectorized'].pop('rows');diff=0.
    for a,b in zip(aa,bb):
        for key in a:
            if key!='alternatives':assert a[key]==b[key],key
        assert [r['index'] for r in a['alternatives']]==[r['index'] for r in b['alternatives']]
        for x,y in zip(a['alternatives'],b['alternatives']):diff=max(diff,abs(x['distance_px']-y['distance_px']))
    assert diff<1e-10
    matching.update(speedup=matching['stage1_original']['median_seconds']/matching['vectorized']['median_seconds'],maximum_alternative_distance_roundoff_px=diff,primary_error_coordinates_and_owners_exact=True)
    contact={};a=next(s['parameters'] for s in seeds() if s['name']=='N3200-h-1-open')
    for label,cls in [('stage1_original',old.Engine),('cached',Engine)]:
        e=cls(2)
        for shift in [0.,1.,2.]:e.geometry(dict(a,s0=a['s0']+shift),Timers())
        timer=Timers();t=time.perf_counter();item,_=e.geometry(a,timer)
        contact[label]=dict(seconds=time.perf_counter()-t,profile=timer.result(),certificate=item['cert'])
    assert contact['stage1_original']['certificate']==contact['cached']['certificate']
    contact['speedup']=contact['stage1_original']['seconds']/contact['cached']['seconds']
    batch={};qq=[dict(p,light_az=p['light_az']+d) for d in [-2.,0.,2.]]
    for label in ['cold','camera_reused']:
        e=Engine(2);results=[];times=[]
        for q in qq:
            if label=='cold':e=Engine(2)
            r=e.evaluate(q,cal['mapping']);results.append(r['reflections']);times.append(r['seconds'])
        batch[label]=dict(seconds=sum(times),per_evaluation_seconds=times,results=results)
    assert batch['cold'].pop('results')==batch['camera_reused'].pop('results')
    batch['speedup']=batch['cold']['seconds']/batch['camera_reused']['seconds']
    result=dict(passed=True,utc=utc(),matching=matching,unchanged_contact_reuse=contact,native_illumination_batch=batch,
        policy='Same native optical calculation and primary errors. Vectorized alternative distances differ only by reported floating roundoff; all owners and ambiguity flags agree. Contact cache reuses exactly identical geometry hashes. No approximate predictor is adopted.')
    save(ROOT/'photo2/r312/results/campaign/profiling/stage2-optimizations.json',result);print({k:v for k,v in result.items() if k not in ['unchanged_contact_reuse']},flush=True)
    return result

if __name__=='__main__':run()
