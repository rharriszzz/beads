"""Adaptive final joint trust radii, charged to the same cumulative fit budget.

An inadmissible missing-lobe side remains a scored trial but cannot furnish a
local derivative for a constraint-preserving step. It is marked unavailable,
never interpreted as zero photographic information.
"""
from pathlib import Path
import numpy as np
from photo2.r297.common import read,save,utc,digest
from .search import Runner,move,Halt,StageEnd

class CachedRunner(Runner):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.native_cache={}
    def trial(self,p,anchors,tag,reference=None):
        # Reuse complete native results only at exactly identical parameters,
        # assignments and regularization reference within this adaptive process.
        key=digest(dict(parameters=p,anchors=anchors,reference=reference))
        if key not in self.native_cache:
            r=super().trial(p,anchors,tag,reference);self.native_cache[key]=r;return r
        replay_key=digest(dict(p=p,anchors=anchors,tag=tag,reference=reference))
        if replay_key in self.state['cache']:return read(self.out/'trials'/f"{self.state['cache'][replay_key]:06d}.json.gz")
        self.check();original=self.native_cache[key];r=dict(original,id=self.state['next_id'],tag=tag,seconds=0.,elapsed=self.elapsed(),cache_hit=original['id'])
        save(self.out/'trials'/f"{r['id']:06d}.json.gz",r);self.state['cache'][replay_key]=r['id'];self.state['next_id']+=1;self.checkpoint();return r

def run(out,seconds=1200,max_evaluations=100000):
    out=Path(out);runner=CachedRunner(out,seconds,True,max_evaluations);s=runner.state
    if s.get('adaptive_complete'):return s
    if not all(k in s['stages'] for k in ['global','distributed','joint']):return s
    runner.deadline=seconds-3
    reference=s['correction_reference'];guard=read(out/'trials'/f"{s['distributed_base_id']:06d}.json.gz")
    best=read(out/'trials'/f"{s['stages']['joint']['trial']:06d}.json.gz")
    guard=runner.trial(guard['parameters'],guard['anchors'],'corrected-objective-reference',reference)
    s['distributed_base_id']=guard['id']
    best=runner.trial(best['parameters'],best['anchors'],'corrected-objective-incumbent',reference)
    s.setdefault('adaptive_started',dict(utc=utc(),elapsed=runner.elapsed(),protocol='Final joint radii .2,.05,.0125 of declared scales, then .05,.0125,.003125 if budget remains; no new sweep, evidence or objective change. Derivative sides adding missing assigned lobes are inadmissible; all scored trials retained.'))
    runner.checkpoint()
    try:
        for cycle,radius in enumerate([.2,.05,.0125,.05,.0125,.003125]):
            tag=f'corrected-adaptive-joint-{cycle}'
            base=runner.trial(best['parameters'],best['anchors'],tag+':base',reference);v=np.array(base['residual'])
            names=s['selected']+(s['field_names'][:4] if cycle%2==0 else s['field_names'][4:8]);cols=[];rows=[base];methods=[];trial_ids=[]
            for name in names:
                valid=[]
                for sign in [-1,1]:
                    r=runner.trial(move(base['parameters'],[name],[sign*radius]),base['anchors'],f'{tag}:{name}:{sign}',reference);trial_ids.append(r['id']);rows.append(r)
                    if r['feasible'] and r['result']['unmatched']<=base['result']['unmatched']:valid.append((sign,np.array(r['residual'])))
                if len(valid)==2:d=(valid[1][1]-valid[0][1])/(2*radius);method='central'
                elif valid:d=(valid[0][1]-v)/(valid[0][0]*radius);method='one-sided no added missing lobe'
                else:d=np.zeros_like(v);method='unavailable: both sides violate missing-lobe guard'
                cols.append(d);methods.append(method)
            J=np.array(cols).T;u,sv,vt=np.linalg.svd(J,full_matrices=False)
            save(out/'sensitivities'/f'{tag}.json.gz',dict(names=names,radius=radius,methods=methods,base=base['id'],trials=trial_ids,residual=v.tolist(),jacobian=J.tolist(),singular_values=sv.tolist(),right_vectors=vt.tolist(),column_norms=np.linalg.norm(J,axis=0).tolist()))
            for damp in [.1,.5]:
                lam=max(1e-4,(sv[0]*damp)**2);z=-(vt.T*(sv/(sv*sv+lam)))@(u.T@v);z/=max(1,abs(z).max()/(2*radius))
                for factor in [1.,.3]:
                    r=runner.trial(move(base['parameters'],names,z*factor),base['anchors'],f'{tag}:LM:{damp}:{factor}',reference)
                    predicted=float(v@v-np.sum((v+J@(z*factor))**2));actual=base['result']['loss']-r['result']['loss'] if r['feasible'] else None
                    save(out/'predictions'/f"{r['id']:06d}.json",dict(id=r['id'],base=base['id'],predicted=predicted,actual=actual,ratio=actual/predicted if actual is not None and predicted>0 else None,radius=radius,damping=lam,step=(z*factor).tolist()))
                    if r['feasible'] and predicted>0 and actual>0 and actual/predicted>.03:rows.append(r)
            chosen=runner.choose(rows,guard)
            if chosen['result']['loss']<best['result']['loss']-1e-5:
                s['accepted'].append(dict(stage=tag,trial=chosen['id'],base=best['id'],decrease=best['result']['loss']-chosen['result']['loss'],elapsed=runner.elapsed()));best=chosen
            s['stages']['joint']=dict(trial=best['id'],elapsed=runner.elapsed(),complete=True,adaptive=True);runner.checkpoint()
    except (Halt,StageEnd):pass
    s['adaptive_complete']=not runner.stop;s['stop_reason']='signal' if runner.stop else 'adaptive joint budget' if runner.elapsed()>=seconds-3 else 'adaptive radii completed'
    s['stages']['joint']=dict(trial=best['id'],elapsed=runner.elapsed(),complete=True,adaptive=True);runner.checkpoint();return s
