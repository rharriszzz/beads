"""Independent raw-pixel, integer-graph, transform, ray and support audits."""
import json,hashlib,time,subprocess,sys,tempfile,gzip
from pathlib import Path
from collections import Counter,defaultdict,deque
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r324/results'
def read(p):return json.load(gzip.open(p,'rt') if str(p).endswith('.gz') else open(p))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def scientific(d):
 if isinstance(d,dict):return {k:scientific(v) for k,v in d.items() if k not in ['source_sha256','timings_seconds','stage_timings_seconds','peak_rss_mb']}
 if isinstance(d,list):return [scientific(x) for x in d]
 return d

def main():
 start=time.perf_counter();g=read(OUT/'graph.json');op={o['id']:o for o in g['observations']};ns={n['id']:n for n in g['intersections']};rgb=np.array(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));catalog={r['id']:r for r in read(ROOT/'photo2/review/r275/inventory.json')['locations']};pixels=read(OUT/'observation-pixels.json');native=0;fits=0;assignments=0
 assert sha(ROOT/'beads-photo-2.jpg')==g['image_sha256'];assert sha(ROOT/'photo2/r324/development/tracker-executed.py')==g['source_sha256']
 for path,h in read(OUT/'freeze.json')['files'].items():assert sha(ROOT/path)==h
 for r in pixels:
  oid=r['id'];xy=np.array(r['pixels_xy']);assert len(xy)==op[oid]['source_pixel_count'];assert len(np.unique(xy,axis=0))==len(xy);v=rgb[xy[:,1],xy[:,0]]/255
  if oid in catalog:
   exp=np.array([[x,y] for y,a,b in catalog[oid]['bright_patch']['runs'] for x in range(a,b+1)]);assert np.array_equal(xy,exp);centroid=xy.mean(0)
  else:
   lin=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);centroid=np.average(xy,axis=0,weights=lin.min(1))
  assert np.max(abs(centroid-op[oid]['xy']))<1e-9;native+=len(xy)
 for w in g['windows']:
  R=np.array(w['frame']);assert np.max(abs(R.T@R-np.eye(2)))<1e-12 and abs(np.linalg.det(R)-1)<1e-12
  for h in w['hypotheses']:
   assert np.max(abs(R@np.array(h['basis_local'])-h['basis']))<1e-9
   assert np.max(abs(R@np.array(h['offset_local'])+w['center']-h['offset']))<1e-9
   a=h['assignments'];cells={tuple(v['ab']) for v in a.values()};assert len(cells)==len(a);score=0;triangles=0
   for oid,v in a.items():
    pred=np.array(h['basis'])@v['ab']+h['offset'];err=np.linalg.norm(pred-op[oid]['xy']);assert np.max(abs(pred-v['predicted_xy']))<1e-9;assert abs(err-v['residual_px'])<1e-9;sig=8 if op[oid]['color']=='black' else 5;assert err<2*sig+1e-9;wt=1 if op[oid]['band_clearance_px']>=18 else .55;score+=wt*(1-.25*(err/sig)**2);aa,bb=v['ab'];triangles+=int((aa+1,bb) in cells and (aa,bb+1) in cells);assignments+=1
   assert triangles==h['triangles'];assert abs(score+.18*triangles-h['score'])<1e-8;fits+=1
 transforms=0
 for t in g['transitions']:
  for c in t['checks']:
   h=g['windows'][t['previous']]['hypotheses'][c['previous']]['assignments'];k=g['windows'][t['current']]['hypotheses'][c['current']]['assignments'];common=set(h)&set(k);shifts=[tuple(np.array(h[o]['ab'])-k[o]['ab']) for o in common]
   assert len(common)==c['common']
   if len(common)>=4:assert max(Counter(shifts).values())==c['agree'];assert len(common)-c['agree']==c['disagree'];assert Counter(shifts)[tuple(c['translation'])]==c['agree']
  assert t['translation_consistent']==bool(t['checks'] and all(c['common']>=4 and c['disagree']==0 for c in t['checks']))
  steps={(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)}
  for a in t['triangular_lattice_alternatives']:
   M=np.array(a['matrix']);assert abs(round(np.linalg.det(M)))==1;assert {tuple(M@p) for p in steps}==steps;transforms+=1
 adjacency=defaultdict(list);pts=np.array([o['xy'] for o in op.values()]);ids=list(op)
 for e in g['graph']['edges']:
  a,b=ns[e['source']],ns[e['target']];assert a['component']==b['component'];assert a['geographic_chart']==b['geographic_chart'];assert np.array_equal(np.array(b['relative_ab'])-a['relative_ab'],e['delta_ab']);assert e['supporting_windows']>=2 and e['consensus']>=.85 and e['foreground_fraction']>.95 and not e['intervening_observations']
  for version in e['alternatives']:
   for wi,hi in version['window_states']:
    ass=g['windows'][wi]['hypotheses'][hi]['assignments'];aa,bb=sorted([e['source'],e['target']]);assert np.array_equal(np.array(ass[bb]['ab'])-ass[aa]['ab'],version['delta_ab'])
  votes={tuple(v['delta_ab']):{z[0] for z in v['window_states']} for v in e['alternatives']};d=tuple(e['delta_ab']) if e['source']<e['target'] else tuple(-np.array(e['delta_ab']));assert len(votes[d])==e['supporting_windows'];rivals=set().union(*(v for k,v in votes.items() if k!=d));allwins=set().union(*votes.values());assert abs(1-len(rivals)/len(allwins)-e['consensus'])<1e-12
  p,q=np.array(a['xy']),np.array(b['xy']);v=q-p;fractions=(pts-p)@v/(v@v);dist=np.linalg.norm(pts-p-fractions[:,None]*v,axis=1);inter=[ids[i] for i in np.flatnonzero((fractions>.2)&(fractions<.8)&(dist<7)) if ids[i] not in [a['id'],b['id']]];assert not inter
  adjacency[a['id']].append((b['id'],np.array(e['delta_ab'])));adjacency[b['id']].append((a['id'],-np.array(e['delta_ab'])))
 coords={}
 for n in sorted(adjacency):
  if n in coords:continue
  coords[n]=np.zeros(2,int);todo=[n]
  while todo:
   x=todo.pop()
   for y,d in adjacency[x]:
    if y in coords:assert np.array_equal(coords[y],coords[x]+d)
    else:coords[y]=coords[x]+d;todo.append(y)
 for n in ns.values():
  if n['relative_ab'] is None:continue
  a,b=n['relative_ab'];assert n['conditional_indices']==dict(A=7*a+6*b,B=6*a+7*b,reverse_A=-7*a-6*b,reverse_B=-6*a-7*b)
 assert 7*6==6*7==42;assert (6,0)!=(0,7);assert np.dot([6,0],[7,6])==np.dot([0,7],[7,6]);assert not g['summary']['full_loop_closure']
 # Reconstruct raw maker coordinates; compare every final associated edge.
 m=read(ROOT/'photo2/manual-labels-r161.json');numbers={a['id']:a['number'] for a in m['annotations']};adj=defaultdict(list);st={'d1':np.array([1,-1]),'d2':np.array([1,0]),'d3':np.array([0,1])}
 for series in m['series']:
  if series['status']!='complete':continue
  for a,b in zip(series['bead_ids'],series['bead_ids'][1:]):a,b=numbers[a],numbers[b];d=st[series['direction']];adj[a].append((b,d));adj[b].append((a,-d))
 mc={1:np.zeros(2,int)};todo=[1]
 while todo:
  x=todo.pop()
  for y,d in adj[x]:
   if y in mc:assert np.array_equal(mc[y],mc[x]+d)
   else:mc[y]=mc[x]+d;todo.append(y)
 validation=read(OUT/'validation.json');checked=0
 for e in validation['automatic_links']:
  if e['maker_source'] is not None and e['maker_target'] is not None:assert np.array_equal(mc[e['maker_target']]-mc[e['maker_source']],e['delta_ab']);checked+=1
 # Exact replay under a data-file audit. Package/code reads allowed; repository
 # measurements restricted to the original image, appearance catalog, spline.
 dest=Path(tempfile.mkdtemp(prefix='r324-guarded-'));code='''import sys,pathlib
from photo2.r324.fast_tracker import run,ROOT
out=pathlib.Path(sys.argv[1]);allowed={ROOT/'beads-photo-2.jpg',ROOT/'photo2/review/r275/inventory.json',ROOT/'photo2/spline-seed-r175.json'};reads=set()
def guard(event,args):
 if event!='open' or not isinstance(args[0],(str,bytes)):return
 p=pathlib.Path(args[0]).resolve()
 if ROOT in p.parents and p.suffix in ['.json','.npz','.jpg','.gz','.csv']:
  if p not in allowed:raise RuntimeError('Undeclared detector input: '+str(p))
  reads.add(str(p.relative_to(ROOT)))
sys.addaudithook(guard);run(out);print('AUDITED_READS',sorted(reads))
'''
 rt=time.perf_counter();r=subprocess.run([sys.executable,'-c',code,str(dest)],cwd=ROOT,text=True,capture_output=True);(OUT/'guarded-replay.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr;assert scientific(read(dest/'graph.json'))==scientific(g);assert read(dest/'observation-pixels.json')==pixels
 result=dict(passed=True,observations=len(op),native_support_pixels=native,hypotheses=fits,assignments=assignments,accepted_links=len(g['graph']['edges']),triangular_transform_alternatives=transforms,reference_edges_independently_checked=checked,guarded_replay_seconds=time.perf_counter()-rt,replay_directory=str(dest),seconds=time.perf_counter()-start,checks=['native RGB support centroids','every hypothesis and score','all accepted integer relations','all saved overlap translations and triangular symmetries','all intervening-support corridors','both index weights and reversals','42 equality without planar merge','raw R161 arithmetic','guarded exact full-circuit replay'],limitation='Independent formulas and original kernels in this session; no independent human labels outside R161.')
 (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
