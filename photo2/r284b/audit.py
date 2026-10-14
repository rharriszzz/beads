"""Exact bounded replay and historical Git-blob preservation audit."""
import hashlib,subprocess
import numpy as np
from PIL import Image
from pathlib import Path
from photo2.r282.common import ROOT,read,save,sha,photo
from .run import OUT,main as run
BASE='73021c29debb95b472d3505a37a7941e7d101b2d'

def main():
    replay=Path('/tmp/beads-r284b-replay');run(replay)
    names=['cases.json','summary.json','freeze.json']+[c['name']+'.json.gz' for c in read(OUT/'cases.json')]+['auto-weak-cues.json','auto-same-color-cues.json']
    for name in names:assert (OUT/name).read_bytes()==(replay/name).read_bytes(),name
    listing=subprocess.check_output(['git','ls-tree','-r',BASE,'--','photo2','beads-photo-2.jpg'],cwd=ROOT).decode().splitlines();checked=0
    for line in listing:
        meta,path=line.split('\t',1);expected=meta.split()[2];data=(ROOT/path).read_bytes();actual=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
        assert actual==expected,path;checked+=1
    native,_,_=photo()
    for case in read(OUT/'cases.json'):
        x,y=case['origin'];saved=np.asarray(Image.open(ROOT/'photo2/review/r284b'/(case['name']+'-native.png')))
        np.testing.assert_array_equal(saved,native[y:y+128,x:x+128])
    freeze=read(OUT/'freeze.json')
    for path,digest in {**freeze['input_hashes'],**freeze['source_hashes']}.items():assert sha(ROOT/path)==digest,path
    save(OUT/'audit.json',dict(replay_files=names,exact_replay=True,historical_base=BASE,historical_blobs_unchanged=checked,freeze_hashes_verified=True,native_crops_exact=10,
        scope='All previously tracked photo2 files and source photo; production unchanged. No Phase2/3 run.'))
    print(f'{len(names)} exact replay files; {checked} historical blobs unchanged',flush=True)

if __name__=='__main__':main()
