"""Evaluate unchanged R270 stress images; truth never enters detection."""
import time
from collections import Counter
import numpy as np
from .coverage_r272 import detect
from .evaluate_coverage_r272 import metric,add_metrics,finish
from .experiment_coverage_r272 import ROOT,OUT,save,lines,check_budget

def semantic(h):
    d={c:abs((h*360-a+180)%360-180) for c,a in [('red',0),('yellow',60)]};c=min(d,key=d.get);return c if d[c]<=25 else 'other'
def colors_for(name):
    if name.startswith('stress-'):
        i=int(name.split('-')[1]);h=(i*.173)%1;return {1:'black' if (i//8)%3==2 else semantic(h),2:semantic(h if i%2==0 else (h+.18)%1)}
    if name.startswith('no-visible'):return {1:'yellow',2:'yellow'}
    p=int(name.split('-')[2]);return {0:{1:'yellow',2:'yellow'},1:{1:'yellow',2:'red'},2:{1:'other',2:'other'},3:{1:'red',2:'yellow'}}[p]
def main():
    t=time.monotonic();images=np.load(ROOT/'photo2/review/r270/synthetic-inputs.npz');truth=np.load(ROOT/'photo2/review/r270/synthetic-truth.npz');total={c:Counter() for c in ('black','red','yellow')};rows=[];records=[]
    for name in images.files:
        check_budget();b,r,_,summary,_=detect(images[name]);m,a=metric(b,truth[name],colors_for(name));add_metrics(total,m);rows.append(dict(scene=name,truth_colors=colors_for(name),metrics=m,associations=a,summary=summary));records.extend(dict(scene=name,**z) for z in r)
    lines('historical-synthetic-candidates.jsonl.gz',records);save('historical-synthetic-evaluation.json',dict(scenes=len(rows),metrics=finish(total),results=rows,elapsed_seconds=time.monotonic()-t,note='Unchanged R270 RGB/truth, including invisible interfaces. Named colors come from generator hue parameters (within25 degrees of red/yellow), never classifier output; other colors excluded from recall denominator but misclassifying them counts as a false positive.'))
    print(finish(total),flush=True)
if __name__=='__main__':main()
