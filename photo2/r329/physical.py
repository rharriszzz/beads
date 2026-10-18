"""Wide count screens and fixed-reference physical diagnostics, no tracking feedback."""
from .common import *
from copy import deepcopy
from collections import Counter
from scipy.spatial import cKDTree
from photo2.r321.model import Chain as FrozenChain,parameters
from photo2.r314.geometry import ShapeChain,contacts
from photo2.r321.packing import side_planes,MARGIN,curvature
from photo2.r320.audit import support
from photo2.r295.geometry import AXES
from photo2.r306.evidence import load
from photo2.r324.coupled import support_ledger,optical

class CountChain(FrozenChain):
 """Same literal glass and derived orientation; allow neighboring integer W.

 R321's nearest-W restriction is intentionally relaxed here only. All bodies,
 closed seam, zero fields, shared shape, and full spatial contact checks remain.
 """
 def __init__(self,p,data):
  assert p['count']==int(p['count']) and p['winding']==int(p['winding']) and p['winding']>0
  assert abs(p['turn']-p['count']/p['winding'])<1e-12
  assert p['topology']=='closed' and p['gap_steps']==0 and p['seam_fraction']==-.5
  ShapeChain.__init__(self,p,data)

def construct(p,data):
 t=time.perf_counter();q=deepcopy(p);s=CountChain(q,data);P=s.length/q['winding'];T=q['turn'];r=q['radius'];sn=np.sin(np.pi/T);cs=np.cos(np.pi/T);D=2*r+MARGIN*r;A=P*P*cs/(2*np.pi*T);B=(P*cs/(2*np.pi))**2
 roots=np.roots([4*sn*sn,4*sn*A-D*D,A*A-D*D*B]);valid=[float(x.real) for x in roots if abs(x.imag)<1e-10 and x.real>0]
 if not valid:return None,dict(classification='unresolved-radius-root',seconds=time.perf_counter()-t)
 q['minor']=float(np.sqrt(max(valid)));s=CountChain(q,data);history=[]
 for _ in range(5):
  g,n,aa,bb=side_planes(s);j=int(np.argmin(g));low=float(g[j]);history.append(dict(minor=s.p['minor'],minimum_plus1_plane=low))
  if low>=MARGIN*r*.95:break
  q=deepcopy(s.p);dr=1e-3*r;q['minor']+=dr;test=CountChain(q,data);delta=test.centers[bb[j]]-test.centers[aa[j]];nn=n[j]
  new=float(delta@nn-support(nn,test.g[AXES[0]][aa[j]],r,q['axial'])-support(nn,test.g[AXES[0]][bb[j]],r,q['axial']));derivative=(new-low)/dr
  if derivative<=0:break
  q['minor']=s.p['minor']+(MARGIN*r-low)/derivative+1e-6*r;s=CountChain(q,data)
 return s,dict(seconds=time.perf_counter()-t,history=history)

def count_screen(states):
 t=time.perf_counter();rows=[];winds=[s['H'] for s in states]
 for n in range(2000,3601):
  candidates=[]
  for name,(wa,wb) in [('A',(7,6)),('B',(6,7))]:
   for a in range(1,n//wa):
    rem=n-wa*a
    if rem<=0 or rem%wb:continue
    b=rem//wb
    if not .65<=a/b<=1.55:continue
    dist=min(abs(a-h[0])+abs(b-h[1]) for h in winds)
    candidates.append(dict(family=name,H=[a,b],distance_to_saved_H=dist,saved_witness=[a,b] in winds))
  candidates.sort(key=lambda z:(z['distance_to_saved_H'],abs(z['H'][0]-z['H'][1])))
  rows.append(dict(N=n,nearest_turn=int(np.floor(n/6.5+.5)),neighbor_turns=[int(np.floor(n/6.5+.5))+d for d in [-1,0,1]],algebraic_windings=candidates,complete_252_repeats=n%252==0,stage='algebraic only until physical ledger says otherwise'))
 save(OUT/'count-screen.json.gz',dict(rows=rows,seconds=time.perf_counter()-t,policy='Positive H and broad ratio .65..1.55 are an enumerated diagnostic family, not physical bounds. Every N remains possible outside tested hypotheses. Both reversals share absolute N. A saved H fixes N; no overwritten topology. P252 divisibility is annotated only.'))
 return rows

def registration(s,obs,coords):
 xy=np.array([o['xy'] for o in obs]);ids=[o['id'] for o in obs];refxy=xy[ids.index(REF)];candidates=np.argsort(np.linalg.norm(s.pc-refxy,axis=1))[:12];ab=np.array([coords[o] for o in ids]);seed=np.array([1180<=o['xy'][0]<=1505 and 200<o['xy'][1]<390 for o in obs]);opts=[]
 for name,w in WEIGHTS.items():
  k=ab@w
  for j in candidates:
   addr=int(s.indices[j]);jj=(addr+k-s.indices[0])%s.n;d=np.linalg.norm(s.pc[jj]-xy,axis=1)
   opts.append(dict(family=name,reference_address=addr,seed_center_proxy_rms=float(np.sqrt(np.mean(d[seed]**2))),all_center_proxy_rms=float(np.sqrt(np.mean(d*d))),mapping_indices=jj,k=k))
 opts.sort(key=lambda z:z['seed_center_proxy_rms']);best=opts[0]
 return best,[{k:v for k,v in z.items() if k not in ['mapping_indices','k']} for z in opts[:8]]

def main():
 began=time.perf_counter();g=read(ROOT/'photo2/r328/results/graph.json.gz');states=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'];count_screen(states);coords=canonical(states[0]);obs=[o for o in g['observations'] if o['id'] in coords];data=load()[0]
 pixels={r['id']:np.array(r['pixels_xy']) for r in read(ROOT/'photo2/r324/results/observation-pixels.json')};pixelobs=[o for o in obs if o['id'] in pixels]
 # Coarse whole-range grid + ordinary remembered-period candidates + photowindings + odd controls.
 ns=sorted(set(range(2000,3601,100))|set(range(2016,3601,252))|{2691,2704,2690,2692,2703,2705,2801,2999,3001})
 configs=[(n,h,1.95,.85,0,'curvature-density','coarse') for n in ns for h in [-1,1]]
 configs += [(n,h,1.80,.65,0,'curvature-density','smaller-thinner-control') for n in [2000,2400,2691,2704,2772,3000,3276,3528,3600] for h in [-1,1]]
 configs += [(n,-1,1.95,.85,d,law,'neighbor-W-or-spacing-control') for n in [2016,2520,2691,2704,2772,3000,3528] for d,law in [(-1,'curvature-density'),(1,'curvature-density'),(0,'uniform')]]
 rows=[];cache={};native_counts=set();full_budget=420
 def trial(config):
  n,h,r,a,d,law,kind=config;t=time.perf_counter();p=parameters(n,r,a,h);p['winding']+=d;p['turn']=n/p['winding'];p['packing_spacing']=law;p['minor']=r/np.sin(np.pi/p['turn'])
  s,construction=construct(p,data);record=dict(id=len(rows),N=n,hand=h,radius=r,axial=a,W=p['winding'],spacing=law,kind=kind,construction=construction)
  if s:
   tt=time.perf_counter();cert=contacts(s,seconds=.12);record['contact_seconds']=time.perf_counter()-tt;record['contact']={k:v for k,v in cert.items() if k!='witnesses'};record['parameters']=s.p
   best,opts=registration(s,obs,coords);record['registration_options']=opts;record['selected_registration']={k:v for k,v in best.items() if k not in ['mapping_indices','k']};record['nominal_diameter_px']=2*r*s.scale
   dnear=cKDTree(s.pc).query([o['xy'] for o in obs])[0];record['unassigned_center_proxy_median_px']=float(np.median(dnear));record['unassigned_center_proxy_p95_px']=float(np.percentile(dnear,95));record['topology_count_compatible']=n==abs(int(np.dot(states[0]['H'],WEIGHTS[best['family']])));record['model_closure']=s.closure()
   if cert['certified']:
    # One actual native support pixel per support: sparse optical ownership, no shading.
    one={o['id']:pixels[o['id']][len(pixels[o['id']])//2:len(pixels[o['id']])//2+1] for o in pixelobs};tt=time.perf_counter();rr,frac,nr=support_ledger(s,pixelobs,one);record['sparse_ownership_seconds']=time.perf_counter()-tt
    jj={o['id']:int(j) for o,j in zip(obs,best['mapping_indices'])};assigned=[float(frac[i,jj[o['id']]]) for i,o in enumerate(pixelobs)]
    record['sparse_native']=dict(rays=nr,all_bodies=s.n,owned_by_any_fraction=float(np.mean([x['modal_index'] is not None for x in rr])),assigned_fraction=float(np.mean(assigned)),unknown=sum(x['unknown'] for x in rr),policy='One original support pixel per observation; approximate ownership estimate, no full support or reflection claim.')
    record['sparse_rows']=[dict(z,assigned_index=int(s.indices[jj[z['id']]]),assigned_fraction=assigned[i]) for i,z in enumerate(rr)]
    cache[record['id']]=(s,best,cert)
  record['seconds']=time.perf_counter()-t;rows.append(record);save(OUT/'physical-trials'/f'{record["id"]:03}.json.gz',record)
  print('PHYSICAL',record['id'],n,h,p['winding'],law,record.get('contact',{}).get('classification'),round(record['seconds'],3),flush=True)
  return record
 for config in configs:
  if time.perf_counter()-began>full_budget:break
  trial(config)
 # Refine around best sparse same-seed owner score, plus odd neighbors. No period preference.
 good=[z for z in rows if z.get('sparse_native') and z['kind']=='coarse'];good.sort(key=lambda z:(-z['sparse_native']['assigned_fraction'],z['selected_registration']['seed_center_proxy_rms']))
 refined=[]
 for parent in good[:3]:
  for delta in [-10,-3,-1,1,3,10]:
   n=parent['N']+delta;conf=(n,parent['hand'],parent['radius'],parent['axial'],0,'curvature-density','adaptive-count-neighbor')
   if 2000<=n<=3600 and conf[:6] not in [q[:6] for q in configs] and conf[:6] not in refined and time.perf_counter()-began<full_budget:
    trial(conf);refined.append(conf[:6])
 # Full original-support ownership and native local reflection evaluation for selected certified cases.
 good=[z for z in rows if z.get('sparse_native')];good.sort(key=lambda z:(-z['sparse_native']['assigned_fraction'],z['selected_registration']['seed_center_proxy_rms']))
 selected=[]
 for wanted in [good[0]['id'] if good else -1]+[next((z['id'] for z in good if z['N']==n),-1) for n in [2016,2691,2704,2772,3000,3528]]:
  if wanted>=0 and wanted not in selected:selected.append(wanted)
 reflections=read(ROOT/'photo2/r324/results/fit-evidence.json')['reflections'];full=[]
 for rid in selected:
  if time.perf_counter()-began>full_budget+120:break
  s,best,cert=cache[rid];t=time.perf_counter();rr,frac,nr=support_ledger(s,pixelobs,pixels);jj={o['id']:int(j) for o,j in zip(obs,best['mapping_indices'])};mapping={o:int(s.indices[j]) for o,j in jj.items()}
  rec=dict(trial=rid,N=s.n,reference=REF,registration=rows[rid]['selected_registration'],full_support_rays=nr,all_bodies=s.n,rows=[dict(z,assigned_index=mapping[z['id']],assigned_fraction=float(frac[i,jj[z['id']]])) for i,z in enumerate(rr)],support_seconds=time.perf_counter()-t)
  local=[o for o in obs if 1180<=o['xy'][0]<=1505 and 200<o['xy'][1]<390];targets=sorted(set(mapping[o['id']] for o in local));refs=[r for r in reflections if r['observation'] in {o['id'] for o in local}]
  result,raster=optical(s,targets,refs,mapping,'R329 local R161-region native reflection; all bodies retained',certificate=cert,grouped=True);rec['native']=result;rec['seconds']=time.perf_counter()-t
  save(OUT/'native-physical'/f'trial-{rid:03}.json.gz',rec);full.append(dict(trial=rid,N=s.n,seconds=rec['seconds'],support_rays=nr,reflection_targets=len(targets),reflection_emax=result.get('emax_px'),missing=result.get('missing')));native_counts.add(s.n)
 summary=[{k:v for k,v in z.items() if k not in ['sparse_rows','parameters']} for z in rows]
 save(OUT/'physical-summary.json',dict(trials=summary,full_native=full,seconds=time.perf_counter()-began,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,counts_constructed=sorted({z['N'] for z in rows}),counts_sparse_native=sorted({z['N'] for z in rows if 'sparse_native' in z}),counts_full_support_and_local_reflection=sorted(native_counts),registration_policy='Same photographic reference and same 12 nearest-address candidates; choose center-distance proxy on fixed R161-region supports. No per-count camera/shape fit. This is conditional registration, not bead-center measurements.',limitation='Count-incompatible photo maps are one-circuit diagnostic extrapolations with explicit closure discrepancy; never claimed valid topology. Full-native means full support pixels plus local reflection targets, not a whole-photo shaded raster. Frozen R321 law is only one tested construction; uniform spacing and neighboring W controls retained.'))
 print('PHYSICAL DONE',len(rows),len(full),time.perf_counter()-began,flush=True)
if __name__=='__main__':main()
