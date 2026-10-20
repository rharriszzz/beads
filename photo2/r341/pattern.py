"""Strict208 after immutable photographic freeze; no color feedback."""
from common import *
from photo2.r338.analyze import metrics
from photo2.r337.common import predict

def main():
 g,obs,co,rgb,auth,old=load();freeze=read(OUT/'freeze.json');assert freeze['pattern_used'] is False and freeze['native_audit_sha256']==sha(OUT/'native-audit.json.gz');final=read(OUT/'graph.json.gz');fo={r['id']:r for r in final['observations']};oldana=read(ROOT/'photo2/r338/analysis/analysis.json.gz');blocks=oldana['blocks'];audit={r['id']:r for r in read(OUT/'native-audit.json.gz')['records']};cohorts=dict(fixed1040=set(co),original1039={r['id'] for r in read(ROOT/'photo2/r336/results/graph.json.gz')['coordinates']},frozen710=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']),physical450={o for o,r in old.items() if r['geometry']['physical_interior'] and o in co},native_owned_common={o for o,r in audit.items() if r['measured_pixels_convincingly_owned'] and o in co});results={name:{c:metrics(oo,co,ids,blocks) for c,ids in cohorts.items()} for name,oo in [('R340',obs),('R341',fo)]};assert results['R340']['fixed1040']['strict_sequence']==read(ROOT/'photo2/r340/autoregion/pattern208.json')['strict_sequence'];transitions=[]
 for k in range(208):
  a=results['R340']['fixed1040']['entries'][k];b=results['R341']['fixed1040']['entries'][k]
  if a!=b:transitions.append(dict(residue=k,R340=a,R341=b,changes=[o for o in freeze['changed_ids'] if o in b['ids']]))
 names=sorted(co);kk=np.array([(7*co[o][0]+6*co[o][1])%2704 for o in names]);bb=np.array([blocks[o] for o in names]);ii=np.array([j for j,o in enumerate(names) if o not in freeze['changed_ids']]);unchanged={}
 for name,oo in [('R340',obs),('R341',fo)]:
  cc=np.array([COLORS.index(oo[o]['color']) for o in names]);scores=[]
  for kind,parent in [('flat',None),('hier104',kk%104)]:
   for hold,occ in [('geographic',None),('whole_occurrence',kk//208)]:
    _,p,b=predict(kk%208,cc,bb,parent=parent,occ=occ);scores.append(dict(model=kind,holdout=hold,n=len(ii),gain_nats=float(np.log(p[ii,cc[ii]]/b[ii,cc[ii]]).mean()),agreement=float((p[ii].argmax(1)==cc[ii]).mean())))
  unchanged[name]=scores
 entries=results['R341']['fixed1040']['entries'];contradictions=[]
 for e in entries:
  maker=[dict(id=o,color=auth[o]['color'],xy=obs[o]['xy'],ab=co[o]) for o in e['ids'] if o in auth];owned=[dict(id=o,color=fo[o]['color'],xy=obs[o]['xy'],ab=co[o]) for o in e['ids'] if audit[o]['measured_pixels_convincingly_owned']]
  if len({r['color'] for r in maker})>1:contradictions.append(dict(residue=e['residue'],maker_records=maker,meaning='Exact208 cannot fit these authoritative colors simultaneously under fixedA indexing; no majority solution.'))
 sequence=results['R341']['fixed1040']['strict_sequence'];save(OUT/'pattern208.json',dict(length=208,mapping='A=7a+6b',N_conditional=2704,repetitions_conditional=13,strict_sequence=sequence,entries=entries,supported=results['R341']['fixed1040']['supported'],conflicting=results['R341']['fixed1040']['conflicting'],insufficient=results['R341']['fixed1040']['insufficient'],actual_shortest_complete_pattern_established=False,exact208_compatible_with_all_authoritative_labels=not bool(contradictions)))
 save(OUT/'pattern-analysis.json',dict(results=results,transitions=transitions,unchanged_color_target_scores=unchanged,maker_contradictions=contradictions,remaining_conflicts=[e for e in entries if e['status']=='conflict'],insufficient_positions=[e for e in entries if e['status']=='observed'],photographic_freeze_sha256=sha(OUT/'freeze.json'),policy='Identical cohort IDs/XY/AB/H/folds across layers. Native-owned subset separately fixed, never counted as disappearance of full-cohort conflicts. Maker contradictions preserved; no broad period/winding search or majority filling.'))
 for name,rr in results.items():print(name,[(c,r['n'],r['supported'],r['conflicting'],r['insufficient']) for c,r in rr.items()])
 print('Resolved',[(e['residue'],e['changes']) for e in transitions if e['R341']['status']=='strong']);print('Maker contradictions',[(e['residue'],[(r['id'],r['color']) for r in e['maker_records']]) for e in contradictions]);print('Remaining',[e['residue'] for e in entries if e['status']=='conflict'])
if __name__=='__main__':main()
