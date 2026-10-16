"""Bounded driver: diagnostic prerequisite, independent fits, shared fit, freeze."""
from copy import deepcopy
import argparse,time
import numpy as np
from .evidence import BASE,read,save,utc,sha
from .model import Local,DEFAULT,BOUNDS,NAMES,predict
from .objective import evaluate,assignment
from .search import run

def best(state):
    return min(state['history'],key=lambda r:r['loss'])

def synthetic():
    s=dict(id='synthetic',center=[1200,1400],tangent=[.8,.6],observations=[],cues={},profiles=[],separators=[],bead_dimensions=[])
    truth=DEFAULT.copy();truth[6]=-8;truth[4]=.14;truth[0]=.18;truth[16]=1.1
    scene=Local(truth,s,-1);cert=scene.certify(iterations=180);assert cert['certified']
    pp,diag=predict(scene,s,2);t=np.array(s['tangent']);c=np.array(s['center'])
    pp=[p for p in pp if abs((np.array(p['point'])-c)@t)<48 and p['strength']>.005]
    rng=np.random.default_rng(301001);observations=[]
    for i,p in enumerate(pp):observations.append(dict(id=f'K{i}',color=['red','yellow','black'][i%3],point=p['point'],weight=1.,split='withheld' if i%4==1 else 'train',known_owner=p['owner']))
    s['observations']=observations
    save(BASE/'evidence/synthetic.json',dict(utc=utc(),truth=truth.tolist(),section=s,physical=cert,diagnostic=diag,independent_check='Native pixel first-hit SDF + shadow predictor generates targets; coarse surface quadrature fits them. Independent numerical representation, shared mathematical construction, not an independent renderer.'))
    out=[]
    for uncertain in [False,True]:
        ss=deepcopy(s);ss['id']='synthetic-uncertain' if uncertain else 'synthetic-known'
        if uncertain:
            for r in ss['observations']:
                r.pop('known_owner');r['point']=(np.array(r['point'])+rng.normal(0,1.5,2)).tolist()
            ss['observations']=ss['observations'][1:]+[dict(id='false',color='black',point=[1211,1438],weight=.2,split='train')]
        save(BASE/f'evidence/{ss["id"]}.json',ss)
        st=run(BASE/f'results/{ss["id"]}',ss,-1,30101+int(uncertain),2048,'de')
        b=best(st);ref=run(BASE/f'results/{ss["id"]}-accurate',ss,-1,30111+int(uncertain),256,'de',1,start=b['parameters'])
        chosen=best(ref);final=evaluate(chosen['parameters'],ss,-1,2,True)
        out.append(dict(name=ss['id'],truth=truth.tolist(),coarse=b,selected=chosen,final=final,parameter_error=(np.array(chosen['parameters'])-truth).tolist(),elapsed=st['elapsed']+ref['elapsed']))
    save(BASE/'results/synthetic-summary.json.gz',out)
    print('Synthetic diagnostic complete',[(r['name'],r['final']['loss']) for r in out],flush=True)

def independent():
    data=read(BASE/'evidence/frozen.json.gz');manifest=[]
    for s in data['sections']:
      for hand in [-1,1]:
        for seed in [3011,3012]:
            name=f'{s["id"]}-h{hand}-s{seed}'
            st=run(BASE/'results'/name,s,hand,seed,1536,'de');b=best(st)
            manifest.append(dict(name=name,section=s['id'],hand=hand,seed=seed,best=b,elapsed=st['elapsed']))
            save(BASE/'results/independent-manifest.json.gz',manifest)
        # Equal evaluations at the same coarse resolution from historical local dimensions.
        st=run(BASE/f'results/{s["id"]}-h{hand}-coordinate',s,hand,3013,1536,'coordinate')
        manifest.append(dict(name=f'{s["id"]}-h{hand}-coordinate',section=s['id'],hand=hand,seed=3013,best=best(st),elapsed=st['elapsed']))
        save(BASE/'results/independent-manifest.json.gz',manifest)

def refine():
    sections=read(BASE/'evidence/frozen.json.gz')['sections'];runs=read(BASE/'results/independent-manifest.json.gz');manifest=[]
    for s in sections:
      for hand in [-1,1]:
        group=[r for r in runs if r['section']==s['id'] and r['hand']==hand]
        # Accurate rerank diverse independent seeds and coordinate control first.
        pool=[]
        for rr in group:
            history=read(BASE/'results'/rr['name']/'checkpoint.json.gz')['history'];accepted=[]
            for row in sorted((r for r in history if r['feasible']),key=lambda r:r['loss']):
                u=(np.array(row['parameters'])-BOUNDS[:,0])/np.ptp(BOUNDS,axis=1)
                if all(np.linalg.norm(u-v)>.35 for v in accepted):
                    accepted.append(u);p=row['parameters'];ev=evaluate(p,s,hand,1,True);pool.append(dict(source=rr['name'],parameters=p,evaluation=ev))
                if len(accepted)==3:break
        save(BASE/f'results/{s["id"]}-h{hand}-rerank.json.gz',pool)
        for rank,item in enumerate(sorted(pool,key=lambda r:r['evaluation']['loss'])[:2]):
            name=f'{s["id"]}-h{hand}-accurate{rank}'
            st=run(BASE/'results'/name,s,hand,30120+rank,384,'de',1,start=item['parameters']);b=best(st)
            manifest.append(dict(name=name,section=s['id'],hand=hand,best=b,elapsed=st['elapsed'],source=item['source']))
            save(BASE/'results/refined-manifest.json.gz',manifest)

def joint():
    """Blockwise DE mutates common dimensions and every local pose jointly."""
    from scipy.stats import qmc
    from photo2.r297.common import run_lock
    from .search import fingerprints
    sections=read(BASE/'evidence/frozen.json.gz')['sections'];ref=read(BASE/'results/refined-manifest.json.gz');out=[]
    lo=np.r_[BOUNDS[:12,0],np.tile(BOUNDS[12:,0],3)];hi=np.r_[BOUNDS[:12,1],np.tile(BOUNDS[12:,1],3)];span=hi-lo
    for hand in [-1,1]:
      path=BASE/f'results/joint-h{hand}';cp=path/'checkpoint.json.gz'
      with run_lock(path):
        rng=np.random.default_rng(30140+hand);starts=[min([r for r in ref if r['section']==s['id'] and r['hand']==hand],key=lambda r:r['best']['loss'])['best']['parameters'] for s in sections]
        # Start shared variables from EACH section, not an average of incompatible fits.
        seeds=[np.r_[p[:12],np.array(starts)[:,12:].ravel()] for p in starts];pop=np.array([np.clip((seeds[i%3]-lo)/span+rng.normal(0,.06,len(lo)),0,1) for i in range(36)]);pop[:3]=[(v-lo)/span for v in seeds];score=np.full(36,1e12);hist=[];elapsed=0
        if cp.exists():
            z=read(cp);assert z['fingerprints']==fingerprints();hist=z['history'];pop=np.array(z['population']);score=np.array(z['scores']);rng.bit_generator.state=z['rng'];elapsed=z['elapsed']
        start=time.monotonic()
        for i in range(len(hist),768):
            target=i%36
            if i<36:u=pop[i].copy()
            else:
                a,b,c=rng.choice([j for j in range(36) if j!=target],3,False);mut=pop[a]+.7*(pop[b]-pop[c]);cross=rng.random(len(lo))<.8;cross[rng.integers(len(lo))]=True;u=np.where(cross,mut,pop[target]);u=np.where((u<0)|(u>1),rng.random(len(lo)),u)
            v=lo+span*u;results=[]
            for j,s in enumerate(sections):results.append(evaluate(np.r_[v[:12],v[12+j*6:18+j*6]],s,hand,1))
            loss=float(np.mean([r['loss'] for r in results]));hist.append(dict(i=i,parameters=v.tolist(),loss=loss,sections=results))
            if loss<score[target]:score[target]=loss;pop[target]=u
            save(cp,dict(fingerprints=fingerprints(),history=hist,population=pop.tolist(),scores=score.tolist(),rng=rng.bit_generator.state,elapsed=elapsed+time.monotonic()-start))
            if i%128==0:print('Joint',hand,i,score.min(),flush=True)
        chosen=min(hist,key=lambda r:r['loss']);out.append(dict(hand=hand,best=chosen,elapsed=elapsed+time.monotonic()-start))
        save(BASE/'results/joint-manifest.json.gz',out)
    # Seal before any native held-out export or comparison; no tuning afterward.
    save(BASE/'results/fit-freeze.json',dict(utc=utc(),sources=fingerprints(),independent_sha256=sha(BASE/'results/refined-manifest.json.gz'),joint_sha256=sha(BASE/'results/joint-manifest.json.gz'),no_more_fitting=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['synthetic','independent','refine','joint']);a=p.parse_args();globals()[a.stage]()
