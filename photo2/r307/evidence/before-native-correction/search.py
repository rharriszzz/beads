"""Budgeted block Gauss--Newton with atomic trials and fixed-owner subproblems."""
from copy import deepcopy
from pathlib import Path
import time,signal,resource,subprocess
import numpy as np
from scipy.stats import spearmanr
from photo2.r297.common import ROOT,read,save,sha,utc,environment,digest
from photo2.r306.evidence import load,SOURCES
from photo2.r306.geometry import valid
from .fast import Chain,predict
from .objective import Objective
BASE=ROOT/'photo2/r307'
SCALARS=dict(scale=.08,axial=.02,minor=.05,elevation=.7,roll=.8,phase=.035,s0=.6,tilt=.5,light_az=2.,light_el=1.2,roughness=.4,turn=.0003)
SCALES=dict(axis_nodes=1.2,local_phase=.04,local_spacing=.0008)
def sources():
    paths=list(BASE.glob('*.py'))+[BASE/'kernel.cpp',ROOT/'photo2/phase2_guided_fit.py']
    paths += [ROOT/f'photo2/{d}/{f}' for d,fs in [('r306',['geometry.py','evidence.py','objective.py','export.py']),('r295',['geometry.py']),('r299',['forward.py']),('r297',['geometry.py'])] for f in fs]
    # Export/UI sources can evolve after fitting; scientific sources cannot.
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.exists() and p.name not in ['delivery.py','review.py','verify.py','tests.py','browser_check.py','preflight.py']}
def initial():
    folder=ROOT/'photo2/r306/results/campaign/exports'
    names=['primary','alternative-2665','alternative-1857','alternative-2433']
    return [dict(name='R306-'+name,parameters=read(folder/(name+'.json.gz'))['parameters']) for name in names]
def move(p,names,z):
    q=deepcopy(p)
    for name,delta in zip(names,z):
        if ':' in name:
            key,k=name.split(':');q[key][int(k)]+=float(delta)*SCALES[key]
        else:q[name]+=float(delta)*SCALARS[name]
    # The spacing mean is a gauge removed before the same arclength normalization.
    q['local_spacing']=(np.array(q['local_spacing'])-np.mean(q['local_spacing'])).tolist()
    return q

def benchmark(out):
    data,m,obs=load();obj=Objective(data,m,obs);starts=initial();p=starts[0]['parameters'];s=Chain(p,data)
    from photo2.r306.geometry import Chain as Original
    # Exclude compilation from warm timing, but record its wall time separately.
    xy=np.load(ROOT/'photo2/r296/evidence/cues.npz')['xy'];rows=[]
    a=None
    for name,sc in [('compiled',s),('original',Original(p,data))]:
        t=time.monotonic();tr=sc.trace(xy);elapsed=time.monotonic()-t
        if a is None:a=tr
        else:
            np.testing.assert_array_equal(a['owner'],tr['owner']);np.testing.assert_array_equal(a['unknown'],tr['unknown']);np.testing.assert_allclose(a['points'],tr['points'],atol=1e-9,rtol=0)
        rows.append(dict(kernel=name,rays=len(xy),seconds=elapsed))
    # Full native saved predictions must agree at the same fixed owner.
    t=time.monotonic();pred,meta=predict(s,1.);saved=read(ROOT/'photo2/r306/results/campaign/exports/primary.json.gz');truth={r['index']:r['reflection'] for r in saved['positions'] if r['reflection']};new={r['index']:r for r in pred};assert set(truth)==set(new)
    delta=max(np.linalg.norm(np.array(new[k]['point'])-truth[k]['centroid']) for k in truth);assert delta<1e-9
    native=dict(seconds=time.monotonic()-t,lobes=len(pred),maximum_centroid_difference=delta,numerics=meta)
    _,base,anchors=obj.evaluate(s,step=1.)
    ranking=[]
    variants=[p]+[move(p,[k],[sign]) for k,sign in [('axial',-1),('phase',1),('minor',-1),('axis_nodes:8',1),('local_spacing:16',1),('local_phase:24',1)]]
    for i,q in enumerate(variants):
        sc=Chain(q,data);cert=sc.certify(iterations=65,witnesses=False);row=dict(id=i,parameters=q,physical=cert)
        if cert['certified']:
            for step in [2.,1.]:
                _,r,_=obj.evaluate(sc,anchors,step=step);row[str(int(step))]=r
        ranking.append(row)
    good=[r for r in ranking if '1' in r];x=[r['2']['loss'] for r in good];y=[r['1']['loss'] for r in good];rho=float(spearmanr(x,y).statistic)
    result=dict(utc=utc(),kernel=rows,native_equivalence=native,ranking=ranking,spearman=rho,coarse_best=int(good[int(np.argmin(x))]['id']),native_best=int(good[int(np.argmin(y))]['id']),policy='Two-pixel native surface/shadow predictor only if rank correlation >= .8; final acceptance uses native fixed owners. Full physical gate never approximated.',fit_step=2. if rho>=.8 else 1.,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    save(out/'benchmark.json',result);print('Benchmark ranking',rho,'step',result['fit_step'],flush=True);return result

class Budget(Exception):pass
class Runner:
    def __init__(self,out,seconds=1200,resume=False,max_evaluations=100000):
        self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True);self.limit=seconds;self.maxeval=max_evaluations
        self.data,self.m,self.obs=load();self.obj=Objective(self.data,self.m,self.obs);self.stop=False;self.t=time.monotonic()
        signal.signal(signal.SIGTERM,lambda *_:setattr(self,'stop',True))
        path=self.out/'checkpoint.json'
        if resume:
            self.state=read(path)
            if self.state.get('sealed'):raise ValueError('Sealed run cannot resume; use a new output')
            if self.state['sources']!=sources():raise ValueError('Scientific source changed; resume refused')
            if self.state['evidence']!={p:sha(ROOT/p) for p in SOURCES}:raise ValueError('Evidence changed')
        else:
            if path.exists():raise ValueError('Output already exists; resume or use a new output')
            self.state=dict(sources=sources(),evidence={p:sha(ROOT/p) for p in SOURCES},environment=environment(),elapsed=0.,next_id=0,cycle=0,history=[],families=[],sensitivity=[],sealed=False,started=utc())
        self.prior=self.state['elapsed'];self.fit_step=read(self.out/'benchmark.json')['fit_step'] if (self.out/'benchmark.json').exists() else 2.
    def checkpoint(self):
        self.state['elapsed']=self.prior+time.monotonic()-self.t;self.state['peak_rss_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        save(self.out/'checkpoint.json',self.state)
    def check(self):
        if self.stop or self.prior+time.monotonic()-self.t>=self.limit or self.state['next_id']>=self.maxeval:raise Budget
    def trial(self,p,anchors,tag,step=None):
        self.check();t=time.monotonic();i=self.state['next_id'];path=self.out/'trials'/f'{i:06d}.json.gz'
        # A published-but-uncheckpointed trial is replayed idempotently on resume.
        row=dict(id=i,parameters=p,tag=tag,step=self.fit_step if step is None else step)
        v=None;a=anchors
        if not valid(p):row.update(feasible=False,reason='parameter bound')
        else:
            try:
                s=Chain(p,self.data);cert=s.certify(iterations=80,witnesses=False);row['physical']=cert
                if cert['certified']:
                    v,r,a=self.obj.evaluate(s,anchors,step=row['step']);row.update(feasible=True,result=r,anchors=a)
                else:row.update(feasible=False,reason='support separation not certified')
            except ValueError as e:row.update(feasible=False,reason=str(e))
        row['seconds']=time.monotonic()-t;row['elapsed']=self.prior+time.monotonic()-self.t
        save(path,row);self.state['next_id']+=1;self.state['history'].append(dict(id=i,tag=tag,feasible=row['feasible'],loss=row.get('result',{}).get('loss'),seconds=row['seconds'],elapsed=row['elapsed']))
        self.checkpoint();return v,row,a
    def run(self):
        try:
            if not self.state.get('initialized'):
                done={r['name'] for r in self.state['families']}
                for r in initial():
                    if r['name'] in done:continue
                    v,row,a=self.trial(r['parameters'],None,'initialize-'+r['name'],step=1.)
                    if row['feasible']:self.state['families'].append(dict(name=r['name'],parameters=r['parameters'],anchors=a,initial_anchors=a,initial=row['result'],native=row['result'],best_id=row['id']))
                self.state['families'].sort(key=lambda r:r['native']['loss']);self.state['initialized']=True;self.checkpoint()
            while True:
                cycle=self.state['cycle'];family=self.state['families'][0 if cycle%6!=5 else (1+(cycle//6)%max(1,len(self.state['families'])-1))];p=family['parameters'];anchors=family['anchors']
                names=list(SCALARS) if cycle%5==0 else [f'{key}:{j}' for key in SCALES for j in range((cycle%5-1)*8,(cycle%5)*8)]
                v,base,_=self.trial(p,anchors,'linearization-base');J=[];pert=[];choices=[]
                for name in names:
                    sides=[]
                    for sign in ([1,-1] if cycle%5==0 else [1]):
                        q=move(p,[name],[sign]);vv,r,_=self.trial(q,anchors,'sensitivity:'+name+':'+str(sign))
                        sides.append((sign,vv,r));pert.append(r['id'])
                        if r['feasible']:choices.append((r['result']['loss'],q,r['id']))
                    good=[x for x in sides if x[1] is not None]
                    if not good:
                        vv,r,_=self.trial(move(p,[name],[-1]),anchors,'sensitivity:'+name+':-1');pert.append(r['id']);good=[(-1,vv,r)] if vv is not None else []
                    if len(good)==2:d=(good[0][1]-good[1][1])/(good[0][0]-good[1][0])
                    elif len(good)==1:d=(good[0][1]-v)/good[0][0]
                    else:d=np.zeros_like(v)
                    J.append(d)
                J=np.array(J).T;u,sv,vt=np.linalg.svd(J,full_matrices=False);damping=max(.0001,(sv[0]*.08)**2) if len(sv) else .01
                z=-(vt.T*(sv/(sv*sv+damping)))@(u.T@v);z/=max(1.,np.max(abs(z))/1.5)
                norms=np.linalg.norm(J,axis=0);corr=J.T@J/np.maximum(norms[:,None]*norms[None,:],1e-12);pairs=sorted([(abs(corr[i,j]),i,j) for i in range(len(names)) for j in range(i)],reverse=True)[:8]
                sensitivity=dict(cycle=cycle,family=family['name'],names=names,base=base['id'],trials=pert,jacobian=J.tolist(),residual=v.tolist(),singular_values=sv.tolist(),right_vectors=vt.tolist(),column_norms=norms.tolist(),couplings=[dict(a=names[i],b=names[j],cosine=float(corr[i,j])) for _,i,j in pairs],step=z.tolist(),damping=damping)
                save(self.out/f'sensitivity-{cycle:03d}.json.gz',sensitivity)
                for factor in [1.,.5]:
                    q=move(p,names,z*factor);vv,r,_=self.trial(q,anchors,'Gauss-Newton')
                    if r['feasible']:
                        predicted=float(v@v-np.sum((v+J@(z*factor))**2));actual=base['result']['loss']-r['result']['loss']
                        r['trust']=dict(predicted_decrease=predicted,actual_decrease=actual,ratio=actual/max(1e-12,predicted));save(self.out/'trials'/f'{r["id"]:06d}.json.gz',r)
                        if actual>0 and predicted>0 and actual/predicted>.05:choices.append((r['result']['loss'],q,r['id']));break
                improved=False
                for loss,q,source in sorted(choices,key=lambda a:a[0])[:2]:
                    if loss>=base['result']['loss']-1e-5:continue
                    _,r,_=self.trial(q,anchors,'native-acceptance',step=1.)
                    if not r['feasible']:continue
                    x=r['result'];old=family['native'];initial_result=family['initial']
                    guard=(x['unmatched']<=old['unmatched'] and x['paper']<=initial_result['paper']+.01 and x['coherence']>=initial_result['coherence']-.01 and x['boundary']<=initial_result['boundary']+.4 and x['reflection_rms']<=initial_result['reflection_rms']+.5)
                    if x['loss']<old['loss']-1e-4 and guard:
                        family.update(parameters=q,native=x,best_id=r['id']);improved=True
                        self.state.setdefault('accepted',[]).append(dict(id=r['id'],cycle=cycle,source=source,elapsed=r['elapsed'],decrease=old['loss']-x['loss']))
                        break
                # Correspondence refresh only after a complete five-block sweep;
                # native fixed-initial controls stay separate and cannot be erased.
                if (cycle+1)%5==0 and improved:
                    _,r,a=self.trial(family['parameters'],None,'correspondence-control',step=1.)
                    if r['feasible']:
                        r['fixed_before']=family['native'];save(self.out/'trials'/f'{r["id"]:06d}.json.gz',r)
                        if r['result']['unmatched']<=family['native']['unmatched'] and r['result']['loss']<family['native']['loss']*.98:
                            family.update(anchors=a,native=r['result']);self.state.setdefault('rematches',[]).append(r['id'])
                self.state['sensitivity'].append(dict(cycle=cycle,family=family['name'],improved=improved,singular_values=sv.tolist(),names=names));self.state['cycle']+=1;self.checkpoint()
                print('cycle',cycle,family['name'],'native',round(family['native']['loss'],5),'accepted',improved,'elapsed',round(self.state['elapsed'],1),flush=True)
                recent=self.state['sensitivity'][-10:]
                if len(recent)==10 and not any(r['improved'] for r in recent):self.state['stop_reason']='ten complete blocks without native accepted improvement';break
        except Budget:self.state['stop_reason']='signal' if self.stop else 'budget'
        self.checkpoint();print('Fit stopped',self.state['stop_reason'],self.state['elapsed'],flush=True);return self.state
