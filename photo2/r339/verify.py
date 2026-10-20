"""Independent integer, native-pixel, reference and strict-pattern checks."""
import argparse
from .common import *
from photo2.r338.verify import independent_scores

def run(root):
 start=time.perf_counter();root=Path(root);seal=read(root/'maker/input-seal.json');assert all(sha(ROOT/p)==h for p,h in seal.items());g,oldobs,co=baseline();final=read(root/'results/graph.json.gz');obs={r['id']:r for r in final['observations']};assert set(obs)==set(oldobs);assert final['coordinates']==g['coordinates'] and final['edges']==g['edges'] and final['H']==g['H'];H=g['H'];maker=read(root/'maker/decisions.json');panels=read(ROOT/'photo2/r338/review/panels.json')
 for r in maker['decisions']:
  p=panels[r['panel']];assert p['id']==r['photograph']
  if r['local_feature'] is not None:assert next(k['id'] for k in p['key'] if k['number']==r['local_feature'])==r['id']
  assert obs[r['id']]['color']==r['color']
 assert maker['ordinary_color_corrections']==3;assert next(r for r in maker['decisions'] if r['local_feature']==12)['id']=='NEW-2259-1961'
 freeze=read(root/'results/freeze.json');changes={r['id'] for r in maker['decisions'] if r['changed']}|{r['id'] for r in freeze['automatic_changes']};assert changes=={'NEW-2185-1265','NEW-1221-2081','NEW-2259-1961','NEW-1247-2991','NEW-2156-1135','NEW-2235-1476'}
 for o,r in oldobs.items():
  assert obs[o]['xy']==r['xy'];assert all(obs[o][k]==v for k,v in r.items() if k!='color');assert obs[o]['color']==('black' if o in changes else r['color'])
 assert all(obs[o]['color']==r['color'] for o,r in freeze['authoritative_labels'].items() if o in obs);assert len(obs)==1058 and len(co)==1040 and len(g['edges'])==2287;assert len({(a%H[0],b-a//H[0]*H[1]) for a,b in co.values()})==1040
 for e in g['edges']:
  a,b=np.array(co[e['target']])-co[e['source']]-e['delta_ab'];assert (a%H[0],b-a//H[0]*H[1])==(0,0)
 assert final['indexed_colors']==dict(Counter(obs[o]['color'] for o in co));assert freeze['pattern_used'] is False and freeze['geometry_changes']==0 and freeze['body_identities_created']==0;assert freeze['classification_sha256']==content_sha(root/'classification/classification.json.gz')
 data=read(root/'classification/classification.json.gz');rows={r['id']:r for r in data['records']};photo=photograph();sample_pixels=0;ring_pixels=0;makerids={r['id'] for r in maker['decisions']};makerobs={r['id']:r for r in read(root/'maker/graph.json.gz')['observations']}
 for o,r in rows.items():
  assert r['xy']==oldobs[o]['xy'];assert not r['reflection_required'] and not r['body_identity_established'];refs=r['reference_ids'];assert o not in refs['black']+refs['colored'] and not makerids.intersection(refs['black']+refs['colored'])
  for z in refs['black']+refs['colored']:assert np.linalg.norm(np.array(rows[z]['xy'])-r['xy'])<=220 and rows[z]['physical_interior']
  assert all(makerobs[z]['color']=='black' for z in refs['black']) and all(makerobs[z]['color'] in ['red','yellow'] for z in refs['colored'])
  decisions=[]
  for j,s in enumerate(r['samples']):
   domain=np.array(s['domain_pixels']);body=np.array(s['body_pixels']);highlight=np.array(s['highlight_pixels']);assert len(domain)==len(body)+len(highlight);point=np.array(r['xy']);radius=[.35,.4,.45][j]*r['spacing'];assert np.all(np.sum((domain-point)**2,axis=1)<=radius**2+1e-8);brightness=photo[domain[:,1],domain[:,0]].max(1).astype(float)/255;threshold=np.quantile(brightness,.8);assert abs(threshold-s['highlight_threshold'])<1e-12;expectedbody=domain[brightness<=threshold];assert np.array_equal(expectedbody,body);value=float(photo[body[:,1],body[:,0]].max(1).mean()/255);assert abs(value-s['brightness'])<1e-12;sample_pixels+=len(domain);v=r['aperture_decisions'][j]
   if v['valid']:
    b=float(np.median([rows[z]['samples'][j]['brightness'] for z in refs['black']]));c=float(np.median([rows[z]['samples'][j]['brightness'] for z in refs['colored']]));assert abs(b-v['black_reference'])<1e-12 and abs(c-v['colored_reference'])<1e-12
    if c>b:
     score=(value-b)/(c-b);assert abs(score-v['score'])<1e-12;dec='black' if score<=.25 else 'not-black' if score>=.75 else 'unknown'
    else:dec='unknown'
   else:dec='unknown'
   assert dec==v['decision'];decisions.append(dec)
  selected=decisions[1] if r['physical_interior'] and r['indexed'] else 'unknown';assert selected==r['simple_decision'];assert r['stable_across_apertures']==(all(v==selected for v in decisions) and selected!='unknown')
  for extent in ['broad','compact']:
   for s in r['old'][extent]:
    pp=np.array(s['ring_pixels']);ring_pixels+=len(pp)
    if not len(pp):continue
    rgb=photo[pp[:,1],pp[:,0]].astype(float)/255.;gray=rgb@[.299,.587,.114];value=rgb.max(1);assert abs(np.median(gray)-s['median_intensity'])<1e-12;assert abs(np.quantile(value,.75)-s['q75_max_channel'])<1e-12
  def old_decision(ts):return 'black' if sum(t['positive'] for t in ts)>=2 and not any(t['negative'] for t in ts) else 'not-black' if sum(t['negative'] for t in ts)>=2 and not any(t['positive'] for t in ts) else 'unknown'
  b,c=old_decision(r['old']['broad']),old_decision(r['old']['compact']);assert r['old']['decision']==(b if b==c else 'unknown')
 assert len(rows)==1058
 for r in freeze['automatic_changes']:
  q=rows[r['id']];assert q['physical_interior'] and q['stable_across_apertures'] and q['simple_decision']=='black' and r['id'] not in freeze['authoritative_labels'];assert q['old']['decision']=='unknown'
 assert {r['id'] for r in freeze['deferred_simple_suspects']}=={'E5-2272-1815','NEW-1702-1860'}
 # A uniformly dark, reflection-free synthetic patch remains measurable.
 # Channel permutations leave maximum-channel body evidence exactly unchanged.
 from .classify import body_sample,decision
 patch=np.full((51,51,3),25,np.uint8);point=np.array([25.,25.]);tree=cKDTree([point]);sample=body_sample(patch,point,12,['known'],np.array([point]),tree,'known');assert not sample['highlight_pixels'] and sample['body_count']>300;assert decision(sample['brightness'],.1,.5)[0]=='black';assert np.array_equal(photo.max(2),photo[:,:,[2,0,1]].max(2))
 analysis=read(root/'analysis/analysis.json.gz');pattern=read(root/'analysis/pattern208.json');assert analysis['freeze_sha256']==content_sha(root/'results/freeze.json');blocks=read(ROOT/'photo2/r338/analysis/analysis.json.gz')['blocks'];cohorts={'unchanged_1040':sorted(co),'original_1039':sorted(r['id'] for r in read(ROOT/'photo2/r336/results/graph.json.gz')['coordinates']),'frozen_710':sorted(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']),'physical_450':sorted(o for o,r in rows.items() if r['physical_interior'] and o in co)};layers={'R338_baseline':oldobs,'maker_only':makerobs,'photographic_final':obs};checks=0
 for lname,labelobs in layers.items():
  for cname,names in cohorts.items():
   result=analysis['results'][lname][cname];statuses=[]
   for residue in range(208):
    ids=[o for o in names if (7*co[o][0]+6*co[o][1])%208==residue];counts=Counter(labelobs[o]['color'] for o in ids);sections={blocks[o] for o in ids};status='conflict' if len(counts)>1 else 'strong' if len(ids)>=3 and len(sections)>=3 else 'observed' if ids else 'unknown';entry=result['entries'][residue];assert counts==entry['counts'] and ids==entry['ids'] and status==entry['status'];statuses.append(status)
   assert statuses.count('strong')==result['supported'] and statuses.count('conflict')==result['conflicting']
   for score in result['scores']:
    for kind,occur in [('geographic',False),('whole_occurrence',True)]:
     gain,agreement=independent_scores(names,labelobs,co,blocks,score['model']=='hier104',occur);assert abs(gain-score[kind]['gain_nats'])<1e-12 and abs(agreement-score[kind]['agreement'])<1e-12;checks+=1
 assert (pattern['supported'],pattern['conflicting'],pattern['insufficient'])==(179,21,8);summary=read(root/'analysis/summary.json');assert summary['resolved_by_maker']==[27,34] and summary['resolved_additionally']==[92];assert pattern['entries']==analysis['results']['photographic_final']['unchanged_1040']['entries']
 rp=read(root/'review/panels.json');keyrows=0
 for r in rp.values():
  assert r['key'][0]['number']==1 and r['key'][0]['id']==r['id'];keys={k['id'] for k in r['key']}
  for k in r['key']:assert k['xy']==obs[k['id']]['xy'] and k['ab']==co[k['id']] and k['color']==obs[k['id']]['color'];keyrows+=1
  assert r['edges']==[e for e in g['edges'] if e['source'] in keys and e['target'] in keys]
  if r['role']=='question target':assert not r['maker_reviewed'] and r['id'] not in freeze['authoritative_labels']
 crops=read(root/'review/native-crops.json')
 for r in crops:assert np.array_equal(np.asarray(Image.open(root/'review'/r['file'])),np.asarray(Image.fromarray(photo).crop(r['bbox'])))
 result=dict(passed=True,historical_hashes=len(seal),maker_decisions=7,exact_own_panel_references=6,maker_color_changes=3,automatic_color_changes=3,unchanged_XY=1058,unchanged_AB=1040,unchanged_primitive_links=2287,no_new_identities=True,classification_targets=1058,geometric_apertures=3174,native_aperture_pixel_samples=sample_pixels,native_old_ring_pixel_samples=ring_pixels,maximum_channel_hue_permutation_invariance=True,reflection_free_body_measurable=True,protected_maker_colors=sum(o in obs for o in freeze['authoritative_labels']),cohort_layer_pairs=12,independent_predictor_checks=checks,supported=179,conflicting=21,insufficient=8,own_panel_key_rows=keyrows,literal_native_crops=len(crops),seconds=time.perf_counter()-start);save(root/'verification.json',result);print('PASS R339 independent',result)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);run(p.parse_args().root)
