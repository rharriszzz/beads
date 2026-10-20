"""Strict fixed208 only after native-color/identity freeze; source cohorts separate."""
from common import *
from photo2.r338.analyze import metrics
from photo2.r337.common import predict

def main():
 g,obs,co,rgb,auth,extra=load();freeze=read(OUT/'freeze.json');assert sha(OUT/'graph.json.gz')==freeze['graph_sha256'] and not freeze['pattern_used_for_color_or_admission'];final=read(OUT/'graph.json.gz');fo={r['id']:r for r in final['observations']};fc={r['id']:r['ab'] for r in final['coordinates']};mo={r['id']:r for r in read(OUT/'maker-only-graph.json.gz')['observations']};blocks=copy.deepcopy(read(ROOT/'photo2/r338/analysis/analysis.json.gz')['blocks']);nearest=min(co,key=lambda o:np.linalg.norm(np.array(obs[o]['xy'])-extra[C62]['xy']));blocks[C62]=blocks[nearest];core=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']);results=dict(R342_same1040=metrics(obs,co,set(co),blocks),R343_metadata_only1040=metrics(obs,co,set(co),blocks),R343_maker_only1040=metrics(mo,co,set(co),blocks),R343_final_common1040=metrics(fo,fc,set(co),blocks),R343_expanded1041=metrics(fo,fc,set(fc),blocks),R342_frozen710=metrics(obs,co,core,blocks),R343_frozen710=metrics(fo,fc,core,blocks));assert results['R342_same1040']['strict_sequence']==read(ROOT/'photo2/r342/pattern208.json')['strict_sequence'];p=results['R343_expanded1041'];old=results['R342_same1040'];changes=[dict(residue=k,before=old['entries'][k],after=e) for k,e in enumerate(p['entries']) if old['entries'][k]!=e]
 names=sorted(fc);kk=np.array([(7*fc[o][0]+6*fc[o][1])%2704 for o in names]);bb=np.array([blocks[o] for o in names]);common=sorted(set(co)-{Q101});scores={}
 for layer,oo,coords in [('R342',obs,co),('R343',fo,fc)]:
  nn=sorted(coords);k=np.array([(7*coords[o][0]+6*coords[o][1])%2704 for o in nn]);b=np.array([blocks[o] for o in nn]);c=np.array([COLORS.index(oo[o]['color']) for o in nn]);ii=np.array([nn.index(o) for o in common]);rr=[]
  for model,parent in [('flat',None),('hier104',k%104)]:
   for hold,occ in [('geographic',None),('whole_occurrence',k//208)]:
    _,pp,base=predict(k%208,c,b,parent=parent,occ=occ);rr.append(dict(model=model,holdout=hold,n=len(ii),agreement=float((pp[ii].argmax(1)==c[ii]).mean()),gain_nats=float(np.log(pp[ii,c[ii]]/base[ii,c[ii]]).mean())))
  scores[layer]=rr
 # Color known from maker before indexing. Test original other occurrences only.
 knew=(7*fc[C62][0]+6*fc[C62][1])%2704;training=[o for o in co if (7*co[o][0]+6*co[o][1])%2704//208!=knew//208];ct=np.array([sum((7*co[o][0]+6*co[o][1])%208==knew%208 and obs[o]['color']==c for o in training) for c in COLORS]);prior=np.array([sum(obs[o]['color']==c for o in training)+1 for c in COLORS],float);prior/=prior.sum();prob=(ct+3*prior)/(ct.sum()+3);validation=dict(id=C62,color='yellow',residue=knew%208,occurrence=knew//208,training_ids=[o for o in training if (7*co[o][0]+6*co[o][1])%208==knew%208],probabilities=dict(zip(COLORS,prob.tolist())),prediction=COLORS[int(prob.argmax())],frequency_baseline=COLORS[int(prior.argmax())],scope='Post-selection known maker pigment, independently associated fixed source. Not a new blind bead label; no motif used for admission.')
 insufficient=[]
 for e in p['entries']:
  if e['status'] in ['observed','unknown']:insufficient.append(dict(**e,occurrences=sorted({(7*fc[o][0]+6*fc[o][1])%2704//208 for o in e['ids']}),interpretation='Geographic diversity insufficient' if len(e['ids'])>=3 else 'Only two recorded observations'))
 save(OUT/'pattern208.json',dict(length=208,mapping='A=7a+6b',N_conditional=2704,repeats_conditional=13,strict_sequence=p['strict_sequence'],entries=p['entries'],supported=p['supported'],conflicting=p['conflicting'],insufficient=p['insufficient'],actual_shortest_complete_sequence_established=False));save(OUT/'pattern-analysis.json',dict(results=results,transitions=changes,blocks=blocks,C62_geographic_assignment=dict(nearest_existing=nearest,block=blocks[C62],policy='Same nearest-neighbor geographic extension used in R338; chosen from XY only'),matched1039_unchanged_target_scores=scores,new_occurrence_prediction=validation,insufficient=insufficient,freeze_sha256=sha(OUT/'freeze.json'),policy='Same strict3agreeing records in3geographic blocks; no contradictory color may be adopted. Metadata-only changes do not alter scores; identical common cohort separated from admission gain. No majority fill or broad period/winding search.'))
 import csv
 with open(OUT/'pattern208.csv','w',newline='') as stream:
  writer=csv.writer(stream,lineterminator='\n');writer.writerow(['position','strict_color','status','observed_color_only','observation_ids'])
  for e in p['entries']:writer.writerow([e['residue'],e['color'] if e['status']=='strong' else '?',e['status'],e['observed_color'],';'.join(e['ids'])])
 print('PATTERN',[(k,v['n'],v['supported'],v['conflicting'],v['insufficient']) for k,v in results.items()]);print('C62 prediction',validation);print('Scores',scores)
if __name__=='__main__':main()
