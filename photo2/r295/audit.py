"""Preservation, original pixels, frozen parameters and isolated search replay."""
import argparse,os,subprocess,tempfile,sys
from pathlib import Path
import numpy as np
from PIL import Image
from .common import *

def compare_fit(a,b,stage):
    assert len(a['candidates'])==len(b['candidates']),stage
    for i,(x,y) in enumerate(zip(a['candidates'],b['candidates'])):
        assert x['parameters']==y['parameters'],(stage,i,'parameters')
        assert x['train']['score']==y['train']['score'],(stage,i,'score')
        if 'trials' in x:
            assert len(x['trials'])==len(y['trials'])
            for j,(u,v) in enumerate(zip(x['trials'],y['trials'])):
                assert u['parameters']==v['parameters'],(stage,i,j,'trial parameters')
                assert u['metrics']['score']==v['metrics']['score'],(stage,i,j,'trial score')
    if 'selected' in a:assert a['selected']['parameters']==b['selected']['parameters']

def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');args=p.parse_args();d=read(EVIDENCE/'preservation.json.gz')
    for name,h in {**d['science'],**d['feedback']}.items():assert sha(ROOT/name)==h,name
    native,_,_=photo();manifest=read(REVIEW/'manifest.json')
    for c in manifest['crops']:
        x0,y0,x1,y1=c['box'];np.testing.assert_array_equal(np.array(Image.open(REVIEW/c['native'])),native[y0:y1,x0:x1])
    freeze=read(EVIDENCE/'final-freeze.json');current=read(OUT/'R295-evaluation.json')['parameters'];assert freeze['models']['R295']==current
    report=dict(prior_science_unchanged=len(d['science']),live_feedback_unchanged=len(d['feedback']),native_crops_exact=len(manifest['crops']),primary_parameters_unchanged_since_final_freeze=True)
    if args.replay:
        with tempfile.TemporaryDirectory(prefix='r295-replay-') as tmp:
            dest=Path(tmp);env={**os.environ,'R295_OUTPUT':str(dest),'R295_REVIEW':str(dest/'review')};replayed=[]
            # Rounds before the annular-volume fallback use their exact source checkpoint.
            # Later code adds physical classification but does not rewrite those histories.
            for stage in ('screen','local','global','revision'):
                source=BASE/'checkpoints/iteration-1/fit.py';code="import runpy,sys;source=sys.argv[1];sys.argv=['fit',sys.argv[2]];runpy.run_path(source,run_name='photo2.r295.fit_replay')['main']()"
                with (BASE/'checkpoints'/('replay-'+stage+'.log')).open('w') as log:subprocess.run([sys.executable,'-c',code,str(source),stage],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
                compare_fit(read(OUT/(stage+'.json')),read(dest/(stage+'.json')),stage);replayed.append(stage)
            for stage in ('joint','sensitivity'):
                with (BASE/'checkpoints'/('replay-'+stage+'.log')).open('w') as log:subprocess.run([sys.executable,'-m','photo2.r295.'+stage],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
                if stage=='joint':compare_fit(read(OUT/'joint.json'),read(dest/'joint.json'),stage)
                else:
                    assert read(OUT/'light-alternative.json')['selected']['parameters']==read(dest/'light-alternative.json')['selected']['parameters']
                    assert read(OUT/'sensitivity.json')['controls']==read(dest/'sensitivity.json')['controls']
                replayed.append(stage)
            for stage,args2 in [('finalize',['--resume-frozen']),('complete_comparisons',[]),('review',[])]:
                with (BASE/'checkpoints'/('replay-'+stage+'.log')).open('w') as log:subprocess.run([sys.executable,'-m','photo2.r295.'+stage,*args2],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            files=list(OUT.glob('*-evaluation.json'))+list(OUT.glob('*-positions.json.gz'))+list(OUT.glob('*-positions.csv'))+list(OUT.glob('*-visibility.npz'))+[OUT/'comparison.json',OUT/'historical-one-to-one.json',OUT/'final-sensitivity.json']
            for file in files:assert sha(file)==sha(dest/file.name),file.name
            images=list(REVIEW.glob('*.png'))
            for file in images:assert sha(file)==sha(dest/'review'/file.name),file.name
            assert read(REVIEW/'manifest.json')==read(dest/'review/manifest.json')
            report['replay']=dict(search_stages=replayed,all_candidate_and_trial_parameters_and_scores_exact=True,data_files_byte_exact=len(files),PNGs_byte_exact=len(images),manifest_exact=True,
                provenance='Original fitting code checkpoint for first four stages; current joint/sensitivity code. Source hashes/timestamps are metadata, not compared as scientific outcomes.')
    save(OUT/'audit.json',report);print(report)
if __name__=='__main__':main()
