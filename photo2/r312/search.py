"""Standalone deterministic two-stage search; atomic trials and resumable state."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import signal,time,resource
import numpy as np
from scipy.stats import qmc
from photo2.r297.common import ROOT,read,save,sha,digest,utc,environment
from photo2.r306.evidence import SOURCES
from photo2.r311.search import sources as inherited_sources
from .model import seeds,canonical,validate,BOX,WIDTH,GROUPS,coordinate,distance
from .objective import Engine,bottleneck,guard,violation
from .profiling import Sampler

def sources():
    paths=['model.py','fast.py','profiling.py','objective.py','search.py']
    result=inherited_sources()
    result.update({f'photo2/r312/{p}':sha(ROOT/'photo2/r312'/p) for p in paths})
    result['photo2/phase2_minimax.py']=sha(ROOT/'photo2/phase2_minimax.py')
    return result

def proposal(p,keys,z,absolute=False,amplitude=1.):
    q=deepcopy(p);pos=0
    for key in keys:
        if key in ['axis_nodes','local_phase','local_spacing']:
            n=len(q[key]);u=np.arange(n)/n;wave=np.zeros(n)
            for f in [1,2,3]:
                a=z[pos%len(z)]*2-1;b=z[(pos+1)%len(z)]*2-1;pos+=2
                wave+=a*np.sin(2*np.pi*f*u)+b*np.cos(2*np.pi*f*u)
            scale={'axis_nodes':8.,'local_phase':.15,'local_spacing':.003}[key]*amplitude
            values=np.array(q[key])+wave*scale/3
            if key!='axis_nodes':values-=values.mean()
            q[key]=values.tolist();continue
        x=z[pos%len(z)];pos+=1;lo,hi=BOX[key]
        value=lo+x*(hi-lo) if absolute else coordinate(p,key)+(2*x-1)*WIDTH[key]*amplitude
        if key not in ['phase','roll','light_az']:value=float(np.clip(value,lo,hi))
        q[key]=float(value)
    return canonical(q)

def broad_plan(startseeds,stage):
    jobs=[dict(kind='start',family=s['family'],parameters=s['parameters'],seed=s['name']) for s in startseeds]
    samples=qmc.Sobol(24,scramble=True,seed=31200+stage).random_base2(7)
    broad=[]
    for i,z in enumerate(samples):
        group=GROUPS[i%len(GROUPS)]
        # Absolute boxes and 0.5x/2x neighborhood blocks are all interleaved.
        for s in startseeds:
            absolute=(i//len(GROUPS))%3==0 and not any(k.endswith('nodes') or k.startswith('local_') for k in group)
            amp=2. if i%3 else .5
            p=proposal(s['parameters'],group,z,absolute,amp)
            broad.append(dict(kind='sobol-box' if absolute else 'sobol-coupled',family=s['family'],parameters=p,seed=s['name'],group=group,sample=i))
    # Fair interleaving, retaining distinct immutable family labels.
    rng=np.random.default_rng(312+stage);order=rng.permutation(len(broad))
    jobs.extend(broad[i] for i in order)
    return jobs

class Runner:
    def __init__(self,out,stage,seconds=1800.,resume=False):
        self.root=Path(out);self.out=self.root/f'stage{stage}';self.out.mkdir(parents=True,exist_ok=True)
        self.stage=stage;self.seconds=seconds;self.stop=False;self.began=time.monotonic();self.cpu=time.process_time()
        self.engine=Engine(stage);self.seeds=seeds();self.rows=[]
        if stage==2:
            prior=read(self.root/'stage1/selection.json')
            assert prior['sealed'] and prior['models'],'Stage 1 must be sealed before full-necklace work'
            original={s['family']:s for s in self.seeds if s['name']==s['family']}
            self.seeds=[original['R306-2405']]+[dict(name=f'stage1-{r["id"]}',family=r['family'],parameters=r['parameters']) for r in prior['models']]+[s for f,s in original.items() if f!='R306-2405']
        self.families={s['family']:s for s in self.seeds if s['name']==s['family']}
        for s in self.seeds:self.families.setdefault(s['family'],s)
        checkpoint=self.out/'checkpoint.json'
        if resume:
            self.state=read(checkpoint);assert not self.state['sealed'],'Sealed search cannot resume'
            assert self.state['sources']==sources(),'Scientific source changed'
            assert self.state['environment']==environment(),'Numerical environment changed'
            assert all(sha(ROOT/p)==h for p,h in self.state['inputs'].items()),'Input changed'
        else:
            assert not checkpoint.exists(),'Use --resume or a new output directory'
            inputs=list(SOURCES)+[s['source'] for s in seeds()]+['photo2/r311/results/campaign/metrics/R306-2405-baseline.json.gz']
            self.state=dict(stage=stage,started=utc(),sources=sources(),environment=environment(),inputs={p:sha(ROOT/p) for p in set(inputs)},
                elapsed=0.,cpu_seconds=0.,next_id=0,pending=None,cache={},cursor=0,
                mappings={},baselines={},sealed=False,adaptive=0,phase='exploration',native_queue=[],deduplicated=0)
            save(self.out/'proposal-plan.json.gz',broad_plan(self.seeds,stage))
            self.state['proposal_plan_sha256']=sha(self.out/'proposal-plan.json.gz')
            self.state['observation_cohort']=self.engine.obs
            if stage==2:self.state['stage1_binding']={p:sha(self.root/'stage1'/p) for p in ['selection.json','checkpoint.json']}
            from .delivery import source_bundle
            source_bundle(self.out/'fitting-source',self.state['sources'])
        assert sha(self.out/'proposal-plan.json.gz')==self.state['proposal_plan_sha256']
        self.plan=read(self.out/'proposal-plan.json.gz')
        assert self.state.get('observation_cohort',self.engine.obs)==self.engine.obs,'Observation cohort changed'
        if stage==2:
            for p,h in self.state.get('stage1_binding',{}).items():assert sha(self.root/'stage1'/p)==h,'Sealed Stage 1 changed'
        self.prior=self.state['elapsed'];self.priorcpu=self.state['cpu_seconds'];self.state.pop('stop_reason',None)
        self.rows=[read(p) for p in sorted((self.out/'trials').glob('*.gz'))]
        for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,lambda *_:setattr(self,'stop',True))
    def elapsed(self):return self.prior+time.monotonic()-self.began
    def checkpoint(self):
        self.state.update(elapsed=self.elapsed(),cpu_seconds=self.priorcpu+time.process_time()-self.cpu,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,budget_seconds=self.seconds)
        save(self.out/'checkpoint.json',self.state)
    def calibrate(self,family,p):
        st=self.state
        if family in st['mappings']:return
        base=self.families[family]['parameters']
        # Calibration is native 1px, performed once per hypothesis, then frozen.
        result=self.engine.evaluate(base,None,step=1.)
        if not result['feasible']:
            result=self.engine.evaluate(p,None,step=1.);base=p
        if not result['feasible']:return result
        mapping=result['mapping']
        if self.stage==2:
            prior=read(self.root/'stage1/checkpoint.json')['mappings'].get(family,{})
            if prior:
                item,_=self.engine.geometry(base,__import__('photo2.r312.profiling',fromlist=['Timers']).Timers())
                s=item['scene'];owners=np.array(sorted({j for z in s.tree.query_ball_point([o['point'] for o in self.engine.obs],60.) for j in z}|{k-int(s.indices[0]) for k in prior.values() if k is not None}),int)
                from .profiling import Timers
                pred,_=self.engine.optics(item,owners,1.,Timers())
                mapping=bottleneck(self.engine.obs,pred,prior)
                result=self.engine.evaluate(base,mapping,step=1.)
        st['mappings'][family]=mapping;st['baselines'][family]=result
        save(self.out/'calibration'/f'{family}.json.gz',dict(parameters=base,result=result,policy='Frozen conditional one-to-one owners; all strong observations retained even if ambiguous. Stage 2 retains Stage 1 owners.'))
    def trial(self,job):
        st=self.state;p=canonical(job['parameters']);step=job.get('step',1. if self.stage==1 or st['phase']=='native' or st.get('native_only',False) else 2.)
        key=digest(dict(parameters=p,step=step,family=job['family']))
        if key in st['cache']:st['deduplicated']+=1;return None
        ident=st['next_id'];path=self.out/'trials'/f'{ident:06d}.json.gz'
        if path.exists():row=read(path);assert row['key']==key
        else:
            began=time.monotonic();cpu=time.process_time();row=dict(job,id=ident,key=key,parameters=p,step=step,feasible=False)
            rejection=validate(p)
            try:
                if rejection:row.update(status='numerical-bound',reason=rejection)
                else:
                    calibration=self.calibrate(job['family'],p)
                    mapping=st['mappings'].get(job['family'])
                    if mapping is None:row.update(status='uncertified-family',reason='No certified complete-family calibration yet',result=calibration)
                    else:
                        result=self.engine.evaluate(p,mapping,step=step)
                        row.update(result=result,feasible=result['feasible'],status='certified' if result['feasible'] else 'unresolved-contact')
                        if result['feasible']:
                            base=st['baselines'][job['family']]
                            row.update(objective_px=result['metrics']['objective_px'],passes_safeguards=guard(result,base),violation=violation(result,base))
                            if self.stage==2:
                                common=st['baselines']['R306-2405']
                                row['passes_family_safeguards']=row['passes_safeguards'];row['passes_common_safeguards']=guard(result,common)
                                row['passes_safeguards'] &= row['passes_common_safeguards']
                                row['violation']=max(row['violation'],violation(result,common))
                            row['acquisition']=row['objective_px']+50*row['violation']
            except (ValueError,FloatingPointError,OverflowError) as e:row.update(status='numerical-rejected',reason=str(e))
            row.update(seconds=time.monotonic()-began,cpu_seconds=time.process_time()-cpu,elapsed=self.elapsed())
            save(path,row)
        st['cache'][key]=ident;st['next_id']=ident+1
        if not any(r['id']==ident for r in self.rows):self.rows.append(row)
        if row.get('passes_safeguards'):
            prior=[r['objective_px'] for r in self.rows if r['id']!=ident and r.get('passes_safeguards') and r['step']==row['step']]
            row['accepted_improvement']=not prior or row['objective_px']<min(prior)
            # Store after acceptance metadata; crash recovery uses this complete file.
            save(path,row)
        if ident%20==0 or row.get('accepted_improvement'):
            print('stage',self.stage,ident,job['kind'],job['family'],row['status'],round(row.get('objective_px',-1),3),'guard',row.get('passes_safeguards'),'elapsed',round(self.elapsed(),1),flush=True)
        return row
    def shortlist(self,n=8,native=False):
        pool=[r for r in self.rows if r.get('passes_safeguards') and (not native or r['step']==1.)]
        pool.sort(key=lambda r:(r['objective_px'],r['result']['metrics']['rms_px']))
        chosen=[]
        for row in pool:
            if all(row['family']!=s['family'] or distance(row['parameters'],s['parameters'])>.035 for s in chosen):chosen.append(row)
            if len(chosen)>=n:break
        return chosen
    def adaptive_job(self):
        st=self.state;rng=np.random.default_rng(312000+self.stage*10000+st['adaptive']);i=st['adaptive'];st['adaptive']+=1
        pool=[r for r in self.rows if r.get('feasible') and 'acquisition' in r and (st['phase']!='native' or r['step']==1.)]
        if not pool:return self.plan[self.state['cursor']%len(self.plan)]
        family=list(st['mappings'])[i%len(st['mappings'])]
        family_pool=sorted([r for r in pool if r['family']==family],key=lambda r:r['acquisition'])
        if not family_pool:family_pool=sorted(pool,key=lambda r:r['acquisition'])[:8]
        # Multiple incumbents and no requirement for feasible intermediate steps.
        parent=family_pool[(i//max(1,len(st['mappings'])))%min(4,len(family_pool))]
        group=GROUPS[(i//len(st['mappings']))%len(GROUPS)]
        radius=[1.,.35,.10,.035][(i//(len(st['mappings'])*len(GROUPS)))%4]
        if i%5==0:group=['light_az','light_el','roughness','light_inverse']
        p=proposal(parent['parameters'],group,rng.random(24),False,radius)
        kind='multistart-refine'
        if i%4==1 and len(family_pool)>=4:
            a,b=rng.choice(len(family_pool[:16]),2,replace=False);a=family_pool[a]['parameters'];b=family_pool[b]['parameters']
            for k in group:
                if k in BOX:
                    lo,hi=BOX[k];p[k]=float(np.clip(coordinate(parent['parameters'],k)+.6*(coordinate(a,k)-coordinate(b,k)),lo,hi))
            p=canonical(p);kind='differential-evolution'
        job=dict(kind=kind,family=parent['family'],parameters=p,parent=parent['id'],group=group,radius=radius)
        if self.stage==2 and i%5==0:
            st['native_queue'].extend(dict(kind='illumination-batch',family=parent['family'],parameters=proposal(parent['parameters'],group,rng.random(24),False,radius),parent=parent['id'],group=group,radius=radius) for _ in range(3))
        return job
    def run(self):
        st=self.state
        if self.stage==2:
            self.calibrate('R306-2405',self.families['R306-2405']['parameters'])
            st['common_safeguard_family']='R306-2405'
        self.checkpoint()
        with Sampler(.01) as sampler:
            while self.elapsed()<self.seconds and not self.stop:
                if st['pending'] is None:
                    if self.stage==2 and self.elapsed()>=self.seconds*.72 and st['phase']!='native' and not st.get('native_only',False):
                        st['phase']='native';st['native_queue']=[dict(kind='native-promotion',family=r['family'],parameters=r['parameters'],parent=r['id'],step=1.) for r in self.shortlist(16)]
                        st['native_queue'] += [dict(kind='native-baseline',family=f,parameters=self.families[f]['parameters'],step=1.) for f in st['mappings']]
                    if st['native_queue']:job=st['native_queue'].pop(0)
                    elif st['cursor']<len(self.seeds):job=self.plan[st['cursor']];st['cursor']+=1
                    elif st['phase']=='exploration' and (self.elapsed()<self.seconds*.55 or st['adaptive']%3==2):
                        job=self.plan[st['cursor']%len(self.plan)];st['cursor']+=1;st['adaptive']+=1
                    else:job=self.adaptive_job()
                    st['pending']=job;self.checkpoint()
                self.trial(st['pending']);st['pending']=None;self.checkpoint()
            st['stop_reason']='signal' if self.stop else 'cumulative wall allowance'
        old=self.out/'sampling.json'
        save(self.out/f'sampling-{st["next_id"]:06d}.json',sampler.result())
        self.checkpoint()
        save(self.out/'summary.json',dict(stage=self.stage,evaluations=len(self.rows),elapsed=st['elapsed'],cpu_seconds=st['cpu_seconds'],statuses=dict(Counter(r['status'] for r in self.rows)),accepted_improvements=sum(r.get('accepted_improvement',False) for r in self.rows),peak_rss_mib=st['peak_rss_mib'],deduplicated=st['deduplicated'],stop_reason=st['stop_reason']))
        if not self.stop:
            models=self.shortlist(8,native=True)
            if not models:raise RuntimeError('No native certified safeguarded finalist; retain the checkpoint')
            st['sealed']=True;self.checkpoint()
            tradeoffs=[]
            if self.stage==2:
                for r in sorted([r for r in self.rows if r.get('feasible') and r['step']==1. and not r.get('passes_safeguards',False)],key=lambda r:r['objective_px']):
                    if all(r['family']!=q['family'] or distance(r['parameters'],q['parameters'])>.04 for q in tradeoffs):tradeoffs.append(r)
                    if len(tradeoffs)==2:break
            save(self.out/'selection.json',dict(sealed=True,utc=utc(),models=models,tradeoffs=tradeoffs,observations=self.engine.obs,physical_indices=list(range(-100,100)) if self.stage==1 else 'all physical bodies',parameters_frozen_between_stages=False))
        return st
