"""Independent data checks and negative controls for the diagnostic supplement."""
from .continuity import *
import hashlib,re,copy
from photo2.r295.geometry import Chain as PythonChain
from photo2.r321.model import Chain
from photo2.r306.evidence import load

def main():
 t=time.perf_counter();checks={};baseline=read(OUT/'baseline.json');archives={'photo2/r329/ILLUSTRATED_GUIDE.md':'photo2/r329/ILLUSTRATED_GUIDE_BEFORE_BODY_REVIEW.md','photo2/r329/guide/READING_THE_PHOTOGRAPH.md':'photo2/r329/guide/READING_THE_PHOTOGRAPH_BEFORE_BODY_REVIEW.md'}
 for name,sha in baseline.items():
  path=ROOT/archives.get(name,name);assert hashlib.sha256(path.read_bytes()).hexdigest()==sha,name
 checks['preserved_baseline_files']=len(baseline);checks['guide_archives']=archives
 data=read(OUT/'continuity.json.gz')['cases'];pixels=0;negative=0;swaps=0
 for case,c in data.items():
  cfg=c['config'];pts={}
  for oid,m in c['measurements'].items():
   assert OBS[oid]['color']!='black';px=np.array(m['pixels']);assert len(np.unique(px,axis=0))==len(px);assert np.allclose(px.mean(0),m['center']);pts[oid]=px.mean(0);pixels+=len(px)
   # Independently check every selected native RGB pixel against its color ratios.
   rgb=IM[px[:,1],px[:,0]];r,g,b=rgb.T
   ok=(r>1.8*g)&(r>2.5*b)&(r>.16) if m['color']=='red' else (g>.45*r)&(g>1.8*b)&(r>.9*g)&(r>.16)
   assert ok.all();assert np.max(np.linalg.norm(px-np.array(OBS[oid]['xy']),axis=1))<=18+1e-8
  vv=vectors(cfg,pts)
  if case!='F':assert all(cfg['target'] not in [r['a'],r['b']] for r in vv)
  for st,p in c['central']['predictions'].items():
   for kind in ['black','target']:
    delta=p[kind+'_delta'];expected=predict(vv,pts[cfg['anchor']],delta)
    assert np.allclose(expected,p[kind+'_predictions'])
    old=copy.deepcopy(OBS[cfg['black']]);OBS[cfg['black']]['xy']=[-1e6,1e6]
    changed=predict(vectors(cfg,{o:measure(OBS[o])[0] for o in pts}),pts[cfg['anchor']],delta);OBS[cfg['black']]=old
    assert np.array_equal(expected,changed);negative+=1
    # Exchange family names and coordinate components; geometry must be invariant.
    exchange=[dict(r,family=1-r['family']) for r in vv];q=predict(exchange,pts[cfg['anchor']],delta[::-1]);assert np.allclose(sorted(expected.tolist()),sorted(q.tolist()));swaps+=1
  # Alter only the other family's vectors. A single-family prediction must not move.
  for f in [0,1]:
   delta=[0,0];delta[f]=1;a=predict(vv,pts[cfg['anchor']],delta);altered=[dict(r,v=r['v']*100) if r['family']!=f else r for r in vv];assert np.array_equal(a,predict(altered,pts[cfg['anchor']],delta))
 checks.update(pigment_pixel_occurrences=pixels,black_coordinate_negative_controls=negative,family_exchange_controls=swaps,other_family_isolation_controls=8)
 bank=read(ROOT/'photo2/r327/results/graph.json.gz');prep=read(ROOT/'photo2/r328/development/final256/prepared.json.gz')
 for r in read(OUT/'candidate-provenance.json.gz')['rows']:
  wi=r['window'];path=r['path'];assert path==ST['closest' if r['state']=='alternative' else r['state']]['path'][wi];assert r['patch']==prep['patches'][wi][path['patch']];assert r['hypothesis']==bank['windows'][wi]['hypotheses'][path['hypothesis']]
 checks['exact_candidate_provenance_records']=6
 gd=read(OUT/'growth-diagnostic.json');assert gd['cases']['E']['closest']['status']=='family_mismatch';assert gd['cases']['E']['working']['status']=='same_family'
 for c in ['G','H']:assert all(v['status']=='direction_uncertain' for v in gd['cases'][c].values())
 result=read(OUT/'screened-growth.json.gz');best=result['states'][0];assert canonical(best)==CO['working'];assert len(canonical(best))==900
 assert gd['experimental_search']['completed'] and best['H']==[214,201]
 for r in gd['replays']:assert r['receipt']['completed'] and r['receipt']['returns']==17
 assert 'C-1144-2947' not in CO['lower'] and len(CO['lower'])==899
 checks['screened_map_equals_primary']=True;checks['unique_indexed']=900;checks['saved_path_returns']=[r['receipt']['returns'] for r in gd['replays']]
 # Compare the raster against original Python camera rays, independent of the native tracer.
 m=np.load(OUT/'model-geometry.npz');frozen=read(ROOT/'photo2/r324/results/R321-geometry-best-frozen.json.gz');s=Chain(frozen['parameters'],load()[0]);assert np.array_equal(m['projected'],s.pc)
 rng=np.random.default_rng(329);sample=rng.choice(len(m['xy']),120,replace=False);slow=PythonChain.trace(s,m['xy'][sample],True);known=~slow['unknown'];assert known.sum()>=110;assert np.array_equal(slow['owner'][known],m['owner'][sample][known])
 checks['independent_python_camera_rays']=len(sample);checks['python_camera_resolved']=int(known.sum());checks['model_center_max_delta']=float(abs(s.pc-np.array(frozen['positions']['projected'])).max())
 for addr in [-33,-27]:
  iso=m['isolated_'+str(addr)].reshape(m['shape']);assert not np.any(np.r_[iso[0],iso[-1],iso[:,0],iso[:,-1]])
 owner=m['owner'].reshape(m['shape']);bb=m['bbox'];step=float(m['step'])
 for row in read(OUT/'colored-model-comparison.json'):
  for v in row['variants']:
   _,px=measure(OBS[row['id']],v['radius'],v['threshold']);jj=int(np.flatnonzero(m['indices']==row['model_address'])[0]);hits=owner[((px[:,1]-bb[1])/step).astype(int),((px[:,0]-bb[0])/step).astype(int)]==jj
   assert len(px)==v['pixels'] and int(hits.sum())==v['covered']
 checks['coverage_variants_recomputed']=27
 figs=read(OUT/'figures.json');assert len(figs)==14;labels=0
 for fig in figs:
  im=Image.open(OUT/'images'/fig['file']);assert im.width==1600 and im.height>=1290
  ids={l['id'] for l in fig['labels']};assert len(ids)==len(fig['labels']);labels+=len(ids)
  for l in fig['labels']:assert np.allclose(l['center'],data[fig['case']]['measurements'][l['id']]['center'])
 for case in 'EFGH':
  box=[1525,220,1710,370] if case=='G' else data[case]['config']['box'];raw=np.asarray(Image.open(OUT/'images'/('raw-'+case.lower()+'.png')));assert np.array_equal(raw,np.rint(IM[box[1]:box[3],box[0]:box[2]]*255).astype(np.uint8))
 checks['raw_crops_exact']=4;checks['figures']=14;checks['label_occurrences']=labels
 # Every local file link must resolve, including archives; internal anchors checked below.
 docs=[OUT/'README.md',OUT/'METHOD_REPORT.md',ROOT/'photo2/r329/ILLUSTRATED_GUIDE.md',ROOT/'photo2/r329/guide/READING_THE_PHOTOGRAPH.md'];links=0
 for doc in docs:
  for href in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',doc.read_text()):
   if href.startswith(('https:','http:')):continue
   path,_,anchor=href.partition('#');dest=(doc.parent/path).resolve() if path else doc
   if dest.name in ['verification.json','browser-verification.json'] and not dest.exists():continue
   assert dest.exists(),(doc,href);links+=1
   if anchor:
    headings=re.findall(r'^#+ (.+)$',dest.read_text(),re.M);slugs=[re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-') for h in headings];assert anchor in slugs,(href,slugs)
 checks['local_links']=links;checks['seconds']=time.perf_counter()-t;checks['passed']=True
 (OUT/'verification.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
