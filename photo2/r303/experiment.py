"""One sealed <=600s numerical campaign: S1, frozen-shape transfer, shared fit."""
import json
import subprocess
import time
import numpy as np
from .core import *
from photo2.r302.experiment import clean,compact
from photo2.r301.experiment import historical_start

def freeze():
    if (BASE/'evidence/protocol.json').exists():raise RuntimeError('Already frozen')
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    protected={p:sha(ROOT/p) for p in paths if p and (p.startswith('photo2/') or p in ['beads.pov','beads-photo-2.jpg'])}
    for p in (ROOT/'photo2').glob('r*/feedback/**/*'):
        if p.is_file():protected[str(p.relative_to(ROOT))]=sha(p)
    save(BASE/'evidence/preservation.json.gz',protected)
    sections=deepcopy(read(ROOT/'photo2/r301/evidence/frozen.json.gz')['sections'])
    sep=read(ROOT/'photo2/r301/evidence/withheld-separators.json')['sections']
    for s,r in zip(sections,sep):s['diagnostic_separators']=r['records']
    save(BASE/'evidence/sections.json.gz',sections)
    starts=[]
    for hand,label in [(-1,'minus'),(1,'plus')]:
        r=read(ROOT/f'photo2/r302/results/native-hierarchy-historical-{label}.json.gz')['result']['parameters']
        v=[r[n] for n in NAMES]
        for mode in MODES:
            starts.append(dict(name=f'{mode}-h{hand}',hand=hand,mode=mode,parameters=encode(v,mode).tolist()))
    p=dict(utc=utc(),starts=starts,source_c=.65*1.05/.70,numerical_cap=600,
       allocation='S1 six x38s; transfer twelve x15s; joint six x13s; two-sided S1 sensitivity six starts charged; final sensitivity charged if time remains. Global deadline580s leaves20s call reserve.',
       sequence='Seal S1 selection before S2/S3 training; fixed shared geometry/camera/light transfer with local axis/phase/spacing only; then short joint training refinement. Withheld reflections/material/valleys evaluated only after final seal.',
       selection='For each family/hand retain best no-flag training model if available, else fewest contradiction flags then lowest common objective. Keep loss-only winner too. No selection on withheld.',
       uncertainty='Retrospective frozen R301 evidence; uncertain contours, correlated cue pixels, no verified physical indices. No statistical confidence claims.',
       pitch='Radius=1; H=2*axial; p=c*H/turn. Local ds/dk=p*(1+spacing*tanh(k/14)); ±2% exploration scale, not a mechanical law or string strain. No count gate.',
       coefficient='Free c is an invertible parameterization of free pitch at fixed positive H and turn; common physical pitch interval .035.. .4 retained in all families. Broad c .1..16.3 includes its entire implied range. Source c=.975 fixed.',
       objective='Identical R302 S1 native reflection/dimension/contour/material objective without density gate. S2/S3 use their frozen envelope endpoints as an additional grouped squared boundary block with4px contradiction threshold. No invented individual dimensions where absent.',
       bounds={m:bounds(m).tolist() for m in MODES},steps={m:steps(m).tolist() for m in MODES},
       shared=list(NAMES[:12]),local=list(NAMES[12:]),sources={str(p.relative_to(ROOT)):sha(p) for p in BASE.glob('*.py')})
    save(BASE/'evidence/protocol.json',p)

def fit(name,initial,sections,hand,mode,seconds,diag,active=None):
    began=time.monotonic();deadline=began+seconds;rng=np.random.default_rng(30300+sum(map(ord,name)))
    # A joint vector has common12 plus six independent local variables/region.
    lo=np.r_[bounds(mode)[:12,0],np.tile(bounds(mode)[12:,0],len(sections))]
    hi=np.r_[bounds(mode)[:12,1],np.tile(bounds(mode)[12:,1],len(sections))]
    st=np.r_[steps(mode)[:12],np.tile(steps(mode)[12:],len(sections))]
    norms=np.r_[diag['column_norms'][:12],np.tile(diag['column_norms'][12:],len(sections))]
    scales=st/np.maximum(1,norms/3)
    active=list(np.flatnonzero(st>0)) if active is None else active
    best=np.array(initial[0]);bestkey=(10**6,np.inf);lossbest=best.copy();minloss=np.inf;history=[]
    def trial(q,stage):
        nonlocal best,bestkey,lossbest,minloss
        if time.monotonic()>=deadline: return False
        q=np.clip(q,lo,hi);out=[]
        for i,s in enumerate(sections):out.append(evaluate(np.r_[q[:12],q[12+6*i:18+6*i]],s,hand,mode))
        loss=float(np.mean([e['loss'] for e in out]));count=sum(len(e.get('flags',['uncertified'])) for e in out)
        key=(sum(not e['feasible'] for e in out)*100+count,loss)
        history.append(dict(parameters=q.tolist(),elapsed=time.monotonic()-began,stage=stage,loss=loss,selection_key=list(key),sections=[compact(e) for e in out]))
        if key<bestkey:best=q.copy();bestkey=key
        if loss<minloss:minloss=loss;lossbest=q.copy()
        return True
    for q in initial:
        if not trial(q,'initial'):break
    # Same sensitivity-scaled hierarchical coordinate and coupled SVD moves as
    # R302. Earlier dimensions reopen in joint stage; no permanent fixing there.
    groups=[[0,7,8,9,12,13],[0,3,4,5,6,9,10,11,16],[4,12,13,14,15,16,17],active]
    iteration=0;radius=1.
    while time.monotonic()<deadline:
        fraction=(time.monotonic()-began)/seconds
        ids=groups[min(3,int(fraction*4))] if len(sections)==1 and active!=list(range(12,18)) else active
        ids=[j for j in ids if j in active];origin=best.copy();before=bestkey;directions=[]
        for j in sorted(ids,key=lambda j:-norms[j]):
            d=np.zeros(len(best));d[j]=scales[j];directions.append(d)
        if fraction>.5:
            for z in np.array(diag['right_vectors']):
                d=np.zeros(len(best));d[:18]=steps(mode)*z/max(1,np.linalg.norm(z*np.array(diag['column_norms']))/3)
                d[[j for j in range(len(d)) if j not in active]]=0
                directions.append(d)
        for d in directions:
            for sign in [-1,1]:
                if not trial(origin+sign*radius*d,'hierarchy'):break
            if time.monotonic()>=deadline:break
        radius=radius*.65 if bestkey>=before else min(1.5,radius*1.1)
        if radius<.2:
            q=best.copy();q[active]+=scales[active]*rng.normal(0,1.2,len(active));trial(q,'coupled-restart');radius=.6
        iteration+=1
        if not directions:break
    result=dict(name=name,mode=mode,hand=hand,best=best.tolist(),bestkey=list(bestkey),loss_winner=lossbest.tolist(),minimum_loss=minloss,history=history,elapsed=time.monotonic()-began,seconds=seconds,active=active)
    save(BASE/f'results/{name}.json.gz',clean(result));print(name,'key',bestkey,'calls',len(history),'seconds',round(result['elapsed'],2),flush=True)
    return result

def run():
    if (BASE/'results/started.json').exists():raise RuntimeError('Single-use campaign already started')
    p=read(BASE/'evidence/protocol.json');ss=read(BASE/'evidence/sections.json.gz');began=time.monotonic();deadline=began+580
    save(BASE/'results/started.json',dict(utc=utc(),sources=p['sources']))
    diagnostics={};s1=[];transfers=[];joint=[]
    for start in p['starts']:
        name=start['name'];mode=start['mode'];hand=start['hand'];v=np.array(start['parameters'])
        d=sensitivity(v,ss[0],hand,mode);diagnostics[name]=clean(d);save(BASE/'results/sensitivity-starts.json.gz',diagnostics)
        alt=encode(historical_start(ss[0],hand),mode);alt=np.clip(alt,*bounds(mode).T);alt[17]=0
        r=fit('S1-'+name,[v,alt],ss[:1],hand,mode,min(38,max(0,deadline-time.monotonic())),d)
        s1.append(r)
    save(BASE/'results/S1-freeze.json',dict(utc=utc(),models=[{k:r[k] for k in ['name','mode','hand','best','bestkey','loss_winner']} for r in s1]))
    for r in s1:
        name=r['name'][3:];d=diagnostics[name]
        for s in ss[1:]:
            # Local historical seeds do not transfer previous region geometry.
            v=np.array(r['best']);oldv=historical_start(s,r['hand']);v[12:]=oldv[12:];v[17]=0
            oldjoint=read(ROOT/f'photo2/r301/results/native-joint-h{r["hand"]}-{s["id"]}.json.gz')['result']['parameters']
            alt=v.copy();alt[12:]=[oldjoint[n] for n in NAMES[12:]];alt[17]=0
            candidates=[v,alt]
            for phase in [-np.pi,-np.pi/2,0,np.pi/2]:
                q=v.copy();q[16]=phase;candidates.append(q)
            transfers.append(fit(f'transfer-{s["id"]}-{name}',candidates,[s],r['hand'],r['mode'],min(15,max(0,deadline-time.monotonic())),d,active=list(range(12,18))))
    save(BASE/'results/transfer-freeze.json',dict(utc=utc(),models=[{k:r[k] for k in ['name','mode','hand','best','bestkey']} for r in transfers]))
    for r in s1:
        name=r['name'][3:];t=[a for a in transfers if a['name'].endswith(name)];v=np.r_[r['best'],t[0]['best'][12:],t[1]['best'][12:]]
        joint.append(fit('joint-'+name,[v],ss,r['hand'],r['mode'],min(13,max(0,deadline-time.monotonic())),diagnostics[name]))
    # Remaining numerical time is spent only on final S1 local sensitivity, never
    # on another fit or withheld selection. Start only if ~8s remains.
    finaldiag={}
    for r in s1:
        if deadline-time.monotonic()<10:break
        d=sensitivity(r['best'],ss[0],r['hand'],r['mode']);finaldiag[r['name']]=clean(d)
        save(BASE/'results/sensitivity-final.json.gz',finaldiag)
    selected=[]
    for stage,runs in [('S1',s1),('transfer',transfers),('joint',joint)]:
        for r in runs:
            sections=ss if stage=='joint' else [ss[0] if stage=='S1' else next(s for s in ss if s['id'] in r['name'])]
            for i,s in enumerate(sections):
                v=np.r_[r['best'][:12],r['best'][12+6*i:18+6*i]]
                selected.append(dict(name=r['name']+(('-'+s['id']) if stage=='joint' else ''),stage=stage,mode=r['mode'],hand=r['hand'],section=s['id'],parameters=v.tolist()))
    save(BASE/'results/fit-freeze.json',dict(utc=utc(),numerical_seconds=time.monotonic()-began,selected=selected,protocol_sha256=sha(BASE/'evidence/protocol.json'),sources={str(p.relative_to(ROOT)):sha(p) for p in BASE.glob('*.py')},policy='No further fitting. All stages selected before comparison reflections, held cue bands and dark valleys.'))
    print('SEALED',round(time.monotonic()-began,2),'seconds',flush=True)

if __name__=='__main__':
    import sys
    {'freeze':freeze,'run':run}[sys.argv[1]]()
