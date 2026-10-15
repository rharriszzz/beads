"""Deterministic A/B/C/D population search with atomic candidate transactions."""
from copy import deepcopy
import signal
import time
import numpy as np
from .common import *
from .geometry import Chain, contact, full_parameters, plane_reference, valid, PITCH, FIELD_SIZE
from .objective import Objective, compact


def starting_models(data, seed):
    from photo2.r296.search import starting_models as old_starts
    cold,bounds=old_starts(data,seed);models=[]
    for identifier in [188,166,94,112]:
        base=read(ROOT/f'photo2/r296/results/pilot/candidates/{identifier:06d}.json.gz')['parameters']
        models.append(dict(parameters=deepcopy(base),origin=f'R296 retained {identifier}'))
        p=deepcopy(base);p.update(local_metric=1.,local_turn=1.)
        models.append(dict(parameters=p,origin=f'R296 {identifier}, physical local metric'))
    for source,count in [('joint.json',2337),('hand-plus-evaluation.json',2709)]:
        row=read(ROOT/'photo2/r295/results'/source)
        base=row['selected']['parameters'] if 'selected' in row else row['parameters']
        for topo in ['closed','open']:
            for turn in [0.,1.]:
                p=full_parameters(base,count,topo);p.update(local_metric=1.,local_turn=turn)
                identifier={(-1,'closed'):188,(-1,'open'):166,(1,'closed'):94,(1,'open'):112}[base['hand'],topo]
                exterior=read(ROOT/f'photo2/r296/results/pilot/candidates/{identifier:06d}.json.gz')['parameters']
                p['phase']=exterior['phase'];p['local_phase_bias']=base['phase']-exterior['phase']
                for key in ['local_phase','local_spacing','local_bend']:
                    p[key]=deepcopy(exterior[key])
                    if key!='local_spacing':
                        for j,k in enumerate(np.linspace(-count/2,count/2,FIELD_SIZE,endpoint=False)):
                            if -150<k<400:p[key][j]=0.
                models.append(dict(parameters=p,origin='R295 compact local metric with R296 exterior fields; assignments free'))
    for cut in [-.25,-.75]:
        for identifier in [166,112]:
            p=deepcopy(read(ROOT/f'photo2/r296/results/pilot/candidates/{identifier:06d}.json.gz')['parameters'])
            p.update(seam_fraction=cut,gap_steps=2.)
            models.append(dict(parameters=p,origin='Alternative open cut; no artificial edge'))
    models.extend(cold[20:32])
    return models,bounds


def merit(row):
    return .65*row['train']['score']+.35*row['validation']['score']


def select_population(rows, capacity):
    """Keep family representatives, then quantitatively separated parameter basins."""
    rows=sorted(rows,key=lambda r:(-merit(r),r['id']))
    chosen=[];families=set()
    for r in rows:
        p=r['parameters'];key=(p['hand'],p['topology'])
        if key not in families:chosen.append(r);families.add(key)
    for r in rows:
        if r in chosen:continue
        p=r['parameters']
        if all(abs(p['count']-q['parameters']['count'])>=12 or abs(p['phase']-q['parameters']['phase'])>.12 or
               abs(p['elevation']-q['parameters']['elevation'])>2 or abs(p['axial']-q['parameters']['axial'])>.025 or
               abs(p.get('local_metric',0)-q['parameters'].get('local_metric',0))>=.25 or abs(p.get('local_turn',0)-q['parameters'].get('local_turn',0))>=.25 or abs(p.get('seam_fraction',-.5)-q['parameters'].get('seam_fraction',-.5))>=.1 or
               np.linalg.norm(np.array(p['local_phase'])-q['parameters']['local_phase'])>.06 for q in chosen):
            chosen.append(r)
        if len(chosen)>=capacity:break
    return sorted(chosen[:capacity],key=lambda r:(-merit(r),r['id']))


def propose(state, pool, data):
    rng=np.random.default_rng();rng.bit_generator.state=state['rng']
    n=state['next_id'];starts=state['starts']
    if n<len(starts):
        trial=deepcopy(starts[n]);trial.update(stage='A',parent=None,operation='global hypothesis')
    else:
        if not pool:raise RuntimeError('No certified full-chain start. Inspect failed contact records; widen the documented count/shape family.')
        age=n-len(starts);slot=age%64
        stage='B' if slot<32 else 'C' if slot<48 else 'D'
        # Every third proposal explores a retained alternative rather than champion.
        parent=pool[int(rng.integers(len(pool)))] if age%3==2 else max(pool,key=merit)
        p=deepcopy(parent['parameters']);step=state['step_scale'];operation=''
        if stage=='B':
            sections=sorted(parent['train']['sections'],key=lambda r:-r['failure'])
            eligible=[r for r in sections if r['n']]
            section=eligible[(age//2)%min(12,len(eligible))]['section']
            # Map the failed geographic section into this candidate's index field.
            observations=[r for r in data['rows'] if r['split']=='train' and int(r['station']/data['length']*FIELD_SIZE)==section]
            scene=Chain(p,data);near=scene.tree.query([r['point'] for r in observations])[1]
            angle=np.angle(np.mean(np.exp(2j*np.pi*(scene.indices[near]/scene.n+.5))))
            knot=int(np.rint((angle/(2*np.pi)%1)*FIELD_SIZE))%FIELD_SIZE
            key,amount=[('local_phase',.12),('local_spacing',.015),('local_bend',1.5)][(age//2)%3]
            sign=-1 if age%2==0 else 1
            # Periodic cubic fields span overlapping sections. One shared geometry
            # is checked and scored globally after each update.
            p[key][knot]+=sign*amount*step
            if key=='local_spacing':
                # Paired local rate changes reduce propagation into distant fits.
                p[key][(knot+1)%FIELD_SIZE]-=sign*amount*step
            if key=='local_phase' and age%4<2:
                for offset in [-1,1]:p[key][(knot+offset)%FIELD_SIZE]+=.35*sign*amount*step
            operation=f'{key}[{knot}] {sign*amount*step:+g}; failure section {section}'
        elif stage=='C':
            keys=[('phase',.06),('s0',.8),('count',3),('winding',1),('local_metric',.2),('local_turn',.2),('elevation',1.5),('smooth',.15)]
            key,amount=keys[((slot-32)//2)%len(keys)];sign=-1 if slot%2==0 else 1
            if key=='smooth':
                key=['local_phase','local_spacing','local_bend'][(age//64)%3]
                v=np.asarray(p[key]);p[key]=(v+.15*((np.roll(v,1)+np.roll(v,-1))/2-v)).tolist()
                operation='global field reconciliation '+key
            else:
                delta=sign*amount*(1 if key in ('count','winding') else step)
                p[key]=p.get(key,0.)+(int(delta) if key in ('count','winding') else delta)
                if key=='count':p['winding']=round(p['count']/parent['parameters']['count']*p['winding'])
                operation=f'global {key} {delta:+g}'
        else:
            keys=[('scale',.08),('yaw',2.),('radius',.025),('perspective',.0001),('turn',.015),('gap_steps',.5),('axial',.015),('minor',.04),('seam_fraction',.04),('local_phase_bias',.04)]
            if slot%4==0:
                # Reproducible count/phase restart, still physical-gated.
                p['count']+=int(rng.integers(-30,31));p['winding']=round(p['count']/p['turn'])
                p['phase']=float(np.clip(p['phase']+rng.uniform(-.3,.3),-np.pi,np.pi))
                operation='count-phase restart'
            else:
                key,amount=keys[int(rng.integers(len(keys)))];delta=float(rng.choice([-1,1]))*amount*step
                p[key]=p.get(key,-.5 if key=='seam_fraction' else 0.)+delta
                if key=='scale':
                    # Paired camera/dimension direction preserves projected size.
                    factor=parent['parameters']['scale']/p['scale']
                    p['radius']*=factor;p['minor']*=factor
                if key=='seam_fraction' and p['topology']=='closed':p['seam_fraction']=-.5
                if key=='turn' and p['topology']=='closed':p['winding']=round(p['count']/p['turn'])
                operation='exploratory '+key
        trial=dict(parameters=p,origin='autonomous refinement',stage=stage,parent=parent['id'],operation=operation)
    state['rng']=rng.bit_generator.state
    return trial


class Runner:
    def __init__(self,out,config,resume=False):
        self.out=Path(out);self.config=config;self.stop=False
        self.data,self.frozen=load_evidence()
        if resume:
            self.state=read(self.out/'checkpoint.json')
            load_evidence(self.state)
            if self.state['sealed']:raise ValueError('Sealed reserved evaluation cannot resume; start a separate run without treating those outcomes as fresh confirmation')
            if self.state['environment']!=environment():raise ValueError('Numerical environment changed since checkpoint')
            if self.state['sources']!=fingerprints():raise ValueError('Implementation changed since checkpoint; resume requires identical source')
            if self.state['evidence']!=self.frozen['inputs_sha256']:raise ValueError('Evidence changed')
            for k in ('seed','population','patience','min_delta','count_min','count_max','objective'):
                if config.get(k) is not None and config[k]!=self.state['config'][k]:raise ValueError('Cannot change resume setting '+k)
            self.config={**self.state['config'],**{k:v for k,v in config.items() if v is not None}}
        else:
            if (self.out/'checkpoint.json').exists() or (self.out/'candidates').exists():raise ValueError('Output already contains a run; use --resume or a new directory')
            starts,counts=starting_models(self.data,config['seed'])
            if config.get('count_min') is not None:counts[0]=config['count_min']
            if config.get('count_max') is not None:counts[1]=config['count_max']
            if counts[0]>counts[1] or counts[0]<401:raise ValueError('Invalid count range')
            self.state=dict(schema=SCHEMA,created=utc(),config=config,sources=fingerprints(),environment=environment(),evidence=self.frozen['inputs_sha256'],
                photographic_cues=self.frozen['cues_sha256'],next_id=0,starts=starts,count_range=counts,rng=np.random.default_rng(config['seed']).bit_generator.state,
                pool=[],pending=None,elapsed_seconds=0.,sealed=False,stop_reason=None,best_validation=None,last_validation_improvement=0,
                last_merit_improvement=0,best_merit=None,step_scale=1.,history=[],seen={},completed_transactions=0)
        self.pool=[read(self.path(i)) for i in self.state['pool']]
        self.objectives={(s,t):Objective(self.data,s,t,mode=self.config.get('objective','balanced')) for s,t in [('train','coarse'),('train','fine'),('validation','fine')]}
        self.started=time.monotonic();self.base_elapsed=self.state['elapsed_seconds']

    def path(self,identifier):
        return self.out/'candidates'/f'{identifier:06d}.json.gz'

    def checkpoint(self):
        self.state['elapsed_seconds']=self.base_elapsed+time.monotonic()-self.started
        save(self.out/'checkpoint.json',self.state)

    def interrupt(self,signum,frame):
        self.stop=True

    def evaluate(self,trial,identifier):
        row=dict(id=identifier,**trial);p=row['parameters'];start=time.monotonic()
        key=digest(p)
        if key in self.state['seen']:
            row.update(status='duplicate',duplicate_of=self.state['seen'][key],reason='Identical parameters already evaluated')
        elif not valid(p,self.state['count_range']):
            row.update(status='bounds-rejected',reason='Documented parameter/count bounds')
        else:
            try:
                scene=Chain(p,self.data);cert=contact(scene)
                row['contact']={k:v for k,v in cert.items() if k!='witnesses'}
                row['closure']=scene.closure()
                if not cert['certified']:
                    row.update(status='physical-rejected',reason=cert['state'])
                else:
                    coarse=self.objectives['train','coarse'].assess(scene,discrete=False);row['coarse']=compact(coarse)
                    parent=next((r for r in self.pool if r['id']==row['parent']),None)
                    promote=(row['stage']=='A' or parent is None or coarse['score']>=parent['coarse']['score']-.015 or identifier%8==0)
                    if not promote:
                        row.update(status='screened',reason='Coarse score below parent by >0.015; every eighth proposal bypasses screening')
                    else:
                        row['train']=self.objectives['train','fine'].assess(scene)
                        row['validation']=self.objectives['validation','fine'].assess(scene)
                        row.update(status='eligible',reason='Certified; fine sampled train/validation evaluation',selection_score=merit(row))
            except (ValueError,FloatingPointError,ArithmeticError) as error:
                row.update(status='numerical-rejected',reason=f'{type(error).__name__}: {error}')
        row['seconds']=time.monotonic()-start
        return row

    def incorporate(self,row):
        n=row['id'];self.state['seen'][digest(row['parameters'])]=n
        if row['status']=='eligible':
            self.pool=select_population(self.pool+[row],self.config['population'])
            best=max(self.pool,key=merit)
            if self.state['best_merit'] is None or merit(best)>self.state['best_merit']+self.config['min_delta']:
                self.state['best_merit']=merit(best);self.state['last_merit_improvement']=n
            v=row['validation']['score']
            if self.state['best_validation'] is None or v>self.state['best_validation']+self.config['min_delta']:
                self.state['best_validation']=v;self.state['last_validation_improvement']=n
        best=max(self.pool,key=merit) if self.pool else None
        self.state['pool']=[r['id'] for r in self.pool]
        self.state['history'].append(dict(id=n,stage=row['stage'],status=row['status'],seconds=row['seconds'],
            score=row.get('selection_score'),best=merit(best) if best else None,best_id=best['id'] if best else None,
            best_validation=self.state['best_validation'],best_train=best['train']['score'] if best else None))
        self.state['next_id']=n+1;self.state['completed_transactions']+=1;self.state['pending']=None
        if n>=len(self.state['starts']) and (n-len(self.state['starts'])+1)%64==0:
            idle=n-max(self.state['last_merit_improvement'],self.state['last_validation_improvement'])
            if idle>=64:self.state['step_scale']=max(.125,self.state['step_scale']*.5)
            else:self.state['step_scale']=min(1.,self.state['step_scale']*1.1)

    def run(self):
        old={s:signal.signal(s,self.interrupt) for s in (signal.SIGINT,signal.SIGTERM)}
        self.state['stop_reason']=None;self.checkpoint()
        try:
            while True:
                n=self.state['next_id'];elapsed=self.base_elapsed+time.monotonic()-self.started
                if self.stop:reason='signal';break
                if n>=self.config['max_evaluations']:reason='evaluation-budget';break
                if elapsed>=self.config['seconds']:reason='time-budget';break
                if n>=len(self.state['starts']) and not self.pool:reason='no-feasible-start';break
                age=n-len(self.state['starts'])
                if age>=128 and n-self.state['last_validation_improvement']>=self.config['patience']:
                    reason='validation-stagnation';break
                if age>=128 and self.state['step_scale']<=.125 and n-self.state['last_merit_improvement']>=128:
                    reason='convergence';break
                if self.state['pending'] is None:
                    self.state['pending']=propose(self.state,self.pool,self.data);self.checkpoint()
                # Crash after result write but before checkpoint: apply immutable
                # completed transaction, never re-evaluate it.
                if self.path(n).exists():row=read(self.path(n))
                else:
                    row=self.evaluate(self.state['pending'],n);save(self.path(n),row)
                self.incorporate(row);self.checkpoint()
                best=max(self.pool,key=merit) if self.pool else None
                print(f"{n:06d} {row['stage']} {row['status']} best={merit(best):.6f} id={best['id']} count={best['parameters']['count']}" if best else f"{n:06d} {row['status']}: {row['reason']}",flush=True)
            self.state['stop_reason']=reason;self.checkpoint()
            return self.state
        except Exception as error:
            import traceback
            save(self.out/'failure.json',dict(utc=utc(),error=repr(error),traceback=traceback.format_exc(),pending=self.state['pending'],next_id=self.state['next_id']))
            self.state['stop_reason']='implementation-error';self.checkpoint()
            raise
        finally:
            for s,handler in old.items():signal.signal(s,handler)
