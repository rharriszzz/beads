"""Independent native RGB/HSV, geometry, authority and strict-pattern checks."""
from common import *
import colorsys,itertools,math

def main():
 g,obs,co,rgb,auth,extra=load();seal=read(OUT/'input-seal.json');assert all(sha(ROOT/p)==h for p,h in seal.items());freeze=read(OUT/'freeze.json');hashes={'graph_sha256':'graph.json.gz','maker_sha256':'maker-decisions.json','association_sha256':'association.json','authority_overlay_sha256':'authority-overlay.json','source_pixels_sha256':'source-pixels.json.gz','sampling_sha256':'sampling-comparison.json'};assert all(sha(OUT/p)==freeze[k] for k,p in hashes.items());assert sha(ROOT/'photo2/r342/recognize.py')==freeze['black_detector_sha256']
 final=read(OUT/'graph.json.gz');fo={r['id']:r for r in final['observations']};fc={r['id']:r['ab'] for r in final['coordinates']};assert (len(fo),len(fc),len(final['edges']))==(1059,1041,2290);assert set(fo)-set(obs)=={C62};assert {o for o in obs if fo[o]['color']!=obs[o]['color']}=={Q101};assert fo[Q101]['color']=='yellow'
 for o,r in obs.items():
  assert fo[o]['xy']==r['xy']
  for k,v in r.items():
   if k!='color':assert fo[o][k]==v
 assert final['coordinates'][:len(g['coordinates'])]==g['coordinates'];assert final['edges'][:2287]==g['edges'];assert final['H']==g['H']==[214,201]
 for o,r in auth.items():
  if o in fo:assert fo[o]['color']==r['color']
 assert all(o not in fo for o in ['NEW-1927-2829','REC266-P146299','C-1979-2669','R332-B-0105-0098','R332-B-0138-0130','E5-1499-3037'])
 # Targeted authority only: preserve red and protection, don't rewrite approval.
 authority_overlay=read(OUT/'authority-overlay.json');assert len(authority_overlay['records'])==1;target=authority_overlay['records'][0];assert target['id']=='NEW-1519-2976' and target['color_before']==target['color_after']=='red';assert not target['explicit_individual_pigment_confirmation'] and target['protected_from_automatic_recoloring'] and target['general_approval_support_retained'] and not target['protection_changed'];assert fo[target['id']]['color']=='red';assert fo[target['id']]['r343_pigment_authority']==target;assert all('r343_pigment_authority' not in fo[o] for o in obs if o!=target['id'])
 steps={(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)};neighbors=defaultdict(set)
 for e in final['edges']:
  a,b=e['source'],e['target'];d=[fc[b][i]-fc[a][i]-e['delta_ab'][i] for i in range(2)];assert d[0]*201==d[1]*214 and d[0]%214==0;assert tuple(e['delta_ab']) in steps;neighbors[a].add(b);neighbors[b].add(a)
 assert len({(a-(a//214)*214,b-(a//214)*201) for a,b in fc.values()})==1041;assert len({(7*a+6*b)%2704 for a,b in fc.values()})==1041
 seen={final['reference']};todo=list(seen)
 while todo:
  o=todo.pop()
  for z in neighbors[o]-seen:seen.add(z);todo.append(z)
 assert seen==set(fc)
 # C62: original support and cached cell exact, unique native fit, true alias count.
 a=read(OUT/'association.json');oldcue=read(OUT/'C62-original-candidate.json.gz');assert fo[C62]['xy']==a['source_xy']==oldcue['xy'];assert fc[C62]==a['cell']==oldcue['cell']==[104,97];assert a['independent_native_identity']['separate_body'] and not a['independent_native_identity']['maker_confirmed_separate_identity'];assert a['legacy_maker_only_identity_gate_would_not_admit'];assert not a['recentered'] and not a['blocked_old_links'];assert set(a['same_body_cache_aliases'])=={C62,'REC266-P123596'};assert 'REC266-P123596' not in fo;assert a['cache_alias_native_evidence']['native_source_inside_independently_inspected_glass'] and a['cache_alias_native_evidence']['distance_to_fixed_C62_support']<5;assert sha(ROOT/a['cache_alias_native_evidence']['source'])==a['cache_alias_native_evidence']['source_sha256']
 H=np.array([214,201]);base=np.array(a['cell']);aa=np.array([co[o] for o in a['local_anchors']]);aa-=np.rint(((aa-base)@H)/(H@H)).astype(int)[:,None]*H;X=np.c_[aa-base,np.ones(len(aa))];B=np.linalg.solve(X.T@X,X.T@np.array([obs[o]['xy'] for o in a['local_anchors']]));assert np.max(np.abs(B-a['native_affine_coefficients']))<1e-7;p=np.array(a['source_xy']);trials=sorted((float(np.linalg.norm(np.r_[np.array(d),1]@B-p)),d) for d in itertools.product(range(-3,4),repeat=2));assert trials[0][1]==(0,0);assert abs(trials[0][0]-a['geometric_error'])<1e-8;assert abs(trials[1][0]-trials[0][0]-a['site_margin'])<1e-8
 oldpairs={frozenset([e['source'],e['target']]) for e in g['edges']};assert len(a['links'])==3 and all(frozenset(v) in oldpairs for v in a['old_neighbor_triangles']);assert len(a['old_neighbor_triangles'])==2
 # Historical raw foreground is a corridor exclusion only, NEVER a pigment rule.
 r,gc,b=rgb.astype(float).transpose(2,0,1)/255.;legacy_raw=((r>1.5*b)&(r>.13))|(rgb.max(2)/255.<.30)
 for row in a['link_audit']:
  e=row['edge'];q=np.array(obs[e['target']]['xy']);v=q-p;pts=np.array([p+(i/30)*v for i in range(31)]);assert np.max(np.abs(pts-row['filled_corridor']['sample_xy']))<1e-9;fractions=[]
  for x,y in pts:
   x0,y0=int(x),int(y);dx=x-x0;dy=y-y0;fractions.append((1-dx)*(1-dy)*legacy_raw[y0,x0]+dx*(1-dy)*legacy_raw[y0,x0+1]+(1-dx)*dy*legacy_raw[y0+1,x0]+dx*dy*legacy_raw[y0+1,x0+1])
  assert abs(float(np.mean(fractions))-row['raw_corridor_fraction'])<1e-10;block=[]
  for o in co:
   if o==e['target']:continue
   w=np.array(obs[o]['xy'])-p;t=float(w@v/(v@v))
   if .2<t<.8 and np.linalg.norm(w-t*v)<7:block.append(o)
  assert not block;lengths=[np.linalg.norm(np.array(obs[x]['xy'])-obs[y]['xy']) for x,y in row['reference_links']];ratio=float(np.linalg.norm(v)/np.median(lengths));assert abs(ratio-row['length_ratio'])<1e-12 and .65<=ratio<=1.45
 # Every plotted point is original native RGB and independently converted HSV.
 points=read(OUT/'source-pixels.json.gz')['points'];assert len(points)==read(OUT/'HSV-summary.json')['pixels'] and len({tuple(r['xy']) for r in points})==len(points);point_by_id=defaultdict(list)
 for row in points:
  x,y=row['xy'];assert row['RGB']==rgb[y,x].tolist();h,s,v=colorsys.rgb_to_hsv(*[int(c)/255 for c in rgb[y,x]]);h=(h*360+180)%360-180;assert max(abs(h-row['H']),abs(s-row['S']),abs(v-row['V']))<1e-10;assert row['hue_interpretable']==(s>=.3 and v>=.2);point_by_id[row['id']].append(row)
 assert all(r['recorded_pigment']=='red' for r in point_by_id['NEW-1927-2829']);assert all(r['recorded_pigment']=='yellow' for r in point_by_id['REC266-P146299']);assert all(r['recorded_pigment']=='red' and not r['individually_confirmed'] for r in point_by_id['NEW-1519-2976']);assert len({r['id'] for r in points if r['individually_confirmed']})==6
 # Clearance patch rederived by brute-force distances to outside pixels, no EDT.
 cores=read(OUT/'glass-regions.json')['records'];comparisons=read(OUT/'sampling-comparison.json')['records'];patchchecks=0
 for core in cores:
  poly=np.array(core['polygon']);lo=poly.min(0)-2;hi=poly.max(0)+3;image=Image.new('1',tuple(hi-lo),0);ImageDraw.Draw(image).polygon([tuple(p-lo) for p in poly],fill=1);mask=np.array(image,bool);yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];inside=set(map(tuple,np.c_[xx[mask],yy[mask]]));outside=np.c_[xx[~mask],yy[~mask]];dist={p:float(np.sqrt(np.min(np.sum((outside-p)**2,axis=1)))) for p in inside};assert {p for p in inside if dist[p]>=2}=={tuple(r['xy']) for r in point_by_id[core['id']]};candidates=[]
  for y in range(int(lo[1]),int(hi[1])-2):
   for x in range(int(lo[0]),int(hi[0])-2):
    patch=[(x+i,y+j) for j in range(3) for i in range(3)]
    if all(p in inside for p in patch):candidates.append((-min(dist[p] for p in patch),y,x))
  negative,y,x=min(candidates);assert -negative>=2 and core['selected_patch']['patch_box']==[x,y,x+3,y+3];patchchecks+=1
 for row in comparisons:
  for name,m in row['methods'].items():
   if m is None:continue
   x0,y0,x1,y1=m['patch_box'];assert m['RGB']==rgb[y0:y1,x0:x1].tolist();patchchecks+=1
 q=next(r for r in comparisons if r['id']==Q101);c=next(r for r in comparisons if r['id']==C62);assert q['methods']['R342_darkest']['pixels_in_conservative_core']==0 and q['methods']['core_clearance']['pixels_in_conservative_core']==9;assert c['methods']['R342_darkest']['pixels_in_conservative_core']==9
 # All five29 occurrences retain color/geometry; no individual pigment truth invented.
 p29=read(OUT/'position29.json');assert len(p29['records'])==5 and not p29['pigment_correction_adopted']
 for row in p29['records']:
  o=row['id'];assert row['recorded_color']==obs[o]['color']==fo[o]['color'] and row['xy']==obs[o]['xy'] and row['ab']==co[o];assert not row['explicit_individual_pigment'];allowed=None
  for e in row['accepted_incident_links']:
   z=e['source'] if e['target']==o else e['target'];q=np.array(co[z]);q-=round(((q-np.array(co[o]))@H)/(H@H))*H;cells={tuple(q-np.array(d)) for d in steps};allowed=cells if allowed is None else allowed&cells
  assert allowed=={tuple(co[o])};assert (7*co[o][0]+6*co[o][1])%208==29
 # Strict consensus rederived without motif or metrics helpers.
 ana=read(OUT/'pattern-analysis.json');blocks=ana['blocks'];coreids=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']);mo=copy.deepcopy(obs);mo[Q101]['color']='yellow';layers={'R342_same1040':(obs,co,set(co)),'R343_metadata_only1040':(obs,co,set(co)),'R343_maker_only1040':(mo,co,set(co)),'R343_final_common1040':(fo,fc,set(co)),'R343_expanded1041':(fo,fc,set(fc)),'R342_frozen710':(obs,co,coreids),'R343_frozen710':(fo,fc,coreids)};entrychecks=0
 for name,(oo,coords,ids) in layers.items():
  saved=ana['results'][name];seq=''
  for k,e in enumerate(saved['entries']):
   names=sorted(o for o in ids if (7*coords[o][0]+6*coords[o][1])%208==k);ct=Counter(oo[o]['color'] for o in names);strong=len(ct)==1 and len(names)>=3 and len({blocks[o] for o in names})>=3;status='conflict' if len(ct)>1 else 'strong' if strong else 'observed' if names else 'unknown';assert status==e['status'] and names==e['ids'] and dict(ct)==e['counts'];seq+=next(iter(ct))[0].upper() if strong else '?';entrychecks+=1
  assert seq==saved['strict_sequence']
 # Matched1039 targets, independent shrinkage probability tables for all8 results.
 targets=set(co)-{Q101};scorechecks=0
 for layer,oo,coords in [('R342',obs,co),('R343',fo,fc)]:
  names=sorted(coords);ks={o:(7*coords[o][0]+6*coords[o][1])%2704 for o in names}
  for result in ana['matched1039_unchanged_target_scores'][layer]:
   predictions={};baseprob={};folds=range(12) if result['holdout']=='geographic' else sorted({ks[o]//208 for o in names})
   for fold in folds:
    test=[o for o in names if (blocks[o]==fold if result['holdout']=='geographic' else ks[o]//208==fold)];training=[o for o in names if (blocks[o] not in [(fold-1)%12,fold,(fold+1)%12] if result['holdout']=='geographic' else ks[o]//208!=fold)];prior=np.array([sum(oo[o]['color']==c for o in training)+1 for c in COLORS],float);prior/=prior.sum()
    for o in test:
     ct=np.array([sum(ks[z]%208==ks[o]%208 and oo[z]['color']==c for z in training) for c in COLORS],float)
     if result['model']=='flat':prob=(ct+3*prior)/(ct.sum()+3)
     else:
      parent=np.array([sum(ks[z]%104==ks[o]%104 and oo[z]['color']==c for z in training) for c in COLORS],float);pt=(parent+3*prior)/(parent.sum()+3);prob=(ct+pt)/(ct.sum()+1)
     predictions[o]=prob;baseprob[o]=prior
   agreement=sum(COLORS[int(predictions[o].argmax())]==oo[o]['color'] for o in targets)/len(targets);gain=float(np.mean([np.log(predictions[o][COLORS.index(oo[o]['color'])]/baseprob[o][COLORS.index(oo[o]['color'])]) for o in targets]));assert abs(agreement-result['agreement'])<1e-12 and abs(gain-result['gain_nats'])<1e-12;scorechecks+=1
 panels=read(OUT/'review/panels.json')
 for r in panels:
  assert r['key'][0]==r['id'];assert np.array_equal(np.array(Image.open(OUT/'review'/r['filename'])),np.array(Image.fromarray(rgb).crop(r['crop_box'])))
 p=read(OUT/'pattern208.json');assert (p['supported'],p['conflicting'],p['insufficient'])==(197,4,7);assert p['strict_sequence'].count('?')==11
 save(OUT/'verification.json',dict(passed=True,historical_files=len(seal),native_RGB_HSV_pixels=len(points),glass_cores=25,clearance_and_RGB_patch_checks=patchchecks,old_observations_preserved=1058,old_coordinates_preserved=1040,old_links_preserved=2287,new_fixed_source_admissions=1,new_links=3,all_primitive_equations=2290,unique_sites_and_Aindices=1041,components=1,C62_independent_native_and_geometry_checks=True,C62_maker_identity_not_falsely_asserted=True,targeted_authority_refinements=1,NEW1519_red_and_protection_retained=True,position29_occurrences_checked=5,strict_entries_checked=entrychecks,heldout_metrics_checked=scorechecks,literal_native_crops=len(panels),black_detector_source_unchanged=True,pattern=[197,4,7],limits='Native core annotations and independent visible-body inspection are explicit photographic scientific inputs. Numerical replay verifies source pixels and consequences, not a second independent human inspection or a proof that all bead labels are correct.'))
 print('PASS R343 independent',len(points),'pixels',entrychecks,'strict entries',scorechecks,'heldout metrics')
if __name__=='__main__':main()
