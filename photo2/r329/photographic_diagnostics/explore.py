import json,gzip
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageOps
from photo2.r329.common import ROOT,read,canonical
OUT=Path(__file__).resolve().parent
G=read(ROOT/'photo2/r328/results/graph.json.gz');OBS={o['id']:o for o in G['observations']}
ss=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'];nov=read(ROOT/'photo2/r329/results/novel-windings.json.gz')['alternatives']
ST={'working':ss[0],'closest':ss[1],'lower':ss[5],'early':next(a['state'] for a in nov if a['state']['H']==[214,176])};CO={k:canonical(s) for k,s in ST.items()}
IM=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))/255.
BOXES={'E':(1600,1445,1805,1655),'F':(1240,218,1505,353),'G':(1515,220,1720,355),'H':(1050,2800,1230,2980)}
# Visible pigment centers: separate color masks; seed only identifies the region,
# no lattice edges or black observations enter this extraction.
def measure(o,radius=18,threshold=1.):
 x,y=o['xy'];x0,y0=int(x)-radius-3,int(y)-radius-3;patch=IM[y0:int(y)+radius+4,x0:int(x)+radius+4];yy,xx=np.indices(patch.shape[:2]);xx=xx+x0;yy=yy+y0;r,g,b=patch.transpose(2,0,1)
 if o['color']=='red':mask=(r>1.8*threshold*g)&(r>2.5*threshold*b)&(r>.16)
 else:mask=(g>.45*threshold*r)&(g>1.8*threshold*b)&(r>.9*threshold*g)&(r>.16)
 mask&=(xx-x)**2+(yy-y)**2<=radius**2
 labels,n=ndi.label(mask);where=np.argwhere(mask)
 if not len(where):return None
 dist=(xx[mask]-x)**2+(yy[mask]-y)**2;k=labels[tuple(where[dist.argmin()])];pts=np.column_stack([xx[labels==k],yy[labels==k]])
 if len(pts)<30:return None
 return pts.mean(0),pts

def design(ab,degree):
 a,b=ab.T;X=np.c_[a*0+1,a,b]
 if degree==2:X=np.c_[X,a*a,a*b,b*b]
 return X

def fit(co,pts,train,test,deg):
 origin=np.mean([co[o] for o in train],0);X=design(np.array([co[o] for o in train])-origin,deg);T=design(np.array([co[o] for o in test])-origin,deg)
 if np.linalg.matrix_rank(X)<X.shape[1]:return None
 coeff=np.linalg.lstsq(X,np.array([pts[o] for o in train]),rcond=None)[0];return T@coeff

def main():
 records={}
 for case,bbox in BOXES.items():
  ids=[o for o in OBS if OBS[o]['color']!='black' and bbox[0]<OBS[o]['xy'][0]<bbox[2] and bbox[1]<OBS[o]['xy'][1]<bbox[3] and o in CO['working']]
  measurements={o:measure(OBS[o]) for o in ids};measurements={o:z for o,z in measurements.items() if z is not None};pts={o:z[0] for o,z in measurements.items()};ids=list(pts)
  print('\n',case,len(ids))
  rowsets=[]
  for axis in [0,1]:
   groups={}
   for o in ids:groups.setdefault(CO['working'][o][axis],[]).append(o)
   for v,target in groups.items():
    if len(target)>=3:
     print('ROW',axis,v,target);rowsets.append((axis,v,target))
  out=[]
  for axis,v,test in rowsets:
   train=[o for o in ids if o not in test]
   for state in ['working',{'E':'closest','F':'working','G':'early','H':'lower'}[case]]:
    if not all(o in CO[state] for o in ids):continue
    for deg in [1,2]:
     pred=fit(CO[state],pts,train,test,deg)
     if pred is None:continue
     err=np.linalg.norm(pred-np.array([pts[o] for o in test]),axis=1)
     print(axis,v,state,deg,'mean',round(err.mean(),2),'max',round(err.max(),2),np.round(err,1).tolist())
     out.append(dict(axis=axis,row=v,targets=test,train=train,state=state,degree=deg,predicted=pred.tolist(),errors=err.tolist()))
  records[case]=dict(measurements={o:dict(center=z[0].tolist(),pixels=z[1].tolist()) for o,z in measurements.items()},row_tests=out)
 gzip.open(OUT/'exploration.json.gz','wt').write(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
