"""Two predeclared new geometries, selected on development only; independent holdout."""
from common import *
from recognize import sample,THRESHOLD

def score(rows,truth):
 result=Counter(dict(n=0,TP=0,TN=0,FP=0,FN=0,abstain=0))
 for o,t in truth.items():
  m=rows[o];result['n']+=1
  if m is None:result['abstain']+=1
  else:result[('TP' if t=='black' else 'FP') if m['raw_decision']=='black' else ('FN' if t=='black' else 'TN')]+=1
 return dict(result)
def main():
 start=time.perf_counter();g,obs,co,rgb,auth,old=load();geo=local_geometry(g,obs);save(OUT/'geometry.json',geo);names=sorted(obs);xy=np.array([obs[o]['xy'] for o in names]);tree=cKDTree(xy);manual=read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records'];development={r['id']:r['color'] for r in manual};development.update({'K-1740-1575':'black','RF70T-K-2172-1154':'black','K-2183-1053':'black','C-1253-2928':'yellow'});heldout={o:r['color'] for o,r in auth.items() if o not in development and o in obs};truth={o:r['color'] for o,r in auth.items() if o in obs};truth.update(development);neighbors={o:[names[j] for j in tree.query_ball_point(obs[o]['xy'],1.1*geo[o]['spacing']) if names[j]!=o] for o in names};variants={}
 for kind in ['circle','ellipse']:
  variants[kind]={o:sample(rgb,obs[o]['xy'],geo[o],[obs[z]['xy'] for z in neighbors[o]],kind) for o in names};print(kind,'development',score(variants[kind],development));print('Dev errors',[(o,m['score']) for o,m in variants[kind].items() if o in development and m and (m['raw_decision']=='black')!=(development[o]=='black')])
 # Select by development-only balanced error count; ellipse preferred only for a meaningful gain.
 scores={kind:score(rows,development) for kind,rows in variants.items()};loss=lambda kind:(scores[kind]['FP']+scores[kind]['FN']+scores[kind]['abstain'],0 if kind=='circle' else 1);selected=min(variants,key=loss)
 save(OUT/'selection.json',dict(selected=selected,development_ids=development,heldout_ids=heldout,development_scores=scores,policy='Only48 manual references plus4 explicitly requested failure cases choose between two predeclared simple geometries. Holdout labels are not used in selection. Threshold73.5 fixed; no later tuning.',alternatives=['R340 rectangle (historical)','circle: semiaxes.25,.25 spacing','ellipse: semiaxes.30,.20 spacing; long axis local primitive(1,-1)'],center='Unchanged R340 geometry-only material-window midpoint; no fitted pigment or reflection feature.'))
 # Holdout evaluation follows model selection; never feeds back into selection.
 evaluation={kind:dict(development=score(rows,development),heldout=score(rows,heldout),maker=score(rows,{o:r['color'] for o,r in auth.items() if o in obs})) for kind,rows in variants.items()};save(OUT/'experiment.json',dict(evaluation=evaluation,selected=selected,seconds=time.perf_counter()-start));save(OUT/'alternatives.json.gz',variants)
 chosen=variants[selected];records=[]
 for o in names:
  m=chosen[o];eligible=o in co and old[o]['geometry']['physical_interior'] and m is not None
  records.append(dict(id=o,xy=obs[o]['xy'],recorded_color=obs[o]['color'],maker_authority=auth.get(o),geometry=geo[o],neighbor_ids=neighbors[o],measurement=m,automatic_decision=m['raw_decision'] if eligible else 'unknown',automatic_abstention_reason=None if eligible else 'outside unchanged physical-interior screen' if not old[o]['geometry']['physical_interior'] else 'unindexed or no complete owned3x3',r340_score=old[o]['measurement']['score'],r340_raw_decision=old[o]['measurement']['decision']))
 save(OUT/'classification.json.gz',dict(records=records,model=selected,threshold=THRESHOLD,pattern_used=False));print('SELECTED',selected,evaluation[selected]);print('All B/R discrepancies',[(r['id'],r['recorded_color'],r['measurement']['score'] if r['measurement'] else None) for r in records if r['measurement'] is None or (r['recorded_color']=='black')!=(r['measurement']['raw_decision']=='black')]);print('colors',Counter(r['recorded_color'] for r in records))
if __name__=='__main__':main()
