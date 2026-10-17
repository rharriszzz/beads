"""Bounded staged joint search using exact inherited geometry and photographic evidence."""
import time,subprocess,json
from copy import deepcopy
from collections import Counter
import numpy as np
from scipy.stats import qmc
from photo2.r297.common import ROOT,read,save,sha,utc,digest
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.geometry import contacts
from photo2.r314.diagnostics import EARLY
from photo2.r315.model import refined_trace,bump
from photo2.r315.diagnose import brackets
from photo2.r316.model import Chain
from photo2.r316.renderer import RayLayers
from photo2.r316.experiment import early
OUT=ROOT/'photo2/r317/results'
SPLITS=['development','comparison','buffer']
NEXT='R282-1459-0316';POS='R282-1537-0308'
PATHS={'R306':'r316/results/R306-model.json.gz','focused3':'r316/results/focused3-model.json.gz','narrow':'r316/results/narrow-model.json.gz','R316':'r316/results/joint-recovery-model.json.gz'}

def check(p):
    k=np.linspace(-110,110,1761);eps=.001
    a=sum(v*bump(k,c,p.get('orientation_halfwidth',18)) for c,v in zip(p.get('compact_centers',[-13,0,13]),p.get('compact_tilt',[0,0,0])))
    if np.max(abs(np.diff(a)/np.diff(k)))>3:raise ValueError('orientation smoothness 3 deg/address')
    if not (.75<=p['axial']<=1.15 and -15<=p['tilt']<=25):raise ValueError('shared axial/tilt exploration bounds')

def evaluate(p,data,e,cache=None):
    check(p);t=time.monotonic();s=Chain(p,data);cert=contacts(s,seconds=.2);r=dict(parameters=p,feasible=cert['certified'],classification=cert['classification'],physical=cert)
    if not r['feasible']:return r,s,None
    tr=cache.trace(s,e.xy) if cache is not None else refined_trace(s,e.xy)
    if tr['unknown'].any():r.update(feasible=False,classification='unresolved-rays');return r,s,tr
    if 'stats' in tr:r['cache']=tr['stats']
    for i,k in enumerate(SPLITS):
        z=e.measure(tr['owner'],tr['unknown'],s.indices,i,True)
        r[k]=dict(vector=z['vector'],cores=z['cores'])
    bs=brackets(e,tr);r['brackets']={k:dict(count=len(b:=[x for x in bs if x['split']==i]),missing=sum(not x['found'] for x in b),p95=float(np.percentile([x['displacement'] for x in b if x['found']],95)) if b else None,maximum=max([x['displacement'] for x in b if x['found']],default=None)) for i,k in enumerate(SPLITS)}
    # Exact full-scene candidate fractions distinguish -14/-15 even when nonmodal.
    r['early']=[]
    for c in e.doc['regions']:
        if c['id'] not in EARLY:continue
        ix=np.flatnonzero(e.m['core'].ravel()==c['label']);ids,ns=np.unique(tr['owner'][ix],return_counts=True)
        r['early'].append(dict(id=c['id'],visible={str(int(s.indices[j])):float(n/len(ix)) for j,n in zip(ids,ns) if j>=0},best_visible=max([float(n/len(ix)) for j,n in zip(ids,ns) if j>=0],default=0)))
    r['compact_rates']=s.compact_rate_bounds;r['evaluation_seconds']=time.monotonic()-t
    return r,s,tr

def vals(r,h='C'):
    cs={z['id']:z for z in r['early']};a=np.array([cs[k]['best_visible'] for k in EARLY])
    if h in ['A','B']:a[EARLY.index(NEXT)]=cs[NEXT]['visible'].get('-14' if h=='A' else '-15',0.)
    return a

def merit(r,h='C',strict=False):
    if not r['feasible']:return (1e6,1e6)
    a=vals(r,h);v=r['development']['vector'];w=r['comparison']['vector']
    # Joint max violation followed by average violations. Separate final gates and Pareto export.
    z=list(np.maximum(0,.90-a)/.15)
    z.extend([max(0,v['paper']-.35)/.35,max(0,w['paper']-1.0)/.6,max(0,v['omission']-9)/3,max(0,w['omission']-9.4)/3,max(0,v['worst']-13.42)/2,max(0,w['worst']-10.77)/2,max(0,v['seam']-33.34)/15,max(0,w['seam']-26.87)/15])
    for k,target in [('development',9),('comparison',14.3)]:z.append(max(0,r['brackets'][k]['p95']-target)/3)
    return (max(z),float(np.mean(np.square(z))))

def vector(r):
    return np.r_[1-vals(r),*[r[k]['vector'][x] for k in SPLITS[:2] for x in ['omission','paper','seam','worst']],*[r['brackets'][k]['p95'] for k in SPLITS[:2]]]

def main():
    began=time.monotonic();deadline=time.time()+780 # scientific run <=13min, delivery independently reserved
    data=load()[0];e=engine();rows=[];seen={};cache=RayLayers();rng=np.random.default_rng(317)
    if (OUT/'search.json').exists():raise RuntimeError('sealed search exists')
    save(OUT/'start.json',dict(start_utc='2026-10-17T23:21:22Z',deadline_utc='2026-10-17T23:51:22Z',search_started=utc(),head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),evidence_sha=sha(ROOT/'photo2/r314/evidence/maps.npz')))
    def trial(p,stage,h='C',local=False):
        if time.time()>deadline:raise TimeoutError
        key=digest(p)
        if key in seen:return seen[key]
        t=time.monotonic()
        try:r,s,tr=evaluate(p,data,e,cache if local else None)
        except ValueError as ex:r=dict(parameters=p,feasible=False,classification='exploration-bound',reason=str(ex))
        r.update(id=len(rows),stage=stage,hypothesis=h,seconds=time.monotonic()-t)
        if 'physical' in r:r['physical'].pop('witnesses',None)
        rows.append(r);seen[key]=r;save(OUT/'trials'/f'{r["id"]:05d}.json.gz',r)
        if len(rows)%10==0 or stage=='baseline':print(r['id'],stage,h,r['classification'],merit(r,h),np.round(vals(r,h),3).tolist() if r['feasible'] else '',flush=True)
        return r
    parents={k:read(ROOT/'photo2'/p)['parameters'] for k,p in PATHS.items()}
    try:
        for k,p in parents.items():trial(p,'baseline')
        base=parents['R316']
        # Sensitivity controls and shared profile alternatives, bore fixed.
        controls=[('axial',.045),('radius',.045),('tilt',4.),('elevation',2.),('rounding',.08)]
        for key,step in controls:
            for sign in [-1,1]:
                p=deepcopy(base);p[key]=p.get(key,.8)+sign*step;trial(p,'A-sensitivity:'+key)
        for edge,face in [(.20,.55),(.344,.8),(.5,1.)]:
            for axial in [.88,.97,1.06]:
                for tilt in [0,8,16]:
                    p=deepcopy(base);p.update(exterior=True,edge=edge,face=face,bore=.14,axial=axial,tilt=tilt);trial(p,'A-profile')
        sob=qmc.Sobol(4,scramble=True,seed=317).random_base2(6)
        for x in sob:
            p=deepcopy(base);p.update(axial=.85+.25*x[0],tilt=-2+20*x[1]);p['radius']*=.96+.08*x[2];p['rounding']=.65+.30*x[3];trial(p,'A-coupled-shape')
        save(OUT/'stage-a.json',dict(trials=len(rows),seconds=time.monotonic()-began))
        # Each correspondence basin has its own start; preserve convex and legacy starts.
        seeds=[]
        for h in ['A','B','C']:
            feasible=[r for r in rows if r['feasible']]
            seeds.append((h,min(feasible,key=lambda r:merit(r,h))))
        convex=[r for r in rows if r['feasible'] and r['parameters'].get('exterior',False)]
        if convex:seeds.append(('C',min(convex,key=merit)))
        seeds.append(('C',next(r for r in rows if digest(r['parameters'])==digest(parents['narrow']))))
        fields=[('compact_phase',i,.07) for i in range(3)]+[('compact_spacing',i,.004) for i in range(3)]+[('compact_tilt',i,4.) for i in range(3)]
        for h,seed in seeds:
            cur=seed;cache=RayLayers()
            for cycle in range(4):
                for field,i,step in fields:
                    choices=[cur]
                    for sign in [-1,1]:
                        p=deepcopy(cur['parameters']);p[field]=list(p.get(field,[0,0,0]));p[field][i]+=sign*step*(.7**cycle);choices.append(trial(p,'B-scaled-coordinate',h,True))
                    cur=min(choices,key=lambda r:merit(r,h))
                for j in range(12):
                    p=deepcopy(cur['parameters'])
                    for field,i,step in fields:
                        p[field]=list(p.get(field,[0,0,0]));p[field][i]+=rng.normal()*step*.6*(.7**cycle)
                    rr=trial(p,'B-coupled-multistart',h,True)
                    if merit(rr,h)<merit(cur,h):cur=rr
            save(OUT/f'basin-{h}-{seed["id"]}.json',dict(seed=seed['id'],best=cur['id'],merit=merit(cur,h)))
        # Additional smooth controls at adjacent minor turns, preserving original fields.
        for h in ['A','B','C']:
            cur=min([r for r in rows if r['feasible']],key=lambda r:merit(r,h));p=deepcopy(cur['parameters']);p['compact_centers']=[-13,0,13,-26,26]
            for field in ['compact_phase','compact_spacing','compact_tilt']:p[field]=list(p.get(field,[0,0,0]))+[0,0]
            cur=trial(p,'B-extended-basis-zero',h,True)
            for cyc in range(2):
                for field,step in [('compact_phase',.08),('compact_spacing',.004),('compact_tilt',4.)]:
                    for i in [3,4]:
                        choices=[cur]
                        for sign in [-1,1]:
                            p=deepcopy(cur['parameters']);p[field][i]+=sign*step;choices.append(trial(p,'B-adjacent-turns',h,True))
                        cur=min(choices,key=lambda r:merit(r,h))
        # Joint refinement retains A/B/C and perturbs shared/profile/registration with local fields.
        for h in ['A','B','C']:
            cur=min([r for r in rows if r['feasible']],key=lambda r:merit(r,h))
            for cycle in range(3):
                for key,step in [('axial',.025),('tilt',2.),('translation_x',1.),('translation_y',1.),('elevation',.7)]:
                    choices=[cur]
                    for sign in [-1,1]:
                        p=deepcopy(cur['parameters'])
                        if key.startswith('translation'):
                            p['translation']=list(p.get('translation',[0,0]));p['translation'][0 if key.endswith('x') else 1]+=sign*step*.6**cycle
                        else:p[key]+=sign*step*.6**cycle
                        choices.append(trial(p,'C-joint-coordinate:'+key,h))
                    cur=min(choices,key=lambda r:merit(r,h))
                for j in range(18):
                    p=deepcopy(cur['parameters']);p['axial']+=rng.normal()*.012;p['tilt']+=rng.normal()*1.5
                    for field,i,step in fields:p[field][i]+=rng.normal()*step*.3
                    rr=trial(p,'C-cross-interaction',h)
                    if merit(rr,h)<merit(cur,h):cur=rr
    except TimeoutError:print('SEARCH TIME CUTOFF',flush=True)
    feasible=[r for r in rows if r['feasible']];vv=np.array([vector(r) for r in feasible]);pareto=[r['id'] for i,r in enumerate(feasible) if not np.any(np.all(vv<=vv[i]+1e-12,axis=1)&np.any(vv<vv[i]-1e-12,axis=1))]
    selected={h:min(feasible,key=lambda r:merit(r,h))['id'] for h in ['A','B','C']}
    save(OUT/'search.json',dict(seconds=time.monotonic()-began,trials=len(rows),classifications=dict(Counter(r['classification'] for r in rows)),stages=dict(Counter(r['stage'] for r in rows)),pareto=pareto,selected=selected,finished=utc(),adopted=False))
    print('DONE',len(rows),selected,flush=True)
if __name__=='__main__':main()
