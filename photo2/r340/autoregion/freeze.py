"""Reversible native-evidence color overlay; run before any pattern analysis."""
from explore import *
from photo2.r337.common import save,sha
import copy,datetime,subprocess
from collections import Counter
JUDGMENTS={
'E5-2139-2470':'Distinct existing black-glass body at the fixed support, between neighboring yellow beads. Automatic patch46 is on its dark right-hand material beside the bright lobe, not on the yellow bodies or the inter-bead gap.',
'NEW-1036-2833':'Existing dark body with a pale lobe at the fixed support. The yellow bodies lie below-left and below-right. Patch53 is within the same dark body to the right of its lobe; no source recentering or neighbor/identity change.',
'NEW-1702-1860':'Existing dark body between yellow neighbors; patch39 lies on its right-hand dark glass. R339 already exposed this body as an uncertain brightness suspect; current contiguous material patch independently supplies dark glass evidence.',
'NEW-903-2501':'Existing dark body distinct from the neighboring yellow bodies. Patch49 is on the dark glass to the right of the bright lobe. Original native support/identity and all links remain fixed.'}
WITNESSES={
 'C-1253-2928':dict(box=[1249,2929,1255,2935],label='yellow',authority='R340 visual native-body control, NOT maker confirmation',judgment='The actual visible orange-yellow glass is left/below the recorded support. The automatic positive patch falls to the upper/right boundary beyond genuine colored material. A raw false-black result; already outside the preexisting physical-interior screen. No coordinate repair or recoloring.'),
 'K-1740-1575':dict(box=[1750,1574,1757,1582],label='black',authority='Existing maker black; witness region is R340 manual diagnostic only',judgment='The automatic small region retains a bright shoulder; dark glass lies farther to the right. This manual diagnostic witness is not substituted into the automatic classifier.'),
 'RF70T-K-2172-1154':dict(box=[2184,1152,2189,1159],label='black',authority='Recorded black plus R340 native inspection; NOT maker confirmation',judgment='The automatic region remains on a broad pale lobe/shoulder; dark body material farther right is visible. Preserve black; no special classifier rule.'),
 'K-2183-1053':dict(box=[2193,1055,2199,1061],label='black',authority='Recorded black plus R340 native inspection; NOT maker confirmation',judgment='Bright shoulder overlaps the automatic region; dark right/lower body material remains visible. Edge screen already abstains. Preserve black.')}

def witness(photo,box):
 x,y,u,v=box;z=photo[y:v,x:u].max(2);ss=np.lib.stride_tricks.sliding_window_view(z,(3,3)).max(axis=(-2,-1));j,i=np.unravel_index(ss.argmin(),ss.shape);xx=int(x+i);yy=int(y+j)
 return dict(approved_manual_box=box,score=int(ss[j,i]),patch_box=[xx,yy,xx+3,yy+3],patch_RGB=photo[yy:yy+3,xx:xx+3].tolist())

def main():
 g,obs,co,photo,geom,auth=setup();data=read(OUT/'classification.json');rows={r['id']:r for r in data['records']};maker=copy.deepcopy(g);mo={r['id']:r for r in maker['observations']};decisions=[]
 for o in ['E5-2272-1815','NEW-2156-1135','MAT25-K-2142-2497','K-1663-3006','NEW-1247-2991','NEW-2235-1476']:
  before=mo[o]['color'];mo[o].update(color='black',r340_maker_color='black',r340_previous_color=before,r340_authority='Explicit R340 maker decision; duplicate NEW-2156-1135 counted once');decisions.append(dict(id=o,before_color=before,color='black',changed=before!='black',source='Explicit maker decision in R340 request'))
 final=copy.deepcopy(maker);fo={r['id']:r for r in final['observations']};changes=[]
 for o,judgment in JUDGMENTS.items():
  assert o not in auth and rows[o]['decision']=='black' and o in co
  before=fo[o]['color'];assert before!='black';fo[o].update(color='black',r340_previous_color=before,r340_authority='Fixed3x3/73.5 plus independent native-glass inspection',r340_evidence='photo2/r340/autoregion/classification.json');changes.append(dict(id=o,before_color=before,color='black',native_judgment=judgment,measurement=rows[o]['measurement'],maker_confirmed=False,pattern_used=False))
 for graph in [maker,final]:graph['indexed_colors']=dict(Counter(r['color'] for r in graph['observations'] if r['id'] in co));graph.update(schema='r340-fixed-material-darkness-pigment-overlay-v1',previous_graph='photo2/r339/results/graph.json.gz',baseline_commit='df7c634c5183efe35a928685655edc0082d8beb9',geometry_changes=0)
 conflicts=[dict(id=o,recorded_color=r['recorded_color'],decision=r['decision'],raw_decision=r['measurement']['decision'],score=r['measurement']['score'],reason=r['abstention_reason']) for o,r in rows.items() if (r['recorded_color']=='black')!=(r['measurement']['decision']=='black')]
 # Exact historical preservation is checked at delivery, including completed diagnostics.
 paths=subprocess.check_output(['git','ls-files','beads-photo-2.jpg','beads.pov','photo2/r332','photo2/r333','photo2/r334','photo2/r335','photo2/r336','photo2/r337','photo2/r338','photo2/r339','photo2/r340/material-diagnostic','photo2/r340/quick-diagnostic'],cwd=ROOT,text=True).splitlines();seal={p:sha(ROOT/p) for p in paths}
 witnesses={o:dict(**r,measurement=witness(photo,r['box'])) for o,r in WITNESSES.items()}
 for o,r in witnesses.items():print('Diagnostic witness',o,r['measurement']['score'])
 freeze=dict(maker_decisions=decisions,authoritative_labels=auth,automatic_changes=changes,raw_recorded_color_disagreements=conflicts,native_stress_cases=witnesses,classification_sha256=sha(OUT/'classification.json'),model_sha256=sha(OUT/'rectangle-model.json'),native_inspection_policy='All48 manual-comparison overlays, all19 raw nonblack-positive hypotheses and all3 recorded-black misses inspected. New corrections only4 independently visible interior bodies; no pattern votes or re-questioning maker decisions.',pattern_used=False,identity_changes=0,geometry_changes=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 save(OUT/'maker-graph.json.gz',maker);save(OUT/'graph.json.gz',final);save(OUT/'freeze.json',freeze);save(OUT/'input-seal.json',seal);print('FROZEN maker changes',sum(r['changed'] for r in decisions),'automatic',len(changes),'historical files',len(seal))
if __name__=='__main__':main()
