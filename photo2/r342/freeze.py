"""Freeze all four maker colors and native inspection before final pattern scoring."""
from common import *
import subprocess,datetime

def main():
 g,obs,co,rgb,auth=load();maker=read(OUT/'maker-decisions.json');review=read(OUT/'native-review.json');assert not review['additional_color_changes'];after=read(OUT/'maker-graph.json.gz');fo={r['id']:r for r in after['observations']}
 for o,r in obs.items():
  assert fo[o]['xy']==r['xy']
  for k,v in r.items():
   if k!='color':assert fo[o][k]==v
 assert after['coordinates']==g['coordinates'] and after['edges']==g['edges'] and after['H']==g['H']
 for o,r in auth.items():
  if o in fo:assert fo[o]['color']==r['color']
 after.update(schema='r342-frozen-maker-pigment-overlay-v1',r342_policy='Four explicit maker colors. No new automatic color, identity, coordinate, link, or winding changes. Full recorded-color pattern cohort retained; optional weak-source exclusions separate.')
 save(OUT/'graph.json.gz',after);save(OUT/'corrections.json',dict(changes=maker['changes'],additional_changes=[],all_authoritative_labels=auth,original_records='photo2/r341/graph.json.gz',native_review='photo2/r342/native-review.json',pattern_used=False))
 paths=subprocess.check_output(['git','ls-files','beads-photo-2.jpg','beads.pov']+[f'photo2/r{n}' for n in range(332,342)]+[f'photo2/R{n}_{k}.md' for n in range(332,342) for k in ['REPORT','REPRODUCE']],cwd=ROOT,text=True).splitlines();save(OUT/'input-seal.json',{p:sha(ROOT/p) for p in paths})
 save(OUT/'freeze.json',dict(base_commit=BASE,changed_ids=sorted(MAKER),graph_sha256=sha(OUT/'graph.json.gz'),native_review_sha256=sha(OUT/'native-review.json'),classification_sha256=sha(OUT/'audited-classification.json.gz'),maker_sha256=sha(OUT/'maker-decisions.json'),hue_diagnostic_sha256=sha(OUT/'hue-diagnostic.json'),pattern_used=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),historical_files=len(paths),default_activity='All1040 indexed sources retained. New black judgments independent of weak-source eligibility. Excluding Q102/Q169 only in explicitly labeled diagnostic cohorts.'))
 print('FROZEN',after['indexed_colors'],len(paths),'old files sealed')
if __name__=='__main__':main()
