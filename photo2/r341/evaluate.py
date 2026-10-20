"""Reference tests and full global audit counts, with truth/ownership kept separate."""
from common import *
from experiment import score

def confusion(records,truth,field):
 c=Counter(dict(n=0,black=0,colored=0,TP=0,TN=0,FP=0,FN=0,abstain_black=0,abstain_colored=0))
 for r in records:
  o=r['id']
  if o not in truth:continue
  t=truth[o]=='black';d=r['measurement']['raw_decision'] if field=='raw' else r[field];c['n']+=1;c['black' if t else 'colored']+=1
  if d=='unknown':c['abstain_black' if t else 'abstain_colored']+=1
  else:c[('TP' if t else 'FP') if d=='black' else ('FN' if t else 'TN')]+=1
 return dict(c,black_recall_among_decided=c['TP']/max(1,c['TP']+c['FN']))

def main():
 g,obs,co,rgb,auth,old=load();records=read(OUT/'native-audit.json.gz')['records'];selection=read(OUT/'selection.json');active={o:r['color'] for o,r in auth.items() if o in obs};manual=read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records'];controls=dict(active,**{o:'red' for o in ['C-0309-0966','C-0313-1445','C-1899-0420']},**{'C-1253-2928':'yellow','C-1264-2957':'yellow','E5-1178-2887':'red','RF70T-K-2172-1154':'black','K-2183-1053':'black'});cohorts={name:{field:confusion(records,truth,field) for field in ['raw','automatic_decision','audited_decision']} for name,truth in [('manual48',{r['id']:r['color'] for r in manual}),('development52',selection['development_ids']),('heldout64',selection['heldout_ids']),('active_maker113',active),('independent_label_controls121',controls)]};comparison={}
 for name in ['R340_raw','R340_automatic','R341_raw','R341_automatic','R341_native_audited']:
  rr=[]
  for r in records:
   row=dict(r)
   if name=='R340_raw':row['comparison']=old[r['id']]['measurement']['decision']
   elif name=='R340_automatic':row['comparison']=old[r['id']]['decision']
   elif name=='R341_raw':row['comparison']=r['measurement']['raw_decision']
   else:row['comparison']=r['automatic_decision'] if name=='R341_automatic' else r['audited_decision']
   rr.append(row)
  comparison[name]=confusion(rr,active,'comparison')
 bycolor={c:dict(n=sum(r['recorded_color']==c for r in records),automatic=dict(Counter(r['automatic_decision'] for r in records if r['recorded_color']==c)),native_audited=dict(Counter(r['audited_decision'] for r in records if r['recorded_color']==c)),native_uncertain_ids=[r['id'] for r in records if r['recorded_color']==c and not r['measured_pixels_convincingly_owned']]) for c in COLORS};excluded=read(OUT/'excluded-maker-controls.json');extra_correct=sum((r['maker_color']=='black')==(r['measurement']['raw_decision']=='black') for r in excluded['records']);save(OUT/'evaluation.json',dict(cohorts=cohorts,R340_R341_same_active_maker_comparison=comparison,inventory_by_color=bycolor,global_counts=dict(raw=Counter(r['measurement']['raw_decision'] for r in records),automatic=Counter(r['automatic_decision'] for r in records),native_audited=Counter(r['audited_decision'] for r in records)),all116_maker=dict(active=113,historically_excluded=3,excluded_raw_agreements=extra_correct,excluded_automatic_abstentions=3,role_admissions=0),classification_errors=[dict(id=r['id'],maker_color=active[r['id']],measurement=r['measurement'],automatic=r['automatic_decision'],audited=r['audited_decision'],reason=r['native_assessment']) for r in records if r['id'] in active and (active[r['id']]=='black')!=(r['measurement']['raw_decision']=='black')],limits='64 maker holdout labels not used to choose R341 geometry; these references were historically exposed in R340. Ownership judgments are explicit human-style native inspection, not independently measured ground truth for all1058. Raw scores, automatic eligibility, native audited decisions and retained labels are separate.'))
 print('MAKER',cohorts['active_maker113']);print('HOLDOUT',cohorts['heldout64']);print('INVENTORY',[(c,x['n'],x['native_audited']) for c,x in bycolor.items()]);print('COMPARE',comparison)
if __name__=='__main__':main()
