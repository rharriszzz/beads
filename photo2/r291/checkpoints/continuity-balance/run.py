"""Develop, freeze, then evaluate new reserved and old retrospective cases."""
import argparse
import time
from pathlib import Path
import numpy as np
from PIL import Image
from .common import *
from .detector import detect,VERSION,PARAMETERS

SOURCES=['photo2/r291/detector.py','photo2/r291/evidence.py','photo2/r291/run.py','photo2/r291/common.py','photo2/r291/evidence/collection.json','photo2/r290/detector.py','photo2/r282/common.py','photo2/bead_detection/brightness_r270.py','photo2/r289/results/photo-landmarks.json.gz']
def hashes():return {p:sha(ROOT/p) for p in SOURCES}

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['development','freeze','retrospective','reserved']);p.add_argument('--output',type=Path);a=p.parse_args();dest=a.output or OUT
    if a.stage=='freeze':
        if (OUT/'algorithm-frozen.json').exists():raise RuntimeError('Already frozen')
        save(OUT/'algorithm-frozen.json',dict(algorithm=VERSION,parameters=PARAMETERS,source_hashes=hashes(),development_sha256=sha(OUT/'development.json.gz'),frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),new_reserved_opened=False,policy='No code/parameter changes after new reserved inference. Old R290 reserved is retrospective, not fresh confirmation.'));print('Frozen before new reserved inference');return
    if a.stage!='development':assert read(OUT/'algorithm-frozen.json')['source_hashes']==hashes(),'Frozen inference sources changed'
    native,rgb,meta=photo();collection=read(EVIDENCE/'collection.json');assert meta==collection['photo'];rows=[]
    features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']]
    for c in collection['cases']:
        if c['split']!=a.stage:continue
        point=np.array(c['feature']['point']);near=[q for q in features if np.linalg.norm(np.array(q['point'])-point)<=170]
        result=detect(rgb,c['feature'],near);result.update(case_id=c['case_id'],split=c['split'],categories=c['categories'],selection_anchor=c['selection_anchor'],photo=meta)
        x0,y0,x1,y1=result['box'];path=dest/'crops'/(c['case_id']+'.png');path.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(native[y0:y1,x0:x1]).save(path);result['crop_sha256']=sha(path);rows.append(result)
        e=result['A']['evidence'];print(c['case_id'],result['A']['candidate_pixels']['pixel_count'],f"support={e['T7']['supported_fraction']:.2f}",f"IoU={min(e['T8']['perturbation_IoU']):.2f}",f"inside={len(e['T4']['other_features_inside'])}",f"seams={e['T1']['protected_separators']}",flush=True)
    save(dest/(a.stage+'.json.gz'),dict(records=rows,photo=meta,source_hashes=hashes(),algorithm=VERSION,parameters=PARAMETERS))
    print('Saved',len(rows),a.stage,'cases')

if __name__=='__main__':main()
