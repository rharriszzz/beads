"""Preserve new completed windings and diagnose start-dependent search pruning."""
from .common import *
from .localize import oriented_rows,evidence
from .physical import construct,parameters
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from photo2.r324.coupled import support_ledger
from collections import Counter

def main():
 g,b,p,ss=inputs();old={tuple(s['H']) for s in ss};new={};scores=[]
 for f in sorted((OUT/'traversals').glob('*.json.gz')):
  run=read(f)
  if not run['completed']:continue
  frame=run['direction']
  for j,raw in enumerate(run['states']):
   s=dict(raw,H=[frame*v for v in raw['H']],coords=[dict(r,ab=[frame*v for v in r['ab']]) for r in raw['coords']]);h=tuple(s['H']);score=s['score']-s['path'][-1].get('score',0)
   scores.append(dict(file=str(f.relative_to(ROOT)),state=j,H=s['H'],score_without_repeat=score,raw_score=s['score'],duplicated_return_score=s['path'][-1].get('score',0),is_original_H=h in old))
   if h not in old and (h not in new or score>new[h]['score_without_repeat']):new[h]=dict(state=s,source=str(f.relative_to(ROOT)),source_state=j,score_without_repeat=score,frame=frame)
 results=[]
 for H,z in new.items():
  s=z['state'];comparisons=[]
  for family,w in [('A',(7,6)),('B',(6,7))]:
   for direction in [1,-1]:
    rows=oriented_rows(g,ss[0],s,w,direction);comparisons.append(dict(family=family,direction=direction,first=trace_first(rows),rows=rows))
  # Compare actual saved local choices by original window, irrespective of traversal.
  pathmap={r['window']:r for r in s['path'][:-1]};changed=[wi for wi,r in enumerate(ss[0]['path'][:-1]) if pathmap.get(wi,{}).get('patch')!=r.get('patch')];ev=evidence(b,p,s)
  results.append(dict(**z,H=list(H),counts={n:abs(int(np.dot(H,w))) for n,w in WEIGHTS.items()},indexed=len(canonical(s)),returns=len(s['returns']),skips=[r['window'] for r in s['path'] if r.get('skipped')],changed_windows=changed,comparisons=comparisons,evidence_reuse={k:v for k,v in ev.items() if k!='predictions'}))
 save(OUT/'novel-windings.json.gz',dict(alternatives=results,score_audit=scores,policy='Completed lower-ranked windings from rotated starts; retained as conditional hypotheses. Scores from different origins repeat different return contexts, so compare scores after removing that contribution. Still correlated, uncalibrated, and beam-pruned.'))
 # Test count-dependent geometry for the unusual largest-departure winding.
 if results:
  chosen=max(results,key=lambda z:max(abs(z['counts']['A']-2704),abs(z['counts']['B']-2691)));s0=chosen['state'];c=canonical(s0);data=load()[0];pixels={r['id']:np.array(r['pixels_xy']) for r in read(ROOT/'photo2/r324/results/observation-pixels.json')};obs=[o for o in g['observations'] if o['id'] in c and o['id'] in pixels];xy=np.array([o['xy'] for o in obs]);ab=np.array([c[o['id']] for o in obs]);ref=next(o['xy'] for o in obs if o['id']==REF);mask=np.array([1180<=o['xy'][0]<=1505 and 200<o['xy'][1]<390 for o in obs]);trials=[]
  for family,w in [('A',(7,6)),('B',(6,7))]:
   for hand in [-1,1]:
    t=time.perf_counter();N=chosen['counts'][family];W=sum(s0['H']);q=parameters(N,1.95,.85,hand);q.update(winding=W,turn=N/W);q['minor']=q['radius']/np.sin(np.pi/q['turn']);scene,construction=construct(q,data);cert=contacts(scene,seconds=.2);record=dict(H=s0['H'],N=N,W=W,family=family,hand=hand,parameters=scene.p,contact={k:v for k,v in cert.items() if k!='witnesses'},construction=construction)
    options=[]
    for sign in [-1,1]:
     rel=sign*(ab@w)
     for j in np.argsort(np.linalg.norm(scene.pc-ref,axis=1))[:12]:
      addr=int(scene.indices[j]);jj=(addr+rel-scene.indices[0])%N;cost=float(np.mean(np.linalg.norm(scene.pc[jj]-xy,axis=1)[mask]**2));options.append((cost,addr,sign,jj))
    cost,addr,sign,jj=min(options,key=lambda z:z[0]);record['registration']=dict(reference_address=addr,direction=sign,seed_center_proxy_rms=np.sqrt(cost))
    if cert['certified']:
     rows,frac,nr=support_ledger(scene,obs,pixels);record['full_native_ownership']=float(frac[np.arange(len(obs)),jj].mean());record['native_rays']=nr;record['rows']=[dict(r,assigned_index=int(scene.indices[jj[i]]),assigned_fraction=float(frac[i,jj[i]])) for i,r in enumerate(rows)]
    record['seconds']=time.perf_counter()-t;trials.append(record)
  save(OUT/'novel-physical.json.gz',dict(trials=trials,policy='Most unusual new completed winding, own conditional N and W=Ha+Hb. Shared frozen camera and shape; full support pixels, no shaded reflection render.'))
 print('NOVEL',[(z['H'],z['counts'],z['indexed'],z['changed_windows']) for z in results],flush=True)
if __name__=='__main__':main()
