"""Separate R291 B factors on exposed original-photo cases; never load holdouts."""
import numpy as np
from .common import *
from .graph import solve
from photo2.r291.evidence import measure,direct_access,separators

def main():
    _,rgb,meta=photo();collection=read(EVIDENCE/'collection.json');old={r['case_id']:r for s in ('development','retrospective','reserved') for r in read(ROOT/f'photo2/r291/results/{s}.json.gz')['records']}
    features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']];refs={q['case_id']:q for q in read(ROOT/'photo2/r291/evidence/completed-review-analysis.json')['cases']};rows=[]
    for c in collection['cases']:
        if c['split']!='development':continue
        r=old[c['case_id']];lo=np.array(r['box'][:2]);x0,y0,x1,y1=r['box'];seed=np.array(c['feature']['point'])-lo;m=measure(rgb[y0:y1,x0:x1],seed);core=np.zeros(m['lum'].shape,bool);q=pixels(c['feature'])-lo;core[q[:,1],q[:,0]]=True
        near=[dict(id=q['id'],local_point=(np.array(q['point'])-lo).tolist(),point=q['point']) for q in features if q['id']!=c['feature']['id'] and np.all(np.array(q['point'])>=lo+2) and np.all(np.array(q['point'])<np.array([x1,y1])-2) and np.linalg.norm(np.array(q['point'])-c['feature']['point'])<=170];access=direct_access(m,seed);peers=separators(m,seed,near)
        masks={};ref=refs.get(c['case_id']);target=set(map(tuple,pixels(r[ref['answer']]['candidate_pixels']))) if ref and ref['answer'] in ('A','B') else None
        for name,penalty,capacity in [('A',4.5,10**8),('dark_only',2.7,10**8),('peer_only',4.5,5000),('both_B',2.7,5000)]:
            mask=solve(m,core,access,peers,stop_penalty=penalty,peer_capacity=capacity);xy=np.c_[np.where(mask)[1]+x0,np.where(mask)[0]+y0];owned=set(map(tuple,xy));masks[name]=dict(pixels=dict(runs=runs(xy),pixel_count=len(xy)),reference_iou=len(owned&target)/len(owned|target) if target else None)
        assert masks['A']['pixels']==r['A']['candidate_pixels']
        if r['B']:assert masks['both_B']['pixels']==r['B']['candidate_pixels']
        rows.append(dict(case_id=c['case_id'],feature_id=c['feature']['id'],point=c['feature']['point'],reference_answer=ref['answer'] if ref else None,variants=masks));print(c['case_id'],{k:v['pixels']['pixel_count'] for k,v in masks.items()},flush=True)
    save(OUT/'r291-B-ablation.json.gz',dict(photo=meta,variants='Full 2x2: stop4.5/2.7 x peer1e8/5000; identical R291 context/evidence. No new reserved cases.',records=rows))
if __name__=='__main__':main()
