"""Post-selection independent optical and shared-shape controls; never rank candidates."""
from copy import deepcopy
import time
import numpy as np
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r297.geometry import reference
from photo2.r309.render import predict
from photo2.r312.objective import bottleneck,statistics
from .objective import Objective,scene

def run(out):
    began=time.monotonic();data,_,obs=load();m=dict(np.load(out.parent/'evidence/maps.npz'));doc=read(out.parent/'evidence/freeze.json');engine=Objective(m,doc)
    rr=reference();local=[]
    for o in obs:
        arc=((o['arc']-data['arc0'])*data['direction']+rr.length/2)%rr.length-rr.length/2
        if abs(arc)<=400 and o['strong']:local.append(o)
    models={p.name.removesuffix('.json.gz'):read(p) for p in (out/'models').glob('*.json.gz')};predictions={};maps={};results=[]
    selection=read(out/'selection.json');parent={f'R313-{i+1}':v['start'] for i,v in enumerate(selection['best'])}
    # Every baseline's mapping is frozen before measuring corresponding candidate.
    ordered=sorted(models,key=lambda n:(n.startswith('R313-'),n))
    for name in ordered:
        r=models[name];s=scene(r['parameters'],data,r['implementation'])
        owners=np.array(sorted({j for a in s.tree.query_ball_point([o['point'] for o in local],60.) for j in a}),int)
        p,meta=predict(s,owners=owners);predictions[name]=p
        if name not in parent:maps[name]=bottleneck(local,p)
        else:maps[name]=maps[parent[name]]
        by={v['index']:v for v in p};rows=[]
        for o in local:
            k=maps[name][o['id']];q=by.get(k);err=float(np.linalg.norm(np.array(q['point'])-o['point'])) if q else None
            rows.append(dict(id=o['id'],observed=o['point'],predicted=q['point'] if q else None,index=k,error_px=err,color=o['color'],strong=o['strong']))
        results.append(dict(name=name,parent=parent.get(name),metrics=statistics(rows),rows=rows,numerics=meta,selection_use=False))
        print('optical diagnostic',name,statistics(rows),flush=True)
    save(out/'reflection-diagnostics.json',dict(models=results,observations=len(local),policy='Fixed photographic arclength cohort. Baseline bottleneck maps frozen for corresponding candidate; rematching never used to select R313. All strong local reflections including black; physical identity unverified.',seconds=time.monotonic()-began))
    winner=selection['selected'];base=models[winner['start']]['parameters'];candidate=winner['parameters'];shape=[]
    variants=[('baseline',deepcopy(base)),('selected',deepcopy(candidate))]
    q=deepcopy(candidate)
    for key in ['axial','scale']:q[key]=base[key]
    variants.append(('selected_with_baseline_dimensions',q))
    q=deepcopy(base)
    for key in ['axial','scale']:q[key]=candidate[key]
    variants.append(('baseline_with_selected_dimensions',q))
    for factor in [.9,1.1]:
        q=deepcopy(base);q['axial']*=factor;variants.append((f'baseline_axial_times_{factor}',q))
    for label,p in variants:
        r,s,tr=engine.evaluate(p,data,winner['implementation'],True)
        shape.append(dict(label=label,**r));print('shape diagnostic',label,r['feasible'],r.get('development',{}).get('score'),flush=True)
    save(out/'shared-shape-controls.json.gz',dict(controls=shape,policy='Post-selection counterfactuals, no candidate selection. Exact shared annular axial aspect and scale only; profile/hole/rim law unchanged. Infeasible counterfactuals cannot establish a photographic preference.'))
    trials=[read(p) for p in sorted((out/'trials').glob('*.gz'))];feasible=[r for r in trials if r['feasible']];profiles={k:dict(total_seconds=float(sum(r.get('profile',{}).get(k,0) for r in trials)),median_seconds=float(np.median([r['profile'][k] for r in feasible]))) for k in ['geometry','contact','render','measure']}
    save(out/'performance.json',dict(fitting_seconds=selection['seconds'],proposal_vectors=len(trials),feasible=len(feasible),uncertified=sum(not r['feasible'] and 'physical' in r for r in trials),bounds_or_geometry_failures=sum(not r['feasible'] and 'physical' not in r for r in trials),median_feasible_evaluation_seconds=float(np.median([r['seconds'] for r in feasible])),profiles=profiles,native_rays_per_evaluation=len(m['xy']),new_acceleration='No new approximation or accelerator introduced; R312 exact compiled native ray kernel and early positive separating planes reused.',diagnostics_seconds=time.monotonic()-began))

if __name__=='__main__':run(ROOT/'photo2/r313/results')
