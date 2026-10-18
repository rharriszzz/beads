"""Independent growth equations, arithmetic, literal supports and Python rays.

Does not call R328.extend, R329.replay, or any inference selector.
"""
from .common import ROOT,OUT,REF,read,save,sha
import time,hashlib,json,csv,resource
from collections import defaultdict,Counter,deque
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import map_coordinates
from photo2.r329.physical import CountChain
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES,Chain as PythonChain
from photo2.r327.verify import native_response
from photo2.r324.verify_physical import literal_support


def check_state(bank,prep,state,seed,origin,direction,frame):
 period=bank['period_px'];stations=bank['stations_px'];n=len(bank['windows']);arc=bank['windows'][origin]['arc_px'];coords={(seed,int(round((arc-stations[seed])/period))):(0,0)};equations=0;selected=set();score=0.
 for step,r in enumerate(state['path']):
  wi=r['window'];assert wi==(origin+direction*step)%n
  if step:
   prev=state['path'][step-1]['window'];arc+=direction*((direction*(bank['windows'][wi]['arc_px']-bank['windows'][prev]['arc_px']))%period)
  if r.get('skipped'):continue
  p=prep['patches'][wi][r['patch']];assert r['hypothesis']==p['hypothesis'];selected.add((wi,r['patch']));offset=np.array(r['offset']);local={(o,int(round((arc-stations[o])/period))):tuple(frame*np.array(ab)+offset) for o,ab in p['assignments'].items()};common=coords.keys()&local.keys();assert len(common)>=(1 if step==0 else 2)
  for k in common:assert coords[k]==local[k]
  assert set(map(tuple,r['attached_to']))==common
  adj=defaultdict(set)
  for a,b,d in p['edges']:
   assert np.array_equal(np.array(p['assignments'][b])-p['assignments'][a],d)
   ka=(a,int(round((arc-stations[a])/period)));kb=(b,int(round((arc-stations[b])/period)));adj[ka].add(kb);adj[kb].add(ka);equations+=1
   assert np.array_equal(np.array(local[kb])-local[ka],frame*np.array(d))
  seen=set(common);todo=list(common)
  while todo:
   x=todo.pop()
   for y in adj[x]-seen:seen.add(y);todo.append(y)
  assert local.keys()<=seen;coords.update(local);assert len(set(coords.values()))==len(coords);score+=r['score']
 assert abs(score-state['score'])<1e-8
 assert {k:tuple(map(int,v)) for k,v in coords.items()}=={(r['observation'],r['turn']):tuple(r['ab']) for r in state['coords']}
 byid=defaultdict(list)
 for (o,t),v in coords.items():byid[o].append((t,np.array(v)))
 returns=[];H=[]
 for o,rr in byid.items():
  if len(rr)<2:continue
  returns.append(o);rr.sort(key=lambda x:x[0]);t,a=rr[0]
  for u,b in rr[1:]:
   d=b-a;assert np.all(d%(u-t)==0);H.append(tuple((d//(u-t)).tolist()))
 assert sorted(returns)==state['returns']
 if H:assert len(set(H))==1 and list(H[0])==state['H']
 else:assert state['H'] is None
 return equations,selected


def main():
 started=time.perf_counter();counts=Counter();seal=read(OUT/'science-seal.json')
 for group in ['sources','inputs']:
  for p,h in seal[group].items():assert sha(ROOT/p)==h,p;counts['sealed_hashes']+=1
 for p,h in read(OUT/'final-photographic-freeze.json')['hashes'].items():assert sha(ROOT/p)==h;counts['frozen_photo_outputs']+=1
 old=read(ROOT/'photo2/r329/development/preservation-before.json')
 for p,h in old.items():assert sha(ROOT/p)==h,p
 counts['prior_files_unchanged']=len(old)
 bank=read(ROOT/'photo2/r327/results/graph.json.gz');prep=read(ROOT/'photo2/r328/development/final256/prepared.json.gz');states=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'];g=read(ROOT/'photo2/r328/results/graph.json.gz');selected=set()
 for state in states:
  eq,sel=check_state(bank,prep,state,'C-0986-0371',0,1,1);counts['growth_equations']+=eq;counts['saved_paths']+=1;selected|=sel
 for f in sorted((OUT/'traversals').glob('*.json.gz')):
  run=read(f)
  for s in run['states']:
   eq,sel=check_state(bank,prep,s,run['seed'],run['origin'],run['direction'],run['direction']);counts['growth_equations']+=eq;counts['saved_paths']+=1;selected|=sel
   if run['completed']:assert len(s['path'])==len(bank['windows'])+1 and len(s['returns'])>=3
 for r in read(OUT/'fixed-origin-replays.json.gz')['runs']:
  assert r['completed'];eq,sel=check_state(bank,prep,r['state'],r['seed'],r['origin'],r['direction'],r['direction']);counts['growth_equations']+=eq;selected|=sel
 # Verify arithmetic ledgers without calling their coordinate normalization helper.
 def base(state):
  c={}
  for r in state['coords']:
   v=np.array(r['ab'])-r['turn']*np.array(state['H'])
   if r['observation'] in c:assert np.array_equal(c[r['observation']],v)
   c[r['observation']]=v
  return {o:v-c[REF] for o,v in c.items()}
 a=base(states[0]);refst=g['stations_px'][REF]
 for z in read(OUT/'index-ledger.json.gz')['comparisons']:
  s=states[z['alternative']];b=base(s);w=np.array([7,6] if z['family']=='A' else [6,7]);direction=z['direction'];valid=[]
  for row in z['rows']:
   o=row['id'];lift=1 if direction==1 and g['stations_px'][o]<refst else -1 if direction==-1 and g['stations_px'][o]>refst else 0
   k=int(direction*((a[o]+lift*np.array(states[0]['H']))@w));other=int(direction*((b[o]+lift*np.array(s['H']))@w));assert row['k']==k and row['alternative_k']==other and row['delta']==other-k
   assert row['primary_modulo']==k%int(np.array(states[0]['H'])@w);counts['index_rows']+=1
   if k>=0:valid.append(row)
  valid.sort(key=lambda r:(r['k'],r['id']));idx=next(i for i,r in enumerate(valid) if r['delta']!=0);assert z['first']['first']==valid[idx];assert z['first']['last_agreement']==(valid[idx-1] if idx else None)
 # Compare graph origin to the historical interior association, not a model address.
 ref=read(OUT/'reference.json');assert ref['id']==REF and ref['xy']==next(o['xy'] for o in g['observations'] if o['id']==REF)
 established=read(ROOT/'photo2/r328/results/established-subset.json');assert any(r['target']==REF and r['maker_target']==15 for r in established['links'])
 # Every selected native pair independently checks foreground and intervening supports.
 from photo2.r325.tracker import preprocess
 im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');rgb=np.array(im);fields=preprocess(im);fg=fields['fg'].astype(np.float32);op={o['id']:o for o in g['observations']};xy=np.array([o['xy'] for o in g['observations']]);ids=[o['id'] for o in g['observations']];pairs=set();hyps=set()
 for wi,pi in selected:
  p=prep['patches'][wi][pi];hyps.add((wi,p['hypothesis']))
  for a,b,d in p['edges']:pairs.add(tuple(sorted((a,b))))
 for a,b in pairs:
  x,y=np.array(op[a]['xy']),np.array(op[b]['xy']);v=y-x;d=xy-x;f=d@v/(v@v);perp=np.linalg.norm(d-f[:,None]*v,axis=1);near={ids[i] for i in np.flatnonzero((f>.2)&(f<.8)&(perp<7))}-{a,b};assert not near
  pts=np.linspace(x,y,31);value=float(map_coordinates(fg,[pts[:,1],pts[:,0]],order=1,mode='nearest').mean());assert value>.95
 counts['native_neighbor_pairs']=len(pairs)
 max_affine=0.
 for wi,hi in sorted(hyps):
  if wi not in list(range(10,35))+list(range(74,84))+list(range(121,130)):continue
  h=bank['windows'][wi]['hypotheses'][hi]
  # All targets at suspect windows: direct original-pixel convolution plus independently solved weighted least squares.
  for r in h['r327_evidence']['rows']:
   target=r['observation'];anchors=r['anchor_ids'];assert target not in anchors;a0=np.array(h['assignments'][target]['ab']);ab=np.array([h['assignments'][o]['ab'] for o in anchors])-a0;scale=max(float(np.median(np.linalg.norm(ab,axis=1))),1);u=ab/scale;wt=np.exp(-np.sum(u*u,axis=1)/8);X=np.column_stack([np.ones(len(u)),u]);y=np.array([op[o]['xy'] for o in anchors]);coef=np.linalg.lstsq(X*np.sqrt(wt[:,None]),y*np.sqrt(wt[:,None]),rcond=None)[0];delta=float(np.linalg.norm(coef[0]-r['predictions_xy'][0]));assert delta<1e-7;max_affine=max(max_affine,delta)
   assert abs(native_response(rgb,op[target]['xy'],op[target]['color'])-r['observed_native_response'])<1e-10
   for pred,val in zip(r['predictions_xy'],r['predicted_native_responses']):assert abs(native_response(rgb,pred,op[target]['color'])-val)<1e-10
   counts['independent_affine_native_rows']+=1
 for c in read(OUT/'native-crops.json')['crops']:assert np.array_equal(np.array(im.crop(c['box'])),np.array(Image.open(OUT/(c['name']+'-native.png'))));counts['exact_native_crops']+=1
 # Screen arithmetic, without using the enumerator.
 screen=read(OUT/'count-screen.json.gz')['rows'];assert [z['N'] for z in screen]==list(range(2000,3601))
 for z in screen:
  assert z['complete_252_repeats']==(z['N']%252==0)
  for h in z['algebraic_windings']:
   w=[7,6] if h['family']=='A' else [6,7];assert sum(a*b for a,b in zip(h['H'],w))==z['N'];counts['count_equations']+=1
 # Color equality constraints from unordered pairs; test reversal and arbitrary origin.
 for filename in ['periods.json.gz','novel-periods.json.gz']:
  for result in read(OUT/filename)['results']:
   rr=result['rows']
   for check in result['periods']:
    pp=check['period'];groups=defaultdict(list)
    for r in rr:groups[(-r['k']+113)%pp].append(r['color'])
    conflicts=sum(sum(any(c!=v for v in colors[:i]) for i,c in enumerate(colors)) for colors in groups.values());pairs=sum(len(colors)*(len(colors)-1)//2 for colors in groups.values());assert conflicts==check['conflict_witnesses'] and pairs==check['pair_comparisons'];assert check['complete_repeat_divides_N']==(result['N']%pp==0);counts['period_checks']+=1
 # Literal support verification for all certified new physical geometries, not just winners.
 data=load()[0];records=[read(f) for f in sorted((OUT/'physical-trials').glob('*.gz'))]+read(OUT/'matched-physical.json.gz')['trials']+read(OUT/'novel-physical.json.gz')['trials']+read(OUT/'frozen-geometry-controls.json.gz')['controls'];seen={};raymodels=[];minimum=1e9
 for r in records:
  if 'parameters' not in r:continue
  key=json.dumps(r['parameters'],sort_keys=True)
  if key in seen:continue
  seen[key]=True;s=CountChain(r['parameters'],data);assert s.n==len(s.indices);line,gg,_=s.placement([s.start,s.start+s.n]);cent=line+s.p['minor']*gg['radial'];assert np.linalg.norm(cent[1]-cent[0])<1e-7
  if r['contact']['certified']:
   cert=s.certify(iterations=120,witnesses=True);assert cert['certified'];ww=cert['witnesses'];aa=np.array([w['pair'][0] for w in ww]);bb=np.array([w['pair'][1] for w in ww]);nn=np.array([w['normal'] for w in ww]);gap=np.sum((s.centers[bb]-s.centers[aa])*nn,axis=1)-literal_support(nn,s.g[AXES[0]][aa],s.radius,s.axial)-literal_support(nn,s.g[AXES[0]][bb],s.radius,s.axial);assert gap.min()>1e-6;assert np.max(abs(gap-np.array([w['gap_units'] for w in ww])))<1e-9;counts['literal_support_witnesses']+=len(ww);minimum=min(minimum,float(gap.min()))
   if s.n in [2016,2516,2554,2690,2691,2692,2703,2704,2705,2772,3000,3528] and s.n not in [z.n for z in raymodels]:raymodels.append(s)
  if r['contact']['classification']=='demonstrated-interpenetration':
   for w in r['contact']['actual_solid_checks']:
    if w['state']!='demonstrated-interpenetration':continue
    for j in w['pair']:
     delta=np.array(w['point'])-s.centers[j];q=np.array([delta@s.g[k][j] for k in AXES]);assert s.local_sdf(q)<0
    counts['actual_penetration_witnesses']+=1
 counts['unique_physical_geometries']=len(seen);rng=np.random.default_rng(329);rays=[]
 for s in raymodels:
  js=rng.choice(s.n,40,replace=False);xy=s.pc[js]+rng.uniform(-s.radius*s.scale,s.radius*s.scale,(40,2));fast=s.camera(xy);slow=PythonChain.trace(s,xy,True);known=~fast['unknown']&~slow['unknown'];assert np.array_equal(fast['owner'][known],slow['owner'][known]);hit=known&(fast['owner']>=0);err=float(np.max(np.linalg.norm(fast['points'][hit]-slow['points'][hit],axis=1))) if hit.any() else 0;assert err<1e-8;counts['original_python_rays']+=len(xy);rays.append(dict(N=s.n,known=int(known.sum()),point_max_difference=err))
 # Native optical cohort arithmetic and independently weighted original centroids.
 for r in [read(f) for f in sorted((OUT/'native-physical').glob('*.gz'))]+read(OUT/'frozen-geometry-controls.json.gz')['controls']:
  if 'native' not in r or not r['native'].get('feasible'):continue
  native=r['native'];rows=native['rows'];missing=sum(z['predicted'] is None for z in rows);assert missing==native['missing'] and bool(missing)==native['maximum_is_infinite'];errors=[]
  for z in rows:
   if z['predicted'] is None:continue
   err=float(np.linalg.norm(np.array(z['predicted'])-z['observed']));assert abs(err-z['error_px'])<1e-9;errors.append(err);counts['reflection_errors']+=1
  if not missing:assert abs(max(errors)-native['emax_px'])<1e-9
 for r in read(ROOT/'photo2/r324/results/fit-evidence.json')['reflections']:
  xy=np.array(r['pixels'],int);rgb0=rgb[xy[:,1],xy[:,0]]/255;lin=np.where(rgb0<=.04045,rgb0/12.92,((rgb0+.055)/1.055)**2.4);point=np.average(xy,axis=0,weights=lin.min(1));assert np.max(abs(point-r['point']))<1e-9;counts['raw_photo_reflection_centroids']+=1
 # Failure-oriented corruption: a single altered coordinate must break the saved path audit.
 import copy
 corrupt=copy.deepcopy(states[0]);corrupt['coords'][0]['ab'][0]+=1
 try:check_state(bank,prep,corrupt,'C-0986-0371',0,1,1)
 except AssertionError:counts['corruption_controls']+=1
 else:raise AssertionError('Corrupted coordinate accepted')
 result=dict(passed=True,counts=dict(counts),minimum_literal_gap=minimum,max_independent_affine_error_px=max_affine,python_ray_models=rays,seconds=time.perf_counter()-started,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,limits='Independent arithmetic/geometry/image measurements, not new truth labels or global photographic accuracy. All prior tracked scientific files hash-identical.');save(OUT/'verification.json',result);print('VERIFIED',result,flush=True)
if __name__=='__main__':main()
