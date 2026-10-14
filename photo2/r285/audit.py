"""Historical immutability, native crops, exact experiment replay and environment."""
import hashlib,subprocess,sys,platform
from pathlib import Path
import numpy as np
from PIL import Image
from photo2.r282.common import ROOT,read,save,sha,photo
from .select import OUT
BASE='e130718b4c20032c601996022a02139539070cb4'

def main():
    entries=subprocess.check_output(['git','ls-tree','-r','-z',BASE,'--','photo2','beads-photo-2.jpg'],cwd=ROOT).split(b'\0');checked=0;changed=[];exceptions=[]
    for entry in entries:
        if not entry:continue
        meta,name=entry.split(b'\t',1);mode,kind,oid=meta.split();name=name.decode();p=ROOT/name
        if kind!=b'blob':continue
        if name=='photo2/PHASE1_MEASUREMENTS.md':exceptions.append(dict(path=name,baseline_blob=oid.decode(),reason='User explicitly requests permanent brightness/darkness contract revision. Historical version remains at baseline commit.'));continue
        data=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=oid.decode():changed.append(name)
        checked+=1
    assert not changed,changed
    native,_,_=photo();manifest=read(OUT/'review-manifest.json');obs={o['id']:o for o in read(OUT/'development.json.gz')['observations']+read(OUT/'confirmation.json.gz')['observations']};count=0
    for q in manifest:
        o=obs[q['id']];x,y=o['origin'];np.testing.assert_array_equal(np.asarray(Image.open(ROOT/'photo2/review/r285'/(q['name']+'-native97.png'))),native[y:y+97,x:x+97]);count+=1
    black=read(OUT/'reflections.json.gz');bo={o['id']:o for o in black['observations']}
    for q in black['selected']:
        x,y=bo[q['id']]['origin'];np.testing.assert_array_equal(np.asarray(Image.open(ROOT/'photo2/review/r285'/(q['name']+'-native.png'))),native[y:y+49,x:x+49]);count+=1
    replay={}
    for name in ('development.json.gz','development-summary.json'):
        p=Path('/tmp/beads-r285-replay')/name;replay[name]=sha(p)==sha(OUT/name);assert replay[name],name
    save(OUT/'audit.json',dict(baseline=BASE,preserved_blobs=checked,changes=changed,intentional_exceptions=exceptions,native_crops_exact=count,exact_replay=replay,methods_freeze=read(OUT/'candidate-freeze.json')))
    import scipy,skimage,matplotlib
    save(OUT/'environment.json',dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__,skimage=skimage.__version__,matplotlib=matplotlib.__version__))
    print(checked,'preserved blobs;',count,'exact native crops;',len(replay),'exact replay files')
if __name__=='__main__':main()
