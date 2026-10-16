"""Single-use, clock-bounded experiment. No automatic second experiment/resume."""
import argparse
import json
import subprocess
import time
from copy import deepcopy
import numpy as np
from scipy.stats import spearmanr
from .core import *
from photo2.r301.experiment import historical_start
from photo2.r301.model import predict as old_predict
from photo2.r301.export import full_predict
from photo2.r297.common import environment, run_lock

def clean(value):
    if isinstance(value,np.ndarray):return clean(value.tolist())
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean(v) for v in value]
    if isinstance(value,(float,np.floating)):return float(value) if np.isfinite(value) else None
    if isinstance(value,np.integer):return int(value)
    return value

def freeze():
    path=BASE/'evidence/protocol.json'
    if path.exists():return read(path)
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    protected={p:sha(ROOT/p) for p in paths if p and (p.startswith('photo2/') or p in ['beads.pov','beads-photo-2.jpg'])}
    for p in (ROOT/'photo2').glob('r*/feedback/**/*'):
        if p.is_file():protected[str(p.relative_to(ROOT))]=sha(p)
    save(BASE/'evidence/preservation.json.gz',protected)
    s=deepcopy(read(ROOT/'photo2/r301/evidence/frozen.json.gz')['sections'][0])
    s['diagnostic_separators']=read(ROOT/'photo2/r301/evidence/withheld-separators.json')['sections'][0]['records']
    save(BASE/'evidence/section.json.gz',s)
    starts=[]
    for name,hand in [('historical-minus',-1),('historical-plus',1),('S1-h1-accurate1',1),('joint-h1-S1',1)]:
        original=historical_start(s,hand) if name.startswith('historical') else [read(ROOT/f'photo2/r301/results/native-{name}.json.gz')['result']['parameters'][n] for n in NAMES]
        v=np.clip(original,*bounds().T);v[17]=0.
        c=Scene(v,s,hand);count=int(np.sum(abs((c.project(c.line)-s['center'])@s['tangent'])<=s['halfspan']))
        if count>30:v[4]*=count/29.
        v=np.clip(v,*bounds().T)
        starts.append(dict(name=name,hand=hand,original=original,parameters=v.tolist(),adaptation='New constant-turn count2000 bound; spacing reset to zero for bounded arclength model; pitch increased by old count/29 if >30 positions. No photo outcomes used.'))
    protocol=dict(utc=utc(),section='S1',conditional_total_count=2000,twist_formula='abs(N*(6.5/turn-1)) <= 6.5',turn_bounds=twist_bounds(2000),numerical_seconds=600,starts=starts,steps=STEPS.tolist(),bounds=bounds().tolist(),seed=30201,
        evidence='Identical R301 S1 ten reflections (7 train/3 retrospective comparison), B15 uncertain visible contour (2 extents/8 dependent vertices), 194 spatially correlated material/paper samples. Four dark valleys and held cue bands remain diagnostics. No reliable transverse width or verified neighbor indices.',
        acceptance='15..30 positions, extended local separation, extent MAE<=3px, visible contour boundary MAE<=4px, paper<=10%, color omission<=23%, all training reflections matched. Engineering contradiction flags, not calibrated truth or full necklace acceptance.',
        budget='Predictor audit and sensitivity charged first; remaining numerical budget minus20s reserve divided equally between hierarchy and accurate-DE controls, four identical starts each. No coarse screen after audit. Final native export/verification is evaluation only; no tuning.',
        hierarchy='Dimensions/projection -> helix/phase/tilt -> centerline and bounded local extension -> joint coupled refinement. Shared light is nuisance, retained in reflection stages. All parameters can reopen at joint stage. Sensitivity SVD and strongest cross-block correlations provide joint proposal directions; weak columns damped.',
        objective='R301 robust squared reflection assignment + grouped squared extents/visible boundary + equal material/background blocks and contradiction barriers. No pixel sample count is an information count.',
        sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((BASE).glob('*.py'))},environment=environment())
    save(path,protocol);return protocol

def diagnose():
    if (BASE/'results/diagnosis.json.gz').exists():raise RuntimeError('Diagnostic already delivered; no overwrite')
    protocol=freeze();s=read(BASE/'evidence/section.json.gz');began=time.monotonic();audit=[];sens=[];rng=np.random.default_rng(30200)
    for start in protocol['starts']:
        v=np.array(start['parameters']);hand=start['hand'];scene=Scene(v,s,hand)
        # Baseline plus deterministic single-parameter and paired variations;
        # no candidate is selected for a good score in either predictor.
        variants=[v]
        for ids in [[0],[3],[4],[7],[9],[16],[0,9],[3,4]]:
            q=v.copy();q[ids]+=STEPS[ids]*rng.choice([-1,1],len(ids));variants.append(np.clip(q,*bounds().T))
        for number,q in enumerate(variants):
            sc=Scene(q,s,hand);cert=sc.certify(iterations=100,witnesses=False)
            row=dict(start=start['name'],number=number,parameters=q.tolist(),physical=cert)
            if cert['certified']:
                predictions={};scores={};timings={}
                for mode in ['coarse','two-pixel','native']:
                    t=time.perf_counter();p,_=old_predict(sc,s,0) if mode=='coarse' else native(sc,s,2. if mode=='two-pixel' else 1.)
                    timings[mode]=time.perf_counter()-t;predictions[mode]=p
                    scores[mode]=assignment(p,[r for r in s['observations'] if r['split']=='train'],s)['loss']
                truth={p['index']:p for p in predictions['native']};errors={}
                for mode in ['coarse','two-pixel']:
                    other={p['index']:p for p in predictions[mode]}
                    common=sorted(set(truth)&set(other));dist=[np.linalg.norm(np.array(truth[k]['point'])-other[k]['point']) for k in common]
                    errors[mode]=dict(common=len(common),missing=sorted(set(truth)-set(other)),extra=sorted(set(other)-set(truth)),rms=float(np.sqrt(np.mean(np.square(dist)))) if dist else None,max=max(dist,default=None))
                row.update(scores=scores,timings=timings,errors=errors,predictions=predictions)
                if number==0:
                    t=time.perf_counter();p,_=full_predict(sc,s,light_params([q[10],q[11],10.],'directional',sc.centers.mean(0)));old={z['index']:z for z in p}
                    row['full_predict_equivalence']=dict(seconds=time.perf_counter()-t,missing=sorted(set(truth)-set(old)),extra=sorted(set(old)-set(truth)),max_common_difference=max([np.linalg.norm(np.array(truth[k]['point'])-old[k]['point']) for k in set(truth)&set(old)],default=None))
            audit.append(row)
        pred,raster=native(scene,s);match=assignment(pred,[r for r in s['observations'] if r['split']=='train'],s)
        anchors=dict(reflection=[(r['id'],r['index']) for r in match['records'] if r['index'] is not None],neighbors=[-6,0,6])
        y,labels,groups,sigma,sec=feature_vector(scene,s,pred,raster,anchors)
        derivatives=[];perturbations=[];valid=[]
        for j,name in enumerate(NAMES):
            sides=[]
            for sign in [-1,1]:
                q=v.copy();q[j]=np.clip(q[j]+sign*STEPS[j],*bounds()[j]);sc=Scene(q,s,hand);cert=sc.certify(iterations=100,witnesses=False)
                pp,rr=native(sc,s);yy,_,_,_,metrics=feature_vector(sc,s,pp,rr,anchors)
                sides.append((q[j]-v[j],yy,cert['certified']))
                perturbations.append(dict(parameter=name,sign=sign,parameters=q.tolist(),physical=cert,values=yy,metrics=metrics))
            lo,hi=sides
            if lo[2] and hi[2]:d=(hi[1]-lo[1])/(hi[0]-lo[0])*STEPS[j];method='central'
            elif hi[2]:d=(hi[1]-y)/hi[0]*STEPS[j];method='forward'
            elif lo[2]:d=(lo[1]-y)/lo[0]*STEPS[j];method='backward'
            else:d=np.full_like(y,np.nan);method='unavailable: both sides uncertified'
            derivatives.append(d);valid.append(method)
        J=np.array(derivatives).T/sigma[:,None]
        data=np.array([g!='prediction_only' for g in groups]);finite=np.all(np.isfinite(J),axis=1)&data
        A=J[finite];u,sv,vt=np.linalg.svd(A,full_matrices=False)
        refl=np.array([g=='reflection' for g in groups])&finite
        norms=np.linalg.norm(A,axis=0);corr=A.T@A/np.maximum(norms[:,None]*norms[None,:],1e-15)
        pairs=sorted([(abs(corr[a,b]),a,b) for a in range(18) for b in range(a+1,18)],reverse=True)[:5]
        combinations=[]
        for _,a,b in pairs[:3]:
            direction=np.zeros(18);direction[a]=1;direction[b]=-np.sign(corr[a,b])*norms[a]/max(norms[b],1e-8);direction/=max(1,np.max(abs(direction)))
            q=np.clip(v+STEPS*direction,*bounds().T);sc=Scene(q,s,hand);pp,rr=native(sc,s);yy,*_=feature_vector(sc,s,pp,rr,anchors)
            combinations.append(dict(parameters=q.tolist(),direction=direction.tolist(),pair=[NAMES[a],NAMES[b]],physical=sc.certify(iterations=100,witnesses=False),actual_standardized=(yy-y)/sigma,predicted_standardized=J@direction))
        record=dict(start=start,anchors=anchors,labels=labels,groups=groups,scales=sigma,values=y,jacobian=J,derivative_method=valid,finite_data_rows=int(finite.sum()),singular_values=sv,right_vectors=vt,reflection_singular_values=np.linalg.svd(J[refl],compute_uv=False),column_norms=norms,
            group_norms={g:np.linalg.norm(np.nan_to_num(J[np.array(groups)==g]),axis=0) for g in sorted(set(groups))},coupled_pairs=[dict(a=NAMES[a],b=NAMES[b],cosine=corr[a,b]) for _,a,b in pairs],perturbations=perturbations,combinations=combinations,base_physical=scene.certify(iterations=100,witnesses=False))
        sens.append(clean(record));save(BASE/'results/sensitivity-progress.json.gz',sens)
        print('Sensitivity',start['name'],'singular values',np.round(sv,2),'elapsed',round(time.monotonic()-began,1),flush=True)
    accepted=[r for r in audit if 'scores' in r];native_scores=np.array([r['scores']['native'] for r in accepted]);rank={}
    k=max(1,int(np.ceil(len(accepted)/4)));truth=set(np.argsort(native_scores)[:k])
    for mode in ['coarse','two-pixel']:
        scores=np.array([r['scores'][mode] for r in accepted]);chosen=set(np.argsort(scores)[:k]);best=int(np.argmin(scores))
        rank[mode]=dict(spearman=float(spearmanr(scores,native_scores).statistic),top_quartile_recall=len(chosen&truth)/k,k=k,best_native_loss=float(native_scores[best]),best_possible_native_loss=float(native_scores.min()),median_seconds=float(np.median([r['timings'][mode] for r in accepted])))
    rank['native_median_seconds']=float(np.median([r['timings']['native'] for r in accepted]))
    result=clean(dict(utc=utc(),seconds=time.monotonic()-began,audit=audit,sensitivity=sens,ranking=rank,decision='Use full native first-hit and shadow predictions for every fitted feasible candidate. No coarse or two-pixel score screens or rejects any candidate.'))
    save(BASE/'results/diagnosis.json.gz',result);print(json.dumps(rank),flush=True)

def compact(ev):
    result={k:v for k,v in ev.items() if k not in ['predictions','train']}
    if ev['feasible']:
        result['secondary']={k:v for k,v in ev['secondary'].items() if k not in ['neighbors']}
        result['assignments']=[dict(id=r['id'],index=r['index'],error=r['error']) for r in ev['train']['records']]
    return result

class TimeUp(Exception):pass

def fit_one(start,s,sensitivity,method,seconds,seed):
    began=time.monotonic();deadline=began+seconds;rng=np.random.default_rng(seed);lo,hi=bounds().T
    v0=np.array(start['parameters']);best=v0.copy();bestloss=np.inf;history=[];schedule=[]
    norms=np.array(sensitivity['column_norms']);scales=STEPS/np.maximum(1,norms/3.)
    # Sensitivity damps violent columns; weak parameters do not gain unlimited
    # freedom. Eigenvectors expose compensating moves across earlier stage groups.
    vectors=np.array(sensitivity['right_vectors'])
    def trial(v,stage):
        nonlocal best,bestloss
        if time.monotonic()>=deadline:raise TimeUp
        v=np.clip(v,lo,hi);ev=evaluate(v,s,start['hand']);loss=ev['loss']
        history.append(dict(i=len(history),elapsed=time.monotonic()-began,parameters=v.tolist(),stage=stage,**compact(ev)))
        if loss<bestloss:bestloss=loss;best=v.copy()
        if len(history)%32==0:save(BASE/f'results/{method}-{start["name"]}-progress.json.gz',dict(history=history,best=best.tolist(),rng=rng.bit_generator.state))
        return loss
    try:
        trial(v0,'initial')
        if method=='hierarchy':
            stages=[('dimensions-camera',[0,7,8,9,12,13],.22),('helix',[0,3,4,5,6,9,10,11,16],.25),('axis-extension',[4,12,13,14,15,16,17],.18),('joint',list(range(18)),.35)]
            for stage,ids,fraction in stages:
                end=min(deadline,time.monotonic()+seconds*fraction);iteration=0;radius=1.
                schedule.append(dict(stage=stage,ids=ids,started=time.monotonic()-began))
                while time.monotonic()<end:
                    before=bestloss;origin=best.copy();directions=[]
                    # Highest-information columns first; correlated pairs and
                    # SVD directions update multiple coupled parameters together.
                    for j in sorted(ids,key=lambda j:-norms[j]):
                        d=np.zeros(18);d[j]=scales[j];directions.append(d)
                    for pair in sensitivity['coupled_pairs']:
                        a,b=NAMES.index(pair['a']),NAMES.index(pair['b'])
                        if a in ids and b in ids:
                            d=np.zeros(18);d[a]=scales[a];d[b]=-np.sign(pair['cosine'])*scales[b];directions.append(d)
                    if stage=='joint':
                        directions.extend([STEPS*z/max(1,float(np.linalg.norm(z*norms))/3) for z in vectors])
                    for d in directions:
                        if time.monotonic()>=end:break
                        for sign in [-1,1]:trial(origin+sign*radius*d,stage)
                    if bestloss>=before-1e-6:radius*=.6
                    else:radius=min(1.5,radius*1.1)
                    if radius<.18:
                        # Targeted restart within an identified coupling, not an
                        # uninformed draw over 18 independent wide intervals.
                        for _ in range(4):
                            z=vectors[rng.integers(len(vectors))];trial(best+STEPS*z*rng.normal(0,1.5),stage+'-coupled-restart')
                        radius=.5
                    iteration+=1
        else:
            # R301-style local population DE, now using the reliable predictor,
            # new constraints and IDENTICAL objective to isolate search strategy.
            population=np.clip(v0+rng.normal(0,1,(24,18))*STEPS*2,lo,hi);population[0]=v0;scores=np.full(24,np.inf)
            for i in range(24):scores[i]=trial(population[i],'DE-initial')
            i=0
            while True:
                k=i%24;a,b,c=rng.choice([j for j in range(24) if j!=k],3,replace=False)
                mutant=population[a]+rng.uniform(.45,.95)*(population[b]-population[c]);cross=rng.random(18)<.8;cross[rng.integers(18)]=True
                q=np.clip(np.where(cross,mutant,population[k]),lo,hi);loss=trial(q,'DE')
                if loss<scores[k]:population[k]=q;scores[k]=loss
                i+=1
    except TimeUp:pass
    result=dict(method=method,start=start,seed=seed,budget_seconds=seconds,elapsed=time.monotonic()-began,best=best.tolist(),bestloss=bestloss,history=history,schedule=schedule,scales=scales.tolist())
    save(BASE/f'results/{method}-{start["name"]}.json.gz',result)
    print(method,start['name'],len(history),'loss',round(bestloss,3),'seconds',round(result['elapsed'],2),flush=True)
    return result

def fit():
    if (BASE/'results/fit-freeze.json').exists():raise RuntimeError('R302 already sealed; no additional fitting')
    protocol=read(BASE/'evidence/protocol.json');diag=read(BASE/'results/diagnosis.json.gz');s=read(BASE/'evidence/section.json.gz')
    remaining=protocol['numerical_seconds']-diag['seconds']-20
    if remaining<=0:raise RuntimeError('Diagnostics consumed budget; report blocker, do not expand')
    seconds=remaining/8;results=[]
    save(BASE/'results/allocation.json',dict(utc=utc(),diagnostic_seconds=diag['seconds'],per_run_seconds=seconds,methods=2,starts=4,cap=600,reserve_seconds=20))
    with run_lock(BASE/'results'):
        for i,start in enumerate(protocol['starts']):
            for method in ['hierarchy','accurate-DE']:
                results.append(fit_one(start,s,diag['sensitivity'][i],method,seconds,30210+i))
        chosen=[]
        for r in results:
            # Retain the predeclared best from EACH start, including failures.
            chosen.append(dict(name=r['method']+'-'+r['start']['name'],hand=r['start']['hand'],parameters=r['best'],loss=r['bestloss'],elapsed=r['elapsed'],evaluations=len(r['history'])))
        save(BASE/'results/fit-freeze.json',dict(utc=utc(),selected=chosen,numerical_seconds=diag['seconds']+sum(r['elapsed'] for r in results),protocol_sha256=sha(BASE/'evidence/protocol.json'),sources={str(p.relative_to(ROOT)):sha(p) for p in sorted(BASE.glob('*.py'))},policy='Selection sealed before withheld evaluation. No further numerical fitting. No second region.'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['freeze','diagnose','fit']);args=parser.parse_args()
    globals()[args.stage]()
