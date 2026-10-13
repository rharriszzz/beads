"""Preserved stress colors, multiple highlights and unobservable boundaries."""
from dataclasses import replace
from collections import Counter
import numpy as np
from .coverage_r272 import detect as baseline
from .interiors_r273 import refine,Parameters
from .expansion_r273 import VARIANTS
METHODS={m:replace(Parameters(),method=m) for m in ("connected","star-color","star-valley")}|VARIANTS
from .historical_coverage_r272 import colors_for
from .evaluate_coverage_r272 import metric,add_metrics,finish
from .experiment_r273 import ROOT,OUT,save,lines

def main():
    images=np.load(ROOT/'photo2/review/r270/synthetic-inputs.npz');truth=np.load(ROOT/'photo2/review/r270/synthetic-truth.npz');totals={m:{c:Counter() for c in ('black','red','yellow')} for m in METHODS};results=[];records=[]
    for name in images.files:
        rgb=images[name];base=baseline(rgb)[0]
        for method in totals:
            b,r,_,summary=refine(rgb,rgb,base,METHODS[method]);m,a=metric(b,truth[name],colors_for(name));add_metrics(totals[method],m);results.append(dict(scene=name,method=method,metrics=m,associations=a,summary=summary));records.extend(dict(scene=name,method=method,**z) for z in r)
    save('historical-synthetic-evaluation.json',dict(scenes=len(images.files),metrics={k:finish(v) for k,v in totals.items()},results=results));lines('historical-synthetic-candidates.jsonl.gz',records);print({k:finish(v) for k,v in totals.items()},flush=True)
if __name__=='__main__':main()
