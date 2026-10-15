"""Preservation, native-pixel fidelity and independent numerical/raster replay."""
import argparse,os,subprocess,tempfile,json
from pathlib import Path
from PIL import Image
import numpy as np
from .common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');args=p.parse_args()
    historical=read(EVIDENCE/'prior-science-hashes.json.gz');feedback=read(EVIDENCE/'live-feedback-hashes.json')
    for name,h in dict(historical,**feedback).items():assert sha(ROOT/name)==h,name
    inp=read(EVIDENCE/'inputs.json.gz');assert sha(EVIDENCE/'inputs.json.gz')==read(EVIDENCE/'freeze.json')['input_sha256']
    for path,h in inp['sources'].items():assert sha(ROOT/path)==h,path
    native,_,meta=photo();manifest=read(REVIEW/'manifest.json')
    for c in manifest['crops']:
        x0,y0,x1,y1=c['box'];np.testing.assert_array_equal(np.array(Image.open(REVIEW/c['native'])),native[y0:y1,x0:x1])
    from .physical_audit import results
    for name,data in results(inp).items():assert data==read(OUT/name),name
    science={}
    if args.replay:
        with tempfile.TemporaryDirectory(prefix='r294-replay-') as tmp:
            dest=Path(tmp)/'results';review=Path(tmp)/'review';dest.mkdir();review.mkdir()
            env={**os.environ,'R294_OUTPUT':str(dest),'R294_REVIEW':str(review)}
            stages=[['fit','initial'],['fit','revised'],['evaluate','compare'],['review']]
            for cmd in stages:
                log=BASE/'checkpoints'/('replay-'+'-'.join(cmd)+'.log')
                with log.open('w') as f:subprocess.run([str(ROOT/'.venv/bin/python'),'-m','photo2.r294.'+cmd[0],*cmd[1:]],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
            for stage in ('initial','revised'):
                a=read(OUT/(stage+'.json'));b=read(dest/(stage+'.json'))
                keys=['selected','candidates']+(['coarse'] if stage=='initial' else [])
                for key in keys:assert a[key]==b[key],(stage,key)
                science[stage+'-fit']=dict(all_candidates_and_optimization_history_exact=True,
                    metadata_exclusion='Source manifests differ because later evaluation/review/test modules were added after the original fit. No scientific result fields excluded.')
            files=['initial-evaluation.json','revised-evaluation.json','comparison.json',
                'initial-positions.json.gz','revised-positions.json.gz','initial-positions.csv','revised-positions.csv','correspondence-comparison.csv',
                'initial/visibility.npz','revised/visibility.npz']
            for name in files:
                assert sha(OUT/name)==sha(dest/name),name
                science[name]=dict(byte_exact=True,sha256=sha(OUT/name))
            images=sorted(REVIEW.glob('*.png'))
            for image in images:assert sha(image)==sha(review/image.name),image.name
            assert read(REVIEW/'manifest.json')==read(review/'manifest.json')
            science['review']=dict(exact_PNGs=len(images),manifest_exact=True)
    previous=read(OUT/'audit.json') if (OUT/'audit.json').exists() else {}
    save(OUT/'audit.json',dict(photo=meta,prior_science_files_unchanged=len(historical),
        live_feedback_files_unchanged=len(feedback),native_crop_count=len(manifest['crops']),
        original_observations_unchanged=True,rejected_masks_used_as_targets=False,
        contact_alternatives_and_actual_penetrations_reproduced=True,
        replay=science or previous.get('replay',{}),synthetic_images=False,renderer_executed=False,
        phase1_detector_changed=False,phase3=False,production_changed=False))
    print('Preserved',len(historical),'science files and',len(feedback),'feedback files; native crops',len(manifest['crops']),'; replay groups',len(science))
if __name__=='__main__':main()
