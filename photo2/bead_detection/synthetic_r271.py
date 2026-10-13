"""Paired R270 synthetic scenes, truth only after automatic acceptance."""
import gzip,json,time
from collections import Counter
import numpy as np
from .trusted_r271 import detect
from .experiment_r271 import ROOT,OUT,save,jsonlines

def main():
    start=time.monotonic();images=np.load(ROOT/'photo2/review/r270/synthetic-inputs.npz');truth=np.load(ROOT/'photo2/review/r270/synthetic-truth.npz');results=[];rows_all=[];paths=[]
    for name in images.files:
        rows,traces,summary,mask,paper=detect(images[name]);t=truth[name];counts=Counter(int(t[r['y'],r['x']]) for r in rows if r['trusted'])
        result=dict(scene=name,candidates=len(rows),trusted=summary['trusted'],background_accepted=counts[0],bodies_with_multiple_locations=sum(n>1 for b,n in counts.items() if b>0),body_location_counts={str(b):n for b,n in counts.items() if b>0},exclusions=summary['exclusions'])
        results.append(result);rows_all.extend(dict(scene=name,**r,truth_body=int(t[r['y'],r['x']])) for r in rows);paths.extend(dict(scene=name,**r) for r in traces)
        print(name,result['trusted'],'background',counts[0],'multiple',result['bodies_with_multiple_locations'],flush=True)
    save('synthetic-summary.json',dict(scenes=len(results),trusted=sum(r['trusted'] for r in results),background_accepted=sum(r['background_accepted'] for r in results),bodies_with_multiple_locations=sum(r['bodies_with_multiple_locations'] for r in results),elapsed_seconds=time.monotonic()-start,results=results))
    jsonlines('synthetic-candidates.jsonl.gz',rows_all);jsonlines('synthetic-traces.jsonl.gz',paths)
if __name__=='__main__':main()
