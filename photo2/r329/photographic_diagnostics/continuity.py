"""Colored-material-only, same-family row-transfer diagnostic.
Historical coordinates specify the tested hypothesis, not the measured geometry.
No black observation coordinate, pixel, intensity or reflection enters prediction.
"""
from .explore import *
from itertools import permutations
import math,time
CASES={
 'E':dict(alt='closest',anchor='C-1721-1566',target='C-1770-1577',black='K-1740-1575',last='MAT25-K-1719-1592',box=[1600,1450,1810,1650],
  rows=[(0,['C-1721-1566','C-1717-1540','C-1705-1514'],[1,1]),(0,['C-1775-1637','C-1777-1612'],[1]),(0,['E5-1694-1563','C-1677-1513','C-1648-1459'],[2,2]),(1,['C-1721-1566','E5-1694-1563','C-1669-1561'],[1,1]),(1,['C-1705-1514','C-1677-1513','C-1621-1521'],[1,2]),(1,['C-1775-1637','C-1749-1623'],[1])]),
 'G':dict(alt='early',anchor='E5-1633-0278',target='P5-1645-0309',black='NEW-1621-315',last='C-1608-0253',box=[1525,220,1710,350],
  rows=[(0,['C-1559-0252','C-1582-0272','E5-1607-0290'],[1,1]),(0,['C-1582-0235','C-1608-0253','E5-1633-0278'],[1,1]),(1,['NEW-1538-305','E5-1561-0289','C-1582-0272','C-1608-0253'],[1,1,1]),(1,['C-1585-0307','E5-1607-0290','E5-1633-0278','C-1659-0261'],[1,1,1])]),
 'H':dict(alt='lower',anchor='E5-1151-2893',target='C-1125-2900',black='NEW-1132-2925',last='E5-1151-2893',omitted='C-1144-2947',box=[1050,2800,1230,2985],
  rows=[(0,['C-1209-2970','C-1198-2943','C-1189-2919'],[1,1]),(0,['C-1098-2901','C-1095-2873','C-1085-2813'],[1,2]),(0,['NEW-1074-2896','C-1064-2868','C-1058-2815'],[1,2]),(1,['C-1119-2879','C-1095-2873','C-1064-2868'],[1,1]),(1,['C-1098-2901','NEW-1074-2896'],[1]),(1,['C-1198-2943','C-1144-2947'],[2])]),
 'F':dict(alt='working',anchor='C-1422-0264',target='C-1391-0312',black='K-1398-0248',last='C-1302-0316',box=[1240,220,1505,355],
  rows=[(0,['C-1251-0290','C-1277-0302','C-1302-0316','C-1324-0332'],[1,1,1]),(0,['C-1279-0252','C-1311-0261','C-1339-0277','P5-1364-0299','C-1391-0312'],[1,1,1,1]),(0,['NEW-1442-248','C-1467-0258','C-1497-0271'],[1,1]),(1,['C-1302-0316','C-1339-0277','NEW-1355-256'],[2,1]),(1,['C-1391-0312','C-1422-0264','NEW-1442-248'],[2,1])])}

def vectors(c,pts,omit=None):
 out=[]
 for family,seq,steps in c['rows']:
  for a,b,n in zip(seq,seq[1:],steps):
   if omit is not None and (a,b)==omit:continue
   if a not in pts or b not in pts:continue
   assert OBS[a]['color']!='black' and OBS[b]['color']!='black'
   out.append(dict(family=family,a=a,b=b,steps=n,mid=(pts[a]+pts[b])/2,v=(pts[b]-pts[a])/n))
 return out

def field(vectors,point,family,bandwidth=55):
 # Never pool the two diagonals; curvature is represented by local variation
 # of measured vectors within this family. No orthogonality/equal-size constraint.
 rr=[r for r in vectors if r['family']==family]
 if not rr:raise ValueError('No same-family reference')
 dist=np.array([np.linalg.norm(r['mid']-point) for r in rr]);wt=np.exp(-.5*(dist/bandwidth)**2);wt/=wt.sum()
 return np.sum(np.array([r['v'] for r in rr])*wt[:,None],axis=0)

def predict(vectors,anchor,delta,bandwidth=55):
 steps=[(d,1 if n>0 else -1) for d,n in enumerate(delta) for _ in range(abs(n))]
 paths=sorted(set(permutations(steps)))
 if not paths:return np.array([anchor])
 out=[]
 for path in paths:
  p=np.array(anchor,copy=True)
  for family,sign in path:
   v=field(vectors,p,family,bandwidth);p=p+sign*field(vectors,p+.5*sign*v,family,bandwidth)
  out.append(p)
 return np.array(out)

def angle(v):return float(np.degrees(np.arctan2(v[1],v[0]))%180)
def angle_diff(a,b):return abs((a-b+90)%180-90)

def run():
 t=time.perf_counter();output={}
 for name,c in CASES.items():
  ids=list(dict.fromkeys([c['anchor'],c['target'],c['last']]+[o for _,seq,_ in c['rows'] for o in seq]+([c['omitted']] if 'omitted' in c else [])))
  colored=[o for o in ids if OBS[o]['color']!='black'];variants=[];base=None
  for radius in [16,18,20]:
   for threshold in [.95,1.,1.05]:
    mm={o:measure(OBS[o],radius,threshold) for o in colored}
    if any(v is None for v in mm.values()):continue
    pts={o:v[0] for o,v in mm.items()};vv=vectors(c,pts)
    if radius==18 and threshold==1.:base=dict(measurements={o:dict(center=v[0].tolist(),pixels=v[1].tolist(),color=OBS[o]['color']) for o,v in mm.items()},vectors=[dict(r,mid=r['mid'].tolist(),v=r['v'].tolist()) for r in vv])
    for bw in [35,55,85]:
     pred={}
     for state in dict.fromkeys(['working',c['alt']]):
      co=CO[state];delta=tuple(co[c['target']][i]-co[c['anchor']][i] for i in range(2));blackdelta=tuple(co[c['black']][i]-co[c['anchor']][i] for i in range(2));pp=predict(vv,pts[c['anchor']],delta,bw);bb=predict(vv,pts[c['anchor']],blackdelta,bw)
      pred[state]=dict(target_delta=delta,black_delta=blackdelta,target_predictions=pp.tolist(),black_predictions=bb.tolist(),errors=np.linalg.norm(pp-pts[c['target']],axis=1).tolist())
     # Same-family held-out reference intervals calibrate local transfer error.
     controls=[]
     for r in vv:
      other=vectors(c,pts,(r['a'],r['b']));delta=[0,0];delta[r['family']]=r['steps'];pp=predict(other,pts[r['a']],delta,bw)
      controls.append(dict(a=r['a'],b=r['b'],family=r['family'],steps=r['steps'],error=float(np.linalg.norm(pp.mean(0)-pts[r['b']])),per_step=float(np.linalg.norm(pp.mean(0)-pts[r['b']])/r['steps'])))
     variants.append(dict(radius=radius,threshold=threshold,bandwidth=bw,predictions=pred,controls=controls))
  assert base is not None
  central=next(v for v in variants if v['radius']==18 and v['threshold']==1 and v['bandwidth']==55)
  summaries={}
  for state in dict.fromkeys(['working',c['alt']]):
   errs=[e for v in variants for e in v['predictions'][state]['errors']];bp=[p for v in variants for p in v['predictions'][state]['black_predictions']];tp=[p for v in variants for p in v['predictions'][state]['target_predictions']]
   summaries[state]=dict(error_min=min(errs),error_median=float(np.median(errs)),error_max=max(errs),black_position_median=np.median(bp,0).tolist(),black_position_range=[np.min(bp,0).tolist(),np.max(bp,0).tolist()],target_position_median=np.median(tp,0).tolist(),target_position_range=[np.min(tp,0).tolist(),np.max(tp,0).tolist()])
  # Direction estimates are derived only from colored-body displacement vectors.
  fam=[];p0=np.array(base['measurements'][c['anchor']]['center']);vv=[dict(r,mid=np.array(r['mid']),v=np.array(r['v'])) for r in base['vectors']];bridge=np.array(base['measurements'][c['target']]['center'])-p0
  for family in [0,1]:
   v=field(vv,p0,family);angles=[angle(r['v']) for r in vv if r['family']==family];spread=max(angle_diff(a,angle(v)) for a in angles)
   fam.append(dict(family=family,vector=v.tolist(),angle_degrees=angle(v),observed_reference_angle_spread=spread,bridge_angle_deviation=angle_diff(angle(bridge),angle(v)),reference_angles=angles))
  output[name]=dict(config=c,**base,variants=variants,central=central,summaries=summaries,estimated_families=fam,bridge_angle=angle(bridge),policy='Black feature coordinates and light are excluded. Colored material centroids are partial-region proxies, not measured body centers. Reference row sequences are photo-reviewed proposals from shared nearby structure; gap step counts remain conditional. Family-specific displacement fields remain separate. 27 mask/locality variants and both step orders retained; ranges are sensitivity, not statistical confidence intervals.')
  print(name,summaries,'families',fam)
 gzip.open(OUT/'continuity.json.gz','wt').write(json.dumps(dict(cases=output,seconds=time.perf_counter()-t),indent=2)+'\n')
 return output
if __name__=='__main__':run()
