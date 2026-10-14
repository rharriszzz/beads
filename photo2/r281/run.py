"""Inference runner. Reads geometry and photographs, never truth ownership rasters."""
import argparse
import numpy as np
from PIL import Image
from photo2.r280.detector import infer as r280,prepare as old_prepare
from .common import OUT,read,save
from .geometry import warp,owner_map,counterfactual,baseline_predictions,serial,project,centers,INDICES
from .detector import infer,prepare,decide

def load_hyp(folder,k,p):
 a=dict(read(folder/f'hyp-{k:+03}.json'));a.update(dict(np.load(folder/f'hyp-{k:+03}.npz')));a['projected_centers']=project(p,centers(INDICES,p['hand'],p['phase'],p['pitch'])).tolist();return a

def scenarios(folder,target,base,p,stage):
 k=target;diam=base['diameter']
 for present in (True,False):
  file=folder/'photo.png' if present else folder/f'absent-{k:+03}'/'photo.png'
  for level in (0.,.05,.10):
   hyp=warp(base,[level*diam,0.],uncertainty=level*diam)
   yield dict(kind='present' if present else 'removed',level=level,orientation=0.,negative=not present),hyp,file
  if stage=='all':
   for angle in (5.,10.):
    yield dict(kind='present-roll' if present else 'removed-roll',level=0.,orientation=angle,negative=not present),warp(base,angle=angle,angle_uncertainty=angle),file
 if stage!='all':return
 for kind in ('paper','neighbor','phase','duplicate','identity'):
  if kind=='paper':hyp=warp(base,[0.,-85.])
  elif kind=='neighbor':
   other=k+1 if k<14 else k-1;shift=np.array(base['projected_centers'][other+14])-base['center'];hyp=warp(base,shift)
  elif kind=='phase':hyp=counterfactual({**p,'phase':p['phase']+.45},k,base['h1'].shape)
  elif kind=='duplicate':hyp={**base,'competitors':['duplicate-claim']}
  else:
   other=k+1 if k<14 else k-1;hyp=counterfactual(p,other,base['h1'].shape)
  yield dict(kind=kind,level=0.,orientation=0.,negative=True),hyp,folder/'photo.png'

def main(split,stage):
 rules=read(OUT/'freeze.json')['rules'] if (OUT/'freeze.json').exists() else None
 if split=='heldout' and rules is None:raise RuntimeError('Freeze first')
 for folder in sorted((OUT/split).glob('scene-*')):
  # Evaluation provider exposes which anonymous geometry queries to run, not
  # their ownership, color, visibility segmentation or expected outcomes.
  p=read(folder/'geometry.json')['parameters'];keys=[int(path.stem.replace('hyp-','')) for path in sorted(folder.glob('hyp-*.json'))]
  cache={};records=[]
  for k in keys:
   base=load_hyp(folder,k,p)
   for meta,hyp,file in scenarios(folder,k,base,p,stage):
    if str(file) not in cache:
     rgb=np.asarray(Image.open(file).convert('RGB'));cache[str(file)]=(rgb,prepare(rgb),old_prepare(rgb))
    rgb,state,old_state=cache[str(file)];result=infer(rgb,hyp,rules,state=state)
    preds=baseline_predictions(hyp)
    if hyp.get('competitors'):
     target=next(x for x in preds if x['id']==hyp['id']);preds.append({**target,'id':'duplicate-claim'})
    baseline=next(r for r in r280(rgb,preds,'C',state=old_state) if r['id']==hyp['id'])
    records.append(dict(query_target=k,photo=str(file.relative_to(OUT)),**meta,hypothesis=serial(hyp),baseline=baseline,result=result,controls={m:decide(result,rules,m) for m in ('material','boundary')}))
  save(folder/'inference.json.gz',records);print(split,folder.name,len(records),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('split');p.add_argument('--stage',default='all');a=p.parse_args();main(a.split,a.stage)
