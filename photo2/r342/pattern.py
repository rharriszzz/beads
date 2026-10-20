"""Fixed208 analysis only after photo freeze; unchanged cohorts, explicit exclusions."""
from common import *
from photo2.r338.analyze import metrics
from photo2.r337.common import predict

def main():
 g,obs,co,rgb,auth=load();freeze=read(OUT/'freeze.json');assert sha(OUT/'graph.json.gz')==freeze['graph_sha256'];fo={r['id']:r for r in read(OUT/'graph.json.gz')['observations']};blocks=read(ROOT/'photo2/r338/analysis/analysis.json.gz')['blocks'];old=read(ROOT/'photo2/r341/pattern208.json');cohorts=dict(full1040=set(co),same_without_Q102=set(co)-{'NEW-1681-1498'},same_without_Q169=set(co)-{'R332-R-0077-0077'},same_without_both=set(co)-{'NEW-1681-1498','R332-R-0077-0077'},frozen710=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']),original1039={r['id'] for r in read(ROOT/'photo2/r336/results/graph.json.gz')['coordinates']});results={n:{c:metrics(oo,co,ids,blocks) for c,ids in cohorts.items()} for n,oo in [('R341',obs),('R342',fo)]};after=results['R342']['full1040'];assert results['R341']['full1040']['strict_sequence']==old['strict_sequence']
 transitions=[dict(residue=i,before=old['entries'][i],after=e,causal_changes=[o for o in MAKER if o in e['ids']]) for i,e in enumerate(after['entries']) if old['entries'][i]!=e]
 names=sorted(co);kk=np.array([(7*co[o][0]+6*co[o][1])%2704 for o in names]);bb=np.array([blocks[o] for o in names]);unchanged=np.array([i for i,o in enumerate(names) if o not in MAKER]);held={}
 for layer,oo in [('R341',obs),('R342',fo)]:
  cc=np.array([COLORS.index(oo[o]['color']) for o in names]);rows=[]
  for model,parent in [('flat',None),('hier104',kk%104)]:
   for hold,occ in [('geographic',None),('whole_occurrence',kk//208)]:
    _,p,b=predict(kk%208,cc,bb,parent=parent,occ=occ);rows.append(dict(model=model,holdout=hold,n=len(unchanged),agreement=float((p[unchanged].argmax(1)==cc[unchanged]).mean()),gain_nats=float(np.log(p[unchanged,cc[unchanged]]/b[unchanged,cc[unchanged]]).mean())))
  held[layer]=rows
 insufficient=[]
 for e in after['entries']:
  if e['status']!='observed':continue
  k=[(7*co[o][0]+6*co[o][1])%2704 for o in e['ids']];insufficient.append(dict(**e,occurrences=sorted({x//208 for x in k}),geographic_blocks={o:blocks[o] for o in e['ids']},reason='Only2 existing observations' if len(e['ids'])<3 else 'Three distinct conditional occurrences but only2 geographic blocks; original strict geographic independence requirement unmet',strict_color_adopted=False))
 # Conditional partial pattern primitivity: explicit witnesses, no length search.
 proper=[];strong=[e for e in after['entries'] if e['status']=='strong']
 for d in [n for n in range(1,208) if 208%n==0]:
  witness=next((dict(first=a['residue'],second=b['residue'],first_color=a['color'],second_color=b['color']) for a in strong for b in strong if a['residue']<b['residue'] and (a['residue']-b['residue'])%d==0 and a['color']!=b['color']),None);proper.append(dict(period=d,rejected=bool(witness),witness=witness))
 contradictions=[]
 for e in after['entries']:
  cc={auth[o]['color'] for o in e['ids'] if o in auth}
  if len(cc)>1:contradictions.append(e['residue'])
 save(OUT/'pattern208.json',dict(length=208,mapping='A=7a+6b',N_conditional=2704,repeats_conditional=13,strict_sequence=after['strict_sequence'],entries=after['entries'],supported=after['supported'],conflicting=after['conflicting'],insufficient=after['insufficient'],actual_shortest_complete_sequence_established=False))
 save(OUT/'pattern-analysis.json',dict(results=results,transitions=transitions,unchanged1036_target_scores=held,insufficient=insufficient,proper_divisor_witnesses=proper,maker_vs_maker_conflicts=contradictions,freeze_sha256=sha(OUT/'freeze.json'),policy='Full cohort retains all recorded authoritative colors and associations. Exact208 conditional; unresolved colors never majority-filled. Other cohort gains are not full-cohort resolutions. Proper-divisor test is only conditional primitivity of supported208 entries, not physical total or broad winding search.'))
 print('PATTERN',[(layer,[(c,v['supported'],v['conflicting'],v['insufficient']) for c,v in r.items()]) for layer,r in results.items()]);print('HELD',held);print('Sequence',after['strict_sequence'])
if __name__=='__main__':main()
