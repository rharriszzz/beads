"""Assess unchanged R292 on a frozen centerline population; no production adoption."""
import argparse,time
from pathlib import Path
import numpy as np
from PIL import Image
from .common import *
from photo2.r292.detector import detect,VERSION,PARAMETERS
from photo2.r292.run import SOURCES as BASE_SOURCES
SOURCES=BASE_SOURCES+['photo2/r293/run.py','photo2/r293/common.py','photo2/r293/evidence/collection.json']
def hashes():return {p:sha(ROOT/p) for p in SOURCES}
def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['development','freeze','reserved']);p.add_argument('--output',type=Path);a=p.parse_args();dest=a.output or OUT
    if a.stage=='freeze':
        if (OUT/'algorithm-frozen.json').exists():raise RuntimeError('Already frozen')
        save(OUT/'algorithm-frozen.json',dict(algorithm=VERSION,parameters=PARAMETERS,source_hashes=hashes(),development_sha256=sha(OUT/'development.json.gz'),frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),reserved_opened=False,decision='Keep R292 unchanged. Assess representative centerline observations rather than tune on old peripheral failures. Preserve partial visible material/bright patches; no complete-silhouette requirement.'));print('Frozen unchanged R292 before reserved evaluation');return
    if a.stage=='reserved':assert read(OUT/'algorithm-frozen.json')['source_hashes']==hashes()
    native,rgb,meta=photo();col=read(EVIDENCE/'collection.json');assert meta==col['photo'];rows=[];features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']];before=hashes()
    for c in col['cases']:
        if c['split']!=a.stage:continue
        p=np.array(c['feature']['point']);near=[q for q in features if np.linalg.norm(np.array(q['point'])-p)<=170];r=detect(rgb,c['feature'],near);r.update(case_id=c['case_id'],split=c['split'],categories=c['categories'],selection_anchor=c['selection_anchor'],photo=meta,priority_evidence=c['priority_evidence']);x0,y0,x1,y1=r['box'];path=dest/'crops'/(c['case_id']+'.png');path.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(native[y0:y1,x0:x1]).save(path);r['crop_sha256']=sha(path);rows.append(r)
        print(c['case_id'],r['A']['candidate_pixels']['pixel_count'],'IoU',round(min(r['A']['evidence']['T8']['perturbation_IoU']),3),'other features',len(r['A']['evidence']['T4']['other_features_inside']),flush=True)
    assert before==hashes();save(dest/(a.stage+'.json.gz'),dict(records=rows,algorithm=VERSION,photo=meta,source_hashes=hashes(),scope='R293 assessment; unchanged R292 single-target inference.'));print('Saved',len(rows),a.stage)
if __name__=='__main__':main()
