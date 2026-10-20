"""Matched-cohort diagnostic evaluation; independent labels, no model selection."""
from explore import *
from photo2.r337.common import save
from collections import Counter

def confusion(rows,truth,decision):
 c=Counter(dict(n=0,black=0,colored=0,TP=0,TN=0,FP=0,FN=0,abstain_black=0,abstain_colored=0))
 for r in rows:
  t=truth[r['id']]=='black';d=decision(r);c['n']+=1;c['black' if t else 'colored']+=1
  if d=='unknown':c['abstain_black' if t else 'abstain_colored']+=1
  else:c[('TP' if t else 'FP') if d=='black' else ('FN' if t else 'TN')]+=1
 return dict(c,black_recall_among_decided=c['TP']/max(1,c['TP']+c['FN']),black_recognition_of_all=c['TP']/max(1,c['black']),colored_false_positive_rate_among_decided=c['FP']/max(1,c['FP']+c['TN']),agreement_among_decided=(c['TP']+c['TN'])/max(1,c['TP']+c['TN']+c['FP']+c['FN']))

def main():
 g,obs,co,photo,geom,auth=setup();data=read(OUT/'classification.json');rows=data['records'];manual=read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records'];mm={r['id']:r for r in manual};old={r['id']:r for r in read(ROOT/'photo2/r339/classification/classification.json.gz')['records']};truth={o:r['color'] for o,r in auth.items() if o in obs};visual=['C-0309-0966','C-0313-1445','C-1899-0420'];newtruth=dict(truth,**{o:'red' for o in visual},**{'C-1253-2928':'yellow','RF70T-K-2172-1154':'black','K-2183-1053':'black'});training=set(data['model']['training_ids']);sets={'manual48':set(mm),'geometry_training24':training,'manual_comparison24':set(mm)-training,'additional_maker65':set(truth)-set(mm),'all_maker113':set(truth),'additional_colored37':{o for o,c in truth.items() if c!='black' and o not in mm}|set(visual),'three_dark_red':set(visual),'posthoc_boundary_control':{'C-1253-2928'},'posthoc_native_black_misses':{'RF70T-K-2172-1154','K-2183-1053'},'all_native_reviewed119':set(newtruth)};results={}
 for name,ids in sets.items():
  rr=[r for r in rows if r['id'] in ids];results[name]=dict(raw=confusion(rr,newtruth,lambda r:r['measurement']['decision']),eligible=confusion(rr,newtruth,lambda r:r['decision']))
 comparison={}
 for method in ['R339_selected','R339_earlier_complex','R340_fixed']:
  rr=[r for r in rows if r['id'] in truth];dec=lambda r:r['decision'] if method=='R340_fixed' else ('unknown' if not r['geometry']['physical_interior'] or not r['geometry']['indexed'] else ((old[r['id']]['simple_decision'] if old[r['id']]['stable_across_apertures'] else 'unknown') if method=='R339_selected' else old[r['id']]['old']['decision']))
  comparison[method]=confusion(rr,truth,dec)
 overlaps=[]
 for r in rows:
  if r['id'] not in mm:continue
  a,b,c,d=mm[r['id']]['absolute_material_box'];x,y,u,v=r['measurement']['region_box'];px,py,pu,pv=r['measurement']['patch_box'];inter=max(0,min(c,u)-max(a,x))*max(0,min(d,v)-max(b,y));area=(u-x)*(v-y);manualarea=(c-a)*(d-b)
  overlaps.append(dict(id=r['id'],number=mm[r['id']]['number'],manual_box=[a,b,c,d],automatic_box=[x,y,u,v],region_IoU=inter/(area+manualarea-inter),automatic_region_fraction_inside_manual=inter/area,selected_patch_fully_inside_manual=a<=px and b<=py and pu<=c and pv<=d,manual_score=mm[r['id']]['score'],automatic_score=r['measurement']['score'],classification_agrees=(mm[r['id']]['color']=='black')==(r['measurement']['decision']=='black')))
 errors=[]
 for r in rows:
  if r['id'] in newtruth and (newtruth[r['id']]=='black')!=(r['measurement']['decision']=='black'):errors.append(dict(id=r['id'],truth=newtruth[r['id']],authority=r['authority'],raw_decision=r['measurement']['decision'],eligible_decision=r['decision'],measurement=r['measurement'],diagnostic_type='maker-label error' if r['id'] in truth else 'posthoc native ownership/coverage stress case'))
 save(OUT/'evaluation.json',dict(cohorts=results,matched_physical_screen_old_new=comparison,manual_region_comparisons=overlaps,errors=errors,all_maker_reference_labels=truth,additional_dark_red_sources={o:'R339 rejected luminance false-positive controls; visually verified red, not maker-confirmed' for o in visual},posthoc_stress_reference_labels={o:newtruth[o] for o in ['C-1253-2928','RF70T-K-2172-1154','K-2183-1053']},global_counts=dict(raw=Counter(r['measurement']['decision'] for r in rows),eligible=Counter(r['decision'] for r in rows),abstention_reasons=Counter(r['abstention_reason'] for r in rows if r['decision']=='unknown')),holdout_limit='Only odd24 fit geometry. Even24 and additional65 have independent labels, but their disk-stage errors were exposed before the one rectangle refinement; results are retrospective, not a pristine blind accuracy estimate. Posthoc3 native stress cases are explicitly nonrandom and did not alter classifier.'))
 for name in ['manual48','additional_maker65','all_maker113','additional_colored37','all_native_reviewed119']:print(name,results[name])
 print('same screen comparison',comparison)
if __name__=='__main__':main()
