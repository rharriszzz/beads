"""Freeze new real-photo holdouts before any R291 detector exists."""
import hashlib
import subprocess
import numpy as np
from .common import *

def main():
    if (EVIDENCE/'collection.json').exists():raise RuntimeError('Collection already frozen')
    _,_,meta=photo()
    old=read(ROOT/'photo2/r290/evidence/collection.json')
    display={q['case_id']:q for q in read(ROOT/'photo2/review/r290/manifest.json')['cases']}
    cases=[]
    for c in old['cases']:
        cases.append(dict(c,split='development' if c['split']=='development' else 'retrospective',old_split=c['split'],categories=display[c['case_id']]['categories']))
    features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']]
    old_points=[c['feature']['point'] for c in cases];fresh=[];unfilled=[]
    def rank(q):return hashlib.sha256(('R291-reserved:'+q['id']).encode()).hexdigest()
    for color,n in [('red',4),('yellow',4),('unknown',2)]:
        for i in range(n):
            pool=[q for q in features if q['color']==color and min(np.linalg.norm(np.array(q['point'])-p) for p in old_points+[v['feature']['point'] for v in fresh])>=100]
            if not pool:
                unfilled.append(dict(color=color,slot=i+1,reason='No remaining independent R289 feature >=100px from all58 old and earlier new targets.'));continue
            q=min(pool,key=rank)
            fresh.append(dict(case_id=f'fresh-{color}-{i+1:02}',feature=q,selection_anchor=q['point'],anchor_distance_px=0.,split='reserved',old_split=None,categories=['new-real-photo','black-reflection','weak-illumination'] if color=='unknown' else ['new-real-photo','diffuse-illumination'],selection_source='Minimum SHA256(R291-reserved:featureID) within predeclared color stratum; >=100px from every R290 target and previous new target. No result inspected.'))
    cases+=fresh
    tracked=subprocess.check_output(['git','ls-files','photo2'],text=True).splitlines()
    hashes={p:sha(ROOT/p) for p in tracked if not p.startswith(('photo2/r291/','photo2/review/r291/','photo2/R291'))}
    feedback=ROOT/'photo2/r290/feedback'
    feedback_hashes={str(p.relative_to(ROOT)):sha(p) for p in feedback.rglob('*') if p.is_file()} if feedback.exists() else {}
    save(EVIDENCE/'historical-hashes.json.gz',hashes)
    save(EVIDENCE/'r290-feedback-hashes.json',feedback_hashes)
    save(EVIDENCE/'collection.json',dict(schema='R291-photographic-collection-v1',cases=cases,photo=meta,new_reserved_count=len(fresh),unfilled=unfilled,policy='Only R290 development used for tuning. Old reserved is retrospective; new reserved is frozen before R291 implementation. No detector or outcomes opened for new cases. >=100px target separation does not make this historically studied photograph independent.',source_hashes={p:sha(ROOT/p) for p in ['photo2/r290/evidence/collection.json','photo2/review/r290/manifest.json','photo2/r289/results/photo-landmarks.json.gz','photo2/r291/select.py','photo2/R291_SPECIFICATION.md']}))
    print('Frozen',len(cases),'cases;',len(fresh),'new reserved;',len(unfilled),'unfilled; preserved',len(hashes),'historical files and',len(feedback_hashes),'feedback files')

if __name__=='__main__':main()
