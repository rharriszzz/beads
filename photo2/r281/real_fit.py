"""Anchor-only local fit. No photograph, other observations or historical pose I/O."""
import itertools
import numpy as np
from scipy.optimize import least_squares
from .common import OUT,read,save,sha
from .geometry import INDICES,R,centers,project,trace,certify,owner_map,counterfactual,serial,warp

FAMILIES=(1,6,7)
def connected(indices):
 seen={0}
 while True:
  more={b for a in seen for b in indices if abs(a-b) in FAMILIES}
  if more<=seen:return len(seen)==len(indices)
  seen|=more

def vector(p):return np.array([*p['translation'],p['scale'],p['roll'],p['phase']])
def parameters(v,p):return {**p,'translation':v[:2].tolist(),'scale':float(v[2]),'roll':float(v[3]),'phase':float(v[4])}

def main():
 folder=OUT/'real';data=read(folder/'anchors.json');anchors=data['anchors'];obs=np.array([r['centroid'] for r in anchors]);zc=(obs[:,0]+1j*obs[:,1]);zc-=zc.mean()
 # All connected four-anchor graphs; labels are arbitrary local model indices.
 assignments=np.array([(0,*p) for c in itertools.combinations([int(k) for k in INDICES if k],3) if connected((0,*c)) for p in itertools.permutations(c)])
 candidates=[]
 for hand,pitch,incl in itertools.product((-1,1),(1.12,1.20),(-30.,0.,30.)):
  bucket=[]
  for phase in np.linspace(-np.pi,np.pi,24,endpoint=False):
   p=dict(hand=hand,pitch=pitch,inclination=incl,roll=0.,phase=float(phase),scale=1.,translation=[0.,0.]);points=project(p,centers(INDICES,hand,phase,pitch))[assignments+14];z=points[:,:,0]+1j*points[:,:,1];zm=z.mean(1);zz=z-zm[:,None];a=(zz.conj()*zc).sum(1)/np.maximum((abs(zz)**2).sum(1),1e-9);scale=abs(a);err=np.mean(abs(zz*a[:,None]-zc)**2,axis=1);err[(scale<5)|(scale>13)]=1e6
   for j in np.argsort(err)[:4]:
    b=(obs[:,0]+1j*obs[:,1]).mean()-a[j]*zm[j];q={**p,'scale':float(scale[j]),'roll':float(np.degrees(np.angle(a[j]))),'translation':[float(b.real),float(b.imag)]}
    bucket.append(dict(parameters=q,assignments=assignments[j].tolist(),proxy_mse=float(err[j])))
  # Retain bounded shortlist per physical alternative; no detector scores here.
  selected=sorted(bucket,key=lambda r:r['proxy_mse'])[:4]
  for r in selected:
   p=r['parameters'];idx=r['assignments'];x=vector(p)
   def residual(v):
    q=parameters(v,p);return (project(q,centers(idx,q['hand'],q['phase'],q['pitch']))-obs).ravel()
   sol=least_squares(residual,x,bounds=([-100,-100,5,x[3]-25,x[4]-.4],[320,280,13,x[3]+25,x[4]+.4]),max_nfev=60)
   q=parameters(sol.x,p);r.update(parameters=q,proxy_rms=float(np.sqrt(np.mean(residual(sol.x)**2))),initial=p);candidates.append(r)
 # Positive interior measurements constrain shared pose by true forward ownership.
 samples=[np.array(r['pixels'])[np.linspace(0,len(r['pixels'])-1,48).astype(int)] for r in anchors];xy=np.concatenate(samples)
 def assess(p,idx):
  owner,_,unknown=trace(p,xy);fractions=[float(np.mean(owner[i*48:(i+1)*48]==idx[i])) for i in range(4)];pred=project(p,centers(idx,p['hand'],p['phase'],p['pitch']));rms=float(np.sqrt(np.mean(np.sum((pred-obs)**2,axis=1))))
  return float(np.mean(fractions)-.10*rms/(2*R*p['scale'])),fractions,rms
 refined=[]
 for hand in (-1,1):
  shortlist=sorted([r for r in candidates if r['parameters']['hand']==hand],key=lambda r:assess(r['parameters'],r['assignments'])[0],reverse=True)[:6]
  for r in shortlist:
   p=r['parameters'];idx=r['assignments'];history=[]
   for step in (1.,.5):
    for iteration in range(2):
     x=vector(p);options=[p]
     for j,delta in enumerate((2.,2.,.25,2.,.06)):
      for sign in (-1,1):
       v=x.copy();v[j]+=sign*step*delta
       if 5<=v[2]<=13:options.append(parameters(v,p))
     p=max(options,key=lambda q:assess(q,idx)[0]);score,frac,rms=assess(p,idx);history.append(dict(parameters=p,score=score,anchor_ownership=frac,centroid_proxy_rms=rms))
   score,frac,rms=assess(p,idx);refined.append({**r,'parameters':p,'score':score,'anchor_ownership':frac,'centroid_proxy_rms':rms,'history':history})
 selected=[]
 for hand in (-1,1):
  for r in sorted([r for r in refined if r['parameters']['hand']==hand],key=lambda r:r['score'],reverse=True):
   if not any(s['assignments']==r['assignments'] and s['parameters']['hand']==hand for s in selected):selected.append(r)
   if sum(s['parameters']['hand']==hand for s in selected)==2:break
 models=[];predictions=[]
 for j,r in enumerate(selected):
  p=r['parameters'];owner,unknown=owner_map(p,(180,220));pc=project(p,centers(INDICES,p['hand'],p['phase'],p['pitch']));idx=r['assignments'];eligible=[]
  for k in INDICES:
   x,y=pc[k+14];area=int((owner==k).sum())
   if k not in idx and any(abs(k-a) in FAMILIES for a in idx) and x>obs[:,0].max()+6 and 20<x<200 and 25<y<155 and area>=100:
    eligible.append((area,int(k)))
  chosen=[k for _,k in sorted(eligible,reverse=True)[:2]];name=f'model-{j:02}';cert=certify(p);assert cert['certified']
  models.append({**r,'id':name,'certificate':cert,'targets':chosen,'projected_centers':pc.tolist(),'anchor_ids':[a['id'] for a in anchors]})
  for k in chosen:
   h=counterfactual(p,k,(180,220),owner,unknown);h['uncertainty_px']=.05*h['diameter']
   for kind,hyp in [('candidate',h),('displaced',warp(h,[0.,-.8*h['diameter']],uncertainty=.05*h['diameter']))]:
    ident=f'{name}-k{k:+03}-{kind}';np.savez_compressed(folder/(ident+'.npz'),h1=hyp['h1'],h0=hyp['h0'],unknown=hyp['unknown']);predictions.append(dict(id=ident,model=name,kind=kind,hypothesis=serial(hyp)))
 save(folder/'fit-alternatives.json.gz',dict(coarse_assignment_count=len(assignments),candidates=candidates,refined=refined))
 save(folder/'prediction-freeze.json',dict(anchor_sha256=sha(folder/'anchors.json'),fit_source_sha256=sha(__file__),models=models,predictions=predictions,inputs=['anchors.json: four frozen observed interiors only','general construction principles','literal rounded annulus'],limits='Centroids initialize a proxy fit; only shared pose moves. Local model labels are not recovered physical identities. Alternative hands retained.'))
 print([(m['id'],m['parameters']['hand'],m['assignments'],m['anchor_ownership'],m['targets']) for m in models])
if __name__=='__main__':main()
