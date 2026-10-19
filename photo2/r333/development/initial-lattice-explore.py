import os
os.environ['MPLCONFIGDIR']='/tmp/r333-mpl'
from photo2.r332.common import *
from collections import Counter
from photo2.r331.analyze import evaluate
from photo2.r330.pattern import scan
import matplotlib.pyplot as plt
G=read(ROOT/'photo2/r332/results/graph.json.gz');co={x['id']:x['ab'] for x in G['coordinates']};obs={x['id']:x for x in G['observations']};ids=sorted(co);ab=np.array([co[o] for o in ids]);c=np.array([['red','yellow','black'].index(obs[o]['color']) for o in ids]);w=np.where(c==2,.55,1.);b=np.minimum((ab.sum(1)%415/415*12).astype(int),11)
for fam,wt in [('A',[7,6]),('B',[6,7])]:
 k=ab@wt
 rows=[evaluate(k,c,w,b,p) for p in [104]+list(range(200,400))]
 print(fam,[(r['period'],round(r['gain_nats'],3),round(r['agreement'],3)) for r in sorted(rows,key=lambda r:-r['penalized_gain'])[:15]],flush=True)
occ={tuple(v):i for i,v in enumerate(ab)}
# don't seam for exploration
rows=[]
for da in range(-22,23):
 for db in range(-22,23):
  if da+db<=0:continue
  pairs=[(i,occ[tuple(v+[da,db])]) for i,v in enumerate(ab) if tuple(v+[da,db]) in occ]
  if len(pairs)<40:continue
  same=sum(c[i]==c[j] for i,j in pairs)/len(pairs)
  rows.append((same,len(pairs),da,db))
print('translations',sorted(rows,reverse=True)[:35])
for n in range(4):
 fig,ax=plt.subplots(figsize=(18,5));sel=(ab.sum(1)>=n*104-20)&(ab.sum(1)<n*104+104)
 for i in np.flatnonzero(sel):
  ax.scatter(ab[i].sum(),ab[i,0]-ab[i,1],c=['#da3434','#ead546','#222'][c[i]],s=65,edgecolors='gray');ax.text(ab[i].sum(),ab[i,0]-ab[i,1]+.16,str(c[i]),fontsize=5)
 ax.grid();ax.set_aspect(2);fig.savefig(ROOT/f'photo2/r333/development/strip-{n}.png');plt.close(fig)
