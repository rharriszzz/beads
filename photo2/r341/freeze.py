"""Pigment-only reversible overlay, frozen before any R341 pattern computation."""
from common import *
import datetime,subprocess

def main():
 g,obs,co,rgb,auth,old=load();audit=read(OUT/'native-audit.json.gz');assert audit['pattern_used'] is False;after=copy.deepcopy(g);changed={};rows={r['id']:r for r in audit['records']};fo={r['id']:r for r in after['observations']}
 for o,r in rows.items():
  if o in auth:assert fo[o]['color']==auth[o]['color'];continue
  if r['audited_decision']=='black' and fo[o]['color']!='black':
   before=fo[o]['color'];fo[o].update(color='black',r341_before_color=before,r341_color_authority='Fixed3x3/73.5 plus independent global native-body audit',r341_evidence='photo2/r341/native-audit.json.gz');changed[o]=dict(id=o,before_color=before,color='black',xy=fo[o]['xy'],ab=co.get(o),measurement=r['measurement'],native_judgment=r['native_assessment'],outside_R340_automatic_eligibility=r['automatic_decision']=='unknown',maker_confirmed=False,pattern_used=False)
 assert set(changed)==set(audit['accepted_changes']) and len(changed)==12
 for o,v in obs.items():
  assert fo[o]['xy']==v['xy']
  for k,z in v.items():
   if k!='color':assert fo[o][k]==z
 after['indexed_colors']=dict(Counter(fo[o]['color'] for o in co));after.update(schema='r341-frozen-native-body-pigment-overlay-v1',previous_graph='photo2/r340/autoregion/graph.json.gz',baseline_commit=BASE,geometry_changes=0,identity_changes=0)
 save(OUT/'graph.json.gz',after);save(OUT/'corrections.json',dict(changes=list(changed.values()),all_maker_colors=auth,all_previous_metadata_preserved=True,geometry_changes=0,identity_changes=0,pattern_used=False));save(OUT/'freeze.json',dict(baseline_commit=BASE,classification_sha256=sha(OUT/'classification.json.gz'),native_audit_sha256=sha(OUT/'native-audit.json.gz'),native_judgments_sha256=sha(OUT/'native-judgments.json'),selected_model_sha256=sha(OUT/'selection.json'),corrected_graph_sha256=sha(OUT/'graph.json.gz'),changed_ids=sorted(changed),pattern_used=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),policy='No pattern analysis results available to this application. Only native owned-glass black results permit changes. Maker colors and all identities/XY/AB/links/exclusions retained. Not-black does not automatically choose red versus yellow.'))
 paths=subprocess.check_output(['git','ls-files','beads-photo-2.jpg','beads.pov']+[f'photo2/r{n}' for n in range(332,341)]+[f'photo2/R{n}_{k}.md' for n in range(332,341) for k in ['REPORT','REPRODUCE']],cwd=ROOT,text=True).splitlines();save(OUT/'input-seal.json',{p:sha(ROOT/p) for p in paths});print('FROZEN',len(changed),'indexed',after['indexed_colors'],'historical',len(paths))
if __name__=='__main__':main()
