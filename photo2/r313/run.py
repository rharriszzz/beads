"""Freeze, compare, then explicitly bounded multistart direct search."""
import argparse,time,signal,subprocess
from copy import deepcopy
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import minimize
from photo2.r297.common import ROOT,read,save,sha,utc,digest
from photo2.r306.evidence import load
from photo2.r311.model import starts
from .evidence import freeze
from .objective import Objective

R312='photo2/r312/results/campaign/stage2/exports/trial-1000144-N2405-h-1-open.json.gz'
R312LOCAL='photo2/r312/results/campaign/stage1/selection.json'

def historical():
    old=starts();selected=[old[i] for i in [0,1,3]]
    selected.append(dict(name='R312-best',parameters=read(ROOT/R312)['parameters'],implementation='R306',source=R312))
    # R312 Stage 1 is especially relevant to the requested local comparison.
    selection=read(ROOT/R312LOCAL)
    selected.append(dict(name='R312-local',parameters=selection['models'][0]['parameters'],implementation='R306',source=R312LOCAL))
    return selected

def export(out,name,row,s,tr):
    result=deepcopy(row);result['name']=name
    result['positions']=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),projected=s.pc.tolist(),frames={k:v.tolist() for k,v in s.g.items()})
    result['cohort']=list(range(-100,100));result['cohort_positions']=int(np.sum((s.indices>=-100)&(s.indices<=99)))
    save(out/'models'/f'{name}.json.gz',result)
    if tr is not None:np.savez_compressed(out/'models'/f'{name}.npz',owner=tr['owner'],unknown=tr['unknown'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'photo2/r313/results');parser.add_argument('--prepare',action='store_true');parser.add_argument('--recompare',action='store_true');parser.add_argument('--fit-seconds',type=float,default=360);parser.add_argument('--review',action='store_true');parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    if args.review:
        from .review import run
        run(out);return
    if args.verify:
        from .verify import run
        run(out);return
    data,_,_=load();evidence=out.parent/'evidence'
    if args.prepare or args.recompare:
        if args.recompare:
            if (out/'selection.json').exists():raise SystemExit('Cannot change baseline after fitting')
            doc=read(evidence/'freeze.json');assert sha(evidence/'maps.npz')==doc['maps_sha256'];maps=dict(np.load(evidence/'maps.npz'))
        else:
            if (evidence/'freeze.json').exists():raise SystemExit('Evidence already frozen; use a new output directory to rerun preparation')
            save(evidence/'start.json',dict(utc=utc(),head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),status=subprocess.check_output(['git','status','--short'],text=True),session_start_utc='2026-10-17T20:01:50Z',hard_deadline_utc='2026-10-17T20:31:50Z'))
            maps,doc=freeze(evidence,data)
        engine=Objective(maps,doc);base=[]
        for h in historical():
            row,s,tr=engine.evaluate(h['parameters'],data,h['implementation'],True);row['source']=h['source'];export(out,h['name'],row,s,tr)
            base.append(dict(name=h['name'],feasible=row['feasible'],development=row.get('development'),comparison=row.get('comparison'),seconds=row['seconds']))
            print(h['name'],row['feasible'],row.get('development',{}).get('score'),row['seconds'],flush=True)
        save(out/'baseline.json',base)
        # Fixed artificial prediction corruptions test detection, not model improvement.
        baseline=read(out/'models/R306-2405.json.gz');raster=np.load(out/'models/R306-2405.npz');shape=tuple(maps['shape']);own=raster['owner'].reshape(shape);un=raster['unknown'].reshape(shape);idx=np.array(baseline['positions']['indices'])
        controls=[]
        for dx,dy in [(0,0),(12,0),(-12,0),(0,12),(0,-12),(25,0)]:
            oo=ndi.shift(own,(dy,dx),order=0,mode='constant',cval=-1);uu=ndi.shift(un,(dy,dx),order=0,mode='constant',cval=False)
            controls.append(dict(kind='translated_prediction',dx=dx,dy=dy,development=engine.measure(oo,uu,idx,0,True)))
        merged=np.where(own>=0,0,-1)
        controls.append(dict(kind='all_bodies_merged_same_coverage',development=engine.measure(merged,un,idx,0,True)))
        blank=np.full_like(own,-1);controls.append(dict(kind='all_material_missing',development=engine.measure(blank,un,idx,0,True)))
        save(out/'controls.json',controls)
        print('Frozen evidence:',doc['counts'],'controls:',[(v['kind'],v.get('dx'),v.get('dy'),v['development']['score']) for v in controls],flush=True)
        return
    doc=read(evidence/'freeze.json');assert sha(evidence/'maps.npz')==doc['maps_sha256'];maps=dict(np.load(evidence/'maps.npz'));engine=Objective(maps,doc)
    if (out/'selection.json').exists():raise SystemExit('Sealed search exists; refusing overwrite')
    controls=read(out/'controls.json');base_control=controls[0]['development']['score']
    assert all(r['development']['score']>base_control for r in controls[1:]),'Prediction corruption control failed; fitting prohibited'
    # Hash bound before any fitting. Core and transition measurements cannot change.
    sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r313').glob('*.py'))}
    save(evidence/'fitting-freeze.json',dict(utc=utc(),sources=sources,evidence=doc['maps_sha256'],seconds=args.fit_seconds,
        selection='Development objective only; no comparison ranking',shape='Existing shared axial aspect and projected radial size; no arbitrary local correction or new annular profile law'))
    began=time.monotonic();deadline=began+args.fit_seconds;stop=[False]
    def interrupt(*_):stop[0]=True
    signal.signal(signal.SIGTERM,interrupt);signal.signal(signal.SIGINT,interrupt)
    histories=[];best=[];evaluation=0;cache={};rng=np.random.default_rng(313)
    candidates=[historical()[i] for i in [0,1,3,4]];scales=np.array([.3,8.,5.,8.,4.,.25,.4,.10,.003])
    keys=['phase','s0','elevation','roll','tilt','minor','scale','axial','spacing_wave']
    class End(Exception):pass
    for h in candidates:
        keys[3]='yaw' if h['implementation']=='R297' else 'roll'
        p0=deepcopy(h['parameters']);original=deepcopy(p0);p0.setdefault('spacing_wave',0.)
        per_deadline=min(deadline,time.monotonic()+args.fit_seconds/len(candidates));incumbent=[float('inf'),p0,None]
        def parameters(v):
            p=deepcopy(original)
            for k,z,sc in zip(keys,v,scales):p[k]=float(p0.get(k,0.)+z*sc)
            p['phase']=float((p['phase']+np.pi)%(2*np.pi)-np.pi)
            p['local_spacing']=(np.array(original['local_spacing'])+p.pop('spacing_wave')*np.cos(2*np.pi*np.arange(len(original['local_spacing']))/len(original['local_spacing']))).tolist()
            return p
        def objective(v):
            nonlocal evaluation
            if stop[0] or time.monotonic()>=per_deadline:raise End()
            p=parameters(v);key=digest(p)
            if key in cache:return cache[key]
            trial=dict(id=evaluation,start=h['name'],parameters=p,vector=np.asarray(v).tolist(),elapsed=time.monotonic()-began);evaluation+=1
            # Numerical bounds, not material measurements. Existing fields stay coherent.
            spacing_limit=max(.018,max(abs(np.array(original['local_spacing'])))+.006)
            if not (20<p['elevation']<89 and .25<p['axial']<1.4 and 2.5<p['minor']<6.5 and 5.5<p['scale']<12 and max(abs(np.array(p['local_spacing'])))<=spacing_limit):
                trial.update(feasible=False,reason='Numerical exploration bounds',score=1e4,seconds=0.)
            else:
                try:
                    result,_,_=engine.evaluate(p,data,h['implementation'],False)
                    trial.update(result);trial['score']=result['development']['score'] if result['feasible'] else 1e3+result['physical']['unresolved_pairs']
                except ValueError as ex:trial.update(feasible=False,reason=str(ex),score=1e4,seconds=0.)
            cache[key]=trial['score'];histories.append(trial);save(out/'trials'/f'{trial["id"]:05d}.json.gz',trial)
            if trial['feasible'] and trial['score']<incumbent[0]:
                incumbent[:]=[trial['score'],p,trial['id']];print('best',h['name'],trial['id'],round(trial['score'],5),'elapsed',round(time.monotonic()-began,1),flush=True)
            return trial['score']
        try:
            objective(np.zeros(len(keys)))
            # Diverse coupled starts: deterministic shared perturbations, then simplex.
            probes=[np.zeros(len(keys))]+[rng.normal(0,.35,len(keys)) for _ in range(5)]
            values=[objective(v) for v in probes];v=probes[int(np.argmin(values))]
            simplex=np.tile(v,(len(keys)+1,1));simplex[1:]+=np.eye(len(keys))*.18
            minimize(objective,v,method='Nelder-Mead',options=dict(initial_simplex=simplex,maxiter=10000,xatol=.01,fatol=1e-4))
        except End:pass
        best.append(dict(start=h['name'],score=incumbent[0],parameters=incumbent[1],trial=incumbent[2],implementation=h['implementation']))
        save(out/'checkpoint.json',dict(utc=utc(),elapsed=time.monotonic()-began,evaluations=evaluation,best=best,stopped=stop[0]))
        if stop[0] or time.monotonic()>=deadline:break
    best.sort(key=lambda r:r['score']);selection=dict(utc=utc(),seconds=time.monotonic()-began,evaluations=evaluation,best=best,sealed=True,selected=best[0],source_hashes=sources,evidence_sha256=doc['maps_sha256'])
    save(out/'selection.json',selection)
    # Final comparison exposure occurs only after selection is sealed.
    for i,b in enumerate(best):
        r,s,tr=engine.evaluate(b['parameters'],data,b['implementation'],True);export(out,f'R313-{i+1}',r,s,tr)
    print('SEALED',selection['seconds'],evaluation,best[0]['score'],flush=True)

if __name__=='__main__':main()
