"""Transactional native discovery and joint basin refinement, no derivative gate."""
from pathlib import Path
from copy import deepcopy
import signal, time, resource
from collections import Counter
import numpy as np
from scipy.stats import qmc
from photo2.r297.common import ROOT, read, save, sha, digest, utc, environment
from photo2.r306.evidence import load, SOURCES
from photo2.r309.measure import Measures
from .model import starts, scene, canonical, validate, BOUNDS, PAIRS, VARIABLES
from .diagnostics import FirstErrors

def sources():
    paths=list((ROOT/'photo2/r311').glob('*.py'))
    # Delivery/audit may be written while sampling; only scientific search and
    # its complete imported geometry/objective dependency tree bind a restart.
    paths=[p for p in paths if p.name in ['model.py','diagnostics.py','search.py']]
    for module in ['r295','r297','r298','r299','r306','r307','r309']:
        paths += list((ROOT/'photo2'/module).glob('*.py'))
    paths += [ROOT/'photo2/r307/kernel.cpp',ROOT/'photo2/phase2_basin_search.py']
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}

def physical(s):
    cert=s.certify(iterations=100,witnesses=False)
    if cert['certified']:return dict(cert,state='certified-separated')
    cert=s.certify(iterations=220,witnesses=True)
    if cert['certified']:
        cert.pop('witnesses',None);return dict(cert,state='certified-separated')
    # A separation failure is not evidence of penetration. Test original solid
    # surface samples on up to24 unresolved pairs; a single negative SDF is a
    # witness, whereas no witness remains explicitly inconclusive.
    from photo2.r295.geometry import SURFACE, AXES
    checks=[]
    for w in [w for w in cert['witnesses'] if not w['separated']][:24]:
        a,b=w['pair'];minimum=0.
        for j,k in [(a,b),(b,a)]:
            pts=s.centers[j]+sum((SURFACE*s.dims)[:,i,None]*s.g[key][j] for i,key in enumerate(AXES))
            delta=pts-s.centers[k];q=np.column_stack([delta@s.g[key][k] for key in AXES])
            minimum=min(minimum,float(s.local_sdf(q).min()))
        checks.append(dict(pair=[int(s.indices[a]),int(s.indices[b])],minimum_sdf=minimum,penetrating=minimum<-.001))
    cert.pop('witnesses');cert['penetration_checks']=checks
    cert['state']='witnessed-penetration' if any(c['penetrating'] for c in checks) else 'unresolved-separation'
    return cert

def broad_plan():
    seeds=starts();plan=[]
    for seed in seeds:plan.append(dict(family=seed['name'],parameters=seed['parameters'],kind='start'))
    grids={}
    for seed in seeds[:3]:
        p=seed['parameters']
        grids[seed['name']]={
          'phase':p['phase']+np.arange(-3,4)*2*np.pi/7,
          's0':np.linspace(-40,40,5),
          'elevation':np.array([30.,40.,50.,60.,70.,80.,88.]),
          'roll':np.linspace(-70,70,7), 'minor':np.linspace(3.,6.,7),
          'scale':np.linspace(6.5,11.,7),'tilt':np.linspace(-30,30,5)}
    jobs=[]
    # Every pair is interleaved across all three principal hypotheses.
    for a,b in PAIRS:
        for i in range(7):
            for j in range(7):
                for seed in seeds[:3]:
                    g=grids[seed['name']]
                    if i>=len(g[a]) or j>=len(g[b]):continue
                    p=deepcopy(seed['parameters']);p[a]=float(g[a][i]);p[b]=float(g[b][j])
                    jobs.append(dict(family=seed['name'],parameters=canonical(p),kind='map',pair=[a,b],cell=[i,j],coordinates=[float(g[a][i]),float(g[b][j])]))
    # Deterministic shuffle avoids completing only the first pair if time ends.
    order=np.random.default_rng(311).permutation(len(jobs));jobs=[jobs[i] for i in order]
    sobol=[]
    blocks=[(['phase','s0','elevation','roll'],[[-np.pi,np.pi],[-40,40],[30,88],[-70,70]]),
            (['elevation','minor','scale','axial'],[[30,88],[3,6],[6.5,11],[.45,1.25]])]
    for bi,(keys,box) in enumerate(blocks):
        samples=qmc.Sobol(4,scramble=True,seed=311+bi).random_base2(5)
        for ni,x in enumerate(samples):
            for seed in seeds[:3]:
                p=deepcopy(seed['parameters'])
                for k,z,(lo,hi) in zip(keys,x,box):p[k]=float(lo+z*(hi-lo))
                sobol.append(dict(family=seed['name'],parameters=canonical(p),kind='sobol',block=keys,sample=ni))
    # Broad 4D evaluations run throughout response mapping, not only afterwards.
    for i,job in enumerate(jobs):
        plan.append(job)
        if i%3==2 and sobol:plan.append(sobol.pop(0))
    plan.extend(sobol)
    return plan

def target_loss(row):
    z={r['id']:r for r in row['first_errors']}
    return float(np.mean([1-z[k]['modal_fraction'] for k in ['C-1477-0290','C-1608-0253']]))

def coordinate_distance(a,b):
    d=[]
    for k in VARIABLES:
        lo,hi=BOUNDS[k];x=a[k]-b[k]
        if k=='phase':x=(x+np.pi)%(2*np.pi)-np.pi
        d.append(x/(hi-lo))
    return float(np.linalg.norm(d))

class Runner:
    def __init__(self,out,seconds=2400.,resume=False,max_evaluations=1600):
        self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True)
        self.seconds=seconds;self.maxeval=max_evaluations;self.stop=False
        self.t=time.monotonic();self.data,self.m,self.obs=load()
        self.objective=Measures(self.data,self.m,self.obs);self.errors=FirstErrors(self.data)
        self.seeds={s['name']:s for s in starts()}
        if resume:
            self.state=read(self.out/'checkpoint.json')
            assert not self.state['sealed'],'Sealed search cannot resume'
            assert self.state['sources']==sources(),'Search source changed'
            assert self.state['environment']==environment(),'Numerical environment changed'
            assert all(sha(ROOT/p)==h for p,h in self.state['evidence'].items()),'Evidence changed'
        else:
            assert not (self.out/'checkpoint.json').exists(),'Use --resume or new output'
            self.state=dict(started=utc(),sources=sources(),evidence={p:sha(ROOT/p) for p in SOURCES},
                            start_models={s['source']:sha(ROOT/s['source']) for s in self.seeds.values()},
                            environment=environment(),elapsed=0.,next_id=0,plan=broad_plan(),cursor=0,
                            cache={},pending=None,basins=[],round=0,refinement=[],refine_cursor=0,
                            stage='broad',sealed=False,transitions=[],deduplicated=0)
        assert all(sha(ROOT/p)==h for p,h in self.state['start_models'].items())
        self.prior=self.state['elapsed'];self.rows=[read(p) for p in sorted((self.out/'trials').glob('*.gz'))]
        # A fully written trial before a killed checkpoint is recovered in run().
        for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,lambda *_:setattr(self,'stop',True))
        self.state.pop('stop_reason',None)
    def elapsed(self):return self.prior+time.monotonic()-self.t
    def checkpoint(self):
        self.state.update(elapsed=self.elapsed(),budget_seconds=self.seconds,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
        save(self.out/'checkpoint.json',self.state)
    def trial(self,job):
        seed=self.seeds[job['family']];p=canonical(job['parameters'])
        key=digest(dict(implementation=seed['implementation'],parameters=p))
        if key in self.state['cache']:
            self.state['deduplicated']+=1;return None
        i=self.state['next_id'];path=self.out/'trials'/f'{i:06d}.json.gz'
        if path.exists():
            row=read(path);assert row['key']==key
        else:
            began=time.monotonic();row=dict(job,id=i,key=key,parameters=p,implementation=seed['implementation'],feasible=False,predicted_improvement=None,prediction_policy='Unmodeled global discovery' if job['kind'] in ['start','map','sobol'] else 'Nearest sampled basin score; no derivative or feasibility prediction')
            if 'predicted_score' in job:
                row['predicted_improvement']=job['parent_score']-job['predicted_score']
            try:
                rejection=validate(p)
                if rejection:row.update(status='bounds-rejected',rejection=rejection)
                else:
                    s=scene(p,self.data,seed['implementation']);cert=physical(s);row['physical']=cert
                    if not cert['certified']:row.update(status=cert['state'],rejection=cert['state'])
                    else:
                        result=self.objective.evaluate(s)
                        row.update(feasible=True,status='feasible',result={k:v for k,v in result.items() if k not in ['boundary','supports','reflections','vectors']},
                                   reflection_records=result['reflections'],first_errors=self.errors.evaluate(s))
                        row['target_loss']=target_loss(row)
                        row['global_score']=result['scores']['balanced']
                        row['search_score']=row['global_score']+.20*row['target_loss']
                        # Missing lobes are scored and recorded, never a basin gate.
                        row['missing_highlights']=result['missing']
                        row['measured_improvement']=job.get('parent_score',row['search_score'])-row['search_score'] if 'parent_score' in job else None
            except (ValueError,ArithmeticError) as e:
                row.update(status='numerical-rejected',rejection=str(e))
            row.update(seconds=time.monotonic()-began,elapsed=self.elapsed())
            save(path,row)
        self.state['cache'][key]=i;self.state['next_id']=i+1
        if not any(r['id']==i for r in self.rows):self.rows.append(row)
        if i%10==0 or job['kind']=='start':print(i,job['family'],job['kind'],row['status'],round(row.get('search_score',-1),5),'elapsed',round(self.elapsed(),1),flush=True)
        return row
    def detect_basins(self):
        basins=[]
        for family in self.seeds:
            rows=[r for r in self.rows if r['feasible'] and r['family']==family]
            if not rows:continue
            base=next((r for r in rows if r['kind']=='start'),min(rows,key=lambda r:r['global_score']))
            # Retain distinct whole-score islands and constrained first-error
            # tradeoffs. No missing-lobe/derivative rejection hides feasible basins.
            pools=[sorted(rows,key=lambda r:r['search_score']),sorted([r for r in rows if r['global_score']<=base['global_score']*1.15],key=lambda r:r['target_loss'])]
            chosen=[]
            for pool in pools:
                for r in pool:
                    if all(coordinate_distance(r['parameters'],q['parameters'])>.045 for q in chosen):chosen.append(r);break
            for r in chosen:
                basins.append(dict(family=family,trial=r['id'],score=r['search_score'],global_score=r['global_score'],target_loss=r['target_loss'],parameters=r['parameters'],kind=r['kind'],physical=r['physical']))
        self.state['basins']=basins;save(self.out/'basins.json',basins)
        return basins
    def refinement_plan(self):
        basins=self.detect_basins();jobs=[];radius=2.**(-self.state['round'])
        for basin in basins:
            p=basin['parameters'];parent=basin['trial'];score=basin['score']
            # Subdivide two axes jointly; samples can cross invalid intermediate
            # states. Multiple radii and centers survive between rounds.
            pair=PAIRS[(self.state['round']+parent)%len(PAIRS)]
            row=next(r for r in self.rows if r['id']==parent)
            if row.get('pair') and self.state['round']<2:pair=row['pair']
            widths=dict(phase=2*np.pi/7,s0=20.,elevation=10.,roll=70/3,minor=.5,scale=.75,tilt=15.)
            for x,y in [(-.5,-.5),(-.5,0),(-.5,.5),(0,-.5),(0,.5),(.5,-.5),(.5,0),(.5,.5)]:
                q=deepcopy(p)
                for k,d in zip(pair,[x,y]):q[k]+=d*widths[k]*radius
                # Inverse-distance mean of nearest feasible sampled scores is
                # an explicitly weak forecast, saved against native outcomes.
                nearby=sorted([r for r in self.rows if r['feasible'] and r['family']==basin['family']],key=lambda r:coordinate_distance(q,r['parameters']))[:4]
                dis=np.array([coordinate_distance(q,r['parameters']) for r in nearby]);w=1/np.maximum(.001,dis)**2
                pred=float(np.average([r['search_score'] for r in nearby],weights=w))
                jobs.append(dict(family=basin['family'],parameters=canonical(q),kind='refine',pair=pair,
                                 round=self.state['round'],parent=parent,parent_score=score,predicted_score=pred))
        # Balanced round robin; families are never collapsed into a single basin.
        return jobs
    def run(self):
        st=self.state;self.checkpoint()
        while True:
            if self.stop:st['stop_reason']='signal';break
            if self.elapsed()>=self.seconds:st['stop_reason']='cumulative time budget';break
            if st['next_id']>=self.maxeval:st['stop_reason']='evaluation budget';break
            if st['pending'] is None:
                if st['stage']=='broad' and (st['cursor']>=len(st['plan']) or self.elapsed()>=self.seconds*.78):
                    st['stage']='refine';st['transitions'].append(dict(elapsed=self.elapsed(),event='broad discovery ended',completed=st['cursor'],planned=len(st['plan'])))
                if st['stage']=='broad':job=st['plan'][st['cursor']]
                else:
                    if st['refine_cursor']>=len(st['refinement']):
                        st['refinement']=self.refinement_plan();st['refine_cursor']=0
                        if not st['refinement']:st['stop_reason']='no certified basin';break
                        st['round']+=1
                        if st['round']>6:st['stop_reason']='six adaptive subdivision rounds complete';break
                    job=st['refinement'][st['refine_cursor']]
                st['pending']=job;self.checkpoint()
            self.trial(st['pending'])
            if st['stage']=='broad':st['cursor']+=1
            else:st['refine_cursor']+=1
            st['pending']=None;self.checkpoint()
        self.detect_basins();self.checkpoint()
        save(self.out/'search-summary.json',dict(stop_reason=st['stop_reason'],elapsed=st['elapsed'],evaluations=st['next_id'],statuses=dict(Counter(r['status'] for r in self.rows)),broad_completed=st['cursor'],broad_planned=len(st['plan']),deduplicated=st['deduplicated'],basins=st['basins']))
        return st
