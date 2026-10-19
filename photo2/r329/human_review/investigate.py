"""Bounded G/H diagnostic controls. No search, model fit or graph mutation."""
from photo2.r329.photographic_diagnostics.continuity import *
from scipy.spatial import ConvexHull
HERE=Path(__file__).resolve().parent

def main():
 start=time.perf_counter();out={}
 for name in ['G','H']:
  c=CASES[name];alt=c['alt'];states=['working',alt];rows=[]
  # Remove each reference chain in turn, not merely each individual vector.
  # H additionally excludes the reference that uses an observation absent in its alternative.
  configs=[('all',c)]+[(f'leave_row_{j}',dict(c,rows=[r for i,r in enumerate(c['rows']) if i!=j])) for j in range(len(c['rows']))]
  for radius in [16,18,20]:
   for threshold in [.95,1,1.05]:
    ids=set([c['anchor'],c['target']]+[o for _,seq,_ in c['rows'] for o in seq]);pts={o:measure(OBS[o],radius,threshold)[0] for o in ids}
    for label,cc in configs:
     vv=vectors(cc,pts)
     for bw in [35,55,85]:
      ev={}
      for st in states:
       delta=np.array(CO[st][c['target']])-CO[st][c['anchor']];pp=predict(vv,pts[c['anchor']],delta,bw)
       ev[st]=dict(errors=np.linalg.norm(pp-pts[c['target']],axis=1).tolist(),prediction=pp.tolist())
      rows.append(dict(reference=label,radius=radius,threshold=threshold,bandwidth=bw,results=ev))
  # More held-out colored targets, shared upstream anchors, affine versus curved.
  box=c['box'];allids=[o for o in OBS if OBS[o]['color']!='black' and box[0]-30<OBS[o]['xy'][0]<box[2]+30 and box[1]-30<OBS[o]['xy'][1]<box[3]+30]
  shared=[o for o in allids if o in CO['working'] and o in CO[alt] and CO['working'][o]==CO[alt][o]]
  targets=([c['target'],'C-1669-0293','NEW-1697-280','E5-1671-0325'] if name=='G' else [c['target'],'C-1119-2879','C-1098-2901','NEW-1074-2896','C-1144-2947'])
  fits=[];availability={o:[measure(OBS[o],r,t) is not None for r in [16,18,20] for t in [.95,1,1.05]] for o in shared};stable=[o for o in shared if all(availability[o])]
  for radius in [16,18,20]:
   for threshold in [.95,1,1.05]:
    mm={o:measure(OBS[o],radius,threshold) for o in set(shared+targets)};pts={o:v[0] for o,v in mm.items() if v is not None};train=[o for o in shared if o in pts and o not in targets]
    for cohort,deg in [(cc,dd) for cc in ['available','fixed'] for dd in [1,2]]:
     train=[o for o in (shared if cohort=='available' else stable) if o in pts and o not in targets]
     for st in states:
      test=[o for o in targets if o in CO[st] and o in pts];pr=fit(CO[st],pts,train,test,deg)
      if pr is None:continue
      # Independent leave-one-anchor-out errors expose extrapolation sensitivity.
      errors=[]
      for o in train:
       p=fit(CO[st],pts,[x for x in train if x!=o],[o],deg)
       if p is not None:errors.append(float(np.linalg.norm(p[0]-pts[o])))
      fits.append(dict(cohort=cohort,radius=radius,threshold=threshold,degree=deg,state=st,train=train,targets={o:dict(prediction=p.tolist(),measured=pts[o].tolist(),error=float(np.linalg.norm(p-pts[o]))) for o,p in zip(test,pr)},anchor_control_errors=errors))
  # Check the assumption that reference intervals are shared between candidates.
  audit=[]
  for j,(family,seq,steps) in enumerate(c['rows']):
   for a,b,n in zip(seq,seq[1:],steps):
    vals={st:(np.array(CO[st][b])-CO[st][a]).tolist() if a in CO[st] and b in CO[st] else None for st in states};audit.append(dict(row=j,a=a,b=b,claimed_family=family,claimed_steps=n,deltas=vals,shared=vals[states[0]]==vals[states[1]]))
  out[name]=dict(config=c,transfer_controls=rows,shared_anchor_fits=fits,shared_colored_anchors=shared,stable_shared_anchors=stable,anchor_availability=availability,reference_audit=audit)
  print(name,'shared',len(shared))
  for label,_ in configs:
   selected=[r for r in rows if r['reference']==label];print(label,{st:[round(float(v),2) for v in np.percentile([e for r in selected for e in r['results'][st]['errors']],[0,50,100])] for st in states})
  for deg in [1,2]:
   print('degree',deg)
   for st in states:
    ff=[f for f in fits if f['degree']==deg and f['state']==st and f['cohort']=='fixed']
    for target in targets:
     err=[f['targets'][target]['error'] for f in ff if target in f['targets']]
     if err:print(st,target,np.round(np.percentile(err,[0,50,100]),2))
   ee=[e for f in fits if f['degree']==deg and f['cohort']=='fixed' for e in f['anchor_control_errors']];print('anchor leaveout',np.round(np.percentile(ee,[0,50,100]),2) if ee else 'unavailable: rank deficient')
  print('nonshared refs',[r for r in audit if not r['shared']])
 gzip.open(HERE/'investigation.json.gz','wt').write(json.dumps(dict(cases=out,seconds=time.perf_counter()-start),indent=2)+'\n')
if __name__=='__main__':main()
