"""Paired interventions on old native supports; every failure remains visible."""
from copy import deepcopy
import numpy as np
from .common import *
from .geometry import Chain, full_parameters, contact
from photo2.r295.geometry import Chain as LocalChain
from photo2.r296.review import native_observations,summarize


def main():
    data,_=load_evidence();old=read(ROOT/'photo2/r295/results/R295-evaluation.json')
    ids={r['id'] for r in old['observations']}
    local=dict(data,rows=[r for r in data['rows'] if r['id'] in ids])
    r295=read(ROOT/'photo2/r295/results/joint.json')['selected']['parameters']
    r296=read(ROOT/'photo2/r296/results/pilot/candidates/000188.json.gz')['parameters']
    cases=[('R295 original local',r295,'local'),('R296 selected',r296,'full')]
    for name,keys in [('camera',['scale','elevation','yaw','perspective']),('shape',['radius','axial','minor']),('phase',['phase','phase_knots']),('legacy spacing',['strain','pitch','s0']),('local fields',['local_phase','local_spacing','local_bend'])]:
        p=deepcopy(r296)
        for k in keys:p[k]=deepcopy(r295[k]) if k in r295 else [0.]*32
        cases.append(('R296 with R295 '+name,p,'full'))
    for count in [2337,2438,2540]:
        for metric,turn in [(0,0),(1,0),(0,1),(1,1)]:
            p=full_parameters(r295,count);p.update(local_metric=metric,local_turn=turn)
            cases.append((f'R295 extended N{count} metric{metric} turn{turn}',p,'full'))
    for i in [166,94,112]:
        p=read(ROOT/f'photo2/r296/results/pilot/candidates/{i:06d}.json.gz')['parameters'];cases.append((f'R296 family {i}',p,'full'))
    out=[]
    for name,p,kind in cases:
        scene=LocalChain(p,data) if kind=='local' else Chain(p,data)
        obs=native_observations(scene,local,['train','validation','reserved','buffer'])
        cert=contact(scene)
        result=dict(name=name,parameters=p,physical={k:v for k,v in cert.items() if k!='witnesses'},
            summary={k:summarize([r for r in obs if r['kind']==k]) for k in ('patch','region')},observations=obs)
        out.append(result)
        print(name,cert['state'],result['summary']['region'],flush=True)
    save(BASE/'results/paired-diagnosis.json.gz',out)

if __name__=='__main__':main()
