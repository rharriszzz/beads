"""Post-freeze real-photo measurement; never changes the fitted models."""
import numpy as np
from PIL import Image
from photo2.r280.detector import infer as baseline,prepare as old_prepare
from .common import OUT,read,save,sha,mask_from_runs
from .detector import infer,prepare
from .geometry import baseline_predictions

def main():
 f=OUT/'real';freeze=read(f/'prediction-freeze.json');assert sha(f/'anchors.json')==freeze['anchor_sha256'];before=sha(f/'prediction-freeze.json');rules=read(OUT/'freeze.json')['rules'];rgb=np.asarray(Image.open(f/'raw.png'));state=prepare(rgb);old=old_prepare(rgb);evidence=read(f/'photo-evidence.json');rows=[]
 for item in freeze['predictions']:
  h={k:v for k,v in item['hypothesis'].items() if k not in ('h1_surfaces','h0_surfaces','unknown')};h.update(dict(np.load(f/(item['id']+'.npz'))));r=infer(rgb,h,rules,state=state);b=next(x for x in baseline(rgb,baseline_predictions(h),'C',state=old) if x['id']==h['id']);support=mask_from_runs(r['support'],rgb.shape[:2]);overlap=[]
  for o in evidence['observations']:
   p=np.array(o['pixels']);valid=(p[:,0]>=0)&(p[:,0]<220)&(p[:,1]>=0)&(p[:,1]<180);p=p[valid];n=int(support[p[:,1],p[:,0]].sum())
   if n:overlap.append(dict(id=o['id'],pixels=n,fraction_of_phase1=n/len(p),anchor=o['id'] in evidence['anchor_ids']))
  rows.append(dict(id=item['id'],model=item['model'],kind=item['kind'],result=r,baseline=b,phase1_overlap=overlap));print(item['id'],r['status'],round(r['margin'],3),b['status'],[(x['id'],x['pixels']) for x in overlap],flush=True)
 assert before==sha(f/'prediction-freeze.json')
 save(f/'measurements.json',dict(prediction_freeze_sha256=before,detector_freeze_sha256=sha(OUT/'freeze.json'),rows=rows,note='Phase1 overlaps are retrospective comparisons only. No independently established real physical identities.'))
if __name__=='__main__':main()
