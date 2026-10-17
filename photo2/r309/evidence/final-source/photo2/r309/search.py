"""CPU-driven shared probes, four equal-allowance global objective branches."""
from pathlib import Path
from copy import deepcopy
import time,signal,resource
import numpy as np
from photo2.r297.common import ROOT,read,save,sha,digest,utc
from photo2.r306.evidence import load,SOURCES
from .geometry import Chain,valid
from .measure import Measures
BASE=ROOT/'photo2/r309'
SCALES=dict(phase=.12,s0=2.,turn=.001,minor=.10,axial=.04,elevation=2.,roll=2.,scale=.15,tilt=1.,minor_y=.02,tilt_y=1.,tilt_y2=1.,perspective=.0001,light_inverse=.0005,light_el=2.,light_az=3.)
OBJECTIVES=['reflection','boundary','ownership','balanced']

def sources():
    return {str(p.relative_to(ROOT)):sha(p) for p in [BASE/f for f in ['geometry.py','render.py','structural.py','measure.py','search.py']]+[ROOT/'photo2/r307/kernel.cpp',ROOT/'photo2/r306/geometry.py']}

def starts():
    rows=[]
    for folder,name in [('r306','primary'),('r306','alternative-2665'),('r306','alternative-1857'),('r307','primary'),('r308','primary')]:
        p=read(ROOT/f'photo2/{folder}/results/campaign/exports/{name}.json.gz')['parameters'];p.update(minor_y=0.,tilt_y=0.,tilt_y2=0.,light_inverse=0.)
        rows.append(dict(name=f'{folder.upper()}-{name}',parameters=p))
    return rows

def move(p,keys,d):
    q=deepcopy(p)
    for k,z in zip(keys,d):q[k]=q.get(k,0)+float(z)*SCALES[k]
    return q

def compact(r):
    return {k:v for k,v in r.items() if k not in ['boundary','supports','reflections']}

class Stop(Exception):pass
class Runner:
    def __init__(self,out,seconds=1200,resume=False,max_evaluations=100000):
        self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True);self.seconds=seconds;self.maxeval=max_evaluations;self.t=time.monotonic();self.stop=False
        signal.signal(signal.SIGTERM,lambda *_:setattr(self,'stop',True));self.data,self.m,self.obs=load();self.obj=Measures(self.data,self.m,self.obs)
        if resume:
            self.state=read(self.out/'checkpoint.json');assert not self.state.get('sealed');assert self.state['sources']==sources();assert self.state['evidence']=={p:sha(ROOT/p) for p in SOURCES}
        else:
            assert not (self.out/'checkpoint.json').exists();self.state=dict(sources=sources(),evidence={p:sha(ROOT/p) for p in SOURCES},elapsed=0.,next_id=0,cache={},shared=[],branches={},started=utc(),sealed=False)
        self.prior=self.state['elapsed'];self.end=seconds;self.state.pop('stop_reason',None)
    def elapsed(self):return self.prior+time.monotonic()-self.t
    def checkpoint(self):
        self.state['elapsed']=self.elapsed();self.state['peak_rss_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;save(self.out/'checkpoint.json',self.state)
    def check(self):
        if self.stop or self.elapsed()>self.end-5 or self.state['next_id']>=self.maxeval:raise Stop()
    def trial(self,p,tag,anchors=None):
        self.check();key=digest(dict(parameters=p,anchors=anchors));n=self.state['cache'].get(key)
        if n is not None:return read(self.out/'trials'/f'{n:06d}.json.gz')
        n=self.state['next_id'];began=time.monotonic();row=dict(id=n,tag=tag,parameters=p,feasible=False)
        try:
            if not valid(p):raise ValueError('bounds')
            s=Chain(p,self.data);cert=s.certify(iterations=100,witnesses=False);row['physical']=cert
            if not cert['certified']:raise ValueError('contact certificate failed')
            result=self.obj.evaluate(s,anchors);row.update(feasible=True,result=compact(result))
        except (ValueError,ArithmeticError) as e:row['rejection']=str(e)
        row['seconds']=time.monotonic()-began;row['elapsed']=self.elapsed();save(self.out/'trials'/f'{n:06d}.json.gz',row)
        self.state['cache'][key]=n;self.state['next_id']+=1;self.checkpoint();print(n,tag,round(row['seconds'],2),row.get('result',{}).get('scores',row.get('rejection')),flush=True);return row
    def shared_plan(self):
        plan=[(s['parameters'],'start:'+s['name']) for s in starts()]
        for s in starts()[:2]:
            p=s['parameters'];name=s['name']
            for k,values in [('phase',np.linspace(-np.pi,np.pi,9)),('s0',[-12,-6,6,12]),('turn',[-.005,0,.005])]:
                if k=='turn' and p['topology']=='closed':continue
                for v in values:q=deepcopy(p);q[k]+=float(v);plan.append((q,f'curve:{name}:{k}:{v}'))
            for delta in [-13,-1,1,13]:
                q=deepcopy(p);q['count']+=delta
                if q['topology']=='closed':q['winding']=round(q['count']/6.5)
                plan.append((q,f'count:{name}:{delta}'))
            for k,vs in [('minor_y',[-.02,.02]),('tilt_y',[-1.,1.]),('tilt_y2',[-1.,1.]),('perspective',[.0003]),('light_inverse',[.001])]:
                for value in vs:q=deepcopy(p);q[k]=value;plan.append((q,f'height-light:{name}:{k}:{value}'))
        return plan
    def vector(self,row,kind):
        v=row['result']['vectors'];keys=list(v) if kind=='balanced' else [kind,'material'];return np.concatenate([v[k] for k in keys])
    def branch(self,kind,end):
        self.end=end;b=self.state['branches'].setdefault(kind,dict(complete=False,cycles=0,accepted=[],controls=[],seconds=0.));began=self.elapsed()
        if b['complete']:return
        candidates=[read(self.out/'trials'/f'{i:06d}.json.gz') for i in self.state['shared']];candidates=[r for r in candidates if r['feasible']]
        if 'best' not in b:b['best']=min(candidates,key=lambda r:r['result']['scores'][kind])['id']
        best=read(self.out/'trials'/f"{b['best']:06d}.json.gz")
        if 'global_only_best' not in b:b['global_only_best']=min([r for r in candidates if not any(r['parameters'].get(k,0) for k in ['minor_y','tilt_y','tilt_y2','light_inverse']) and r['parameters']['perspective']<1e-5],key=lambda r:r['result']['scores'][kind])['id']
        blocks=[['phase','s0','minor','axial','elevation','scale'],['minor_y','tilt_y','perspective','light_inverse'],['roll','tilt','light_el','light_az'],['phase','s0','turn']]
        try:
            while True:
                self.check();cycle=b['cycles'];keys=blocks[cycle%len(blocks)];radius=[1.,.35,.12][min(2,cycle//len(blocks))];base=self.trial(best['parameters'],f'{kind}:fixed-base',best['result']['anchors']);v=self.vector(base,kind);columns=[];trialids=[];reliable=[];pool=[base]
                for k in keys:
                    sides=[self.trial(move(base['parameters'],[k],[sign*radius]),f'{kind}:probe:{k}:{sign}:{radius}',base['result']['anchors']) for sign in [-1,1]];pool+=sides;trialids+=[x['id'] for x in sides]
                    if all(x['feasible'] for x in sides):
                        a,z=[self.vector(x,kind) for x in sides];ratio=float(np.linalg.norm(a+z-2*v)/max(1e-12,np.linalg.norm(z-a)));columns.append((z-a)/(2*radius));reliable.append(ratio<.35)
                    else:columns.append(np.zeros_like(v));reliable.append(False)
                J=np.array(columns).T;record=dict(base=base['id'],keys=keys,radius=radius,trial_ids=trialids,reliable=reliable,singular_values=np.linalg.svd(J,compute_uv=False).tolist(),jacobian=J.tolist())
                if all(reliable) and np.linalg.norm(J)>1e-8:
                    delta=-np.linalg.solve(J.T@J+np.eye(len(keys))*.05,J.T@v);delta*=min(1.,radius/max(abs(delta)));proposal=self.trial(move(base['parameters'],keys,delta),f'{kind}:guided',base['result']['anchors']);pool.append(proposal);record.update(step=delta.tolist(),predicted_squared_residual_reduction=float(v@v-(v+J@delta)@(v+J@delta)),actual_squared_residual_reduction=float(v@v-self.vector(proposal,kind)@self.vector(proposal,kind)) if proposal['feasible'] else None)
                else:
                    # Discontinuous branch: tested bracket/coordinate steps only.
                    record['method']='native bounded coordinate bracket; unstable gradient rejected'
                new=min([r for r in pool if r['feasible']],key=lambda r:r['result']['scores'][kind]);old=base['result']['scores'][kind]
                if new['result']['scores'][kind]<old-1e-6:
                    free=self.trial(new['parameters'],f'{kind}:rematch-control');record['fixed_gain']=old-new['result']['scores'][kind];record['rematch_gain']=new['result']['scores'][kind]-free['result']['scores'][kind];best=free;b['best']=best['id'];b['accepted'].append(dict(trial=best['id'],elapsed=self.elapsed(),fixed_gain=record['fixed_gain'],rematch_gain=record['rematch_gain']))
                b['controls'].append(record);b['cycles']+=1;save(self.out/f'{kind}-sensitivity.json.gz',b['controls']);self.checkpoint()
                if cycle>=7 and not b['accepted']:b['stop_reason']='eight stagnant global blocks';break
        except Stop:b['stop_reason']='signal' if self.stop else 'allowance or evaluation bound'
        b['seconds']+=self.elapsed()-began;b['complete']=not self.stop;self.checkpoint()
    def run(self):
        try:
            self.end=min(self.seconds*.30,self.seconds)
            for i,(p,tag) in enumerate(self.shared_plan()):
                if i<len(self.state['shared']):continue
                r=self.trial(p,tag);self.state['shared'].append(r['id']);self.checkpoint()
        except Stop:pass
        self.state['shared_complete']=True;self.end=self.seconds
        if not self.stop and self.state['next_id']<self.maxeval:
            remaining=[k for k in OBJECTIVES if not self.state['branches'].get(k,{}).get('complete')]
            allowance=max(0,(self.seconds-self.elapsed())/max(1,len(remaining)))
            for kind in remaining:
                self.branch(kind,min(self.seconds,self.elapsed()+allowance))
                if self.stop:break
        self.state['stop_reason']='signal' if self.stop else 'bounded comparison complete';self.checkpoint();return self.state
