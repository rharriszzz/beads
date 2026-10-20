"""Independent native pixels, geometry, preserved history and strict208 counts."""
from explore import *
from photo2.r337.common import sha,save,quotient
from collections import Counter
import time

def main():
 start=time.perf_counter();g,obs,co,photo,geom,auth=setup();data=read(OUT/'classification.json');freeze=read(OUT/'freeze.json');final=read(OUT/'graph.json.gz');fo={r['id']:r for r in final['observations']};assert freeze['pattern_used'] is False
 seal=read(OUT/'input-seal.json');assert all(sha(ROOT/p)==h for p,h in seal.items());assert freeze['classification_sha256']==sha(OUT/'classification.json');assert freeze['model_sha256']==sha(OUT/'rectangle-model.json')
 assert set(fo)==set(obs) and len(fo)==1058;assert final['coordinates']==g['coordinates'] and final['edges']==g['edges'] and final['H']==g['H'];assert all(fo[o]['xy']==obs[o]['xy'] for o in obs);assert all(fo[o]['color']==r['color'] for o,r in auth.items() if o in fo)
 changed={o for o in obs if fo[o]['color']!=obs[o]['color']};assert changed=={'E5-2272-1815','E5-2139-2470','NEW-1036-2833','NEW-1702-1860','NEW-903-2501'};assert len(freeze['maker_decisions'])==6 and sum(r['changed'] for r in freeze['maker_decisions'])==1
 for o,old in obs.items():
  for k,v in old.items():
   if k!='color':assert fo[o][k]==v,(o,k)
 for e in g['edges']:assert quotient(np.array(co[e['target']])-co[e['source']]-e['delta_ab'],g['H'])==(0,0)
 assert len({quotient(ab,g['H']) for ab in co.values()})==1040
 # Independently reconstruct common all-color local spacing directly from2287 links.
 mids=np.array([(np.array(obs[e['source']]['xy'])+obs[e['target']]['xy'])/2 for e in g['edges']]);lengths=np.array([np.linalg.norm(np.array(obs[e['source']]['xy'])-obs[e['target']]['xy']) for e in g['edges']]);samples=0
 manual=read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records'];train=[r for r in manual if r['number']%2==1];bounds=np.median([(np.array(r['absolute_material_box'])-np.tile(r['xy'],2))/geom[r['id']]['spacing'] for r in train],axis=0);assert np.array_equal(bounds,np.array(data['model']['bounds_fraction']))
 physics={r['id'] for r in read(ROOT/'photo2/r338/analysis/analysis.json.gz')['physical_interior_records'] if r['physical_interior']};eligible=set()
 for r in data['records']:
  o=r['id'];p=np.array(obs[o]['xy']);s=float(np.median(lengths[np.linalg.norm(mids-p,axis=1)<100]));assert abs(s-r['geometry']['spacing'])<1e-10
  box=np.rint(np.tile(p,2)+s*bounds).astype(int).tolist();m=r['measurement'];assert box==m['region_box'];a,b,c,d=box;score=256
  for y in range(b,d-2):
   for x in range(a,c-2):score=min(score,max(int(photo[y+j,x+i,k]) for j in range(3) for i in range(3) for k in range(3)));samples+=1
  assert score==m['score'];x,y,u,v=m['patch_box'];assert [u-x,v-y]==[3,3];assert np.asarray(m['patch_RGB']).tolist()==photo[y:v,x:u].tolist();assert max(max(vv) for row in m['patch_RGB'] for vv in row)==score;assert m['decision']==('black' if score<73.5 else 'not-black')
  if o in physics and o in co:eligible.add(o);assert r['decision']==m['decision']
  else:assert r['decision']=='unknown'
 assert len(eligible)==450
 # Independent strict consensus checks without calling motif/metrics/predict.
 analysis=read(OUT/'pattern-analysis.json');blocks=read(ROOT/'photo2/r338/analysis/analysis.json.gz')['blocks'];graphs=dict(R339=g,maker=read(OUT/'maker-graph.json.gz'),final=final);cohorts=dict(unchanged1040=set(co),original1039={r['id'] for r in read(ROOT/'photo2/r336/results/graph.json.gz')['coordinates']},frozen710=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']),physical450=eligible);checks=0
 for layer,graph in graphs.items():
  colors={r['id']:r['color'] for r in graph['observations']}
  for cohort,ids in cohorts.items():
   counts=Counter();seq=''
   for k in range(208):
    oo=[o for o in sorted(ids) if ((7*co[o][0]+6*co[o][1])%2704)%208==k];cc=Counter(colors[o] for o in oo);sections={blocks[o] for o in oo};status='conflict' if len(cc)>1 else 'strong' if len(oo)>=3 and len(sections)>=3 else 'observed' if oo else 'unknown';counts[status]+=1;e=analysis['results'][layer][cohort]['entries'][k];assert e['status']==status and e['counts']==cc and e['ids']==oo;seq+=colors[oo[0]][0].upper() if status=='strong' else '?';checks+=1
   assert seq==analysis['results'][layer][cohort]['strict_sequence']
 pattern=read(OUT/'pattern208.json');assert (pattern['supported'],pattern['conflicting'],pattern['insufficient'])==(181,19,8)
 evaluation=read(OUT/'evaluation.json');assert evaluation['cohorts']['manual48']['raw']['FP']==evaluation['cohorts']['manual48']['raw']['FN']==0;assert evaluation['cohorts']['all_maker113']['raw']['FN']==1 and evaluation['cohorts']['all_maker113']['raw']['FP']==0
 for r in read(OUT/'review/literal-crops.json'):assert np.array_equal(np.asarray(Image.open(OUT/'review'/r['raw'])),photo[r['crop_box'][1]:r['crop_box'][3],r['crop_box'][0]:r['crop_box'][2]])
 save(OUT/'verification.json',dict(passed=True,historical_files=len(seal),active_pixel_scores=1058,explicit_native3x3_candidates=samples,neighbor_spacing_checks=1058,unchanged_native_XY=1058,unchanged_lattice_coordinates=1040,unchanged_primitive_equations=2287,unique_bead_quotients=1040,maker_colors_protected=sum(o in obs for o in auth),maker_decisions=6,changed_colors=5,automatic_corrections=4,edge_screen_unchanged450=True,independent_strict_entries=checks,literal_native_crops=9,supported=181,conflicting=19,insufficient=8,seconds=time.perf_counter()-start));print('PASS R340 independent verification',time.perf_counter()-start)
if __name__=='__main__':main()
