"""Descriptive whole-circuit trends and geographic rejected-contact clusters."""
from pathlib import Path
from collections import Counter
import numpy as np
from photo2.r297.common import read,save
from photo2.r297.geometry import reference
from .geometry import Chain

def build(out,models,data):
    out=Path(out);ref=reference();trends=[]
    for model in models:
        rows=[r for r in model['correspondences']['records'] if r['strong'] and r['error_px'] is not None]
        f=np.array([((r['arc']-data['arc0'])*data['direction'])%ref.length/ref.length for r in rows])
        x=np.c_[np.ones(len(f)),f];coefficients={}
        for key in ['error_px','tangent_px','normal_px']:
            y=np.array([r[key] for r in rows]);beta=np.linalg.lstsq(x,y,rcond=None)[0]
            coefficients[key]=dict(intercept_px=float(beta[0]),slope_px_per_circuit=float(beta[1]),mean_px=float(y.mean()))
        order=np.sort(f);gaps=np.diff(np.r_[order,order[0]+1])*ref.length
        trends.append(dict(model=model['name'],n=len(rows),coefficients=coefficients,largest_matched_strong_gap_px=float(gaps.max()),
            regional=model['regions'],interpretation='Descriptive linear slopes in one fixed photographic circuit gauge; no statistical independence or physical index-drift claim. Regional jumps/recoveries and sparse intervals must be read alongside these numbers.'))
    save(out/'whole-circuit-trends.json',trends)
    failures=[]
    for name in ['campaign-initial',out.name,'independent']:
        folder=out.parent/name
        if not (folder/'checkpoint.json').exists():continue
        state=read(folder/'checkpoint.json')
        for h in state['history']:
            if h['status']!='physical-rejected':continue
            row=read(folder/'candidates'/f'{h["id"]:06d}.json.gz');scene=Chain(row['parameters'],data)
            cases=[]
            for q in row['contact']['penetration_checks']:
                ix=np.searchsorted(scene.indices,q['pair']);point=scene.pc[ix].mean(0)
                arc=float(ref.project([point])['arc'][0]);section=int(((arc-data['arc0'])*data['direction'])%ref.length/ref.length*32)%32
                cases.append(dict(**q,point=point.tolist(),section=section))
            failures.append(dict(run=name,candidate=h['id'],count=scene.n,hand=scene.p['hand'],topology=scene.p['topology'],
                uncertified=row['contact']['unresolved_pairs'],sampled_penetrating=sum(r['penetrating'] for r in cases),
                demonstrated_by_section=dict(Counter(r['section'] for r in cases if r['penetrating'])),cases=cases))
    save(out/'rejected-contact-clusters.json.gz',dict(candidates=failures,
        interpretation='Geographic clusters of saved solid-penetration witnesses from rejected proposals. A failed support certificate without a penetrating sample remains unresolved. None of these models is accepted. Counts across trials are repeated diagnostics, not independent physical collisions.'))
