"""Native three-stage global basin search with bounded Fourier corrections.

All timed evaluations use the full chain and native optical raster. Cached trial
transactions make restart replay deterministic without recharging completed work.
"""
from pathlib import Path
from copy import deepcopy
import time,signal,resource
import numpy as np
from scipy.linalg import qr
from scipy.interpolate import CubicSpline
from photo2.r297.common import ROOT,read,save,sha,digest,utc,environment
from photo2.r306.evidence import load,SOURCES
from photo2.r306.geometry import valid
from photo2.r307.fast import Chain
from .objective import Objective
BASE=ROOT/'photo2/r308'
SCALES=dict(scale=.12,axial=.035,minor=.08,elevation=1.2,roll=1.5,phase=.08,s0=1.5,tilt=1.2,turn=.0007)
FIELD_SCALES=dict(axis_nodes=.7,local_phase=.018,local_spacing=.0005)
FIELD_LIMITS=dict(axis_nodes=2.,local_phase=.06,local_spacing=.002)

def sources():
    files=[BASE/'search.py',BASE/'objective.py',BASE/'native_refine.py',ROOT/'photo2/phase2_hierarchical_fit.py']
    files += [ROOT/f'photo2/{name}' for name in ['r307/fast.py','r307/kernel.cpp','r306/geometry.py','r306/evidence.py','r295/geometry.py','r299/forward.py','r297/geometry.py']]
    return {str(p.relative_to(ROOT)):sha(p) for p in files}

def starts():
    items=[('R306-primary','r306','primary'),('R307-primary','r307','primary')]+[(f'R306-{name}','r306',name) for name in ['alternative-2665','alternative-1857','alternative-2433']]
    return [dict(name=n,parameters=read(ROOT/f'photo2/{folder}/results/campaign/exports/{f}.json.gz')['parameters']) for n,folder,f in items]

def move(p,names,z):
    q=deepcopy(p)
    for name,d in zip(names,z):
        if ':' not in name:q[name]+=float(d)*SCALES[name]
        else:
            key,mode,wave=name.split(':');theta=2*np.pi*int(mode)*np.arange(32)/32
            basis=np.sin(theta) if wave=='sin' else np.cos(theta)
            q[key]=(np.array(q[key])+float(d)*FIELD_SCALES[key]*basis).tolist()
    return q

def correction(p,reference,data=None):
    out={};fine=np.linspace(0,1,1025)
    for key,limit in FIELD_LIMITS.items():
        delta=np.array(p[key])-reference[key];f=CubicSpline(np.linspace(0,1,33),np.r_[delta,delta[0]],bc_type='periodic')
        v=f(fine);out[key]=dict(maximum=float(abs(v).max()),rms=float(np.sqrt(np.mean(v*v))),rate_max_per_circuit=float(abs(f(fine,1)).max()),roughness=float(np.sqrt(np.mean(np.diff(v,2)**2))),limit=limit)
    out['within_bounds']=all(out[k]['maximum']<=lim+1e-9 for k,lim in FIELD_LIMITS.items())
    if data is not None:
        q=deepcopy(p)
        for key in FIELD_LIMITS:q[key]=reference[key]
        a,b=Chain(p,data),Chain(q,data);dis=np.linalg.norm(a.pc-b.pc,axis=1)
        out['projected_center_displacement_max_px']=float(dis.max());out['projected_center_displacement_rms_px']=float(np.sqrt(np.mean(dis*dis)))
        out['displacement_limit_px']=.10*2*p['radius']*p['scale']
        out['within_bounds'] &= bool(dis.max()<=out['displacement_limit_px']+1e-9)
    return out

class Halt(Exception):pass
class StageEnd(Exception):pass
class Runner:
    def __init__(self,out,seconds=1200,resume=False,max_evaluations=100000):
        self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True);self.seconds=seconds;self.maxeval=max_evaluations
        self.t=time.monotonic();self.stop=False;signal.signal(signal.SIGTERM,lambda *_:setattr(self,'stop',True))
        self.data,self.m,self.obs=load();self.obj=Objective(self.data,self.m,self.obs)
        if resume:
            self.state=read(self.out/'checkpoint.json');assert not self.state.get('sealed'),'Sealed output: use a new directory'
            assert self.state['sources']==sources(),'Changed scientific source'
            assert self.state['evidence']=={p:sha(ROOT/p) for p in SOURCES},'Changed evidence'
        else:
            assert not (self.out/'checkpoint.json').exists(),'Use --resume or a new output'
            self.state=dict(sources=sources(),evidence={p:sha(ROOT/p) for p in SOURCES},environment=environment(),started=utc(),elapsed=0.,next_id=0,cache={},accepted=[],stages={},families=[],sealed=False)
        self.prior=self.state['elapsed'];self.deadline=seconds
    def elapsed(self):return self.prior+time.monotonic()-self.t
    def checkpoint(self):
        self.state.update(elapsed=self.elapsed(),peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024);save(self.out/'checkpoint.json',self.state)
    def check(self):
        if self.stop or self.elapsed()>=self.seconds or self.state['next_id']>=self.maxeval:raise Halt
        if self.elapsed()>=self.deadline:raise StageEnd
    def trial(self,p,anchors,tag,reference=None):
        key=digest(dict(p=p,anchors=anchors,tag=tag,reference=reference))
        if key in self.state['cache']:return read(self.out/'trials'/f"{self.state['cache'][key]:06d}.json.gz")
        self.check();t=time.monotonic();i=self.state['next_id'];r=dict(id=i,tag=tag,parameters=p,feasible=False,reason='parameter bound',native_step=1.)
        if valid(p):
            try:
                corr=correction(p,reference,self.data) if reference is not None else None
                r['correction']=corr
                if corr is not None and not corr['within_bounds']:r['reason']='distributed effect bound'
                else:
                    s=Chain(p,self.data);cert=s.certify(iterations=80,witnesses=False);r['physical']=cert
                    if cert['certified']:
                        v,result,a=self.obj.evaluate(s,anchors,step=1.)
                        if reference is not None:
                            reg=[]
                            for k,lim in FIELD_LIMITS.items():
                                d=(np.array(p[k])-reference[k])/lim
                                reg.extend((np.sqrt(.08/32)*d).tolist());reg.extend((np.sqrt(.08/32)*(np.roll(d,1)-2*d+np.roll(d,-1))).tolist())
                            reg=np.array(reg);v=np.r_[v,reg];result['correction_penalty']=float(reg@reg);result['loss']=float(v@v)
                        r.update(feasible=True,reason=None,result=result,anchors=a,residual=v.tolist())
                    else:r['reason']='support separation not certified'
            except ValueError as e:r['reason']=str(e)
        r.update(seconds=time.monotonic()-t,elapsed=self.elapsed())
        save(self.out/'trials'/f'{i:06d}.json.gz',r);self.state['cache'][key]=i;self.state['next_id']+=1;self.checkpoint()
        print(i,tag,'loss',round(r.get('result',{}).get('loss',-1),5),'elapsed',round(r['elapsed'],1),flush=True)
        return r
    def guarded(self,r,base):
        if not r['feasible']:return False
        x,y=r['result'],base['result']
        return x['unmatched']<=y['unmatched'] and x['paper']<=y['paper']+.005 and x['coherence']>=y['coherence']-.01 and x['boundary']<=y['boundary']+.25 and x['reverse_boundary']<=y['reverse_boundary']+.25 and x['colored_missing']<=y['colored_missing']+.01 and x['reflection_rms']<=y['reflection_rms']+.4
    def choose(self,rows,guard):
        return min([r for r in rows if self.guarded(r,guard)],key=lambda r:r['result']['loss'])
    def jacobian(self,base,names,tag,reference=None):
        p=base['parameters'];a=base['anchors'];v=np.array(base['residual']);cols=[];trials=[];candidates=[base]
        for name in names:
            side=[]
            for sign in [-1,1]:
                r=self.trial(move(p,[name],[sign]),a,f'{tag}:{name}:{sign}',reference);trials.append(r['id'])
                if r['feasible']:side.append((sign,np.array(r['residual'])));candidates.append(r)
            d=(side[1][1]-side[0][1])/2 if len(side)==2 else (side[0][1]-v)/side[0][0] if side else np.zeros_like(v)
            cols.append(d)
        J=np.array(cols).T;u,sv,vt=np.linalg.svd(J,full_matrices=False);norm=np.linalg.norm(J,axis=0);cos=J.T@J/np.maximum(norm[:,None]*norm[None,:],1e-12)
        rec=dict(names=names,base=base['id'],trials=trials,jacobian=J.tolist(),residual=v.tolist(),singular_values=sv.tolist(),right_vectors=vt.tolist(),column_norms=norm.tolist(),couplings=sorted([dict(a=names[i],b=names[j],cosine=float(cos[i,j])) for i in range(len(names)) for j in range(i)],key=lambda r:-abs(r['cosine'])))
        save(self.out/'sensitivities'/f'{tag}.json.gz',rec)
        return J,rec,candidates
    def descent(self,base,names,guard,tag,reference=None):
        # Correspondences stay fixed throughout this numerical block.
        base=self.trial(base['parameters'],base['anchors'],tag+':base',reference)
        J,rec,rows=self.jacobian(base,names,tag,reference);v=np.array(base['residual']);u,sv,vt=np.linalg.svd(J,full_matrices=False)
        for damping in [.05,.3]:
            lam=max(1e-4,(sv[0]*damping)**2);z=-(vt.T*(sv/(sv*sv+lam)))@(u.T@v);z/=max(1,abs(z).max()/3)
            for factor in [1.,.4]:
                r=self.trial(move(base['parameters'],names,z*factor),base['anchors'],f'{tag}:LM:{damping}:{factor}',reference)
                predicted=float(v@v-np.sum((v+J@(z*factor))**2));actual=base['result']['loss']-r['result']['loss'] if r['feasible'] else None
                trust=dict(id=r['id'],base=base['id'],predicted=predicted,actual=actual,ratio=actual/predicted if actual is not None and predicted>0 else None,damping=lam,step=(z*factor).tolist())
                save(self.out/'predictions'/f"{r['id']:06d}.json",trust)
                if r['feasible'] and actual>0 and predicted>0 and actual/predicted>.03:rows.append(r)
        best=self.choose(rows,guard)
        if best['result']['loss']<base['result']['loss']-1e-5:
            event=dict(stage=tag,trial=best['id'],base=base['id'],decrease=base['result']['loss']-best['result']['loss'],elapsed=self.elapsed())
            if event['trial'] not in [e['trial'] for e in self.state['accepted']]:self.state['accepted'].append(event)
        return best
    def stage1(self):
        self.deadline=self.seconds*.56
        initial=[self.trial(r['parameters'],None,'initial:'+r['name']) for r in starts()]
        self.state['initial_ids']=[r['id'] for r in initial];self.checkpoint()
        best=min([r for r in initial if r['feasible']],key=lambda r:r['result']['loss']);baseline=best
        names=[k for k in SCALES if k!='turn' or best['parameters']['topology']=='open']
        J,rec,candidates=self.jacobian(best,names,'discovery')
        _,rr,piv=qr(J,mode='economic',pivoting=True);selected=[names[i] for i in piv[:min(8,len(names))]]
        ranking=[dict(parameter=names[i],scaled_sensitivity=rec['column_norms'][i],physical_step=SCALES[names[i]],qr_order=int(list(piv).index(i)),selected=names[i] in selected) for i in np.argsort(-np.array(rec['column_norms']))]
        save(self.out/'global-discovery.json',dict(ranking=ranking,selected=selected,couplings=rec['couplings'],singular_values=rec['singular_values'],interpretation='Scaled numerical responses, not statistical rank or identified physical constants. Turn and spacing are coupled by fixed integer count and total arclength.'))
        self.state['selected']=selected;self.state['baseline_id']=baseline['id'];self.checkpoint()
        pool=[baseline]+[r for r in candidates if self.guarded(r,baseline)]
        try:
            curves=[]
            specifications=[('phase',np.linspace(-np.pi,np.pi,19)),('s0',np.linspace(-13,13,15))]
            for name in [r['parameter'] for r in ranking if r['parameter'] not in ['phase','s0','turn']][:2]:specifications.append((name,np.array([-6,-3,0,3,6])*SCALES[name]))
            for name,values in specifications:
                rows=[]
                for value in values:
                    p=deepcopy(baseline['parameters']);p[name]+=float(value)
                    r=self.trial(p,None,f'curve:{name}:{value:.9g}');rows.append(dict(offset=float(value),trial=r['id'],feasible=r['feasible'],loss=r.get('result',{}).get('loss')))
                    if self.guarded(r,baseline):pool.append(r)
                minima=[r for i,r in enumerate(rows) if r['feasible'] and all(r['loss']<=rows[j]['loss'] for j in [i-1,i+1] if 0<=j<len(rows) and rows[j]['feasible'])]
                curves.append(dict(parameter=name,base=baseline['id'],rows=rows,minima=minima));save(self.out/'response-curves.json',curves)
            pairs=[('phase','s0')]
            strongest=next((r for r in rec['couplings'] if r['a'] in selected and r['b'] in selected and set([r['a'],r['b']])!=set(pairs[0])),None)
            if strongest:pairs.append((strongest['a'],strongest['b']))
            grids=[]
            for a,b in pairs:
                rows=[]
                for x in [-4,-2,0,2,4]:
                    for y in [-4,0,4]:
                        p=move(baseline['parameters'],[a,b],[x,y]);r=self.trial(p,None,f'pair:{a}:{b}:{x}:{y}')
                        rows.append(dict(x=x*SCALES[a],y=y*SCALES[b],trial=r['id'],loss=r.get('result',{}).get('loss'),feasible=r['feasible']))
                        if self.guarded(r,baseline):pool.append(r)
                grids.append(dict(a=a,b=b,base=baseline['id'],rows=rows));save(self.out/'response-pairs.json',grids)
            # Distinct coarse basins, not a monotonic walk through worse states.
            basins=[]
            for r in sorted(pool,key=lambda x:x['result']['loss']):
                if not basins or all(abs(r['parameters']['phase']-b['parameters']['phase'])>.12 or abs(r['parameters']['s0']-b['parameters']['s0'])>2 for b in basins):basins.append(r)
                if len(basins)==3:break
            save(self.out/'basins.json',[dict(trial=r['id'],parameters=r['parameters'],loss=r['result']['loss']) for r in basins])
            for i,basin in enumerate(basins):pool.append(self.descent(basin,selected,baseline,f'global-{i}'))
        except StageEnd:pass
        best=self.choose(pool,baseline);self.state['stages']['global']=dict(trial=best['id'],baseline=baseline['id'],elapsed=self.elapsed(),complete=True);self.checkpoint()
    def stage2(self):
        self.deadline=self.seconds*.79;base=read(self.out/'trials'/f"{self.state['stages']['global']['trial']:06d}.json.gz");reference=base['parameters']
        best=self.trial(reference,base['anchors'],'distributed-base',reference);guard=best
        self.state['correction_reference']=reference;self.state['distributed_base_id']=best['id'];self.checkpoint();rank=[]
        try:
            # Two-sided coordinate screens of global Fourier modes. No dense
            # 96-coefficient Jacobian; select only eight successful directions.
            for mode in [1,2,3,4]:
                for key in FIELD_SCALES:
                    for wave in ['sin','cos']:
                        name=f'{key}:{mode}:{wave}';rows=[]
                        for sign in [-1,1]:rows.append(self.trial(move(reference,[name],[sign]),base['anchors'],f'fourier:{name}:{sign}',reference))
                        good=[r for r in rows if self.guarded(r,guard)];r=min(good,key=lambda r:r['result']['loss']) if good else guard
                        rank.append(dict(name=name,best=r['id'],decrease=guard['result']['loss']-r['result']['loss']))
                        if r['result']['loss']<best['result']['loss']:best=r
                        save(self.out/'fourier-screen.json',rank)
            names=[r['name'] for r in sorted(rank,key=lambda r:-r['decrease'])[:8]]
            self.state['field_names']=names;self.checkpoint()
            for i in range(3):best=self.descent(best,names,guard,f'distributed-{i}',reference)
        except StageEnd:pass
        if 'field_names' not in self.state:self.state['field_names']=[r['name'] for r in sorted(rank,key=lambda r:-r['decrease'])[:6]]
        self.state['stages']['distributed']=dict(trial=best['id'],elapsed=self.elapsed(),complete=True);self.checkpoint()
    def stage3(self):
        self.deadline=self.seconds-3;reference=self.state['correction_reference'];guard=read(self.out/'trials'/f"{self.state['distributed_base_id']:06d}.json.gz")
        best=read(self.out/'trials'/f"{self.state['stages']['distributed']['trial']:06d}.json.gz");stale=0
        try:
            for i in range(20):
                names=self.state['selected'][:4]+self.state['field_names'][:4] if i%2==0 else self.state['selected'][4:]+self.state['field_names'][4:8]
                if not names:break
                new=self.descent(best,names,guard,f'joint-{i}',reference);stale=stale+1 if new['result']['loss']>=best['result']['loss']-1e-4 else 0;best=new
                self.state['stages']['joint']=dict(trial=best['id'],elapsed=self.elapsed());self.checkpoint()
                if stale>=4:self.state['stop_reason']='four complete joint blocks without improvement';break
        except StageEnd:pass
        self.state['stages']['joint']=dict(trial=best['id'],elapsed=self.elapsed(),complete=True);self.checkpoint()
    def run(self):
        try:
            for key,fn in [('global',self.stage1),('distributed',self.stage2),('joint',self.stage3)]:
                if not self.state['stages'].get(key,{}).get('complete'):fn()
            self.state.setdefault('stop_reason','three stages complete within budget')
        except Halt:self.state['stop_reason']='signal' if self.stop else 'budget'
        self.checkpoint();return self.state
