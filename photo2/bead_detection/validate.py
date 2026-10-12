"""Validate saved full-photo masks, dark perimeters and optional isolated replay."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from .detect import ROOT, Parameters, sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--isolation',action='store_true');args=ap.parse_args()
    work=ROOT/'photo2/output/detection-r259';data=json.loads((work/'regions.json').read_text())
    labels=np.load(work/'labels.npz')['labels'];occupied=np.zeros(labels.shape,bool)
    value=ndi.gaussian_filter(np.asarray(Image.open(work/'photo.png')).max(axis=2).astype(np.float32)/255,data['parameters']['blur_sigma'])
    checks=[];black=0
    for r in data['regions']:
        x0,y0,x1,y1=r['bbox'];mask=np.zeros((y1-y0,x1-x0),bool)
        for y,a,b in r['pixel_runs']:mask[y-y0,a-x0:b-x0+1]=True
        assert mask.sum()==r['pixel_count']==r['area_px2']
        yy,xx=np.where(mask);np.testing.assert_allclose([xx.mean()+x0,yy.mean()+y0],r['centroid'])
        assert not (occupied[y0:y1,x0:x1]&mask).any()
        occupied[y0:y1,x0:x1]|=mask
        assert all(c[0]==c[-1] for c in r['contours'])
        if r['kind']=='reflection-on-dark':
            rim=mask&~ndi.binary_erosion(mask,structure=np.ones((3,3)))
            assert np.all(value[y0:y1,x0:x1][rim]<=data['parameters']['dark_value'])
            assert r['extent']=='reflection-and-dark-perimeter'
            black+=1
    np.testing.assert_array_equal(occupied,labels>0)
    rows=data['regions']+data['rejected']
    assert len({r['id'] for r in rows})==len(rows)
    assert len({i for r in rows for i in r['maxima_ids']})==len(data['maxima'])
    checks.extend(['all-native-pixel-counts-and-centroids','exclusive-masks-match-label-raster',
                   'all-contours-closed','all-retained-dark-perimeters-fully-below-threshold',
                   'unique-region-ids-and-complete-maxima-accounting'])
    if args.isolation:
        with tempfile.TemporaryDirectory(prefix='r259-isolation-') as temp:
            root=Path(temp);code=root/'package'/'detector';code.mkdir(parents=True)
            shutil.copy2(Path(__file__).parent/'detect.py',code/'detect.py')
            shutil.copy2(ROOT/'beads-photo-2.jpg',root/'photo.jpg')
            # Only one standalone detector file and source photo exist here.
            subprocess.run([sys.executable,str(code/'detect.py'),'--image',str(root/'photo.jpg'),'--output',str(root/'result')],cwd=root,check=True,stdout=subprocess.DEVNULL)
            assert sha(root/'result'/'regions.json')==sha(work/'regions.json')
            np.testing.assert_array_equal(np.load(root/'result'/'labels.npz')['labels'],labels)
            checks.append('isolated-code-and-photo-replay-byte-identical-json-and-labels')
    report=dict(generation_id=data['generation_id'],checks=checks,retained=len(data['regions']),dark_perimeters_checked=black,
                source_sha256=data['image_sha256'],detector_sha256=data['detector_sha256'])
    (work/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
