"""Freeze previously unexamined target outcomes before R292 development."""
import hashlib
import subprocess
import time
import numpy as np
from .common import *

def main():
    if (EVIDENCE/'collection.json').exists():raise RuntimeError('Already frozen')
    _,_,meta=photo();old=read(ROOT/'photo2/r291/evidence/collection.json')
    cases=[dict(c,split='development',previous_split=c['split']) for c in old['cases']]
    features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']]
    anchors=[c['feature']['point'] for c in cases];fresh=[];unfilled=[]
    for color,n in [('red',4),('yellow',4),('unknown',2)]:
        for i in range(n):
            pool=[q for q in features if q['color']==color and min(np.linalg.norm(np.array(q['point'])-p) for p in anchors+[v['feature']['point'] for v in fresh])>=100]
            if not pool:unfilled.append([color,i+1]);continue
            q=min(pool,key=lambda q:hashlib.sha256(('R292-reserved:'+q['id']).encode()).hexdigest())
            fresh.append(dict(case_id=f'holdout-{color}-{i+1:02}',feature=q,selection_anchor=q['point'],split='reserved',categories=['new-real-photo','weak-illumination','black-reflection'] if color=='unknown' else ['new-real-photo','diffuse-illumination'],selection_source='Minimum SHA256(R292-reserved:featureID); >=100px from all68 R291 targets and earlier new targets. No segmentation outcomes examined.'))
    preserved={p:sha(ROOT/p) for p in subprocess.check_output(['git','ls-files','photo2'],text=True).splitlines() if not p.startswith(('photo2/r292/','photo2/review/r292/','photo2/R292'))}
    feedback={str(p.relative_to(ROOT)):sha(p) for r in ('r290','r291') for p in (ROOT/'photo2'/r/'feedback').rglob('*') if p.is_file()}
    save(EVIDENCE/'historical-hashes.json.gz',preserved);save(EVIDENCE/'feedback-hashes.json',feedback)
    save(EVIDENCE/'collection.json',dict(schema='R292-real-photo-collection-v1',frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),photo=meta,cases=cases+fresh,new_reserved_count=len(fresh),unfilled=unfilled,source_hashes={p:sha(ROOT/p) for p in ['photo2/r292/select.py','photo2/R292_SPECIFICATION.md','photo2/r291/evidence/collection.json','photo2/r289/results/photo-landmarks.json.gz']},policy='All previously exposed68 cases are development. New targets frozen before detector implementation. One studied real photograph; target separation does not imply independent scene or material.'))
    print('Frozen',len(cases),'development and',len(fresh),'reserved; preserved',len(preserved),'historical files and',len(feedback),'feedback files')
if __name__=='__main__':main()
