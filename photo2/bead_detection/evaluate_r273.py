"""Known synthetic identities evaluate all region alternatives after detection."""
import time,json
from collections import Counter
from dataclasses import replace
from .interiors_r273 import refine,Parameters
from .expansion_r273 import VARIANTS
METHODS={m:replace(Parameters(),method=m) for m in ("connected","star-color","star-valley")}|VARIANTS
from .coverage_r272 import detect as baseline
from .evaluate_coverage_r272 import scenes,metric,add_metrics,finish
from .test_r273 import reflections
from .experiment_r273 import OUT,save,lines

def main():
    start=time.time();totals={method:{c:Counter() for c in ('black','red','yellow')} for method in METHODS};results=[];records=[]
    for name,rgb,truth,colors,condition in scenes():
        base=baseline(rgb)[0]
        for method in totals:
            b,r,_,summary=refine(rgb,rgb,base,METHODS[method]);m,a=metric(b,truth,colors);add_metrics(totals[method],m);results.append(dict(scene=name,method=method,metrics=m,associations=a,summary=summary));records.extend(dict(scene=name,method=method,**row) for row in r)
    ownership=[]
    for name in ('weak','equal','close','separate'):
        rgb,truth=reflections(name);base=baseline(rgb)[0]
        for rule in ('winner','margin','defer'):
            b,r,edges,summary=refine(rgb,rgb,base,replace(Parameters(),black_rule=rule));m,a=metric(b,truth,{i:'black' for i in set(truth.ravel()) if i});ownership.append(dict(scene=name,rule=rule,metrics=m,rows=r,pairs=edges))
    save('synthetic-evaluation.json',dict(scenes=52,metrics={k:finish(v) for k,v in totals.items()},results=results,elapsed_seconds=time.time()-start));save('synthetic-black-ownership.json',ownership);lines('synthetic-candidates.jsonl.gz',records);print({k:finish(v) for k,v in totals.items()},flush=True)
if __name__=='__main__':main()
