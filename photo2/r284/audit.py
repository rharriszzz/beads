"""Exact independent real-case replay and pre-round Git-blob preservation."""
import hashlib,subprocess
from pathlib import Path
from PIL import Image
import numpy as np
from photo2.r282.common import ROOT,photo,read,save,sha
from .run import OUT,main as rerun
from .review import REVIEW


def main():
    replay=Path('/tmp/beads-r284a-replay');rerun(replay)
    names=['cases.json','summary.json','method-freeze.json']
    for c in read(OUT/'cases.json'):names += [c['name']+'.json.gz',c['name']+'-cues.json']
    exact=[]
    for name in names:
        assert (OUT/name).read_bytes()==(replay/name).read_bytes(),name;exact.append(name)
    native,_,_=photo()
    for c in read(OUT/'cases.json'):
        x,y=c['origin'];actual=np.asarray(Image.open(REVIEW/(c['name']+'-native.png')))
        np.testing.assert_array_equal(actual,native[y:y+128,x:x+128])
    old=[]
    listing=subprocess.check_output(['git','ls-tree','-r','fb26cd9','--','photo2','beads-photo-2.jpg'],cwd=ROOT,text=True)
    for line in listing.splitlines():
        metadata,name=line.split('\t',1);mode,kind,expected=metadata.split()
        if kind!='blob':continue
        p=ROOT/name;body=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
        assert actual==expected,name;old.append(name)
    save(OUT/'audit.json',dict(exact_replay_files=exact,old_git_blobs_unchanged=len(old),old_commit='fb26cd9',native_crops_exact=8,
        note='All pre-round photo2 and source-photo Git blobs unchanged. Real cases replayed from source pixels in a separate directory.'))
    print(len(exact),'exact replay files;',len(old),'old Git blobs unchanged; 8 native crops exact')

if __name__=='__main__':main()
