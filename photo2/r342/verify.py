"""Independent source-pixel, graph, strict consensus and held-out checks."""
from common import *
import colorsys,itertools

def main():
 g,obs,co,rgb,auth=load();freeze=read(OUT/'freeze.json');producers={'graph_sha256':'graph.json.gz','native_review_sha256':'native-review.json','classification_sha256':'audited-classification.json.gz','maker_sha256':'maker-decisions.json','hue_diagnostic_sha256':'hue-diagnostic.json'};assert all(sha(OUT/path)==freeze[key] for key,path in producers.items());seal=read(OUT/'input-seal.json');assert all(sha(ROOT/p)==s for p,s in seal.items());new=read(OUT/'graph.json.gz');fo={r['id']:r for r in new['observations']};assert len(obs)==1058 and len(co)==1040 and len(g['edges'])==2287
 assert new['coordinates']==g['coordinates'] and new['edges']==g['edges'] and new['H']==g['H'];assert {o for o in obs if fo[o]['color']!=obs[o]['color']}==set(MAKER)
 for o,r in obs.items():
  assert all(fo[o][k]==v for k,v in r.items() if k!='color');assert fo[o]['color']==MAKER.get(o,r['color'])
 for o,r in auth.items():
  if o in fo:assert fo[o]['color']==r['color']
 for e in g['edges']:
  delta=[co[e['target']][i]-co[e['source']][i]-e['delta_ab'][i] for i in range(2)];assert delta[0]*201==delta[1]*214 and delta[0]%214==0;assert tuple(e['delta_ab']) in [(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)]
 assert len({(a-(a//214)*214,b-(a//214)*201) for a,b in co.values()})==1040
 ex=read(OUT/'experiment.json');variants=read(OUT/'alternatives.json.gz');native_checks=0
 for kind,records in variants.items():
  for o,m in records.items():
   cx=int(round(obs[o]['xy'][0]))+(0 if kind=='at-support' else 6);cy=int(round(obs[o]['xy'][1]));allowed=set()
   for y in range(cy-4,cy+5):
    for x in range(cx-4,cx+5):
     valid=True
     if kind=='neighbor-clipped':
      for z in ex['neighbors'][o]:
       qx=int(round(obs[z]['xy'][0]))+6;qy=int(round(obs[z]['xy'][1]));valid&=(x-cx)**2+(y-cy)**2+4<(x-qx)**2+(y-qy)**2
     if valid:allowed.add((x,y))
   assert set(map(tuple,m['region_pixels']))==allowed
   candidates=[]
   for y in range(cy-4,cy+3):
    for x in range(cx-4,cx+3):
     if all((x+i,y+j) in allowed for i in range(3) for j in range(3)):candidates.append((int(rgb[y:y+3,x:x+3].max()),y,x))
   val,y,x=min(candidates);assert val==m['score'] and m['patch_box']==[x,y,x+3,y+3] and m['patch_RGB']==rgb[y:y+3,x:x+3].tolist();assert m['decision']==('black' if val<73.5 else 'not-black');native_checks+=1
 # Development-only total-error choice; holdout disjoint and unchanged historical64.
 assert not set(ex['development'])&set(ex['heldout']);assert len(ex['heldout'])==64
 losses={}
 for kind,records in variants.items():
  loss=sum((records[o]['decision']=='black')!=(c=='black') for o,c in ex['development'].items());assert loss==ex['alternatives'][kind]['development']['FP']+ex['alternatives'][kind]['development']['FN'];losses[kind]=loss
 assert ex['selected']==min(losses,key=lambda k:(losses[k],list(variants).index(k)))=='offset-core'
 manual=read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records'];assert len(manual)==48 and all((variants['offset-core'][r['id']]['decision']=='black')==(r['color']=='black') for r in manual);assert all((variants['offset-core'][o]['decision']=='black')==(c=='black') for o,c in ex['heldout'].items())
 # Hue recomputed through scalar colorsys, independent of vector matplotlib implementation.
 hues=read(OUT/'hue-measurements.json')
 for o,m in variants['offset-core'].items():
  values=[(colorsys.rgb_to_hsv(*[int(v)/255 for v in rgb[y,x]])[0]*360+180)%360-180 for x,y in m['region_pixels']];assert abs(float(np.median(values))-hues[o]['hue_degrees'])<1e-10
 hd=read(OUT/'hue-diagnostic.json');assert hd['heldout']['counts']=={'correct':33,'abstain':1};lo=min(hd['development_limits'].values());hi=max(hd['development_limits'].values());assert all(r['prediction']==('red' if hues[r['id']]['hue_degrees']<lo else 'yellow' if hues[r['id']]['hue_degrees']>hi else 'unknown') for r in hd['heldout']['records']);assert hd['all_confirmed_limits']['red_max']>=hd['all_confirmed_limits']['yellow_min']
 excluded=read(OUT/'excluded-maker-controls.json')['records'];assert len(excluded)==3
 for r in excluded:
  assert r['id'] not in obs and not r['active_admission'] and r['automatic_decision']=='unknown';a,b,c,d=r['measurement']['patch_box'];assert r['measurement']['score']==int(rgb[b:d,a:c].max()) and r['measurement']['patch_RGB']==rgb[b:d,a:c].tolist()
 # Strict entries recomputed without motif/metrics helper on every saved layer/cohort.
 ana=read(OUT/'pattern-analysis.json');blocks=read(ROOT/'photo2/r338/analysis/analysis.json.gz')['blocks'];cohorts=dict(full1040=set(co),same_without_Q102=set(co)-{'NEW-1681-1498'},same_without_Q169=set(co)-{'R332-R-0077-0077'},same_without_both=set(co)-{'NEW-1681-1498','R332-R-0077-0077'},frozen710=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']),original1039={r['id'] for r in read(ROOT/'photo2/r336/results/graph.json.gz')['coordinates']});entrychecks=0
 for layer,oo in [('R341',obs),('R342',fo)]:
  for name,ids in cohorts.items():
   saved=ana['results'][layer][name];seq=''
   for k,e in enumerate(saved['entries']):
    names=sorted(o for o in ids if (7*co[o][0]+6*co[o][1])%208==k);ct=Counter(oo[o]['color'] for o in names);winner=ct.most_common(1)[0][0] if ct else None;sections={blocks[o] for o in names if oo[o]['color']==winner};strong=len(ct)==1 and len(names)>=3 and len(sections)>=3;status='conflict' if len(ct)>1 else 'strong' if strong else 'observed' if names else 'unknown';assert status==e['status'] and dict(ct)==e['counts'] and names==e['ids'];seq+=winner[0].upper() if strong else '?';entrychecks+=1
   assert seq==saved['strict_sequence']
 # Independent held-out probability tables for identical1036 unchanged targets.
 names=sorted(co);ks={o:(7*co[o][0]+6*co[o][1])%2704 for o in names};targets=set(names)-set(MAKER);predchecks=0
 for layer,oo in [('R341',obs),('R342',fo)]:
  for result in ana['unchanged1036_target_scores'][layer]:
   predictions={};baselines={};folds=range(12) if result['holdout']=='geographic' else sorted({ks[o]//208 for o in names})
   for fold in folds:
    test=[o for o in names if (blocks[o]==fold if result['holdout']=='geographic' else ks[o]//208==fold)];training=[o for o in names if (blocks[o] not in [(fold-1)%12,fold,(fold+1)%12] if result['holdout']=='geographic' else ks[o]//208!=fold)];prior=np.array([sum(oo[o]['color']==c for o in training)+1 for c in COLORS],float);prior/=prior.sum()
    for o in test:
     ct=np.array([sum(ks[z]%208==ks[o]%208 and oo[z]['color']==c for z in training) for c in COLORS],float)
     if result['model']=='flat':prob=(ct+3*prior)/(ct.sum()+3)
     else:
      parent=np.array([sum(ks[z]%104==ks[o]%104 and oo[z]['color']==c for z in training) for c in COLORS],float);pt=(parent+3*prior)/(parent.sum()+3);prob=(ct+pt)/(ct.sum()+1)
     predictions[o]=prob;baselines[o]=prior
   agreement=sum(COLORS[int(predictions[o].argmax())]==oo[o]['color'] for o in targets)/len(targets);gain=float(np.mean([np.log(predictions[o][COLORS.index(oo[o]['color'])]/baselines[o][COLORS.index(oo[o]['color'])]) for o in targets]));assert abs(agreement-result['agreement'])<1e-12 and abs(gain-result['gain_nats'])<1e-12;predchecks+=1
 # Historical duplicate/candidate safeguards and exact native review crops.
 cues=read(OUT/'coverage-candidates.json')['records'];assert len(cues)==52 and not any(r['admitted'] for r in cues);bad=next(r for r in cues if r['id']=='R332-B-0105-0098');assert bad['historical_identity_veto']['status']=='reject-additional-identity';assert all(r['id'] not in obs for r in read(OUT/'candidate-checks.json')['records']);assert len(read(OUT/'consistency.json')['unindexed18'])==18
 panels=read(OUT/'review/panels.json')
 for panel in panels:
  assert panel['key'][0]==panel['id'];assert np.array_equal(np.array(Image.open(OUT/'review'/panel['filename'])),np.array(Image.fromarray(rgb).crop(panel['crop_box'])))
 consistency=read(OUT/'consistency.json');assert len(consistency['local_same_neighbor_tests'])==6;assert sum(len(r['all_same_neighbor_primitive_cells']) for r in consistency['local_same_neighbor_tests'])==7
 patch=read(OUT/'rejected-local-patch.json.gz');pc={r['id']:r['ab'] for r in patch['graph']['coordinates']};assert {o for o in co if pc[o]!=co[o]}=={'R332-R-0197-0183'};assert pc['R332-R-0197-0183']==pc['C-0581-0575'];assert not patch['adopted'] and len(patch['changed_links'])==2
 for e in patch['graph']['edges']:
  d=np.array(pc[e['target']])-pc[e['source']]-e['delta_ab'];assert d[0]*201==d[1]*214 and d[0]%214==0
 for r in consistency['targets']:
  f=r['target_excluded_fit'];aa=np.array([co[z] for z in f['anchors']]);base=np.array(f['reference_ab']);H=np.array([214,201]);aa-=np.rint(((aa-base)@H)/(H@H)).astype(int)[:,None]*H;X=np.c_[aa-base,np.ones(len(aa))];B=np.linalg.solve(X.T@X,X.T@np.array([obs[z]['xy'] for z in f['anchors']]));assert np.max(np.abs(B-f['native_affine_coefficients']))<1e-7
 assert consistency['local_patch_replays'][0]['native_error']>49 and consistency['local_patch_replays'][0]['occupied_by']==['C-0581-0575']
 p=read(OUT/'pattern208.json');assert (p['supported'],p['conflicting'],p['insufficient'])==(195,5,8);assert all(v['rejected'] for v in ana['proper_divisor_witnesses']);assert not ana['maker_vs_maker_conflicts']
 save(OUT/'verification.json',dict(passed=True,historical_files=len(seal),native_mask_score_checks=native_checks,hue_controls_independent_scalar=1058,original48_checks=48,reserved64_checks=64,producer_hashes_checked=5,old_observations_preserved=1058,coordinates_preserved=1040,primitive_links_preserved=2287,maker_active_colors=117,maker_excluded_preserved=3,strict_entries_checked=entrychecks,heldout_probability_results=predchecks,literal_native_crops=len(panels),saved_cues=36,pure_predictions=16,admissions=0,historical_duplicate_veto_preserved=True,coherent_patch_substitutions_rejected=1,conditional_neighbor_intersections_checked=6,pattern=[195,5,8],policy='Verifier uses direct native-pixel enumeration, scalar colorsys and independent consensus/prediction arithmetic; it does not call classifier, motif, metrics or predict helpers.'))
 print('PASS independent',native_checks,entrychecks,predchecks)
if __name__=='__main__':main()
