"""Ownership validation on unchanged R270 synthetic scenes, truth withheld."""
from collections import Counter
import json
import numpy as np
from .experiment_r272 import ROOT,OUT,save,lines
from .trusted_r271 import detect
from .inventory_r272 import inventory

def main():
    images=np.load(ROOT/'photo2/review/r270/synthetic-inputs.npz');truths=np.load(ROOT/'photo2/review/r270/synthetic-truth.npz');results=[];allrecords=[];failures=[]
    for name in images.files:
        rgb=images[name];truth=truths[name];loc,_,_,_,paper=detect(rgb);beads,records,summary=inventory(rgb,rgb,loc,paper);owners=Counter();counts=Counter()
        for b in beads:
            body=int(truth[b['brightest']['y'],b['brightest']['x']]);owners[body]+=1
            inside=[int(truth[y,x]) for y,a,z in b['region']['runs'] for x in range(a,z+1)];counts['pixels']+=len(inside);counts['background_pixels']+=sum(k==0 for k in inside);counts['other_body_pixels']+=sum(k not in (0,body) for k in inside)
            if body==0 or any(k!=body for k in inside):failures.append(dict(scene=name,bead=b,body_at_peak=body))
        result=dict(scene=name,accepted=len(beads),colors=summary['colors'],duplicate_bodies=sum(v>1 for k,v in owners.items() if k>0),**counts);results.append(result);allrecords.extend(dict(scene=name,**r) for r in records)
    lines('synthetic-region-candidates.jsonl.gz',allrecords);save('synthetic-ownership.json',dict(scenes=len(results),accepted=sum(r['accepted'] for r in results),background_pixels=sum(r.get('background_pixels',0) for r in results),other_body_pixels=sum(r.get('other_body_pixels',0) for r in results),duplicate_bodies=sum(r['duplicate_bodies'] for r in results),results=results,failures=failures));print((OUT/'synthetic-ownership.json').read_text()[:1000]);assert not failures
if __name__=='__main__':main()
