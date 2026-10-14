import argparse
import numpy as np
from PIL import Image
from .common import OUT,read,save,sha,ROOT
from .detector import infer,prepare
from .experiments import cases
from .baseline_match import match

def run(split,stage):
 freeze=OUT/'freeze.json'
 if split!='dev' and not freeze.exists():raise RuntimeError('Freeze development rules first')
 thresholds=read(freeze)['thresholds'] if freeze.exists() else None
 for folder in sorted((OUT/split).glob('scene-*')):
  rgb=np.asarray(Image.open(folder/'photo.png').convert('RGB'));state=prepare(rgb)
  g=read(folder/'geometry.json');other=read(folder/'perturbed-geometry.json');inventory=read(folder/'phase1.json.gz') if (folder/'phase1.json.gz').exists() else None
  for name,pred,meta in cases(g,other,rgb.shape[:2],stage):
   path=folder/(name+'.json.gz')
   data=dict(metadata=meta,predictions=pred,methods={m:infer(rgb,pred,m,thresholds,state=state) for m in 'ABC'})
   if inventory is not None:data['methods']['P']=match(state,pred,inventory)
   save(path,data)
  print(split,folder.name,stage,flush=True)

def baseline(split):
 from .phase1 import detect_phase1
 for folder in sorted((OUT/split).glob('scene-*')):
  rgb=np.asarray(Image.open(folder/'photo.png').convert('RGB'))
  out=detect_phase1(rgb);save(folder/'phase1.json.gz',out);print('phase1',folder, len(out['locations']),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('split');p.add_argument('--stage',default='all');p.add_argument('--baseline',action='store_true');a=p.parse_args()
 baseline(a.split) if a.baseline else run(a.split,a.stage)
