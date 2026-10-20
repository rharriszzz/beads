"""Targeted primitive/topological and target-excluded native consistency, no reindexing."""
from common import *

def fit_target(o,obs,co):
 names=[z for z in co if z!=o and np.linalg.norm(np.array(obs[z]['xy'])-obs[o]['xy'])<70];ref=min(names,key=lambda z:np.linalg.norm(np.array(obs[z]['xy'])-obs[o]['xy']));base=np.array(co[ref]);H=np.array([214,201]);aa=np.array([co[z] for z in names]);aa-=np.rint(((aa-base)@H)/(H@H)).astype(int)[:,None]*H;X=np.c_[aa-base,np.ones(len(names))];xy=np.array([obs[z]['xy'] for z in names]);B=np.linalg.lstsq(X,xy,rcond=None)[0];q=np.linalg.solve(B[:2].T,np.array(obs[o]['xy'])-B[2]);ab=q+base;pred=np.r_[np.array(co[o])-base,1]@B if o in co else None
 return dict(reference=ref,reference_ab=base.tolist(),native_affine_coefficients=B.tolist(),anchors=names,estimated_ab=ab.tolist(),nearest_cell=np.rint(ab).astype(int).tolist(),native_target_error=float(np.linalg.norm(pred-obs[o]['xy'])) if pred is not None else None,native_fit_rms=float(np.sqrt(np.mean(np.sum((X@B-xy)**2,axis=1)))),nearest_cell_prediction=(np.r_[np.rint(ab)-base,1]@B).tolist())
def main():
 g,obs,co,rgb,auth=load();fo={r['id']:r for r in read(OUT/'maker-graph.json.gz')['observations']};p=read(ROOT/'photo2/r341/pattern208.json');targets={o for e in p['entries'] if e['status']=='conflict' and e['residue'] not in [9,35,102,169] for o in e['ids']};checks=[]
 for o in sorted(targets):
  local=[e for e in g['edges'] if o in [e['source'],e['target']]];checks.append(dict(id=o,color=fo[o]['color'],xy=obs[o]['xy'],ab=co[o],degree=len(local),incident_links=local,target_excluded_fit=fit_target(o,obs,co)))
 unindexed=[]
 for o in sorted(set(obs)-set(co)):
  row=fit_target(o,obs,co);cell=row['nearest_cell'];row.update(id=o,color=fo[o]['color'],xy=obs[o]['xy'],hypothetical_residue=(7*cell[0]+6*cell[1])%208,nearest_native_distance=float(min(np.linalg.norm(np.array(obs[z]['xy'])-obs[o]['xy']) for z in co)));row['occupied_by']=[z for z in co if quotient(co[z],g['H'])==quotient(cell,g['H'])];row['adopted']=False;unindexed.append(row)
 comparisons=[]
 for e in p['entries']:
  if e['status']!='conflict' or e['residue'] in [9,35,102,169]:continue
  first=e['ids'][0]
  for o in e['ids'][1:]:
   delta=np.array(co[o])-co[first];shift=int(round((delta[0]-delta[1])/13));adjusted=delta-shift*np.array(g['H']);assert adjusted[0]==adjusted[1] and adjusted[0]%16==0
   comparisons.append(dict(residue=e['residue'],first=first,other=o,delta_ab=delta.tolist(),winding_multiples=shift,translation_16_copies=int(adjusted[0]//16),opposite_colors=fo[first]['color']!=fo[o]['color']))
 # Color-blind enumeration of every cell compatible with the SAME physical
 # neighbors, even allowing primitive-family reassignment. No index score chosen.
 primitives=[(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)];local_tests=[];patch_replays=[]
 for r in checks:
  o=r['id']
  if r['color']!='red':continue
  base=np.array(co[o]);allowed=None
  for e in r['incident_links']:
   z=e['target'] if e['source']==o else e['source'];q=np.array(co[z]);q-=round(((q-base)@g['H'])/np.dot(g['H'],g['H']))*np.array(g['H']);cells={tuple(q-np.array(step)) for step in primitives};allowed=cells if allowed is None else allowed&cells
  alternatives=[]
  for ab in sorted(allowed):
   fit=r['target_excluded_fit'];B=np.array(fit['native_affine_coefficients']);prediction=np.r_[np.array(ab)-fit['reference_ab'],1]@B;error=float(np.linalg.norm(prediction-obs[o]['xy']));occupied=[z for z in co if z!=o and quotient(co[z],g['H'])==quotient(ab,g['H'])];alternatives.append(dict(cell=list(ab),native_prediction=prediction.tolist(),native_error=error,occupied_by=occupied,current=list(ab)==co[o]))
   if list(ab)==co[o]:continue
   patch=copy.deepcopy(read(OUT/'maker-graph.json.gz'));pc={z['id']:z['ab'] for z in patch['coordinates']};pc[o]=list(ab)
   for z in patch['coordinates']:
    if z['id']==o:z['ab']=list(ab)
   changed=[]
   for e in patch['edges']:
    if o not in [e['source'],e['target']]:continue
    d=np.array(pc[e['target']])-pc[e['source']];d-=round((d@g['H'])/np.dot(g['H'],g['H']))*np.array(g['H']);assert tuple(d) in primitives;changed.append(dict(source=e['source'],target=e['target'],old_delta_ab=e['delta_ab'],new_delta_ab=d.tolist()));e['delta_ab']=d.tolist();e['family']='F0' if d[1]==0 else 'F1' if d[0]==0 else 'difference'
   equations=True
   for e in patch['edges']:
    d=np.array(pc[e['target']])-pc[e['source']]-e['delta_ab'];equations&=bool(d[0]*201==d[1]*214 and d[0]%214==0)
   rejection='Reject: native target-excluded continuation misses original source by %.2fpx versus %.2fpx for current site; primitive equations alone do not establish photographic realization.'%(error,fit['native_target_error'])
   save(OUT/'rejected-local-patch.json.gz',dict(graph=patch,source=o,changed_links=changed,old_ab=co[o],new_ab=list(ab),primitive_replay=equations,duplicate_occupancy=bool(occupied),adopted=False,rejection=rejection,occupied_by=occupied));patch_replays.append(dict(id=o,old_ab=co[o],new_ab=list(ab),changed_links=changed,native_error=error,current_native_error=fit['native_target_error'],all2287_equations=equations,duplicate_occupancy=bool(occupied),occupied_by=occupied,adopted=False,rejection=rejection))
  local_tests.append(dict(id=o,degree=r['degree'],all_same_neighbor_primitive_cells=alternatives))
 save(OUT/'consistency.json',dict(targets=checks,unindexed18=unindexed,repeat_pair_equations=comparisons,local_same_neighbor_tests=local_tests,local_patch_replays=patch_replays,policy='All active coordinates and links retained. Color-blind neighbor intersections give a unique cell for five red minority sources; one degree2 source has an alternate primitive cell. Actual patch substitution replays equations but fails native geometry and is rejected. No alternate winding/row campaign or isolated periodicity edit.'))
 print('Unindexed hypothetically wanted',[(r['id'],r['hypothetical_residue'],r['occupied_by'],r['nearest_native_distance']) for r in unindexed if r['hypothetical_residue'] in [43,62,75,82,89,140,147,186]])
 print('Conflict minority native errors',[(r['id'],r['degree'],r['target_excluded_fit']['native_target_error']) for r in checks if r['color']=='red'])
if __name__=='__main__':main()
