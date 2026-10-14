"""Identical R280 present/absent comparison, used only for development."""
import numpy as np
from PIL import Image
from photo2.r280.common import OUT as OLD
from photo2.r280.detector import infer as baseline
from .common import OUT,read,save
from .geometry import counterfactual
from .detector import infer,decide

def main():
 rows=[]
 for item in read(OLD/'absence-summary.json'):
  folder=OLD/'heldout'/item['scene'];p=read(folder/'geometry.json')['parameters'];k=int(item['removed'].replace('model-',''));hyp=counterfactual(p,k,(224,320))
  for present,path in [(True,folder/'photo.png'),(False,OLD/'absence'/item['scene']/'photo.png')]:
   rgb=np.asarray(Image.open(path).convert('RGB'));r=infer(rgb,hyp);b=read(folder/'A1-exact.json.gz')['methods']['C'] if present else read(OLD/'absence'/item['scene']/'inference.json.gz')['methods']['C'];b=next(x for x in b if x['id']==item['removed'])
   rows.append(dict(scene=item['scene'],target=k,present=present,baseline=b,result=r));print(item['scene'],present,b['status'],r['status'],round(r['margin'],3),r['metrics']['context_coverage'],flush=True)
 save(OUT/'legacy-development.json.gz',rows)
if __name__=='__main__':main()
