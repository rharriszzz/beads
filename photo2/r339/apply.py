"""Freeze automatic pigment changes, independently of periodic diagnostics."""
import argparse
from .common import *
def run(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);g=read(artifact('maker/graph.json.gz'));after=copy.deepcopy(g);obs={r['id']:r for r in after['observations']};co={r['id']:r['ab'] for r in g['coordinates']};auth=authority();rows=read(artifact('classification/classification.json.gz'))['records'];changes=[];deferred=[]
 # These native judgments corroborate already established working body
 # ownership; they never admit/merge a body or move a support. All five simple
 # suspects were inspected before reading their pattern residues.
 judgments={
 'NEW-1247-2991':'One distinct existing dark glass body between the red outer row and yellow inner row; colored reflection isolated from surrounding dark material. Fixed aperture remains within the visible body; no recentering.',
 'NEW-2156-1135':'Existing dark body is distinguishable from the yellow neighbors above/left and below/right; a tinted bright patch is excluded from material brightness. No new identity or location claim.',
 'NEW-2235-1476':'Existing dark body and its bright patch are separate from adjacent yellow bodies. Remaining material is consistently dark across common aperture scales.',
 'E5-2272-1815':'Distinct existing dark-looking body, but maximum-channel contrast crosses the decision boundary with aperture extent; preserve yellow pending resolution, not a majority change.',
 'NEW-1702-1860':'Existing material appears dark, but the larger aperture crosses the conservative black/unknown boundary; preserve red and its uncertainty.'}
 for r in rows:
  o=r['id'];eligible=r['simple_decision']=='black' and r['stable_across_apertures'] and r['physical_interior'] and o in co
  if o in auth:assert obs[o]['color']==auth[o]['color']
  if eligible and obs[o]['color']!='black' and o not in auth:
   assert o in judgments;before=obs[o]['color'];obs[o].update(color='black',r339_before_color=before,r339_color_authority='simple common-body maximum-channel brightness plus native ownership inspection',r339_classification_source='photo2/r339/classification/classification.json.gz');changes.append(dict(id=o,before_color=before,color='black',xy=obs[o]['xy'],ab=co[o],native_judgment=judgments[o],simple_score=r['aperture_decisions'][1]['score'],reference_ids=r['reference_ids'],authority='R339 conservative photographic application; not maker judgment',pattern_used=False))
  elif r['simple_decision']=='black' and obs[o]['color']!='black':deferred.append(dict(id=o,color=obs[o]['color'],reason='aperture sensitivity; no stable decision' if not r['stable_across_apertures'] else 'maker authoritative',native_judgment=judgments.get(o)))
 after['indexed_colors']=dict(Counter(obs[o]['color'] for o in co));after.update(schema='r339-frozen-photographic-color-overlay-v1',baseline_commit=BASE,previous_graph='photo2/r338/results/graph.json.gz',geometry_policy='All original observations, XY/AB, IDs, edges, winding and exclusions retained. Pigment-only changes with original record preserved in prior layers.',classifier_policy='Selected simple one-aperture/one-trim method; require robustness across predeclared aperture variations for new corrections. Old two-extent procedure remains comparison only. No pattern color used.')
 save(out/'graph.json.gz',after);save(out/'freeze.json',dict(maker_decisions=read(artifact('maker/decisions.json')),automatic_changes=changes,deferred_simple_suspects=deferred,native_judgments=judgments,authoritative_labels=auth,classification_sha256=content_sha(artifact('classification/classification.json.gz')),classification_digest_scope='Canonical decoded classification JSON excluding measured runtime; gzip creation timestamp is not evidence',pattern_used=False,body_identities_created=0,geometry_changes=0,scope='Photographic evidence frozen before fixed208 analysis; corrections preserve full prior record/provenance in the baseline graph. No color-feedback iteration.'))
 save(out/'summary.json',dict(records=len(obs),indexed=len(co),links=len(g['edges']),maker_changes=3,automatic_changes=len(changes),automatic_ids=[r['id'] for r in changes],deferred_ids=[r['id'] for r in deferred],indexed_colors=after['indexed_colors'],geometry_changes=0,identities_created=0));print('APPLY',len(changes),[r['id'] for r in changes], 'defer',[r['id'] for r in deferred])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
