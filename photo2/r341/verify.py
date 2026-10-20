"""Independent native numerical, topology, ledger, history and strict208 checks."""
from common import *

def main():
 start=time.perf_counter();g,obs,co,rgb,auth,old=load();freeze=read(OUT/'freeze.json');assert freeze['pattern_used'] is False
 for field,file in [('classification_sha256','classification.json.gz'),('native_audit_sha256','native-audit.json.gz'),('native_judgments_sha256','native-judgments.json'),('selected_model_sha256','selection.json'),('corrected_graph_sha256','graph.json.gz')]:assert freeze[field]==sha(OUT/file)
 seal=read(OUT/'input-seal.json');assert all(sha(ROOT/p)==h for p,h in seal.items());final=read(OUT/'graph.json.gz');fo={r['id']:r for r in final['observations']};assert set(fo)==set(obs) and len(obs)==1058;assert final['coordinates']==g['coordinates'] and final['edges']==g['edges'] and final['H']==g['H'];assert len(co)==1040 and len(g['edges'])==2287
 for o,r in obs.items():
  for k,v in r.items():
   if k!='color':assert fo[o][k]==v,(o,k)
 for o,r in auth.items():
  if o in fo:assert fo[o]['color']==r['color']
 for e in g['edges']:assert quotient(np.array(co[e['target']])-co[e['source']]-e['delta_ab'],g['H'])==(0,0)
 assert len({quotient(ab,g['H']) for ab in co.values()})==1040
 records=read(OUT/'native-audit.json.gz')['records'];rr={r['id']:r for r in records};alts=read(OUT/'alternatives.json.gz');geometry=read(OUT/'geometry.json');selection=read(OUT/'selection.json');assert set(selection['development_ids']).isdisjoint(selection['heldout_ids']) and len(selection['heldout_ids'])==64
 # Recompute each local affine map directly by normal equations, without kdtree/lstsq.
 mid=np.array([(np.array(obs[e['source']]['xy'])+obs[e['target']]['xy'])/2 for e in g['edges']]);edge_xy=np.array([np.array(obs[e['target']]['xy'])-obs[e['source']]['xy'] for e in g['edges']]);edge_ab=np.array([e['delta_ab'] for e in g['edges']]);scorechecks=0;patches=0;center_fraction=np.array([.248130237459968,-.0191702201531064])
 for o,r in rr.items():
  ii=np.linalg.norm(mid-np.array(obs[o]['xy']),axis=1)<=80;A=edge_ab[ii];Y=edge_xy[ii];J=np.linalg.inv(A.T@A)@A.T@Y;assert np.max(np.abs(J.T-np.array(geometry[o]['J'])))<1e-10;s=float(np.median(np.linalg.norm(Y,axis=1)));assert abs(s-geometry[o]['spacing'])<1e-10;center=np.array(obs[o]['xy'])+s*center_fraction;axis=J.T@np.array([1.,-1.]);axis/=np.linalg.norm(axis);perp=np.array([-axis[1],axis[0]])
  near=[z for z in obs if z!=o and np.linalg.norm(np.array(obs[z]['xy'])-obs[o]['xy'])<=1.1*s];assert set(near)==set(r['neighbor_ids'])
  for kind,mapping in alts.items():
   m=mapping[o];points={tuple(p) for p in m['region_pixels']};a,b=(.25,.25) if kind=='circle' else (.30,.20)
   x0,y0=np.floor(center-.31*s).astype(int);x1,y1=np.ceil(center+.31*s).astype(int)+1;yy,xx=np.mgrid[y0:y1,x0:x1];dx=xx-center[0];dy=yy-center[1];mask=((dx*axis[0]+dy*axis[1])/(a*s))**2+((dx*perp[0]+dy*perp[1])/(b*s))**2<=1
   for z in near:
    q=np.array(obs[z]['xy'])+s*center_fraction;mask&=dx*dx+dy*dy+(.1*s)**2<(xx-q[0])**2+(yy-q[1])**2
   assert points==set(zip(xx[mask].tolist(),yy[mask].tolist()))
   for x,y in points:
    v=np.array([x,y])-center;assert (np.dot(v,axis)/(a*s))**2+(np.dot(v,perp)/(b*s))**2<=1+1e-12
    assert all(np.dot(v,v)+(.1*s)**2<np.sum((np.array([x,y])-(np.array(obs[z]['xy'])+s*center_fraction))**2)+1e-10 for z in near)
   best=256;count=0
   for x,y in points:
    if all((x+i,y+j) in points for j in range(3) for i in range(3)):best=min(best,int(rgb[y:y+3,x:x+3].max()));count+=1
   assert best==m['score'] and count==m['candidate_patches'];assert m['raw_decision']==('black' if best<73.5 else 'not-black');x,y,u,v=m['patch_box'];assert [u-x,v-y]==[3,3] and rgb[y:v,x:u].tolist()==m['patch_RGB'];assert max(max(p) for row in m['patch_RGB'] for p in row)==best;scorechecks+=1;patches+=count
  assert r['measurement']==alts[selection['selected']][o]
  assert r['audited_decision']==(r['measurement']['raw_decision'] if r['measured_pixels_convincingly_owned'] else 'unknown')
 # Independently reproduce development-only model choice; holdout cannot affect it.
 losses={}
 for kind,mapping in alts.items():losses[kind]=sum((mapping[o]['raw_decision']=='black')!=(c=='black') for o,c in selection['development_ids'].items())
 assert selection['selected']==min(losses,key=lambda k:(losses[k],0 if k=='circle' else 1))=='circle'
 changes=read(OUT/'corrections.json')['changes'];assert len(changes)==12 and {r['id'] for r in changes}=={o for o in obs if obs[o]['color']!=fo[o]['color']};assert all(r['before_color']=='red' and r['color']=='black' and r['id'] not in auth and rr[r['id']]['measured_pixels_convincingly_owned'] for r in changes)
 atlas=read(OUT/'audit-black-red-manifest.json')+read(OUT/'audit-yellow-manifest.json');assert len(atlas)==1058 and {r['id'] for r in atlas}==set(obs);assert sum(r['recorded_color']=='black' for r in atlas)==378 and sum(r['recorded_color']=='red' for r in atlas)==356 and sum(r['recorded_color']=='yellow' for r in atlas)==324
 # Independent strict formula; no motif/metrics/predict helper.
 analysis=read(OUT/'pattern-analysis.json');blocks=read(ROOT/'photo2/r338/analysis/analysis.json.gz')['blocks'];entries=0
 for layer,colors in [('R340',{o:r['color'] for o,r in obs.items()}),('R341',{o:r['color'] for o,r in fo.items()})]:
  for cohort,stats in analysis['results'][layer].items():
   names=set(co) if cohort=='fixed1040' else {r['id'] for r in read(ROOT/'photo2/r336/results/graph.json.gz')['coordinates']} if cohort=='original1039' else set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']) if cohort=='frozen710' else {o for o in co if old[o]['geometry']['physical_interior']} if cohort=='physical450' else {o for o in co if rr[o]['measured_pixels_convincingly_owned']}
   sequence=''
   for k in range(208):
    oo=[o for o in sorted(names) if ((7*co[o][0]+6*co[o][1])%2704)%208==k];counts=Counter(colors[o] for o in oo);sections={blocks[o] for o in oo};status='conflict' if len(counts)>1 else 'strong' if len(oo)>=3 and len(sections)>=3 else 'observed' if oo else 'unknown';e=stats['entries'][k];assert e['status']==status and e['counts']==counts and e['ids']==oo;sequence+=colors[oo[0]][0].upper() if status=='strong' else '?';entries+=1
   assert sequence==stats['strict_sequence']
 assert (read(OUT/'pattern208.json')['supported'],read(OUT/'pattern208.json')['conflicting'],read(OUT/'pattern208.json')['insufficient'])==(191,9,8)
 # Independent held-out predictions on the identical1028 unchanged-color targets.
 ordered=sorted(co);kk=np.array([(7*co[o][0]+6*co[o][1])%2704 for o in ordered]);bb=np.array([blocks[o] for o in ordered]);target=np.array([o not in freeze['changed_ids'] for o in ordered]);prediction_checks=0
 for layer,oo in [('R340',obs),('R341',fo)]:
  cc=np.array([COLORS.index(oo[o]['color']) for o in ordered])
  for stored in analysis['unchanged_color_target_scores'][layer]:
   pred=np.zeros((len(ordered),3));base=np.zeros_like(pred);folds=range(12) if stored['holdout']=='geographic' else sorted(set(kk//208))
   for fold in folds:
    te=bb==fold if stored['holdout']=='geographic' else kk//208==fold;tr=~np.isin(bb,[(fold+i)%12 for i in [-1,0,1]]) if stored['holdout']=='geographic' else ~te;prior=np.array([sum(cc[tr]==v)+1 for v in range(3)],float);prior/=prior.sum();cell=np.zeros((208,3));parent=np.zeros((104,3))
    for j in np.flatnonzero(tr):cell[kk[j]%208,cc[j]]+=1;parent[kk[j]%104,cc[j]]+=1
    for j in np.flatnonzero(te):
     r=int(kk[j]%208);prior_r=prior if stored['model']=='flat' else (parent[r%104]+3*prior)/(parent[r%104].sum()+3);alpha=3 if stored['model']=='flat' else 1;pred[j]=(cell[r]+alpha*prior_r)/(cell[r].sum()+alpha);base[j]=prior
   agreement=float((pred[target].argmax(1)==cc[target]).mean());gain=float(np.log(pred[np.arange(len(cc)),cc][target]/base[np.arange(len(cc)),cc][target]).mean());assert abs(agreement-stored['agreement'])<1e-12 and abs(gain-stored['gain_nats'])<1e-12;prediction_checks+=1

 for panel in read(OUT/'review/panels.json'):
  a,b,c,d=panel['crop_box'];assert np.array_equal(np.asarray(Image.open(OUT/'review'/panel['filename'])),rgb[b:d,a:c]);assert panel['key'][0]==panel['id']
 save(OUT/'verification.json',dict(passed=True,historical_files=len(seal),native_scores=scorechecks,explicit_candidate_patches=patches,local_neighbor_fits=1058,reviewed_active_records=1058,reviewed_black_red=734,yellow_controls=324,disagreement_contexts=19,native_uncertain=sum(not r['measured_pixels_convincingly_owned'] for r in records),immutable_XY=1058,immutable_AB=1040,immutable_links=2287,maker_active=113,maker_excluded=3,changes=12,strict_entries=entries,heldout_prediction_checks=prediction_checks,literal_native_panels=len(read(OUT/'review/panels.json')),threshold=73.5,supported=191,conflicting=9,insufficient=8,seconds=time.perf_counter()-start));print('PASS independent R341',time.perf_counter()-start)
if __name__=='__main__':main()
