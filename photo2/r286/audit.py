"""Historical byte preservation, exact original crops and independent replay."""
import hashlib,subprocess,platform,sys
import numpy as np
from PIL import Image
from .common import *
BASE='8448689b68df9fa0a57f3f4e9450434e116f5f00'
def main():
    entries=subprocess.check_output(['git','ls-tree','-r','-z',BASE,'--','photo2','beads-photo-2.jpg'],cwd=ROOT).split(b'\0');checked=0;changed=[];exceptions=[]
    for entry in entries:
        if not entry:continue
        meta,name=entry.split(b'\t',1);mode,kind,oid=meta.split();name=name.decode()
        if kind!=b'blob':continue
        if name=='photo2/PHASE1_MEASUREMENTS.md':exceptions.append(dict(path=name,baseline_blob=oid.decode(),reason='User requests permanent R286 dark-seam/central-edge contract and review decisions.'));continue
        p=ROOT/name;data=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=oid.decode():changed.append(name)
        checked+=1
    assert not changed,changed
    native,_,_=photo();crop_count=0
    for stage in ('development','confirmation'):
        for case in read(OUT/(stage+'.json.gz'))['cases']:
            o=min(case['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-case['seed']));x,y=o['origin'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/(case['name']+'-native.png'))),native[y:y+97,x:x+97]);crop_count+=1
            if stage=='confirmation':
                x,y=np.array(case['seed'])-80;np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/(case['name']+'-group-native.png'))),native[y:y+161,x:x+161]);crop_count+=1
    extras=read(OUT/'additional-review.json');conf=[o for q in read(OUT/'confirmation.json.gz')['cases'] for o in q['observations']]
    for q in extras:
        o=next(o for o in conf if o['id']==q['id']);x,y=o['origin'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/(q['name']+'-native.png'))),native[y:y+97,x:x+97]);crop_count+=1
    black=read(OLD/'reflections.json.gz');bo={o['id']:o for o in black['observations']}
    for q in black['selected'][:2]:
        x,y=bo[q['id']]['origin'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/(q['name']+'-native.png'))),native[y:y+49,x:x+49]);crop_count+=1
    context=read(OUT/'two-sided-context/development.json.gz')['cases'][0]['observations'][0];x,y=context['origin'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/'P1-right-yellow-native.png')),native[y:y+97,x:x+97]);crop_count+=1
    q=read(OUT/'two-sided-context/crop.json');x,y=q['origin'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/'two-sided-native.png')),native[y:y+131,x:x+131]);crop_count+=1
    replay={}
    for name in ('development.json.gz','confirmation.json.gz'):
        p=Path('/tmp/beads-r286-replay')/name;replay[name]=sha(p)==sha(OUT/name);assert replay[name],name
    # Saved original P5 S support also independently reconstructed in diagnosis.
    f=read(OUT/'candidate-freeze.json');assert f['method_sha256']==sha(Path(__file__).parent/'methods.py');assert f['selection_sha256']==sha(OUT/'selection.json')
    save(OUT/'audit.json',dict(baseline=BASE,preserved_blobs=checked,changes=changed,intentional_exceptions=exceptions,native_crops_exact=crop_count,exact_replay=replay,methods_freeze=f))
    import scipy,skimage,matplotlib
    save(OUT/'environment.json',dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__,skimage=skimage.__version__,matplotlib=matplotlib.__version__))
    print(checked,'old blobs /',crop_count,'exact native crops / two exact rerun files')
if __name__=='__main__':main()
