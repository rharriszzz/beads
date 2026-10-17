"""Limited translation and compact-field controls after causal diagnosis; no optical fit."""
import time
from copy import deepcopy
from collections import Counter
import numpy as np
from scipy.stats import qmc
from photo2.r297.common import ROOT,read,save,digest
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.geometry import contacts
from photo2.r314.objective import acceptance
from photo2.r314.diagnostics import EARLY
from photo2.r307.fast import grid
from .model import Chain,refined_trace
from .diagnose import OUT,brackets


def evaluate(p,data,e,oldcert=None):
    s=Chain(p,data);cert=oldcert or contacts(s,seconds=.4)
    row=dict(parameters=p,physical=cert,feasible=cert['certified'],classification=cert['classification'])
    if not cert['certified']:return row,s,None
    tr=s.trace(e.xy);ix=np.flatnonzero(tr['unknown'])
    if len(ix):
        rr=refined_trace(s,e.xy[ix]);tr['owner'][ix]=rr['owner'];tr['unknown'][ix]=rr['unknown']
    r=e.measure(tr['owner'],tr['unknown'],s.indices,0,True);bs=brackets(e,tr);bd=[b['displacement'] for b in bs if b['split']==0 and b['found']];r['bracket_finite_p95']=float(np.percentile(bd,95)) if bd else None;r['bracket_missing']=sum(b['split']==0 and not b['found'] for b in bs)
    early=[c for c in r['cores'] if c['id'] in EARLY];r['early_mean']=float(np.mean([c['modal_fraction'] for c in early]));r['early_min']=float(min(c['modal_fraction'] for c in early));row.update(development=r,compact_rate_bounds=s.compact_rate_bounds)
    return row,s,tr

def rank(r):
    if not r['feasible']:return (1e8,)
    z=r['development'];v=z['vector'];bb=z['bracket_finite_p95'] if z['bracket_finite_p95'] is not None else 1e4
    # Absolute errors only. No historical owner or two-point core loss veto in exploration.
    vals=[v['omission']/5,v['paper']/.5,v['seam']/10,v['worst']/3,bb/3,(1-z['early_min'])/.2]
    return tuple(sorted(vals,reverse=True))+(-z['early_mean'],)

def main():
    began=time.monotonic();deadline=began+240;data=load()[0];e=engine();trials=[];cache=set();baselines={};best={}
    def trial(p,label,parent,cert=None):
        key=digest(p)
        if key in cache:return None
        cache.add(key);t=time.monotonic()
        try:r,s,tr=evaluate(p,data,e,cert)
        except ValueError as ex:r=dict(parameters=p,feasible=False,classification='rate-bound',reason=str(ex));s=tr=None
        r.update(id=len(trials),experiment=label,parent=parent,seconds=time.monotonic()-t);small=deepcopy(r);small['physical'].pop('witnesses',None) if 'physical' in small else None;trials.append(small);save(OUT/'trials'/f'{r["id"]:04d}.json.gz',small)
        if r['feasible'] and (parent not in best or rank(r)<rank(best[parent])):
            best[parent]=r;print('BEST',r['id'],label,parent,rank(r),flush=True)
        return r
    names=['R306-2405','R313-focused-3','R312-local']
    for name in names:
        p=read(ROOT/f'photo2/r314/results/models/{name}.json.gz')['parameters'];r=trial(p,'baseline',name);baselines[name]=r
        for dx in [-8,-4,0,4,8]:
            for dy in [-8,-4,0,4,8]:
                if dx==dy==0:continue
                q=deepcopy(p);q['translation']=[dx,dy];trial(q,'translation-grid',name,r['physical'])
    # Controlled camera alternatives, shared geometry law and dimensions unchanged.
    p=baselines[names[0]]['parameters']
    for key,values in [('perspective',[0.,.0002,.0006]),('elevation',[40.,75.,85.]),('roll',[p['roll']-20,p['roll']+20]),('phase',[p['phase']-.3,p['phase']+.3]),('s0',[p['s0']-8,p['s0']+8])]:
        for value in values:
            q=deepcopy(p);q[key]=value;trial(q,'camera-placement-control:'+key,names[0])
    # Isolate representational addition before coupled refinement.
    compact_seed=deepcopy(best[names[0]]['parameters'])
    for field,amps in [('compact_phase',[-.2,-.1,.1,.2]),('compact_spacing',[-.01,-.005,.005,.01])]:
        for i in range(3):
            for amp in amps:
                q=deepcopy(compact_seed);q[field]=[0.,0.,0.];q[field][i]=amp;trial(q,'compact-one-direction',names[0])
    seed=deepcopy(best[names[0]]['parameters']);rng=np.random.default_rng(315)
    for n,z in enumerate(qmc.Sobol(10,scramble=True,seed=315).random_base2(7)*2-1):
        if time.monotonic()>deadline:break
        q=deepcopy(seed if n<64 else best[names[0]]['parameters']);factor=1. if n<64 else .25
        q['translation']=(np.array(q.get('translation',[0,0]))+z[:2]*4*factor).tolist();q['phase']+=z[2]*.2*factor;q['s0']+=z[3]*4*factor
        q['compact_phase']=(np.array(q.get('compact_phase',[0]*3))+z[4:7]*.18*factor).tolist();q['compact_spacing']=(np.array(q.get('compact_spacing',[0]*3))+z[7:]*.007*factor).tolist()
        if max(abs(np.array(q['translation'])))>12:continue
        trial(q,'compact-coupled',names[0])
    selected=[]
    # Include best translation-only and best new compact experiment, regardless of adoption.
    choices=[('baseline',baselines[names[0]])]
    translations=[r for r in trials if r['experiment']=='translation-grid' and r['parent']==names[0] and r['feasible']]
    choices.append(('translation',min(translations,key=rank)));choices.append(('compact',best[names[0]]))
    for name,row in choices:
        r,s,tr=evaluate(row['parameters'],data,e);r.update(name=name,trial_id=row['id']);assert r['feasible'];r['comparison']=e.measure(tr['owner'],tr['unknown'],s.indices,1,True);r['buffer']=e.measure(tr['owner'],tr['unknown'],s.indices,2,True)
        r['historical_acceptance']={k:acceptance(r[k],baselines[names[0]][k] if k=='development' else read(ROOT/f'photo2/r314/results/models/{names[0]}.json.gz')[k]) for k in ['development','comparison']}
        r['positions']=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),frames={k:v.tolist() for k,v in s.g.items()},projected=s.pc.tolist());ix=np.flatnonzero((s.indices>=-100)&(s.indices<=99));xy=grid(s,1.,ix);full=refined_trace(s,xy);r['target']=dict(count=len(ix),rays=len(xy),unknown=int(full['unknown'].sum()),visible_counts=[dict(index=int(s.indices[j]),pixels=int(np.sum(full['owner']==j))) for j in ix]);np.savez_compressed(OUT/f'{name}-target.npz',xy=xy,owner=full['owner'],unknown=full['unknown']);np.savez_compressed(OUT/f'{name}-raster.npz',owner=tr['owner'],unknown=tr['unknown']);save(OUT/f'{name}-model.json.gz',r);save(OUT/f'{name}-brackets.json.gz',brackets(e,tr));selected.append(dict(name=name,id=row['id'],rank=rank(r),parameters=r['parameters'],development=r['development'],comparison=r['comparison'],target=r['target']))
    save(OUT/'experiment.json.gz',dict(seconds=time.monotonic()-began,trials=len(trials),classifications=dict(Counter(r['classification'] for r in trials)),experiment_counts=dict(Counter(r['experiment'] for r in trials)),selected=selected,all_trial_ids=[r['id'] for r in trials],scope='3 saved count/hand/topology families translation; camera controls and new compact fields on R306 only; no optical fit or count/hand search',rank_policy='Lexicographic sorted absolute geometric violations; known paper, seam, fragmentation, bracket and material errors cannot disappear in weighted coverage sum. Historical conjunction reported separately; no adoption.'))
if __name__=='__main__':main()
