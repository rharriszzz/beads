"""Sequential development, source freeze, then reserved-only inference."""
import argparse
import collections
import time
import numpy as np
from PIL import Image
from .common import *
from .detector import detect, VERSION, PARAMETERS

SOURCES=['photo2/r290/detector.py','photo2/r290/run.py','photo2/r290/evidence/tests.json','photo2/r290/evidence/collection.json','photo2/r290/evidence/development-observations.json']

def hashes():return {p:sha(ROOT/p) for p in SOURCES}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['development','freeze','reserved']);parser.add_argument('--output',type=str);args=parser.parse_args()
    dest=OUT if args.output is None else __import__('pathlib').Path(args.output)
    if args.stage=='freeze':
        assert (OUT/'development.json.gz').exists()
        if (OUT/'algorithm-frozen.json').exists():raise RuntimeError('Already frozen')
        save(OUT/'algorithm-frozen.json',dict(algorithm=VERSION,parameters=PARAMETERS,source_hashes=hashes(),development_results_sha256=sha(OUT/'development.json.gz'),frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),reserved_opened=False,policy='No detector or parameter changes after reserved inference. Any discovered failure is reported for user review.'))
        print('Frozen before reserved inference');return
    if args.stage=='reserved':
        assert read(OUT/'algorithm-frozen.json')['source_hashes']==hashes(),'Frozen sources changed'
    data=read(EVIDENCE/'collection.json');native,rgb,meta=photo()
    assert meta==data['photo']
    features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']]
    results=[];t0=time.monotonic()
    for c in data['cases']:
        if c['split']!=args.stage:continue
        p=np.array(c['feature']['point']);near=[q for q in features if np.linalg.norm(np.array(q['point'])-p)<170]
        r=detect(rgb,c['feature'],near);r.update(case_id=c['case_id'],split=c['split'],categories=c['categories'],selection_anchor=c['selection_anchor'],selection_anchor_distance_px=c['anchor_distance_px'],photo=meta)
        results.append(r)
        # Exact native decoded RGB; PNGs carry no resized or painted pixels.
        x0,y0,x1,y1=r['box'];dest_images=dest/'crops';dest_images.mkdir(parents=True,exist_ok=True)
        path=dest_images/(c['case_id']+'.png');Image.fromarray(native[y0:y1,x0:x1]).save(path)
        r['crop_sha256']=sha(path)
        print(c['case_id'],r['A']['status'],f"{r['A']['evidence']['T7']['supported_fraction']:.2f}",r['A']['candidate_pixels']['pixel_count'],flush=True)
    save(dest/(args.stage+'.json.gz'),dict(records=results,algorithm=VERSION,parameters=PARAMETERS,source_hashes=hashes(),photo=meta))
    print(dict(statuses=dict(collections.Counter(r['A']['status'] for r in results)),seconds=round(time.monotonic()-t0,1)))

if __name__=='__main__':main()
