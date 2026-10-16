"""Checkpointed, physically gated hierarchy with measured-response joint moves."""
from copy import deepcopy
from pathlib import Path
import signal, time, traceback
import numpy as np
from photo2.r297.common import ROOT, read, save, sha, digest, utc, environment
from photo2.r297.geometry import reference, R
from photo2.r298.geometry import Chain as Historical
from .geometry import Chain, canonical, valid, contact, FIELD
from .evidence import load, freeze
from .objective import Objective, vector

STEPS=dict(scale=.10,axial=.035,minor=.08,elevation=2.,roll=3.,perspective=.00005,
           phase=.09,s0=1.2,tilt=1.5,light_az=5.,light_el=3.,turn=.0015,roughness=.7)
GROUPS={'dimensions':['scale','axial','minor','elevation','roll','perspective'],
        'phase-light':['phase','s0','tilt','light_az','light_el','turn','roughness']}

def fingerprints():
    paths=[]
    for name in ['r306','r299','r298','r297','r296','r295','r293','r282','r280','r279']:
        paths += [p for p in (ROOT/'photo2'/name).glob('*.py') if name!='r306' or p.name in ('geometry.py','evidence.py','objective.py','search.py','__init__.py')]
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}

def starts(data):
    out=[]
    for ident in [767,694,121,631]:
        p=read(ROOT/f'photo2/r297/results/pilot/exports/model-{ident}.json.gz')['parameters']
        out.append(dict(parameters=canonical(p),origin=f'R297 {ident}; bounded fields, new arclength axis'))
    hist=read(ROOT/'photo2/r298/results/refinement-history.json.gz'); selection=read(ROOT/'photo2/r298/results/selection.json')
    for ident in selection['families']:
        out.append(dict(parameters=canonical(hist[ident]['parameters']),origin=f'R298 {ident}; bounded fields, new arclength axis'))
    # R303/R305 shared shapes/cameras and single S1 registration, without its splice.
    from photo2.r305.model import source
    from photo2.r303.core import Scene
    for name in ['primary','hand-minus','calibrated']:
        row,s=source(name);local=Scene(row['parameters'],s,row['hand'],row['mode'])
        lp=local.p;base=deepcopy(out[4]['parameters']);base.update(hand=row['hand'],axial=lp['axial']/.7,
            minor=lp['minor']*R,scale=lp['scale']/R,elevation=lp['elevation'],roll=lp['roll'],tilt=lp['tilt'],
            phase=lp['phase'],light_az=lp['light_az'],light_el=lp['light_el'],perspective=0.,
            local_phase=[0.]*FIELD,local_spacing=[0.]*FIELD,axis_nodes=[0.]*FIELD,s0=0.)
        provisional=Chain(canonical(base),data)
        count=int(round(provisional.length/(lp['pitch']*R)))
        count=int(np.clip(count,2000,3100))
        # Transport the local S1 phase to the one global bead-zero gauge.
        origin=float(reference().project([local.offset])['arc'][0]);u0=float(provisional.inverse(provisional.a0))
        grid=np.linspace(0,reference().length,16385);speed=np.linalg.norm(provisional.spline(grid,1),axis=1)
        from scipy.integrate import cumulative_simpson
        lengths=cumulative_simpson(speed,x=grid,initial=0);sorigin=float(np.interp(origin,grid,lengths))
        ds=(sorigin-provisional.a0+provisional.length/2)%provisional.length-provisional.length/2
        for topology in ['open','closed']:
            p=canonical(dict(base,count=count,topology=topology,turn=lp['turn']))
            turns=p['winding']/count if topology=='closed' else 1/p['turn']
            p['phase']=float((lp['phase']-row['hand']*2*np.pi*(ds/provisional.length*count)*turns+np.pi)%(2*np.pi)-np.pi)
            out.append(dict(parameters=p,origin=f'R303/R305 {name}; shared shape/camera, phase transported from S1, literal rounded-annulus shape'))
    for hand in [-1,1]:
        base=next(x['parameters'] for x in out[4:] if x['parameters']['hand']==hand)
        for count in [2002,2204,2405,2607,2808,3010]:
            for topology in ['closed','open']:
                p=canonical(dict(deepcopy(base),count=count,topology=topology,local_phase=[0.]*FIELD,local_spacing=[0.]*FIELD))
                out.append(dict(parameters=p,origin=f'count-grid {count} hand {hand} {topology}'))
    return out

def merit(r): return r['train']['loss']

def select(rows,capacity=12):
    rows=sorted(rows,key=lambda r:(merit(r),r['id']));out=[];families=set()
    for r in rows:
        p=r['parameters'];family=(p['hand'],p['topology'])
        if family not in families:out.append(r);families.add(family)
    for r in rows:
        if any(q['id']==r['id'] for q in out):continue
        p=r['parameters']
        if all(abs(p['count']-q['parameters']['count'])>=6 or abs(p['phase']-q['parameters']['phase'])>.08 or
               abs(p['axial']-q['parameters']['axial'])>.02 or np.linalg.norm(np.array(p['axis_nodes'])-q['parameters']['axis_nodes'])>1.5 or
               np.linalg.norm(np.array(p['local_phase'])-q['parameters']['local_phase'])>.10 for q in out):out.append(r)
        if len(out)>=capacity:break
    return sorted(out,key=merit)

class Runner:
    def __init__(self,out,seconds=3600,seed=306,resume=False,max_evaluations=100000,initialize_from=None):
        self.out=Path(out);self.stop=False;self.seconds=seconds;self.max_evaluations=max_evaluations
        if resume:
            self.state=read(self.out/'checkpoint.json')
            if self.state.get('sealed'):raise ValueError('Sealed run cannot resume after comparison exposure')
            if self.state['sources']!=fingerprints():raise ValueError('Scientific source changed since checkpoint')
            if self.state['environment']!=environment():raise ValueError('Numerical environment changed')
            data,m,obs=load()
            if any(sha(ROOT/p)!=h for p,h in self.state['evidence'].items()):raise ValueError('Evidence changed')
        else:
            if (self.out/'checkpoint.json').exists():raise ValueError('Existing output: use --resume or a new directory')
            data,m,obs,hashes=freeze(self.out)
            self.state=dict(schema=306,created=utc(),sources=fingerprints(),environment=environment(),evidence=hashes,
                seed=seed,rng=np.random.default_rng(seed).bit_generator.state,starts=starts(data),next_id=0,pool=[],pending=None,
                elapsed_seconds=0.,sealed=False,history=[],last_improvement=0,step_scale=1.,sensitivity=[],sensitivities=[],sensitivity_cycle=-1,
                count_range=[1800,3200],seen={},budget_seconds=seconds,stop_reason=None)
            if initialize_from is not None:
                source=Path(initialize_from);prior=read(source/'checkpoint.json');warm=[]
                for i in prior['pool']:
                    path=source/'candidates'/f'{i:06d}.json.gz';row=read(path)
                    warm.append(dict(parameters=row['parameters'],origin=f'Checkpoint warm start {source.name}/{i}; reevaluated on current objective',source_sha256=sha(path)))
                self.state['starts']=warm+self.state['starts'];self.state['initialized_from']=dict(path=str(source),checkpoint_sha256=sha(source/'checkpoint.json'),previously_sealed=prior['sealed'])
        self.data=data;self.m=m;self.obs=obs;self.objective=Objective(data,m,obs)
        self.pool=[read(self.path(i)) for i in self.state['pool']]
        self.started=time.monotonic();self.base_elapsed=self.state['elapsed_seconds']

    def path(self,i):return self.out/'candidates'/f'{i:06d}.json.gz'
    def checkpoint(self):
        self.state['elapsed_seconds']=self.base_elapsed+time.monotonic()-self.started
        self.state['budget_seconds']=self.seconds;save(self.out/'checkpoint.json',self.state)
    def interrupt(self,*args):self.stop=True

    def propose(self):
        st=self.state;n=st['next_id'];rng=np.random.default_rng();rng.bit_generator.state=st['rng']
        if n<len(st['starts']):return dict(**deepcopy(st['starts'][n]),stage='initialization',parent=None,operation='global coherent start')
        age=n-len(st['starts']);cycle=age//240
        if not self.pool:raise RuntimeError('No feasible initialization')
        parent=self.pool[0] if age%4!=3 else self.pool[int(rng.integers(len(self.pool)))];p=deepcopy(parent['parameters'])
        stage='global';op='';scale=st['step_scale'];extra={}
        if age%240 < 2*len(STEPS):
            # Fixed incumbent for a complete two-sided block, preserving derivatives.
            if st['sensitivity_cycle']!=cycle:
                st['sensitivity_cycle']=cycle;st['sensitivity_parent']=parent['id'];st['sensitivity']=[]
            parent=read(self.path(st['sensitivity_parent']));p=deepcopy(parent['parameters'])
            j=(age%240)//2;key=list(STEPS)[j];sign=-1 if age%2==0 else 1
            p[key]+=sign*STEPS[key];stage='sensitivity';op=f'{key} {sign:+d}'
            extra=dict(sensitivity_key=key,sensitivity_sign=sign,sensitivity_cycle=cycle)
        else:
            slot=age%80
            if slot<24:
                group='dimensions' if cycle==0 and slot<16 else ['dimensions','phase-light'][age%2]
                key=GROUPS[group][int(rng.integers(len(GROUPS[group])))];response=st.get('response_scale',{}).get(key,1.)
                p[key]+=float(rng.choice([-1,1]))*STEPS[key]*scale*response;op=key;stage=group
                if age%6==0 and st.get('coupled'):
                    direction=st['coupled'][int(rng.integers(len(st['coupled'])))];sgn=float(rng.choice([-1,1]))
                    for k,v in zip(STEPS,direction):p[k]+=sgn*STEPS[k]*float(v)*scale
                    op+=' + measured singular direction'
            elif slot<44:
                stage='coarse-axis';freq=1+int(rng.integers(4));phase=float(rng.uniform(0,2*np.pi))
                p['axis_nodes']=(np.array(p['axis_nodes'])+scale*1.5*np.cos(2*np.pi*freq*np.arange(FIELD)/FIELD+phase)).tolist();op=f'global axis harmonic {freq}'
            elif slot<72:
                stage='coupled-regional';rows=sorted([s for s in parent['train']['sections'] if s['n']],key=lambda s:-s.get('priority',1-s['containment']))
                region=rows[int(rng.integers(min(10,len(rows))))]['section']
                evidence=[r for r in self.objective.photo.rows if int(r['station']/self.data['length']*32)%32==region]
                scene=Chain(p,self.data);point=np.mean([r['point'] for r in evidence],axis=0)
                owner=int(scene.tree.query(point)[1]);k=int(np.rint((scene.indices[owner]/scene.n+.5)%1*FIELD))%FIELD
                diagnostic=next(r for r in rows if r['section']==region)
                key=['local_phase','local_spacing','axis_nodes'][(slot+cycle)%3]
                if slot%4==0 and diagnostic.get('reflection_n',0)>=3:
                    key='axis_nodes' if abs(diagnostic['normal_mean'])>abs(diagnostic['tangent_mean']) else 'local_phase'
                amount={'local_phase':.07,'local_spacing':.002,'axis_nodes':1.5}[key]*scale*float(rng.choice([-1,1]))
                if key=='axis_nodes':k=int(np.rint(reference().project([point])['arc'][0]/reference().length*FIELD))%FIELD
                for offset,w in [(-1,.35),(0,1.),(1,.35)]:p[key][(k+offset)%FIELD]+=amount*w
                if key=='local_spacing':
                    p[key]=(np.array(p[key])-np.mean(p[key])).tolist()
                op=f'{key}[{k}] informative section {region}'
            else:
                stage='discrete-reconcile'
                choice=int(rng.integers(6))
                if choice<3:
                    delta=int(rng.choice([-26,-13,-6,-1,1,6,13,26]));p['count']+=delta;p['winding']=round(p['count']/6.5)
                    p['turn']=float(np.clip(p['turn'],6.5*p['count']/(p['count']+6.5),6.5*p['count']/(p['count']-6.5)));op=f'count {delta:+d}'
                elif choice==3:
                    key=['axis_nodes','local_phase','local_spacing'][int(rng.integers(3))];v=np.array(p[key]);p[key]=(v+.2*((np.roll(v,1)+np.roll(v,-1))/2-v)).tolist();op='smooth '+key
                elif choice==4:
                    p['phase']+=float(rng.uniform(-.4,.4));op='phase basin restart'
                else:
                    if p['topology']=='open':p['seam_fraction']+=float(rng.choice([-.04,.04]));p['gap_steps']+=float(rng.choice([-.25,.25]));op='open cut and gap'
                    else:p['winding']+=int(rng.choice([-1,1]));op='closure winding'
        p['phase']=float((p['phase']+np.pi)%(2*np.pi)-np.pi);st['rng']=rng.bit_generator.state
        return dict(parameters=p,origin='automatic sensitivity-guided hierarchy',parent=parent['id'],stage=stage,operation=op,**extra)

    def evaluate(self,trial,i):
        row=dict(id=i,**trial);t=time.monotonic();p=row['parameters'];key=digest(p)
        if key in self.state['seen']:row.update(status='duplicate',duplicate_of=self.state['seen'][key])
        elif not valid(p,self.state['count_range']):row.update(status='bounds-rejected')
        else:
            try:
                scene=Chain(p,self.data)
                cert=scene.certify(iterations=65,witnesses=True)
                if not cert['certified']:
                    # Actual solid samples distinguish witnessed penetration from
                    # a failed separating-plane certificate. Both are rejected.
                    cert['penetration_checks']=scene.penetration(cert)
                    cert['state']='demonstrated-interpenetration' if any(q['penetrating'] for q in cert['penetration_checks']) else 'unresolved'
                    row.update(status='physical-rejected',contact=cert,closure=scene.closure())
                else:
                    row['contact']={k:v for k,v in cert.items() if k!='witnesses'};row['closure']=scene.closure()
                    coarse=self.objective.assess(scene,reflections=False);row['coarse']=coarse
                    parent=next((r for r in self.pool if r['id']==row['parent']),None)
                    if row['stage'] not in ('initialization','sensitivity') and parent and coarse['loss']>parent['coarse']['loss']+.25 and i%8:
                        row['status']='structure-screened'
                    else:
                        from .objective import predict,match
                        pred,meta=predict(scene,3.,self.objective.obs)
                        train=deepcopy(coarse);train['reflection']=match(self.objective.obs,pred);train['reflection_numerics']=meta
                        for region in train['sections']:
                            rr=[r for r in train['reflection']['records'] if r['section']==region['section'] and r['error_px'] is not None]
                            region['reflection_n']=len(rr)
                            region['reflection_rms']=float(np.sqrt(np.mean([r['error_px']**2 for r in rr]))) if rr else None
                            region['tangent_mean']=float(np.mean([r['tangent_px'] for r in rr])) if rr else 0.
                            region['normal_mean']=float(np.mean([r['normal_px'] for r in rr])) if rr else 0.
                            region['priority']=2*(1-(region['containment'] if region['containment'] is not None else 1.))+(region['reflection_rms'] or 0)/24*(1 if len(rr)>=3 else .25)
                        train['loss']+=.35*train['reflection']['loss'];row.update(status='eligible',train=train,predictions=pred)
            except (ValueError,ArithmeticError,FloatingPointError) as e:row.update(status='numerical-rejected',reason=repr(e))
        row['seconds']=time.monotonic()-t
        return row

    def incorporate(self,row):
        st=self.state;n=row['id'];st['seen'][digest(row['parameters'])]=n
        old=merit(self.pool[0]) if self.pool else np.inf
        if row['status']=='eligible':self.pool=select(self.pool+[row])
        if self.pool and merit(self.pool[0])<old-1e-4:st['last_improvement']=n
        if row['stage']=='sensitivity':
            st['sensitivity'].append(n)
            if len(st['sensitivity'])==2*len(STEPS):self.analyze_sensitivity()
        st['history'].append(dict(id=n,status=row['status'],stage=row['stage'],seconds=row['seconds'],loss=row.get('train',{}).get('loss'),
            best_id=self.pool[0]['id'] if self.pool else None,best=merit(self.pool[0]) if self.pool else None))
        st['pool']=[r['id'] for r in self.pool];st['next_id']=n+1;st['pending']=None
        if n>len(st['starts']) and (n-len(st['starts']))%160==0:
            st['step_scale']=max(.2,st['step_scale']*.7) if n-st['last_improvement']>120 else min(1.,st['step_scale']*1.1)

    def analyze_sensitivity(self):
        st=self.state;rows=[read(self.path(i)) for i in st['sensitivity']];columns=[];keys=[];switches={}
        for key in STEPS:
            rr=[r for r in rows if r['sensitivity_key']==key]
            if len(rr)!=2 or any(r['status']!='eligible' for r in rr):continue
            rr.sort(key=lambda r:r['sensitivity_sign']);col=(vector(rr[1]['train'])-vector(rr[0]['train']))/2
            columns.append(col);keys.append(key)
            a={r['id']:r['index'] for r in rr[0]['train']['reflection']['records']};b={r['id']:r['index'] for r in rr[1]['train']['reflection']['records']}
            switches[key]=sum(a[k]!=b[k] for k in a)
        result=dict(cycle=st['sensitivity_cycle'],parent=st['sensitivity_parent'],keys=keys,probes=st['sensitivity'],assignment_switches=switches,
            meaning='Grouped structural response at declared perturbation scales. Not statistical rank or confidence intervals; held-out features excluded. Reflection owner switches recorded separately.')
        if columns:
            matrix=np.column_stack(columns);u,s,v=np.linalg.svd(matrix,full_matrices=False)
            result.update(matrix=matrix.tolist(),singular_values=s.tolist(),responses=np.linalg.norm(matrix,axis=0).tolist())
            st['response_scale']={k:float(np.clip(1/max(.1,np.linalg.norm(c)),.35,1.5)) for k,c in zip(keys,columns)}
            st['coupled']=[]
            for direction in v[:min(4,len(v))]:
                full=np.zeros(len(STEPS))
                for k,a in zip(keys,direction):full[list(STEPS).index(k)]=a
                st['coupled'].append(full.tolist())
        st['sensitivities'].append(result);save(self.out/f'sensitivity-{st["sensitivity_cycle"]:03d}.json',result)

    def run(self):
        handlers={s:signal.signal(s,self.interrupt) for s in (signal.SIGINT,signal.SIGTERM)}
        self.checkpoint()
        try:
            while True:
                n=self.state['next_id'];elapsed=self.base_elapsed+time.monotonic()-self.started
                if self.stop:reason='signal';break
                if elapsed>=self.seconds:reason='time-budget';break
                if n>=self.max_evaluations:reason='evaluation-budget';break
                # Stagnation requires repeated hierarchy cycles, never a short local fit.
                if n>1200 and n-self.state['last_improvement']>600 and self.state['step_scale']<=.2:reason='demonstrated-search-stall';break
                if self.state['pending'] is None:self.state['pending']=self.propose();self.checkpoint()
                if self.path(n).exists():row=read(self.path(n))
                else:row=self.evaluate(self.state['pending'],n);save(self.path(n),row)
                self.incorporate(row);self.checkpoint()
                best=self.pool[0] if self.pool else None
                print(f'{n:05} {row["stage"]} {row["status"]} {row["seconds"]:.2f}s best='+
                    (f'{merit(best):.5f} id={best["id"]} N={best["parameters"]["count"]} hand={best["parameters"]["hand"]}' if best else 'none'),flush=True)
            self.state['stop_reason']=reason;self.checkpoint();return self.state
        except Exception as e:
            save(self.out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),next_id=self.state['next_id']))
            self.checkpoint();raise
        finally:
            for s,h in handlers.items():signal.signal(s,h)
