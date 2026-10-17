"""Standalone fixed-measurement controls, multibasin search and sealed exports."""
import argparse,time,signal,subprocess,traceback
from copy import deepcopy
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from photo2.r297.common import ROOT,read,save,sha,utc,digest
from photo2.r306.evidence import load
from .objective import Objective,acceptance,dominates
from .geometry import ShapeChain,contacts,paper

OUT=ROOT/'photo2/r314/results';EV=OUT.parent/'evidence'
NAMES=['R306-2405','R312-best','R312-local','R313-focused-3','R313-focused-1','R309-2733']
OLD=ROOT/'photo2/r313/continuation/models'
SCALES=dict(phase=.65,s0=12.,elevation=10.,roll=15.,perspective=.00015,scale=.65,minor=.45,axial=.18,tilt=12.,trajectory_mix=.25,edge=.16,face=.22,hole=.13,rounding=.20,spacing_cos=.004,spacing_sin=.004,phase_cos=.12,phase_sin=.12)
GROUPS=[['phase','s0','elevation','roll'],['minor','axial','tilt','trajectory_mix'],['edge','face','axial','scale'],['phase','s0','minor','scale'],['perspective','elevation','roll','scale'],['spacing_cos','spacing_sin','phase_cos','phase_sin','phase','s0'],['hole','rounding','axial','tilt'],list(SCALES)]
BOUNDS=dict(elevation=(25,88),roll=(-100,100),perspective=(0,.001),scale=(5.5,12),minor=(2.5,7),axial=(.25,1.4),tilt=(-70,70),trajectory_mix=(-.6,1),edge=(.04,.60),face=(.25,1),hole=(.02,.60),rounding=(.25,1),bore=(.02,.30))

def engine():return Objective(dict(np.load(EV/'maps.npz')),read(EV/'freeze.json'))
def make(p,data):return ShapeChain(p,data)

def evaluated(p,data,eng,detail=False,seconds=.25):
    began=time.monotonic();s=make(p,data);cert=contacts(s,seconds=seconds);r=dict(parameters=p,feasible=cert['certified'],classification=cert['classification'],physical=cert)
    tr=None
    if cert['classification']!='demonstrated-interpenetration':
        tr=s.trace(eng.xy);r['development']=eng.measure(tr['owner'],tr['unknown'],s.indices,0,detail)
        if detail:
            r['comparison']=eng.measure(tr['owner'],tr['unknown'],s.indices,1,True);r['buffer']=eng.measure(tr['owner'],tr['unknown'],s.indices,2,True);r['paper']=paper(s)
    r['seconds']=time.monotonic()-began;return r,s,tr

def export(name,row,s,tr):
    r=deepcopy(row);r.update(name=name,positions=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),projected=s.pc.tolist(),frames={k:v.tolist() for k,v in s.g.items()}),cohort=list(range(-100,100)),cohort_positions=int(np.sum((s.indices>=-100)&(s.indices<=99))))
    save(OUT/'models'/f'{name}.json.gz',r)
    if tr is not None:np.savez_compressed(OUT/'models'/f'{name}.npz',owner=tr['owner'],unknown=tr['unknown'])
    return r

def prepare():
    if (OUT/'prepared.json').exists():raise SystemExit('Preparation sealed')
    data,_,_=load();eng=engine();bases=[]
    save(OUT/'start.json',dict(utc=utc(),session_start_utc='2026-10-17T21:09:25Z',search_cutoff_utc='2026-10-17T21:33:25Z',deadline_utc='2026-10-17T21:39:25Z',head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),historical_source='All tracked history protected by original HEAD and git diff; only additive handoffs allowed',evidence_sha256=sha(EV/'maps.npz')))
    for name in NAMES:
        old=read(OLD/f'{name}.json.gz');r,s,tr=evaluated(old['parameters'],data,eng,True,1.)
        assert r['feasible'],name
        np.testing.assert_allclose(s.centers,old['positions']['centers'],atol=1e-12,rtol=0)
        prior=np.load(OLD/f'{name}.npz');np.testing.assert_array_equal(tr['owner'],prior['owner']);np.testing.assert_array_equal(tr['unknown'],prior['unknown'])
        r['source']=str((OLD/f'{name}.json.gz').relative_to(ROOT));bases.append(export(name,r,s,tr));print('BASE',name,r['development']['vector'],flush=True)
    base=bases[0];a=np.load(OUT/'models/R306-2405.npz');own=a['owner'].reshape(eng.shape);un=a['unknown'].reshape(eng.shape);idx=np.array(base['positions']['indices']);controls=[]
    def control(name,oo,uu=un,ii=idx):
        r=eng.measure(oo,uu,ii,0,True);acc=acceptance(r,base['development']);controls.append(dict(name=name,metrics=r,acceptance=acc));print('CONTROL',name,acc,flush=True)
    control('unchanged',own)
    control('pure_index_permutation',np.where(own>=0,len(idx)-1-own,-1),un,idx[::-1])
    for width in [3,7]:
        dd,near=ndi.distance_transform_edt(own<0,return_indices=True);oo=own.copy();sel=(own<0)&(dd<=width);oo[sel]=own[tuple(near[:,sel])];control(f'expansion_{width}px',oo)
    control('all_owners_merged',np.where(own>=0,0,-1))
    control('adjacent_owner_pairs_merged',np.where(own>=0,own//2*2,-1))
    for dx,dy in [(12,0),(-12,0),(0,12),(0,-12)]:control(f'displaced_{dx}_{dy}',ndi.shift(own,(dy,dx),order=0,cval=-1),ndi.shift(un,(dy,dx),order=0,cval=False))
    for key,value in [('phase',base['parameters']['phase']+1.2),('scale',base['parameters']['scale']*1.18),('scale',base['parameters']['scale']*.82)]:
        p=dict(base['parameters']);p[key]=value;r,s,tr=evaluated(p,data,eng,True,.5)
        # Deliberate controls still measured if physical invalid: rendering is diagnostic only.
        if tr is None:tr=s.trace(eng.xy)
        control(f'physical_{key}_{value:.4f}',tr['owner'],tr['unknown'],s.indices);controls[-1]['physical']=r['physical'];controls[-1]['parameters']=p
    assert controls[0]['metrics']['vector']==controls[1]['metrics']['vector']
    for c in controls[2:]:assert not c['acceptance']['passed'],c['name']
    save(OUT/'controls.json',dict(passed=True,cases=controls))
    save(OUT/'prepared.json',dict(utc=utc(),names=NAMES,controls_pass=True,sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r314').glob('*.py'))},evidence_sha256=sha(EV/'maps.npz')))

def merit(r):
    v=r['development']['vector'];values=[v[k]/t for k,t in zip(v,[5.,.5,20.,3.,10.,3.])]
    values.append(max((1-c['modal_fraction'])/.2 for c in r['development']['cores']))
    return tuple(sorted(values,reverse=True))

def perturb(parent,base,rng,scale,group):
    p=deepcopy(parent)
    for key in group:
        z=float(rng.normal())*scale*SCALES[key]
        if key.startswith('spacing_') or key.startswith('phase_'):
            field='local_spacing' if key.startswith('spacing_') else 'local_phase';n=len(p[field]);phase=np.arange(n)/n*2*np.pi;wave=np.sin(phase) if key.endswith('sin') else np.cos(phase);p[field]=(np.array(p[field])+z*wave).tolist()
        else:p[key]=float(p.get(key,dict(edge=.344,face=.8,hole=.14,rounding=.8).get(key,0))+z)
    p['phase']=float((p['phase']+np.pi)%(2*np.pi)-np.pi)
    return p

def fit(seconds):
    if (OUT/'selection.json').exists():raise SystemExit('Search already sealed')
    prep=read(OUT/'prepared.json');assert prep['controls_pass'];assert sha(EV/'maps.npz')==prep['evidence_sha256']
    data,_,_=load();eng=engine();bases=[read(OUT/'models'/f'{n}.json.gz') for n in NAMES];baseline=bases[0]['development'];sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r314').glob('*')) if p.is_file()};save(OUT/'search-plan.json',dict(utc=utc(),seconds=seconds,seed=31417,basins=NAMES,groups=GROUPS,scales=SCALES,bounds=BOUNDS,sources=sources,evidence_sha256=sha(EV/'maps.npz'),strategy='First half broad alternating legacy/new exterior coupled groups across six basins; second half population differential/coupled refinement of multiple nondominated feasible candidates. Maximum normalized geometric violations, Pareto archive, separate immutable conjunctive acceptance. No highlight fitting.'))
    began=time.monotonic();deadline=began+seconds;stopped=[False];signal.signal(signal.SIGTERM,lambda *_:stopped.__setitem__(0,True));signal.signal(signal.SIGINT,lambda *_:stopped.__setitem__(0,True));rng=np.random.default_rng(31417);count=0;cache=set();pop=[[] for _ in bases];pareto=[];accepted=[]
    for i,b in enumerate(bases):
        z=deepcopy(b);z.update(id=-i-1,start=NAMES[i]);pop[i].append(z)
    while time.monotonic()<deadline and not stopped[0]:
        i=count%len(bases);base=bases[i];fraction=(time.monotonic()-began)/seconds;group=GROUPS[int(rng.integers(len(GROUPS)))];phase='broad' if fraction<.5 else 'refine'
        if phase=='broad':
            parent=base['parameters'];factor=[.25,.55,1.,1.5][(count//len(bases))%4]
        else:
            pool=sorted(pop[i],key=merit)[:12];parent=pool[int(rng.integers(len(pool)))]['parameters'];factor=[.08,.18,.35,.6][int(rng.integers(4))]
        p=perturb(parent,base['parameters'],rng,factor,group)
        if phase=='broad' and (count//len(bases))%2==0:
            p.update(exterior=True,bore=.14);p.setdefault('edge',(1-p.get('hole',.14))/2*p.get('rounding',.8));p.setdefault('face',p.get('rounding',.8))
        if phase=='refine' and len(pop[i])>=3 and count%4==0:
            choices=rng.choice(len(pop[i]),2,replace=False);a,b=[pop[i][j]['parameters'] for j in choices]
            for key in group:
                if key in a and key in b and isinstance(a[key],(int,float)) and key not in ['exterior']:p[key]=float(p.get(key,0)+.4*(a[key]-b[key]))
        key=digest(p)
        if key in cache:continue
        cache.add(key);tick=time.monotonic();reason=next((k for k,(lo,hi) in BOUNDS.items() if k in p and not lo<=p[k]<=hi),None)
        row=dict(id=count,start=NAMES[i],phase=phase,group=group,parameters=p,elapsed=tick-began)
        if reason:row.update(feasible=False,classification='numerical-bound',reason=reason)
        else:
            try:
                r,s,tr=evaluated(p,data,eng,False,.25);row.update(r);row['physical'].pop('witnesses',None)
                if 'development' in r:row['acceptance']=acceptance(r['development'],baseline)
            except ValueError as ex:row.update(feasible=False,classification='numerical-bound',reason=str(ex))
        row['seconds']=time.monotonic()-tick;save(OUT/'trials'/f'{count:05d}.json.gz',row)
        if row['feasible']:
            pop[i].append(row);pop[i]=sorted(pop[i],key=merit)[:20]
            if not any(dominates(x['development'],row['development']) for x in pareto):
                pareto=[x for x in pareto if not dominates(row['development'],x['development'])]+[row]
            if row['acceptance']['passed']:accepted.append(count)
            if pop[i][0]['id']==count:print('BEST',count,NAMES[i],phase,merit(row),row['acceptance']['passed'],'elapsed',round(time.monotonic()-began,1),flush=True)
        count+=1
        if count%25==0:save(OUT/'checkpoint.json',dict(utc=utc(),elapsed=time.monotonic()-began,evaluations=count,best=[dict(id=p[0]['id'],start=NAMES[j],parameters=p[0]['parameters']) for j,p in enumerate(pop)],pareto=[x['id'] for x in pareto],accepted=accepted))
    best=[dict(id=p[0]['id'],start=NAMES[j],parameters=p[0]['parameters'],merit=merit(p[0])) for j,p in enumerate(pop)]
    save(OUT/'selection.json',dict(utc=utc(),seconds=time.monotonic()-began,evaluations=count,best=best,pareto=[x['id'] for x in pareto],accepted=accepted,sealed=True,stopped=stopped[0],sources=sources))
    print('SEALED',count,'accepted',accepted,'seconds',time.monotonic()-began,flush=True)

def finalize():
    data,_,_=load();eng=engine();sel=read(OUT/'selection.json');assert sel['sealed'];baseline=read(OUT/'models/R306-2405.json.gz');models=[]
    for i,b in enumerate(sel['best']):
        r,s,tr=evaluated(b['parameters'],data,eng,True,3.);assert r['feasible'];r.update(source_trial=b['id'],parent=b['start']);r['acceptance']={k:acceptance(r[k],baseline[k]) for k in ['development','comparison']};r['ready']=all(not r[k]['absolute_failures'] and r['acceptance'][k]['passed'] for k in ['development','comparison']);models.append(export(f'R314-basin-{i+1}',r,s,tr));print('EXPORT',i+1,r['ready'],r['development']['vector'],flush=True)
    summary=[]
    for path in sorted((OUT/'models').glob('*.json.gz')):
        r=read(path)
        for k in ['development','comparison','buffer']:summary.append(dict(name=r['name'],split=k,vector=r[k]['vector'],absolute_failures=r[k]['absolute_failures'],acceptance=acceptance(r[k],baseline[k]),core_coverage=[dict(id=c['id'],index=c['index'],fraction=c['modal_fraction']) for c in r[k]['cores']]))
    save(OUT/'summary.json',dict(rows=summary,geometry_ready=any(r['ready'] for r in models),highlight_optimization=False,reason='No optical fitting without simultaneous geometric readiness and established correspondence cohort'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','fit','finalize']);p.add_argument('--seconds',type=float,default=600);a=p.parse_args()
    {'prepare':prepare,'fit':lambda:fit(a.seconds),'finalize':finalize}[a.action]()
