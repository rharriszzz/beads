"""Exact historical preservation, native crops, frozen sources and independent replay."""
import hashlib
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/beads-r288-mpl")
import platform
import subprocess
import sys
from PIL import Image
from .common import *

def main():
    entries=subprocess.check_output(['git','ls-tree','-r','-z',BASE,'--','photo2','beads-photo-2.jpg'],cwd=ROOT).split(b'\0')
    checked=0;changed=[];exceptions=[]
    for entry in entries:
        if not entry:continue
        meta,name=entry.split(b'\t',1);mode,kind,oid=meta.split();name=name.decode()
        if kind!=b'blob':continue
        if name=='photo2/PHASE1_MEASUREMENTS.md':
            exceptions.append(dict(path=name,baseline_blob=oid.decode(),reason='User-requested permanent R288 brightness/ownership principles and review decisions.'));continue
        data=(ROOT/name).read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=oid.decode():changed.append(name)
        checked+=1
    assert not changed,changed
    native,_,_=photo();crop_count=0
    for stage in ('development','confirmation'):
        for q in read(OUT/(stage+'-review-manifest.json')):
            x,y=q['origin'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/(q['name']+'-native.png'))),native[y:y+97,x:x+97]);crop_count+=1
        for case in read(OUT/(stage+'.json.gz'))['cases']:
            if True:
                x,y=np.array(case['seed'])-72;np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/(case['name']+'-group-native.png'))),native[y:y+145,x:x+145]);crop_count+=1
    for q in read(OUT/'additional-review-manifest.json'):
        x,y=q['origin'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/(q['name']+'-native.png'))),native[y:y+97,x:x+97]);crop_count+=1
    assert sha(ROOT/'photo2/J_AND_M_EXPLAINED.md')==read(OUT/'explanation-checkpoint.json')['explanation_sha256']
    assert sha(ROOT/'photo2/r288/methods_EW_initial.py')==read(OUT/'first-anchor-proposals.json.gz')['source_hash']
    replay={}
    for name in ('development.json.gz','confirmation.json.gz'):
        replay[name]=sha(Path('/tmp/beads-r288-replay')/name)==sha(OUT/name);assert replay[name],name
    f=read(OUT/'freeze.json')
    for name,h in f['source_hashes'].items():assert sha(Path(__file__).parent/name)==h,name
    assert sha(OUT/'selection.json')==f['selection_sha256']
    assert sha(OUT/'development.json.gz')==f['development_sha256']
    black=read(OUT/'black-preservation.json');assert sha(ROOT/black['source'])==black['sha256']
    save(OUT/'audit.json',dict(baseline=BASE,preserved_blobs=checked,changes=changed,intentional_exceptions=exceptions,native_crops_exact=crop_count,exact_replay=replay,freeze=f,black_source_unchanged=True))
    import scipy,skimage,matplotlib
    save(OUT/'environment.json',dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__,skimage=skimage.__version__,matplotlib=matplotlib.__version__))
    print(checked,'old blobs /',crop_count,'exact native crops / two exact rerun files; freeze and black source pass')

if __name__=='__main__':main()
