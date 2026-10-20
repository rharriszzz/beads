"""Fixed208 analysis after native freeze; fixed IDs, coordinates and folds."""
from explore import *
from photo2.r337.common import save,COLORS,predict,sha
from photo2.r338.analyze import metrics

def main():
 g,obs,co,photo,geom,auth=setup();freeze=read(OUT/'freeze.json');assert freeze['pattern_used'] is False
 final=read(OUT/'graph.json.gz');maker=read(OUT/'maker-graph.json.gz');oldanalysis=read(ROOT/'photo2/r338/analysis/analysis.json.gz');blocks=oldanalysis['blocks'];cohorts=dict(unchanged1040=set(co),original1039={r['id'] for r in read(ROOT/'photo2/r336/results/graph.json.gz')['coordinates']},frozen710=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']),physical450={o for o,r in geom.items() if r['physical_interior'] and o in co});layers=dict(R339=obs,maker={r['id']:r for r in maker['observations']},final={r['id']:r for r in final['observations']});results={name:{c:metrics(oo,co,ids,blocks) for c,ids in cohorts.items()} for name,oo in layers.items()};previous=read(ROOT/'photo2/r339/analysis/pattern208.json');assert results['R339']['unchanged1040']['strict_sequence']==previous['strict_sequence'];transitions=[]
 for i in range(208):
  a,b,c=[results[n]['unchanged1040']['entries'][i] for n in layers]
  if a!=c:transitions.append(dict(residue=i,R339=a,maker=b,final=c))
 changed={o for o in co if obs[o]['color']!=layers['final'][o]['color']};names=sorted(co);kk=np.array([(7*co[o][0]+6*co[o][1])%2704 for o in names]);bb=np.array([blocks[o] for o in names]);ii=np.array([j for j,o in enumerate(names) if o not in changed]);unchanged={}
 for name,oo in layers.items():
  cc=np.array([COLORS.index(oo[o]['color']) for o in names]);scores=[]
  for kind,parent in [('flat',None),('hier104',kk%104)]:
   for hold,occ in [('geographic',None),('whole_occurrence',kk//208)]:
    _,p,b=predict(kk%208,cc,bb,parent=parent,occ=occ);scores.append(dict(model=kind,holdout=hold,n=len(ii),gain_nats=float(np.log(p[ii,cc[ii]]/b[ii,cc[ii]]).mean()),agreement=float((p[ii].argmax(1)==cc[ii]).mean())))
  unchanged[name]=scores
 entries=results['final']['unchanged1040']['entries'];save(OUT/'pattern208.json',dict(length=208,mapping='A = 7a + 6b',N_conditional=2704,repetitions_conditional=13,strict_sequence=results['final']['unchanged1040']['strict_sequence'],entries=entries,supported=results['final']['unchanged1040']['supported'],conflicting=results['final']['unchanged1040']['conflicting'],insufficient=results['final']['unchanged1040']['insufficient'],actual_shortest_complete_pattern_established=False))
 save(OUT/'pattern-analysis.json',dict(results=results,transitions=transitions,unchanged_color_target_scores=unchanged,changed_ids=sorted(changed),remaining_conflicts=[e for e in entries if e['status']=='conflict'],freeze_sha256=sha(OUT/'freeze.json'),policy='All three layers use identical1040 indexed IDs, geometry, folds; original1039/core710/physical450 separately fixed. No new observations, no majority filling, no index/count/period search.'))
 for n,rr in results.items():print(n,[(c,r['n'],r['supported'],r['conflicting'],r['insufficient']) for c,r in rr.items()])
 print('Transitions',[(r['residue'],r['R339']['status'],r['maker']['status'],r['final']['status']) for r in transitions])
if __name__=='__main__':main()
