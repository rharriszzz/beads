"""Preserved geographic body-appearance classifier comparison."""
from photo2.r334.common import *
from scipy.special import softmax
from collections import Counter
r=read(artifact('classification/audit.json.gz'));rows=r['records'];g,obs,co,ids,ab,c,w,b,st=reviewed_dataset('relocated');ix={o:i for i,o in enumerate(ids)};names=[x['id'] for x in rows];labels=np.array([COLORS.index(x['overlay_color']) for x in rows]);xy=np.array([x['xy'] for x in rows]);from scipy.spatial import cKDTree
tree=cKDTree([obs[o]['xy'] for o in ids]);blocks=np.array([int(b[ix[o]]) if o in ix else int(b[tree.query(xy[j])[1]]) for j,o in enumerate(names)])
features=[]
for rad in range(3):
 ff=[]
 for row in rows:
  q=row['samples'][rad];raw=np.array(q.get('feature') or [0.]*27);light=row['lighting']['value'];f=np.r_[raw,raw[:12]/max(light,.1),q.get('median_value',0)/max(light,.1),q.get('red_material_fraction',0),q.get('yellow_material_fraction',0)];ff.append(f)
 features.append(np.array(ff))
for shrink in [.25,.5,.75]:
 pred=np.zeros((len(rows),3,3))
 for rad,F in enumerate(features):
  valid=np.array([q['samples'][rad]['valid'] for q in rows])
  for block in range(12):
   tr=np.array([j for j,o in enumerate(names) if o in obs and blocks[j]!=block and valid[j]]);te=np.flatnonzero(blocks==block);scale=np.maximum(np.percentile(F[tr],75,axis=0)-np.percentile(F[tr],25,axis=0),.04);X=F[tr]/scale;Y=F[te]/scale;mu=np.array([np.median(X[labels[tr]==a],axis=0) for a in range(3)]);res=X-mu[labels[tr]];cov=res.T@res/len(tr);cov=(1-shrink)*cov+shrink*np.diag(np.diag(cov))+.1*np.eye(len(scale));inv=np.linalg.inv(cov);dist=np.array([np.einsum('ij,jk,ik->i',Y-m,inv,Y-m) for m in mu]).T;pred[te,rad]=softmax(-.5*dist,axis=1)
 print('shrink',shrink)
 for j,row in enumerate(rows):
  if row['maker_reviewed']:print(row['id'],COLORS[pred[j].mean(0).argmax()],np.round(pred[j].mean(0),2))
 print('r161',Counter((row['label'],COLORS[pred[names.index(row['id'])].mean(0).argmax()]) for row in r['historical_reference_controls']))
