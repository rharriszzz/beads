"""Export every fixed boundary bracket and explicit missing-boundary counts."""
import numpy as np
from photo2.r297.common import read,save
from .run import OUT,engine

def main():
 e=engine();models=[]
 for path in sorted((OUT/'models').glob('*.json.gz')):
  r=read(path);a=np.load(path.with_name(r['name']+'.npz'));o=a['owner'].ravel();u=a['unknown'].ravel();rows=[]
  for bracket,(aa,bb,dist,split) in zip(e.m['external_brackets'],e.brackets):
   good=(o[aa]>=0)&(o[bb]<0)&~u[aa]&~u[bb];y,x,axis,sign,gap=map(int,bracket);rows.append(dict(material_endpoint=(e.m['origin']+[x,y]).tolist(),axis=axis,direction=sign,gap_pixels=gap,split=split,missing_in_extended_scan=not bool(good.any()),excess_distance_px=float(dist[good].min()) if good.any() else None,penalty_px=50. if not good.any() else 0.))
  models.append(dict(name=r['name'],brackets=rows,by_split={str(s):dict(n=sum(r['split']==s for r in rows),missing=sum(r['split']==s and r['missing_in_extended_scan'] for r in rows)) for s in [0,1,2]}))
 save(OUT/'boundary-brackets.json.gz',dict(models=models,policy='Missing means no correctly oriented foreground-to-paper transition in the bracket plus 12px extension. The 50px optimization penalty is not a measured displacement.'))
if __name__=='__main__':main()
