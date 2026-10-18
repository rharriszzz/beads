"""Count/W models paired with their own photographic winding, never overwritten N."""
from .common import *
from .physical import construct,parameters
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from photo2.r324.coupled import support_ledger,optical
from collections import Counter

def main():
 start=time.perf_counter();g=read(ROOT/'photo2/r328/results/graph.json.gz');states=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'];op={o['id']:o for o in g['observations']};data=load()[0];pixels={r['id']:np.array(r['pixels_xy']) for r in read(ROOT/'photo2/r324/results/observation-pixels.json')};allrows=[];native=[]
 for si,state in enumerate(states):
  c=canonical(state);obs=[o for o in g['observations'] if o['id'] in c and o['id'] in pixels];xy=np.array([o['xy'] for o in obs]);seed=np.array([1180<=o['xy'][0]<=1505 and 200<o['xy'][1]<390 for o in obs]);ab=np.array([c[o['id']] for o in obs]);ref=op[REF]['xy'];cache={}
  for name,w in [('A',(7,6)),('B',(6,7))]:
   N=int(np.dot(state['H'],w));W=sum(state['H']);records=[]
   for hand in [-1,1]:
    t=time.perf_counter();p=parameters(N,1.95,.85,hand);p['winding']=W;p['turn']=N/W;p['minor']=p['radius']/np.sin(np.pi/p['turn']);s,con=construct(p,data);cert=contacts(s,seconds=.15);rec=dict(alternative=si,H=state['H'],N=N,W=W,family=name,hand=hand,parameters=s.p,construction=con,contact={k:v for k,v in cert.items() if k!='witnesses'})
    opts=[]
    for sign in [1,-1]:
     rel=sign*(ab@w)
     for j in np.argsort(np.linalg.norm(s.pc-ref,axis=1))[:12]:
      address=int(s.indices[j]);jj=(address+rel-s.indices[0])%N;d=np.linalg.norm(s.pc[jj]-xy,axis=1);opts.append((float(np.sqrt(np.mean(d[seed]**2))),sign,address,jj,rel))
    cost,sign,address,jj,rel=min(opts,key=lambda z:z[0]);rec['registration']=dict(direction=sign,reference_address=address,seed_center_proxy_rms=cost)
    if cert['certified']:
     one={o['id']:pixels[o['id']][len(pixels[o['id']])//2:len(pixels[o['id']])//2+1] for o in obs};rr,frac,nr=support_ledger(s,obs,one);vals=frac[np.arange(len(obs)),jj];rec['sparse_ownership']=float(vals.mean());rec['sparse_native_rays']=nr;rec['mapping']={o['id']:int(s.indices[j]) for o,j in zip(obs,jj)};cache[hand]=(s,cert,jj,rec['mapping'])
    rec['seconds']=time.perf_counter()-t;records.append(rec);allrows.append(rec)
   good=[r for r in records if 'sparse_ownership' in r]
   if si in [0,1,2] and good:
    best=max(good,key=lambda r:r['sparse_ownership']);s,cert,jj,mapping=cache[best['hand']];t=time.perf_counter();rr,frac,nr=support_ledger(s,obs,pixels);details=[dict(z,relative_index=int((np.array(c[z['id']])@w)*best['registration']['direction']),assigned_index=mapping[z['id']],assigned_fraction=float(frac[i,jj[i]])) for i,z in enumerate(rr)];native.append(dict(alternative=si,H=state['H'],N=N,W=W,family=name,hand=best['hand'],registration=best['registration'],full_native_ownership=float(np.mean([z['assigned_fraction'] for z in details])),rays=nr,rows=details,seconds=time.perf_counter()-t))
  save(OUT/'matched-physical.json.gz',dict(trials=allrows,native=native,seconds=time.perf_counter()-start,policy='N is derived from each candidate H and family. W=Ha+Hb is an explicit neighboring-turn construction hypothesis, not a proven crochet law. Both model hands and global index reversals tested. Shared radius1.95/axial.85, camera and fixed-reference registration rules; no geometry optimization.'))
  print('MATCHED',si,state['H'],[(r['family'],r['hand'],r.get('sparse_ownership')) for r in allrows[-4:]],flush=True)
if __name__=='__main__':main()
