"""Reproduction, provenance and evidence-integrity checks."""
import sys,subprocess
import numpy as np
from PIL import Image
from .common import OUT,ROOT,read,save,sha,mask_from_runs
from .detector import infer,prepare
from .geometry import certify

def main():
 old=read(OUT/'preserved-input-hashes.json');changed=[p for p,h in old.items() if sha(ROOT/p)!=h];assert not changed,changed
 frozen=read(OUT/'freeze.json');diff=[p for p,h in frozen['source_hashes'].items() if sha(ROOT/p)!=h];assert diff==['photo2/r280/geometry.py'],diff
 repair=read(OUT/'dependency-repair.json');assert sha(ROOT/'photo2/r280/geometry.py')==repair['new_geometry_sha256'];assert sha(ROOT/'photo2/r280/contact.py')==repair['contact_sha256']
 replay=OUT/'heldout/scene-00';rgb=np.asarray(Image.open(replay/'photo.png').convert('RGB'));state=prepare(rgb);count=0
 for file in sorted(replay.glob('A*.json.gz')):
  a=read(file)
  for method in 'ABC':
   b=infer(rgb,a['predictions'],method,frozen['thresholds'],state=state);assert a['methods'][method]==b,(file,method);count+=len(b)
 scenes=[]
 for split in ('dev','heldout','stress'):
  for f in sorted((OUT/split).glob('scene-*')):
   g=read(f/'geometry.json');t=read(f/'truth.json');c=certify(g['parameters']);assert c==t['certificate']
   assert c['certified']==(split!='stress');assert t['projection_check']['all_resolved_agree']
   for path in f.glob('A*.json.gz'):
    a=read(path)
    for results in a['methods'].values():
     for r in results:
      mask=mask_from_runs(r['support'],(224,320));assert int(mask.sum())==r['positive_pixels'];assert r['physical_center'] is None
      if r['location'] is not None:np.testing.assert_allclose(np.argwhere(mask)[:,::-1].mean(0),r['location'])
   scenes.append(dict(split=split,scene=f.name,**t['projection_check']))
 expected=read(OUT/'real-replay-before.json');assert all(sha(OUT/p)==h for p,h in expected.items())
 # Source-only import audit in a fresh interpreter catches accidental legacy I/O.
 script="import sys,json; paths=[]\ndef hook(e,a):\n if e=='open' and isinstance(a[0],str) and a[0].endswith(('.json','.csv','.gz','.npy','.npz')):paths.append(a[0])\nsys.addaudithook(hook)\nimport photo2.r280.geometry\nprint(json.dumps(paths))"
 import json
 paths=json.loads(subprocess.check_output([sys.executable,'-c',script],text=True));assert not any('/photo2/' in p for p in paths)
 result=dict(preserved_files=len(old),changed_old_files=changed,frozen_detector_unchanged=True,postfreeze_change='Numerically identical contact import isolation; no threshold/measurement changes.',replayed_predictions=count,real_replayed_files=len(expected),native_support_audit=True,scenes=scenes,geometry_import_reads=paths)
 save(OUT/'audit.json',result);print({k:v for k,v in result.items() if k not in ('scenes','geometry_import_reads')})
if __name__=='__main__':main()
