"""Preservation, native crops, saved pipelines and independent replay comparison."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from .common import OUT,ROOT,read,save,sha,photo,pixels


def normalized(value):
    if isinstance(value,dict):
        return {k:normalized(v) for k,v in value.items() if k not in ('source_sha256','fit_source_sha256','prediction_freeze_sha256','local_prediction_sha256')}
    if isinstance(value,list):return [normalized(v) for v in value]
    return value


def main(replay=None):
    base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();data=subprocess.check_output(['git','ls-tree','-rz',base,'--','photo2','beads.pov','beads-photo-2.jpg'],cwd=ROOT)
    count=0
    for entry in data.split(b'\0'):
        if not entry:continue
        meta,path=entry.split(b'\t');parts=meta.split();p=ROOT/path.decode();raw=p.read_bytes()
        digest=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert digest==parts[2].decode(),str(p);count+=1
    native,_,_=photo();crop_count=0
    for folder in (OUT/'local',OUT/'local-confirmation'):
        origin=read(folder/'anchors.json')['origin'];raw=np.asarray(Image.open(folder/'raw.png'));x,y=origin
        np.testing.assert_array_equal(raw,native[y:y+raw.shape[0],x:x+raw.shape[1]]);crop_count+=1
    comparisons=[]
    if replay:
        replay=Path(replay)
        # Saved native predictions/POV images and all algorithmic JSON. Browser
        # screenshots depend on environment and are deliberately not replayed.
        skip={'audit.json','browser-check.json','method-freeze.json'}
        for p in sorted(OUT.rglob('*')):
            if not p.is_file() or p.name in skip or p.suffix in ('.log','.pov','.npy') or 'browser' in p.name:continue
            if p.name=='complete.json':continue
            q=replay/p.relative_to(OUT)
            assert q.exists(),'Replay output missing: '+str(p.relative_to(OUT))
            if p.name.endswith(('.json','.json.gz')):
                a,b=normalized(read(p)),normalized(read(q))
                # Absolute output paths in phase3 provenance are relative already.
                if p.name in ('confirmation-results.json','synthetic-results.json'):
                    a.pop('method_freeze_sha256',None);b.pop('method_freeze_sha256',None)
                assert a==b,'Replay mismatch: '+str(p.relative_to(OUT))
            elif p.suffix=='.npz':
                a,b=np.load(p),np.load(q);assert set(a.files)==set(b.files)
                for k in a.files:np.testing.assert_array_equal(a[k],b[k])
            elif p.suffix=='.png':np.testing.assert_array_equal(np.asarray(Image.open(p)),np.asarray(Image.open(q)))
            else:continue
            comparisons.append(str(p.relative_to(OUT)))
    result=dict(base_commit=base,historical_files=count,historical_files_unchanged=True,raw_photo_crops_exact=crop_count,
        replay_files=comparisons,replay_count=len(comparisons),
        replay_metadata_exclusions='Source-file and dependent freeze digests differ where source gained output-path support after original freeze. Numerical predictions and measurements compared independently. Browser screenshots excluded.')
    save(OUT/'audit.json',result);print('historical',count,'replay',len(comparisons),'raw crops',crop_count,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--replay');main(p.parse_args().replay)
