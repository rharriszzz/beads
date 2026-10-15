"""Frozen real-photo development, source freeze and untouched holdout evaluation."""
import argparse,time
from pathlib import Path
import numpy as np
from PIL import Image
from .common import *
from .detector import detect,VERSION,PARAMETERS
SOURCES=['photo2/r292/'+p for p in ('detector.py','graph.py','separators.py','continuation.py','run.py','common.py','evidence/collection.json')]+['photo2/r291/'+p for p in ('detector.py','evidence.py')]+['photo2/r290/detector.py','photo2/r282/common.py','photo2/bead_detection/brightness_r270.py','photo2/r289/results/photo-landmarks.json.gz']
def hashes():return {p:sha(ROOT/p) for p in SOURCES}
def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['development','freeze','reserved']);p.add_argument('--output',type=Path);a=p.parse_args();dest=a.output or OUT
    if a.stage=='freeze':
        if (OUT/'algorithm-frozen.json').exists():raise RuntimeError('Already frozen')
        save(OUT/'algorithm-frozen.json',dict(algorithm=VERSION,parameters=PARAMETERS,source_hashes=hashes(),development_sha256=sha(OUT/'development.json.gz'),frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),reserved_opened=False,policy='No changes to inference after holdout evaluation. All earlier R291 outcomes are exposed.'));print('Frozen');return
    if a.stage=='reserved':assert read(OUT/'algorithm-frozen.json')['source_hashes']==hashes(),'Frozen sources changed'
    native,rgb,meta=photo();collection=read(EVIDENCE/'collection.json');assert meta==collection['photo'];rows=[];features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']]
    initial_hashes=hashes()
    for c in collection['cases']:
        if c['split']!=a.stage:continue
        point=np.array(c['feature']['point']);near=[q for q in features if np.linalg.norm(np.array(q['point'])-point)<=170];r=detect(rgb,c['feature'],near);r.update(case_id=c['case_id'],split=c['split'],categories=c['categories'],selection_anchor=c['selection_anchor'],photo=meta)
        x0,y0,x1,y1=r['box'];path=dest/'crops'/(c['case_id']+'.png');path.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(native[y0:y1,x0:x1]).save(path);r['crop_sha256']=sha(path);rows.append(r)
        print(c['case_id'],r['A']['candidate_pixels']['pixel_count'],'arcs',len(r['separator_arcs']),'cross',sum(v['straddled_samples'] for v in r['separator_comparison']['before'] if v['enforced']),'->',sum(v['straddled_samples'] for v in r['separator_comparison']['after'] if v['enforced']),flush=True)
    assert initial_hashes==hashes(),'Sources changed during inference'
    save(dest/(a.stage+'.json.gz'),dict(records=rows,photo=meta,source_hashes=initial_hashes,algorithm=VERSION,parameters=PARAMETERS));print('Saved',len(rows),a.stage)
if __name__=='__main__':main()
