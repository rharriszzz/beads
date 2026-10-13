"""Color-contact controls and unchanged stress suites; known truth is evaluation-only."""
import json,time
from collections import Counter
import numpy as np
from .experiment_r274 import ROOT,OUT,save,lines
from .synthetic_r274 import scenes
from .evaluate_coverage_r272 import scenes as old_scenes,metric,add_metrics,finish
from .historical_coverage_r272 import colors_for
from .coverage_r272 import detect as baseline
from .interiors_r273 import refine as old_refine
from .hue_r274 import VARIANTS,refine

def main():
 start=time.time();images=np.load(ROOT/'photo2/review/r270/synthetic-inputs.npz');truth=np.load(ROOT/'photo2/review/r270/synthetic-truth.npz');suites={'color-contact':list(scenes()),'r272':[(n,r,t,c) for n,r,t,c,_ in old_scenes()],'r270':[(n,images[n],truth[n],colors_for(n)) for n in images.files]};summary={};records=[];results=[]
 for suite,items in suites.items():
  totals={m:{c:Counter() for c in ('black','red','yellow')} for m in VARIANTS}
  for name,rgb,t,c in items:
   base=baseline(rgb)[0];old=old_refine(rgb,rgb,base)[1]
   for method,p in VARIANTS.items():
    b,loc,rows,s=refine(rgb,rgb,base,old,p);m,a=metric(b,t,c);add_metrics(totals[method],m);results.append(dict(suite=suite,scene=name,method=method,baseline_candidates=len(base),metrics=m,associations=a,summary=s));records.extend(dict(suite=suite,scene=name,method=method,**r) for r in rows)
  summary[suite]={k:finish(v) for k,v in totals.items()};print(suite,summary[suite],flush=True)
 save('synthetic-evaluation.json',dict(summary=summary,results=results,elapsed_seconds=time.time()-start));lines('synthetic-records.jsonl.gz',records);items=list(scenes());np.savez_compressed(OUT/'synthetic-inputs.npz',**{n:r for n,r,t,c in items});np.savez_compressed(OUT/'synthetic-truth.npz',**{n:t for n,r,t,c in items})
if __name__=='__main__':main()
