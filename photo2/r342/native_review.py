"""Explicit photographic ownership review; no motif-derived color adoption."""
from common import *
from experiment import confusion
# These three are the COMPLETE raw disagreements after the maker changes.
REVIEW={
 'C-1253-2928':dict(owned=False,reason='Fixed core still extends above/right of visible yellow glass. Score48 is boundary darkness; keep yellow and abstain.'),
 'NEW-563-1633':dict(owned=False,reason='Fixed patch below the visible yellow E5-0562-1620 body, within shadow/rim. No separate glass attributable to this unindexed source; no black correction.'),
 'NEW-1681-1498':dict(owned=False,reason='Maker black authoritative. Fixed offset core touches the yellow shoulder/ambiguous boundary; score99 does not measure safely owned black glass. Abstain automatically, retain black in color ledger.'),
}
MINORITY={
 'NEW-1519-2976':'Maker red remains authoritative. Hue20.35 overlaps confirmed shadow-yellow; no photographic recoloring permitted. Geometry has3 accepted incident links; exact208 conflicts with several clearly yellow occurrences.',
 'R332-R-0037-0040':'Tiny peripheral red/purple response adjacent to red body; safe independent body material cannot be certified. No repeat-derived color or identity change.',
 'REC266-P035619':'Dim peripheral response in red shoulder/paper boundary; no safely attributed own-body sample. No correction.',
 'REC266-P100583':'A visible orange/brown partial body is distinguishable. Hue12.23 lies on red side of controls, but shadow-yellow remains plausible; pigment and own-body association need native judgment.',
 'R332-R-0125-0118':'Dim orange partial body/crescent below/right of red neighbor. Hue11.37 is not decisive where own-body boundary is unresolved. No correction.',
 'R332-R-0197-0183':'Very small dim red/purple edge response below yellow/orange neighbor. Fixed patch peripheral; independently distinguishable body not certified. Do not manufacture a pigment question.'}
CANDIDATE_JUDGMENTS={
 'REC266-P102347':'Visible partial orange/yellow body near paper edge; old source was recentered by5.9pixels. Retain original cache provenance and deferred status. No promotion from mask or plausible site alone.',
 'R332-Y-0104-0097':'Visible dim amber body at rope edge; promising existing cue, but not independently certified red/yellow or safe association. Retain provisional; no automatic identity admission.',
 'R332-B-0105-0098':'Already rejected in R338 as K-0935-2540 shoulder (same as REC266-P122012). This historical duplicate veto overrides good numerical spacing/darkness. Do not reopen or admit.',
 'R332-B-0110-0103':'Black-positive pixels under red C-1004-2311 at rope boundary; separate body versus rim cannot be certified in native photograph. Geometry alone insufficient.',
 'R332-B-0175-0167':'Black-positive near outer edge of existing black bodies; independent closed body boundary at cue remains uncertain. No promotion.'}
def main():
 g,obs,co,rgb,auth=load();data=read(OUT/'classification.json.gz');rows=data['records'];physical={r['id']:r for r in read(ROOT/'photo2/r338/analysis/analysis.json.gz')['physical_interior_records']};prior={r['id']:r for r in read(ROOT/'photo2/r341/native-audit.json.gz')['records']};truth={o:r['color'] for o,r in auth.items() if o in obs};full_disagreements=[]
 for r in rows:
  o=r['id'];m=r['measurement'];clear=physical[o]['clearance'] if o in physical else None
  # Fixed18pixel clearance, no bead-diameter or neighbor-spacing dependence.
  eligible=o in co and clear is not None and clear>=18
  r['outline_clearance_px']=clear;r['automatic_decision']=m['decision'] if eligible else 'unknown'
  r['native_review']=REVIEW.get(o);r['reviewed_decision']='unknown' if o in REVIEW else r['automatic_decision'];r['patch_same_as_R341']=m['patch_box']==prior[o]['measurement']['patch_box'];r['native_ownership_status']='explicitly unsafe; abstain' if o in REVIEW else 'same previously reviewed patch' if r['patch_same_as_R341'] and prior[o]['measured_pixels_convincingly_owned'] else 'not newly certified by this round'
  if (r['recorded_color']=='black')!=(m['decision']=='black'):full_disagreements.append(o)
 assert set(full_disagreements)==set(REVIEW)
 evals={}
 for name in ['raw','automatic_decision','reviewed_decision']:
  decisions={r['id']:r['measurement']['decision'] if name=='raw' else r[name] for r in rows};evals[name]=confusion({r['id']:r['measurement'] for r in rows},truth,decisions)
 save(OUT/'native-review.json',dict(raw_disagreements=REVIEW,remaining_conflict_native_inspection=MINORITY,candidate_inspection=CANDIDATE_JUDGMENTS,additional_color_changes=[],pattern_used_for_pigment=False,all_raw_disagreements_inspected=True,whole_inventory_new_ownership_certification=False,notes='Reference tests are retrospective, not new blind photographic truth. Unreviewed core ownership is not certified merely because its binary result matches a stored color. No automatic overwrites of contradictory or uncertain records.'))
 save(OUT/'audited-classification.json.gz',dict(records=rows,model='fixed offset9x9 core',threshold=73.5,pattern_used=False));save(OUT/'evaluation.json',dict(active_maker117=evals,global_counts={f:dict(Counter(r['measurement']['decision'] if f=='raw' else r[f] for r in rows)) for f in ['raw','automatic_decision','reviewed_decision']},global_label_disagreements=full_disagreements,selected_patch_exactly_same_as_R341=sum(r['patch_same_as_R341'] for r in rows),native_false_black_cases=['C-1253-2928','NEW-563-1633'],maker_raw_missed_black=['NEW-1681-1498'],additional_color_changes=0,all120_maker=dict(active=117,historically_excluded=3,excluded_labels_preserved=True),policy='Automatic eligibility: indexed plus saved original-outline clearance>=18pixels. This is a fixed edge abstention, not bead size. Native reviewed vetoes are explicit inspection inputs, not classifier rules; matching stored color is not new ownership truth.'))
 result=read(OUT/'evaluation.json');result['abstentions_by_maker_color']={f:dict(Counter(truth[r['id']] for r in rows if r['id'] in truth and r[f]=='unknown')) for f in ['automatic_decision','reviewed_decision']};result['R341_raw_same117']=confusion({o:dict(decision=r['measurement']['raw_decision']) for o,r in prior.items()},truth);result['same_fixed_eligibility476_comparison']={layer:confusion({o:dict(decision=r['measurement']['raw_decision']) for o,r in prior.items()} if layer=='R341' else {r['id']:r['measurement'] for r in rows},truth,{r['id']:(prior[r['id']]['measurement']['raw_decision'] if layer=='R341' else r['measurement']['decision']) if r['automatic_decision']!='unknown' else 'unknown' for r in rows}) for layer in ['R341','R342']};save(OUT/'evaluation.json',result);print('evaluation',evals);print('global',result['global_counts'])
if __name__=='__main__':main()
