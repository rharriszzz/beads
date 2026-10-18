"""Fixed-reference frozen 3D ledgers and isolated correspondence/geometry controls."""
from .common import *
from .physical import CountChain
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from photo2.r324.coupled import support_ledger,optical
from photo2.r321.packing import curvature
from scipy.spatial import cKDTree
from collections import Counter
from copy import deepcopy

def main():
 began=time.perf_counter();g=read(ROOT/'photo2/r328/results/graph.json.gz');state=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'][0];coords=canonical(state);obs={o['id']:o for o in g['observations']};data=load()[0];models=[]
 for label in ['R321-geometry-best','R321-photo-sized-rescue']:
  source=ROOT/f'photo2/r324/results/{label}-frozen.json.gz';m=read(source);s=CountChain(m['parameters'],data);assert np.max(abs(s.pc-np.array(m['positions']['projected'])))<1e-8
  support={z['id']:z for z in m['support']};native={r['observation']:r for r in m['native']['rows']};rast=np.load(ROOT/f'photo2/r324/results/{label}-raster.npz');kappa=curvature(s);families=[]
  for name,weights in WEIGHTS.items():
   option=min((z for z in m['seed_options'] if z['interpretation']==name),key=lambda z:z['loss']);origin=option['mapping'][REF];rows=[]
   for oid,ab in coords.items():
    if oid not in support:continue
    sr=support[oid];k=int(np.dot(ab,weights));j=int((origin+k-s.indices[0])%s.n);idx=int(s.indices[j]);modal=sr['modal_index'];d=int((modal-idx+s.n//2)%s.n-s.n//2) if modal is not None and sr['modal_fraction']>=.6 else None
    fraction=next((z['fraction'] for z in sr['owners'] if z['index']==idx),0.);visible=rast['xy'][rast['owner']==j];vd=float(cKDTree(visible).query(obs[oid]['xy'])[0]) if len(visible) else None
    nr=native.get(oid);reflection=nr if nr and nr['index']==idx else None
    rows.append(dict(id=oid,xy=obs[oid]['xy'],color=obs[oid]['color'],ab=ab,k=k,photo_modulo=k%abs(int(np.dot(state['H'],weights))),model_address=idx,model_modulo=(origin+k)%s.n,modal_address=modal,modal_fraction=sr['modal_fraction'],delta=d,support_ownership=fraction,projected_center=s.pc[j].tolist(),center_to_support_proxy_px=float(np.linalg.norm(s.pc[j]-obs[oid]['xy'])),visible_region_distance_px=vd,reflection_error_px=reflection['error_px'] if reflection else None,reflection_observed=reflection['observed'] if reflection else None,reflection_predicted=reflection['predicted'] if reflection else None,curvature=float(kappa[j]),owners=sr['owners']))
   rows.sort(key=lambda r:(r['k'],r['id']));traces={str(d):trace_first(rows,direction=d) for d in [-1,1]}
   # Persistent departure requires 3 of next 5 confident observations, not a numerical epsilon.
   positive=[r for r in rows if r['k']>=0 and r['delta'] is not None];persistent=next((dict(first=r,next_five=positive[i:i+5]) for i,r in enumerate(positive) if abs(r['delta'])>=1 and sum(abs(z['delta'])>=1 for z in positive[i:i+5])>=3),None)
   families.append(dict(family=name,weights=weights,reference_address=origin,conditional_photo_N=abs(int(np.dot(state['H'],weights))),model_N=s.n,closure_index_mismatch=s.n-abs(int(np.dot(state['H'],weights))),rows=rows,first=traces,persistent_forward=persistent))
  primary=next(z for z in families if z['family']==m['seed_options'][0]['interpretation']);first=primary['first']['1']['first'];boundary=first['k'];shift=first['delta'];cf=[]
  for scope in ['single_observation','suffix']:
   changed=[];mapping={}
   for row in primary['rows']:
    active=row['id']==first['id'] if scope=='single_observation' else row['k']>=boundary
    idx=int(s.indices[(row['model_address']+shift*active-s.indices[0])%s.n]);fraction=next((z['fraction'] for z in row['owners'] if z['index']==idx),0.)
    mapping[row['id']]=idx;changed.append(dict(id=row['id'],k=row['k'],before=row['support_ownership'],after=fraction,before_address=row['model_address'],after_address=idx))
   broken=[]
   for e in g['graph']['edges']:
    a,b=e['source'],e['target']
    if a not in mapping or b not in mapping:continue
    expected=int(np.dot(e['delta_ab'],primary['weights']));actual=int((mapping[b]-mapping[a]+s.n//2)%s.n-s.n//2)
    # Count only newly broken links, removing inherited physical/photo closure incompatibility.
    olda=next(r['model_address'] for r in primary['rows'] if r['id']==a);oldb=next(r['model_address'] for r in primary['rows'] if r['id']==b);old=int((oldb-olda+s.n//2)%s.n-s.n//2)
    if actual!=expected and old==expected:broken.append(dict(source=a,target=b,expected=expected,after=actual))
   groups={}
   for name,rr in [('prefix',[r for r in changed if 0<=r['k']<boundary]),('next200',[r for r in changed if boundary<=r['k']<boundary+200]),('remainder',[r for r in changed if r['k']>=boundary])]:
    groups[name]=dict(observations=len(rr),before_mean=float(np.mean([r['before'] for r in rr])) if rr else None,after_mean=float(np.mean([r['after'] for r in rr])) if rr else None,improved=sum(r['after']>r['before'] for r in rr),worsened=sum(r['after']<r['before'] for r in rr))
   cf.append(dict(scope=scope,boundary=boundary,shift=shift,groups=groups,newly_broken_links=broken,rows=changed,policy='Isolated correspondence intervention on fixed geometry. Suffix replay is deterministic address propagation; breaks photo links and cannot be adopted as a valid lattice correction.'))
  models.append(dict(label=label,source_sha256=sha(source),families=families,selected_family=primary['family'],counterfactuals=cf,first_forward=primary['first']['1'],first_reverse=primary['first']['-1'],native_scope='Visible-region distances available only inside archived seed raster; null elsewhere. Center-support distance is a proxy, never a measured center error.'))
 save(OUT/'frozen-ledger.json.gz',dict(reference=REF,models=models,seconds=time.perf_counter()-began))
 # Geometry controls at the frozen N3000 first departure. Same addresses, camera and reference.
 base=read(ROOT/'photo2/r324/results/R321-geometry-best-frozen.json.gz');chosen=models[0];family=next(z for z in chosen['families'] if z['family']==chosen['selected_family']);p=base['parameters'];local=[obs[r['id']] for r in family['rows'] if -50<=r['k']<=200];pixels={r['id']:np.array(r['pixels_xy']) for r in read(ROOT/'photo2/r324/results/observation-pixels.json')};local=[o for o in local if o['id'] in pixels];mapping={r['id']:r['model_address'] for r in family['rows']};refs=[r for r in read(ROOT/'photo2/r324/results/fit-evidence.json')['reflections'] if r['observation'] in {o['id'] for o in local}];controls=[]
 for kind,value in [('baseline',0),('phase',-.15),('phase',-.075),('phase',.075),('phase',.15),('s0',-3.),('s0',3.),('uniform',0)]:
  t=time.perf_counter();q=deepcopy(p)
  if kind=='phase':q['phase']+=value
  if kind=='s0':q['s0']+=value
  if kind=='uniform':q['packing_spacing']='uniform'
  s=CountChain(q,data);cert=contacts(s,seconds=.5);record=dict(kind=kind,value=value,parameters=q,contact={k:v for k,v in cert.items() if k!='witnesses'},mapping=mapping)
  if cert['certified']:
   rr,frac,nr=support_ledger(s,local,pixels);diagnostic=[]
   for i,o in enumerate(local):
    old=next(z for z in family['rows'] if z['id']==o['id']);j=int((mapping[o['id']]-s.indices[0])%s.n);diagnostic.append(dict(id=o['id'],k=old['k'],before=old['support_ownership'],after=float(frac[i,j]),modal_index=rr[i]['modal_index'],modal_fraction=rr[i]['modal_fraction']))
   record['support_rows']=diagnostic;record['support_rays']=nr;record['prefix_mean']=float(np.mean([r['after'] for r in diagnostic if 0<=r['k']<31]));record['next200_mean']=float(np.mean([r['after'] for r in diagnostic if 31<=r['k']<=200]));record['first_support']=next(r for r in diagnostic if r['id']=='K-1398-0248')
   native,raster=optical(s,sorted({mapping[o['id']] for o in local}),refs,mapping,'Fixed-address geometry control around first frozen-model divergence',certificate=cert,grouped=True);record['native']=native
  record['seconds']=time.perf_counter()-t;controls.append(record)
 save(OUT/'frozen-geometry-controls.json.gz',dict(controls=controls,policy='Global phase/station and spacing interventions, fixed physical addresses relative to C-1302. No per-bead transforms. Contact failure blocks optics. All original photo and model sources unchanged.'))
 print('FROZEN',[(m['label'],m['first_forward']['first']['id'],m['first_forward']['first']['k']) for m in models],[(z['kind'],z['value'],z['contact']['classification'],z.get('prefix_mean'),z.get('next200_mean')) for z in controls],flush=True)
if __name__=='__main__':main()
